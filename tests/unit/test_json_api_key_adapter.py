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

from pes.adapters.json_api_key_adapter import JsonApiKeyAdapter
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
