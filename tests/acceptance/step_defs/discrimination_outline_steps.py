"""Step definitions for Wave 3 discrimination table and proposal outline.

Invokes through: DiscriminationService, OutlineService (driving ports -- to be
created in C2). Does NOT import internal discriminator builders or outline
generators directly.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/discrimination_outline.feature")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def discrim_context() -> dict[str, Any]:
    """Mutable context to pass data between steps."""
    return {}


# --- Given steps ---


@given("a strategy brief exists with key discriminators")
def strategy_with_discriminators(discrim_context):
    """Strategy brief contains discriminator candidates."""
    discrim_context["strategy_available"] = True


@given("research findings include competitor landscape and prior art")
def research_with_competitors(discrim_context):
    """Research findings have competitor and prior art data."""
    discrim_context["research_available"] = True


@given("TPOC answers revealed the agency's failed prior approach")
def tpoc_revealed_failure(discrim_context):
    """TPOC data includes insight about agency's prior failed approach."""
    discrim_context["tpoc_failure_insight"] = True


@given("a discrimination table has been generated for AF243-001")
def discrimination_generated(discrim_context):
    """Discrimination table has been generated."""
    discrim_context["discrimination_generated"] = True


@given("a compliance matrix exists with 47 items")
def matrix_with_47_items(discrim_context):
    """Compliance matrix with 47 items available."""
    discrim_context["matrix_item_count"] = 47


@given("a discrimination table has been approved")
def discrimination_approved(discrim_context):
    """Discrimination table has been approved."""
    discrim_context["discrimination_approved"] = True


@given(
    parsers.parse(
        "the solicitation allows {pages:d} pages for the technical volume"
    )
)
def solicitation_page_limit(discrim_context, pages):
    """Set solicitation page limit."""
    discrim_context["page_limit"] = pages


@given("a proposal outline has been generated for AF243-001")
def outline_generated(discrim_context):
    """Proposal outline has been generated."""
    discrim_context["outline_generated"] = True


@given("no discrimination table has been approved")
def no_discrimination(discrim_context):
    """Ensure no discrimination table is approved."""
    discrim_context["discrimination_approved"] = False


@given("no proposal outline has been generated")
def no_outline(discrim_context):
    """Ensure no outline exists."""
    discrim_context["outline_generated"] = False


@given("no discrimination table has been generated")
def no_discrimination_generated(discrim_context):
    """Ensure no discrimination table exists."""
    discrim_context["discrimination_generated"] = False


@given(
    parsers.parse("the outline covers only {count:d} of those items")
)
def partial_outline_coverage(discrim_context, count):
    """Outline covers only some compliance items."""
    discrim_context["outline_covered_items"] = count


@given("any valid compliance matrix and approved discrimination table")
def any_valid_matrix_and_discrimination(discrim_context):
    """Property test precondition."""
    discrim_context["discrimination_approved"] = True
    discrim_context["matrix_item_count"] = 47


@given("any valid solicitation page limit")
def any_valid_page_limit(discrim_context):
    """Property test precondition."""
    discrim_context["page_limit"] = 25


# --- When steps ---


@when("the discrimination table is generated")
def generate_discrimination(discrim_context):
    """Invoke discrimination table generation through driving port."""
    pytest.skip("Awaiting DiscriminationService implementation")


@when(
    parsers.parse(
        'Phil provides discrimination feedback "{feedback}"'
    )
)
def revise_discrimination(discrim_context, feedback):
    """Submit discrimination revision feedback."""
    discrim_context["revision_feedback"] = feedback
    pytest.skip("Awaiting DiscriminationService implementation")


@when("the proposal outline is generated")
def generate_outline(discrim_context):
    """Invoke outline generation through driving port."""
    pytest.skip("Awaiting OutlineService implementation")


@when("Phil approves the proposal outline")
def approve_outline(discrim_context):
    """Approve outline through driving port."""
    pytest.skip("Awaiting OutlineService implementation")


@when(
    parsers.parse('Phil provides outline feedback "{feedback}"')
)
def revise_outline(discrim_context, feedback):
    """Submit outline revision feedback."""
    discrim_context["revision_feedback"] = feedback
    pytest.skip("Awaiting OutlineService implementation")


@when("Phil attempts to generate the discrimination table")
def attempt_generate_discrimination(discrim_context):
    """Attempt discrimination without prerequisites."""
    pytest.skip("Awaiting DiscriminationService implementation")


@when("Phil attempts to generate the proposal outline")
def attempt_generate_outline(discrim_context):
    """Attempt outline without prerequisites."""
    pytest.skip("Awaiting OutlineService implementation")


@when("Phil attempts to approve the proposal outline")
def attempt_approve_outline(discrim_context):
    """Attempt approval of nonexistent outline."""
    pytest.skip("Awaiting OutlineService implementation")


@when("Phil attempts to approve the discrimination table")
def attempt_approve_discrimination(discrim_context):
    """Attempt approval of nonexistent discrimination table."""
    pytest.skip("Awaiting DiscriminationService implementation")


@when("the outline mapping is validated")
def validate_outline_mapping(discrim_context):
    """Validate outline covers all compliance items."""
    pytest.skip("Awaiting OutlineService implementation")


# --- Then steps ---


@then("Phil sees discriminators covering company strengths versus competitors")
def verify_company_discriminators(discrim_context):
    """Verify company discriminators present."""
    pytest.skip("Awaiting DiscriminationService implementation")


@then(
    "Phil sees discriminators covering technical approach versus prior art"
)
def verify_technical_discriminators(discrim_context):
    """Verify technical discriminators present."""
    pytest.skip("Awaiting DiscriminationService implementation")


@then(
    "Phil sees discriminators covering team qualifications and past performance"
)
def verify_team_discriminators(discrim_context):
    """Verify team discriminators present."""
    pytest.skip("Awaiting DiscriminationService implementation")


@then("each discriminator cites supporting evidence")
def verify_evidence_citations(discrim_context):
    """Verify evidence cited for each discriminator."""
    pytest.skip("Awaiting DiscriminationService implementation")


@then(
    "the technical discriminators explicitly contrast with the failed prior approach"
)
def verify_tpoc_contrast(discrim_context):
    """Verify TPOC failure insight used in discrimination."""
    pytest.skip("Awaiting DiscriminationService implementation")


@then("the TPOC insight is cited as evidence")
def verify_tpoc_evidence_cited(discrim_context):
    """Verify TPOC insight cited."""
    pytest.skip("Awaiting DiscriminationService implementation")


@then("the discrimination table is revised incorporating the feedback")
def verify_discrimination_revised(discrim_context):
    """Verify discrimination table revised."""
    pytest.skip("Awaiting DiscriminationService implementation")


@then("Phil reviews the revised discrimination table")
def verify_revised_discrimination(discrim_context):
    """Verify revised table presented."""
    pytest.skip("Awaiting DiscriminationService implementation")


@then("every compliance item is mapped to a proposal section")
def verify_all_items_mapped(discrim_context):
    """Verify compliance coverage in outline."""
    pytest.skip("Awaiting OutlineService implementation")


@then("Phil sees page budgets assigned to each section")
def verify_page_budgets(discrim_context):
    """Verify page budgets present."""
    pytest.skip("Awaiting OutlineService implementation")


@then("Phil sees figure and table placeholders defined")
def verify_placeholders(discrim_context):
    """Verify figure/table placeholders."""
    pytest.skip("Awaiting OutlineService implementation")


@then("Phil sees thesis statements for each section")
def verify_thesis_statements(discrim_context):
    """Verify thesis statements present."""
    pytest.skip("Awaiting OutlineService implementation")


@then(
    parsers.parse(
        "the section page budgets total to {pages:d} pages or fewer"
    )
)
def verify_page_budget_total(discrim_context, pages):
    """Verify page budgets sum correctly."""
    pytest.skip("Awaiting OutlineService implementation")


@then("the approval is recorded in the proposal state")
def verify_outline_approval(discrim_context):
    """Verify outline approval recorded."""
    pytest.skip("Awaiting OutlineService implementation")


@then("Wave 4 is unlocked")
def verify_wave_4_unlocked(discrim_context):
    """Verify Wave 4 status changed."""
    pytest.skip("Awaiting OutlineService implementation")


@then("the proposal outline is revised incorporating the feedback")
def verify_outline_revised(discrim_context):
    """Verify outline revised."""
    pytest.skip("Awaiting OutlineService implementation")


@then("Phil reviews the revised outline")
def verify_revised_outline(discrim_context):
    """Verify revised outline presented."""
    pytest.skip("Awaiting OutlineService implementation")


@then(parsers.parse('Phil sees "{message}"'))
def verify_discrim_message(discrim_context, message):
    """Verify user-facing message."""
    error = discrim_context.get("error", "")
    assert message.lower() in error.lower(), (
        f"Expected '{message}' in error message, got: '{error}'"
    )


@then("Phil sees guidance to complete Wave 2 research review first")
def verify_research_guidance(discrim_context):
    """Verify guidance points to research review."""
    pytest.skip("Awaiting DiscriminationService implementation")


@then("Phil sees guidance to complete the discrimination review first")
def verify_discrimination_guidance(discrim_context):
    """Verify guidance points to discrimination review."""
    pytest.skip("Awaiting OutlineService implementation")


@then("Phil sees guidance to generate one first")
def verify_generate_guidance(discrim_context):
    """Verify guidance to generate."""
    pytest.skip("Awaiting implementation")


@then(
    parsers.parse(
        "Phil sees a warning that {count:d} compliance items are not mapped to any section"
    )
)
def verify_unmapped_warning(discrim_context, count):
    """Verify unmapped items warning."""
    pytest.skip("Awaiting OutlineService implementation")


@then("the unmapped items are listed by ID")
def verify_unmapped_listed(discrim_context):
    """Verify unmapped items enumerated."""
    pytest.skip("Awaiting OutlineService implementation")


@then("every compliance item is mapped to at least one section")
def verify_full_mapping_property(discrim_context):
    """Property: all items mapped."""
    pytest.skip("Awaiting OutlineService implementation")


@then(
    "the sum of all section page budgets does not exceed the solicitation limit"
)
def verify_budget_limit_property(discrim_context):
    """Property: budgets within limit."""
    pytest.skip("Awaiting OutlineService implementation")
