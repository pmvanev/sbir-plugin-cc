"""Claude Code hook protocol adapter.

Translates JSON stdin/stdout and exit codes to EnforcementEngine calls.
Hook protocol: JSON on stdin, JSON on stdout, exit codes 0=allow, 1=block, 2=reject.
"""

from __future__ import annotations

from typing import Any

from pes.adapters.json_rule_adapter import JsonRuleAdapter
from pes.adapters.json_state_adapter import JsonStateAdapter
from pes.domain.engine import EnforcementEngine
from pes.domain.rules import Decision
from pes.domain.state import StateNotFoundError
from pes.ports.audit_port import AuditLogger


class _NullAuditLogger(AuditLogger):
    """No-op audit logger for when no audit path is configured."""

    def log(self, entry: dict[str, Any]) -> None:
        pass


def process_hook_event(
    hook_input: dict[str, Any],
    state_dir: str,
    config_path: str,
) -> dict[str, Any]:
    """Process a Claude Code hook event and return result with exit_code.

    Args:
        hook_input: Parsed JSON from stdin containing event type and data.
        state_dir: Path to .sbir directory containing proposal state.
        config_path: Path to pes-config.json.

    Returns:
        Dict with 'exit_code' (0=allow, 1=block) and optional 'message'.
    """
    event = hook_input.get("event", "")
    rule_loader = JsonRuleAdapter(config_path)
    audit_logger = _NullAuditLogger()
    engine = EnforcementEngine(rule_loader, audit_logger)

    if event == "SessionStart":
        return _handle_session_start(engine, state_dir)

    if event == "PreToolUse":
        tool_name = hook_input.get("tool", {}).get("name", "")
        return _handle_pre_tool_use(engine, state_dir, tool_name)

    return {"exit_code": 0}


def _handle_session_start(engine: EnforcementEngine, state_dir: str) -> dict[str, Any]:
    """Handle SessionStart event -- integrity check."""
    state_reader = JsonStateAdapter(state_dir)
    try:
        state = state_reader.load()
    except StateNotFoundError:
        return {"exit_code": 0}

    result = engine.check_session_start(state)
    return {"exit_code": 0 if result.decision == Decision.ALLOW else 1}


def _handle_pre_tool_use(
    engine: EnforcementEngine, state_dir: str, tool_name: str
) -> dict[str, Any]:
    """Handle PreToolUse event -- rule evaluation."""
    state_reader = JsonStateAdapter(state_dir)
    try:
        state = state_reader.load()
    except StateNotFoundError:
        return {"exit_code": 0}

    result = engine.evaluate(state, tool_name=tool_name)

    if result.decision == Decision.BLOCK:
        return {
            "exit_code": 1,
            "message": "; ".join(result.messages),
        }

    return {"exit_code": 0}
