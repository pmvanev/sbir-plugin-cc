"""Unit tests for FinderService -- driving port for topic discovery.

Test Budget: 5 behaviors x 2 = 10 max unit tests.
Tests invoke through FinderService (driving port) with InMemoryTopicFetchAdapter
(fake driven port). No mocks inside the hexagon.

Behaviors tested:
1. Fetch all topics (happy path)
2. Fetch with agency/phase filters
3. API unavailable returns error context with guidance
4. Partial results from rate limiting
5. Missing profile returns guidance messages
"""

from __future__ import annotations

from typing import Any

from pes.domain.finder_service import FinderService
from tests.acceptance.solicitation_finder.conftest import make_topic
from tests.acceptance.solicitation_finder.fakes import InMemoryTopicFetchAdapter


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
