"""Filesystem image registry adapter.

Implements ImageRegistryPort by persisting image entries to
.sbir/corpus/image-registry.json with atomic writes.

Atomic write pattern: write .tmp -> backup .bak -> rename .tmp to target.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pes.domain.corpus_image import ImageEntry, QualityLevel
from pes.ports.image_registry_port import ImageRegistryPort

REGISTRY_FILENAME = "image-registry.json"


class FilesystemImageRegistryAdapter(ImageRegistryPort):
    """JSON file-backed image registry with atomic writes."""

    def __init__(self, registry_dir: str) -> None:
        self._dir = Path(registry_dir)
        self._file = self._dir / REGISTRY_FILENAME
        self._tmp = self._dir / f"{REGISTRY_FILENAME}.tmp"
        self._bak = self._dir / f"{REGISTRY_FILENAME}.bak"
        self._entries: list[ImageEntry] = []
        self._hashes: dict[str, int] = {}  # hash -> index in _entries
        self._load()

    # -- Port interface --

    def add(self, entry: ImageEntry) -> bool:
        if entry.content_hash in self._hashes:
            idx = self._hashes[entry.content_hash]
            self._entries[idx] = self._entries[idx].with_merged_source(
                entry.source_proposal
            )
            self._persist()
            return False
        self._hashes[entry.content_hash] = len(self._entries)
        self._entries.append(entry)
        self._persist()
        return True

    def get_by_id(self, image_id: str) -> ImageEntry | None:
        for entry in self._entries:
            if entry.id == image_id:
                return entry
        return None

    def get_all(self) -> list[ImageEntry]:
        return list(self._entries)

    def update_flag(self, image_id: str, flag: str | None) -> bool:
        for i, entry in enumerate(self._entries):
            if entry.id == image_id:
                self._entries[i] = entry.with_flag(flag)
                self._persist()
                return True
        return False

    # -- Persistence --

    def _persist(self) -> None:
        """Write registry to JSON with atomic write pattern."""
        data = {
            "entries": [self._entry_to_dict(e) for e in self._entries],
        }
        self._tmp.write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )
        if self._file.exists():
            self._bak.write_bytes(self._file.read_bytes())
        self._tmp.replace(self._file)

    def _load(self) -> None:
        """Load existing registry from JSON file if present."""
        if not self._file.exists():
            return
        try:
            text = self._file.read_text(encoding="utf-8")
            data = json.loads(text)
            for raw in data.get("entries", []):
                entry = self._dict_to_entry(raw)
                self._hashes[entry.content_hash] = len(self._entries)
                self._entries.append(entry)
        except (json.JSONDecodeError, KeyError):
            # Corrupted file -- start fresh
            self._entries.clear()
            self._hashes.clear()

    @staticmethod
    def _entry_to_dict(entry: ImageEntry) -> dict[str, Any]:
        return {
            "id": entry.id,
            "source_proposal": entry.source_proposal,
            "page_number": entry.page_number,
            "caption": entry.caption,
            "figure_type": entry.figure_type,
            "dpi": entry.dpi,
            "content_hash": entry.content_hash,
            "quality_level": entry.quality_level.value,
            "extraction_date": entry.extraction_date,
            "agency": entry.agency,
            "origin_type": entry.origin_type,
            "compliance_flag": entry.compliance_flag,
            "duplicate_sources": list(entry.duplicate_sources),
        }

    @staticmethod
    def _dict_to_entry(raw: dict[str, Any]) -> ImageEntry:
        return ImageEntry(
            id=raw["id"],
            source_proposal=raw["source_proposal"],
            page_number=raw["page_number"],
            caption=raw["caption"],
            figure_type=raw["figure_type"],
            dpi=raw["dpi"],
            content_hash=raw["content_hash"],
            quality_level=QualityLevel(raw["quality_level"]),
            extraction_date=raw.get("extraction_date", ""),
            agency=raw.get("agency", ""),
            origin_type=raw.get("origin_type", "company-created"),
            compliance_flag=raw.get("compliance_flag"),
            duplicate_sources=tuple(raw.get("duplicate_sources", ())),
        )
