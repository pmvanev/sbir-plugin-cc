"""Port interfaces for proposal state persistence.

Driving ports: StateReader, StateWriter
These define the business contract for state persistence.
Adapters implement these for specific infrastructure (JSON files, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class StateReader(ABC):
    """Read proposal state -- driving port."""

    @abstractmethod
    def load(self) -> dict[str, Any]:
        """Load proposal state.

        Returns the state dictionary.

        Raises:
            StateNotFoundError: if no state file exists.
            StateCorruptedError: if state file is invalid (may include recovered state).
        """

    @abstractmethod
    def exists(self) -> bool:
        """Check whether a proposal state file exists."""


class StateWriter(ABC):
    """Write proposal state -- driving port."""

    @abstractmethod
    def save(self, state: dict[str, Any]) -> None:
        """Persist proposal state atomically.

        Writes to .tmp, backs up existing to .bak, renames .tmp to target.
        """
