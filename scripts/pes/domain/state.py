"""Proposal state domain model and schema."""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "2.0.0"


class StateNotFoundError(Exception):
    """Raised when no proposal state file exists."""


class StateCorruptedError(Exception):
    """Raised when proposal state file contains invalid JSON."""

    def __init__(self, message: str, recovered_state: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.recovered_state = recovered_state
