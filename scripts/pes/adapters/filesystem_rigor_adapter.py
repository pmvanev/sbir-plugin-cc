"""Filesystem adapter for rigor profile persistence.

Implements RigorProfileReader, RigorProfileWriter,
RigorDefinitionsReader, and ModelTierReader ports using JSON files
with atomic write pattern: write .tmp -> backup .bak -> rename .tmp to target.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pes.ports.rigor_port import (
    ModelTierReader,
    RigorDefinitionsReader,
    RigorProfileReader,
    RigorProfileWriter,
)

RIGOR_PROFILE_FILENAME = "rigor-profile.json"
RIGOR_DEFINITIONS_FILENAME = "rigor-profiles.json"
MODEL_TIERS_FILENAME = "model-tiers.json"


class FilesystemRigorAdapter(
    RigorProfileReader, RigorProfileWriter, RigorDefinitionsReader, ModelTierReader
):
    """JSON file-based rigor profile persistence with atomic writes."""

    def read_active_profile(self, proposal_dir: Path) -> dict[str, Any] | None:
        """Read the active rigor profile for a proposal.

        Returns the profile dict, or None if no profile exists.
        """
        profile_file = proposal_dir / RIGOR_PROFILE_FILENAME
        if not profile_file.exists():
            return None

        text = profile_file.read_text(encoding="utf-8")
        result: dict[str, Any] = json.loads(text)
        return result

    def write_profile(self, proposal_dir: Path, data: dict[str, Any]) -> None:
        """Persist a rigor profile atomically.

        Writes to .tmp, backs up existing to .bak, renames .tmp to target.
        Creates the proposal directory if absent.
        """
        proposal_dir.mkdir(parents=True, exist_ok=True)

        profile_file = proposal_dir / RIGOR_PROFILE_FILENAME
        tmp_file = proposal_dir / f"{RIGOR_PROFILE_FILENAME}.tmp"
        bak_file = proposal_dir / f"{RIGOR_PROFILE_FILENAME}.bak"

        # Write to temporary file first
        tmp_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

        # Backup existing profile if present
        if profile_file.exists():
            bak_file.write_bytes(profile_file.read_bytes())

        # Atomic rename: .tmp -> target
        tmp_file.replace(profile_file)

    def read_definitions(self, config_dir: Path) -> dict[str, Any]:
        """Load profile definitions (rigor-profiles.json).

        Raises FileNotFoundError if definitions file is missing.
        """
        definitions_file = config_dir / RIGOR_DEFINITIONS_FILENAME
        if not definitions_file.exists():
            raise FileNotFoundError(
                f"Rigor profile definitions not found: {definitions_file}"
            )

        text = definitions_file.read_text(encoding="utf-8")
        result: dict[str, Any] = json.loads(text)
        return result

    def read_tier_mapping(
        self, config_dir: Path, override_dir: Path | None = None
    ) -> dict[str, Any]:
        """Load model tier mapping with optional .sbir/ override.

        If override_dir contains model-tiers.json, use that instead.
        Raises FileNotFoundError if no tier mapping found.
        """
        # Check override first
        if override_dir is not None:
            override_file = override_dir / MODEL_TIERS_FILENAME
            if override_file.exists():
                text = override_file.read_text(encoding="utf-8")
                result: dict[str, Any] = json.loads(text)
                return result

        # Fall back to plugin config
        config_file = config_dir / MODEL_TIERS_FILENAME
        if not config_file.exists():
            raise FileNotFoundError(
                f"Model tier mapping not found: {config_file}"
            )

        text = config_file.read_text(encoding="utf-8")
        result_config: dict[str, Any] = json.loads(text)
        return result_config
