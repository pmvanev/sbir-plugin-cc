"""Tests for hook_adapter CLI entry point (main function).

Verifies the __main__ block that hooks.json invokes:
  python -m pes.adapters.hook_adapter <session-start|pre-tool-use>
"""

from __future__ import annotations

import json
import subprocess
import sys


def _run_hook(subcommand: str, stdin_data: str = "{}") -> tuple[int, str, str]:
    """Run hook_adapter as subprocess, return (exit_code, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "pes.adapters.hook_adapter", subcommand],
        input=stdin_data,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "scripts", "PATH": ""},
        cwd=".",
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


class TestHookAdapterCli:
    """CLI entry point tests."""

    def test_session_start_no_state_exits_0(self) -> None:
        exit_code, stdout, _ = _run_hook("session-start")
        assert exit_code == 0

    def test_pre_tool_use_no_state_exits_0(self) -> None:
        exit_code, stdout, _ = _run_hook("pre-tool-use", '{"tool": {"name": "Write"}}')
        assert exit_code == 0

    def test_unknown_subcommand_exits_2(self) -> None:
        exit_code, stdout, _ = _run_hook("bad-command")
        assert exit_code == 2
        output = json.loads(stdout)
        assert "Unknown subcommand" in output["error"]

    def test_empty_stdin_does_not_crash(self) -> None:
        exit_code, _, _ = _run_hook("session-start", "")
        assert exit_code == 0

    def test_invalid_json_stdin_does_not_crash(self) -> None:
        exit_code, _, _ = _run_hook("session-start", "not-json{{{")
        assert exit_code == 0
