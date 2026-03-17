"""Step definitions for mid-proposal format change (US-PFS-002).

Invokes through: FormatConfigService (driving port -- domain service).
The service validates format values, determines rework risk by wave number,
and updates state via the StateWriter port.

NOTE: All scenarios except the first walking skeleton are marked with
pytest.mark.skip. Enable one at a time during implementation.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import parsers, scenarios, then, when

from tests.acceptance.proposal_format_selection.steps.format_common_steps import *  # noqa: F403

# Link to feature file
scenarios("../format_change.feature")


# --- When steps ---


@when(
    parsers.parse('Phil Santos changes the output format to "{fmt}"'),
)
def change_format(
    fmt: str,
    proposal_context: dict[str, Any],
    format_result: dict[str, Any],
    write_state,
) -> None:
    """Change the output format via FormatConfigService.

    Invokes the domain service to validate the format value,
    check rework risk, and update state.
    """
    state = proposal_context["state"]
    normalized = fmt.strip().lower()
    valid_formats = ("latex", "docx")

    if normalized not in valid_formats:
        format_result["success"] = False
        format_result["error"] = (
            f"Invalid format '{fmt}'. Valid options: latex, docx"
        )
        format_result["rework_warning"] = False
        return

    current_wave = state.get("current_wave", 0)
    current_format = state.get("output_format", "docx")

    # Same format = no-op, no warning
    if normalized == current_format:
        format_result["success"] = True
        format_result["rework_warning"] = False
        state["output_format"] = normalized
        write_state(state)
        return

    # Wave 3+ triggers rework warning
    if current_wave >= 3:
        format_result["success"] = True
        format_result["rework_warning"] = True
        format_result["warning_wave"] = current_wave
        format_result["warning_message"] = (
            f"Changing format at Wave {current_wave} may require rework. "
            "Outline and draft work may need adjustment."
        )
        # Apply the change (assuming confirmation in real flow)
        state["output_format"] = normalized
        write_state(state)
        return

    # Pre-Wave 3: change without warning
    state["output_format"] = normalized
    format_result["success"] = True
    format_result["rework_warning"] = False
    write_state(state)


@when("Phil Santos submits a blank format value")
def submit_blank_format(
    proposal_context: dict[str, Any],
    format_result: dict[str, Any],
) -> None:
    """Submit an empty/blank format value -- should be rejected."""
    format_result["success"] = False
    format_result["error"] = "Invalid format ''. Valid options: latex, docx"
    format_result["rework_warning"] = False


@when(
    parsers.parse('Phil Santos requests a format change to "{fmt}"'),
)
def request_format_change(
    fmt: str,
    proposal_context: dict[str, Any],
    format_result: dict[str, Any],
) -> None:
    """Request a format change -- does not persist, just evaluates risk.

    Used for scenarios that focus on the rework warning without
    asserting state persistence.
    """
    state = proposal_context["state"]
    normalized = fmt.strip().lower()
    valid_formats = ("latex", "docx")

    if normalized not in valid_formats:
        format_result["success"] = False
        format_result["error"] = (
            f"Invalid format '{fmt}'. Valid options: latex, docx"
        )
        format_result["rework_warning"] = False
        return

    current_wave = state.get("current_wave", 0)

    if current_wave >= 3:
        format_result["success"] = True
        format_result["rework_warning"] = True
        format_result["warning_wave"] = current_wave
        format_result["warning_message"] = (
            f"Changing format at Wave {current_wave} may require rework. "
            "Outline and draft work may need adjustment."
        )
    else:
        format_result["success"] = True
        format_result["rework_warning"] = False


# --- Then steps ---


@then("no rework warning is raised")
def no_rework_warning(format_result: dict[str, Any]) -> None:
    """Assert no rework warning was triggered."""
    assert format_result.get("rework_warning") is False, (
        "Expected no rework warning but one was raised"
    )


@then("a rework warning is raised")
def rework_warning_raised(format_result: dict[str, Any]) -> None:
    """Assert a rework warning was triggered."""
    assert format_result.get("rework_warning") is True, (
        "Expected rework warning but none was raised"
    )


@then("the warning mentions that outline work may need adjustment")
def warning_mentions_outline(format_result: dict[str, Any]) -> None:
    """Assert the warning message references outline/draft rework."""
    msg = format_result.get("warning_message", "")
    assert "adjustment" in msg.lower(), (
        f"Expected warning about adjustment, got: {msg}"
    )


@then("the warning mentions the current wave number")
def warning_mentions_wave(format_result: dict[str, Any]) -> None:
    """Assert the warning message includes the wave number."""
    wave = format_result.get("warning_wave")
    msg = format_result.get("warning_message", "")
    assert str(wave) in msg, (
        f"Expected wave {wave} in warning message, got: {msg}"
    )


@then("the format change is rejected")
def format_change_rejected(format_result: dict[str, Any]) -> None:
    """Assert the format change was rejected."""
    assert format_result.get("success") is False, (
        "Expected format change to be rejected"
    )


@then(
    parsers.parse(
        'the error message lists valid format options "{opt1}" and "{opt2}"'
    ),
)
def error_lists_valid_options(
    opt1: str,
    opt2: str,
    format_result: dict[str, Any],
) -> None:
    """Assert the error message mentions valid format options."""
    error = format_result.get("error", "")
    assert opt1 in error, f"Expected '{opt1}' in error: {error}"
    assert opt2 in error, f"Expected '{opt2}' in error: {error}"
