"""Enforcement engine -- evaluates rules against proposal state."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from pes.domain.corpus_integrity import CorpusIntegrityEvaluator
from pes.domain.deadline_blocking import DeadlineBlockingEvaluator
from pes.domain.housekeeping import CrashSignalCleaner
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
