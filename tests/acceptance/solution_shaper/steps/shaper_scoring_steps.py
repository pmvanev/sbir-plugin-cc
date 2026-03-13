"""Scoring model step definitions for Solution Shaper acceptance tests.

Tests the approach scoring model: composite calculation, weight validation,
score differentiation, and boundary conditions.

Driving port: scoring model logic (pure domain -- weights, composite calc).
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../milestone-01-approach-scoring.feature")


# ---------------------------------------------------------------------------
# Scoring Helpers (pure domain logic, no I/O)
# ---------------------------------------------------------------------------


def compute_composite(scores: dict[str, float], weights: dict[str, float]) -> float:
    """Compute weighted composite score from dimension scores and weights."""
    total = sum(scores[dim] * weights[dim] for dim in weights)
    return round(total, 4)


def validate_score_range(score: float) -> bool:
    """Check that a score is within 0.00 to 1.00."""
    return 0.00 <= score <= 1.00


# ---------------------------------------------------------------------------
# Given Steps -- Scoring Model
# ---------------------------------------------------------------------------


@given(
    parsers.parse(
        "an approach scored {personnel:g} on personnel alignment, "
        "{past_perf:g} on past performance, {tech:g} on technical readiness, "
        "{sol_fit:g} on solicitation fit, and {comm:g} on commercialization"
    ),
    target_fixture="single_approach",
)
def approach_with_scores(
    personnel: float,
    past_perf: float,
    tech: float,
    sol_fit: float,
    comm: float,
) -> dict[str, Any]:
    return {
        "scores": {
            "personnel_alignment": personnel,
            "past_performance": past_perf,
            "technical_readiness": tech,
            "solicitation_fit": sol_fit,
            "commercialization": comm,
        }
    }


@given(
    parsers.parse(
        "the scoring weights are personnel {p:g}, past performance {pp:g}, "
        "technical readiness {tr:g}, solicitation fit {sf:g}, "
        "and commercialization {c:g}"
    ),
    target_fixture="custom_weights",
)
def custom_weights(
    p: float, pp: float, tr: float, sf: float, c: float
) -> dict[str, float]:
    return {
        "personnel_alignment": p,
        "past_performance": pp,
        "technical_readiness": tr,
        "solicitation_fit": sf,
        "commercialization": c,
    }


@given(
    parsers.parse(
        'approach "{name}" scores {personnel:g} on personnel alignment '
        "and {past_perf:g} on past performance"
    ),
)
def approach_with_partial_scores(
    name: str,
    personnel: float,
    past_perf: float,
    shaper_context: dict[str, Any],
):
    approaches = shaper_context.setdefault("approaches", {})
    approaches[name] = {
        "scores": {
            "personnel_alignment": personnel,
            "past_performance": past_perf,
        }
    }


@given(
    parsers.parse(
        "both approaches score {tech:g} on technical readiness, "
        "{sol_fit:g} on solicitation fit, and {comm:g} on commercialization"
    ),
)
def both_approaches_shared_scores(
    tech: float,
    sol_fit: float,
    comm: float,
    shaper_context: dict[str, Any],
):
    for approach in shaper_context["approaches"].values():
        approach["scores"]["technical_readiness"] = tech
        approach["scores"]["solicitation_fit"] = sol_fit
        approach["scores"]["commercialization"] = comm


@given(
    parsers.parse(
        'approach "{name_a}" and approach "{name_b}" both score '
        "{score:g} on all five dimensions"
    ),
)
def uniform_approaches(
    name_a: str,
    name_b: str,
    score: float,
    shaper_context: dict[str, Any],
):
    approaches = shaper_context.setdefault("approaches", {})
    for name in (name_a, name_b):
        approaches[name] = {
            "scores": {
                "personnel_alignment": score,
                "past_performance": score,
                "technical_readiness": score,
                "solicitation_fit": score,
                "commercialization": score,
            }
        }


@given("any combination of dimension scores for an approach")
def any_dimension_scores(shaper_context: dict[str, Any]):
    """Placeholder for property-based test -- crafter implements with generators."""
    # Example concrete instance for now; crafter replaces with hypothesis
    shaper_context["test_scores"] = {
        "personnel_alignment": 0.50,
        "past_performance": 0.75,
        "technical_readiness": 0.30,
        "solicitation_fit": 0.90,
        "commercialization": 0.10,
    }


@given("any valid set of dimension scores and weights")
def any_scores_and_weights(shaper_context: dict[str, Any]):
    """Placeholder for property-based test -- crafter implements with generators."""
    from tests.acceptance.solution_shaper.conftest import DEFAULT_WEIGHTS

    shaper_context["test_scores"] = {
        "personnel_alignment": 0.60,
        "past_performance": 0.40,
        "technical_readiness": 0.80,
        "solicitation_fit": 0.50,
        "commercialization": 0.70,
    }
    shaper_context["test_weights"] = DEFAULT_WEIGHTS.copy()


@given("the default scoring weights")
def given_default_weights(
    default_weights: dict[str, float], shaper_context: dict[str, Any]
):
    shaper_context["weights"] = default_weights


# ---------------------------------------------------------------------------
# When Steps -- Scoring Model
# ---------------------------------------------------------------------------


@when("the composite score is calculated", target_fixture="composite_result")
def calculate_composite(
    single_approach: dict[str, Any],
    custom_weights: dict[str, float],
) -> float:
    return compute_composite(single_approach["scores"], custom_weights)


@when("composite scores are calculated for both approaches")
def calculate_both_composites(
    shaper_context: dict[str, Any],
    default_weights: dict[str, float],
):
    shaper_context["composites"] = {}
    for name, approach in shaper_context["approaches"].items():
        shaper_context["composites"][name] = compute_composite(
            approach["scores"], default_weights
        )


@when("the composite is computed from those scores and weights")
def compute_from_context(shaper_context: dict[str, Any]):
    from tests.acceptance.solution_shaper.conftest import DEFAULT_WEIGHTS

    scores = shaper_context["test_scores"]
    weights = shaper_context.get("test_weights", DEFAULT_WEIGHTS)
    shaper_context["computed_composite"] = compute_composite(scores, weights)


@when("scores are validated")
def validate_scores(shaper_context: dict[str, Any]):
    shaper_context["score_valid"] = all(
        validate_score_range(s) for s in shaper_context["test_scores"].values()
    )


@when("the weights are validated")
def validate_weights(shaper_context: dict[str, Any]):
    shaper_context["weight_sum"] = round(
        sum(shaper_context["weights"].values()), 2
    )


# ---------------------------------------------------------------------------
# Then Steps -- Scoring Model
# ---------------------------------------------------------------------------


@then(parsers.parse("the composite score is {expected:g}"))
def composite_equals(composite_result: float, expected: float):
    assert composite_result == pytest.approx(expected, abs=0.001), (
        f"Expected composite {expected}, got {composite_result}"
    )


@then(parsers.parse('"{higher}" scores higher than "{lower}"'))
def scores_higher(higher: str, lower: str, shaper_context: dict[str, Any]):
    composites = shaper_context["composites"]
    assert composites[higher] > composites[lower], (
        f"Expected {higher} ({composites[higher]}) > {lower} ({composites[lower]})"
    )


@then(parsers.parse("the score spread is at least {spread:d} percentage points"))
def score_spread_at_least(spread: int, shaper_context: dict[str, Any]):
    composites = list(shaper_context["composites"].values())
    actual_spread = (max(composites) - min(composites)) * 100
    assert actual_spread >= spread, (
        f"Expected spread >= {spread}pp, got {actual_spread:.1f}pp"
    )


@then(
    parsers.parse(
        '"{name_a}" and "{name_b}" have the same composite score of {expected:g}'
    )
)
def equal_composites(
    name_a: str, name_b: str, expected: float, shaper_context: dict[str, Any]
):
    composites = shaper_context["composites"]
    assert composites[name_a] == pytest.approx(expected, abs=0.001)
    assert composites[name_b] == pytest.approx(expected, abs=0.001)


@then(parsers.parse("each dimension score is between {low:g} and {high:g} inclusive"))
def scores_in_range(low: float, high: float, shaper_context: dict[str, Any]):
    assert shaper_context["score_valid"], "Not all scores within valid range"


@then(
    parsers.parse(
        "the composite score is greater than or equal to {minimum:g}"
    )
)
def composite_non_negative(minimum: float, shaper_context: dict[str, Any]):
    from tests.acceptance.solution_shaper.conftest import DEFAULT_WEIGHTS

    scores = shaper_context["test_scores"]
    weights = shaper_context.get("test_weights", DEFAULT_WEIGHTS)
    result = compute_composite(scores, weights)
    assert result >= minimum, f"Composite {result} < {minimum}"


@then(parsers.parse("the weights sum to {expected:g}"))
def weights_sum_to(expected: float, shaper_context: dict[str, Any]):
    assert shaper_context["weight_sum"] == pytest.approx(expected, abs=0.001), (
        f"Weights sum to {shaper_context['weight_sum']}, expected {expected}"
    )


# Need pytest import for approx
import pytest
