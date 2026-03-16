"""Integration tests for FilesystemImageRegistryAdapter.

Tests the adapter against a real filesystem using tmp_path.
Validates: add, read-by-id, read-all, update-flag, duplicate merge,
and atomic JSON persistence.
"""

from __future__ import annotations

import json

import pytest

from pes.domain.corpus_image import ImageEntry, QualityLevel
from pes.ports.image_registry_port import ImageRegistryPort
from pes.adapters.filesystem_image_registry_adapter import (
    FilesystemImageRegistryAdapter,
)


@pytest.fixture()
def registry(tmp_path) -> FilesystemImageRegistryAdapter:
    """Adapter backed by a temporary directory."""
    sbir_dir = tmp_path / ".sbir" / "corpus"
    sbir_dir.mkdir(parents=True)
    return FilesystemImageRegistryAdapter(str(sbir_dir))


def _make_entry(
    *,
    image_id: str = "af243-001-p07-img01",
    source_proposal: str = "AF243-001",
    page_number: int = 7,
    caption: str = "Figure 3: CDES System Architecture",
    figure_type: str = "system-diagram",
    dpi: int = 300,
    content_hash: str = "abc123deadbeef",
    compliance_flag: str | None = None,
) -> ImageEntry:
    return ImageEntry(
        id=image_id,
        source_proposal=source_proposal,
        page_number=page_number,
        caption=caption,
        figure_type=figure_type,
        dpi=dpi,
        content_hash=content_hash,
        quality_level=QualityLevel.from_dpi(dpi),
        compliance_flag=compliance_flag,
    )


class TestFilesystemImageRegistryAdapter:
    """Integration tests -- real filesystem, no mocks."""

    def test_add_and_read_by_id(self, registry: FilesystemImageRegistryAdapter):
        entry = _make_entry()
        added = registry.add(entry)
        assert added is True

        retrieved = registry.get_by_id("af243-001-p07-img01")
        assert retrieved is not None
        assert retrieved.source_proposal == "AF243-001"
        assert retrieved.caption == "Figure 3: CDES System Architecture"
        assert retrieved.dpi == 300
        assert retrieved.content_hash == "abc123deadbeef"
        assert retrieved.compliance_flag is None

    def test_read_all_returns_all_entries(
        self, registry: FilesystemImageRegistryAdapter
    ):
        registry.add(_make_entry(image_id="img-01", content_hash="hash-a"))
        registry.add(_make_entry(image_id="img-02", content_hash="hash-b"))

        all_entries = registry.get_all()
        assert len(all_entries) == 2
        ids = {e.id for e in all_entries}
        assert ids == {"img-01", "img-02"}

    def test_update_flag(self, registry: FilesystemImageRegistryAdapter):
        registry.add(_make_entry())

        updated = registry.update_flag(
            "af243-001-p07-img01", "possible government-furnished"
        )
        assert updated is True

        entry = registry.get_by_id("af243-001-p07-img01")
        assert entry is not None
        assert entry.compliance_flag == "possible government-furnished"

    def test_update_flag_nonexistent_returns_false(
        self, registry: FilesystemImageRegistryAdapter
    ):
        result = registry.update_flag("nonexistent", "flag")
        assert result is False

    def test_duplicate_hash_merges_sources(
        self, registry: FilesystemImageRegistryAdapter
    ):
        entry_a = _make_entry(
            image_id="af243-p01",
            source_proposal="AF243-001",
            content_hash="shared-hash",
        )
        entry_b = _make_entry(
            image_id="darpa-p01",
            source_proposal="DARPA-HR-22",
            content_hash="shared-hash",
        )

        assert registry.add(entry_a) is True
        assert registry.add(entry_b) is False  # duplicate

        all_entries = registry.get_all()
        assert len(all_entries) == 1  # not duplicated

        original = all_entries[0]
        all_sources = [original.source_proposal] + list(
            original.duplicate_sources
        )
        assert "AF243-001" in all_sources
        assert "DARPA-HR-22" in all_sources

    def test_persists_to_json_file(
        self, registry: FilesystemImageRegistryAdapter, tmp_path
    ):
        registry.add(_make_entry())

        json_path = tmp_path / ".sbir" / "corpus" / "image-registry.json"
        assert json_path.exists()

        data = json.loads(json_path.read_text(encoding="utf-8"))
        assert len(data["entries"]) == 1
        assert data["entries"][0]["id"] == "af243-001-p07-img01"

    def test_atomic_write_no_partial_file(
        self, registry: FilesystemImageRegistryAdapter, tmp_path
    ):
        """After a successful write, no .tmp file should remain."""
        registry.add(_make_entry())

        tmp_file = (
            tmp_path / ".sbir" / "corpus" / "image-registry.json.tmp"
        )
        assert not tmp_file.exists()

    def test_read_by_id_nonexistent_returns_none(
        self, registry: FilesystemImageRegistryAdapter
    ):
        assert registry.get_by_id("nonexistent") is None

    def test_get_all_empty_registry(
        self, registry: FilesystemImageRegistryAdapter
    ):
        assert registry.get_all() == []
