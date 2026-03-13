"""JSON file adapter for finder results persistence.

Implements FinderResultsPort using JSON files with atomic write pattern:
write .tmp -> backup .bak -> rename .tmp to target.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pes.ports.finder_results_port import FinderResultsPort

RESULTS_FILENAME = "finder-results.json"


class JsonFinderResultsAdapter(FinderResultsPort):
    """JSON file-based finder results persistence with atomic writes."""

    def __init__(self, results_dir: str) -> None:
        self._results_dir = Path(results_dir)
        self._results_file = self._results_dir / RESULTS_FILENAME
        self._tmp_file = self._results_dir / f"{RESULTS_FILENAME}.tmp"
        self._bak_file = self._results_dir / f"{RESULTS_FILENAME}.bak"

    def read(self) -> dict[str, Any] | None:
        """Read finder results from JSON file.

        Returns None if no results file exists.
        """
        if not self._results_file.exists():
            return None

        text = self._results_file.read_text(encoding="utf-8")
        result: dict[str, Any] = json.loads(text)
        return result

    def write(self, results: dict[str, Any]) -> None:
        """Write results atomically: .tmp -> backup .bak -> rename .tmp to target."""
        # Create directory if absent
        self._results_dir.mkdir(parents=True, exist_ok=True)

        # Write to temporary file first
        self._tmp_file.write_text(
            json.dumps(results, indent=2), encoding="utf-8"
        )

        # Backup existing results if present
        if self._results_file.exists():
            self._bak_file.write_bytes(self._results_file.read_bytes())

        # Atomic rename: .tmp -> target
        self._tmp_file.replace(self._results_file)

    def exists(self) -> bool:
        """Check whether finder-results.json exists."""
        return self._results_file.exists()
