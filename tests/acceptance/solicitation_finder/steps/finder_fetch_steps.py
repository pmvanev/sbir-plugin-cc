"""Step definitions for topic fetching and keyword pre-filter scenarios.

Invokes through:
- TopicFetchPort (driven port -- topic source abstraction)
- KeywordPreFilter (pure domain logic -- no I/O)
- FinderService (application orchestrator)

Does NOT import DSIP API adapter or HTTP client internals directly.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

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
    parsers.parse(
        'the company profile has capabilities "{cap1}", "{cap2}", "{cap3}"'
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


@given(parsers.parse('the company profile has capabilities "{caps}"'))
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


# --- When steps ---


@when("Phil searches for matching solicitation topics")
def phil_searches_topics(finder_context: dict[str, Any]):
    """Phil invokes the solicitation finder with no filters.

    TODO: Wire to FinderService.search() through the driving port
    once production code is implemented.
    """
    finder_context["action"] = "search"
    finder_context["filters"] = finder_context.get("filters", {})


@when("Phil searches for Air Force Phase I topics")
def phil_searches_filtered(finder_context: dict[str, Any]):
    """Phil invokes the finder with agency and phase filters."""
    finder_context["action"] = "search"
    finder_context["filters"] = {"agency": "Air Force", "phase": "I"}


@when("Phil searches for topics using the solicitation document")
def phil_searches_with_document(finder_context: dict[str, Any]):
    """Phil invokes the finder with a --file flag."""
    finder_context["action"] = "search_document"


@when("the keyword pre-filter runs")
def keyword_prefilter_runs(finder_context: dict[str, Any]):
    """Run the keyword pre-filter against fetched topics.

    TODO: Wire to KeywordPreFilter.filter() once production code
    is implemented.
    """
    finder_context["action"] = "prefilter"


# --- Then steps ---


@then(parsers.parse('the tool displays "{company}" as the active company'))
def displays_company_name(company: str, finder_context: dict[str, Any]):
    """Verify the company name is displayed."""
    # TODO: Assert against FinderService output
    pass


@then(parsers.parse("the tool retrieves {count:d} topics"))
def retrieves_n_topics(count: int, finder_context: dict[str, Any]):
    """Verify topic count retrieved."""
    # TODO: Assert against FinderService.search() result
    pass


@then("the tool displays a progress indicator during fetching")
def displays_progress(finder_context: dict[str, Any]):
    """Verify progress reporting during fetch."""
    # TODO: Assert progress callback invoked
    pass


@then(
    parsers.parse('the active filters show agency "{agency}" and phase "{phase}"'),
)
def active_filters_displayed(
    agency: str, phase: str, finder_context: dict[str, Any]
):
    """Verify active filter display."""
    # TODO: Assert against FinderService output
    pass


@then("the tool suggests providing a solicitation document as a file")
def suggests_file_fallback(finder_context: dict[str, Any]):
    """Verify fallback suggestion."""
    # TODO: Assert against error output
    pass


@then("the tool displays the download location for solicitation documents")
def displays_download_url(finder_context: dict[str, Any]):
    """Verify download URL is shown."""
    # TODO: Assert against error output
    pass


@then(parsers.parse("{count:d} topics are extracted from the document"))
def topics_extracted_from_document(count: int, finder_context: dict[str, Any]):
    """Verify topic extraction from document."""
    # TODO: Assert against BaaPdfAdapter result
    pass


@then(parsers.parse("{count:d} candidate topics are identified"))
def n_candidates_identified(count: int, finder_context: dict[str, Any]):
    """Verify candidate count after pre-filter."""
    # TODO: Assert against KeywordPreFilter result
    pass


@then(
    parsers.parse(
        "{count:d} candidate topics are identified from {total:d} total"
    ),
)
def n_candidates_from_total(
    count: int, total: int, finder_context: dict[str, Any]
):
    """Verify candidate/total counts."""
    # TODO: Assert against FinderService statistics
    pass


@then(parsers.parse("{count:d} topics are eliminated"))
def n_topics_eliminated(count: int, finder_context: dict[str, Any]):
    """Verify elimination count."""
    # TODO: Assert against KeywordPreFilter statistics
    pass


@then("the topic is included as a candidate")
def topic_is_candidate(finder_context: dict[str, Any]):
    """Verify the topic passed the pre-filter."""
    # TODO: Assert topic in candidate list
    pass


@then("zero candidates are identified")
def zero_candidates(finder_context: dict[str, Any]):
    """Verify no candidates matched."""
    # TODO: Assert empty candidate list
    pass


@then(parsers.parse("all {count:d} topics pass the pre-filter"))
def all_topics_pass(count: int, finder_context: dict[str, Any]):
    """Verify all topics passed (empty capabilities)."""
    # TODO: Assert candidate count equals input count
    pass


@then("the tool offers to score partial results or retry later")
def offers_partial_options(finder_context: dict[str, Any]):
    """Verify partial result options offered."""
    # TODO: Assert against error output options
    pass


@then(
    "the tool explains that the profile enables matching, eligibility, "
    "and personnel alignment",
)
def explains_profile_value(finder_context: dict[str, Any]):
    """Verify profile explanation is shown."""
    # TODO: Assert against error output
    pass


@then("the tool suggests creating a profile first")
def suggests_profile_setup(finder_context: dict[str, Any]):
    """Verify profile setup suggestion."""
    # TODO: Assert suggestion message
    pass


@then(parsers.parse("{count:d} topics are listed without five-dimension scoring"))
def topics_listed_no_scoring(count: int, finder_context: dict[str, Any]):
    """Verify degraded mode: topics listed but not scored."""
    # TODO: Assert topic list without scores
    pass


@then("the tool warns about each missing profile section")
def warns_missing_sections(finder_context: dict[str, Any]):
    """Verify per-section warnings."""
    # TODO: Assert warnings for missing sections
    pass


@then("scoring proceeds with defaults for missing dimensions")
def scoring_with_defaults(finder_context: dict[str, Any]):
    """Verify default scoring for missing dimensions."""
    # TODO: Assert default scores applied
    pass


@then("recommendations cap at EVALUATE for dimensions with missing data")
def recommendations_capped(finder_context: dict[str, Any]):
    """Verify recommendation capping."""
    # TODO: Assert EVALUATE cap
    pass


@then("the tool suggests reviewing the profile or broadening filters")
def suggests_review_or_broaden(finder_context: dict[str, Any]):
    """Verify suggestion to review profile or broaden filters."""
    # TODO: Assert against output
    pass
