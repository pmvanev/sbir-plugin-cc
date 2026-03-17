"""Step definitions for mid-proposal format change (US-PFS-002).

Invokes through: FormatConfigService (driving port -- domain service).
The service validates format values, determines rework risk by wave number,
and updates state via the StateWriter port.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import parsers, scenarios, then, when

from pes.domain.format_config_service import FormatConfigService
from tests.acceptance.proposal_format_selection.steps.format_common_steps import *  # noqa: F403

# Link to feature file
scenarios("../format_change.feature")


# --- Helpers ---


def _make_service(write_state) -> FormatConfigService:
    """Build a FormatConfigService wired to the test's state writer."""

    class _TestStateWriter:
        """Adapter bridging FormatConfigService to conftest write_state fixture."""

        def __init__(self, writer):
            self._writer = writer

        def save(self, state: dict[str, Any]) -> None:
            self._writer(state)

    return FormatConfigService(state_writer=_TestStateWriter(write_state))


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
    """Change the output format via FormatConfigService."""
    state = proposal_context["state"]
    # Persist initial state so read_state() works even for no-op changes
    write_state(state)
    service = _make_service(write_state)
    result = service.change_format(state, fmt)
    format_result.update(result)


@when("Phil Santos submits a blank format value")
def submit_blank_format(
    proposal_context: dict[str, Any],
    format_result: dict[str, Any],
    write_state,
) -> None:
    """Submit an empty/blank format value -- should be rejected."""
    state = proposal_context["state"]
    service = _make_service(write_state)
    result = service.change_format(state, "")
    format_result.update(result)


@when(
    parsers.parse('Phil Santos requests a format change to "{fmt}"'),
)
def request_format_change(
    fmt: str,
    proposal_context: dict[str, Any],
    format_result: dict[str, Any],
    write_state,
) -> None:
    """Request a format change -- evaluates risk and persists if valid."""
    state = proposal_context["state"]
    service = _make_service(write_state)
    result = service.change_format(state, fmt)
    format_result.update(result)


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
