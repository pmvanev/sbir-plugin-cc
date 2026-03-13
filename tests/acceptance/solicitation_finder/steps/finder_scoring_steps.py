"""Step definitions for topic scoring and ranking scenarios.

Invokes through:
- TopicScoringService (application service -- five-dimension scoring)
- FinderService (orchestrator)

Does NOT import internal scoring logic or LLM client directly.
Scoring is delegated to domain services through driving ports.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.solicitation_finder.steps.finder_common_steps import *  # noqa: F403

# Link to feature files
scenarios("../milestone-01-scoring.feature")


# --- Given steps: scoring setup ---


@given(
    parsers.parse("{count:d} candidate topics have full descriptions"),
)
def candidates_with_descriptions(count: int, finder_context: dict[str, Any]):
    """Candidates enriched with full topic descriptions."""
    finder_context["candidate_count"] = count


@given(
    parsers.parse(
        "the company profile has capabilities, certifications with SAM active "
        "and Secret clearance, {count:d} employees, and Air Force Phase I past "
        "performance in directed energy"
    ),
)
def full_profile_for_scoring(
    count: int,
    radiant_profile: dict[str, Any],
    write_profile,
    finder_context: dict[str, Any],
):
    """Write full profile matching the scoring scenario."""
    profile = radiant_profile.copy()
    profile["employee_count"] = count
    write_profile(profile)
    finder_context["profile"] = profile


@given(parsers.parse('topic "{topic_id}" has been scored'))
def topic_has_been_scored(
    topic_id: str,
    scored_results: dict[str, Any],
    finder_context: dict[str, Any],
):
    """A specific topic has already been scored."""
    for result in scored_results["results"]:
        if result["topic_id"] == topic_id:
            finder_context["scored_topic"] = result
            break
    finder_context["scored_results"] = scored_results


@given(parsers.parse('topic "{topic_id}" requires TS clearance'))
def topic_requires_ts(
    topic_id: str,
    ts_clearance_topic: dict[str, Any],
    finder_context: dict[str, Any],
):
    """Topic has TS clearance requirement."""
    finder_context["current_topic"] = ts_clearance_topic


@given(parsers.parse('the company profile has security clearance "{clearance}"'))
def profile_has_clearance(
    clearance: str,
    radiant_profile: dict[str, Any],
    write_profile,
    finder_context: dict[str, Any],
):
    """Set specific security clearance on profile."""
    profile = radiant_profile.copy()
    profile["certifications"]["security_clearance"] = clearance
    write_profile(profile)
    finder_context["profile"] = profile


@given(parsers.parse('topic "{topic_id}" is an STTR solicitation'))
def topic_is_sttr(
    topic_id: str,
    sttr_topic: dict[str, Any],
    finder_context: dict[str, Any],
):
    """Topic is an STTR program."""
    finder_context["current_topic"] = sttr_topic


@given("the company profile has no research institution partners")
def profile_no_partners(
    profile_no_partners: dict[str, Any],
    write_profile,
    finder_context: dict[str, Any],
):
    """Profile with empty research institution partners."""
    write_profile(profile_no_partners)
    finder_context["profile"] = profile_no_partners


@given("the company profile has no past performance entries")
def profile_no_past_performance(
    profile_no_past_performance: dict[str, Any],
    write_profile,
    finder_context: dict[str, Any],
):
    """Profile with empty past performance."""
    write_profile(profile_no_past_performance)
    finder_context["profile"] = profile_no_past_performance


@given(parsers.parse('topic "{topic_id}" has composite score {score:g}'))
def topic_with_composite(
    topic_id: str, score: float, finder_context: dict[str, Any]
):
    """Set up a topic with a specific composite score."""
    finder_context.setdefault("score_topics", {})[topic_id] = score


@given("any valid combination of topics and company profile gaps")
def any_valid_combination(finder_context: dict[str, Any]):
    """Property test setup: any valid input combination."""
    finder_context["property_test"] = "score_non_negative"


@given("any valid set of dimension scores")
def any_valid_dimensions(finder_context: dict[str, Any]):
    """Property test setup: any valid dimension scores."""
    finder_context["property_test"] = "score_max_one"


# --- When steps ---


@when("the topics are scored")
def topics_scored(finder_context: dict[str, Any]):
    """Score all candidate topics.

    TODO: Wire to scoring service through driving port.
    """
    finder_context["action"] = "score"


@when("the dimension breakdown is retrieved")
def retrieve_breakdown(finder_context: dict[str, Any]):
    """Retrieve dimension breakdown for a scored topic.

    TODO: Wire to FinderResultsPort.read() for topic detail.
    """
    finder_context["action"] = "breakdown"


@when("the topic is scored")
def single_topic_scored(finder_context: dict[str, Any]):
    """Score a single topic.

    TODO: Wire to scoring service for single topic.
    """
    finder_context["action"] = "score_single"


@when("scoring runs")
def scoring_runs(finder_context: dict[str, Any]):
    """Run scoring with current profile/topic configuration.

    TODO: Wire to scoring service.
    """
    finder_context["action"] = "score_all"


@when("recommendations are applied")
def recommendations_applied(finder_context: dict[str, Any]):
    """Apply recommendation thresholds to scored topics.

    TODO: Wire to recommendation logic.
    """
    finder_context["action"] = "recommend"


@when("the composite score is calculated")
def composite_calculated(finder_context: dict[str, Any]):
    """Calculate composite score (property test).

    TODO: Wire to composite score calculation.
    """
    finder_context["action"] = "composite"


# --- Then steps ---


@then(
    parsers.parse(
        'topic "{topic_id}" scores composite {score:g} with recommendation {rec}'
    ),
)
def topic_scores_composite(
    topic_id: str, score: float, rec: str, finder_context: dict[str, Any]
):
    """Verify topic composite score and recommendation."""
    # TODO: Assert against scoring service output
    pass


@then("topics are ranked by composite score descending")
def topics_ranked_descending(finder_context: dict[str, Any]):
    """Verify descending sort order."""
    # TODO: Assert rank ordering
    pass


@then(parsers.parse("the subject matter expertise score is {score:g}"))
def sme_score(score: float, finder_context: dict[str, Any]):
    """Verify SME dimension score."""
    # TODO: Assert dimension score
    pass


@then(parsers.parse("the past performance score is {score:g}"))
def pp_score(score: float, finder_context: dict[str, Any]):
    """Verify past performance dimension score."""
    # TODO: Assert dimension score
    pass


@then(parsers.parse("the certifications score is {score:g}"))
def cert_score(score: float, finder_context: dict[str, Any]):
    """Verify certifications dimension score."""
    # TODO: Assert dimension score
    pass


@then(parsers.parse("the eligibility score is {score:g}"))
def elig_score(score: float, finder_context: dict[str, Any]):
    """Verify eligibility dimension score."""
    # TODO: Assert dimension score
    pass


@then(parsers.parse("the partnership score is {score:g}"))
def sttr_score(score: float, finder_context: dict[str, Any]):
    """Verify STTR/partnership dimension score."""
    # TODO: Assert dimension score
    pass


@then(parsers.parse('"{topic_id}" receives recommendation {rec}'))
def topic_recommendation(
    topic_id: str, rec: str, finder_context: dict[str, Any]
):
    """Verify topic recommendation."""
    # TODO: Assert against scoring output
    pass


@then(parsers.parse('the disqualification reason is "{reason}"'))
def disqualification_reason(reason: str, finder_context: dict[str, Any]):
    """Verify disqualification reason text."""
    # TODO: Assert against scoring output
    pass


@then("past performance dimension scores 0.0 for all topics")
def pp_scores_zero(finder_context: dict[str, Any]):
    """Verify PP dimension defaults to 0.0."""
    # TODO: Assert against scoring output
    pass


@then("recommendations cap at EVALUATE rather than NO-GO from data absence")
def no_false_nogo(finder_context: dict[str, Any]):
    """Verify no false NO-GO from missing data."""
    # TODO: Assert recommendation capping
    pass


@then("the score is greater than or equal to zero")
def score_non_negative(finder_context: dict[str, Any]):
    """Property assertion: score >= 0."""
    # TODO: Property-based test assertion
    pass


@then("the score is less than or equal to 1.0")
def score_max_one(finder_context: dict[str, Any]):
    """Property assertion: score <= 1.0."""
    # TODO: Property-based test assertion
    pass
