"""JSON file adapter for topic data caching with TTL-based freshness.

Implements TopicCachePort using JSON files with atomic write pattern:
write .tmp -> backup .bak -> rename .tmp to target.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pes.ports.topic_cache_port import CacheResult, TopicCachePort

CACHE_FILENAME = "dsip_topics.json"


class JsonTopicCacheAdapter(TopicCachePort):
    """JSON file-based topic cache with atomic writes and TTL freshness."""

    def __init__(self, cache_dir: str) -> None:
        self._cache_dir = Path(cache_dir)
        self._cache_file = self._cache_dir / CACHE_FILENAME
        self._tmp_file = self._cache_dir / f"{CACHE_FILENAME}.tmp"
        self._bak_file = self._cache_dir / f"{CACHE_FILENAME}.bak"

    def read(self) -> CacheResult | None:
        """Read cached topic data from JSON file.

        Returns None if no file exists or file contains invalid JSON.
        """
        if not self._cache_file.exists():
            return None

        try:
            text = self._cache_file.read_text(encoding="utf-8")
            data: dict[str, Any] = json.loads(text)
        except (json.JSONDecodeError, OSError):
            return None

        return CacheResult(
            topics=data.get("topics", []),
            scrape_date=data.get("scrape_date", ""),
            source=data.get("source", ""),
            ttl_hours=data.get("ttl_hours", 24),
            total_topics=data.get("total_topics", 0),
            enrichment_completeness=data.get("enrichment_completeness", {}),
            filters_applied=data.get("filters_applied", {}),
        )

    def write(self, topics: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
        """Write topics atomically: .tmp -> backup .bak -> rename .tmp to target."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        cache_data = {
            **metadata,
            "topics": topics,
        }

        # Write to temporary file first
        self._tmp_file.write_text(
            json.dumps(cache_data, indent=2), encoding="utf-8"
        )

        # Backup existing cache if present
        if self._cache_file.exists():
            self._bak_file.write_bytes(self._cache_file.read_bytes())

        # Atomic rename: .tmp -> target
        self._tmp_file.replace(self._cache_file)

    def is_fresh(self, ttl_hours: int = 24) -> bool:
        """Check if cached data is fresh within the TTL window."""
        result = self.read()
        if result is None:
            return False
        return result.is_fresh(ttl_hours)

    def exists(self) -> bool:
        """Check whether dsip_topics.json exists."""
        return self._cache_file.exists()
