"""Step definitions for C3 walking skeleton scenarios.

Walking skeletons trace thin vertical slices of user value E2E.
These step definitions delegate to the same driving ports as focused
scenarios but compose longer journeys.
"""

from __future__ import annotations

import json

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.rules import Decision
from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to walking skeleton C3 feature file
scenarios("../features/walking_skeleton_c3.feature")

# Walking skeleton steps reuse step definitions from C3 domain modules.
# pytest-bdd discovers steps by importing them.
# Steps are defined in:
#   - common_steps.py (plugin active, proposal state setup)
#   - pes_enforcement_c3_steps.py (C3 PES blocking, PDC gate)
#   - visual_asset_steps.py (figure generation)
#   - formatting_assembly_steps.py (formatting, assembly)
#   - final_review_steps.py (review, sign-off)
#   - submission_steps.py (packaging, confirmation)
#   - debrief_steps.py (outcome, debrief)


# --- Walking Skeleton 8 specific steps ---


@given(
    "Phil has an active proposal with section 3.2 having a RED Tier 2 PDC item",
    target_fixture="active_state",
)
def proposal_with_red_pdc(sample_state, write_state, proposal_dir):
    """Set up proposal ready for Wave 5 but with RED PDC."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 5
    state["waves"] = {
        "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
        "1": {"status": "completed", "completed_at": "2026-03-05T10:00:00Z"},
        "2": {"status": "completed", "completed_at": "2026-03-06T10:00:00Z"},
        "3": {"status": "completed", "completed_at": "2026-03-07T10:00:00Z"},
        "4": {"status": "completed", "completed_at": "2026-03-08T10:00:00Z"},
        "5": {"status": "active", "completed_at": None},
    }
    # Create RED PDC file for section 3.2
    pdcs_dir = proposal_dir / "pdcs"
    pdcs_dir.mkdir(exist_ok=True)
    pdc_data = {
        "section_id": "3.2",
        "tier_1": {"status": "GREEN", "items": []},
        "tier_2": {
            "status": "RED",
            "items": [
                {
                    "item_id": "pdc-3.2-t2-001",
                    "description": "Phase II pathway uses generic language",
                    "status": "RED",
                }
            ],
        },
    }
    (pdcs_dir / "section-3.2.pdc").write_text(json.dumps(pdc_data, indent=2))
    write_state(state)
    return state


@when(
    "Phil attempts to start Wave 5 visual asset work",
    target_fixture="enforcement_result",
)
def attempt_wave_5_skeleton(enforcement_engine, state_file):
    """Invoke Wave 5 command through PES enforcement."""
    from pes.adapters.json_state_adapter import JsonStateAdapter

    state_reader = JsonStateAdapter(str(state_file.parent))
    state = state_reader.load()
    return enforcement_engine.evaluate(state, tool_name="wave_5_visuals")


@then("the enforcement system blocks the action")
def verify_action_blocked_skeleton(enforcement_result):
    """Verify enforcement returns block decision."""
    assert enforcement_result.decision == Decision.BLOCK


@then("Phil sees the specific section and PDC items that remain RED")
def verify_red_pdc_details_skeleton(enforcement_result):
    """Verify message contains PDC-specific details."""
    all_messages = " ".join(enforcement_result.messages).lower()
    assert "pdc" in all_messages or "red" in all_messages or "section" in all_messages, (
        f"Expected PDC details in {enforcement_result.messages}"
    )


@then("Phil sees guidance to resolve the RED items before proceeding")
def verify_red_resolution_guidance(enforcement_result):
    """Verify guidance to resolve RED items."""
    assert len(enforcement_result.messages) > 0, (
        "Expected guidance messages for RED PDC items"
    )


# --- Walking Skeleton 6 and 7 steps ---
# These compose steps from other domain modules.
# Additional skeleton-specific steps below.


@given(
    "Phil has an active proposal with all sections approved and PDCs GREEN",
    target_fixture="active_state",
)
def proposal_all_approved_green(sample_state, write_state, proposal_dir):
    """Set up proposal with all sections approved and PDCs GREEN."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 5
    state["waves"] = {
        "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
        "1": {"status": "completed", "completed_at": "2026-03-05T10:00:00Z"},
        "2": {"status": "completed", "completed_at": "2026-03-06T10:00:00Z"},
        "3": {"status": "completed", "completed_at": "2026-03-07T10:00:00Z"},
        "4": {"status": "completed", "completed_at": "2026-03-08T10:00:00Z"},
        "5": {"status": "active", "completed_at": None},
    }
    # Create GREEN PDC files
    pdcs_dir = proposal_dir / "pdcs"
    pdcs_dir.mkdir(exist_ok=True)
    for section_id in ["3.1", "3.2", "3.3", "3.4", "4.1"]:
        pdc_data = {
            "section_id": section_id,
            "tier_1": {"status": "GREEN", "items": []},
            "tier_2": {"status": "GREEN", "items": []},
        }
        (pdcs_dir / f"section-{section_id}.pdc").write_text(
            json.dumps(pdc_data, indent=2)
        )
    write_state(state)
    return state


@given(
    parsers.parse("the approved outline contains {count:d} figure placeholders"),
)
def outline_with_figures(proposal_dir, count):
    """Create outline with figure placeholders for skeleton."""
    outline_dir = proposal_dir / "artifacts" / "wave-3-outline"
    outline_dir.mkdir(parents=True, exist_ok=True)
    content = "# Proposal Outline\n\n"
    for i in range(1, count + 1):
        content += f"[Figure {i}: Placeholder]\n\n"
    (outline_dir / "proposal-outline.md").write_text(content)


@then(
    parsers.parse(
        "Phil sees {count:d} figures classified by type and generation method"
    ),
)
def verify_figures_classified(count):
    """Verify figures classified in skeleton journey."""
    pytest.skip("Awaiting VisualAssetService implementation")


@when("Phil generates and approves all figures")
def generate_and_approve_all():
    """Generate and approve all figures in skeleton journey."""
    pytest.skip("Awaiting VisualAssetService implementation")


@then("Phil sees a cross-reference log with all references valid")
def verify_cross_refs_valid():
    """Verify cross-references valid in skeleton journey."""
    pytest.skip("Awaiting VisualAssetService implementation")


@when(
    parsers.parse('Phil formats the proposal selecting "{medium}"'),
)
def format_proposal_skeleton(medium):
    """Format proposal in skeleton journey."""
    pytest.skip("Awaiting FormattingService implementation")


@then("Phil sees formatting applied with page count within limits")
def verify_formatting_with_pages():
    """Verify formatting applied in skeleton journey."""
    pytest.skip("Awaiting FormattingService implementation")


@then("Phil sees a jargon audit with any undefined acronyms flagged")
def verify_jargon_audit():
    """Verify jargon audit in skeleton journey."""
    pytest.skip("Awaiting FormattingService implementation")


@then(
    "Phil sees Volume 1 (Technical), Volume 2 (Cost), and Volume 3 (Company Info)"
)
def verify_three_volumes():
    """Verify three volumes created in skeleton journey."""
    pytest.skip("Awaiting AssemblyService implementation")


@then("Phil reviews the assembled package at the human checkpoint")
def verify_assembly_checkpoint():
    """Verify human checkpoint in skeleton journey."""
    pytest.skip("Awaiting AssemblyService implementation")


@then("Phil sees evaluation scores with rationales")
def verify_scores_with_rationales():
    """Verify evaluation scores in skeleton journey."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("Phil sees red team objections tagged by severity")
def verify_red_team_tagged():
    """Verify red team objections in skeleton journey."""
    pytest.skip("Awaiting FinalReviewService implementation")


@when("Phil addresses HIGH issues and signs off")
def address_and_signoff():
    """Address issues and sign off in skeleton journey."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("Phil sees all files correctly named and sized for the portal")
def verify_files_named_sized():
    """Verify files are named and sized correctly in skeleton journey."""
    pytest.skip("Awaiting SubmissionService implementation")


@when("Phil confirms submission and enters the confirmation number")
def confirm_and_enter_number():
    """Confirm submission and enter number in skeleton journey."""
    pytest.skip("Awaiting SubmissionService implementation")


@then("an immutable archive is created and artifacts are read-only")
def verify_immutable_archive():
    """Verify immutable archive in skeleton journey."""
    pytest.skip("Awaiting SubmissionService implementation")


@when("Phil records the outcome and ingests the debrief")
def record_outcome_ingest():
    """Record outcome and ingest debrief in skeleton journey."""
    pytest.skip("Awaiting OutcomeService + DebriefService implementation")


@then("Phil sees critiques mapped to proposal sections")
def verify_critiques_mapped():
    """Verify critiques mapped in skeleton journey."""
    pytest.skip("Awaiting DebriefService implementation")


@then("Phil sees pattern analysis across the corpus")
def verify_pattern_analysis():
    """Verify pattern analysis in skeleton journey."""
    pytest.skip("Awaiting OutcomeService implementation")
