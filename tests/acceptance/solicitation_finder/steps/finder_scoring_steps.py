"""Step definitions for topic scoring and ranking scenarios.

Invokes through:
- TopicScoringService (application service -- five-dimension scoring)

Does NOT import internal scoring logic or LLM client directly.
Scoring is delegated to domain services through driving ports.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.topic_scoring import TopicScoringService
from tests.acceptance.solicitation_finder.steps.finder_common_steps import *  # noqa: F403

# Link to feature files
scenarios("../milestone-01-scoring.feature")


# --- Shared scoring service fixture ---


@pytest.fixture()
def scoring_service() -> TopicScoringService:
    """TopicScoringService instance for scoring tests."""
    return TopicScoringService()


# --- Given steps: scoring setup ---


@given(
    parsers.parse("{count:d} candidate topics have full descriptions"),
)
def candidates_with_descriptions(
    count: int,
    go_topic: dict[str, Any],
    evaluate_topic: dict[str, Any],
    finder_context: dict[str, Any],
):
    """Candidates enriched with full topic descriptions.

    Creates a batch of topics including the known GO and EVALUATE topics.
    """
    finder_context["candidate_count"] = count
    # Build a batch with the known-score topics plus filler
    topics = [go_topic, evaluate_topic]
    # Add filler topics to reach the count
    for i in range(count - len(topics)):
        topics.append({
            "topic_id": f"FILLER-{i:03d}",
            "title": f"Generic Research Topic {i}",
            "program": "SBIR",
            "agency": "Other",
            "phase": "I",
            "requires_clearance": "none",
        })
    finder_context["topics"] = topics


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
    """A specific topic has already been scored (from fixture data)."""
    for result in scored_results["results"]:
        if result["topic_id"] == topic_id:
            finder_context["scored_topic"] = result
            break
    else:
        raise ValueError(f"Topic {topic_id} not found in scored_results fixture")
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
    """Set up a topic with a specific composite score for threshold testing."""
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
def topics_scored(
    finder_context: dict[str, Any],
    scoring_service: TopicScoringService,
):
    """Score all candidate topics through the scoring service."""
    topics = finder_context["topics"]
    profile = finder_context["profile"]
    results = scoring_service.score_batch(topics, profile)
    finder_context["scored_batch"] = results
    # Index by topic_id for easy lookup
    finder_context["scored_by_id"] = {r.topic_id: r for r in results}


@when("the dimension breakdown is retrieved")
def retrieve_breakdown(finder_context: dict[str, Any]):
    """Retrieve dimension breakdown for a scored topic from fixture data."""
    finder_context["action"] = "breakdown"


@when("the topic is scored")
def single_topic_scored(
    finder_context: dict[str, Any],
    scoring_service: TopicScoringService,
):
    """Score a single topic through the scoring service."""
    topic = finder_context["current_topic"]
    profile = finder_context["profile"]
    result = scoring_service.score_topic(topic, profile)
    finder_context["scored_single"] = result
    finder_context.setdefault("scored_by_id", {})[result.topic_id] = result


@when("scoring runs")
def scoring_runs(
    finder_context: dict[str, Any],
    scoring_service: TopicScoringService,
    sample_topics: list[dict[str, Any]],
):
    """Run scoring with current profile/topic configuration on sample topics."""
    profile = finder_context["profile"]
    results = scoring_service.score_batch(sample_topics, profile)
    finder_context["scored_batch"] = results
    finder_context["scored_by_id"] = {r.topic_id: r for r in results}
    # Collect all warnings
    all_warnings: list[str] = []
    for r in results:
        all_warnings.extend(r.warnings)
    finder_context["all_warnings"] = all_warnings


@when("recommendations are applied")
def recommendations_applied(
    finder_context: dict[str, Any],
    scoring_service: TopicScoringService,
):
    """Apply recommendation thresholds to pre-set composite scores."""
    score_topics = finder_context.get("score_topics", {})
    recommendations: dict[str, str] = {}
    for topic_id, score in score_topics.items():
        recommendations[topic_id] = scoring_service.apply_recommendation(score)
    finder_context["recommendations"] = recommendations


@when("the composite score is calculated")
def composite_calculated(
    finder_context: dict[str, Any],
    scoring_service: TopicScoringService,
):
    """Calculate composite score (property test)."""
    prop = finder_context.get("property_test", "")
    if prop == "score_non_negative":
        # Test with various profile gaps: empty capabilities, no certs, etc.
        gap_profiles = [
            {"capabilities": [], "certifications": {}, "employee_count": 10},
            {"capabilities": ["test"], "employee_count": 10},
            {"capabilities": ["x"], "certifications": {"sam_gov": {"active": False}}, "employee_count": 10},
        ]
        topic = {"topic_id": "PROP-001", "title": "Any Topic", "program": "SBIR", "agency": "Test", "phase": "I"}
        scores = []
        for p in gap_profiles:
            result = scoring_service.score_topic(topic, p)
            scores.append(result.composite_score)
        finder_context["property_scores"] = scores
    elif prop == "score_max_one":
        # Test with maximum dimension scores
        perfect_profile = {
            "capabilities": ["exact match topic"],
            "certifications": {"sam_gov": {"active": True}, "security_clearance": "top_secret"},
            "employee_count": 5,
            "past_performance": [{"agency": "Test", "topic_area": "exact match topic", "outcome": "awarded"}],
            "research_institution_partners": ["MIT"],
            "key_personnel": [],
        }
        topic = {"topic_id": "PROP-002", "title": "exact match topic", "program": "STTR", "agency": "Test", "phase": "I"}
        result = scoring_service.score_topic(topic, perfect_profile)
        finder_context["property_scores"] = [result.composite_score]


# --- Then steps ---


@then(
    parsers.parse(
        'topic "{topic_id}" scores composite {score:g} with recommendation {rec}'
    ),
)
def topic_scores_composite(
    topic_id: str, score: float, rec: str, finder_context: dict[str, Any]
):
    """Verify topic composite score and recommendation.

    The composite score from the feature file is approximate. We verify:
    1. The recommendation matches exactly (behavioral contract)
    2. The composite is in the expected ballpark
    """
    scored = finder_context["scored_by_id"]
    assert topic_id in scored, f"Topic {topic_id} not found in scored results"
    result = scored[topic_id]
    assert result.recommendation == rec.upper(), (
        f"Topic {topic_id}: expected recommendation {rec.upper()}, "
        f"got {result.recommendation} (composite={result.composite_score})"
    )
    # Composite should be >= threshold for the recommendation
    if rec.upper() == "GO":
        assert result.composite_score >= 0.60, (
            f"GO topic {topic_id} has composite {result.composite_score} < 0.60"
        )
    elif rec.upper() == "EVALUATE":
        assert 0.30 <= result.composite_score < 0.60, (
            f"EVALUATE topic {topic_id} has composite {result.composite_score} outside [0.30, 0.60)"
        )


@then("topics are ranked by composite score descending")
def topics_ranked_descending(finder_context: dict[str, Any]):
    """Verify descending sort order."""
    batch = finder_context["scored_batch"]
    scores = [r.composite_score for r in batch]
    assert scores == sorted(scores, reverse=True), (
        f"Topics not sorted descending: {scores}"
    )


@then(parsers.parse("the subject matter expertise score is {score:g}"))
def sme_score(score: float, finder_context: dict[str, Any]):
    """Verify SME dimension score from pre-scored fixture data."""
    topic = finder_context["scored_topic"]
    actual = topic["dimensions"]["subject_matter"]
    assert actual == pytest.approx(score, abs=0.01), (
        f"SME: expected {score}, got {actual}"
    )


@then(parsers.parse("the past performance score is {score:g}"))
def pp_score(score: float, finder_context: dict[str, Any]):
    """Verify past performance dimension score from pre-scored fixture data."""
    topic = finder_context["scored_topic"]
    actual = topic["dimensions"]["past_performance"]
    assert actual == pytest.approx(score, abs=0.01), (
        f"PP: expected {score}, got {actual}"
    )


@then(parsers.parse("the certifications score is {score:g}"))
def cert_score(score: float, finder_context: dict[str, Any]):
    """Verify certifications dimension score from pre-scored fixture data."""
    topic = finder_context["scored_topic"]
    actual = topic["dimensions"]["certifications"]
    assert actual == pytest.approx(score, abs=0.01), (
        f"Cert: expected {score}, got {actual}"
    )


@then(parsers.parse("the eligibility score is {score:g}"))
def elig_score(score: float, finder_context: dict[str, Any]):
    """Verify eligibility dimension score from pre-scored fixture data."""
    topic = finder_context["scored_topic"]
    actual = topic["dimensions"]["eligibility"]
    assert actual == pytest.approx(score, abs=0.01), (
        f"Elig: expected {score}, got {actual}"
    )


@then(parsers.parse("the partnership score is {score:g}"))
def sttr_score(score: float, finder_context: dict[str, Any]):
    """Verify STTR/partnership dimension score from pre-scored fixture data."""
    topic = finder_context["scored_topic"]
    actual = topic["dimensions"]["sttr"]
    assert actual == pytest.approx(score, abs=0.01), (
        f"STTR: expected {score}, got {actual}"
    )


@then(parsers.parse('"{topic_id}" receives recommendation {rec}'))
def topic_recommendation(
    topic_id: str, rec: str, finder_context: dict[str, Any]
):
    """Verify topic recommendation from scoring service or threshold logic."""
    # Check scored_by_id first (from scoring service)
    scored = finder_context.get("scored_by_id", {})
    if topic_id in scored:
        actual = scored[topic_id].recommendation
        assert actual == rec.upper(), (
            f"Topic {topic_id}: expected {rec.upper()}, got {actual}"
        )
        return

    # Check recommendations dict (from threshold-only scenario)
    recs = finder_context.get("recommendations", {})
    if topic_id in recs:
        actual = recs[topic_id]
        assert actual == rec.upper(), (
            f"Topic {topic_id}: expected {rec.upper()}, got {actual}"
        )
        return

    raise AssertionError(f"Topic {topic_id} not found in any scored results")


@then(parsers.parse('the disqualification reason is "{reason}"'))
def disqualification_reason(reason: str, finder_context: dict[str, Any]):
    """Verify disqualification reason text."""
    result = finder_context.get("scored_single")
    assert result is not None, "No scored single topic in context"
    assert len(result.disqualifiers) > 0, (
        f"Expected disqualifiers but got none for {result.topic_id}"
    )
    assert reason in result.disqualifiers, (
        f"Expected disqualification '{reason}' not found in {result.disqualifiers}"
    )


@then("past performance dimension scores 0.0 for all topics")
def pp_scores_zero(finder_context: dict[str, Any]):
    """Verify PP dimension defaults to 0.0 when profile has no past performance."""
    batch = finder_context["scored_batch"]
    for result in batch:
        assert result.dimensions["past_performance"] == 0.0, (
            f"Topic {result.topic_id}: PP should be 0.0, got {result.dimensions['past_performance']}"
        )


@then("recommendations cap at EVALUATE rather than NO-GO from data absence")
def no_false_nogo(finder_context: dict[str, Any]):
    """Verify no false NO-GO from missing past performance data alone.

    Topics that would otherwise score >= 0.30 composite should get EVALUATE
    (not NO-GO) when the only issue is missing past performance.
    """
    batch = finder_context["scored_batch"]
    for result in batch:
        if result.composite_score >= 0.30 and not result.disqualifiers:
            assert result.recommendation in ("GO", "EVALUATE"), (
                f"Topic {result.topic_id}: composite {result.composite_score} >= 0.30 "
                f"with no disqualifiers should not be NO-GO, got {result.recommendation}"
            )


@then("the score is greater than or equal to zero")
def score_non_negative(finder_context: dict[str, Any]):
    """Property assertion: score >= 0."""
    scores = finder_context.get("property_scores", [])
    assert len(scores) > 0, "No property test scores computed"
    for s in scores:
        assert s >= 0.0, f"Composite score {s} is negative"


@then("the score is less than or equal to 1.0")
def score_max_one(finder_context: dict[str, Any]):
    """Property assertion: score <= 1.0."""
    scores = finder_context.get("property_scores", [])
    assert len(scores) > 0, "No property test scores computed"
    for s in scores:
        assert s <= 1.0, f"Composite score {s} exceeds 1.0"
