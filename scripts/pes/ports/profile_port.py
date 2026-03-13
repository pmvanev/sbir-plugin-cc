"""Port interface for company profile persistence.

Driving port: ProfilePort
Defines the business contract for profile read/write/exists/metadata.
Adapters implement this for specific infrastructure (JSON files, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ProfileMetadata:
    """Metadata about an existing company profile."""

    exists: bool
    company_name: str | None = None
    last_modified: str | None = None


class ProfilePort(ABC):
    """Abstract interface for company profile persistence."""

    @abstractmethod
    def read(self) -> dict[str, Any] | None:
        """Read the company profile.

        Returns the profile dict, or None if no profile exists.
        """

    @abstractmethod
    def write(self, profile: dict[str, Any]) -> None:
        """Write the company profile atomically.

        Writes to .tmp, backs up existing to .bak, renames .tmp to target.
        Creates the profile directory if absent.
        """

    @abstractmethod
    def exists(self) -> bool:
        """Check whether a company profile file exists."""

    @abstractmethod
    def metadata(self) -> ProfileMetadata:
        """Return metadata about the existing profile.

        Returns ProfileMetadata with exists=False if no profile found.
        """
