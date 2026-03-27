"""Enforcement engine -- evaluates rules against proposal state."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pes.domain.agent_wave_mapping import is_agent_authorized_for_wave, is_agent_recognized
from pes.domain.corpus_integrity import CorpusIntegrityEvaluator
from pes.domain.deadline_blocking import DeadlineBlockingEvaluator
from pes.domain.figure_pipeline_gate import FigurePipelineGateEvaluator
from pes.domain.housekeeping import AuditLogRotator, CrashSignalCleaner
from pes.domain.outline_gate import OutlineGateEvaluator
from pes.domain.pdc_gate import PdcGateEvaluator
from pes.domain.post_action_validator import PostActionValidator
from pes.domain.rules import Decision, EnforcementResult, EnforcementRule
from pes.domain.session_checker import SessionChecker
from pes.domain.style_profile_gate import StyleProfileGateEvaluator
from pes.domain.submission_immutability import SubmissionImmutabilityEvaluator
from pes.domain.wave_rules import WaveOrderingEvaluator
from pes.domain.writing_style_gate import WritingStyleGateEvaluator
from pes.ports.audit_port import AuditLogger
from pes.ports.rule_port import RuleLoader

logger = logging.getLogger(__name__)


class EnforcementEngine:
    """Driving port: evaluates enforcement rules against proposal state."""

    def __init__(self, rule_loader: RuleLoader, audit_logger: AuditLogger) -> None:
        self._rule_loader = rule_loader
        self._audit_logger = audit_logger
        self._session_checker = SessionChecker()
        self._crash_cleaner = CrashSignalCleaner()
        self._audit_rotator = AuditLogRotator()
        self._post_action_validator = PostActionValidator()

        # Rule evaluators keyed by rule_type for dispatch
        self._evaluators: dict[str, Any] = {
            "wave_ordering": WaveOrderingEvaluator(),
            "pdc_gate": PdcGateEvaluator(),
            "deadline_blocking": DeadlineBlockingEvaluator(),
            "submission_immutability": SubmissionImmutabilityEvaluator(),
            "corpus_integrity": CorpusIntegrityEvaluator(),
            "figure_pipeline_gate": FigurePipelineGateEvaluator(),
            "style_profile_gate": StyleProfileGateEvaluator(),
            "writing_style_gate": WritingStyleGateEvaluator(),
            "outline_gate": OutlineGateEvaluator(),
        }

    def check_session_start(
        self,
        state: dict[str, Any],
        proposal_dir: str | None = None,
    ) -> EnforcementResult:
        """Run integrity check at session startup.

        Performs crash signal cleanup, then runs session integrity checks.
        Returns ALLOW with warning messages for issues found.
        Returns ALLOW with no messages for clean state.
        """
        messages: list[str] = []

        if proposal_dir:
            messages.extend(self._clean_crash_signals(proposal_dir, state))
            self._rotate_audit_logs(proposal_dir, state)

        messages.extend(
            self._session_checker.check(state, proposal_dir=proposal_dir)
        )

        result = EnforcementResult(decision=Decision.ALLOW, messages=messages)
        self._safe_audit_log({
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "session_start",
            "decision": result.decision.value.lower(),
            "proposal_id": state.get("proposal_id", "unknown"),
            "messages": messages,
        })
        return result

    def evaluate(
        self,
        state: dict[str, Any],
        tool_name: str,
        tool_context: dict[str, Any] | None = None,
    ) -> EnforcementResult:
        """Evaluate enforcement rules for a tool invocation.

        Returns ALLOW if all rules pass, BLOCK with messages if any rule triggers.
        """
        tool_context = tool_context or {}
        rules = self._rule_loader.load_rules()
        block_messages: list[str] = []

        for rule in rules:
            if self._rule_triggers(rule, state, tool_name, tool_context):
                block_messages.append(self._build_message(rule, state))

        decision = Decision.BLOCK if block_messages else Decision.ALLOW

        result = EnforcementResult(decision=decision, messages=block_messages)

        self._safe_audit_log({
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "evaluate",
            "decision": result.decision.value.lower(),
            "tool_name": tool_name,
            "proposal_id": state.get("proposal_id", "unknown"),
            "messages": block_messages,
        })

        return result

    def check_post_action(
        self,
        state: dict[str, Any],
        tool_name: str,
        artifact_info: dict[str, Any],
    ) -> EnforcementResult:
        """Validate post-action results after a tool completes.

        Checks artifact placement and state file integrity for write operations.
        Returns ALLOW with warning messages for issues found.
        Post-action validation is advisory -- never blocks.
        """
        messages = self._post_action_validator.validate(
            state, tool_name, artifact_info,
        )

        result = EnforcementResult(decision=Decision.ALLOW, messages=messages)

        self._safe_audit_log({
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "post_action",
            "decision": "allow",
            "tool_name": tool_name,
            "proposal_id": state.get("proposal_id", "unknown"),
            "messages": messages,
            "file_path": artifact_info.get("file_path", ""),
        })

        return result

    def check_agent_dispatch(
        self,
        state: dict[str, Any] | None,
        agent_name: str,
    ) -> EnforcementResult:
        """Verify an agent is authorized for the current proposal wave.

        Returns BLOCK if no active proposal, agent is unrecognized,
        or agent is not authorized for the current wave.
        Returns ALLOW with audit entry for authorized dispatch.
        """
        if state is None or "proposal_id" not in state:
            return self._dispatch_result(
                Decision.BLOCK,
                ["no active proposal for agent dispatch"],
                agent_name=agent_name,
                proposal_id="unknown",
            )

        proposal_id = state.get("proposal_id", "unknown")
        current_wave = state.get("current_wave", -1)

        if not is_agent_recognized(agent_name):
            return self._dispatch_result(
                Decision.BLOCK,
                [f"{agent_name} is not a recognized agent"],
                agent_name=agent_name,
                wave=current_wave,
                proposal_id=proposal_id,
            )

        if not is_agent_authorized_for_wave(agent_name, current_wave):
            return self._dispatch_result(
                Decision.BLOCK,
                [f"{agent_name} is not authorized for Wave {current_wave}"],
                agent_name=agent_name,
                wave=current_wave,
                proposal_id=proposal_id,
            )

        return self._dispatch_result(
            Decision.ALLOW,
            [],
            agent_name=agent_name,
            wave=current_wave,
            proposal_id=proposal_id,
        )

    def record_agent_stop(
        self,
        state: dict[str, Any],
        agent_name: str,
    ) -> EnforcementResult:
        """Record agent deactivation in audit trail.

        SubagentStop is audit-only -- never blocks.
        Returns ALLOW with audit entry containing agent name and wave.
        """
        proposal_id = state.get("proposal_id", "unknown")
        current_wave = state.get("current_wave", -1)

        result = EnforcementResult(decision=Decision.ALLOW)
        self._safe_audit_log({
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "agent_stop",
            "decision": "allow",
            "agent_name": agent_name,
            "wave": current_wave,
            "proposal_id": proposal_id,
            "messages": [],
        })
        return result

    def _clean_crash_signals(
        self, proposal_dir: str, state: dict[str, Any]
    ) -> list[str]:
        """Clean crash signals and return warning messages for failures."""
        messages: list[str] = []
        proposal_id = state.get("proposal_id", "unknown")
        for cleanup in self._crash_cleaner.clean(proposal_dir):
            self._safe_audit_log({
                "timestamp": datetime.now(UTC).isoformat(),
                "event": "crash_signal_cleanup",
                "file": cleanup["file"],
                "status": cleanup["status"],
                "proposal_id": proposal_id,
            })
            if cleanup["status"] == "failed":
                reason = cleanup.get("reason", "unknown error")
                messages.append(
                    f"Crash signal '{cleanup['file']}' could not be removed: "
                    f"{reason}"
                )
        return messages

    def _rotate_audit_logs(
        self, proposal_dir: str, state: dict[str, Any]
    ) -> None:
        """Rotate audit logs and record rotation events."""
        audit_dir = str(Path(proposal_dir) / ".sbir" / "audit")
        proposal_id = state.get("proposal_id", "unknown")
        for rotation in self._audit_rotator.rotate(audit_dir):
            event_name = (
                "audit_log_size_rotation"
                if rotation["action"] == "size_rotation"
                else "audit_log_retention_rotation"
            )
            self._safe_audit_log({
                "timestamp": datetime.now(UTC).isoformat(),
                "event": event_name,
                "action": rotation["action"],
                "archive_file": rotation.get("archive_file", ""),
                "proposal_id": proposal_id,
            })

    def _dispatch_result(
        self,
        decision: Decision,
        messages: list[str],
        **audit_fields: Any,
    ) -> EnforcementResult:
        """Build enforcement result and log agent dispatch audit entry."""
        result = EnforcementResult(decision=decision, messages=messages)
        self._safe_audit_log({
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "agent_dispatch",
            "decision": decision.value.lower(),
            "messages": messages,
            **audit_fields,
        })
        return result

    def _safe_audit_log(self, entry: dict[str, Any]) -> None:
        """Log audit entry, suppressing write failures with a warning."""
        try:
            self._audit_logger.log(entry)
        except Exception:
            logger.warning(
                "Audit write failed for event=%s decision=%s -- "
                "enforcement decision was not affected",
                entry.get("event", "unknown"),
                entry.get("decision", "unknown"),
            )

    def _rule_triggers(
        self,
        rule: EnforcementRule,
        state: dict[str, Any],
        tool_name: str,
        tool_context: dict[str, Any] | None = None,
    ) -> bool:
        """Check if a single rule triggers given current state and tool."""
        evaluator = self._evaluators.get(rule.rule_type)
        if evaluator is None:
            return False
        return evaluator.triggers(rule, state, tool_name, tool_context=tool_context or {})

    def _build_message(
        self, rule: EnforcementRule, state: dict[str, Any]
    ) -> str:
        """Build a detailed block message for the given rule."""
        evaluator = self._evaluators.get(rule.rule_type)
        if evaluator and hasattr(evaluator, "build_block_message"):
            return evaluator.build_block_message(rule, state)
        return rule.message
