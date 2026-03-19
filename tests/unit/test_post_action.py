"""Tests for EnforcementEngine.check_post_action -- post-tool validation.

Tests invoke through the EnforcementEngine driving port with fake adapters
at port boundaries (RuleLoader, AuditLogger). No mocks inside the hexagon.

Targeted domain tests (B5-B8) test PostActionValidator directly for
mutation coverage.

Test Budget: 8 behaviors x 2 = 16 max unit tests
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


class TestPostActionMissingArtifact:
    """Verify missing artifact detection through driving port."""

    def test_missing_artifact_returns_allow_with_warning(
        self, engine: EnforcementEngine, wave_4_state: dict[str, Any],
        tmp_path,
    ) -> None:
        # Use absolute path to a nonexistent file -- triggers existence check
        missing = str(tmp_path / "artifacts" / "wave-4-drafting" / "sections" / "nonexistent.md")
        artifact_info = {
            "tool_name": "Write",
            "file_path": missing,
        }
        result = engine.check_post_action(wave_4_state, "Write", artifact_info)
        assert result.decision == Decision.ALLOW
        assert len(result.messages) >= 1
        combined = " ".join(result.messages).lower()
        assert "not created" in combined

    def test_missing_artifact_audits_warning(
        self, engine: EnforcementEngine, wave_4_state: dict[str, Any],
        audit_logger: FakeAuditLogger, tmp_path,
    ) -> None:
        missing = str(tmp_path / "artifacts" / "wave-4-drafting" / "sections" / "nonexistent.md")
        artifact_info = {
            "tool_name": "Write",
            "file_path": missing,
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


# =============================================================================
# Targeted domain tests for mutation coverage
# =============================================================================
# These test PostActionValidator directly to catch fine-grained mutations
# that the EnforcementEngine driving-port tests miss.

import json

from pes.domain.post_action_validator import PostActionValidator, WAVE_DIR_NAMES


# --- B5: _check_artifact_placement with correct/incorrect wave dirs ---


class TestArtifactPlacementDirect:

    def test_correct_wave_dir_returns_no_warnings(self) -> None:
        validator = PostActionValidator()
        state = {"current_wave": 3}
        result = validator._check_artifact_placement(
            state, "artifacts/wave-3-outline/draft.md"
        )
        assert result == []

    @pytest.mark.parametrize("current_wave,expected_dir", [
        (0, "wave-0-discovery"),
        (1, "wave-1-strategy"),
        (2, "wave-2-research"),
        (3, "wave-3-outline"),
        (4, "wave-4-drafting"),
        (5, "wave-5-visuals"),
        (6, "wave-6-format"),
        (7, "wave-7-review"),
        (8, "wave-8-submission"),
        (9, "wave-9-learning"),
    ])
    def test_wave_dir_names_are_correct(self, current_wave: int, expected_dir: str) -> None:
        assert WAVE_DIR_NAMES[current_wave] == expected_dir

    def test_wrong_wave_dir_returns_warning_with_both_dirs(self) -> None:
        validator = PostActionValidator()
        state = {"current_wave": 4}
        result = validator._check_artifact_placement(
            state, "artifacts/wave-3-outline/draft.md"
        )
        assert len(result) == 1
        assert "wave-3-outline" in result[0]
        assert "wave-4-drafting" in result[0]

    def test_no_wave_dir_in_path_returns_no_warnings(self) -> None:
        validator = PostActionValidator()
        state = {"current_wave": 4}
        result = validator._check_artifact_placement(
            state, "artifacts/some-other-dir/file.md"
        )
        assert result == []

    def test_backslash_paths_normalized(self) -> None:
        validator = PostActionValidator()
        state = {"current_wave": 4}
        result = validator._check_artifact_placement(
            state, "artifacts\\wave-4-drafting\\file.md"
        )
        assert result == []

    def test_unknown_wave_uses_fallback_dir_name(self) -> None:
        validator = PostActionValidator()
        state = {"current_wave": 99}
        result = validator._check_artifact_placement(
            state, "artifacts/wave-99-unknown/file.md"
        )
        assert len(result) == 1


# --- B6: _check_state_wellformed with valid/invalid/missing JSON ---


class TestStateFileWellformedDirect:

    def test_valid_json_returns_no_warnings(self, tmp_path) -> None:
        state_file = tmp_path / "proposal-state.json"
        state_file.write_text(json.dumps({"key": "value"}))

        validator = PostActionValidator()
        result = validator._check_state_file(str(state_file))
        assert result == []

    def test_invalid_json_returns_malformed_warning(self, tmp_path) -> None:
        state_file = tmp_path / "proposal-state.json"
        state_file.write_text("{not valid json")

        validator = PostActionValidator()
        result = validator._check_state_file(str(state_file))
        assert len(result) == 1
        assert "malformed" in result[0].lower()

    def test_missing_file_returns_not_found_warning(self, tmp_path) -> None:
        validator = PostActionValidator()
        result = validator._check_state_file(str(tmp_path / "nonexistent.json"))
        assert len(result) == 1
        assert "not found" in result[0].lower()


# --- B7: _check_artifact_exists with existing/missing files ---


class TestArtifactExistsDirect:

    def test_existing_file_returns_no_warnings(self, tmp_path) -> None:
        f = tmp_path / "artifact.md"
        f.write_text("content")

        validator = PostActionValidator()
        result = validator._check_artifact_exists(str(f))
        assert result == []

    def test_missing_absolute_file_returns_warning(self, tmp_path) -> None:
        missing = str(tmp_path / "nonexistent.md")

        validator = PostActionValidator()
        result = validator._check_artifact_exists(missing)
        assert len(result) == 1
        assert "not created" in result[0].lower()

    def test_relative_path_skips_existence_check(self) -> None:
        validator = PostActionValidator()
        result = validator._check_artifact_exists("relative/path/file.md")
        assert result == []


# --- B8: validate() orchestration ---


class TestValidateOrchestration:

    def test_non_write_tool_returns_no_warnings(self) -> None:
        validator = PostActionValidator()
        result = validator.validate(
            {"current_wave": 4}, "Read", {"file_path": "anything"}
        )
        assert result == []

    @pytest.mark.parametrize("tool_name", ["Write", "Edit"])
    def test_write_tools_trigger_validation(self, tool_name: str, tmp_path) -> None:
        validator = PostActionValidator()
        missing = str(tmp_path / "artifacts" / "wave-4-drafting" / "missing.md")
        result = validator.validate(
            {"current_wave": 4}, tool_name, {"file_path": missing}
        )
        assert len(result) >= 1

    def test_state_file_validation_triggered_by_filename(self, tmp_path) -> None:
        state_file = tmp_path / "proposal-state.json"
        state_file.write_text("{bad json")

        validator = PostActionValidator()
        result = validator.validate(
            {"current_wave": 0}, "Write", {"file_path": str(state_file)}
        )
        assert any("malformed" in m.lower() for m in result)

    def test_non_artifact_non_state_write_returns_no_warnings(self) -> None:
        validator = PostActionValidator()
        result = validator.validate(
            {"current_wave": 4}, "Write", {"file_path": "some/regular/file.md"}
        )
        assert result == []
