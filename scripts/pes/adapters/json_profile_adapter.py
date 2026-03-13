"""JSON file adapter for company profile persistence.

Implements ProfilePort using JSON files with atomic write pattern:
write .tmp -> backup .bak -> rename .tmp to target.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pes.ports.profile_port import ProfileMetadata, ProfilePort

PROFILE_FILENAME = "company-profile.json"


class JsonProfileAdapter(ProfilePort):
    """JSON file-based profile persistence with atomic writes."""

    def __init__(self, profile_dir: str) -> None:
        self._profile_dir = Path(profile_dir)
        self._profile_file = self._profile_dir / PROFILE_FILENAME
        self._tmp_file = self._profile_dir / f"{PROFILE_FILENAME}.tmp"
        self._bak_file = self._profile_dir / f"{PROFILE_FILENAME}.bak"

    def read(self) -> dict[str, Any] | None:
        """Read the company profile from JSON file.

        Returns None if no profile exists.
        """
        if not self._profile_file.exists():
            return None

        text = self._profile_file.read_text(encoding="utf-8")
        result: dict[str, Any] = json.loads(text)
        return result

    def write(self, profile: dict[str, Any]) -> None:
        """Write profile atomically: .tmp -> backup .bak -> rename .tmp to target."""
        # Create directory if absent
        self._profile_dir.mkdir(parents=True, exist_ok=True)

        # Write to temporary file first
        self._tmp_file.write_text(
            json.dumps(profile, indent=2), encoding="utf-8"
        )

        # Backup existing profile if present
        if self._profile_file.exists():
            self._bak_file.write_bytes(self._profile_file.read_bytes())

        # Atomic rename: .tmp -> target
        self._tmp_file.replace(self._profile_file)

    def exists(self) -> bool:
        """Check whether company-profile.json exists."""
        return self._profile_file.exists()

    def metadata(self) -> ProfileMetadata:
        """Return metadata about the existing profile."""
        if not self._profile_file.exists():
            return ProfileMetadata(exists=False)

        text = self._profile_file.read_text(encoding="utf-8")
        data: dict[str, Any] = json.loads(text)
        stat = self._profile_file.stat()
        last_modified = datetime.fromtimestamp(
            stat.st_mtime, tz=timezone.utc
        ).isoformat()

        return ProfileMetadata(
            exists=True,
            company_name=data.get("company_name"),
            last_modified=last_modified,
        )
