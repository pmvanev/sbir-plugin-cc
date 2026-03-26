"""Port interface for API key persistence and validation.

Driven port: ApiKeyPort
Defines the business contract for API key read/write/validate.
Adapters implement this for specific infrastructure (JSON files, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ApiKeyPort(ABC):
    """Abstract interface for API key management."""

    @abstractmethod
    def read_key(self, service_name: str) -> str | None:
        """Read a stored API key for the given service.

        Returns the key string, or None if no key is stored.
        Raises ApiKeyError on malformed storage (e.g., invalid JSON).
        """

    @abstractmethod
    def write_key(self, service_name: str, key: str) -> None:
        """Save an API key with restricted file permissions.

        Creates the storage directory if absent.
        Sets owner-only read/write permissions on the key file.
        """


class ApiKeyError(Exception):
    """Raised when the API key storage is malformed or unreadable."""
