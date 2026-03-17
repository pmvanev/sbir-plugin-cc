"""Step definitions for Winning Pattern Confidence Levels feature.

Tests validate confidence tier calculation based on win corpus size.
"""

from __future__ import annotations

from typing import Any

import jsonschema
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.proposal_quality_discovery.conftest import (
    build_winning_patterns,
    calculate_confidence,
    now_iso,
)

scenarios("../features/confidence_calculation.feature")


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given(
    parsers.parse("winning patterns assembled from {n:d} winning proposals"),
    target_fixture="artifact_context",
)
def patterns_from_wins(n):
    return {"win_count": n}


@given(
    parsers.parse('winning patterns with confidence "{conf}" from {n:d} wins'),
    target_fixture="artifact_context",
)
def patterns_with_confidence(conf, n):
    return {"win_count": n, "current_confidence": conf}


@given(
    parsers.parse("a winning patterns artifact with win count {n:d}"),
    target_fixture="artifact_context",
)
def patterns_invalid_win_count(n):
    return {"win_count": n, "invalid_test": True}


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when("confidence level is calculated", target_fixture="calculated_confidence")
def calc_confidence(artifact_context):
    return calculate_confidence(artifact_context["win_count"])


@when(parsers.parse("{n:d} new winning proposals are added"))
def add_wins(artifact_context, n):
    artifact_context["win_count"] += n


@when(
    "confidence level is recalculated",
    target_fixture="calculated_confidence",
)
def recalc_confidence(artifact_context):
    return calculate_confidence(artifact_context["win_count"])


@when("the artifact is validated", target_fixture="validation_error")
def validate_invalid_patterns(artifact_context, winning_patterns_schema):
    data = {
        "schema_version": "1.0.0",
        "updated_at": now_iso(),
        "confidence_level": "low",
        "win_count": artifact_context["win_count"],
        "proposal_ratings": [],
        "patterns": [],
    }
    try:
        jsonschema.validate(data, winning_patterns_schema)
        return None
    except jsonschema.ValidationError as e:
        return str(e.message)


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------


@then(parsers.parse('confidence level is "{level}"'))
def confidence_is(calculated_confidence, level):
    assert calculated_confidence == level


@then(parsers.parse("win count is {n:d}"))
def win_count_is(artifact_context, n):
    assert artifact_context["win_count"] == n


@then("validation fails because win count must not be negative")
def negative_win_count(validation_error):
    assert validation_error is not None
