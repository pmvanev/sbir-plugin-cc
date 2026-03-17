"""Step definitions for format selection during proposal setup (US-PFS-001).

Invokes through: FormatConfigService (driving port -- domain service).
Does NOT import internal validators or state internals directly.

The FormatConfigService is the entry point for all format-related domain logic.
Tests exercise it with state dicts and assert on FormatConfigResult.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.format_config_service import FormatConfigService
from tests.acceptance.proposal_format_selection.steps.format_common_steps import *  # noqa: F403

# Link to feature file
scenarios("../format_setup.feature")


# --- Helpers ---


def _make_service(write_state) -> FormatConfigService:
    """Build a FormatConfigService wired to the test's state writer."""

    class _TestStateWriter:
        def __init__(self, writer):
            self._writer = writer

        def save(self, state: dict[str, Any]) -> None:
            self._writer(state)

    return FormatConfigService(state_writer=_TestStateWriter(write_state))


# --- Given steps ---


@given("an existing proposal state without an output format field")
def state_without_format(
    base_proposal_state: dict[str, Any],
    proposal_context: dict[str, Any],
) -> None:
    """Create a legacy state that lacks the output_format field."""
    state = dict(base_proposal_state)
    state.pop("output_format", None)
    proposal_context["state"] = state


@given(
    parsers.parse('a proposal state with output format set to "{fmt}"'),
)
def state_with_invalid_format(
    fmt: str,
    base_proposal_state: dict[str, Any],
    proposal_context: dict[str, Any],
) -> None:
    """Create a state with an arbitrary format value for validation testing."""
    state = dict(base_proposal_state)
    state["output_format"] = fmt
    proposal_context["state"] = state


# --- When steps ---


@when("the proposal state is saved")
def save_state_with_format(
    proposal_context: dict[str, Any],
    write_state,
) -> None:
    """Save the proposal state (with selected format applied) to disk.

    Uses FormatConfigService.apply_selected_format() to set the format,
    then persists via StateWriter port.
    """
    state = proposal_context["state"]
    service = _make_service(write_state)
    if "selected_format" in proposal_context:
        service.apply_selected_format(state, proposal_context["selected_format"])
    else:
        write_state(state)


@when("the proposal state is saved with no explicit format selection")
def save_state_default_format(
    proposal_context: dict[str, Any],
    write_state,
) -> None:
    """Save state without setting a format -- default should apply.

    Invokes FormatConfigService.apply_default_format() to ensure
    the default is set, then persists via StateWriter.
    """
    state = proposal_context["state"]
    service = _make_service(write_state)
    service.apply_default_format(state)


@when("the format configuration service reads the current format")
def read_format_from_service(
    proposal_context: dict[str, Any],
    format_result: dict[str, Any],
) -> None:
    """Read the effective format from a state dict via FormatConfigService.

    The service handles missing fields by returning the default.
    """
    state = proposal_context["state"]
    effective = FormatConfigService.get_effective_format(state)
    format_result["effective_format"] = effective


@when("the state is validated against the schema")
def validate_state_schema(
    proposal_context: dict[str, Any],
    format_result: dict[str, Any],
) -> None:
    """Validate the proposal state format field via FormatConfigService.

    Uses the same validation logic as the production state persistence flow.
    """
    state = proposal_context["state"]
    result = FormatConfigService.validate_format(state)
    format_result["schema_valid"] = result["valid"]
    if not result["valid"]:
        format_result["schema_error"] = result["error"]


# --- Then steps ---


@then("the proposal state is valid against the schema")
def state_is_schema_valid(read_state) -> None:
    """Assert the persisted state passes schema validation."""
    state = read_state()
    result = FormatConfigService.validate_format(state)
    assert result["valid"], f"Schema validation failed: {result.get('error')}"


@then(
    parsers.parse('the effective output format is "{fmt}"'),
)
def effective_format_is(fmt: str, format_result: dict[str, Any]) -> None:
    """Assert the effective format returned by the service."""
    assert format_result["effective_format"] == fmt


@then("validation rejects the state with a format error")
def schema_rejects_format(format_result: dict[str, Any]) -> None:
    """Assert schema validation failed due to invalid format."""
    assert format_result["schema_valid"] is False
    assert "output_format" in format_result.get("schema_error", "")
