"""Unit tests for RigorService -- driving port for rigor profile management.

Tests through the RigorService driving port with in-memory fakes at port boundaries.
Covers: set_profile, get_active_profile, resolve_model_tier, get_suggestion,
compute_diff, resolve_behavioral_params.

Test Budget: 7 behaviors x 2 = 14 max unit tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from pes.domain.rigor_service import (
    NoActiveProposalError,
    RigorService,
    SetProfileResult,
)


# ---------------------------------------------------------------------------
# In-memory fakes at port boundaries
# ---------------------------------------------------------------------------

STANDARD_DEFINITIONS: dict[str, Any] = {
    "schema_version": "1.0",
    "profiles": {
        "lean": {
            "roles": {
                "writer": "basic",
                "reviewer": None,
                "researcher": "basic",
                "strategist": "basic",
                "formatter": "basic",
                "orchestrator": "basic",
                "compliance": "basic",
                "analyst": "basic",
            },
            "review_passes": 0,
            "critique_max_iterations": 0,
            "iteration_cap": 1,
        },
        "standard": {
            "roles": {
                "writer": "standard",
                "reviewer": "basic",
                "researcher": "standard",
                "strategist": "standard",
                "formatter": "standard",
                "orchestrator": "standard",
                "compliance": "standard",
                "analyst": "standard",
            },
            "review_passes": 1,
            "critique_max_iterations": 2,
            "iteration_cap": 2,
        },
        "thorough": {
            "roles": {
                "writer": "strongest",
                "reviewer": "standard",
                "researcher": "strongest",
                "strategist": "strongest",
                "formatter": "standard",
                "orchestrator": "standard",
                "compliance": "standard",
                "analyst": "standard",
            },
            "review_passes": 2,
            "critique_max_iterations": 3,
            "iteration_cap": 2,
        },
        "exhaustive": {
            "roles": {
                "writer": "strongest",
                "reviewer": "strongest",
                "researcher": "strongest",
                "strategist": "strongest",
                "formatter": "strongest",
                "orchestrator": "strongest",
                "compliance": "strongest",
                "analyst": "strongest",
            },
            "review_passes": 2,
            "critique_max_iterations": 3,
            "iteration_cap": 2,
        },
    },
}

STANDARD_TIER_MAPPING: dict[str, Any] = {
    "schema_version": "1.0",
    "tiers": {
        "basic": {"model_id": "claude-haiku-4-5-20251001"},
        "standard": {"model_id": "claude-sonnet-4-6-20250514"},
        "strongest": {"model_id": "claude-opus-4-6-20250514"},
    },
}


class InMemoryRigorAdapter:
    """In-memory fake implementing all rigor port interfaces."""

    def __init__(
        self,
        definitions: dict[str, Any] | None = None,
        tier_mapping: dict[str, Any] | None = None,
    ) -> None:
        self._profiles: dict[str, dict[str, Any]] = {}
        self._definitions = definitions or STANDARD_DEFINITIONS
        self._tier_mapping = tier_mapping or STANDARD_TIER_MAPPING

    def read_active_profile(self, proposal_dir: Path) -> dict[str, Any] | None:
        key = str(proposal_dir)
        return self._profiles.get(key)

    def write_profile(self, proposal_dir: Path, data: dict[str, Any]) -> None:
        self._profiles[str(proposal_dir)] = data

    def read_definitions(self, config_dir: Path) -> dict[str, Any]:
        return self._definitions

    def read_tier_mapping(
        self, config_dir: Path, override_dir: Path | None = None
    ) -> dict[str, Any]:
        return self._tier_mapping

    def seed_profile(self, proposal_dir: Path, data: dict[str, Any]) -> None:
        """Test helper: pre-seed a profile."""
        self._profiles[str(proposal_dir)] = data


def make_service(
    adapter: InMemoryRigorAdapter | None = None,
    config_dir: Path | None = None,
) -> RigorService:
    """Build a RigorService with in-memory adapter."""
    if adapter is None:
        adapter = InMemoryRigorAdapter()
    return RigorService(
        reader=adapter,
        writer=adapter,
        definitions_reader=adapter,
        tier_reader=adapter,
        config_dir=config_dir or Path("/fake/config"),
    )


PROPOSAL_DIR = Path("/fake/proposals/af243-001")


# ---------------------------------------------------------------------------
# 1. set_profile: produces diff and history entry
# ---------------------------------------------------------------------------


class TestSetProfile:
    """Tests for set_profile through RigorService driving port."""

    def test_set_profile_returns_diff_and_appends_history(self) -> None:
        """Profile change produces per-role diff and history entry."""
        adapter = InMemoryRigorAdapter()
        adapter.seed_profile(
            PROPOSAL_DIR,
            {"schema_version": "1.0.0", "profile": "standard", "set_at": "2026-01-01T00:00:00Z", "history": []},
        )
        service = make_service(adapter)

        result = service.set_profile(proposal_dir=PROPOSAL_DIR, new_profile="thorough")

        assert result.changed is True
        assert result.new_profile == "thorough"
        assert result.old_profile == "standard"
        # Diff should show writer changed from standard to strongest
        assert "writer" in result.diff
        assert result.diff["writer"]["from"] == "standard"
        assert result.diff["writer"]["to"] == "strongest"

        # History entry written
        persisted = adapter.read_active_profile(PROPOSAL_DIR)
        assert persisted is not None
        assert persisted["profile"] == "thorough"
        assert len(persisted["history"]) == 1
        entry = persisted["history"][0]
        assert entry["from"] == "standard"
        assert entry["to"] == "thorough"
        assert "at" in entry

    def test_same_profile_returns_noop(self) -> None:
        """Same-profile set returns no-op with no history change."""
        adapter = InMemoryRigorAdapter()
        adapter.seed_profile(
            PROPOSAL_DIR,
            {"schema_version": "1.0.0", "profile": "thorough", "set_at": "2026-01-01T00:00:00Z", "history": []},
        )
        service = make_service(adapter)

        result = service.set_profile(proposal_dir=PROPOSAL_DIR, new_profile="thorough")

        assert result.changed is False
        assert result.no_change is True
        # No history appended
        persisted = adapter.read_active_profile(PROPOSAL_DIR)
        assert len(persisted["history"]) == 0

    def test_no_active_proposal_raises_error(self) -> None:
        """No-active-proposal returns guidance error."""
        service = make_service()

        with pytest.raises(NoActiveProposalError):
            service.set_profile(proposal_dir=None, new_profile="thorough")

    def test_invalid_profile_raises_error(self) -> None:
        """Invalid profile name raises InvalidProfileError."""
        from pes.domain.rigor import InvalidProfileError

        adapter = InMemoryRigorAdapter()
        adapter.seed_profile(
            PROPOSAL_DIR,
            {"schema_version": "1.0.0", "profile": "standard", "set_at": "2026-01-01T00:00:00Z", "history": []},
        )
        service = make_service(adapter)

        with pytest.raises(InvalidProfileError):
            service.set_profile(proposal_dir=PROPOSAL_DIR, new_profile="ultra")

    def test_set_profile_with_wave_records_wave_in_history(self) -> None:
        """History entry includes wave number when provided."""
        adapter = InMemoryRigorAdapter()
        adapter.seed_profile(
            PROPOSAL_DIR,
            {"schema_version": "1.0.0", "profile": "standard", "set_at": "2026-01-01T00:00:00Z", "history": []},
        )
        service = make_service(adapter)

        result = service.set_profile(
            proposal_dir=PROPOSAL_DIR, new_profile="thorough", current_wave=3
        )

        persisted = adapter.read_active_profile(PROPOSAL_DIR)
        entry = persisted["history"][-1]
        assert entry["wave"] == 3


# ---------------------------------------------------------------------------
# 2. get_active_profile: returns profile name or default
# ---------------------------------------------------------------------------


class TestGetActiveProfile:
    """Tests for get_active_profile through RigorService driving port."""

    def test_returns_active_profile_name(self) -> None:
        """Returns the current profile name from persisted state."""
        adapter = InMemoryRigorAdapter()
        adapter.seed_profile(
            PROPOSAL_DIR,
            {"schema_version": "1.0.0", "profile": "thorough", "set_at": "2026-01-01T00:00:00Z", "history": []},
        )
        service = make_service(adapter)

        result = service.get_active_profile(proposal_dir=PROPOSAL_DIR)

        assert result == "thorough"

    def test_returns_standard_when_no_profile_exists(self) -> None:
        """Missing profile defaults to 'standard'."""
        service = make_service()

        result = service.get_active_profile(proposal_dir=PROPOSAL_DIR)

        assert result == "standard"


# ---------------------------------------------------------------------------
# 3. resolve_model_tier: role -> concrete model ID string
# ---------------------------------------------------------------------------


class TestResolveModelTier:
    """Tests for resolve_model_tier through RigorService driving port."""

    def test_resolves_writer_at_thorough_to_strongest(self) -> None:
        """Writer role at thorough rigor resolves to 'strongest' tier."""
        adapter = InMemoryRigorAdapter()
        adapter.seed_profile(
            PROPOSAL_DIR,
            {"schema_version": "1.0.0", "profile": "thorough", "set_at": "2026-01-01T00:00:00Z", "history": []},
        )
        service = make_service(adapter)

        result = service.resolve_model_tier(
            proposal_dir=PROPOSAL_DIR, agent_role="writer"
        )

        assert result == "strongest"

    def test_defaults_to_standard_tier_when_no_profile(self) -> None:
        """Missing profile defaults to standard, resolving writer to 'standard' tier."""
        service = make_service()

        result = service.resolve_model_tier(
            proposal_dir=PROPOSAL_DIR, agent_role="writer"
        )

        assert result == "standard"


# ---------------------------------------------------------------------------
# 4. get_suggestion: fit score + phase -> profile suggestion
# ---------------------------------------------------------------------------


class TestGetSuggestion:
    """Tests for get_suggestion through RigorService driving port."""

    @pytest.mark.parametrize(
        "fit_score,phase,expected",
        [
            (85, "II", "thorough"),
            (80, "II", "thorough"),
            (64, "I", "lean"),
            (69, "I", "lean"),
            (75, "I", None),
            (70, "I", None),
            (90, "I", None),
            (60, "II", None),
        ],
    )
    def test_suggestion_rules(
        self, fit_score: int, phase: str, expected: str | None
    ) -> None:
        """Suggestion is thorough for high-fit Phase II, lean for low-fit Phase I, else None."""
        from pes.domain.rigor import compute_rigor_suggestion

        result = compute_rigor_suggestion(fit_score=fit_score, phase=phase)
        assert result == expected
