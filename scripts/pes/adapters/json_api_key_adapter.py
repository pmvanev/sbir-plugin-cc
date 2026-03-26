"""JSON file adapter for API key persistence.

Implements ApiKeyPort using a single api-keys.json file.
Keys are stored as {service_name: key_value} entries.
File permissions are set to owner-only (0o600) on Unix.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from pes.ports.api_key_port import ApiKeyError, ApiKeyPort

API_KEYS_FILENAME = "api-keys.json"


class JsonApiKeyAdapter(ApiKeyPort):
    """JSON file-based API key persistence with restricted permissions."""

    def __init__(self, key_dir: str) -> None:
        self._key_dir = Path(key_dir)
        self._keys_file = self._key_dir / API_KEYS_FILENAME

    def read_key(self, service_name: str) -> str | None:
        """Read a stored API key for the given service.

        Returns None if the key file does not exist or the service
        has no entry. Raises ApiKeyError on malformed JSON.
        """
        if not self._keys_file.exists():
            return None

        try:
            text = self._keys_file.read_text(encoding="utf-8")
            data: dict[str, Any] = json.loads(text)
        except (json.JSONDecodeError, ValueError) as exc:
            msg = f"API key file is malformed: {self._keys_file} ({exc})"
            raise ApiKeyError(msg) from exc

        return data.get(service_name)

    def write_key(self, service_name: str, key: str) -> None:
        """Save an API key, creating the directory if absent.

        Reads existing keys first (to preserve other service entries),
        then writes atomically and sets owner-only permissions on Unix.
        """
        self._key_dir.mkdir(parents=True, exist_ok=True)

        # Preserve existing keys
        existing: dict[str, Any] = {}
        if self._keys_file.exists():
            try:
                text = self._keys_file.read_text(encoding="utf-8")
                existing = json.loads(text)
            except (json.JSONDecodeError, ValueError):
                existing = {}

        existing[service_name] = key

        # Write atomically via tmp file
        tmp_file = self._key_dir / f"{API_KEYS_FILENAME}.tmp"
        tmp_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        tmp_file.replace(self._keys_file)

        # Set owner-only permissions on Unix
        if sys.platform != "win32":
            os.chmod(self._keys_file, 0o600)
