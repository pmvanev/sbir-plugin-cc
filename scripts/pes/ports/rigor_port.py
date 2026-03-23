"""Port interfaces for rigor profile persistence.

Driving ports: RigorProfileReader, RigorProfileWriter,
               RigorDefinitionsReader, ModelTierReader
These define the business contract for rigor profile persistence.
Adapters implement these for specific infrastructure (JSON files, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class RigorProfileReader(ABC):
    """Read a per-proposal rigor profile -- driving port."""

    @abstractmethod
    def read_active_profile(self, proposal_dir: Path) -> dict[str, Any] | None:
        """Read the active rigor profile for a proposal.

        Returns the profile dict, or None if no profile exists.
        """


class RigorProfileWriter(ABC):
    """Write a per-proposal rigor profile -- driving port."""

    @abstractmethod
    def write_profile(self, proposal_dir: Path, data: dict[str, Any]) -> None:
        """Persist a rigor profile atomically.

        Writes to .tmp, backs up existing to .bak, renames .tmp to target.
        Creates the proposal directory if absent.
        """


class RigorDefinitionsReader(ABC):
    """Read rigor profile definitions from plugin config -- driving port."""

    @abstractmethod
    def read_definitions(self, config_dir: Path) -> dict[str, Any]:
        """Load profile definitions (rigor-profiles.json).

        Raises FileNotFoundError if definitions file is missing.
        """


class ModelTierReader(ABC):
    """Read model tier mapping with optional override -- driving port."""

    @abstractmethod
    def read_tier_mapping(
        self, config_dir: Path, override_dir: Path | None = None
    ) -> dict[str, Any]:
        """Load model tier mapping (model-tiers.json).

        If override_dir is provided and contains model-tiers.json,
        use the override instead of the plugin config.

        Raises FileNotFoundError if no tier mapping found.
        """
