"""Port interface for topic data caching with TTL-based freshness.

Driven port: TopicCachePort
Defines the business contract for caching enriched topic data.
Adapters implement this for specific infrastructure (JSON files, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass
class CacheResult:
    """Result of reading cached topic data.

    Attributes:
        topics: List of enriched topic dicts.
        scrape_date: ISO timestamp of when the data was scraped.
        source: Data source identifier (e.g., "dsip_api").
        ttl_hours: Time-to-live in hours for freshness check.
        total_topics: Total topics available at source when scraped.
        enrichment_completeness: Counts of descriptions, instructions, qa, total.
        filters_applied: Filters used when cache was written.
    """

    topics: list[dict[str, Any]] = field(default_factory=list)
    scrape_date: str = ""
    source: str = ""
    ttl_hours: int = 24
    total_topics: int = 0
    enrichment_completeness: dict[str, int] = field(default_factory=dict)
    filters_applied: dict[str, Any] = field(default_factory=dict)

    def is_fresh(self, ttl_hours: int | None = None) -> bool:
        """Check if the cached data is fresh within the TTL window.

        Args:
            ttl_hours: Override TTL in hours. Uses self.ttl_hours if None.

        Returns:
            True if scrape_date + ttl_hours > now, False otherwise.
        """
        if not self.scrape_date:
            return False
        effective_ttl = ttl_hours if ttl_hours is not None else self.ttl_hours
        scrape_dt = datetime.fromisoformat(self.scrape_date)
        return datetime.now() - scrape_dt < timedelta(hours=effective_ttl)


class TopicCachePort(ABC):
    """Abstract interface for topic data caching."""

    @abstractmethod
    def read(self) -> CacheResult | None:
        """Read cached topic data.

        Returns the CacheResult, or None if no cache exists or cache is corrupt.
        """

    @abstractmethod
    def write(self, topics: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
        """Write enriched topics to cache atomically.

        Writes to .tmp, backs up existing to .bak, renames .tmp to target.
        Creates the directory if absent.

        Args:
            topics: List of enriched topic dicts.
            metadata: Dict with scrape_date, source, ttl_hours, total_topics,
                      enrichment_completeness, and optional filters_applied.
        """

    @abstractmethod
    def is_fresh(self, ttl_hours: int = 24) -> bool:
        """Check if the cached data is fresh within the TTL window.

        Returns False if no cache exists or cache is unreadable.
        """

    @abstractmethod
    def exists(self) -> bool:
        """Check whether a cache file exists."""
