"""Targeted mutation-killing tests for FinderService.

Kills surviving mutants by testing exact message content, every code path,
and precise field values in SearchResult.
"""

from __future__ import annotations

from typing import Any

from pes.domain.finder_service import FinderService, SearchResult
from tests.acceptance.solicitation_finder.conftest import make_topic
from tests.acceptance.solicitation_finder.fakes import (
    InMemoryFinderResultsAdapter,
    InMemoryTopicFetchAdapter,
)


def _topics(n: int, **kw: str) -> list[dict[str, Any]]:
    return [make_topic(topic_id=f"T-{i:03d}", topic_code=f"T-{i:03d}",
                       title=f"Topic #{i}", **kw) for i in range(1, n + 1)]


def _profile(name: str = "Test Corp", **kw: Any) -> dict[str, Any]:
    p: dict[str, Any] = {"company_name": name, "capabilities": ["testing"]}
    p.update(kw)
    return p


class TestSearchResultDefaults:
    """Kill mutants on SearchResult dataclass defaults."""

    def test_default_topics_empty(self) -> None:
        r = SearchResult()
        assert r.topics == []

    def test_default_total_zero(self) -> None:
        r = SearchResult()
        assert r.total == 0

    def test_default_source_empty_string(self) -> None:
        r = SearchResult()
        assert r.source == ""

    def test_default_partial_false(self) -> None:
        r = SearchResult()
        assert r.partial is False

    def test_default_error_none(self) -> None:
        r = SearchResult()
        assert r.error is None

    def test_default_company_name_none(self) -> None:
        r = SearchResult()
        assert r.company_name is None

    def test_default_messages_empty(self) -> None:
        r = SearchResult()
        assert r.messages == []

    def test_default_progress_reported_false(self) -> None:
        r = SearchResult()
        assert r.progress_reported is False

    def test_default_counts_zero(self) -> None:
        r = SearchResult()
        assert r.total_fetched == 0
        assert r.candidates_count == 0
        assert r.eliminated_count == 0


class TestNoProfileExactMessages:
    """Kill mutants on exact no-profile message strings."""

    def test_no_profile_returns_exactly_three_messages(self) -> None:
        svc = FinderService(topic_fetch=InMemoryTopicFetchAdapter(topics=[]), profile=None)
        result = svc.search()
        assert result.messages == [
            "No company profile found",
            "The company profile enables matching, eligibility, and personnel alignment",
            "Create a company profile first",
        ]

    def test_no_profile_returns_empty_topics(self) -> None:
        svc = FinderService(topic_fetch=InMemoryTopicFetchAdapter(topics=_topics(5)), profile=None)
        result = svc.search()
        assert result.topics == []
        assert result.total == 0
        assert result.source == ""


class TestDegradedMode:
    """Kill mutants on degraded_mode code path."""

    def test_degraded_mode_with_no_profile_returns_topics(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(10))
        svc = FinderService(topic_fetch=adapter, profile=None)
        result = svc.search(degraded_mode=True)
        assert len(result.topics) == 10
        assert result.company_name is None

    def test_degraded_mode_message_exact(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(3))
        svc = FinderService(topic_fetch=adapter, profile=None)
        result = svc.search(degraded_mode=True)
        assert "No company profile: scoring accuracy severely degraded" in result.messages


class TestUnavailableSourceExactMessages:
    """Kill mutants on source-unavailable error messages."""

    def test_unavailable_exact_messages(self) -> None:
        adapter = InMemoryTopicFetchAdapter(available=False)
        svc = FinderService(topic_fetch=adapter, profile=_profile())
        result = svc.search()
        assert "topic source unavailable" in result.messages
        assert "You can provide a solicitation document as a file instead" in result.messages
        assert any("dodsbirsttr.mil" in m for m in result.messages)

    def test_unavailable_returns_error_and_source(self) -> None:
        adapter = InMemoryTopicFetchAdapter(available=False)
        svc = FinderService(topic_fetch=adapter, profile=_profile())
        result = svc.search()
        assert result.error is not None
        assert result.source == "dsip_api"
        assert result.company_name == "Test Corp"
        assert result.filters_applied == {}


class TestRateLimitExactMessages:
    """Kill mutants on rate-limit partial results messages."""

    def test_rate_limit_exact_messages(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(200), rate_limit_after=100)
        svc = FinderService(topic_fetch=adapter, profile=_profile())
        result = svc.search()
        assert "source rate limit reached after 100 topics" in result.messages
        assert "You can score partial results or retry later" in result.messages

    def test_rate_limit_sets_partial_true(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(50), rate_limit_after=25)
        svc = FinderService(topic_fetch=adapter, profile=_profile())
        result = svc.search()
        assert result.partial is True
        assert len(result.topics) == 25


class TestBaaPdfSourceMessage:
    """Kill mutants on baa_pdf source branch."""

    def test_baa_pdf_source_message(self) -> None:
        # Create a custom adapter that returns baa_pdf source
        from pes.ports.topic_fetch_port import FetchResult, TopicFetchPort

        class BaaPdfFake(TopicFetchPort):
            def fetch(self, filters=None, on_progress=None):
                return FetchResult(
                    topics=_topics(47), total=47,
                    source="baa_pdf", partial=False, error=None,
                )

        svc = FinderService(topic_fetch=BaaPdfFake(), profile=_profile())
        result = svc.search()
        assert "Source: solicitation document (47 topics extracted)" in result.messages


class TestProgressReported:
    """Kill mutants on progress_reported flag."""

    def test_search_reports_progress(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(5))
        svc = FinderService(topic_fetch=adapter, profile=_profile())
        result = svc.search()
        # InMemoryTopicFetchAdapter calls on_progress, so progress_reported = True
        assert result.progress_reported is True

    def test_search_and_filter_sets_progress_reported(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(5))
        svc = FinderService(topic_fetch=adapter, profile=_profile())
        result = svc.search_and_filter(on_progress=lambda x: None)
        assert result.progress_reported is True

    def test_search_and_filter_no_callback_progress_false(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(5))
        svc = FinderService(topic_fetch=adapter, profile=_profile())
        result = svc.search_and_filter()
        assert result.progress_reported is False


class TestProfileCompleteness:
    """Kill mutants on _check_profile_completeness."""

    def test_missing_certifications_warns(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(1))
        profile = {"company_name": "X", "capabilities": ["test"]}
        svc = FinderService(topic_fetch=adapter, profile=profile)
        result = svc.search()
        cert_warn = [m for m in result.messages if "certifications" in m]
        assert len(cert_warn) == 1
        assert "scoring capped at EVALUATE" in cert_warn[0]

    def test_missing_past_performance_warns(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(1))
        profile = {"company_name": "X", "capabilities": ["test"]}
        svc = FinderService(topic_fetch=adapter, profile=profile)
        result = svc.search()
        pp_warn = [m for m in result.messages if "past performance" in m]
        assert len(pp_warn) == 1

    def test_missing_key_personnel_warns(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(1))
        profile = {"company_name": "X", "capabilities": ["test"]}
        svc = FinderService(topic_fetch=adapter, profile=profile)
        result = svc.search()
        kp_warn = [m for m in result.messages if "key personnel" in m]
        assert len(kp_warn) == 1

    def test_complete_profile_no_completeness_warnings(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(1))
        profile = _profile(
            certifications={"sam_gov": {"active": True}},
            past_performance=[{"agency": "AF"}],
            key_personnel=[{"name": "Dr. X"}],
        )
        svc = FinderService(topic_fetch=adapter, profile=profile)
        result = svc.search()
        section_warns = [m for m in result.messages if "Missing profile section" in m]
        assert section_warns == []

    def test_empty_list_section_warns(self) -> None:
        """Empty list counts as missing."""
        adapter = InMemoryTopicFetchAdapter(topics=_topics(1))
        profile = _profile(past_performance=[], certifications={}, key_personnel=[])
        svc = FinderService(topic_fetch=adapter, profile=profile)
        result = svc.search()
        section_warns = [m for m in result.messages if "Missing profile section" in m]
        assert len(section_warns) == 3

    def test_warning_format_per_section(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(1))
        profile = {"company_name": "X", "capabilities": ["test"]}
        svc = FinderService(topic_fetch=adapter, profile=profile)
        result = svc.search()
        for label in ["certifications", "past performance", "key personnel"]:
            expected = (
                f"Missing profile section: {label} -- "
                f"scoring capped at EVALUATE for {label} dimension"
            )
            assert expected in result.messages, f"Missing warning for {label}"


class TestSearchAndFilterFields:
    """Kill mutants on SearchResult field assignments in search_and_filter."""

    def test_returns_exact_statistics(self) -> None:
        de = [make_topic(topic_id=f"DE-{i}", topic_code=f"DE-{i}",
                         title=f"Directed Energy #{i}") for i in range(3)]
        bio = [make_topic(topic_id=f"BIO-{i}", topic_code=f"BIO-{i}",
                          title=f"Biology #{i}") for i in range(7)]
        adapter = InMemoryTopicFetchAdapter(topics=de + bio)
        svc = FinderService(
            topic_fetch=adapter,
            profile=_profile(capabilities=["directed energy"]),
        )
        result = svc.search_and_filter()
        assert result.total_fetched == 10
        assert result.candidates_count == 3
        assert result.eliminated_count == 7
        assert result.total == 10
        assert result.source == "dsip_api"
        assert result.partial is False
        assert result.error is None
        assert result.company_name == "Test Corp"

    def test_search_and_filter_source_unavailable(self) -> None:
        adapter = InMemoryTopicFetchAdapter(available=False)
        svc = FinderService(topic_fetch=adapter, profile=_profile())
        result = svc.search_and_filter()
        assert result.error is not None
        assert result.total_fetched == 0
        assert result.candidates_count == 0
        assert "topic source unavailable" in result.messages

    def test_search_and_filter_with_filters(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(5))
        svc = FinderService(topic_fetch=adapter, profile=_profile())
        result = svc.search_and_filter(filters={"agency": "Air Force"})
        assert result.filters_applied == {"agency": "Air Force"}


class TestSearchAndFilterProgressEvents:
    """Kill mutants on progress callback event content."""

    def test_progress_events_have_correct_phases_and_status(self) -> None:
        de = [make_topic(topic_id=f"DE-{i}", topic_code=f"DE-{i}",
                         title=f"Directed Energy #{i}") for i in range(3)]
        adapter = InMemoryTopicFetchAdapter(topics=de)
        svc = FinderService(
            topic_fetch=adapter,
            profile=_profile(capabilities=["directed energy"]),
        )
        events: list[dict[str, Any]] = []
        svc.search_and_filter(on_progress=lambda e: events.append(e))

        # Should have: fetch started, fetch progress from adapter, fetch complete,
        # filter started, filter complete
        fetch_started = [e for e in events if e.get("phase") == "fetch" and e.get("status") == "started"]
        fetch_complete = [e for e in events if e.get("phase") == "fetch" and e.get("status") == "complete"]
        filter_started = [e for e in events if e.get("phase") == "filter" and e.get("status") == "started"]
        filter_complete = [e for e in events if e.get("phase") == "filter" and e.get("status") == "complete"]
        assert len(fetch_started) == 1
        assert len(fetch_complete) == 1
        assert fetch_complete[0]["count"] == 3
        assert len(filter_started) == 1
        assert len(filter_complete) == 1
        assert filter_complete[0]["candidates"] == 3

    def test_no_progress_callback_does_not_error(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(2))
        svc = FinderService(topic_fetch=adapter, profile=_profile())
        result = svc.search_and_filter(on_progress=None)
        assert result.progress_reported is False


class TestPersistResults:
    """Kill mutants on persist_results."""

    def test_persist_writes_exact_data(self) -> None:
        results_port = InMemoryFinderResultsAdapter()
        svc = FinderService(
            topic_fetch=InMemoryTopicFetchAdapter(topics=[]),
            profile=_profile(),
            results_port=results_port,
        )
        data = {"results": [{"id": "T-001"}], "count": 1}
        svc.persist_results(data)
        assert results_port.read() == data

    def test_persist_without_port_error_message(self) -> None:
        import pytest
        svc = FinderService(
            topic_fetch=InMemoryTopicFetchAdapter(topics=[]),
            profile=_profile(),
        )
        with pytest.raises(ValueError, match="No results port configured"):
            svc.persist_results({"results": []})


class TestCompanyNameExtraction:
    """Kill mutants on company_name extraction logic."""

    def test_company_name_from_profile(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(1))
        svc = FinderService(topic_fetch=adapter, profile=_profile("Acme Corp"))
        result = svc.search()
        assert result.company_name == "Acme Corp"

    def test_no_profile_company_name_none(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=[])
        svc = FinderService(topic_fetch=adapter, profile=None)
        result = svc.search()
        assert result.company_name is None

    def test_profile_missing_company_name_key(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(1))
        svc = FinderService(topic_fetch=adapter, profile={"capabilities": ["test"]})
        result = svc.search()
        assert result.company_name == ""

    def test_search_and_filter_company_name(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(1))
        svc = FinderService(topic_fetch=adapter, profile=_profile("XYZ Inc"))
        result = svc.search_and_filter()
        assert result.company_name == "XYZ Inc"


class TestFiltersApplied:
    """Kill mutants on filters_applied field."""

    def test_no_filters_returns_empty_dict(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(1))
        svc = FinderService(topic_fetch=adapter, profile=_profile())
        result = svc.search()
        assert result.filters_applied == {}

    def test_filters_passed_through(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(1))
        svc = FinderService(topic_fetch=adapter, profile=_profile())
        result = svc.search(filters={"agency": "Navy"})
        assert result.filters_applied == {"agency": "Navy"}

    def test_none_filters_becomes_empty_dict(self) -> None:
        adapter = InMemoryTopicFetchAdapter(topics=_topics(1))
        svc = FinderService(topic_fetch=adapter, profile=_profile())
        result = svc.search(filters=None)
        assert result.filters_applied == {}
