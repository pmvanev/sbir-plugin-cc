"""In-memory fake adapters for DSIP topic scraper acceptance tests.

These fakes implement driven port interfaces with in-memory state,
enabling fast isolated testing without real infrastructure.

Fakes provided:
- InMemoryTopicFetchAdapter: simulates DSIP API topic fetching
- InMemoryTopicEnrichmentAdapter: simulates per-topic PDF enrichment
- InMemoryTopicCacheAdapter: simulates file-based topic cache with TTL

"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from pes.ports.topic_cache_port import CacheResult
from pes.ports.topic_enrichment_port import EnrichmentResult, TopicEnrichmentPort
from pes.ports.topic_fetch_port import FetchResult, TopicFetchPort


class InMemoryTopicFetchAdapter(TopicFetchPort):
    """In-memory fake for TopicFetchPort.

    Simulates topic source behavior including pagination, rate limiting,
    unavailability, and structural changes.
    """

    def __init__(
        self,
        topics: list[dict[str, Any]] | None = None,
        available: bool = True,
        rate_limit_after: int | None = None,
        page_size: int = 100,
        transient_error_pages: list[int] | None = None,
        structural_change: bool = False,
    ) -> None:
        self._topics = topics or []
        self._available = available
        self._rate_limit_after = rate_limit_after
        self._page_size = page_size
        self._transient_error_pages = transient_error_pages or []
        self._structural_change = structural_change
        self._retry_counts: dict[int, int] = {}

    def fetch(
        self,
        filters: dict[str, str] | None = None,
        on_progress: Any | None = None,
    ) -> FetchResult:
        """Fetch topics from in-memory store."""
        if not self._available:
            return FetchResult(
                topics=[],
                total=0,
                source="dsip_api",
                partial=False,
                error="topic source unavailable",
            )

        if self._structural_change:
            return FetchResult(
                topics=[],
                total=0,
                source="dsip_api",
                partial=False,
                error="structural_change:expected 'data' key, found 'topics'",
            )

        topics = self._topics

        # Apply filters if provided
        if filters:
            if "agency" in filters:
                topics = [t for t in topics if t.get("agency") == filters["agency"]]
            if "phase" in filters:
                topics = [t for t in topics if t.get("phase") == filters["phase"]]

        # Report progress
        if on_progress is not None:
            on_progress({"fetched": len(topics), "total": len(topics)})

        # Simulate rate limiting
        if self._rate_limit_after is not None:
            limited = topics[: self._rate_limit_after]
            return FetchResult(
                topics=limited,
                total=len(topics),
                source="dsip_api",
                partial=True,
                error=f"rate limited after {len(limited)} topics",
            )

        return FetchResult(
            topics=topics,
            total=len(topics),
            source="dsip_api",
            partial=False,
            error=None,
        )


class InMemoryTopicEnrichmentAdapter(TopicEnrichmentPort):
    """In-memory fake for TopicEnrichmentPort.

    Simulates per-topic PDF enrichment with configurable failures,
    timeouts, and content variations.
    """

    def __init__(
        self,
        enrichment_data: dict[str, dict[str, Any]] | None = None,
        failing_topics: list[str] | None = None,
        timeout_topics: list[str] | None = None,
        download_failure_topics: list[str] | None = None,
    ) -> None:
        self._enrichment_data = enrichment_data or {}
        self._failing_topics = set(failing_topics or [])
        self._timeout_topics = set(timeout_topics or [])
        self._download_failure_topics = set(download_failure_topics or [])
        self.progress_log: list[dict[str, Any]] = []

    def enrich(
        self,
        topic_ids: list[str],
        on_progress: Any | None = None,
    ) -> EnrichmentResult:
        """Enrich topics and return enrichment result."""
        enriched: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        desc_count = 0
        instr_count = 0
        qa_count = 0

        for i, topic_id in enumerate(topic_ids):
            progress = {
                "index": i + 1,
                "total": len(topic_ids),
                "topic_id": topic_id,
            }

            if topic_id in self._download_failure_topics:
                progress["status"] = "download_failed"
                errors.append({
                    "topic_id": topic_id,
                    "error": "document download failed",
                })
            elif topic_id in self._timeout_topics:
                progress["status"] = "timeout"
                errors.append({
                    "topic_id": topic_id,
                    "error": "enrichment timeout",
                })
            elif topic_id in self._failing_topics:
                progress["status"] = "extraction_failed"
                errors.append({
                    "topic_id": topic_id,
                    "error": "description extraction failed",
                })
            else:
                data = self._enrichment_data.get(topic_id, {})
                progress["status"] = "ok"
                default_desc = (
                    f"Background: This topic ({topic_id}) seeks innovative approaches "
                    f"to advance defense capabilities. Phase I will demonstrate feasibility "
                    f"of the proposed concept through modeling, simulation, and limited "
                    f"prototyping. Phase II will develop a working prototype suitable for "
                    f"field evaluation. The expected TRL entry is 3 with TRL 5 exit. "
                    f"References include prior SBIR work in related areas. Proposers "
                    f"should demonstrate relevant domain expertise and access to "
                    f"necessary test facilities. Additional detail on requirements "
                    f"and evaluation criteria is provided in the full solicitation "
                    f"document available through the DSIP portal."
                )
                enriched.append({
                    "topic_id": topic_id,
                    "description": data.get("description", default_desc),
                    "instructions": data.get("instructions"),
                    "component_instructions": data.get("component_instructions"),
                    "qa_entries": data.get("qa_entries", []),
                })
                desc_count += 1
                if data.get("instructions"):
                    instr_count += 1
                qa_count += 1 if data.get("qa_entries") else 0

            self.progress_log.append(progress)
            if on_progress is not None:
                on_progress(progress)

        return EnrichmentResult(
            enriched=enriched,
            errors=errors,
            completeness={
                "descriptions": desc_count,
                "instructions": instr_count,
                "qa": qa_count,
                "total": len(topic_ids),
            },
        )


class InMemoryTopicCacheAdapter:
    """In-memory fake for TopicCachePort.

    Simulates file-based topic cache with TTL freshness check.
    """

    def __init__(
        self,
        data: dict[str, Any] | None = None,
        corrupt: bool = False,
    ) -> None:
        self._data = data
        self._corrupt = corrupt

    def read(self) -> CacheResult | None:
        """Read cached topic data as CacheResult (matching TopicCachePort contract)."""
        if self._corrupt:
            return None
        if self._data is None:
            return None
        return CacheResult(
            topics=self._data.get("topics", []),
            scrape_date=self._data.get("scrape_date", ""),
            source=self._data.get("source", ""),
            ttl_hours=self._data.get("ttl_hours", 24),
            total_topics=self._data.get("total_topics", 0),
            enrichment_completeness=self._data.get("enrichment_completeness", {}),
            filters_applied=self._data.get("filters_applied", {}),
        )

    def write(self, topics: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
        """Write enriched topics to cache."""
        self._data = {
            **metadata,
            "topics": topics,
        }

    def is_fresh(self, ttl_hours: int = 24) -> bool:
        """Check if cache is fresh within TTL window."""
        if self._data is None or self._corrupt:
            return False
        scrape_date_str = self._data.get("scrape_date")
        if not scrape_date_str:
            return False
        scrape_date = datetime.fromisoformat(scrape_date_str)
        return datetime.now() - scrape_date < timedelta(hours=ttl_hours)

    def exists(self) -> bool:
        """Check if cache data exists."""
        return self._data is not None

    def get_filters(self) -> dict[str, Any]:
        """Get the filters used when cache was written."""
        if self._data is None:
            return {}
        return self._data.get("filters_applied", {})
