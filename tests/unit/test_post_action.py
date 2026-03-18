"""Tests for EnforcementEngine.check_post_action -- post-tool validation.

Tests invoke through the EnforcementEngine driving port with fake adapters
at port boundaries (RuleLoader, AuditLogger). No mocks inside the hexagon.

Test Budget: 3 behaviors x 2 = 6 max unit tests
"""

from __future__ import annotations

from typing import Any

import pytest

from pes.domain.engine import EnforcementEngine
from pes.domain.rules import Decision, EnforcementRule
from pes.ports.audit_port import AuditLogger
from pes.ports.rule_port import RuleLoader


# --- Fake adapters at port boundaries ---


class FakeRuleLoader(RuleLoader):
    def __init__(self, rules: list[EnforcementRule] | None = None) -> None:
        self._rules = rules or []

    def load_rules(self) -> list[EnforcementRule]:
        return self._rules


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
def wave_4_state() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "proposal_id": "test-uuid-001",
        "go_no_go": "go",
        "current_wave": 4,
        "topic": {"deadline": "2026-04-15"},
    }


# --- Tests ---


class TestPostActionArtifactPlacement:
    """Verify artifact placement validation through driving port."""

    def test_artifact_in_correct_wave_directory_returns_allow(
        self, engine: EnforcementEngine, wave_4_state: dict[str, Any],
        audit_logger: FakeAuditLogger,
    ) -> None:
        artifact_info = {
            "tool_name": "Write",
            "file_path": "artifacts/wave-4-drafting/sections/technical-approach.md",
        }
        result = engine.check_post_action(wave_4_state, "Write", artifact_info)
        assert result.decision == Decision.ALLOW
        assert result.messages == []

    def test_artifact_in_correct_wave_directory_audits_result(
        self, engine: EnforcementEngine, wave_4_state: dict[str, Any],
        audit_logger: FakeAuditLogger,
    ) -> None:
        artifact_info = {
            "tool_name": "Write",
            "file_path": "artifacts/wave-4-drafting/sections/technical-approach.md",
        }
        engine.check_post_action(wave_4_state, "Write", artifact_info)
        assert len(audit_logger.entries) >= 1
        entry = audit_logger.entries[-1]
        assert entry["event"] == "post_action"
        assert entry["decision"] == "allow"
        assert "timestamp" in entry

    def test_artifact_in_wrong_wave_directory_returns_allow_with_warning(
        self, engine: EnforcementEngine, wave_4_state: dict[str, Any],
    ) -> None:
        artifact_info = {
            "tool_name": "Write",
            "file_path": "artifacts/wave-3-outline/technical-approach.md",
        }
        result = engine.check_post_action(wave_4_state, "Write", artifact_info)
        # Post-action is advisory -- ALLOW with warning messages
        assert result.decision == Decision.ALLOW
        assert len(result.messages) >= 1
        combined = " ".join(result.messages)
        assert "wave-3" in combined.lower() or "wave-4" in combined.lower()

    def test_artifact_in_wrong_wave_directory_audits_warning(
        self, engine: EnforcementEngine, wave_4_state: dict[str, Any],
        audit_logger: FakeAuditLogger,
    ) -> None:
        artifact_info = {
            "tool_name": "Write",
            "file_path": "artifacts/wave-3-outline/technical-approach.md",
        }
        engine.check_post_action(wave_4_state, "Write", artifact_info)
        assert len(audit_logger.entries) >= 1
        entry = audit_logger.entries[-1]
        assert entry["event"] == "post_action"
        assert len(entry.get("messages", [])) >= 1


class TestPostActionStateFileVerification:
    """Verify state file well-formedness check through driving port."""

    def test_state_file_write_returns_allow_when_valid(
        self, engine: EnforcementEngine, wave_4_state: dict[str, Any],
        tmp_path, audit_logger: FakeAuditLogger,
    ) -> None:
        import json

        state_file = tmp_path / "proposal-state.json"
        state_file.write_text(json.dumps(wave_4_state, indent=2))
        artifact_info = {
            "tool_name": "Write",
            "file_path": str(state_file),
        }
        result = engine.check_post_action(wave_4_state, "Write", artifact_info)
        assert result.decision == Decision.ALLOW
        assert result.messages == []

    def test_state_file_write_audits_verification(
        self, engine: EnforcementEngine, wave_4_state: dict[str, Any],
        tmp_path, audit_logger: FakeAuditLogger,
    ) -> None:
        import json

        state_file = tmp_path / "proposal-state.json"
        state_file.write_text(json.dumps(wave_4_state, indent=2))
        artifact_info = {
            "tool_name": "Write",
            "file_path": str(state_file),
        }
        engine.check_post_action(wave_4_state, "Write", artifact_info)
        assert len(audit_logger.entries) >= 1
        entry = audit_logger.entries[-1]
        assert entry["event"] == "post_action"
        assert entry["decision"] == "allow"
