"""File-based audit logger adapter.

Implements AuditLogger port by appending JSON entries to a log file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pes.ports.audit_port import AuditLogger


class FileAuditAdapter(AuditLogger):
    """Append audit entries as JSON lines to a file."""

    def __init__(self, audit_dir: str) -> None:
        self._audit_dir = Path(audit_dir)
        self._log_file = self._audit_dir / "pes-audit.log"

    def log(self, entry: dict[str, Any]) -> None:
        """Append a single audit entry as a JSON line."""
        self._audit_dir.mkdir(parents=True, exist_ok=True)
        with self._log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
