"""Tests for ClaudeCodeHookAdapter -- hook protocol translation.

Tests invoke through the HookAdapter public API with fake adapters
at port boundaries (EnforcementEngine, StateReader).

The hook adapter is responsible for:
- Parsing JSON from stdin (hook event)
- Invoking EnforcementEngine
- Producing JSON stdout with correct exit code

Test Budget: 3 behaviors x 2 = 6 max unit tests
"""

from __future__ import annotations

import json

from pes.adapters.hook_adapter import process_hook_event


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
