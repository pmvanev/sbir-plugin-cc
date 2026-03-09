"""Step definitions for Wave 2 research orchestration.

Invokes through: ResearchService (driving port -- to be created in C2).
Does NOT import internal research generators, patent scanners, or market
analysis components directly.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/research.feature")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def research_context() -> dict[str, Any]:
    """Mutable context to pass data between steps."""
    return {}


# --- Given steps ---


@given("a strategy brief exists with technical approach and TRL positioning")
def strategy_brief_with_approach(research_context):
    """Strategy brief has been generated with approach and TRL data."""
    research_context["strategy_brief_available"] = True
    # Will wire to real StrategyBrief domain object when ResearchService exists


@given("research findings have been generated for AF243-001")
def research_findings_exist(research_context):
    """Research findings have been generated via ResearchService."""
    research_context["findings_generated"] = True
    # Will invoke ResearchService.generate_findings() when implemented


@given("the strategy brief does not exist")
def no_strategy_brief(research_context):
    """Ensure no strategy brief is available."""
    research_context["strategy_brief_available"] = False


@given("no research findings have been generated")
def no_research_findings(research_context):
    """Ensure no research findings exist."""
    research_context["findings_generated"] = False


@given("TPOC data is not available")
def tpoc_data_unavailable(research_context):
    """TPOC data has not been ingested."""
    research_context["tpoc_available"] = False


@given("any completed research review")
def any_completed_research(research_context):
    """Precondition for property test -- any valid completed research."""
    research_context["findings_generated"] = True


# --- When steps ---


@when("the research orchestration generates findings")
def generate_research(research_context):
    """Invoke research generation through ResearchService driving port."""
    # TODO: Invoke ResearchService.generate_findings() when implemented
    pytest.skip("Awaiting ResearchService implementation")


@when("Phil reaches the research review checkpoint")
def reach_research_checkpoint(research_context):
    """Invoke research checkpoint through driving port."""
    pytest.skip("Awaiting ResearchService implementation")


@when("Phil approves the research review")
def approve_research(research_context):
    """Approve research through ResearchService driving port."""
    pytest.skip("Awaiting ResearchService implementation")


@when(
    parsers.parse('Phil provides research revision feedback "{feedback}"')
)
def revise_research(research_context, feedback):
    """Submit revision feedback through driving port."""
    research_context["revision_feedback"] = feedback
    pytest.skip("Awaiting ResearchService implementation")


@when("Phil attempts to generate research findings")
def attempt_generate_research(research_context):
    """Attempt research generation without prerequisites."""
    pytest.skip("Awaiting ResearchService implementation")


@when("Phil attempts to approve the research review")
def attempt_approve_research(research_context):
    """Attempt approval of nonexistent research."""
    pytest.skip("Awaiting ResearchService implementation")


@when("Phil attempts to revise research findings")
def attempt_revise_research(research_context):
    """Attempt revision of nonexistent research."""
    pytest.skip("Awaiting ResearchService implementation")


@when("no prior SBIR awards are found for the topic")
def no_prior_awards(research_context):
    """Prior award search returns no results."""
    research_context["prior_awards_found"] = False


@when("the research review is approved")
def research_approved_property(research_context):
    """Property test: research approval."""
    pytest.skip("Awaiting ResearchService implementation")


# --- Then steps ---


@then("Phil sees research findings covering technical landscape")
def verify_technical_landscape(research_context):
    """Verify technical landscape findings present."""
    pytest.skip("Awaiting ResearchService implementation")


@then("Phil sees research findings covering patent landscape")
def verify_patent_landscape(research_context):
    """Verify patent landscape findings present."""
    pytest.skip("Awaiting ResearchService implementation")


@then("Phil sees research findings covering prior award analysis")
def verify_prior_awards(research_context):
    """Verify prior award analysis present."""
    pytest.skip("Awaiting ResearchService implementation")


@then(
    "Phil sees research findings covering market research with TAM, SAM, and SOM"
)
def verify_market_research(research_context):
    """Verify market research with sizing present."""
    pytest.skip("Awaiting ResearchService implementation")


@then("Phil sees research findings covering commercialization pathway")
def verify_commercialization(research_context):
    """Verify commercialization pathway present."""
    pytest.skip("Awaiting ResearchService implementation")


@then("Phil sees research findings covering refined TRL positioning")
def verify_trl_refinement(research_context):
    """Verify TRL refinement present."""
    pytest.skip("Awaiting ResearchService implementation")


@then("Phil sees the six research artifacts listed for review")
def verify_six_artifacts(research_context):
    """Verify all six research artifacts presented."""
    pytest.skip("Awaiting ResearchService implementation")


@then("Phil can approve, revise, or skip the research review")
def verify_checkpoint_options(research_context):
    """Verify checkpoint presents approve/revise/skip options."""
    pytest.skip("Awaiting ResearchService implementation")


@then("the approval is recorded in the proposal state")
def verify_research_approval(research_context):
    """Verify approval recorded in state."""
    pytest.skip("Awaiting ResearchService implementation")


@then("Wave 3 is unlocked")
def verify_wave_3_unlocked(research_context):
    """Verify Wave 3 status changed."""
    pytest.skip("Awaiting ResearchService implementation")


@then("the research findings are regenerated incorporating the feedback")
def verify_research_revision(research_context):
    """Verify research regenerated with feedback."""
    pytest.skip("Awaiting ResearchService implementation")


@then("Phil reviews the revised research findings")
def verify_revised_research(research_context):
    """Verify revised research presented for review."""
    pytest.skip("Awaiting ResearchService implementation")


@then(parsers.parse('Phil sees "{message}"'))
def verify_research_message(research_context, message):
    """Verify user-facing research message."""
    error = research_context.get("error", "")
    assert message.lower() in error.lower(), (
        f"Expected '{message}' in error message, got: '{error}'"
    )


@then("Phil sees guidance to complete Wave 1 strategy alignment first")
def verify_strategy_guidance(research_context):
    """Verify guidance points to strategy alignment."""
    pytest.skip("Awaiting ResearchService implementation")


@then("Phil sees guidance to generate research first")
def verify_generate_research_guidance(research_context):
    """Verify guidance to generate research."""
    pytest.skip("Awaiting ResearchService implementation")


@then('the research findings note "TPOC data not available"')
def verify_tpoc_absent_in_research(research_context):
    """Verify TPOC absence noted in research."""
    pytest.skip("Awaiting ResearchService implementation")


@then(
    "the findings are generated from strategy brief and solicitation data alone"
)
def verify_research_without_tpoc(research_context):
    """Verify research generated without TPOC data."""
    pytest.skip("Awaiting ResearchService implementation")


@then(
    parsers.parse(
        'the prior award analysis notes "{message}"'
    )
)
def verify_no_prior_awards_note(research_context, message):
    """Verify prior award absence noted."""
    pytest.skip("Awaiting ResearchService implementation")


@then("the research continues with adjacent topic analysis")
def verify_adjacent_analysis(research_context):
    """Verify research broadens to adjacent topics."""
    pytest.skip("Awaiting ResearchService implementation")


@then("the approval timestamp is always recorded in the state")
def verify_approval_timestamp_property(research_context):
    """Property: approval always records timestamp."""
    pytest.skip("Awaiting ResearchService implementation")
