"""Tests for FilesystemFeedbackAdapter -- feedback persistence through port boundary.

Tests exercise the FeedbackWriterPort via FilesystemFeedbackAdapter using real
filesystem (tmp_path). Verifies atomic writes, filename conventions, directory
creation, and JSON schema compliance.

Test Budget: 5 distinct behaviors x 2 = 10 max. Using 5.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pes.adapters.filesystem_feedback_adapter import FilesystemFeedbackAdapter
from pes.domain.feedback import (
    FeedbackEntry,
    FeedbackSnapshot,
    FeedbackType,
    QualityRatings,
)


def _make_entry(timestamp: str = "2026-03-25T10:00:00Z") -> FeedbackEntry:
    snapshot = FeedbackSnapshot(
        plugin_version="1.0.0",
        proposal_id="AF243-001",
        topic_id="AF243-D001",
        topic_title="AI Navigation",
        topic_agency="USAF",
        topic_deadline="2026-06-01",
        topic_phase="Phase I",
        current_wave=3,
        completed_waves=[1, 2],
        skipped_waves=[],
        rigor_profile="standard",
        company_name="Acme Corp",
        company_profile_age_days=10,
        finder_results_age_days=5,
    )
    return FeedbackEntry(
        feedback_id="fb-001",
        timestamp=timestamp,
        type=FeedbackType.QUALITY,
        ratings=QualityRatings(past_performance=4, writing_quality=3),
        free_text="Looks good",
        context_snapshot=snapshot,
    )


@pytest.fixture()
def adapter() -> FilesystemFeedbackAdapter:
    return FilesystemFeedbackAdapter()


class TestFeedbackFilename:
    """Filename uses feedback-{timestamp}.json with colons replaced by hyphens."""

    def test_write_returns_path_with_colon_free_filename(
        self, adapter: FilesystemFeedbackAdapter, tmp_path: Path
    ) -> None:
        entry = _make_entry("2026-03-25T18:30:00Z")
        output_dir = tmp_path / "feedback"

        result = adapter.write(entry, output_dir)

        assert result.name == "feedback-2026-03-25T18-30-00Z.json"


class TestFeedbackDirectoryCreation:
    """Output directory is created automatically if absent."""

    def test_write_creates_output_directory_when_absent(
        self, adapter: FilesystemFeedbackAdapter, tmp_path: Path
    ) -> None:
        entry = _make_entry()
        output_dir = tmp_path / "deeply" / "nested" / "feedback"
        assert not output_dir.exists()

        adapter.write(entry, output_dir)

        assert output_dir.is_dir()


class TestFeedbackJsonContent:
    """Written file is valid JSON matching entry.to_dict()."""

    def test_written_file_contains_json_matching_entry_to_dict(
        self, adapter: FilesystemFeedbackAdapter, tmp_path: Path
    ) -> None:
        entry = _make_entry()
        output_dir = tmp_path / "feedback"

        result_path = adapter.write(entry, output_dir)

        data = json.loads(result_path.read_text(encoding="utf-8"))
        assert data == entry.to_dict()


class TestFeedbackAtomicWrite:
    """Atomic write: .tmp does not remain; .bak created when target exists."""

    def test_no_tmp_file_remains_after_write(
        self, adapter: FilesystemFeedbackAdapter, tmp_path: Path
    ) -> None:
        entry = _make_entry()
        output_dir = tmp_path / "feedback"

        result_path = adapter.write(entry, output_dir)

        tmp_file = result_path.parent / (result_path.name + ".tmp")
        assert not tmp_file.exists()

    def test_creates_backup_when_target_already_exists(
        self, adapter: FilesystemFeedbackAdapter, tmp_path: Path
    ) -> None:
        entry = _make_entry("2026-03-25T10:00:00Z")
        output_dir = tmp_path / "feedback"

        # Write once to create the target
        result_path = adapter.write(entry, output_dir)
        # Write again to trigger backup
        adapter.write(entry, output_dir)

        bak_file = result_path.parent / (result_path.name + ".bak")
        assert bak_file.exists()
