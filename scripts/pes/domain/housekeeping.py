"""Crash signal housekeeping -- domain service.

Detects and removes stale crash signal files from .sbir/ on session start.
Reports each removal for auditing. Warns on locked/unremovable files without
blocking the session.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CRASH_SIGNAL_PATTERN = "*.signal"


class CrashSignalCleaner:
    """Clean up stale crash signal files from a proposal's .sbir directory."""

    def clean(self, proposal_dir: str) -> list[dict[str, Any]]:
        """Scan .sbir/ for crash signal files, remove them, return results.

        Returns a list of dicts, each describing a cleanup action:
          - {"file": str, "status": "removed"}
          - {"file": str, "status": "failed", "reason": str}
        """
        sbir_dir = Path(proposal_dir) / ".sbir"
        if not sbir_dir.exists():
            return []

        results: list[dict[str, Any]] = []
        for signal_file in sorted(sbir_dir.glob(CRASH_SIGNAL_PATTERN)):
            try:
                signal_file.unlink()
                results.append({
                    "file": signal_file.name,
                    "status": "removed",
                })
            except OSError as exc:
                logger.warning(
                    "Could not remove crash signal %s: %s",
                    signal_file.name,
                    exc,
                )
                results.append({
                    "file": signal_file.name,
                    "status": "failed",
                    "reason": str(exc),
                })

        return results
