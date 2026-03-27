"""Claude Code hook protocol adapter.

Translates JSON stdin/stdout and exit codes to EnforcementEngine calls.
Hook protocol: JSON on stdin, JSON on stdout, exit codes 0=allow, 1=block, 2=reject.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pes.adapters.file_audit_adapter import FileAuditAdapter
from pes.adapters.json_rule_adapter import JsonRuleAdapter
from pes.adapters.json_state_adapter import JsonStateAdapter
from pes.domain.engine import EnforcementEngine
from pes.domain.rules import Decision, EnforcementResult
from pes.domain.state import StateNotFoundError

# Prerequisite files checked when file_path targets wave-5-visuals/
_WAVE5_PREREQUISITES = ("figure-specs.md", "style-profile.yaml")

# Path segment that identifies visual asset directories
_WAVE5_VISUALS_SEGMENT = "wave-5-visuals"

# Path segment that identifies drafting directories
_WAVE4_DRAFTING_SEGMENT = "wave-4-drafting"

# Path segment that identifies outline directories
_WAVE3_OUTLINE_SEGMENT = "wave-3-outline"

# Outline artifacts checked in sibling wave-3-outline/ when targeting wave-4-drafting/
_OUTLINE_ARTIFACTS = ("proposal-outline.md",)

# Global artifacts checked when file_path targets wave-4-drafting/
_GLOBAL_ARTIFACTS = ("quality-preferences.json",)


def _detect_wave_segment(normalized: str, segment_name: str) -> bool:
    """Check if a normalized path contains a wave segment directory."""
    marker = f"/{segment_name}/"
    return marker in normalized or normalized.endswith(f"/{segment_name}")


def _find_wave_dir(file_path: str, normalized: str, segment_name: str) -> str:
    """Extract the wave directory portion from a file path."""
    marker = f"/{segment_name}/"
    segment_idx = normalized.find(marker)
    if segment_idx == -1:
        # Path ends with segment (no trailing slash)
        return file_path
    return file_path[: segment_idx + len(segment_name) + 1]


def _resolve_global_artifacts() -> list[str]:
    """Check ~/.sbir/ for global artifact files (quality-preferences.json)."""
    sbir_global = Path.home() / ".sbir"
    found = []
    for artifact in _GLOBAL_ARTIFACTS:
        if (sbir_global / artifact).is_file():
            found.append(artifact)
    return found


def resolve_tool_context(hook_input: dict[str, Any]) -> dict[str, Any]:
    """Extract file_path from hook input and resolve artifact prerequisites.

    For PreToolUse events, extracts file_path from hook_input['tool']['file_path'].
    When the path targets a wave-5-visuals/ directory, checks disk for prerequisite
    files (figure-specs.md, style-profile.yaml) and reports which are present.
    When the path targets a wave-4-drafting/ directory, checks ~/.sbir/ for global
    artifacts (quality-preferences.json) and populates global_artifacts_present.
    Also checks the sibling wave-3-outline/ directory for proposal-outline.md
    and populates outline_artifacts_present.

    Supports both multi-proposal (artifacts/{topic-id}/wave-N-name/) and
    legacy (artifacts/wave-N-name/) path layouts.

    Returns:
        Dict with 'file_path' (str), 'artifacts_present' (list),
        'global_artifacts_present' (list), and 'outline_artifacts_present' (list)
        when relevant wave paths detected.
    """
    file_path = hook_input.get("tool", {}).get("file_path", "")
    if not file_path:
        return {
            "file_path": "",
            "artifacts_present": [],
            "global_artifacts_present": [],
            "outline_artifacts_present": [],
        }

    # Normalize path separators for cross-platform compatibility
    normalized = file_path.replace("\\", "/")

    is_wave5 = _detect_wave_segment(normalized, _WAVE5_VISUALS_SEGMENT)
    is_wave4 = _detect_wave_segment(normalized, _WAVE4_DRAFTING_SEGMENT)

    # For paths outside both wave-5-visuals/ and wave-4-drafting/
    if not is_wave5 and not is_wave4:
        return {
            "file_path": file_path,
            "artifacts_present": [],
            "global_artifacts_present": [],
            "outline_artifacts_present": [],
        }

    # Resolve wave-5-visuals local prerequisites
    artifacts_present: list[str] = []
    if is_wave5:
        visuals_dir = _find_wave_dir(file_path, normalized, _WAVE5_VISUALS_SEGMENT)
        for prereq in _WAVE5_PREREQUISITES:
            prereq_path = os.path.join(visuals_dir, prereq)
            if os.path.isfile(prereq_path):
                artifacts_present.append(prereq)

    # Resolve global artifacts for wave-4-drafting
    global_artifacts_present: list[str] = []
    outline_artifacts_present: list[str] = []
    if is_wave4:
        global_artifacts_present = _resolve_global_artifacts()

        # Resolve outline artifacts from sibling wave-3-outline/ directory
        wave4_dir = _find_wave_dir(file_path, normalized, _WAVE4_DRAFTING_SEGMENT)
        outline_dir = wave4_dir.replace(_WAVE4_DRAFTING_SEGMENT, _WAVE3_OUTLINE_SEGMENT)
        for artifact in _OUTLINE_ARTIFACTS:
            if os.path.isfile(os.path.join(outline_dir, artifact)):
                outline_artifacts_present.append(artifact)

    return {
        "file_path": file_path,
        "artifacts_present": artifacts_present,
        "global_artifacts_present": global_artifacts_present,
        "outline_artifacts_present": outline_artifacts_present,
    }


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
    audit_dir = os.path.join(state_dir, "audit")
    audit_logger = FileAuditAdapter(audit_dir)
    engine = EnforcementEngine(rule_loader, audit_logger)

    handler = _EVENT_HANDLERS.get(event)
    if handler is None:
        return {"exit_code": 0}  # unknown event -- allow

    return handler(engine, state_dir, hook_input)


def _load_state(state_dir: str) -> dict[str, Any] | None:
    """Load proposal state, returning None if not found."""
    try:
        return JsonStateAdapter(state_dir).load()
    except StateNotFoundError:
        return None


def _to_exit_response(result: EnforcementResult) -> dict[str, Any]:
    """Convert enforcement result to hook exit response."""
    if result.decision == Decision.BLOCK:
        return {"exit_code": 1, "message": "; ".join(result.messages)}
    response: dict[str, Any] = {"exit_code": 0}
    if result.messages:
        response["message"] = "; ".join(result.messages)
    return response


def _handle_session_start(
    engine: EnforcementEngine, state_dir: str, hook_input: dict[str, Any]
) -> dict[str, Any]:
    """Handle SessionStart event -- integrity check."""
    state = _load_state(state_dir)
    if state is None:
        return {"exit_code": 0}
    result = engine.check_session_start(state)
    return {"exit_code": 0 if result.decision == Decision.ALLOW else 1}


def _handle_pre_tool_use(
    engine: EnforcementEngine, state_dir: str, hook_input: dict[str, Any]
) -> dict[str, Any]:
    """Handle PreToolUse event -- rule evaluation.

    Extracts file_path from tool info, resolves wave-5-visuals artifact
    prerequisites, and passes tool_context to engine.evaluate().
    """
    state = _load_state(state_dir)
    if state is None:
        return {"exit_code": 0}
    tool_name = hook_input.get("tool", {}).get("name", "")
    tool_context = resolve_tool_context(hook_input)
    return _to_exit_response(
        engine.evaluate(state, tool_name=tool_name, tool_context=tool_context)
    )


def _handle_subagent_start(
    engine: EnforcementEngine, state_dir: str, hook_input: dict[str, Any]
) -> dict[str, Any]:
    """Handle SubagentStart event -- agent-wave authorization check."""
    state = _load_state(state_dir)
    agent_name = hook_input.get("agent_type", "")
    return _to_exit_response(engine.check_agent_dispatch(state, agent_name))


def _handle_subagent_stop(
    engine: EnforcementEngine, state_dir: str, hook_input: dict[str, Any]
) -> dict[str, Any]:
    """Handle SubagentStop event -- record agent deactivation in audit trail."""
    state = _load_state(state_dir)
    if state is None:
        return {"exit_code": 0}
    agent_name = hook_input.get("agent_type", "")
    engine.record_agent_stop(state, agent_name)
    return {"exit_code": 0}


# Tools that only read data -- skip post-action validation entirely
READ_ONLY_TOOLS = {"Read", "Glob", "Grep"}


def _handle_post_tool_use(
    engine: EnforcementEngine, state_dir: str, hook_input: dict[str, Any]
) -> dict[str, Any]:
    """Handle PostToolUse event -- post-action validation.

    Skips validation for read-only tools (Read, Glob, Grep).
    Ensures audit directory exists before validation (infrastructure concern).
    """
    tool_info = hook_input.get("tool", {})
    tool_name = tool_info.get("name", "")

    if tool_name in READ_ONLY_TOOLS:
        return {"exit_code": 0}

    state = _load_state(state_dir)
    if state is None:
        return {"exit_code": 0}

    # Ensure audit directory exists (infrastructure concern stays in adapter)
    audit_dir = os.path.join(state_dir, "audit")
    os.makedirs(audit_dir, exist_ok=True)

    artifact_info = {
        "tool_name": tool_name,
        "file_path": tool_info.get("file_path", ""),
    }
    result = engine.check_post_action(state, tool_name, artifact_info)
    return _to_exit_response(result)


# Event name -> handler dispatch table
_EVENT_HANDLERS: dict[
    str,
    Callable[
        [EnforcementEngine, str, dict[str, Any]],
        dict[str, Any],
    ],
] = {
    "SessionStart": _handle_session_start,
    "PreToolUse": _handle_pre_tool_use,
    "PostToolUse": _handle_post_tool_use,
    "SubagentStart": _handle_subagent_start,
    "SubagentStop": _handle_subagent_stop,
}


def main() -> None:
    """CLI entry point for Claude Code hooks.

    Usage: python -m pes.adapters.hook_adapter <event-type>
    Reads JSON from stdin, writes JSON to stdout, exits with 0=allow or 1=block.
    """
    import json
    import os
    import sys

    if len(sys.argv) < 2:
        msg = (
            "Usage: hook_adapter "
            "<session-start|subagent-start|subagent-stop|pre-tool-use|post-tool-use>"
        )
        print(json.dumps({"error": msg}))
        sys.exit(2)

    subcommand = sys.argv[1]
    event_map = {
        "session-start": "SessionStart",
        "subagent-start": "SubagentStart",
        "subagent-stop": "SubagentStop",
        "pre-tool-use": "PreToolUse",
        "post-tool-use": "PostToolUse",
    }

    event = event_map.get(subcommand)
    if event is None:
        print(json.dumps({"error": f"Unknown subcommand: {subcommand}"}))
        sys.exit(2)

    # Read hook input from stdin
    try:
        raw = sys.stdin.read()
        hook_input = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, ValueError):
        hook_input = {}

    hook_input["event"] = event

    # Resolve workspace layout and derive state_dir
    from pathlib import Path

    from pes.adapters.workspace_resolver import WorkspaceResolutionError, resolve_workspace

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", os.getcwd())
    config_path = os.path.join(plugin_root, "templates", "pes-config.json")

    workspace_root = Path(os.getcwd())
    try:
        ctx = resolve_workspace(workspace_root)
    except WorkspaceResolutionError:
        # Cannot resolve workspace -- allow hook to proceed
        sys.exit(0)

    if ctx.layout == "fresh":
        # No proposal state -- nothing to enforce
        sys.exit(0)

    state_dir = str(ctx.state_dir)
    result = process_hook_event(hook_input, state_dir, config_path)

    exit_code = result.pop("exit_code", 0)
    if result:
        print(json.dumps(result))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
