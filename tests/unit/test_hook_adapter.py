"""Tests for ClaudeCodeHookAdapter -- hook protocol translation.

Tests invoke through the HookAdapter public API with fake adapters
at port boundaries (EnforcementEngine, StateReader).

The hook adapter is responsible for:
- Parsing JSON from stdin (hook event)
- Invoking EnforcementEngine
- Producing JSON stdout with correct exit code
- Extracting file_path from PreToolUse events and resolving artifact context
- Resolving global artifacts (~/.sbir/) for wave-4-drafting paths

Test Budget: 11 behaviors x 2 = 22 max unit tests (9 existing + 5 new)
"""

from __future__ import annotations

import json

from pes.adapters.hook_adapter import process_hook_event, resolve_tool_context


class TestHookAdapterSessionStart:
    """SessionStart hook event handling."""

    def test_session_start_clean_state_returns_exit_code_0(self, tmp_path) -> None:
        sbir_dir = tmp_path / ".sbir"
        sbir_dir.mkdir()

        hook_input = {
            "event": "SessionStart",
            "session": {"id": "test-session-001"},
        }
        result = process_hook_event(
            hook_input,
            state_dir=str(sbir_dir),
            config_path=str(sbir_dir / "pes-config.json"),
        )
        assert result["exit_code"] == 0

    def test_session_start_no_state_returns_exit_code_0(self, tmp_path) -> None:
        """Missing state file should not block session start."""
        nonexistent = tmp_path / "nonexistent" / ".sbir"

        hook_input = {
            "event": "SessionStart",
            "session": {"id": "test-session-002"},
        }
        result = process_hook_event(
            hook_input,
            state_dir=str(nonexistent),
            config_path=str(nonexistent / "pes-config.json"),
        )
        assert result["exit_code"] == 0


class TestHookAdapterPreToolUse:
    """PreToolUse hook event handling."""

    def test_pre_tool_use_blocked_returns_exit_code_1_with_message(
        self, tmp_path,
    ) -> None:
        # Set up state with pending Go/No-Go
        sbir_dir = tmp_path / ".sbir"
        sbir_dir.mkdir()
        state_file = sbir_dir / "proposal-state.json"
        state = {
            "schema_version": "1.0.0",
            "proposal_id": "test-uuid",
            "go_no_go": "pending",
            "current_wave": 0,
            "waves": {"0": {"status": "active", "completed_at": None}},
            "topic": {"deadline": "2026-04-15"},
            "strategy_brief": {"status": "not_started"},
            "compliance_matrix": {"item_count": 0},
        }
        state_file.write_text(json.dumps(state))

        # Write config with wave ordering rule
        config = {
            "rules": [
                {
                    "rule_id": "wave-1-requires-go",
                    "description": "Wave 1 requires Go decision",
                    "rule_type": "wave_ordering",
                    "condition": {"requires_go_no_go": "go", "target_wave": 1},
                    "message": "Wave 1 requires Go decision in Wave 0",
                }
            ]
        }
        config_file = sbir_dir / "pes-config.json"
        config_file.write_text(json.dumps(config))

        hook_input = {
            "event": "PreToolUse",
            "tool": {"name": "wave_1_strategy"},
        }
        result = process_hook_event(
            hook_input,
            state_dir=str(sbir_dir),
            config_path=str(config_file),
        )
        assert result["exit_code"] == 1
        assert "Wave 1 requires Go decision" in result.get("message", "")


class TestResolveToolContext:
    """Tool context resolution for PreToolUse events.

    resolve_tool_context extracts file_path from hook input, detects
    wave-5-visuals/ paths, and checks prerequisite file existence on disk.
    """

    def test_wave5_visuals_path_with_existing_prerequisites(self, tmp_path) -> None:
        """When file_path targets wave-5-visuals/ and prerequisites exist, they appear in artifacts_present."""
        # Create artifact directory with prerequisites
        artifact_dir = tmp_path / "artifacts" / "sf25d-t1201" / "wave-5-visuals"
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "figure-specs.md").write_text("# Specs")
        (artifact_dir / "style-profile.yaml").write_text("style: default")

        file_path = str(artifact_dir / "figure-1-arch.svg")
        hook_input = {"tool": {"name": "Write", "file_path": file_path}}

        ctx = resolve_tool_context(hook_input)

        assert ctx["file_path"] == file_path
        assert "figure-specs.md" in ctx["artifacts_present"]
        assert "style-profile.yaml" in ctx["artifacts_present"]

    def test_wave5_visuals_path_without_prerequisites(self, tmp_path) -> None:
        """When file_path targets wave-5-visuals/ but no prerequisites exist, artifacts_present is empty."""
        artifact_dir = tmp_path / "artifacts" / "sf25d-t1201" / "wave-5-visuals"
        artifact_dir.mkdir(parents=True)

        file_path = str(artifact_dir / "figure-1-arch.svg")
        hook_input = {"tool": {"name": "Write", "file_path": file_path}}

        ctx = resolve_tool_context(hook_input)

        assert ctx["file_path"] == file_path
        assert ctx["artifacts_present"] == []

    def test_non_wave5_path_returns_empty_artifacts(self, tmp_path) -> None:
        """When file_path is outside wave-5-visuals/, artifacts_present is empty."""
        file_path = str(tmp_path / "artifacts" / "sf25d-t1201" / "wave-4-drafting" / "section-1.md")
        hook_input = {"tool": {"name": "Write", "file_path": file_path}}

        ctx = resolve_tool_context(hook_input)

        assert ctx["file_path"] == file_path
        assert ctx["artifacts_present"] == []

    def test_legacy_layout_wave5_path(self, tmp_path) -> None:
        """Legacy single-proposal layout: artifacts/wave-5-visuals/ (no topic-id subdirectory)."""
        artifact_dir = tmp_path / "artifacts" / "wave-5-visuals"
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "figure-specs.md").write_text("# Specs")

        file_path = str(artifact_dir / "figure-2-flow.svg")
        hook_input = {"tool": {"name": "Write", "file_path": file_path}}

        ctx = resolve_tool_context(hook_input)

        assert ctx["file_path"] == file_path
        assert "figure-specs.md" in ctx["artifacts_present"]

    def test_missing_file_path_returns_empty_context(self) -> None:
        """When hook_input has no file_path, returns empty file_path and no artifacts."""
        hook_input = {"tool": {"name": "Write"}}

        ctx = resolve_tool_context(hook_input)

        assert ctx["file_path"] == ""
        assert ctx["artifacts_present"] == []

    def test_subdirectory_under_wave5_visuals(self, tmp_path) -> None:
        """Files in subdirectories of wave-5-visuals/ also trigger artifact checks."""
        artifact_dir = tmp_path / "artifacts" / "sf25d-t1201" / "wave-5-visuals"
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "style-profile.yaml").write_text("style: default")
        sub_dir = artifact_dir / "external-briefs"
        sub_dir.mkdir()

        file_path = str(sub_dir / "figure-3-brief.md")
        hook_input = {"tool": {"name": "Write", "file_path": file_path}}

        ctx = resolve_tool_context(hook_input)

        assert ctx["file_path"] == file_path
        assert "style-profile.yaml" in ctx["artifacts_present"]
        assert "figure-specs.md" not in ctx["artifacts_present"]


class TestResolveToolContextGlobalArtifacts:
    """Global artifact resolution for wave-4-drafting paths.

    When file_path targets wave-4-drafting/, resolve_tool_context checks
    ~/.sbir/ for quality-preferences.json and populates global_artifacts_present.
    """

    def test_wave4_drafting_path_with_quality_preferences(self, tmp_path, monkeypatch) -> None:
        """When file_path targets wave-4-drafting/ and quality-preferences.json exists at ~/.sbir/,
        global_artifacts_present includes quality-preferences.json."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        sbir_global = fake_home / ".sbir"
        sbir_global.mkdir()
        (sbir_global / "quality-preferences.json").write_text('{"style": "formal"}')
        monkeypatch.setattr("pathlib.Path.home", lambda: fake_home)

        drafting = tmp_path / "artifacts" / "sf25d-t1201" / "wave-4-drafting"
        file_path = str(drafting / "section-1.md")
        hook_input = {"tool": {"name": "Write", "file_path": file_path}}

        ctx = resolve_tool_context(hook_input)

        assert ctx["file_path"] == file_path
        assert "quality-preferences.json" in ctx["global_artifacts_present"]

    def test_wave4_drafting_path_without_quality_preferences(self, tmp_path, monkeypatch) -> None:
        """When wave-4-drafting/ targeted but quality-preferences.json missing,
        global_artifacts_present is empty."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        (fake_home / ".sbir").mkdir()
        monkeypatch.setattr("pathlib.Path.home", lambda: fake_home)

        drafting = tmp_path / "artifacts" / "sf25d-t1201" / "wave-4-drafting"
        file_path = str(drafting / "section-1.md")
        hook_input = {"tool": {"name": "Write", "file_path": file_path}}

        ctx = resolve_tool_context(hook_input)

        assert ctx["file_path"] == file_path
        assert ctx["global_artifacts_present"] == []

    def test_non_wave4_non_wave5_path_no_global_artifacts(self) -> None:
        """When file_path is outside wave-4-drafting/ and wave-5-visuals/,
        global_artifacts_present is empty list."""
        file_path = "/some/project/artifacts/wave-3-strategy/brief.md"
        hook_input = {"tool": {"name": "Write", "file_path": file_path}}

        ctx = resolve_tool_context(hook_input)

        assert ctx["global_artifacts_present"] == []

    def test_wave5_visuals_path_has_empty_global_artifacts(self, tmp_path) -> None:
        """wave-5-visuals/ paths get global_artifacts_present as empty list (not missing)."""
        artifact_dir = tmp_path / "artifacts" / "sf25d-t1201" / "wave-5-visuals"
        artifact_dir.mkdir(parents=True)

        file_path = str(artifact_dir / "figure-1.svg")
        hook_input = {"tool": {"name": "Write", "file_path": file_path}}

        ctx = resolve_tool_context(hook_input)

        assert ctx["global_artifacts_present"] == []
        # Existing artifacts_present behavior unchanged
        assert ctx["artifacts_present"] == []

    def test_legacy_layout_wave4_drafting_path(self, tmp_path, monkeypatch) -> None:
        """Legacy single-proposal layout: artifacts/wave-4-drafting/ (no topic-id)."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        sbir_global = fake_home / ".sbir"
        sbir_global.mkdir()
        (sbir_global / "quality-preferences.json").write_text("{}")
        monkeypatch.setattr("pathlib.Path.home", lambda: fake_home)

        file_path = str(tmp_path / "artifacts" / "wave-4-drafting" / "section-2.md")
        hook_input = {"tool": {"name": "Write", "file_path": file_path}}

        ctx = resolve_tool_context(hook_input)

        assert "quality-preferences.json" in ctx["global_artifacts_present"]
