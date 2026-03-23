"""Tests for FilesystemRigorAdapter -- rigor persistence through port boundary.

Tests exercise the RigorProfileReader/Writer, RigorDefinitionsReader,
and ModelTierReader ports via FilesystemRigorAdapter using real filesystem
(tmp_path). Verifies atomic writes, override detection, and read/write
round-trips with actual file operations.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pes.adapters.filesystem_rigor_adapter import FilesystemRigorAdapter


SAMPLE_PROFILE = {
    "schema_version": "1.0",
    "profile_name": "standard",
    "agent_roles": {
        "writer": "standard",
        "reviewer": "basic",
    },
    "review_passes": 1,
    "critique_max_iterations": 2,
    "iteration_cap": 2,
}

SAMPLE_DEFINITIONS = {
    "schema_version": "1.0",
    "profiles": {
        "lean": {"roles": {"writer": "basic"}, "review_passes": 0},
        "standard": {"roles": {"writer": "standard"}, "review_passes": 1},
    },
}

SAMPLE_TIERS = {
    "schema_version": "1.0",
    "tiers": {
        "basic": {"model_id": "claude-haiku-4-5-20251001"},
        "standard": {"model_id": "claude-sonnet-4-6-20250514"},
    },
}


@pytest.fixture()
def adapter() -> FilesystemRigorAdapter:
    return FilesystemRigorAdapter()


class TestRigorProfileReadWrite:
    """Round-trip read/write through RigorProfileReader/Writer ports."""

    def test_saves_and_reads_profile(
        self, adapter: FilesystemRigorAdapter, tmp_path: Path
    ) -> None:
        proposal_dir = tmp_path / ".sbir" / "proposals" / "AF243-001"
        proposal_dir.mkdir(parents=True)

        adapter.write_profile(proposal_dir, SAMPLE_PROFILE)
        loaded = adapter.read_active_profile(proposal_dir)

        assert loaded is not None
        assert loaded["profile_name"] == "standard"
        assert loaded["review_passes"] == 1

    def test_read_missing_profile_returns_none(
        self, adapter: FilesystemRigorAdapter, tmp_path: Path
    ) -> None:
        proposal_dir = tmp_path / ".sbir" / "proposals" / "AF243-001"
        proposal_dir.mkdir(parents=True)

        result = adapter.read_active_profile(proposal_dir)
        assert result is None


class TestRigorProfileAtomicWrite:
    """Atomic write pattern: .tmp -> backup .bak -> rename to target."""

    def test_creates_backup_on_overwrite(
        self, adapter: FilesystemRigorAdapter, tmp_path: Path
    ) -> None:
        proposal_dir = tmp_path / ".sbir" / "proposals" / "AF243-001"
        proposal_dir.mkdir(parents=True)

        adapter.write_profile(proposal_dir, SAMPLE_PROFILE)

        updated = {**SAMPLE_PROFILE, "profile_name": "thorough"}
        adapter.write_profile(proposal_dir, updated)

        bak_file = proposal_dir / "rigor-profile.json.bak"
        assert bak_file.exists()
        backup_data = json.loads(bak_file.read_text())
        assert backup_data["profile_name"] == "standard"

    def test_no_tmp_file_remains_after_write(
        self, adapter: FilesystemRigorAdapter, tmp_path: Path
    ) -> None:
        proposal_dir = tmp_path / ".sbir" / "proposals" / "AF243-001"
        proposal_dir.mkdir(parents=True)

        adapter.write_profile(proposal_dir, SAMPLE_PROFILE)

        tmp_file = proposal_dir / "rigor-profile.json.tmp"
        assert not tmp_file.exists()

    def test_write_creates_directory_if_absent(
        self, adapter: FilesystemRigorAdapter, tmp_path: Path
    ) -> None:
        proposal_dir = tmp_path / ".sbir" / "proposals" / "AF243-001"
        # Do NOT mkdir -- adapter should create it

        adapter.write_profile(proposal_dir, SAMPLE_PROFILE)

        loaded = adapter.read_active_profile(proposal_dir)
        assert loaded is not None
        assert loaded["profile_name"] == "standard"


class TestRigorDefinitionsReader:
    """Read profile definitions from plugin config directory."""

    def test_reads_definitions_from_config(
        self, adapter: FilesystemRigorAdapter, tmp_path: Path
    ) -> None:
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "rigor-profiles.json").write_text(
            json.dumps(SAMPLE_DEFINITIONS), encoding="utf-8"
        )

        result = adapter.read_definitions(config_dir)
        assert "profiles" in result
        assert "lean" in result["profiles"]
        assert "standard" in result["profiles"]

    def test_raises_when_definitions_missing(
        self, adapter: FilesystemRigorAdapter, tmp_path: Path
    ) -> None:
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        with pytest.raises(FileNotFoundError):
            adapter.read_definitions(config_dir)


class TestModelTierReader:
    """Read model tier mapping with optional .sbir/ override."""

    def test_reads_tier_mapping_from_config(
        self, adapter: FilesystemRigorAdapter, tmp_path: Path
    ) -> None:
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "model-tiers.json").write_text(
            json.dumps(SAMPLE_TIERS), encoding="utf-8"
        )

        result = adapter.read_tier_mapping(config_dir)
        assert "tiers" in result
        assert "basic" in result["tiers"]

    def test_override_takes_precedence(
        self, adapter: FilesystemRigorAdapter, tmp_path: Path
    ) -> None:
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "model-tiers.json").write_text(
            json.dumps(SAMPLE_TIERS), encoding="utf-8"
        )

        override_dir = tmp_path / ".sbir"
        override_dir.mkdir()
        override_tiers = {
            "schema_version": "1.0",
            "tiers": {"basic": {"model_id": "custom-model"}},
        }
        (override_dir / "model-tiers.json").write_text(
            json.dumps(override_tiers), encoding="utf-8"
        )

        result = adapter.read_tier_mapping(config_dir, override_dir=override_dir)
        assert result["tiers"]["basic"]["model_id"] == "custom-model"

    def test_falls_back_to_config_when_no_override(
        self, adapter: FilesystemRigorAdapter, tmp_path: Path
    ) -> None:
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "model-tiers.json").write_text(
            json.dumps(SAMPLE_TIERS), encoding="utf-8"
        )

        override_dir = tmp_path / ".sbir"
        override_dir.mkdir()
        # No model-tiers.json in override dir

        result = adapter.read_tier_mapping(config_dir, override_dir=override_dir)
        assert result["tiers"]["basic"]["model_id"] == "claude-haiku-4-5-20251001"
