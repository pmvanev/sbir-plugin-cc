"""Enforcement engine -- evaluates rules against proposal state."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pes.domain.agent_wave_mapping import is_agent_authorized_for_wave, is_agent_recognized
from pes.domain.corpus_integrity import CorpusIntegrityEvaluator
from pes.domain.deadline_blocking import DeadlineBlockingEvaluator
from pes.domain.post_action_validator import PostActionValidator
from pes.domain.housekeeping import AuditLogRotator, CrashSignalCleaner
from pes.domain.pdc_gate import PdcGateEvaluator
from pes.domain.rules import Decision, EnforcementResult, EnforcementRule
from pes.domain.session_checker import SessionChecker
from pes.domain.submission_immutability import SubmissionImmutabilityEvaluator
from pes.domain.wave_rules import WaveOrderingEvaluator
from pes.ports.audit_port import AuditLogger
from pes.ports.rule_port import RuleLoader

logger = logging.getLogger(__name__)


class EnforcementEngine:
    """Driving port: evaluates enforcement rules against proposal state."""

    def __init__(self, rule_loader: RuleLoader, audit_logger: AuditLogger) -> None:
        self._rule_loader = rule_loader
        self._audit_logger = audit_logger
        self._wave_evaluator = WaveOrderingEvaluator()
        self._pdc_gate_evaluator = PdcGateEvaluator()
        self._deadline_evaluator = DeadlineBlockingEvaluator()
        self._submission_evaluator = SubmissionImmutabilityEvaluator()
        self._corpus_evaluator = CorpusIntegrityEvaluator()
        self._session_checker = SessionChecker()
        self._crash_cleaner = CrashSignalCleaner()
        self._audit_rotator = AuditLogRotator()
        self._post_action_validator = PostActionValidator()

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

        # Crash signal housekeeping
        if proposal_dir:
            cleanup_results = self._crash_cleaner.clean(proposal_dir)
            for cleanup in cleanup_results:
                self._safe_audit_log({
                    "timestamp": datetime.now(UTC).isoformat(),
                    "event": "crash_signal_cleanup",
                    "file": cleanup["file"],
                    "status": cleanup["status"],
                    "proposal_id": state.get("proposal_id", "unknown"),
                })
                if cleanup["status"] == "failed":
                    reason = cleanup.get("reason", "unknown error")
                    messages.append(
                        f"Crash signal '{cleanup['file']}' could not be removed: "
                        f"{reason}"
                    )

        # Audit log rotation
        if proposal_dir:
            audit_dir = str(Path(proposal_dir) / ".sbir" / "audit")
            rotation_results = self._audit_rotator.rotate(audit_dir)
            for rotation in rotation_results:
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
                    "proposal_id": state.get("proposal_id", "unknown"),
                })

        # Existing integrity checks
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

    def evaluate(self, state: dict[str, Any], tool_name: str) -> EnforcementResult:
        """Evaluate enforcement rules for a tool invocation.

        Returns ALLOW if all rules pass, BLOCK with messages if any rule triggers.
        """
        rules = self._rule_loader.load_rules()
        block_messages: list[str] = []

        for rule in rules:
            if self._rule_triggers(rule, state, tool_name):
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
            result = EnforcementResult(
                decision=Decision.BLOCK,
                messages=["no active proposal for agent dispatch"],
            )
            self._safe_audit_log({
                "timestamp": datetime.now(UTC).isoformat(),
                "event": "agent_dispatch",
                "decision": "block",
                "agent_name": agent_name,
                "proposal_id": "unknown",
                "messages": result.messages,
            })
            return result

        proposal_id = state.get("proposal_id", "unknown")
        current_wave = state.get("current_wave", -1)

        if not is_agent_recognized(agent_name):
            result = EnforcementResult(
                decision=Decision.BLOCK,
                messages=[f"{agent_name} is not a recognized agent"],
            )
            self._safe_audit_log({
                "timestamp": datetime.now(UTC).isoformat(),
                "event": "agent_dispatch",
                "decision": "block",
                "agent_name": agent_name,
                "wave": current_wave,
                "proposal_id": proposal_id,
                "messages": result.messages,
            })
            return result

        if not is_agent_authorized_for_wave(agent_name, current_wave):
            result = EnforcementResult(
                decision=Decision.BLOCK,
                messages=[
                    f"{agent_name} is not authorized for Wave {current_wave}"
                ],
            )
            self._safe_audit_log({
                "timestamp": datetime.now(UTC).isoformat(),
                "event": "agent_dispatch",
                "decision": "block",
                "agent_name": agent_name,
                "wave": current_wave,
                "proposal_id": proposal_id,
                "messages": result.messages,
            })
            return result

        result = EnforcementResult(decision=Decision.ALLOW)
        self._safe_audit_log({
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "agent_dispatch",
            "decision": "allow",
            "agent_name": agent_name,
            "wave": current_wave,
            "proposal_id": proposal_id,
            "messages": [],
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
        self, rule: EnforcementRule, state: dict[str, Any], tool_name: str
    ) -> bool:
        """Check if a single rule triggers given current state and tool."""
        if rule.rule_type == "wave_ordering":
            return self._wave_evaluator.triggers(rule, state, tool_name)
        if rule.rule_type == "pdc_gate":
            return self._pdc_gate_evaluator.triggers(rule, state, tool_name)
        if rule.rule_type == "deadline_blocking":
            return self._deadline_evaluator.triggers(rule, state, tool_name)
        if rule.rule_type == "submission_immutability":
            return self._submission_evaluator.triggers(rule, state, tool_name)
        if rule.rule_type == "corpus_integrity":
            return self._corpus_evaluator.triggers(rule, state, tool_name)
        return False

    def _build_message(
        self, rule: EnforcementRule, state: dict[str, Any]
    ) -> str:
        """Build a detailed block message for the given rule."""
        if rule.rule_type == "pdc_gate":
            return self._pdc_gate_evaluator.build_block_message(rule, state)
        if rule.rule_type == "deadline_blocking":
            return self._deadline_evaluator.build_block_message(rule, state)
        if rule.rule_type == "submission_immutability":
            return self._submission_evaluator.build_block_message(rule, state)
        return rule.message
