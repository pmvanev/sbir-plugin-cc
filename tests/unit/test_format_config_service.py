"""Unit tests for FormatConfigService (driving port for mid-proposal format changes).

Test Budget: 6 behaviors x 2 = 12 unit tests max.

Behaviors:
1. Valid format change before Wave 3 -> persists, no warning
2. Format change at Wave 3+ -> rework warning with wave context
3. Invalid format rejected with valid options listed
4. Empty/blank format rejected
5. Same-format change is no-op without warning
6. Case-insensitive format acceptance

Tests enter through driving port (FormatConfigService.change_format).
StateWriter driven port replaced with in-memory fake.
"""

from __future__ import annotations

from typing import Any

import pytest

from pes.domain.format_config_service import FormatConfigService
from pes.ports.state_port import StateWriter


# ---------------------------------------------------------------------------
# Fake driven port
# ---------------------------------------------------------------------------


class InMemoryStateWriter(StateWriter):
    """Captures saved state for assertions."""

    def __init__(self) -> None:
        self.saved_states: list[dict[str, Any]] = []

    def save(self, state: dict[str, Any]) -> None:
        self.saved_states.append(state)

    def load(self) -> dict[str, Any]:
        if not self.saved_states:
            raise FileNotFoundError
        return self.saved_states[-1]

    def exists(self) -> bool:
        return len(self.saved_states) > 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_state(
    current_wave: int = 1,
    output_format: str = "docx",
) -> dict[str, Any]:
    """Build minimal proposal state for format change testing."""
    return {
        "current_wave": current_wave,
        "output_format": output_format,
    }


def _make_service() -> tuple[FormatConfigService, InMemoryStateWriter]:
    """Wire FormatConfigService with fake StateWriter."""
    writer = InMemoryStateWriter()
    service = FormatConfigService(state_writer=writer)
    return service, writer


# ---------------------------------------------------------------------------
# Behavior 1: Valid format change before Wave 3
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "wave,current_fmt,new_fmt",
    [
        (1, "docx", "latex"),
        (2, "latex", "docx"),
        (1, "latex", "docx"),
    ],
)
def test_valid_format_change_before_wave3_persists_without_warning(
    wave: int, current_fmt: str, new_fmt: str
) -> None:
    """Format changes before Wave 3 succeed, persist new format, no warning."""
    service, writer = _make_service()
    state = _make_state(current_wave=wave, output_format=current_fmt)

    result = service.change_format(state, new_fmt)

    assert result["success"] is True
    assert result["rework_warning"] is False
    assert len(writer.saved_states) == 1
    assert writer.saved_states[0]["output_format"] == new_fmt


# ---------------------------------------------------------------------------
# Behavior 2: Format change at Wave 3+ triggers rework warning
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("wave", [3, 4, 5, 6])
def test_format_change_at_wave3_or_later_returns_rework_warning(
    wave: int,
) -> None:
    """Format changes at Wave 3+ return rework warning with wave context."""
    service, writer = _make_service()
    state = _make_state(current_wave=wave, output_format="docx")

    result = service.change_format(state, "latex")

    assert result["success"] is True
    assert result["rework_warning"] is True
    assert result["warning_wave"] == wave
    assert str(wave) in result["warning_message"]
    assert "adjustment" in result["warning_message"].lower()
    # Still persists the change
    assert len(writer.saved_states) == 1
    assert writer.saved_states[0]["output_format"] == "latex"


# ---------------------------------------------------------------------------
# Behavior 3: Invalid format rejected with valid options
# ---------------------------------------------------------------------------


def test_invalid_format_rejected_with_valid_options() -> None:
    """Invalid format values are rejected with error listing valid options."""
    service, writer = _make_service()
    state = _make_state()

    result = service.change_format(state, "pdf")

    assert result["success"] is False
    assert "latex" in result["error"]
    assert "docx" in result["error"]
    assert result["rework_warning"] is False
    assert len(writer.saved_states) == 0


# ---------------------------------------------------------------------------
# Behavior 4: Empty/blank format rejected
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("blank_value", ["", "   "])
def test_empty_or_blank_format_rejected(blank_value: str) -> None:
    """Empty or whitespace-only format values are rejected."""
    service, writer = _make_service()
    state = _make_state()

    result = service.change_format(state, blank_value)

    assert result["success"] is False
    assert result["rework_warning"] is False
    assert len(writer.saved_states) == 0


# ---------------------------------------------------------------------------
# Behavior 5: Same-format change is no-op
# ---------------------------------------------------------------------------


def test_same_format_change_is_noop_without_warning() -> None:
    """Changing to the same format succeeds without warning or state write."""
    service, writer = _make_service()
    state = _make_state(current_wave=4, output_format="latex")

    result = service.change_format(state, "latex")

    assert result["success"] is True
    assert result["rework_warning"] is False
    # No-op: should not write state
    assert len(writer.saved_states) == 0


# ---------------------------------------------------------------------------
# Behavior 6: Case-insensitive format acceptance
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fmt_input", ["LATEX", "Latex", "LaTeX", "DOCX", "Docx"])
def test_format_accepted_case_insensitively(fmt_input: str) -> None:
    """Format values are normalized to lowercase before validation."""
    service, writer = _make_service()
    state = _make_state(current_wave=1, output_format="docx" if "latex" in fmt_input.lower() else "latex")

    result = service.change_format(state, fmt_input)

    assert result["success"] is True
    assert len(writer.saved_states) == 1
    assert writer.saved_states[0]["output_format"] == fmt_input.strip().lower()
