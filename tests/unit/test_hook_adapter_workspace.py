"""Tests for hook adapter integration with workspace path resolution.

Verifies that hook_adapter.main() uses workspace_resolver to determine
state_dir and audit_dir instead of hardcoding .sbir path.

Driving port: process_hook_event() for direct behavior testing,
main() via monkeypatched os.getcwd() for CLI integration.

Test Budget: 4 behaviors x 2 = 8 max unit tests
Behaviors:
1. Multi-proposal workspace: hooks resolve state from active proposal
2. Legacy workspace: hooks resolve state from root .sbir (backward compatible)
3. Fresh workspace: hooks allow without enforcement (exit 0)
4. Audit dir sourced from workspace context
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from pes.adapters.hook_adapter import main, process_hook_event
from tests.acceptance.multi_proposal_workspace.conftest import make_proposal_state


def _make_config(tmp_path: Path, rules: list | None = None) -> str:
    """Create pes-config.json and return its path."""
    config = {"rules": rules or []}
    config_path = tmp_path / "pes-config.json"
    config_path.write_text(json.dumps(config))
    return str(config_path)


def _wave_ordering_rule() -> dict:
    """Standard wave ordering rule for testing."""
    return {
        "rule_id": "wave-1-requires-go",
        "description": "Wave 1 requires Go decision",
        "rule_type": "wave_ordering",
        "condition": {"requires_go_no_go": "go", "target_wave": 1},
        "message": "Wave 1 requires Go decision in Wave 0",
    }


def _make_state(**overrides) -> dict:
    """Build minimal state dict compatible with PES engine."""
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
    state.update(overrides)
    return state


# --- Behavior 1: Multi-proposal workspace hooks use resolved state ---


def test_multi_proposal_hooks_resolve_state_from_active_proposal(
    tmp_path: Path,
) -> None:
    """In multi-proposal workspace, hooks read state from active proposal namespace."""
    sbir = tmp_path / ".sbir"
    sbir.mkdir()
    proposals = sbir / "proposals"
    proposals.mkdir()

    # Active proposal has pending go/no-go
    pa = proposals / "af263-042"
    pa.mkdir()
    (pa / "audit").mkdir()
    (pa / "proposal-state.json").write_text(json.dumps(_make_state()))

    (sbir / "active-proposal").write_text("af263-042")

    config_path = _make_config(tmp_path, [_wave_ordering_rule()])

    hook_input = {"event": "PreToolUse", "tool": {"name": "wave_1_strategy"}}

    # The resolved state_dir should be proposals/af263-042
    result = process_hook_event(
        hook_input,
        state_dir=str(pa),  # This is what workspace_resolver would return
        config_path=config_path,
    )
    # Pending go/no-go + wave ordering rule -> block
    assert result["exit_code"] == 1
    assert "Wave 1 requires Go decision" in result.get("message", "")


# --- Behavior 2: Legacy workspace backward compatibility ---


def test_legacy_workspace_hooks_use_root_sbir(tmp_path: Path) -> None:
    """Legacy workspace produces same hook behavior using root .sbir."""
    sbir = tmp_path / ".sbir"
    sbir.mkdir()
    (sbir / "proposal-state.json").write_text(json.dumps(_make_state()))

    config_path = _make_config(tmp_path, [_wave_ordering_rule()])

    hook_input = {"event": "PreToolUse", "tool": {"name": "wave_1_strategy"}}

    result = process_hook_event(
        hook_input,
        state_dir=str(sbir),  # Legacy: root .sbir
        config_path=config_path,
    )
    assert result["exit_code"] == 1
    assert "Wave 1 requires Go decision" in result.get("message", "")


# --- Behavior 3: Fresh workspace allows without enforcement ---


def test_fresh_workspace_main_allows_all_hooks(tmp_path: Path) -> None:
    """main() in fresh workspace (no .sbir) exits 0 without enforcement."""
    config_path = _make_config(tmp_path)

    with (
        patch("os.getcwd", return_value=str(tmp_path)),
        patch("os.environ", {"CLAUDE_PLUGIN_ROOT": str(tmp_path)}),
        patch("sys.argv", ["hook_adapter", "session-start"]),
        patch("sys.stdin") as mock_stdin,
        pytest.raises(SystemExit) as exc_info,
    ):
        mock_stdin.read.return_value = "{}"
        # Need config file at expected location
        templates = tmp_path / "templates"
        templates.mkdir(exist_ok=True)
        (templates / "pes-config.json").write_text(json.dumps({"rules": []}))

        main()

    assert exc_info.value.code == 0


# --- Behavior 4: Audit dir from workspace context ---


def test_process_hook_event_uses_audit_dir_from_state_dir(tmp_path: Path) -> None:
    """Audit dir is derived from state_dir, not hardcoded root .sbir/audit."""
    # Set up proposal namespace as state_dir
    proposal_dir = tmp_path / "proposals" / "af263-042"
    proposal_dir.mkdir(parents=True)
    audit_dir = proposal_dir / "audit"
    audit_dir.mkdir()

    state = _make_state(go_no_go="go", current_wave=1)
    state["strategy_brief"] = {"status": "complete"}
    state["compliance_matrix"] = {"item_count": 3}
    (proposal_dir / "proposal-state.json").write_text(json.dumps(state))

    config_path = _make_config(tmp_path)

    hook_input = {
        "event": "PostToolUse",
        "tool": {"name": "Write", "file_path": "/some/file.py"},
    }

    result = process_hook_event(
        hook_input,
        state_dir=str(proposal_dir),
        config_path=config_path,
    )
    assert result["exit_code"] == 0
    # Verify audit was written to proposal_dir/audit, not some other location
    # The FileAuditAdapter creates audit entries in state_dir/audit
    audit_files = list(audit_dir.iterdir())
    assert len(audit_files) >= 1, "Audit entry should be written to per-proposal audit dir"


def test_main_resolves_multi_workspace_state_dir(tmp_path: Path) -> None:
    """main() uses workspace_resolver to resolve state_dir for multi-proposal."""
    sbir = tmp_path / ".sbir"
    sbir.mkdir()
    proposals = sbir / "proposals"
    proposals.mkdir()

    pa = proposals / "af263-042"
    pa.mkdir()
    (pa / "audit").mkdir()
    (pa / "proposal-state.json").write_text(json.dumps(_make_state()))

    (sbir / "active-proposal").write_text("af263-042")

    templates = tmp_path / "templates"
    templates.mkdir()
    config = {"rules": [_wave_ordering_rule()]}
    (templates / "pes-config.json").write_text(json.dumps(config))

    with (
        patch("os.getcwd", return_value=str(tmp_path)),
        patch("os.environ", {"CLAUDE_PLUGIN_ROOT": str(tmp_path)}),
        patch("sys.argv", ["hook_adapter", "pre-tool-use"]),
        patch("sys.stdin") as mock_stdin,
        pytest.raises(SystemExit) as exc_info,
    ):
        mock_stdin.read.return_value = json.dumps(
            {"tool": {"name": "wave_1_strategy"}}
        )
        main()

    # Should block because af263-042 has pending go_no_go
    assert exc_info.value.code == 1
