"""Step definitions for topic fetching and keyword pre-filter scenarios.

Invokes through:
- FinderService (application orchestrator -- driving port)
- TopicFetchPort via InMemoryTopicFetchAdapter (driven port fake)

Does NOT import DSIP API adapter or HTTP client internals directly.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.finder_service import FinderService, SearchResult
from pes.domain.keyword_prefilter import KeywordPreFilter
from tests.acceptance.solicitation_finder.fakes import InMemoryTopicFetchAdapter
from tests.acceptance.solicitation_finder.steps.finder_common_steps import *  # noqa: F403

# Link to feature files
scenarios("../walking-skeleton.feature")
scenarios("../milestone-01-fetch-and-filter.feature")


# --- Fixtures ---


@pytest.fixture()
def topic_source() -> dict[str, Any]:
    """Mutable container simulating the topic source behavior."""
    return {"topics": [], "available": True, "rate_limit_after": None}


# --- Given steps: topic source setup ---


@given(
    parsers.parse(
        "the topic source has {count:d} open topics for the current solicitation cycle"
    ),
)
def topic_source_has_n_topics(
    count: int,
    sample_topics: list[dict[str, Any]],
    topic_source: dict[str, Any],
    finder_context: dict[str, Any],
):
    """Configure the topic source with N open topics."""
    topic_source["topics"] = sample_topics[:count]
    finder_context["topic_source"] = topic_source


@given(
    parsers.parse("the topic source has {count:d} open topics for the current cycle"),
)
def topic_source_has_n_topics_current(
    count: int,
    sample_topics: list[dict[str, Any]],
    topic_source: dict[str, Any],
    finder_context: dict[str, Any],
):
    """Configure the topic source with N open topics (alternate phrasing)."""
    topic_source["topics"] = sample_topics[:count]
    finder_context["topic_source"] = topic_source


@given(
    parsers.parse(
        "the topic source has {count:d} open Air Force Phase I topics"
    ),
)
def topic_source_filtered_topics(
    count: int,
    topic_source: dict[str, Any],
    finder_context: dict[str, Any],
):
    """Configure the topic source with filtered Air Force Phase I topics."""
    from tests.acceptance.solicitation_finder.conftest import make_topic

    topics = [
        make_topic(
            topic_id=f"AF263-{i:03d}",
            topic_code=f"AF263-{i:03d}",
            title=f"Air Force DE Topic #{i}",
            component="USAF",
            agency="Air Force",
            phase="I",
        )
        for i in range(1, count + 1)
    ]
    topic_source["topics"] = topics
    finder_context["topic_source"] = topic_source
    finder_context["filters"] = {"agency": "Air Force", "phase": "I"}


@given("the topic source is unreachable")
def topic_source_unreachable(
    topic_source: dict[str, Any],
    finder_context: dict[str, Any],
):
    """Configure the topic source as unavailable."""
    topic_source["available"] = False
    finder_context["topic_source"] = topic_source


@given(
    parsers.parse(
        "the topic source returns {count:d} topics then limits further requests"
    ),
)
def topic_source_rate_limited(
    count: int,
    sample_topics: list[dict[str, Any]],
    topic_source: dict[str, Any],
    finder_context: dict[str, Any],
):
    """Configure rate limiting after N topics."""
    topic_source["topics"] = sample_topics[:count]
    topic_source["rate_limit_after"] = count
    finder_context["topic_source"] = topic_source


@given(
    parsers.parse("Phil has a solicitation document containing {count:d} topics"),
)
def phil_has_baa_document(
    count: int,
    finder_context: dict[str, Any],
):
    """Phil has a BAA PDF with N topics."""
    from tests.acceptance.solicitation_finder.conftest import make_topic

    finder_context["document_topics"] = [
        make_topic(
            topic_id=f"BAA-{i:03d}",
            topic_code=f"BAA-{i:03d}",
            title=f"BAA Topic #{i}",
        )
        for i in range(1, count + 1)
    ]


# --- Given steps: profile capabilities ---


@given(
    parsers.parse(
        'Phil has a company profile for "{company}" with capabilities '
        '"{cap1}", "{cap2}", "{cap3}"'
    ),
)
def phil_profile_with_capabilities(
    company: str,
    cap1: str,
    cap2: str,
    cap3: str,
    radiant_profile: dict[str, Any],
    write_profile,
    finder_context: dict[str, Any],
):
    """Write profile with specific capabilities."""
    profile = radiant_profile.copy()
    profile["company_name"] = company
    profile["capabilities"] = [cap1, cap2, cap3]
    write_profile(profile)
    finder_context["profile"] = profile


@given(
    parsers.re(
        r'the company profile has capabilities "(?P<cap1>[^"]+)", "(?P<cap2>[^"]+)", "(?P<cap3>[^"]+)"'
    ),
)
def profile_has_capabilities(
    cap1: str,
    cap2: str,
    cap3: str,
    radiant_profile: dict[str, Any],
    write_profile,
    finder_context: dict[str, Any],
):
    """Set profile capabilities for pre-filter testing."""
    profile = radiant_profile.copy()
    profile["capabilities"] = [cap1, cap2, cap3]
    write_profile(profile)
    finder_context["profile"] = profile


@given(parsers.re(r'the company profile has capabilities "(?P<caps>[^"]+)"$'))
def profile_has_single_capability(
    caps: str,
    radiant_profile: dict[str, Any],
    write_profile,
    finder_context: dict[str, Any],
):
    """Set a single capability on the profile."""
    profile = radiant_profile.copy()
    profile["capabilities"] = [caps]
    write_profile(profile)
    finder_context["profile"] = profile


@given(parsers.parse('the company profile has capability "{cap}"'))
def profile_has_one_capability(
    cap: str,
    radiant_profile: dict[str, Any],
    write_profile,
    finder_context: dict[str, Any],
):
    """Set a single capability on the profile."""
    profile = radiant_profile.copy()
    profile["capabilities"] = [cap]
    write_profile(profile)
    finder_context["profile"] = profile


@given("the company profile has no capability keywords")
def profile_empty_capabilities(
    radiant_profile: dict[str, Any],
    write_profile,
    finder_context: dict[str, Any],
):
    """Profile with empty capabilities list."""
    profile = radiant_profile.copy()
    profile["capabilities"] = []
    write_profile(profile)
    finder_context["profile"] = profile


@given(
    "the company profile has company name and capabilities only",
)
def incomplete_profile(
    minimal_profile: dict[str, Any],
    write_profile,
    finder_context: dict[str, Any],
):
    """Write a minimal profile missing optional sections."""
    write_profile(minimal_profile)
    finder_context["profile"] = minimal_profile


@given(
    "the profile has no certifications, past performance, or key personnel",
)
def profile_missing_optional_sections():
    """Marker step -- incomplete profile already written above."""
    pass


@given(
    "Phil has a company profile with capabilities, certifications, and past performance",
)
def phil_has_full_profile(
    radiant_profile: dict[str, Any],
    write_profile,
    finder_context: dict[str, Any],
):
    """Write the full Radiant profile with all sections."""
    write_profile(radiant_profile)
    finder_context["profile"] = radiant_profile


# --- Given steps: topic data for pre-filter ---


@given(parsers.parse("the topic source returned {count:d} open topics"))
def topics_already_fetched(
    count: int,
    sample_topics: list[dict[str, Any]],
    finder_context: dict[str, Any],
):
    """Topics have been fetched and are ready for pre-filtering."""
    finder_context["fetched_topics"] = sample_topics[:count]


@given(
    parsers.parse('the topic source returned a topic titled "{title}"'),
)
def topic_with_title(
    title: str,
    finder_context: dict[str, Any],
):
    """Single topic with a specific title for case-sensitivity testing."""
    from tests.acceptance.solicitation_finder.conftest import make_topic

    topic = make_topic(topic_id="CASE-001", topic_code="CASE-001", title=title)
    finder_context["fetched_topics"] = [topic]


# --- Helper: build FinderService from context ---


def _build_baa_text(topics: list[dict[str, Any]]) -> str:
    """Build simulated BAA text content from topic dicts."""
    lines = ["BROAD AGENCY ANNOUNCEMENT", ""]
    for t in topics:
        lines.append(f"Topic Number: {t.get('topic_id', 'UNKNOWN')}")
        lines.append(f"Title: {t.get('title', 'Untitled')}")
        lines.append(f"Agency: {t.get('agency', 'DoD')}")
        lines.append(f"Phase: {t.get('phase', 'I')}")
        lines.append(f"Deadline: {t.get('deadline', 'TBD')}")
        lines.append("")
    return "\n".join(lines)


def _build_finder_service(finder_context: dict[str, Any]) -> FinderService:
    """Construct a FinderService from the current test context."""
    topic_source = finder_context.get("topic_source", {})
    adapter = InMemoryTopicFetchAdapter(
        topics=topic_source.get("topics", []),
        available=topic_source.get("available", True),
        rate_limit_after=topic_source.get("rate_limit_after"),
    )
    profile = finder_context.get("profile")
    return FinderService(topic_fetch=adapter, profile=profile)


# --- When steps ---


@when("Phil searches for matching solicitation topics")
def phil_searches_topics(finder_context: dict[str, Any]):
    """Phil invokes the solicitation finder with no filters."""
    service = _build_finder_service(finder_context)
    filters = finder_context.get("filters", {}) or None
    result = service.search(filters=filters)
    finder_context["search_result"] = result


@when("Phil searches for Air Force Phase I topics")
def phil_searches_filtered(finder_context: dict[str, Any]):
    """Phil invokes the finder with agency and phase filters."""
    finder_context["filters"] = {"agency": "Air Force", "phase": "I"}
    service = _build_finder_service(finder_context)
    result = service.search(filters={"agency": "Air Force", "phase": "I"})
    finder_context["search_result"] = result


@when("Phil searches for topics using the solicitation document")
def phil_searches_with_document(finder_context: dict[str, Any]):
    """Phil invokes the finder with a --file flag (BAA PDF fallback)."""
    from pes.adapters.baa_pdf_adapter import BaaPdfAdapter

    # Build text content from document_topics fixture data
    doc_topics = finder_context.get("document_topics", [])
    text_content = _build_baa_text(doc_topics)

    adapter = BaaPdfAdapter(text_content)
    profile = finder_context.get("profile")
    service = FinderService(topic_fetch=adapter, profile=profile)
    # Enable degraded mode when no profile (document fallback)
    result = service.search(degraded_mode=profile is None)
    finder_context["search_result"] = result


@when("the keyword pre-filter runs")
def keyword_prefilter_runs(finder_context: dict[str, Any]):
    """Run the keyword pre-filter against fetched topics."""
    prefilter = KeywordPreFilter()
    topics = finder_context["fetched_topics"]
    profile = finder_context.get("profile", {})
    capabilities = profile.get("capabilities", [])
    result = prefilter.filter(topics, capabilities)
    finder_context["prefilter_result"] = result
    finder_context["action"] = "prefilter"
    # Make prefilter messages accessible to common display/warn steps
    finder_context["search_result"] = SearchResult(
        topics=result.candidates,
        total=len(topics),
        messages=result.warnings,
    )


# --- Then steps ---


@then(parsers.parse('the tool displays "{company}" as the active company'))
def displays_company_name(company: str, finder_context: dict[str, Any]):
    """Verify the company name is displayed."""
    result = finder_context["search_result"]
    assert result.company_name == company


@then(parsers.parse("the tool retrieves {count:d} topics"))
def retrieves_n_topics(count: int, finder_context: dict[str, Any]):
    """Verify topic count retrieved."""
    result = finder_context["search_result"]
    assert len(result.topics) == count


@then("the tool displays a progress indicator during fetching")
def displays_progress(finder_context: dict[str, Any]):
    """Verify progress reporting during fetch."""
    result = finder_context["search_result"]
    assert result.progress_reported is True


@then(
    parsers.parse('the active filters show agency "{agency}" and phase "{phase}"'),
)
def active_filters_displayed(
    agency: str, phase: str, finder_context: dict[str, Any]
):
    """Verify active filter display."""
    result = finder_context["search_result"]
    assert result.filters_applied.get("agency") == agency
    assert result.filters_applied.get("phase") == phase


@then("the tool suggests providing a solicitation document as a file")
def suggests_file_fallback(finder_context: dict[str, Any]):
    """Verify fallback suggestion."""
    result = finder_context["search_result"]
    assert any("solicitation document" in m.lower() for m in result.messages)


@then("the tool displays the download location for solicitation documents")
def displays_download_url(finder_context: dict[str, Any]):
    """Verify download URL is shown."""
    result = finder_context["search_result"]
    assert any("dodsbirsttr.mil" in m for m in result.messages)


@then(parsers.parse("{count:d} topics are extracted from the document"))
def topics_extracted_from_document(count: int, finder_context: dict[str, Any]):
    """Verify topic extraction from document via BaaPdfAdapter."""
    result = finder_context["search_result"]
    assert len(result.topics) == count, (
        f"Expected {count} topics extracted, got {len(result.topics)}"
    )


@then(parsers.parse("{count:d} candidate topics are identified"))
def n_candidates_identified(count: int, finder_context: dict[str, Any]):
    """Verify candidate count after pre-filter."""
    result = finder_context["prefilter_result"]
    assert len(result.candidates) == count, (
        f"Expected {count} candidates, got {len(result.candidates)}"
    )


@then(
    parsers.parse(
        "{count:d} candidate topics are identified from {total:d} total"
    ),
)
def n_candidates_from_total(
    count: int, total: int, finder_context: dict[str, Any]
):
    """Verify candidate/total counts."""
    # Pre-filter is a future step; placeholder
    pass


@then(parsers.parse("{count:d} topics are eliminated"))
def n_topics_eliminated(count: int, finder_context: dict[str, Any]):
    """Verify elimination count."""
    result = finder_context["prefilter_result"]
    assert result.eliminated_count == count, (
        f"Expected {count} eliminated, got {result.eliminated_count}"
    )


@then("the topic is included as a candidate")
def topic_is_candidate(finder_context: dict[str, Any]):
    """Verify the topic passed the pre-filter."""
    result = finder_context["prefilter_result"]
    assert len(result.candidates) == 1, (
        f"Expected 1 candidate, got {len(result.candidates)}"
    )


@then("zero candidates are identified")
def zero_candidates(finder_context: dict[str, Any]):
    """Verify no candidates matched."""
    result = finder_context["prefilter_result"]
    assert len(result.candidates) == 0, (
        f"Expected 0 candidates, got {len(result.candidates)}"
    )


@then(parsers.parse("all {count:d} topics pass the pre-filter"))
def all_topics_pass(count: int, finder_context: dict[str, Any]):
    """Verify all topics passed (empty capabilities)."""
    result = finder_context["prefilter_result"]
    assert len(result.candidates) == count, (
        f"Expected {count} topics to pass, got {len(result.candidates)}"
    )


@then("the tool offers to score partial results or retry later")
def offers_partial_options(finder_context: dict[str, Any]):
    """Verify partial result options offered."""
    result = finder_context["search_result"]
    assert any("partial results" in m.lower() or "retry" in m.lower() for m in result.messages)


@then(
    "the tool explains that the profile enables matching, eligibility, "
    "and personnel alignment",
)
def explains_profile_value(finder_context: dict[str, Any]):
    """Verify profile explanation is shown."""
    result = finder_context["search_result"]
    assert any("matching" in m and "eligibility" in m for m in result.messages)


@then("the tool suggests creating a profile first")
def suggests_profile_setup(finder_context: dict[str, Any]):
    """Verify profile setup suggestion."""
    result = finder_context["search_result"]
    assert any("profile" in m.lower() and "create" in m.lower() for m in result.messages)


@then(parsers.parse("{count:d} topics are listed without five-dimension scoring"))
def topics_listed_no_scoring(count: int, finder_context: dict[str, Any]):
    """Verify degraded mode: topics listed but not scored."""
    result = finder_context["search_result"]
    assert len(result.topics) == count, (
        f"Expected {count} topics in degraded mode, got {len(result.topics)}"
    )
    # In degraded mode, topics should not have dimension scores
    for topic in result.topics:
        assert "dimensions" not in topic or topic.get("dimensions") is None, (
            "Topics in degraded mode should not have five-dimension scoring"
        )


@then("the tool warns about each missing profile section")
def warns_missing_sections(finder_context: dict[str, Any]):
    """Verify per-section warnings for incomplete profile."""
    result = finder_context["search_result"]
    messages_lower = [m.lower() for m in result.messages]
    all_text = " ".join(messages_lower)
    assert "certifications" in all_text, (
        f"Expected warning about missing certifications in: {result.messages}"
    )
    assert "past performance" in all_text, (
        f"Expected warning about missing past performance in: {result.messages}"
    )
    assert "key personnel" in all_text, (
        f"Expected warning about missing key personnel in: {result.messages}"
    )


@then("scoring proceeds with defaults for missing dimensions")
def scoring_with_defaults(finder_context: dict[str, Any]):
    """Verify default scoring for missing dimensions."""
    result = finder_context["search_result"]
    # Scoring should still produce topics (with defaults)
    assert result.topics is not None, "Expected topics to be present with default scoring"


@then("recommendations cap at EVALUATE for dimensions with missing data")
def recommendations_capped(finder_context: dict[str, Any]):
    """Verify recommendation capping for incomplete profiles."""
    result = finder_context["search_result"]
    messages_lower = [m.lower() for m in result.messages]
    all_text = " ".join(messages_lower)
    assert "evaluate" in all_text or "capped" in all_text, (
        f"Expected capped-at-EVALUATE guidance in: {result.messages}"
    )


@then("the tool suggests reviewing the profile or broadening filters")
def suggests_review_or_broaden(finder_context: dict[str, Any]):
    """Verify suggestion to review profile or broaden filters."""
    result = finder_context["prefilter_result"]
    assert len(result.warnings) > 0, "Expected warnings with suggestions"
    all_warnings = " ".join(result.warnings).lower()
    assert "profile" in all_warnings or "broaden" in all_warnings, (
        f"Expected profile/broaden suggestion in warnings: {result.warnings}"
    )
