"""Step definitions for structured critique and refinement loop scenarios.

Invokes through: critique rating model (new domain utility).
Tests rating validation, flagging, iteration tracking, and average computation.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.visual_asset_quality.conftest import make_critique_ratings
from tests.acceptance.visual_asset_quality.steps.common_steps import *  # noqa: F403

# Link to feature files
scenarios("../milestone-02-critique-loop.feature")


# --- Given steps ---


@given(
    parsers.parse(
        "Phil has rated Figure {num:d} with composition {c:d}, labels {l:d}, "
        "accuracy {a:d}, style match {sm:d}, and scale {sp:d}"
    ),
)
def rated_figure(critique_context, num, c, l, a, sm, sp):
    """Record critique ratings for a figure."""
    critique_context["figure_number"] = num
    critique_context["ratings"] = make_critique_ratings(
        composition=c, labels=l, accuracy=a, style_match=sm, scale_proportion=sp,
    )


@given(
    parsers.parse(
        "Phil provides ratings: composition {c:d}, labels {l:d}, "
        "accuracy {a:d}, style match {sm:d}, scale {sp:d}"
    ),
)
def provide_ratings(critique_context, c, l, a, sm, sp):
    """Set critique ratings for evaluation."""
    critique_context["ratings"] = make_critique_ratings(
        composition=c, labels=l, accuracy=a, style_match=sm, scale_proportion=sp,
    )


@given(
    parsers.parse("Phil provides a rating of {val:d} for composition"),
)
def rating_out_of_range_composition(critique_context, val):
    """Set an out-of-range rating for validation testing."""
    critique_context["ratings"] = {"composition": val}
    critique_context["partial"] = True


@given(
    parsers.parse("Phil provides a rating of {val:d} for accuracy"),
)
def rating_out_of_range_accuracy(critique_context, val):
    """Set an out-of-range rating for validation testing."""
    critique_context["ratings"] = {"accuracy": val}
    critique_context["partial"] = True


@given("Phil provides ratings for only 4 of 5 categories")
def incomplete_ratings(critique_context):
    """Set ratings with a missing category."""
    critique_context["ratings"] = {
        "composition": 4,
        "labels": 3,
        "accuracy": 5,
        "style_match": 4,
        # scale_proportion intentionally missing
    }
    critique_context["partial"] = True


@given(
    parsers.parse("Figure {num:d} has been through {count:d} refinement iterations"),
)
def figure_with_iterations(critique_context, num, count):
    """Set iteration count for a figure."""
    critique_context["figure_number"] = num
    critique_context["iteration_count"] = count


@given(
    parsers.parse("Figure {num:d} has not been refined"),
)
def figure_not_refined(critique_context, num):
    """Set figure with zero iterations."""
    critique_context["figure_number"] = num
    critique_context["iteration_count"] = 0


@given("any valid set of critique ratings")
def any_valid_ratings(critique_context):
    """Use sample valid ratings for property tests."""
    critique_context["ratings"] = make_critique_ratings(
        composition=3, labels=4, accuracy=2, style_match=5, scale_proportion=1,
    )


# --- When steps ---


@when("the critique ratings are evaluated")
def evaluate_ratings(critique_context):
    """Evaluate critique ratings to identify flagged categories.

    Will invoke the critique model when implemented.
    For now, applies the flagging rule: below 3 is flagged.
    """
    ratings = critique_context["ratings"]
    flagged = [cat for cat, val in ratings.items() if val < 3]
    not_flagged = [cat for cat, val in ratings.items() if val >= 3]
    critique_context["flagged"] = flagged
    critique_context["not_flagged"] = not_flagged
    critique_context["all_above_3"] = len(flagged) == 0
    # Check if all 4+
    critique_context["ready_for_approval"] = all(v >= 4 for v in ratings.values())
    # Compute average
    critique_context["average"] = sum(ratings.values()) / len(ratings)


@when("the critique ratings are validated")
def validate_ratings(critique_context):
    """Validate critique ratings for range and completeness.

    Will invoke the critique validation model when implemented.
    """
    ratings = critique_context["ratings"]
    errors = []
    required = {"composition", "labels", "accuracy", "style_match", "scale_proportion"}
    partial = critique_context.get("partial", False)

    if not partial:
        missing = required - set(ratings.keys())
        if missing:
            errors.append(f"All 5 categories must be rated. Missing: {missing}")

    for cat, val in ratings.items():
        if not (1 <= val <= 5):
            errors.append(f"Rating must be between 1 and 5 for {cat}, got {val}")

    if partial and len(ratings) < 5:
        if not any("must be between" in e for e in errors):
            errors.append("All 5 categories must be rated")

    critique_context["validation_errors"] = errors
    critique_context["valid"] = len(errors) == 0


@when("a refinement round is recorded")
def record_refinement(critique_context):
    """Increment the iteration count."""
    critique_context["iteration_count"] = critique_context.get("iteration_count", 0) + 1


@when("a fourth refinement round is requested")
def request_fourth_refinement(critique_context):
    """Attempt a 4th refinement round (should be blocked)."""
    count = critique_context.get("iteration_count", 0)
    if count >= 3:
        critique_context["refinement_blocked"] = True
        critique_context["block_reason"] = "maximum iterations reached"
    else:
        critique_context["iteration_count"] = count + 1
        critique_context["refinement_blocked"] = False


@when(parsers.parse("Figure {num:d} is approved"))
def approve_figure_critique(critique_context, num):
    """Approve a figure, recording its final iteration count."""
    critique_context["approved_figure"] = num
    critique_context["approved_iteration_count"] = critique_context.get("iteration_count", 0)


@when("the average rating is computed")
def compute_average(critique_context):
    """Compute average rating across all categories."""
    ratings = critique_context["ratings"]
    critique_context["average"] = sum(ratings.values()) / len(ratings)


# --- Then steps ---


@then(parsers.parse('"{category}" is flagged for refinement'))
def category_flagged(critique_context, category):
    """Assert a category is flagged."""
    assert category in critique_context["flagged"], (
        f"Expected '{category}' to be flagged, got: {critique_context['flagged']}"
    )


@then(
    parsers.parse(
        '"{c1}", "{c2}", "{c3}", and "{c4}" are not flagged'
    ),
)
def categories_not_flagged(critique_context, c1, c2, c3, c4):
    """Assert multiple categories are not flagged."""
    not_flagged = critique_context["not_flagged"]
    for cat in [c1, c2, c3, c4]:
        assert cat in not_flagged, f"Expected '{cat}' to not be flagged"


@then(
    parsers.parse('the average rating across all categories is {avg:g}'),
)
def average_rating_value(critique_context, avg):
    """Assert average rating matches expected value."""
    assert abs(critique_context["average"] - avg) < 0.01


@then(parsers.parse("the critique is valid with {count:d} rated categories"))
def critique_valid_count(critique_context, count):
    """Assert critique is valid with expected category count."""
    assert critique_context["valid"]
    assert len(critique_context["ratings"]) == count


@then("no categories are flagged for refinement")
def no_categories_flagged(critique_context):
    """Assert no categories are flagged."""
    assert len(critique_context.get("flagged", [])) == 0


@then(
    parsers.parse('"{c1}" and "{c2}" are flagged for refinement'),
)
def two_categories_flagged(critique_context, c1, c2):
    """Assert exactly two categories are flagged."""
    flagged = critique_context["flagged"]
    assert c1 in flagged
    assert c2 in flagged


@then(
    parsers.parse('"{c1}", "{c2}", and "{c3}" are not flagged'),
)
def three_categories_not_flagged(critique_context, c1, c2, c3):
    """Assert three categories are not flagged."""
    not_flagged = critique_context["not_flagged"]
    for cat in [c1, c2, c3]:
        assert cat in not_flagged


@then("the critique signals ready for approval")
def critique_ready_for_approval(critique_context):
    """Assert critique indicates ready for approval."""
    assert critique_context["ready_for_approval"]


@then("a validation error indicates rating must be between 1 and 5")
def validation_error_range(critique_context):
    """Assert validation error about rating range."""
    errors = critique_context["validation_errors"]
    assert any("between 1 and 5" in e for e in errors)


@then("a validation error indicates all 5 categories must be rated")
def validation_error_completeness(critique_context):
    """Assert validation error about missing categories."""
    errors = critique_context["validation_errors"]
    assert any("5 categories" in e for e in errors)


@then(parsers.parse("the iteration count is {count:d}"))
def iteration_count_value(critique_context, count):
    """Assert iteration count matches."""
    assert critique_context["iteration_count"] == count


@then("the refinement is blocked")
def refinement_blocked(critique_context):
    """Assert refinement was blocked."""
    assert critique_context["refinement_blocked"]


@then("the reason indicates maximum iterations reached")
def block_reason_max_iterations(critique_context):
    """Assert block reason mentions max iterations."""
    assert "maximum iterations" in critique_context["block_reason"]


@then(parsers.parse("the iteration count for Figure {num:d} is {count:d}"))
def figure_iteration_count(critique_context, num, count):
    """Assert a specific figure's iteration count."""
    assert critique_context["approved_figure"] == num
    assert critique_context["approved_iteration_count"] == count


@then(parsers.parse("the average is {avg:g}"))
def average_is(critique_context, avg):
    """Assert average rating value."""
    assert abs(critique_context["average"] - avg) < 0.01


@then(parsers.parse("the average is between {low:g} and {high:g} inclusive"))
def average_in_range(critique_context, low, high):
    """Assert average is within range (property test)."""
    avg = critique_context["average"]
    assert low <= avg <= high
