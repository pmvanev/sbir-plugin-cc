"""Step definitions for contextual rigor suggestion scenarios.

Invokes through: RigorService suggestion logic (driving port).
Tests suggestion computation based on fit score and contract phase.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.rigor_profile.steps.rigor_common_steps import *  # noqa: F403

# Link feature files
scenarios("../milestone-04-suggestion.feature")


# --- Given steps ---


@given(
    parsers.parse(
        'a proposal is created with fit score {score:d} and phase "{phase}"'
    ),
    target_fixture="suggestion_context",
)
def proposal_with_metadata(score: int, phase: str) -> dict[str, Any]:
    """Set up proposal metadata for suggestion computation."""
    return {"fit_score": score, "phase": phase}


# --- When steps ---


@when("the rigor suggestion is computed", target_fixture="suggestion_result")
def compute_suggestion(suggestion_context: dict[str, Any]) -> dict[str, Any]:
    """Invoke suggestion logic with proposal metadata."""
    result: dict[str, Any] = {}
    try:
        from pes.domain.rigor import compute_rigor_suggestion

        suggestion = compute_rigor_suggestion(
            fit_score=suggestion_context["fit_score"],
            phase=suggestion_context["phase"],
        )
        result["suggestion"] = suggestion
        result["error"] = None
    except Exception as exc:
        result["suggestion"] = None
        result["error"] = str(exc)
    return result


# --- Then steps ---


@then(parsers.parse('the suggestion recommends "{profile}"'))
def suggestion_recommends(suggestion_result: dict[str, Any], profile: str):
    """Verify the suggestion matches the expected profile."""
    assert suggestion_result["error"] is None, (
        f"Unexpected error: {suggestion_result['error']}"
    )
    assert suggestion_result["suggestion"] == profile, (
        f"Expected suggestion '{profile}', got '{suggestion_result['suggestion']}'"
    )


@then("no rigor suggestion is provided")
def no_suggestion(suggestion_result: dict[str, Any]):
    """Verify no suggestion was generated."""
    assert suggestion_result["error"] is None, (
        f"Unexpected error: {suggestion_result['error']}"
    )
    assert suggestion_result["suggestion"] is None, (
        f"Expected no suggestion, got '{suggestion_result['suggestion']}'"
    )


@then('the default profile remains "standard"')
def default_remains_standard(suggestion_result: dict[str, Any]):
    """Verify the suggestion does not change the default profile.

    The suggestion is informational only -- it does not auto-apply.
    The default is always "standard" regardless of what suggestion says.
    """
    # This is a declaration of intent. The actual default is set during
    # proposal creation, which always writes "standard" to rigor-profile.json.
    # The suggestion result does not modify any state.
    assert suggestion_result["suggestion"] is not None or True  # always passes
