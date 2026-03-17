"""Step definitions for PDC Gate enforcement scenarios (US-PEW-001).

Invokes through driving port: EnforcementEngine.evaluate() only.
Does NOT import PdcGateEvaluator directly.
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, scenarios

from tests.acceptance.pes_enforcement_wiring.steps.pew_common_steps import *  # noqa: F403

scenarios("../pdc_gate.feature")


# ---------------------------------------------------------------------------
# Given Steps (PDC-specific)
# ---------------------------------------------------------------------------


@given(
    parsers.parse(
        'Phil\'s proposal "{topic_id}" has all pre-draft checklist sections'
        " at GREEN for Tier 1 and Tier 2"
    ),
)
def proposal_all_green_pdc(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal with all PDC sections GREEN."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 5
    state["pdc_status"] = {
        "technical_approach": {"tier_1": "GREEN", "tier_2": "GREEN", "red_items": []},
        "budget": {"tier_1": "GREEN", "tier_2": "GREEN", "red_items": []},
        "schedule": {"tier_1": "GREEN", "tier_2": "GREEN", "red_items": []},
    }
    enforcement_context["state"] = state


@given(
    parsers.parse(
        'Phil\'s proposal "{topic_id}" has a pre-draft checklist with section'
        ' "{section}" showing Tier 2 RED for "{red_item}"'
    ),
)
def proposal_with_red_tier2_pdc(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
    section: str,
    red_item: str,
):
    """Set up proposal state with a RED Tier 2 PDC item."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 5
    state["pdc_status"] = {
        section: {
            "tier_1": "GREEN",
            "tier_2": "RED",
            "red_items": [red_item],
        }
    }
    enforcement_context["state"] = state


@given(
    parsers.parse('Phil\'s proposal "{topic_id}" has no pre-draft checklist data'),
)
def proposal_no_pdc_data(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal with no pdc_status field."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 5
    # Deliberately no pdc_status key
    enforcement_context["state"] = state
