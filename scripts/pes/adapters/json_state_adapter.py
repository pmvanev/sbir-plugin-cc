"""JSON file adapter for proposal state persistence.

Implements StateReader and StateWriter ports using JSON files
with atomic write pattern: write .tmp -> backup .bak -> rename .tmp to target.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pes.domain.state import StateCorruptedError, StateNotFoundError
from pes.ports.state_port import StateReader, StateWriter

STATE_FILENAME = "proposal-state.json"


class JsonStateAdapter(StateReader, StateWriter):
    """JSON file-based state persistence with atomic writes and crash recovery."""

    def __init__(self, state_dir: str) -> None:
        self._state_dir = Path(state_dir)
        self._state_file = self._state_dir / STATE_FILENAME
        self._tmp_file = self._state_dir / f"{STATE_FILENAME}.tmp"
        self._bak_file = self._state_dir / f"{STATE_FILENAME}.bak"

    def load(self) -> dict[str, Any]:
        """Load proposal state from JSON file.

        Raises StateNotFoundError if file missing.
        Raises StateCorruptedError if JSON invalid, with recovery from .bak if available.
        """
        if not self._state_file.exists():
            raise StateNotFoundError(
                "No active proposal found. Start with /proposal new"
            )

        try:
            text = self._state_file.read_text(encoding="utf-8")
            result: dict[str, Any] = json.loads(text)
            return result
        except (json.JSONDecodeError, ValueError) as err:
            recovered = self._attempt_recovery()
            raise StateCorruptedError(
                "Proposal state file is corrupted.",
                recovered_state=recovered,
            ) from err

    def exists(self) -> bool:
        """Check whether proposal-state.json exists."""
        return self._state_file.exists()

    def save(self, state: dict[str, Any]) -> None:
        """Persist state atomically: write .tmp, backup existing to .bak, rename .tmp."""
        # Write to temporary file first
        self._tmp_file.write_text(
            json.dumps(state, indent=2), encoding="utf-8"
        )

        # Backup existing state file if present
        if self._state_file.exists():
            self._bak_file.write_bytes(self._state_file.read_bytes())

        # Atomic rename: .tmp -> target
        self._tmp_file.replace(self._state_file)

    def _attempt_recovery(self) -> dict[str, Any] | None:
        """Try to recover state from .bak file."""
        if not self._bak_file.exists():
            return None
        try:
            text = self._bak_file.read_text(encoding="utf-8")
            recovered: dict[str, Any] = json.loads(text)
            return recovered
        except (json.JSONDecodeError, ValueError):
            return None
