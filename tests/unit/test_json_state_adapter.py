"""Tests for JsonStateAdapter -- state persistence through port boundary.

Tests exercise the StateReader/StateWriter ports via JsonStateAdapter
using real filesystem (tmp_path). This verifies atomic writes, crash
recovery, and error handling with actual file operations.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pes.adapters.json_state_adapter import JsonStateAdapter
from pes.domain.state import StateCorruptedError, StateNotFoundError


@pytest.fixture()
def state_dir(tmp_path: Path) -> Path:
    """Create a fresh .sbir directory for each test."""
    sbir = tmp_path / ".sbir"
    sbir.mkdir()
    return sbir


@pytest.fixture()
def adapter(state_dir: Path) -> JsonStateAdapter:
    """JsonStateAdapter pointed at temp .sbir directory."""
    return JsonStateAdapter(str(state_dir))


@pytest.fixture()
def sample_state() -> dict:
    """Minimal valid proposal state."""
    return {
        "schema_version": "1.0.0",
        "proposal_id": "test-uuid-001",
        "topic": {
            "id": "AF243-001",
            "agency": "Air Force",
            "phase": "I",
            "deadline": "2026-04-15",
            "title": "Test Topic",
            "solicitation_url": None,
        },
        "go_no_go": "pending",
        "current_wave": 0,
        "waves": {
            "0": {"status": "not_started", "completed_at": None},
        },
        "created_at": "2026-03-01T10:00:00Z",
        "updated_at": "2026-03-01T10:00:00Z",
    }


class TestJsonStateAdapterSaveAndLoad:
    """Save and load round-trip through StateWriter/StateReader ports."""

    def test_saves_and_loads_state(self, adapter: JsonStateAdapter, sample_state: dict) -> None:
        adapter.save(sample_state)
        loaded = adapter.load()
        assert loaded["proposal_id"] == "test-uuid-001"
        assert loaded["schema_version"] == "1.0.0"
        assert loaded["go_no_go"] == "pending"

    def test_exists_reflects_file_presence(
        self, adapter: JsonStateAdapter, sample_state: dict
    ) -> None:
        assert adapter.exists() is False
        adapter.save(sample_state)
        assert adapter.exists() is True


class TestJsonStateAdapterMissingState:
    """Missing state file raises StateNotFoundError with helpful message."""

    def test_load_missing_file_raises_with_helpful_message(
        self, adapter: JsonStateAdapter
    ) -> None:
        with pytest.raises(StateNotFoundError) as exc_info:
            adapter.load()
        message = str(exc_info.value)
        assert "No active proposal found" in message
        assert "/proposal new" in message


class TestJsonStateAdapterAtomicWrite:
    """Atomic write pattern: .tmp -> backup .bak -> rename to target."""

    def test_atomic_write_creates_backup_on_second_save(
        self, adapter: JsonStateAdapter, sample_state: dict, state_dir: Path
    ) -> None:
        adapter.save(sample_state)
        sample_state["go_no_go"] = "go"
        adapter.save(sample_state)

        bak_file = state_dir / "proposal-state.json.bak"
        assert bak_file.exists()
        backup_data = json.loads(bak_file.read_text())
        assert backup_data["go_no_go"] == "pending"

    def test_no_tmp_file_remains_after_save(
        self, adapter: JsonStateAdapter, sample_state: dict, state_dir: Path
    ) -> None:
        adapter.save(sample_state)
        tmp_file = state_dir / "proposal-state.json.tmp"
        assert not tmp_file.exists()


class TestJsonStateAdapterCorruptionRecovery:
    """Corrupted state detected with recovery from .bak."""

    def test_corrupted_file_raises_state_corrupted_error(
        self, adapter: JsonStateAdapter, state_dir: Path
    ) -> None:
        state_file = state_dir / "proposal-state.json"
        state_file.write_text('{"schema_version": "1.0.0", "broken')
        with pytest.raises(StateCorruptedError):
            adapter.load()

    def test_corrupted_file_recovers_from_backup(
        self, adapter: JsonStateAdapter, sample_state: dict, state_dir: Path
    ) -> None:
        # Save valid state (creates the file)
        adapter.save(sample_state)
        # Save again to create .bak
        sample_state["go_no_go"] = "go"
        adapter.save(sample_state)
        # Corrupt the main file
        state_file = state_dir / "proposal-state.json"
        state_file.write_text('{"truncated": true')

        with pytest.raises(StateCorruptedError) as exc_info:
            adapter.load()
        assert exc_info.value.recovered_state is not None
        assert exc_info.value.recovered_state["go_no_go"] == "pending"
