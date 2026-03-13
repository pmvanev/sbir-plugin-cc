"""Unit tests for FinderService -- driving port for topic discovery.

Test Budget: 8 behaviors x 2 = 16 max unit tests.
Tests invoke through FinderService (driving port) with InMemoryTopicFetchAdapter
(fake driven port). No mocks inside the hexagon.

Behaviors tested:
1. Fetch all topics (happy path)
2. Fetch with agency/phase filters
3. API unavailable returns error context with guidance
4. Partial results from rate limiting
5. Missing profile returns guidance messages
6. Search-and-filter orchestration returns candidates with statistics
7. Persist scored results via FinderResultsPort
8. Progress callback reports fetch and filter phases
"""

from __future__ import annotations

from typing import Any

from pes.domain.finder_service import FinderService
from tests.acceptance.solicitation_finder.conftest import make_topic
from tests.acceptance.solicitation_finder.fakes import (
    InMemoryFinderResultsAdapter,
    InMemoryTopicFetchAdapter,
)


def _make_topics(count: int, **overrides: str) -> list[dict[str, Any]]:
    """Generate N test topics with optional field overrides."""
    return [
        make_topic(
            topic_id=f"T-{i:03d}",
            topic_code=f"T-{i:03d}",
            title=f"Topic #{i}",
            **overrides,
        )
        for i in range(1, count + 1)
    ]


def _make_profile(company_name: str = "Test Corp") -> dict[str, Any]:
    """Create a minimal company profile."""
    return {"company_name": company_name, "capabilities": ["testing"]}


class TestFinderServiceFetch:
    """Behavior 1: Fetch all topics and return correct count."""

    def test_fetches_all_topics_with_correct_count(self) -> None:
        topics = _make_topics(50)
        adapter = InMemoryTopicFetchAdapter(topics=topics)
        service = FinderService(topic_fetch=adapter, profile=_make_profile())

        result = service.search()

        assert len(result.topics) == 50
        assert result.total == 50
        assert result.source == "dsip_api"
        assert result.partial is False
        assert result.error is None

    def test_reports_company_name_from_profile(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_make_topics(5))
        service = FinderService(
            topic_fetch=adapter,
            profile=_make_profile("Radiant Defense Systems, LLC"),
        )

        result = service.search()

        assert result.company_name == "Radiant Defense Systems, LLC"


class TestFinderServiceFilters:
    """Behavior 2: Fetch with configurable filters."""

    def test_filters_by_agency_and_phase(self) -> None:
        af_topics = _make_topics(10, agency="Air Force", phase="I")
        navy_topics = _make_topics(5, agency="Navy", phase="II")
        all_topics = af_topics + navy_topics
        adapter = InMemoryTopicFetchAdapter(topics=all_topics)
        service = FinderService(topic_fetch=adapter, profile=_make_profile())

        result = service.search(filters={"agency": "Air Force", "phase": "I"})

        assert len(result.topics) == 10
        assert result.filters_applied == {"agency": "Air Force", "phase": "I"}


class TestFinderServiceUnavailable:
    """Behavior 3: API unavailable returns error with guidance."""

    def test_unavailable_source_returns_error_with_messages(self) -> None:
        adapter = InMemoryTopicFetchAdapter(available=False)
        service = FinderService(topic_fetch=adapter, profile=_make_profile())

        result = service.search()

        assert result.error is not None
        assert len(result.topics) == 0
        assert any("unavailable" in m.lower() for m in result.messages)
        assert any("solicitation document" in m.lower() for m in result.messages)
        assert any("dodsbirsttr.mil" in m for m in result.messages)


class TestFinderServicePartialResults:
    """Behavior 4: Rate limiting returns partial results."""

    def test_rate_limited_returns_partial_with_message(self) -> None:
        topics = _make_topics(200)
        adapter = InMemoryTopicFetchAdapter(topics=topics, rate_limit_after=100)
        service = FinderService(topic_fetch=adapter, profile=_make_profile())

        result = service.search()

        assert len(result.topics) == 100
        assert result.partial is True
        assert any("rate limit" in m.lower() for m in result.messages)
        assert any("retry" in m.lower() for m in result.messages)


class TestFinderServiceNoProfile:
    """Behavior 5: Missing profile returns guidance."""

    def test_no_profile_returns_guidance_messages(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_make_topics(10))
        service = FinderService(topic_fetch=adapter, profile=None)

        result = service.search()

        assert len(result.topics) == 0
        assert any("no company profile" in m.lower() for m in result.messages)
        assert any("create" in m.lower() for m in result.messages)

    def test_no_profile_does_not_call_topic_source(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_make_topics(10))
        service = FinderService(topic_fetch=adapter, profile=None)

        result = service.search()

        # No topics returned, source was not called
        assert result.source == ""
        assert result.total == 0


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


class TestFinderServiceSearchAndFilter:
    """Behavior 6: Search-and-filter orchestration returns candidates with statistics."""

    def test_search_and_filter_returns_candidates_with_statistics(self) -> None:
        topics = _make_de_topics(10) + _make_bio_topics(40)
        adapter = InMemoryTopicFetchAdapter(topics=topics)
        profile = {
            "company_name": "Test Corp",
            "capabilities": ["directed energy"],
        }
        service = FinderService(topic_fetch=adapter, profile=profile)

        result = service.search_and_filter()

        assert result.total_fetched == 50
        assert result.candidates_count == 10
        assert result.eliminated_count == 40
        assert len(result.topics) == 10

    def test_search_and_filter_includes_prefilter_messages(self) -> None:
        topics = _make_de_topics(5) + _make_bio_topics(15)
        adapter = InMemoryTopicFetchAdapter(topics=topics)
        profile = {
            "company_name": "Test Corp",
            "capabilities": ["directed energy"],
        }
        service = FinderService(topic_fetch=adapter, profile=profile)

        result = service.search_and_filter()

        assert any("keyword match" in m.lower() for m in result.messages)
        assert any("5 candidate" in m.lower() for m in result.messages)


class TestFinderServicePersistResults:
    """Behavior 7: Persist scored results via FinderResultsPort."""

    def test_persist_results_writes_to_results_port(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=[])
        results_port = InMemoryFinderResultsAdapter()
        profile = _make_profile()
        service = FinderService(
            topic_fetch=adapter,
            profile=profile,
            results_port=results_port,
        )
        scored_data = {
            "results": [{"topic_id": "T-001", "score": 0.85}],
            "topics_scored": 1,
        }

        service.persist_results(scored_data)

        stored = results_port.read()
        assert stored is not None
        assert stored["topics_scored"] == 1

    def test_persist_results_without_port_raises(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=[])
        service = FinderService(topic_fetch=adapter, profile=_make_profile())

        import pytest

        with pytest.raises(ValueError, match="results port"):
            service.persist_results({"results": []})


class TestFinderServiceProgress:
    """Behavior 8: Progress callback reports fetch and filter phases."""

    def test_progress_callback_receives_fetch_and_filter_events(self) -> None:
        topics = _make_de_topics(5) + _make_bio_topics(10)
        adapter = InMemoryTopicFetchAdapter(topics=topics)
        profile = {
            "company_name": "Test Corp",
            "capabilities": ["directed energy"],
        }
        service = FinderService(topic_fetch=adapter, profile=profile)
        progress_events: list[dict[str, Any]] = []

        result = service.search_and_filter(
            on_progress=lambda info: progress_events.append(info),
        )

        phases_reported = [e.get("phase") for e in progress_events]
        assert "fetch" in phases_reported
        assert "filter" in phases_reported
