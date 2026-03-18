"""Tests for crash signal housekeeping -- through EnforcementEngine driving port.

Tests invoke EnforcementEngine.check_session_start() with a real
housekeeping module and fake adapters at port boundaries.

Test Budget: 4 behaviors x 2 = 8 max unit tests
Behaviors:
  B1 - Single crash signal removed and cleanup audited
  B2 - Multiple crash signals all removed, each cleanup audited
  B3 - Locked/unremovable crash signal produces warning, session continues
  B4 - Clean workspace starts normally, no cleanup entries
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pes.domain.engine import EnforcementEngine
from pes.domain.rules import Decision
from pes.ports.audit_port import AuditLogger
from pes.ports.rule_port import RuleLoader


# --- Fake adapters at port boundaries ---


class FakeRuleLoader(RuleLoader):
    def load_rules(self):
        return []


class FakeAuditLogger(AuditLogger):
    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    def log(self, entry: dict[str, Any]) -> None:
        self.entries.append(entry)


# --- Fixtures ---


@pytest.fixture()
def audit_logger() -> FakeAuditLogger:
    return FakeAuditLogger()


@pytest.fixture()
def engine(audit_logger: FakeAuditLogger) -> EnforcementEngine:
    return EnforcementEngine(FakeRuleLoader(), audit_logger)


@pytest.fixture()
def base_state() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "proposal_id": "test-uuid-hk",
        "go_no_go": "pending",
        "current_wave": 0,
        "topic": {"id": "AF243-001", "deadline": "2026-04-15"},
    }


@pytest.fixture()
def proposal_dir(tmp_path: Path) -> Path:
    sbir_dir = tmp_path / ".sbir"
    sbir_dir.mkdir()
    return tmp_path


def _create_crash_signal(sbir_dir: Path, name: str = "session-crash.signal") -> Path:
    signal = sbir_dir / name
    signal.write_text(json.dumps({
        "session_id": "prev-001",
        "timestamp": "2026-03-17T14:30:00Z",
        "reason": "unexpected_termination",
    }))
    return signal


# --- B1: Single crash signal removed and cleanup audited ---


class TestSingleCrashSignalCleanup:

    def test_crash_signal_removed_on_session_start(
        self,
        engine: EnforcementEngine,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        signal = _create_crash_signal(proposal_dir / ".sbir")
        assert signal.exists()

        result = engine.check_session_start(
            base_state, proposal_dir=str(proposal_dir)
        )

        assert result.decision == Decision.ALLOW
        assert not signal.exists()

    def test_crash_signal_cleanup_is_audited(
        self,
        engine: EnforcementEngine,
        audit_logger: FakeAuditLogger,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        _create_crash_signal(proposal_dir / ".sbir")

        engine.check_session_start(base_state, proposal_dir=str(proposal_dir))

        cleanup_entries = [
            e for e in audit_logger.entries
            if e.get("event") == "crash_signal_cleanup"
        ]
        assert len(cleanup_entries) >= 1


# --- B2: Multiple crash signals all removed, each audited ---


class TestMultipleCrashSignalCleanup:

    def test_all_crash_signals_removed(
        self,
        engine: EnforcementEngine,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        sbir_dir = proposal_dir / ".sbir"
        signals = [
            _create_crash_signal(sbir_dir, f"session-crash-{i}.signal")
            for i in range(3)
        ]

        engine.check_session_start(base_state, proposal_dir=str(proposal_dir))

        for s in signals:
            assert not s.exists(), f"Signal still exists: {s}"

    def test_each_cleanup_individually_audited(
        self,
        engine: EnforcementEngine,
        audit_logger: FakeAuditLogger,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        sbir_dir = proposal_dir / ".sbir"
        for i in range(3):
            _create_crash_signal(sbir_dir, f"session-crash-{i}.signal")

        engine.check_session_start(base_state, proposal_dir=str(proposal_dir))

        cleanup_entries = [
            e for e in audit_logger.entries
            if e.get("event") == "crash_signal_cleanup"
        ]
        assert len(cleanup_entries) == 3


# --- B3: Locked crash signal produces warning, session continues ---


class TestLockedCrashSignalWarning:

    def test_locked_signal_produces_warning_message(
        self,
        engine: EnforcementEngine,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        import os
        import stat

        signal = _create_crash_signal(proposal_dir / ".sbir")
        os.chmod(str(signal), stat.S_IREAD)

        try:
            result = engine.check_session_start(
                base_state, proposal_dir=str(proposal_dir)
            )

            assert result.decision == Decision.ALLOW
            warning_msgs = [
                m for m in result.messages
                if "could not be removed" in m.lower()
                or "unable to remove" in m.lower()
                or "locked" in m.lower()
                or "permission" in m.lower()
            ]
            assert len(warning_msgs) >= 1
        finally:
            # Restore permissions for cleanup
            os.chmod(str(signal), stat.S_IWRITE | stat.S_IREAD)


# --- B4: Clean workspace, no cleanup entries ---


class TestCleanWorkspaceNoCleanup:

    def test_no_cleanup_entries_when_no_crash_signals(
        self,
        engine: EnforcementEngine,
        audit_logger: FakeAuditLogger,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        result = engine.check_session_start(
            base_state, proposal_dir=str(proposal_dir)
        )

        assert result.decision == Decision.ALLOW
        cleanup_entries = [
            e for e in audit_logger.entries
            if e.get("event") == "crash_signal_cleanup"
        ]
        assert len(cleanup_entries) == 0
        # But session_start audit entry IS present
        session_entries = [
            e for e in audit_logger.entries
            if e.get("event") == "session_start"
        ]
        assert len(session_entries) == 1
