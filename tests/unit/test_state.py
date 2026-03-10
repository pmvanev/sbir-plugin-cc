"""Tests for proposal state domain model.

Domain model tested indirectly through adapter tests (Mandate 2).
This file validates only the schema version constant and error contracts
that are part of the port boundary API.
"""

from __future__ import annotations

from pes.domain.state import SCHEMA_VERSION, StateCorruptedError, StateNotFoundError


class TestStateErrors:
    """State error types carry the right information for callers."""

    def test_state_not_found_error_is_an_exception(self) -> None:
        error = StateNotFoundError("No active proposal found. Start with /proposal new")
        assert "No active proposal found" in str(error)

    def test_state_corrupted_error_carries_recovered_state(self) -> None:
        recovered = {"proposal_id": "recovered-uuid"}
        error = StateCorruptedError("Corrupted", recovered_state=recovered)
        assert error.recovered_state == recovered
        assert error.recovered_state["proposal_id"] == "recovered-uuid"

    def test_schema_version_is_2_0_0(self) -> None:
        assert SCHEMA_VERSION == "2.0.0"
