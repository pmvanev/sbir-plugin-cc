"""Session housekeeping -- domain services.

Crash signal cleanup: detects and removes stale crash signal files from .sbir/
on session start. Reports each removal for auditing. Warns on locked/unremovable
files without blocking the session.

Audit log rotation: rotates audit log entries exceeding 365-day retention window
and rotates oversized log files with timestamped archive.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timedelta
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


class AuditLogRotator:
    """Rotate audit log files by retention window and file size."""

    DEFAULT_RETENTION_DAYS = 365
    DEFAULT_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

    def __init__(
        self,
        retention_days: int = DEFAULT_RETENTION_DAYS,
        max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
    ) -> None:
        self._retention_days = retention_days
        self._max_file_size_bytes = max_file_size_bytes

    def rotate(self, audit_dir: str) -> list[dict[str, Any]]:
        """Perform retention and size rotation on the audit log.

        Returns a list of rotation action dicts for auditing:
          - {"action": "retention_rotation", "archived_count": int, "archive_file": str}
          - {"action": "size_rotation", "archive_file": str, "original_size": int}
        """
        results: list[dict[str, Any]] = []
        audit_path = Path(audit_dir)
        log_file = audit_path / "pes-audit.log"

        if not log_file.exists():
            return results

        # Size rotation first -- if file is oversized, archive entire file
        if log_file.stat().st_size > self._max_file_size_bytes:
            size_result = self._rotate_by_size(log_file)
            if size_result:
                results.append(size_result)
            return results  # Size rotation replaces file, skip retention

        # Retention rotation -- archive entries older than retention window
        retention_result = self._rotate_by_retention(log_file)
        if retention_result:
            results.append(retention_result)

        return results

    def _rotate_by_size(self, log_file: Path) -> dict[str, Any] | None:
        """Rename oversized log file to timestamped archive, start fresh."""
        original_size = log_file.stat().st_size
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        archive_name = f"{log_file.name}.archive.{timestamp}"
        archive_path = log_file.parent / archive_name

        try:
            log_file.rename(archive_path)
            # Create fresh empty log file
            log_file.write_text("")
            return {
                "action": "size_rotation",
                "archive_file": archive_name,
                "original_size": original_size,
            }
        except OSError as exc:
            logger.warning(
                "Could not rotate oversized audit log: %s", exc
            )
            return None

    def _rotate_by_retention(self, log_file: Path) -> dict[str, Any] | None:
        """Archive entries older than the retention window."""
        # Use date comparison (day granularity) so entries from exactly
        # N days ago are preserved (not archived). Only entries from
        # strictly more than N calendar days ago are archived.
        cutoff_date = (datetime.now(UTC) - timedelta(days=self._retention_days)).date()

        try:
            raw_lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        except OSError as exc:
            logger.warning("Could not read audit log for rotation: %s", exc)
            return None

        current_entries: list[str] = []
        archived_entries: list[str] = []

        for line in raw_lines:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                ts_str = entry.get("timestamp", "")
                if ts_str:
                    entry_time = datetime.fromisoformat(ts_str)
                    if entry_time.tzinfo is None:
                        entry_time = entry_time.replace(tzinfo=UTC)
                    if entry_time.date() < cutoff_date:
                        archived_entries.append(line)
                        continue
            except (json.JSONDecodeError, ValueError):
                pass  # Keep unparseable lines in current
            current_entries.append(line)

        if not archived_entries:
            return None

        # Write archived entries to timestamped archive file
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        archive_name = f"{log_file.name}.archive.{timestamp}"
        archive_path = log_file.parent / archive_name

        try:
            archive_path.write_text(
                "\n".join(archived_entries) + "\n", encoding="utf-8"
            )
            # Rewrite active log with only current entries
            log_file.write_text(
                "\n".join(current_entries) + "\n", encoding="utf-8"
            )
            return {
                "action": "retention_rotation",
                "archived_count": len(archived_entries),
                "archive_file": archive_name,
            }
        except OSError as exc:
            logger.warning("Could not write audit archive: %s", exc)
            return None
