"""Rigor service -- driving port for profile selection, diff, and resolution.

Application service orchestrating rigor profile management:
- Profile validation, selection, and persistence
- Diff computation between old and new profiles
- Model tier resolution for agent roles
- Behavioral parameter resolution (review passes, critique iterations)

Pure application logic. Infrastructure accessed through port interfaces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pes.domain.rigor import (
    DEFAULT_PROFILE_NAME,
    DiffComputer,
    ProfileValidator,
    RigorProfile,
)
from pes.ports.rigor_port import (
    ModelTierReader,
    RigorDefinitionsReader,
    RigorProfileReader,
    RigorProfileWriter,
)


class NoActiveProposalError(Exception):
    """Raised when an operation requires an active proposal but none exists."""


@dataclass
class SetProfileResult:
    """Result of a set_profile operation."""

    changed: bool
    new_profile: str
    old_profile: str
    no_change: bool = False
    diff: dict[str, Any] = field(default_factory=dict)
    message: str = ""

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like access for acceptance test compatibility."""
        return getattr(self, key, default)


class RigorService:
    """Driving port: manages rigor profile lifecycle for proposals.

    Delegates persistence to port interfaces (reader, writer, definitions, tiers).
    Domain logic (validation, diff) uses pure domain objects.

    Supports two construction styles:
    1. Explicit ports: RigorService(reader=..., writer=..., definitions_reader=..., tier_reader=..., config_dir=...)
    2. Single adapter: RigorService(adapter) where adapter implements all port interfaces
       and has a plugin_config_dir attribute.
    """

    def __init__(
        self,
        reader: RigorProfileReader | None = None,
        writer: RigorProfileWriter | None = None,
        definitions_reader: RigorDefinitionsReader | None = None,
        tier_reader: ModelTierReader | None = None,
        config_dir: Path | None = None,
    ) -> None:
        # If reader is the only arg and it's a combined adapter, use it for all ports
        if (
            reader is not None
            and writer is None
            and definitions_reader is None
            and isinstance(reader, RigorProfileWriter)
        ):
            adapter = reader
            self._reader = adapter
            self._writer = adapter
            self._definitions_reader = adapter  # type: ignore[assignment]
            self._tier_reader = adapter  # type: ignore[assignment]
            self._config_dir = getattr(adapter, "plugin_config_dir", config_dir or Path("."))
        else:
            assert reader is not None
            assert writer is not None
            assert definitions_reader is not None
            assert tier_reader is not None
            self._reader = reader
            self._writer = writer
            self._definitions_reader = definitions_reader
            self._tier_reader = tier_reader
            self._config_dir = config_dir or Path(".")
        self._validator = ProfileValidator()

    def set_profile(
        self,
        proposal_dir: Path | None,
        new_profile: str,
        current_wave: int | None = None,
    ) -> SetProfileResult:
        """Set a rigor profile for the active proposal.

        Validates profile name, computes diff, writes state with history.
        Returns SetProfileResult with diff and confirmation.

        Raises NoActiveProposalError if proposal_dir is None.
        Raises InvalidProfileError if new_profile is not valid.
        """
        if proposal_dir is None:
            raise NoActiveProposalError(
                "No active proposal. Use /proposal switch to select one."
            )

        self._validator.validate(new_profile)

        # Read current state
        current_data = self._reader.read_active_profile(proposal_dir)
        old_profile = (
            current_data.get("profile", DEFAULT_PROFILE_NAME)
            if current_data
            else DEFAULT_PROFILE_NAME
        )

        # Same-profile no-op
        if old_profile == new_profile:
            return SetProfileResult(
                changed=False,
                new_profile=new_profile,
                old_profile=old_profile,
                no_change=True,
                message=f"Rigor is already '{new_profile}'.",
            )

        # Compute diff
        definitions = self._definitions_reader.read_definitions(self._config_dir)
        diff = self._compute_role_diff(old_profile, new_profile, definitions)

        # Build history entry
        history = (
            list(current_data.get("history", [])) if current_data else []
        )
        entry: dict[str, Any] = {
            "from": old_profile,
            "to": new_profile,
            "at": datetime.now(timezone.utc).isoformat(),
        }
        if current_wave is not None:
            entry["wave"] = current_wave
        history.append(entry)

        # Write new state
        new_data: dict[str, Any] = {
            "schema_version": "1.0.0",
            "profile": new_profile,
            "set_at": datetime.now(timezone.utc).isoformat(),
            "history": history,
        }
        self._writer.write_profile(proposal_dir, new_data)

        return SetProfileResult(
            changed=True,
            new_profile=new_profile,
            old_profile=old_profile,
            diff=diff,
            message=f"Rigor changed from '{old_profile}' to '{new_profile}'.",
        )

    def get_active_profile(self, proposal_dir: Path) -> str:
        """Read the active rigor profile name for a proposal.

        Returns the profile name string. Defaults to 'standard' if missing.
        """
        data = self._reader.read_active_profile(proposal_dir)
        if data is None:
            return DEFAULT_PROFILE_NAME
        return data.get("profile", DEFAULT_PROFILE_NAME)

    def resolve_model_tier(
        self, proposal_dir: Path, agent_role: str
    ) -> str:
        """Resolve the model tier for an agent role from the active profile.

        Returns the tier name string (e.g., 'basic', 'standard', 'strongest').
        """
        profile_name = self.get_active_profile(proposal_dir)
        definitions = self._definitions_reader.read_definitions(self._config_dir)
        profiles = definitions.get("profiles", {})
        profile_def = profiles.get(profile_name, {})
        roles = profile_def.get("roles", {})
        tier = roles.get(agent_role)
        if tier is None:
            return "standard"  # fallback for unknown roles or null tiers
        return tier

    def resolve_behavioral_params(
        self, proposal_dir: Path
    ) -> dict[str, Any]:
        """Resolve behavioral parameters from the active rigor profile.

        Returns dict with review_passes, critique_max_iterations, iteration_cap.
        """
        profile_name = self.get_active_profile(proposal_dir)
        definitions = self._definitions_reader.read_definitions(self._config_dir)
        profiles = definitions.get("profiles", {})
        profile_def = profiles.get(profile_name, {})
        return {
            "review_passes": profile_def.get("review_passes", 1),
            "critique_max_iterations": profile_def.get("critique_max_iterations", 2),
            "iteration_cap": profile_def.get("iteration_cap", 2),
        }

    def compute_diff(
        self, from_profile: str, to_profile: str
    ) -> dict[str, Any]:
        """Compute a structured diff between two profile names.

        Returns dict with agent_roles, review_passes, critique_max_iterations changes.
        Raises InvalidProfileError for invalid profile names.
        """
        self._validator.validate(from_profile)
        self._validator.validate(to_profile)

        definitions = self._definitions_reader.read_definitions(self._config_dir)
        return self._compute_structured_diff(from_profile, to_profile, definitions)

    def get_profile_definition(self, profile_name: str) -> dict[str, Any]:
        """Get the full profile definition for a profile name."""
        definitions = self._definitions_reader.read_definitions(self._config_dir)
        profiles = definitions.get("profiles", {})
        return profiles.get(profile_name, {})

    def get_all_definitions(self) -> dict[str, Any]:
        """Get all profile definitions."""
        definitions = self._definitions_reader.read_definitions(self._config_dir)
        return definitions.get("profiles", {})

    # --- Private helpers ---

    def _compute_role_diff(
        self,
        old_profile: str,
        new_profile: str,
        definitions: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute per-role diff dict for set_profile result.

        Returns dict like: {"writer": {"from": "standard", "to": "strongest"}, ...}
        Also includes param changes like critique_max_iterations.
        """
        profiles = definitions.get("profiles", {})
        old_roles = profiles.get(old_profile, {}).get("roles", {})
        new_roles = profiles.get(new_profile, {}).get("roles", {})

        diff: dict[str, Any] = {}
        all_roles = set(old_roles) | set(new_roles)
        for role in sorted(all_roles):
            old_tier = old_roles.get(role)
            new_tier = new_roles.get(role)
            if old_tier != new_tier:
                diff[role] = {"from": old_tier, "to": new_tier}

        # Include param changes
        old_def = profiles.get(old_profile, {})
        new_def = profiles.get(new_profile, {})
        for param in ("review_passes", "critique_max_iterations", "iteration_cap"):
            old_val = old_def.get(param)
            new_val = new_def.get(param)
            if old_val != new_val:
                diff[param] = {"from": old_val, "to": new_val}

        return diff

    def _compute_structured_diff(
        self,
        from_profile: str,
        to_profile: str,
        definitions: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute structured diff for compute_diff API.

        Returns dict with separate agent_roles, review_passes, etc. keys.
        """
        profiles = definitions.get("profiles", {})
        old_roles = profiles.get(from_profile, {}).get("roles", {})
        new_roles = profiles.get(to_profile, {}).get("roles", {})

        role_changes: dict[str, Any] = {}
        all_roles = set(old_roles) | set(new_roles)
        for role in sorted(all_roles):
            old_tier = old_roles.get(role)
            new_tier = new_roles.get(role)
            if old_tier != new_tier:
                role_changes[role] = {"from": old_tier, "to": new_tier}

        result: dict[str, Any] = {"agent_roles": role_changes}

        old_def = profiles.get(from_profile, {})
        new_def = profiles.get(to_profile, {})
        for param in ("review_passes", "critique_max_iterations", "iteration_cap"):
            old_val = old_def.get(param)
            new_val = new_def.get(param)
            if old_val != new_val:
                result[param] = {"from": old_val, "to": new_val}

        return result
