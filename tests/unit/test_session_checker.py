"""Tests for session startup integrity checks through EnforcementEngine (driving port).

SessionChecker is a domain service tested indirectly through the engine.
Tests enter through EnforcementEngine.check_session_start() and assert
observable outcomes (decision, messages).

Test Budget: 4 behaviors x 2 = 8 max unit tests
- Orphaned files detection (1 behavior)
- Clean state no warnings (1 behavior)
- Deadline proximity warning (1 behavior)
- Corrupted state recovery (1 behavior)
"""

from __future__ import annotations

from datetime import date, timedelta
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
def clean_state() -> dict[str, Any]:
    """Consistent state with no orphaned files, distant deadline."""
    return {
        "schema_version": "1.0.0",
        "proposal_id": "test-uuid-001",
        "go_no_go": "go",
        "current_wave": 1,
        "topic": {"deadline": (date.today() + timedelta(days=30)).isoformat()},
        "artifacts": ["drafts/section-3.2.md"],
    }


# --- Test: Orphaned files detection ---


class TestOrphanedFilesDetection:
    """Orphaned artifact files not tracked in state produce warnings."""

    def test_detects_orphaned_file_not_in_state(
        self, engine: EnforcementEngine, tmp_path, audit_logger: FakeAuditLogger
    ) -> None:
        state = {
            "schema_version": "1.0.0",
            "proposal_id": "test-uuid-002",
            "go_no_go": "go",
            "current_wave": 1,
            "topic": {"deadline": (date.today() + timedelta(days=30)).isoformat()},
            "artifacts": [],
        }
        # Create orphaned file on disk
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()
        (drafts_dir / "section-3.2.md").write_text("orphaned draft")

        result = engine.check_session_start(state, proposal_dir=str(tmp_path))

        assert result.decision == Decision.ALLOW
        assert len(result.messages) > 0
        assert any("3.2" in msg for msg in result.messages)

    def test_orphaned_file_message_mentions_compliance(
        self, engine: EnforcementEngine, tmp_path
    ) -> None:
        state = {
            "schema_version": "1.0.0",
            "proposal_id": "test-uuid-003",
            "go_no_go": "go",
            "current_wave": 1,
            "topic": {"deadline": (date.today() + timedelta(days=30)).isoformat()},
            "artifacts": [],
        }
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()
        (drafts_dir / "section-3.2.md").write_text("orphaned draft")

        result = engine.check_session_start(state, proposal_dir=str(tmp_path))

        all_messages = " ".join(result.messages).lower()
        assert "compliance" in all_messages


# --- Test: Clean state ---


class TestCleanStateNoWarnings:
    """Consistent state with no orphans and distant deadline produces no warnings."""

    def test_clean_state_returns_allow_with_no_messages(
        self, engine: EnforcementEngine, clean_state: dict[str, Any], tmp_path
    ) -> None:
        # Create tracked file so it's not orphaned
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()
        (drafts_dir / "section-3.2.md").write_text("tracked draft")

        result = engine.check_session_start(clean_state, proposal_dir=str(tmp_path))

        assert result.decision == Decision.ALLOW
        assert result.messages == []

    def test_clean_state_without_proposal_dir_returns_allow(
        self, engine: EnforcementEngine, clean_state: dict[str, Any]
    ) -> None:
        result = engine.check_session_start(clean_state)

        assert result.decision == Decision.ALLOW
        assert result.messages == []


# --- Test: Deadline proximity ---


class TestDeadlineProximityWarning:
    """Deadline within threshold produces warning with prioritization guidance."""

    @pytest.mark.parametrize("days_remaining", [1, 2, 3])
    def test_warns_when_deadline_within_threshold(
        self, engine: EnforcementEngine, days_remaining: int
    ) -> None:
        state = {
            "schema_version": "1.0.0",
            "proposal_id": "test-uuid-004",
            "go_no_go": "go",
            "current_wave": 1,
            "topic": {
                "deadline": (date.today() + timedelta(days=days_remaining)).isoformat(),
            },
        }

        result = engine.check_session_start(state)

        assert result.decision == Decision.ALLOW
        assert len(result.messages) > 0
        all_messages = " ".join(result.messages).lower()
        assert "deadline" in all_messages
        assert "priorit" in all_messages


# --- Test: Corrupted state recovery ---


class TestCorruptedStateRecovery:
    """Corrupted state flag triggers recovery messages."""

    def test_corrupted_state_produces_warning_messages(
        self, engine: EnforcementEngine
    ) -> None:
        state = {
            "_corrupted": True,
            "_recovered_state": {"proposal_id": "recovered-001"},
        }

        result = engine.check_session_start(state)

        assert result.decision == Decision.ALLOW
        assert len(result.messages) > 0
        all_messages = " ".join(result.messages).lower()
        assert "corrupt" in all_messages
        assert "recover" in all_messages

    def test_corrupted_state_without_backup_warns_no_recovery(
        self, engine: EnforcementEngine
    ) -> None:
        state = {
            "_corrupted": True,
            "_recovered_state": None,
        }

        result = engine.check_session_start(state)

        assert result.decision == Decision.ALLOW
        assert len(result.messages) > 0
        all_messages = " ".join(result.messages).lower()
        assert "corrupt" in all_messages
