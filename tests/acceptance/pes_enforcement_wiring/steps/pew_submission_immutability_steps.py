"""Step definitions for Submission Immutability enforcement scenarios (US-PEW-003).

Invokes through driving port: EnforcementEngine.evaluate() only.
Does NOT import SubmissionImmutabilityEvaluator directly.
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, scenarios, then

from tests.acceptance.pes_enforcement_wiring.steps.pew_common_steps import *  # noqa: F403

scenarios("../submission_immutability.feature")


# ---------------------------------------------------------------------------
# Given Steps (Submission-specific)
# ---------------------------------------------------------------------------


@given(
    parsers.parse(
        'Phil\'s proposal "{topic_id}" has submission status "{status}"'
        " and is not finalized"
    ),
)
def proposal_not_finalized(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
    status: str,
):
    """Set up proposal with submission status but immutable=false."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["submission"] = {"status": status, "immutable": False}
    enforcement_context["state"] = state


@given(
    parsers.parse(
        'Phil\'s proposal "{topic_id}" has submission status "{status}"'
        " but is not marked finalized"
    ),
)
def proposal_submitted_not_immutable(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
    status: str,
):
    """Set up proposal submitted but NOT immutable."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["submission"] = {"status": status, "immutable": False}
    enforcement_context["state"] = state


@given(
    parsers.parse('Phil\'s proposal "{topic_id}" has no submission information'),
)
def proposal_no_submission(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal with no submission field."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    # Deliberately no submission key
    enforcement_context["state"] = state


@given(
    "Phil's proposal has been submitted and finalized but has no topic identifier",
)
def proposal_submitted_no_topic_id(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
):
    """Set up submitted+immutable proposal without topic.id."""
    state = base_proposal_state.copy()
    state["topic"] = {}  # No id field
    state["submission"] = {"status": "submitted", "immutable": True}
    enforcement_context["state"] = state


# ---------------------------------------------------------------------------
# Then Steps (Submission-specific)
# ---------------------------------------------------------------------------


@then("the block reason uses the configured default message")
def block_reason_is_default(enforcement_context: dict[str, Any]):
    """Verify the block message falls back to the rule's configured message."""
    result = enforcement_context["result"]
    all_messages = " ".join(result.messages)
    # When topic.id is missing, SubmissionImmutabilityEvaluator falls back
    # to rule.message which is "Proposal is submitted. Artifacts are read-only."
    assert "Proposal is submitted. Artifacts are read-only." in all_messages, (
        f"Expected default message in: {result.messages}"
    )
