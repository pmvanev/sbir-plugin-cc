"""Tests for JsonApiKeyAdapter -- API key persistence through port boundary.

Tests exercise the ApiKeyPort via JsonApiKeyAdapter using real filesystem
(tmp_path). Verifies read/write round-trip, missing file handling, malformed
file error, directory creation, and file permissions.

Test Budget: 5 distinct behaviors x 2 = 10 max. Using 5.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from pes.adapters.json_api_key_adapter import API_KEYS_FILENAME, JsonApiKeyAdapter
from pes.ports.api_key_port import ApiKeyError


@pytest.fixture()
def key_dir(tmp_path: Path) -> Path:
    """Fresh temporary directory simulating ~/.sbir/."""
    sbir_dir = tmp_path / ".sbir"
    sbir_dir.mkdir()
    return sbir_dir


@pytest.fixture()
def adapter(key_dir: Path) -> JsonApiKeyAdapter:
    return JsonApiKeyAdapter(str(key_dir))


# ---------- B1: read_key returns stored key ----------


def test_read_key_returns_stored_key(adapter, key_dir):
    """Given a valid api-keys.json with sam_gov key, read_key returns the key."""
    keys_file = key_dir / "api-keys.json"
    keys_file.write_text(json.dumps({"sam_gov": "my-secret-api-key-1234"}))

    result = adapter.read_key("sam_gov")

    assert result == "my-secret-api-key-1234"


# ---------- B2: read_key returns None when no file ----------


def test_read_key_returns_none_when_no_file(tmp_path):
    """Given no api-keys.json file, read_key returns None without error."""
    adapter = JsonApiKeyAdapter(str(tmp_path / "nonexistent"))

    result = adapter.read_key("sam_gov")

    assert result is None


# ---------- B3: read_key raises ApiKeyError on malformed JSON ----------


def test_read_key_raises_error_on_malformed_json(adapter, key_dir):
    """Given malformed api-keys.json, read_key raises ApiKeyError with clear message."""
    keys_file = key_dir / "api-keys.json"
    keys_file.write_text("{not valid json!!!")

    with pytest.raises(ApiKeyError, match="malformed"):
        adapter.read_key("sam_gov")


# ---------- B4: write_key creates directory and file ----------


def test_write_key_creates_directory_and_file(tmp_path):
    """Given a non-existent directory, write_key creates it and saves the key."""
    new_dir = tmp_path / "brand-new" / ".sbir"
    adapter = JsonApiKeyAdapter(str(new_dir))

    adapter.write_key("sam_gov", "new-key-value-5678")

    # Verify round-trip
    assert adapter.read_key("sam_gov") == "new-key-value-5678"
    # Verify directory was created
    assert new_dir.exists()


# ---------- B5: write_key sets owner-only permissions (Unix) ----------


@pytest.mark.skipif(sys.platform == "win32", reason="Unix permissions not available on Windows")
def test_write_key_sets_owner_only_permissions(adapter, key_dir):
    """Given a key value, write_key sets file to owner-only read/write (0o600)."""
    adapter.write_key("sam_gov", "secret-key-9999")

    keys_file = key_dir / "api-keys.json"
    mode = os.stat(keys_file).st_mode & 0o777
    assert mode == 0o600


# ---------- Mutation-killing tests ----------


class TestJsonApiKeyMutationKillers:
    """Targeted tests to kill surviving mutants in json_api_key_adapter.py."""

    def test_api_keys_filename_constant(self):
        """Kill mutant: API_KEYS_FILENAME string mutation."""
        assert API_KEYS_FILENAME == "api-keys.json"

    def test_read_key_missing_service_returns_none(self, adapter, key_dir):
        """Kill mutant: data.get(service_name) returns None for missing key."""
        keys_file = key_dir / "api-keys.json"
        keys_file.write_text(json.dumps({"other_service": "key-123"}))
        result = adapter.read_key("sam_gov")
        assert result is None

    def test_write_key_preserves_existing_keys(self, adapter, key_dir):
        """Kill mutant: existing key preservation logic."""
        keys_file = key_dir / "api-keys.json"
        keys_file.write_text(json.dumps({"other": "existing-key"}))

        adapter.write_key("sam_gov", "new-key")

        stored = json.loads(keys_file.read_text())
        assert stored["other"] == "existing-key"
        assert stored["sam_gov"] == "new-key"

    def test_write_key_overwrites_existing_service_key(self, adapter, key_dir):
        """Kill mutant: existing[service_name] = key assignment."""
        keys_file = key_dir / "api-keys.json"
        keys_file.write_text(json.dumps({"sam_gov": "old-key"}))

        adapter.write_key("sam_gov", "new-key")

        stored = json.loads(keys_file.read_text())
        assert stored["sam_gov"] == "new-key"

    def test_write_key_handles_malformed_existing_file(self, adapter, key_dir):
        """Kill mutant: except clause resetting existing to {}."""
        keys_file = key_dir / "api-keys.json"
        keys_file.write_text("{bad json!!!")

        adapter.write_key("sam_gov", "recovered-key")

        stored = json.loads(keys_file.read_text())
        assert stored["sam_gov"] == "recovered-key"
        assert len(stored) == 1  # Old data discarded

    def test_read_key_error_message_contains_file_path(self, adapter, key_dir):
        """Kill mutant: error message format string mutation."""
        keys_file = key_dir / "api-keys.json"
        keys_file.write_text("{not valid")

        with pytest.raises(ApiKeyError) as exc_info:
            adapter.read_key("sam_gov")
        assert "malformed" in str(exc_info.value)
        assert str(keys_file) in str(exc_info.value)

    def test_write_key_uses_atomic_rename(self, adapter, key_dir):
        """Kill mutant: tmp file path and replace() call."""
        adapter.write_key("sam_gov", "atomic-key")
        # tmp file should not exist after write
        tmp_file = key_dir / f"{API_KEYS_FILENAME}.tmp"
        assert not tmp_file.exists()
        # actual file should exist with correct content
        keys_file = key_dir / API_KEYS_FILENAME
        assert keys_file.exists()
        stored = json.loads(keys_file.read_text())
        assert stored["sam_gov"] == "atomic-key"

    def test_write_key_creates_parents(self, tmp_path):
        """Kill mutant: parents=True in mkdir."""
        deep_dir = tmp_path / "a" / "b" / "c"
        adapter = JsonApiKeyAdapter(str(deep_dir))
        adapter.write_key("test", "value")
        assert deep_dir.exists()
        assert adapter.read_key("test") == "value"

    def test_keys_file_path_construction(self, key_dir):
        """Kill mutant: key_dir / API_KEYS_FILENAME path join."""
        adapter = JsonApiKeyAdapter(str(key_dir))
        assert adapter._keys_file == key_dir / "api-keys.json"

    def test_write_key_json_is_indented(self, adapter, key_dir):
        """Kill mutant: json.dumps indent=2 parameter."""
        adapter.write_key("sam_gov", "key-123")
        keys_file = key_dir / "api-keys.json"
        text = keys_file.read_text()
        # Indented JSON has newlines and spaces
        assert "\n" in text
        assert "  " in text

    def test_read_key_uses_utf8_encoding(self, adapter, key_dir):
        """Kill mutant: encoding='utf-8' parameter."""
        keys_file = key_dir / "api-keys.json"
        keys_file.write_text(json.dumps({"test": "val\u00fc\u00e9"}), encoding="utf-8")
        result = adapter.read_key("test")
        assert result == "val\u00fc\u00e9"
