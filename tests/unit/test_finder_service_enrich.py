"""Unit tests for FinderService.search_and_enrich -- enrichment orchestration.

Test Budget: 6 behaviors x 2 = 12 max unit tests.
Tests invoke through FinderService (driving port) with in-memory fakes
for TopicFetchPort, TopicEnrichmentPort, and TopicCachePort.
No mocks inside the hexagon.

Behaviors tested:
1. Fresh cache returns cached topics without re-fetching
2. Stale/missing cache triggers fetch + pre-filter + enrichment pipeline
3. Pre-filtered candidates enriched before return
4. Enriched results persisted to cache after enrichment
5. Partial enrichment failures produce usable results with completeness report
6. Backward compatibility -- existing search() and search_and_filter() unaffected
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest

from pes.domain.finder_service import FinderService, SearchResult
from tests.acceptance.dsip_topic_scraper.conftest import make_topic
from tests.acceptance.dsip_topic_scraper.fakes import (
    InMemoryTopicCacheAdapter,
    InMemoryTopicEnrichmentAdapter,
    InMemoryTopicFetchAdapter,
)


# --- Helpers ---


def _make_de_topics(count: int) -> list[dict[str, Any]]:
    """Generate directed-energy topics that match 'directed energy' keyword."""
    return [
        make_topic(
            topic_id=f"DE-{i:03d}",
            topic_code=f"DE-{i:03d}",
            title=f"Directed Energy System #{i}",
        )
        for i in range(1, count + 1)
    ]


def _make_bio_topics(count: int) -> list[dict[str, Any]]:
    """Generate non-matching biodefense topics."""
    return [
        make_topic(
            topic_id=f"BIO-{i:03d}",
            topic_code=f"BIO-{i:03d}",
            title=f"Biodefense Research #{i}",
        )
        for i in range(1, count + 1)
    ]


def _de_profile() -> dict[str, Any]:
    """Profile with directed energy capabilities."""
    return {
        "company_name": "Radiant Defense Systems, LLC",
        "capabilities": ["directed energy"],
    }


def _fresh_cache_data(topics: list[dict[str, Any]]) -> dict[str, Any]:
    """Build fresh cache data (12 hours old)."""
    return {
        "scrape_date": (datetime.now() - timedelta(hours=12)).isoformat(),
        "source": "dsip_api",
        "ttl_hours": 24,
        "total_topics": len(topics),
        "filters_applied": {},
        "enrichment_completeness": {
            "descriptions": len(topics),
            "instructions": 0,
            "qa": 0,
            "total": len(topics),
        },
        "topics": topics,
    }


def _stale_cache_data(topics: list[dict[str, Any]]) -> dict[str, Any]:
    """Build stale cache data (36 hours old)."""
    data = _fresh_cache_data(topics)
    data["scrape_date"] = (datetime.now() - timedelta(hours=36)).isoformat()
    return data


def _build_service(
    topics: list[dict[str, Any]] | None = None,
    profile: dict[str, Any] | None = None,
    enrichment_data: dict[str, dict[str, Any]] | None = None,
    failing_topics: list[str] | None = None,
    cache_data: dict[str, Any] | None = None,
    available: bool = True,
    rate_limit_after: int | None = None,
) -> tuple[FinderService, InMemoryTopicCacheAdapter]:
    """Build FinderService with in-memory fakes, return (service, cache_adapter)."""
    fetch_adapter = InMemoryTopicFetchAdapter(
        topics=topics or [],
        available=available,
        rate_limit_after=rate_limit_after,
    )
    enrichment_adapter = InMemoryTopicEnrichmentAdapter(
        enrichment_data=enrichment_data or {},
        failing_topics=failing_topics or [],
    )
    cache_adapter = InMemoryTopicCacheAdapter(data=cache_data)
    service = FinderService(
        topic_fetch=fetch_adapter,
        profile=profile or _de_profile(),
        enrichment_port=enrichment_adapter,
        cache_port=cache_adapter,
    )
    return service, cache_adapter


class TestFreshCacheReturnsWithoutFetch:
    """Behavior 1: Fresh cache returns cached topics without re-fetching."""

    def test_fresh_cache_returns_cached_topics(self) -> None:
        cached_topics = _make_de_topics(5)
        # Add enrichment fields to cached topics
        for t in cached_topics:
            t["description"] = f"Desc for {t['topic_id']}"
            t["enrichment_status"] = "ok"
        cache_data = _fresh_cache_data(cached_topics)

        service, _ = _build_service(
            topics=_make_de_topics(10),  # source has 10, but cache is fresh
            cache_data=cache_data,
        )

        result = service.search_and_enrich(ttl_hours=24)

        assert len(result.topics) == 5
        assert result.source == "dsip_api"

    def test_fresh_cache_does_not_trigger_enrichment(self) -> None:
        cached_topics = _make_de_topics(3)
        for t in cached_topics:
            t["description"] = f"Desc for {t['topic_id']}"
        cache_data = _fresh_cache_data(cached_topics)

        service, _ = _build_service(
            topics=_make_de_topics(20),  # ignored because cache is fresh
            cache_data=cache_data,
        )

        result = service.search_and_enrich(ttl_hours=24)

        # Should return cached data, not freshly fetched 20 topics
        assert len(result.topics) == 3


class TestStaleCacheTriggersPipeline:
    """Behavior 2: Stale/missing cache triggers fetch + pre-filter + enrichment."""

    def test_missing_cache_triggers_full_pipeline(self) -> None:
        de_topics = _make_de_topics(5)
        bio_topics = _make_bio_topics(10)
        all_topics = de_topics + bio_topics

        service, cache = _build_service(
            topics=all_topics,
            cache_data=None,  # no cache
        )

        result = service.search_and_enrich()

        # Only DE topics match the profile capability "directed energy"
        assert len(result.topics) == 5
        assert result.total_fetched == 15

    def test_stale_cache_triggers_fresh_fetch(self) -> None:
        stale_topics = _make_de_topics(3)
        for t in stale_topics:
            t["description"] = f"Stale desc for {t['topic_id']}"
        stale = _stale_cache_data(stale_topics)

        fresh_de = _make_de_topics(7)
        fresh_bio = _make_bio_topics(8)

        service, _ = _build_service(
            topics=fresh_de + fresh_bio,
            cache_data=stale,  # stale cache
        )

        result = service.search_and_enrich(ttl_hours=24)

        # Fresh fetch: 7 DE topics match, 8 bio eliminated
        assert len(result.topics) == 7


class TestCandidatesEnrichedBeforeReturn:
    """Behavior 3: Pre-filtered candidates enriched before return."""

    def test_enriched_topics_contain_descriptions(self) -> None:
        de_topics = _make_de_topics(3)
        bio_topics = _make_bio_topics(5)

        service, _ = _build_service(
            topics=de_topics + bio_topics,
            cache_data=None,
        )

        result = service.search_and_enrich()

        # Each returned topic should have a description from enrichment
        for topic in result.topics:
            assert "description" in topic


class TestEnrichedResultsCached:
    """Behavior 4: Enriched results persisted to cache after enrichment."""

    def test_enriched_results_written_to_cache(self) -> None:
        de_topics = _make_de_topics(4)

        service, cache = _build_service(
            topics=de_topics,
            cache_data=None,
        )

        service.search_and_enrich()

        assert cache.exists()
        assert cache.is_fresh(24)


class TestPartialEnrichmentFailures:
    """Behavior 5: Partial enrichment failures produce usable results with completeness report."""

    def test_partial_failures_return_successful_topics_with_report(self) -> None:
        de_topics = _make_de_topics(5)
        failing = ["DE-002", "DE-004"]

        service, _ = _build_service(
            topics=de_topics,
            failing_topics=failing,
            cache_data=None,
        )

        result = service.search_and_enrich()

        # 3 out of 5 succeed
        assert len(result.topics) == 3
        # Messages should contain completeness info
        assert any("3" in m and "5" in m for m in result.messages)

    def test_all_enrichments_fail_still_returns_messages(self) -> None:
        de_topics = _make_de_topics(2)
        failing = ["DE-001", "DE-002"]

        service, _ = _build_service(
            topics=de_topics,
            failing_topics=failing,
            cache_data=None,
        )

        result = service.search_and_enrich()

        assert len(result.topics) == 0
        assert len(result.messages) > 0


class TestBackwardCompatibility:
    """Behavior 6: Existing search() and search_and_filter() remain unchanged."""

    def test_search_still_works_without_enrichment_ports(self) -> None:
        topics = _make_de_topics(5)
        fetch_adapter = InMemoryTopicFetchAdapter(topics=topics)
        service = FinderService(
            topic_fetch=fetch_adapter,
            profile=_de_profile(),
        )

        result = service.search()

        assert len(result.topics) == 5
        assert result.error is None

    def test_search_and_filter_returns_correct_candidate_and_eliminated_counts(self) -> None:
        """search_and_filter without enrichment ports filters 15 topics:
        5 DE topics match capabilities, 10 bio topics eliminated."""
        de_topics = _make_de_topics(5)
        bio_topics = _make_bio_topics(10)
        fetch_adapter = InMemoryTopicFetchAdapter(topics=de_topics + bio_topics)
        service = FinderService(
            topic_fetch=fetch_adapter,
            profile=_de_profile(),
        )

        result = service.search_and_filter()

        assert result.candidates_count == 5, "5 DE topics should match 'directed energy' capability"
        assert result.eliminated_count == 10, "10 bio topics should be eliminated"
        assert result.total_fetched == 15, "All 15 topics should have been fetched"
        assert len(result.topics) == 5, "Returned topics should be the 5 candidates"
