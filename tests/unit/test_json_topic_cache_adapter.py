"""Integration tests for JsonTopicCacheAdapter.

Tests the real file-based adapter with tmp_path for filesystem isolation.
Validates: write/read round-trip, TTL freshness, atomic writes,
missing file handling, and corrupt file handling.

Test Budget: 5 behaviors x 2 = 10 max. Using 7 tests.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from pes.adapters.json_topic_cache_adapter import JsonTopicCacheAdapter
from pes.ports.topic_cache_port import CacheResult


def _make_topics(count: int = 3) -> list[dict[str, Any]]:
    """Build a list of enriched topic dicts for testing."""
    return [
        {
            "topic_id": f"AF263-{i:03d}",
            "title": f"Topic {i}",
            "description": f"Description for topic {i}" * 50,
            "enrichment_status": "ok",
        }
        for i in range(1, count + 1)
    ]


def _make_metadata(
    scrape_date: str | None = None,
    source: str = "dsip_api",
    ttl_hours: int = 24,
    total_topics: int = 247,
) -> dict[str, Any]:
    """Build cache metadata dict."""
    return {
        "scrape_date": scrape_date or datetime.now().isoformat(),
        "source": source,
        "ttl_hours": ttl_hours,
        "total_topics": total_topics,
        "enrichment_completeness": {
            "descriptions": 3,
            "instructions": 2,
            "qa": 1,
            "total": 3,
        },
    }


class TestJsonTopicCacheAdapterWriteRead:
    """Behavior 1: Write and read cache round-trip."""

    def test_write_then_read_returns_cache_result_with_all_fields(
        self, tmp_path: Path
    ) -> None:
        adapter = JsonTopicCacheAdapter(str(tmp_path))
        topics = _make_topics(42)
        metadata = _make_metadata()

        adapter.write(topics, metadata)
        result = adapter.read()

        assert result is not None
        assert isinstance(result, CacheResult)
        assert len(result.topics) == 42
        assert result.source == "dsip_api"
        assert result.scrape_date is not None
        assert result.total_topics == 247
        assert result.enrichment_completeness["descriptions"] == 3

    def test_write_creates_cache_file_with_valid_json(
        self, tmp_path: Path
    ) -> None:
        adapter = JsonTopicCacheAdapter(str(tmp_path))
        topics = _make_topics(2)
        metadata = _make_metadata()

        adapter.write(topics, metadata)

        cache_file = tmp_path / "dsip_topics.json"
        assert cache_file.exists()
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        assert "topics" in data
        assert "scrape_date" in data
        assert "source" in data
        assert len(data["topics"]) == 2


class TestJsonTopicCacheAdapterFreshness:
    """Behavior 2: TTL-based freshness check."""

    @pytest.mark.parametrize(
        "hours_ago,ttl_hours,expected_fresh",
        [
            (12, 24, True),   # 12h old, 24h TTL -> fresh
            (36, 24, False),  # 36h old, 24h TTL -> stale
            (23, 24, True),   # just under TTL -> fresh
            (25, 24, False),  # just over TTL -> stale
            (0, 1, True),     # just written, 1h TTL -> fresh
        ],
    )
    def test_is_fresh_based_on_ttl(
        self,
        tmp_path: Path,
        hours_ago: int,
        ttl_hours: int,
        expected_fresh: bool,
    ) -> None:
        adapter = JsonTopicCacheAdapter(str(tmp_path))
        scrape_date = (datetime.now() - timedelta(hours=hours_ago)).isoformat()
        metadata = _make_metadata(scrape_date=scrape_date, ttl_hours=ttl_hours)
        adapter.write(_make_topics(1), metadata)

        result = adapter.is_fresh(ttl_hours)

        assert result is expected_fresh


class TestJsonTopicCacheAdapterAtomicWrite:
    """Behavior 3: Atomic write with backup."""

    def test_second_write_creates_backup_file(self, tmp_path: Path) -> None:
        adapter = JsonTopicCacheAdapter(str(tmp_path))
        # First write
        adapter.write(_make_topics(1), _make_metadata())
        # Second write (should create .bak)
        adapter.write(_make_topics(2), _make_metadata())

        bak_file = tmp_path / "dsip_topics.json.bak"
        assert bak_file.exists()
        bak_data = json.loads(bak_file.read_text(encoding="utf-8"))
        assert len(bak_data["topics"]) == 1  # Original data backed up

    def test_write_creates_directory_if_absent(self, tmp_path: Path) -> None:
        nested = tmp_path / "nested" / ".sbir"
        adapter = JsonTopicCacheAdapter(str(nested))

        adapter.write(_make_topics(1), _make_metadata())

        assert (nested / "dsip_topics.json").exists()


class TestJsonTopicCacheAdapterMissingFile:
    """Behavior 4: Missing cache file returns None."""

    def test_read_returns_none_when_no_file(self, tmp_path: Path) -> None:
        adapter = JsonTopicCacheAdapter(str(tmp_path))
        result = adapter.read()
        assert result is None

    def test_is_fresh_returns_false_when_no_file(self, tmp_path: Path) -> None:
        adapter = JsonTopicCacheAdapter(str(tmp_path))
        result = adapter.is_fresh(24)
        assert result is False


class TestJsonTopicCacheAdapterCorruptFile:
    """Behavior 5: Corrupt cache file returns None gracefully."""

    def test_read_returns_none_for_corrupt_json(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "dsip_topics.json"
        cache_file.write_text("not valid json {{{", encoding="utf-8")

        adapter = JsonTopicCacheAdapter(str(tmp_path))
        result = adapter.read()

        assert result is None
