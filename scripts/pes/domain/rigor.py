"""Rigor profile domain objects -- value objects, validation, diff computation.

Pure domain module. No infrastructure imports.
"""

from __future__ import annotations

from dataclasses import dataclass


VALID_PROFILE_NAMES: frozenset[str] = frozenset({
    "lean", "standard", "thorough", "exhaustive",
})

DEFAULT_PROFILE_NAME: str = "standard"


class InvalidProfileError(Exception):
    """Raised when a profile name is not in the valid set."""


@dataclass(frozen=True)
class RigorProfile:
    """Immutable value object representing a rigor profile configuration."""

    profile_name: str
    agent_roles: dict[str, str | None]
    review_passes: int
    critique_max_iterations: int
    iteration_cap: int


@dataclass
class ProfileDiff:
    """Result of comparing two RigorProfile instances."""

    role_changes: list[tuple[str, str | None, str | None]]
    param_changes: list[tuple[str, int, int]]


class ProfileValidator:
    """Validates profile names against the known set."""

    def validate(self, profile_name: str) -> None:
        """Raise InvalidProfileError if profile_name is not valid."""
        if profile_name not in VALID_PROFILE_NAMES:
            valid_list = ", ".join(sorted(VALID_PROFILE_NAMES))
            raise InvalidProfileError(
                f"Invalid profile '{profile_name}'. "
                f"Valid profiles: {valid_list}"
            )


class DiffComputer:
    """Computes differences between two RigorProfile instances."""

    @staticmethod
    def compute(old: RigorProfile, new: RigorProfile) -> ProfileDiff:
        """Return a ProfileDiff describing changes from old to new."""
        role_changes: list[tuple[str, str | None, str | None]] = []
        all_roles = set(old.agent_roles) | set(new.agent_roles)
        for role in sorted(all_roles):
            old_tier = old.agent_roles.get(role)
            new_tier = new.agent_roles.get(role)
            if old_tier != new_tier:
                role_changes.append((role, old_tier, new_tier))

        param_changes: list[tuple[str, int, int]] = []
        for param in ("review_passes", "critique_max_iterations", "iteration_cap"):
            old_val = getattr(old, param)
            new_val = getattr(new, param)
            if old_val != new_val:
                param_changes.append((param, old_val, new_val))

        return ProfileDiff(
            role_changes=role_changes,
            param_changes=param_changes,
        )


def compute_rigor_suggestion(
    fit_score: int,
    phase: str,
    contract_value: float | None = None,
) -> str | None:
    """Compute a contextual rigor profile suggestion.

    Rules:
    - fit >= 80 AND Phase II -> suggest "thorough"
    - fit < 70 AND Phase I -> suggest "lean"
    - otherwise -> None (no suggestion)
    """
    if fit_score >= 80 and phase == "II":
        return "thorough"
    if fit_score < 70 and phase == "I":
        return "lean"
    return None
