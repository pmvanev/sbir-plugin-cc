"""Port interface for finder results persistence.

Driven port: FinderResultsPort
Defines the business contract for reading and writing scored finder results.
Adapters implement this for specific infrastructure (JSON files, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class FinderResultsPort(ABC):
    """Abstract interface for finder results persistence."""

    @abstractmethod
    def read(self) -> dict[str, Any] | None:
        """Read the finder results.

        Returns the results dict, or None if no results file exists.
        """

    @abstractmethod
    def write(self, results: dict[str, Any]) -> None:
        """Write finder results atomically.

        Writes to .tmp, backs up existing to .bak, renames .tmp to target.
        Creates the directory if absent.
        """

    @abstractmethod
    def exists(self) -> bool:
        """Check whether a finder results file exists."""
