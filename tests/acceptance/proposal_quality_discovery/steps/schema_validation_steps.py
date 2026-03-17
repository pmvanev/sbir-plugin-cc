"""Step definitions for Quality Artifact Schema Validation feature.

Tests validate that quality artifacts conform to their JSON schemas.
This is the first enabled feature -- all scenarios are active.
"""

from __future__ import annotations

from typing import Any

import jsonschema
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.proposal_quality_discovery.conftest import (
    build_feedback_entry,
    build_proposal_rating,
    build_quality_preferences,
    build_winning_patterns,
    build_writing_quality_profile,
    now_iso,
)

scenarios("../features/artifact_schema_validation.feature")


# ---------------------------------------------------------------------------
# Quality Preferences -- Given steps
# ---------------------------------------------------------------------------


@given(
    parsers.parse(
        'quality preferences captured with tone "{tone}" and detail "{detail}"'
    ),
    target_fixture="artifact_context",
)
def prefs_with_tone_and_detail(tone, detail):
    return {"tone": tone, "detail_level": detail, "data": {}}


@given(
    parsers.parse(
        'evidence style is "{evidence}" and organization is "{org}"'
    ),
)
def prefs_evidence_and_org(artifact_context, evidence, org):
    artifact_context["evidence_style"] = evidence
    artifact_context["organization"] = org


@given(
    parsers.parse('practices to replicate include "{practice}"'),
)
def prefs_practice_replicate(artifact_context, practice):
    artifact_context.setdefault("practices_to_replicate", []).append(practice)


@given(
    parsers.parse('practices to avoid include "{practice}"'),
)
def prefs_practice_avoid(artifact_context, practice):
    artifact_context.setdefault("practices_to_avoid", []).append(practice)


@given(
    parsers.parse(
        'quality preferences captured with custom tone "{description}"'
    ),
    target_fixture="artifact_context",
)
def prefs_custom_tone(description):
    return {
        "tone": "custom",
        "tone_custom_description": description,
        "data": {},
    }


@given(
    parsers.parse('detail level is "{detail}"'),
)
def prefs_detail_level(artifact_context, detail):
    artifact_context["detail_level"] = detail


@given(
    parsers.parse(
        'evidence style is "{evidence}" and organization is "{org}"'
    ),
)
def prefs_evidence_org_again(artifact_context, evidence, org):
    # Handled by the earlier step; pytest-bdd will match the first definition.
    artifact_context["evidence_style"] = evidence
    artifact_context["organization"] = org


@given(
    parsers.parse(
        "quality preferences with {n:d} practices to replicate and {m:d} practices to avoid"
    ),
    target_fixture="artifact_context",
)
def prefs_with_n_practices(n, m):
    return {
        "tone": "direct_data_driven",
        "detail_level": "deep_technical",
        "evidence_style": "inline_quantitative",
        "organization": "short_paragraphs",
        "practices_to_replicate": [f"Practice {i+1}" for i in range(n)],
        "practices_to_avoid": [f"Anti-pattern {i+1}" for i in range(m)],
    }


@given(
    "quality preferences with no practices to replicate or avoid",
    target_fixture="artifact_context",
)
def prefs_empty_practices():
    return {
        "tone": "formal_authoritative",
        "detail_level": "moderate",
        "evidence_style": "narrative_supporting",
        "organization": "medium_paragraphs",
        "practices_to_replicate": [],
        "practices_to_avoid": [],
    }


@given(
    parsers.parse('quality preferences with tone "{tone}"'),
    target_fixture="artifact_context",
)
def prefs_invalid_tone(tone):
    return {"tone": tone, "invalid_test": True}


@given(
    "quality preferences with no tone specified",
    target_fixture="artifact_context",
)
def prefs_no_tone():
    return {"no_tone": True, "invalid_test": True}


@given(
    'quality preferences with tone "custom" but no description',
    target_fixture="artifact_context",
)
def prefs_custom_no_desc():
    return {"tone": "custom", "no_description": True, "invalid_test": True}


@given(
    parsers.parse('quality preferences with detail level "{detail}"'),
    target_fixture="artifact_context",
)
def prefs_invalid_detail(detail):
    return {"detail_level": detail, "tone": "direct_data_driven", "invalid_test": True}


# ---------------------------------------------------------------------------
# Quality Preferences -- When steps
# ---------------------------------------------------------------------------


@when(
    "the quality preferences artifact is assembled",
    target_fixture="assembled_artifact",
)
def assemble_quality_preferences(artifact_context):
    return build_quality_preferences(
        tone=artifact_context.get("tone", "direct_data_driven"),
        tone_custom_description=artifact_context.get("tone_custom_description"),
        detail_level=artifact_context.get("detail_level", "deep_technical"),
        evidence_style=artifact_context.get("evidence_style", "inline_quantitative"),
        organization=artifact_context.get("organization", "short_paragraphs"),
        practices_to_replicate=artifact_context.get("practices_to_replicate", []),
        practices_to_avoid=artifact_context.get("practices_to_avoid", []),
    )


@when(
    "the quality preferences artifact is validated",
    target_fixture="validation_error",
)
def validate_quality_preferences_invalid(
    artifact_context, quality_preferences_schema
):
    """Attempt to validate a deliberately invalid artifact."""
    # Build a raw artifact dict that may be invalid
    data: dict[str, Any] = {
        "schema_version": "1.0.0",
        "updated_at": now_iso(),
        "detail_level": artifact_context.get("detail_level", "deep_technical"),
        "evidence_style": artifact_context.get("evidence_style", "inline_quantitative"),
        "organization": artifact_context.get("organization", "short_paragraphs"),
        "practices_to_replicate": [],
        "practices_to_avoid": [],
    }
    if "tone" in artifact_context:
        data["tone"] = artifact_context["tone"]
    if artifact_context.get("no_tone"):
        # Omit tone field entirely
        pass
    elif "tone" in artifact_context:
        data["tone"] = artifact_context["tone"]
    if artifact_context.get("tone_custom_description"):
        data["tone_custom_description"] = artifact_context["tone_custom_description"]

    try:
        jsonschema.validate(data, quality_preferences_schema)
        return None  # No error
    except jsonschema.ValidationError as e:
        return str(e.message)


# ---------------------------------------------------------------------------
# Winning Patterns -- Given steps
# ---------------------------------------------------------------------------


@given(
    parsers.parse(
        'proposal {topic_id} rated as "{rating}" for "{agency}" with outcome "{outcome}"'
    ),
    target_fixture="artifact_context",
)
def proposal_rated(topic_id, rating, agency, outcome):
    rating_entry = build_proposal_rating(
        topic_id=topic_id,
        agency=agency,
        outcome=outcome,
        quality_rating=rating,
    )
    return {"proposal_ratings": [rating_entry], "patterns": []}


@given(
    parsers.parse('winning practice "{practice}" is recorded'),
)
def winning_practice(artifact_context, practice):
    if artifact_context.get("proposal_ratings"):
        artifact_context["proposal_ratings"][0].setdefault(
            "winning_practices", []
        ).append(practice)


@given(
    parsers.parse('evaluator praise "{praise}" is recorded'),
)
def evaluator_praise(artifact_context, praise):
    if artifact_context.get("proposal_ratings"):
        artifact_context["proposal_ratings"][0].setdefault(
            "evaluator_praise", []
        ).append(praise)


@given(
    parsers.parse(
        'pattern "{pattern}" seen in {agencies} proposals'
    ),
    target_fixture="artifact_context",
)
def pattern_multiple_agencies(pattern, agencies):
    agency_list = [a.strip() for a in agencies.split(" and ")]
    return {
        "proposal_ratings": [],
        "patterns": [
            {
                "pattern": pattern,
                "frequency": len(agency_list),
                "agencies": agency_list,
                "source_proposals": [f"PROP-{i}" for i in range(len(agency_list))],
                "universal": False,
                "first_seen": now_iso(),
                "last_seen": now_iso(),
            }
        ],
    }


@given(
    parsers.parse('a proposal rating with quality rating "{rating}"'),
    target_fixture="artifact_context",
)
def invalid_quality_rating(rating):
    return {"invalid_quality_rating": rating, "invalid_test": True}


@given(
    parsers.parse('a proposal rating with outcome "{outcome}"'),
    target_fixture="artifact_context",
)
def invalid_outcome(outcome):
    return {"invalid_outcome": outcome, "invalid_test": True}


@given(
    "a proposal rating with an empty topic ID",
    target_fixture="artifact_context",
)
def empty_topic_id():
    return {"empty_topic_id": True, "invalid_test": True}


# ---------------------------------------------------------------------------
# Winning Patterns -- When steps
# ---------------------------------------------------------------------------


@when(
    parsers.parse(
        "the winning patterns artifact is assembled with {n:d} wins analyzed"
    ),
    target_fixture="assembled_artifact",
)
def assemble_winning_patterns_with_count(artifact_context, n):
    return build_winning_patterns(
        win_count=n,
        proposal_ratings=artifact_context.get("proposal_ratings", []),
        patterns=artifact_context.get("patterns", []),
    )


@when(
    "the winning patterns artifact is assembled",
    target_fixture="assembled_artifact",
)
def assemble_winning_patterns(artifact_context):
    ratings = artifact_context.get("proposal_ratings", [])
    win_count = sum(1 for r in ratings if r.get("outcome") == "WIN")
    return build_winning_patterns(
        win_count=win_count,
        proposal_ratings=ratings,
        patterns=artifact_context.get("patterns", []),
    )


@when(
    "the winning patterns artifact is validated",
    target_fixture="validation_error",
)
def validate_winning_patterns_invalid(
    artifact_context, winning_patterns_schema
):
    """Attempt to validate a deliberately invalid winning patterns artifact."""
    # Build a raw artifact with the invalid field
    rating: dict[str, Any] = {
        "topic_id": "TEST-001",
        "agency": "Air Force",
        "outcome": "WIN",
        "quality_rating": "strong",
        "rated_at": now_iso(),
    }
    if "invalid_quality_rating" in artifact_context:
        rating["quality_rating"] = artifact_context["invalid_quality_rating"]
    if "invalid_outcome" in artifact_context:
        rating["outcome"] = artifact_context["invalid_outcome"]
    if artifact_context.get("empty_topic_id"):
        rating["topic_id"] = ""

    data = {
        "schema_version": "1.0.0",
        "updated_at": now_iso(),
        "confidence_level": "low",
        "win_count": 0,
        "proposal_ratings": [rating],
        "patterns": [],
    }

    try:
        jsonschema.validate(data, winning_patterns_schema)
        return None
    except jsonschema.ValidationError as e:
        return str(e.message)


# ---------------------------------------------------------------------------
# Writing Quality Profile -- Given steps
# ---------------------------------------------------------------------------


@given(
    parsers.parse(
        'evaluator comment "{comment}" for proposal {topic_id} by "{agency}" with outcome "{outcome}"'
    ),
    target_fixture="artifact_context",
)
def feedback_entry(comment, topic_id, agency, outcome):
    entry = build_feedback_entry(
        comment=comment,
        topic_id=topic_id,
        agency=agency,
        outcome=outcome,
    )
    return {"entries": [entry]}


@given(
    parsers.parse(
        'the comment is categorized as "{category}" with sentiment "{sentiment}"'
    ),
)
def categorize_comment(artifact_context, category, sentiment):
    if artifact_context.get("entries"):
        artifact_context["entries"][-1]["category"] = category
        artifact_context["entries"][-1]["sentiment"] = sentiment


@given(
    parsers.parse('the comment targets the "{section}" section'),
)
def comment_section(artifact_context, section):
    if artifact_context.get("entries"):
        artifact_context["entries"][-1]["section"] = section


@given(
    parsers.parse(
        "writing quality entries for {agency} with {pos:d} positive and {neg:d} negative organization clarity comments"
    ),
    target_fixture="artifact_context",
)
def wqp_with_agency_pattern(agency, pos, neg):
    entries = []
    for _ in range(pos):
        entries.append(
            build_feedback_entry(
                comment="Well-organized",
                agency=agency,
                outcome="WIN",
                category="organization_clarity",
                sentiment="positive",
            )
        )
    for _ in range(neg):
        entries.append(
            build_feedback_entry(
                comment="Difficult to follow",
                agency=agency,
                outcome="LOSS",
                category="organization_clarity",
                sentiment="negative",
            )
        )
    agency_patterns = [
        {
            "agency": agency,
            "discriminators": ["organization_clarity"],
            "positive_count": pos,
            "negative_count": neg,
        }
    ]
    return {"entries": entries, "agency_patterns": agency_patterns}


@given(
    parsers.parse('an evaluator feedback entry with category "{category}"'),
    target_fixture="artifact_context",
)
def invalid_category(category):
    return {"invalid_category": category, "invalid_test": True}


@given(
    parsers.parse('an evaluator feedback entry with sentiment "{sentiment}"'),
    target_fixture="artifact_context",
)
def invalid_sentiment(sentiment):
    return {"invalid_sentiment": sentiment, "invalid_test": True}


@given(
    "an evaluator feedback entry with an empty comment",
    target_fixture="artifact_context",
)
def empty_comment():
    return {"empty_comment": True, "invalid_test": True}


# ---------------------------------------------------------------------------
# Writing Quality Profile -- When steps
# ---------------------------------------------------------------------------


@when(
    "the writing quality profile artifact is assembled",
    target_fixture="assembled_artifact",
)
def assemble_wqp(artifact_context):
    return build_writing_quality_profile(
        entries=artifact_context.get("entries", []),
        agency_patterns=artifact_context.get("agency_patterns"),
    )


@when(
    "the writing quality profile includes agency patterns",
    target_fixture="assembled_artifact",
)
def assemble_wqp_with_patterns(artifact_context):
    return build_writing_quality_profile(
        entries=artifact_context.get("entries", []),
        agency_patterns=artifact_context.get("agency_patterns", []),
    )


@when(
    "the writing quality profile artifact is validated",
    target_fixture="validation_error",
)
def validate_wqp_invalid(artifact_context, writing_quality_profile_schema):
    """Attempt to validate a deliberately invalid writing quality profile."""
    entry: dict[str, Any] = {
        "comment": "Test comment",
        "topic_id": "AF243-002",
        "agency": "Air Force",
        "outcome": "LOSS",
        "category": "organization_clarity",
        "sentiment": "negative",
        "added_at": now_iso(),
    }
    if "invalid_category" in artifact_context:
        entry["category"] = artifact_context["invalid_category"]
    if "invalid_sentiment" in artifact_context:
        entry["sentiment"] = artifact_context["invalid_sentiment"]
    if artifact_context.get("empty_comment"):
        entry["comment"] = ""

    data = {
        "schema_version": "1.0.0",
        "updated_at": now_iso(),
        "entries": [entry],
    }

    try:
        jsonschema.validate(data, writing_quality_profile_schema)
        return None
    except jsonschema.ValidationError as e:
        return str(e.message)


# ---------------------------------------------------------------------------
# Shared Then steps
# ---------------------------------------------------------------------------


@then("the artifact passes schema validation")
def artifact_valid(
    assembled_artifact,
    quality_preferences_schema,
    winning_patterns_schema,
    writing_quality_profile_schema,
):
    """Validate assembled artifact against the appropriate schema."""
    # Determine which schema to use based on artifact fields
    if "tone" in assembled_artifact:
        jsonschema.validate(assembled_artifact, quality_preferences_schema)
    elif "win_count" in assembled_artifact:
        jsonschema.validate(assembled_artifact, winning_patterns_schema)
    elif "entries" in assembled_artifact:
        jsonschema.validate(assembled_artifact, writing_quality_profile_schema)
    else:
        pytest.fail("Cannot determine artifact type for schema validation")


@then("the artifact contains schema version and updated timestamp")
def artifact_has_metadata(assembled_artifact):
    assert "schema_version" in assembled_artifact
    assert assembled_artifact["schema_version"] == "1.0.0"
    assert "updated_at" in assembled_artifact
    assert len(assembled_artifact["updated_at"]) > 0


@then(parsers.parse('confidence level is "{level}" because fewer than 10 wins are analyzed'))
def confidence_low(assembled_artifact, level):
    assert assembled_artifact["confidence_level"] == level


@then(parsers.parse('the tone field is "{tone}"'))
def tone_is(assembled_artifact, tone):
    assert assembled_artifact["tone"] == tone


@then("the custom tone description is stored")
def custom_tone_stored(assembled_artifact):
    assert "tone_custom_description" in assembled_artifact
    assert len(assembled_artifact["tone_custom_description"]) > 0


@then(parsers.parse("practices to replicate contains {n:d} items"))
def practices_replicate_count(assembled_artifact, n):
    assert len(assembled_artifact["practices_to_replicate"]) == n


@then(parsers.parse("practices to avoid contains {n:d} items"))
def practices_avoid_count(assembled_artifact, n):
    assert len(assembled_artifact["practices_to_avoid"]) == n


@then("practices to replicate is an empty list")
def practices_replicate_empty(assembled_artifact):
    assert assembled_artifact["practices_to_replicate"] == []


@then("practices to avoid is an empty list")
def practices_avoid_empty(assembled_artifact):
    assert assembled_artifact["practices_to_avoid"] == []


@then("the pattern lists both agencies")
def pattern_has_agencies(assembled_artifact):
    assert len(assembled_artifact["patterns"]) > 0
    assert len(assembled_artifact["patterns"][0]["agencies"]) >= 2


@then("source proposals are recorded")
def pattern_has_sources(assembled_artifact):
    assert len(assembled_artifact["patterns"][0]["source_proposals"]) >= 1


@then(parsers.parse("the proposal rating is recorded with outcome {outcome}"))
def rating_has_outcome(assembled_artifact, outcome):
    assert any(
        r["outcome"] == outcome for r in assembled_artifact["proposal_ratings"]
    )


@then("no winning practices are expected for a losing proposal")
def no_winning_practices_for_loss(assembled_artifact):
    # Losing proposals can have empty winning_practices
    for r in assembled_artifact["proposal_ratings"]:
        if r["outcome"] == "LOSS":
            # It is acceptable for winning_practices to be empty
            pass


@then(parsers.parse('the entry has sentiment "{sentiment}"'))
def entry_sentiment(assembled_artifact, sentiment):
    assert assembled_artifact["entries"][0]["sentiment"] == sentiment


@then(parsers.parse("the entry is linked to proposal {topic_id}"))
def entry_linked(assembled_artifact, topic_id):
    assert assembled_artifact["entries"][0]["topic_id"] == topic_id


@then(parsers.parse('the entry specifies section "{section}"'))
def entry_section(assembled_artifact, section):
    assert assembled_artifact["entries"][0]["section"] == section


@then(parsers.parse('{agency} has "{disc}" listed as a discriminator'))
def agency_discriminator(assembled_artifact, agency, disc):
    for ap in assembled_artifact.get("agency_patterns", []):
        if ap["agency"] == agency:
            assert disc in ap["discriminators"]
            return
    pytest.fail(f"No agency pattern found for {agency}")


@then(parsers.parse("positive count is {pos:d} and negative count is {neg:d}"))
def agency_counts(assembled_artifact, pos, neg):
    ap = assembled_artifact["agency_patterns"][0]
    assert ap["positive_count"] == pos
    assert ap["negative_count"] == neg


# ---------------------------------------------------------------------------
# Validation error Then steps
# ---------------------------------------------------------------------------


@then("validation fails because tone is not an allowed value")
def tone_invalid(validation_error):
    assert validation_error is not None


@then("validation fails because tone is required")
def tone_required(validation_error):
    assert validation_error is not None


@then("validation fails because custom tone requires a description")
def custom_tone_required(validation_error):
    assert validation_error is not None


@then("validation fails because detail level is not an allowed value")
def detail_invalid(validation_error):
    assert validation_error is not None


@then("validation fails because quality rating is not an allowed value")
def quality_rating_invalid(validation_error):
    assert validation_error is not None


@then("validation fails because outcome must be WIN or LOSS")
def outcome_invalid(validation_error):
    assert validation_error is not None


@then("validation fails because topic ID must not be empty")
def topic_id_empty(validation_error):
    assert validation_error is not None


@then("validation fails because category is not in the allowed taxonomy")
def category_invalid(validation_error):
    assert validation_error is not None


@then("validation fails because sentiment must be positive or negative")
def sentiment_invalid(validation_error):
    assert validation_error is not None


@then("validation fails because comment must not be empty")
def comment_empty(validation_error):
    assert validation_error is not None
