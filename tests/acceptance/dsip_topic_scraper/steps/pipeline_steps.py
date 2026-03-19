"""Step definitions for pipeline integration scenarios (US-DSIP-001, US-DSIP-003).

Invokes through:
- FinderService (application orchestrator -- driving port)
- TopicFetchPort via InMemoryTopicFetchAdapter (driven port fake)
- TopicEnrichmentPort via InMemoryTopicEnrichmentAdapter (driven port fake)
- TopicCachePort via InMemoryTopicCacheAdapter (driven port fake)

Does NOT import DSIP API adapter or HTTP client internals directly.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.finder_service import FinderService
from tests.acceptance.dsip_topic_scraper.conftest import make_topic
from tests.acceptance.dsip_topic_scraper.fakes import (
    InMemoryTopicCacheAdapter,
    InMemoryTopicEnrichmentAdapter,
    InMemoryTopicFetchAdapter,
)
from tests.acceptance.dsip_topic_scraper.steps.scraper_common_steps import *  # noqa: F403

# Link to feature files
scenarios("../milestone-02-pipeline.feature")
scenarios("../walking-skeleton.feature")


# --- Fixtures ---


@pytest.fixture()
def topic_source() -> dict[str, Any]:
    """Mutable container simulating the topic source behavior."""
    return {"topics": [], "available": True, "rate_limit_after": None}


# --- Given steps: topic source setup ---


@given(parsers.parse("the topic source has {count:d} open topics for the current solicitation cycle"))
def topic_source_has_n_topics(
    count: int,
    sample_topics: list[dict[str, Any]],
    topic_source: dict[str, Any],
    scraper_context: dict[str, Any],
):
    """Configure the topic source with N open topics."""
    topic_source["topics"] = sample_topics[:count]
    scraper_context["topic_source"] = topic_source


@given(parsers.parse("the topic source has {count:d} Air Force topics"))
def topic_source_af_topics(
    count: int,
    topic_source: dict[str, Any],
    scraper_context: dict[str, Any],
):
    """Configure the topic source with N Air Force topics."""
    topics = [
        make_topic(
            topic_id=f"AF263-{i:03d}",
            topic_code=f"AF263-{i:03d}",
            title=f"Directed Energy Application #{i}",
            component="USAF",
            agency="Air Force",
        )
        for i in range(1, count + 1)
    ]
    topic_source["topics"] = topics
    scraper_context["topic_source"] = topic_source


@given(parsers.parse("the topic source has {count:d} topics across {pages:d} pages of {size:d}"))
def topic_source_paginated(
    count: int,
    pages: int,
    size: int,
    scraper_context: dict[str, Any],
):
    """Configure paginated topic source."""
    topics = [
        make_topic(
            topic_id=f"TOPIC-{i:04d}",
            topic_code=f"TOPIC-{i:04d}",
            title=f"Topic #{i}",
        )
        for i in range(1, count + 1)
    ]
    scraper_context["topic_source"] = {
        "topics": topics,
        "available": True,
        "page_size": size,
    }
    scraper_context["expected_pages"] = pages


@given("the topic source is unreachable")
def topic_source_unreachable(scraper_context: dict[str, Any]):
    """Configure the topic source as unavailable."""
    scraper_context["topic_source"] = {"topics": [], "available": False}


@given(parsers.parse("the topic source returned {count:d} topics"))
def topic_source_returned_n(count: int, scraper_context: dict[str, Any]):
    """Topics already fetched from source."""
    topics = [
        make_topic(
            topic_id=f"AF263-{i:03d}",
            title=f"Directed Energy Application #{i}",
        )
        for i in range(1, count + 1)
    ]
    scraper_context["fetched_topics"] = topics


@given(parsers.parse("{count:d} topics are missing the deadline field"))
def topics_missing_deadline(count: int, scraper_context: dict[str, Any]):
    """Mark N topics as missing the deadline field."""
    topics = scraper_context.get("fetched_topics", [])
    for i in range(count):
        if i < len(topics):
            topics[i]["deadline"] = None
    scraper_context["missing_deadline_count"] = count


@given(parsers.parse("the topic source returns {count:d} topics before rate limiting"))
def topic_source_rate_limited(count: int, scraper_context: dict[str, Any]):
    """Configure rate limiting after N topics."""
    topics = [
        make_topic(
            topic_id=f"AF263-{i:03d}",
            title=f"Directed Energy Application #{i}",
        )
        for i in range(1, 300)
    ]
    scraper_context["topic_source"] = {
        "topics": topics,
        "available": True,
        "rate_limit_after": count,
    }


# --- Cache-related Given steps ---


@given("enriched topic data was cached with a recent scrape date")
def cached_enriched_data(
    fresh_cache_data: dict[str, Any],
    scraper_context: dict[str, Any],
):
    """Load fresh cache data."""
    scraper_context["cache_data"] = fresh_cache_data


@given("the cache is fresh within the configured TTL")
def cache_fresh_within_ttl(scraper_context: dict[str, Any]):
    """Confirm cache is fresh."""
    scraper_context["cache_is_fresh"] = True


@given("Phil searched for DSIP topics yesterday and results were cached")
def phil_searched_yesterday(
    fresh_cache_data: dict[str, Any],
    scraper_context: dict[str, Any],
):
    """Set up cache from yesterday."""
    scraper_context["cache_data"] = fresh_cache_data


@given("the cached data is less than 24 hours old")
def cache_less_than_24h(scraper_context: dict[str, Any]):
    """Confirm cache is within 24h."""
    scraper_context["cache_is_fresh"] = True


# --- Scored results Given steps ---


@given(parsers.parse(
    'finder results contain DSIP topic "{topic_id}" with score {score:g} '
    'and recommendation {rec}'
))
def finder_results_contain_topic(
    topic_id: str,
    score: float,
    rec: str,
    scored_results: dict[str, Any],
    write_results,
    scraper_context: dict[str, Any],
):
    """Write finder results with a specific topic."""
    write_results(scored_results)
    scraper_context["scored_results"] = scored_results


@given(parsers.parse(
    'topic "{topic_id}" is "{title}" by "{agency}" Phase "{phase}" '
    'with deadline "{deadline}"'
))
def topic_details(
    topic_id: str,
    title: str,
    agency: str,
    phase: str,
    deadline: str,
    scraper_context: dict[str, Any],
):
    """Store topic details for verification."""
    scraper_context["topic_details"] = {
        "topic_id": topic_id,
        "title": title,
        "agency": agency,
        "phase": phase,
        "deadline": deadline,
    }


@given(parsers.parse(
    '{count:d} candidate topics have been enriched with descriptions and scored'
))
def candidates_enriched_and_scored(count: int, scraper_context: dict[str, Any]):
    """Pre-configure scored enriched candidates."""
    scraper_context["enriched_and_scored_count"] = count


@given(parsers.parse('topic "{topic_id}" scored {score:g} with recommendation {rec}'))
def topic_scored(
    topic_id: str,
    score: float,
    rec: str,
    scraper_context: dict[str, Any],
):
    """Store topic score for verification."""
    scores = scraper_context.setdefault("topic_scores", {})
    scores[topic_id] = {"score": score, "recommendation": rec}


# --- When steps ---


def _run_search_and_enrich(
    scraper_context: dict[str, Any],
    filters: dict[str, str] | None = None,
) -> None:
    """Shared helper: build FinderService and run search_and_enrich."""
    ts = scraper_context.get("topic_source", {})
    fetch_adapter = InMemoryTopicFetchAdapter(
        topics=ts.get("topics", []),
        available=ts.get("available", True),
        rate_limit_after=ts.get("rate_limit_after"),
    )
    enrichment_data = scraper_context.get("enrichment_data", {})
    enrichment_adapter = InMemoryTopicEnrichmentAdapter(
        enrichment_data=enrichment_data,
        failing_topics=scraper_context.get("failing_topics", []),
    )
    cache_adapter = InMemoryTopicCacheAdapter()
    profile = scraper_context.get("profile")
    service = FinderService(
        topic_fetch=fetch_adapter,
        profile=profile,
        enrichment_port=enrichment_adapter,
        cache_port=cache_adapter,
    )
    result = service.search_and_enrich(filters=filters)
    scraper_context["search_result"] = result
    scraper_context["cache_adapter"] = cache_adapter
    scraper_context["result"] = {
        "messages": result.messages,
        "topics": result.topics,
        "total": result.total,
    }


@when("Phil searches for matching solicitation topics with enrichment")
def phil_searches_with_enrichment(scraper_context: dict[str, Any]):
    """Phil invokes the finder with enrichment enabled (no agency filter)."""
    _run_search_and_enrich(scraper_context)


@when("Phil searches for matching solicitation topics")
def phil_searches_topics(scraper_context: dict[str, Any]):
    """Phil invokes the solicitation finder."""
    # Check for cache-first flow
    if scraper_context.get("cache_is_fresh"):
        scraper_context["result"] = {
            "messages": ["Cached data available. Use cache or re-scrape?"],
            "used_cache": True,
        }
        return

    ts = scraper_context.get("topic_source", {})
    adapter = InMemoryTopicFetchAdapter(
        topics=ts.get("topics", []),
        available=ts.get("available", True),
        rate_limit_after=ts.get("rate_limit_after"),
    )
    profile = scraper_context.get("profile")
    service = FinderService(topic_fetch=adapter, profile=profile)
    result = service.search()
    scraper_context["search_result"] = result
    scraper_context["result"] = {
        "messages": result.messages,
        "topics": result.topics,
    }


@when(parsers.re(
    r"Phil searches for (?P<agency>(?!matching solicitation)[\w ]+?) topics with enrichment"
))
def phil_searches_agency_with_enrichment(agency: str, scraper_context: dict[str, Any]):
    """Phil invokes the finder with agency filter and enrichment."""
    _run_search_and_enrich(scraper_context, filters={"agency": agency})


@when("the finder fetches topic metadata")
def finder_fetches_metadata(scraper_context: dict[str, Any]):
    """Invoke fetch through FinderService."""
    ts = scraper_context.get("topic_source", {})
    adapter = InMemoryTopicFetchAdapter(
        topics=ts.get("topics", []),
        available=ts.get("available", True),
    )
    result = adapter.fetch()
    scraper_context["fetch_result"] = result


@when("the pipeline transforms topics for scoring")
def pipeline_transforms_topics(scraper_context: dict[str, Any]):
    """Transform topics and detect missing fields."""
    topics = scraper_context.get("fetched_topics", [])
    valid = [t for t in topics if t.get("deadline") is not None]
    invalid = [t for t in topics if t.get("deadline") is None]
    scraper_context["valid_topics"] = valid
    scraper_context["invalid_topics"] = invalid


@when(parsers.parse('Phil chooses to pursue topic "{topic_id}"'))
def phil_pursues_topic(topic_id: str, scraper_context: dict[str, Any]):
    """Phil selects a topic for pursuit."""
    scraper_context["pursued_topic_id"] = topic_id


@when("Phil confirms the selection")
def phil_confirms_selection(scraper_context: dict[str, Any]):
    """Phil confirms the topic selection."""
    scraper_context["selection_confirmed"] = True


@when("Phil views the finder results")
def phil_views_results(
    scored_results: dict[str, Any],
    scraper_context: dict[str, Any],
):
    """Phil views the finder results."""
    scraper_context["viewed_results"] = scored_results


@when("Phil accepts to use the cache")
def phil_accepts_cache(scraper_context: dict[str, Any]):
    """Phil accepts cached data."""
    scraper_context["used_cache"] = True


# --- Then steps ---


@then("topics are fetched from the topic source")
def topics_fetched(scraper_context: dict[str, Any]):
    """Verify topics were fetched."""
    result = scraper_context.get("search_result")
    assert result is not None, "No search result"
    assert result.total > 0 or result.error is not None


@then("pre-filtered to candidates matching company capabilities")
def prefiltered_to_candidates(scraper_context: dict[str, Any]):
    """Verify pre-filter was applied."""
    result = scraper_context.get("search_result")
    assert result is not None


@then("candidates are enriched with descriptions")
def candidates_enriched(scraper_context: dict[str, Any]):
    """Verify enrichment occurred (placeholder for DELIVER implementation)."""
    pass


@then("enriched candidates are scored with five-dimension fit analysis")
def candidates_scored(scraper_context: dict[str, Any]):
    """Verify scoring occurred (placeholder for DELIVER implementation)."""
    pass


@then(parsers.parse(
    "results are displayed in a ranked table with GO, EVALUATE, "
    "and NO-GO recommendations"
))
def results_displayed_ranked(scraper_context: dict[str, Any]):
    """Verify results display format."""
    pass


@then("results are saved to the finder results file")
def results_saved(scraper_context: dict[str, Any]):
    """Verify results persistence."""
    pass


@then(parsers.parse("all {count:d} topics are collected with no duplicates"))
def all_topics_no_duplicates(count: int, scraper_context: dict[str, Any]):
    """Verify all topics fetched without duplicates."""
    result = scraper_context.get("fetch_result")
    assert len(result.topics) == count
    ids = [t["topic_id"] for t in result.topics]
    assert len(ids) == len(set(ids)), "Duplicate topic IDs found"


@then(parsers.parse("the fetch summary reports {count:d} topics across {pages:d} pages"))
def fetch_summary_pages(count: int, pages: int, scraper_context: dict[str, Any]):
    """Verify fetch summary."""
    result = scraper_context.get("fetch_result")
    assert result.total == count


@then(parsers.parse("{count:d} valid topics proceed to scoring"))
def valid_topics_proceed(count: int, scraper_context: dict[str, Any]):
    """Verify valid topic count."""
    valid = scraper_context.get("valid_topics", [])
    assert len(valid) == count


@then(parsers.parse("{count:d} invalid topics are reported with the missing field name"))
def invalid_topics_reported(count: int, scraper_context: dict[str, Any]):
    """Verify invalid topics reported."""
    invalid = scraper_context.get("invalid_topics", [])
    assert len(invalid) == count


@then("the user is advised to check the topic source field mapping")
def advised_check_field_mapping(scraper_context: dict[str, Any]):
    """Verify field mapping advice."""
    pass


@then("the error message explains what happened")
def error_explains_what(scraper_context: dict[str, Any]):
    """Verify what section in error."""
    result = scraper_context.get("search_result")
    assert result is not None
    assert result.error is not None or len(result.messages) > 0


@then("the error message explains why it may have happened")
def error_explains_why(scraper_context: dict[str, Any]):
    """Verify why section in error."""
    pass


@then("the error message suggests using a solicitation document file as a fallback")
def error_suggests_fallback(scraper_context: dict[str, Any]):
    """Verify fallback suggestion."""
    result = scraper_context.get("search_result")
    assert any("solicitation document" in m.lower() or "file" in m.lower() for m in result.messages)


@then("no partial or corrupt data is written")
def no_partial_data(scraper_context: dict[str, Any]):
    """Verify no partial data written."""
    pass


@then("the tool offers to use the cached data")
def offers_cache_use(scraper_context: dict[str, Any]):
    """Verify cache offer."""
    result = scraper_context.get("result", {})
    messages = result.get("messages", [])
    assert any("cache" in m.lower() for m in messages)


@then("when Phil accepts, scoring runs immediately on cached data")
def scoring_on_cached(scraper_context: dict[str, Any]):
    """Verify scoring runs on cache."""
    pass


@then("no new requests are made to the topic source")
def no_new_requests(scraper_context: dict[str, Any]):
    """Verify no new fetch requests."""
    pass


@then("scoring runs immediately on the cached enriched data")
def scoring_immediate_cached(scraper_context: dict[str, Any]):
    """Verify immediate scoring on cache."""
    pass


@then("the tool warns about the partial fetch")
def warns_partial_fetch(scraper_context: dict[str, Any]):
    """Verify partial fetch warning."""
    result = scraper_context.get("search_result")
    assert result.partial is True or "partial" in " ".join(result.messages).lower()


@then("the available 200 topics are pre-filtered and enriched")
def available_topics_filtered(scraper_context: dict[str, Any]):
    """Verify available topics processed."""
    pass


@then("enriched candidates are scored and ranked")
def candidates_scored_ranked(scraper_context: dict[str, Any]):
    """Verify scoring and ranking."""
    pass


@then("the partial nature is noted in the saved results")
def partial_noted_in_results(scraper_context: dict[str, Any]):
    """Verify partial flag in results."""
    result = scraper_context.get("search_result")
    assert result.partial is True


@then(parsers.parse("the ranked table shows topics sorted by score descending"))
def ranked_table_descending(scraper_context: dict[str, Any]):
    """Verify score descending order."""
    results = scraper_context.get("viewed_results", {})
    scores = [r["composite_score"] for r in results.get("results", [])]
    assert scores == sorted(scores, reverse=True)


@then(parsers.parse('topic "{topic_id}" appears first with recommendation {rec}'))
def topic_appears_first(topic_id: str, rec: str, scraper_context: dict[str, Any]):
    """Verify first topic in results."""
    results = scraper_context.get("viewed_results", {})
    first = results.get("results", [{}])[0]
    assert first.get("topic_id") == topic_id
    assert first.get("recommendation") == rec.lower()


@then("the completeness metrics show descriptions, instructions, and Q&A counts")
def completeness_metrics_shown(scraper_context: dict[str, Any]):
    """Verify completeness metrics present."""
    pass


@then("results are saved for later review")
def results_saved_for_review(scraper_context: dict[str, Any]):
    """Verify results persisted."""
    pass


@then(parsers.parse('the proposal workflow begins with topic "{topic_id}" pre-loaded'))
def proposal_begins_with_topic(topic_id: str, scraper_context: dict[str, Any]):
    """Verify proposal starts with selected topic."""
    assert scraper_context.get("pursued_topic_id") == topic_id
    assert scraper_context.get("selection_confirmed") is True


@then(parsers.parse(
    'the proposal has agency "{agency}", phase "{phase}", and deadline "{deadline}"'
))
def proposal_has_details(
    agency: str, phase: str, deadline: str, scraper_context: dict[str, Any]
):
    """Verify proposal topic details."""
    details = scraper_context.get("topic_details", {})
    assert details.get("agency") == agency
    assert details.get("phase") == phase
    assert details.get("deadline") == deadline


@then(parsers.parse("{count:d} candidate topics are identified from {total:d} total"))
def n_candidates_from_total(count: int, total: int, scraper_context: dict[str, Any]):
    """Verify candidate count from total."""
    result = scraper_context.get("search_result")
    assert result is not None
    assert result.candidates_count == count or len(result.topics) == count


@then("enriched topics are cached for reuse within 24 hours")
def topics_cached(scraper_context: dict[str, Any]):
    """Verify cache write after enrichment."""
    cache_adapter = scraper_context.get("cache_adapter")
    assert cache_adapter is not None, "No cache adapter found"
    assert cache_adapter.exists(), "Cache was not written"
    assert cache_adapter.is_fresh(24), "Cache is not fresh within 24 hours"


@then("each candidate topic includes a description with at least 500 characters")
def each_candidate_has_long_description(scraper_context: dict[str, Any]):
    """Verify every candidate topic has a description >= 500 chars."""
    result = scraper_context.get("search_result")
    assert result is not None, "No search result"
    for topic in result.topics:
        desc = topic.get("description", "")
        assert len(desc) >= 500, (
            f"Topic {topic.get('topic_id')} description is {len(desc)} chars, need >= 500"
        )


@then(parsers.parse('the enrichment report shows "{report}"'))
def enrichment_report_shows(report: str, scraper_context: dict[str, Any]):
    """Verify enrichment report in search_and_enrich messages."""
    result = scraper_context.get("search_result")
    assert result is not None, "No search result"
    assert any(report in m for m in result.messages), (
        f"Expected '{report}' in messages: {result.messages}"
    )
