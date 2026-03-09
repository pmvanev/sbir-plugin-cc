"""Step definitions for Wave 4 drafting, review, and iteration.

Invokes through: DraftService, ReviewService (driving ports -- to be created
in C2). Does NOT import internal section writers, jargon auditors, or
cross-reference checkers directly.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/drafting.feature")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def drafting_context() -> dict[str, Any]:
    """Mutable context to pass data between steps."""
    return {}


# --- Given steps ---


@given(
    "an approved outline with a technical approach section and 8-page budget"
)
def outline_with_tech_approach(drafting_context):
    """Approved outline includes technical approach section."""
    drafting_context["outline_available"] = True
    drafting_context["tech_approach_pages"] = 8


@given("an approved outline with a statement of work section")
def outline_with_sow(drafting_context):
    """Approved outline includes SOW section."""
    drafting_context["outline_available"] = True
    drafting_context["sow_available"] = True


@given("an approved outline covering all required proposal sections")
def outline_with_all_sections(drafting_context):
    """Approved outline covers all nine required sections."""
    drafting_context["outline_available"] = True
    drafting_context["all_sections"] = True


@given("a draft exists for the technical approach section")
def tech_approach_drafted(drafting_context):
    """Technical approach section has been drafted."""
    drafting_context["tech_approach_drafted"] = True


@given(
    'debrief history includes "Insufficient TRL advancement methodology" '
    "as a known weakness"
)
def debrief_weakness_exists(drafting_context):
    """Debrief corpus contains known weakness pattern."""
    drafting_context["debrief_weakness"] = (
        "Insufficient TRL advancement methodology"
    )


@given("all proposal sections have been drafted")
def all_sections_drafted(drafting_context):
    """All nine sections have drafts."""
    drafting_context["all_drafted"] = True


@given("the technical approach section has review findings")
def tech_approach_has_findings(drafting_context):
    """Review produced findings for technical approach."""
    drafting_context["has_review_findings"] = True


@given("the technical approach was revised after first review")
def tech_approach_revised(drafting_context):
    """Technical approach has been revised once."""
    drafting_context["revision_count"] = 1


@given("the technical approach has completed 2 review cycles")
def two_review_cycles(drafting_context):
    """Technical approach reviewed twice."""
    drafting_context["review_cycles"] = 2


@given("unresolved findings remain")
def unresolved_findings(drafting_context):
    """Some findings not addressed after 2 cycles."""
    drafting_context["unresolved_count"] = 2


@given("no proposal outline has been approved")
def no_outline_approved(drafting_context):
    """Ensure no outline approval."""
    drafting_context["outline_available"] = False


@given(
    'an approved outline that does not include an "executive summary" section'
)
def outline_without_exec_summary(drafting_context):
    """Outline does not have executive summary."""
    drafting_context["outline_available"] = True
    drafting_context["missing_section"] = "executive summary"


@given("no draft exists for the past performance section")
def no_past_performance_draft(drafting_context):
    """No draft for past performance."""
    drafting_context["past_performance_drafted"] = False


@given("the technical approach has an 8-page budget")
def tech_approach_budget(drafting_context):
    """Technical approach page budget is 8."""
    drafting_context["tech_approach_pages"] = 8


@given(
    "2 compliance items mapped to technical approach are not addressed "
    "in the draft"
)
def unaddressed_compliance_items(drafting_context):
    """Draft misses 2 compliance items."""
    drafting_context["unaddressed_items"] = 2


@given("no debrief history exists in the corpus")
def no_debrief_history(drafting_context):
    """Empty debrief corpus."""
    drafting_context["debrief_available"] = False


@given('a draft uses "CONOPS" 7 times without definition')
def undefined_acronym(drafting_context):
    """Draft has undefined acronym."""
    drafting_context["undefined_acronyms"] = ["CONOPS"]


@given(
    'a draft references "Figure 3" but only Figures 1 and 2 exist'
)
def missing_figure_reference(drafting_context):
    """Draft cites nonexistent figure."""
    drafting_context["missing_figures"] = ["Figure 3"]


@given("any valid section draft produced from the approved outline")
def any_valid_draft(drafting_context):
    """Property test precondition."""
    drafting_context["outline_available"] = True


@given("any section review")
def any_section_review(drafting_context):
    """Property test precondition."""
    drafting_context["review_available"] = True


@given(
    "the outline includes a technical approach section with 8-page budget"
)
def outline_tech_approach_8_pages(drafting_context):
    """Walking skeleton: outline with tech approach."""
    drafting_context["tech_approach_pages"] = 8


# --- When steps ---


@when("Phil requests a draft of the technical approach section")
def draft_tech_approach(drafting_context):
    """Invoke section drafting through DraftService driving port."""
    pytest.skip("Awaiting DraftService implementation")


@when("Phil requests a draft of the statement of work section")
def draft_sow(drafting_context):
    """Invoke SOW drafting through driving port."""
    pytest.skip("Awaiting DraftService implementation")


@when("Phil drafts each section in the recommended order")
def draft_all_sections(drafting_context):
    """Invoke sequential drafting through driving port."""
    pytest.skip("Awaiting DraftService implementation")


@when("the section is submitted for review")
def submit_for_review(drafting_context):
    """Invoke section review through ReviewService driving port."""
    pytest.skip("Awaiting ReviewService implementation")


@when("the full draft review is requested")
def request_full_review(drafting_context):
    """Invoke full draft review through driving port."""
    pytest.skip("Awaiting ReviewService implementation")


@when("Phil requests iteration on the technical approach section")
def iterate_tech_approach(drafting_context):
    """Invoke iteration through DraftService driving port."""
    pytest.skip("Awaiting DraftService implementation")


@when("the revised section is re-reviewed")
def re_review_section(drafting_context):
    """Invoke re-review through driving port."""
    pytest.skip("Awaiting ReviewService implementation")


@when("a third review cycle is requested")
def request_third_review(drafting_context):
    """Invoke third review cycle."""
    pytest.skip("Awaiting ReviewService implementation")


@when("Phil attempts to draft a section")
def attempt_draft_without_outline(drafting_context):
    """Attempt drafting without outline."""
    pytest.skip("Awaiting DraftService implementation")


@when(
    parsers.parse(
        'Phil attempts to draft an "{section_name}" section'
    )
)
def attempt_draft_missing_section(drafting_context, section_name):
    """Attempt drafting a section not in outline."""
    drafting_context["attempted_section"] = section_name
    pytest.skip("Awaiting DraftService implementation")


@when("Phil requests review of the past performance section")
def request_review_no_draft(drafting_context):
    """Attempt review of un-drafted section."""
    pytest.skip("Awaiting ReviewService implementation")


@when("Phil's draft reaches approximately 5200 words")
def draft_over_budget(drafting_context):
    """Draft exceeds page budget."""
    drafting_context["word_count"] = 5200
    pytest.skip("Awaiting DraftService implementation")


@when("the compliance check runs against the section")
def check_section_compliance(drafting_context):
    """Run compliance check against drafted section."""
    pytest.skip("Awaiting DraftService implementation")


@when("the technical approach section is submitted for review")
def submit_tech_for_review(drafting_context):
    """Submit technical approach for review."""
    pytest.skip("Awaiting ReviewService implementation")


@when("the draft is validated")
def validate_draft(drafting_context):
    """Property: validate draft compliance tracing."""
    pytest.skip("Awaiting DraftService implementation")


@when("findings are produced")
def produce_findings(drafting_context):
    """Property: findings produced from review."""
    pytest.skip("Awaiting ReviewService implementation")


# --- Then steps ---


@then("Phil sees a draft addressing the mapped compliance items")
def verify_compliance_addressed(drafting_context):
    """Verify draft addresses compliance items."""
    pytest.skip("Awaiting DraftService implementation")


@then("the draft references discriminators from the discrimination table")
def verify_discriminator_references(drafting_context):
    """Verify draft uses discrimination table."""
    pytest.skip("Awaiting DraftService implementation")


@then("the draft word count is reported against the page budget")
def verify_word_count_reported(drafting_context):
    """Verify word count tracking."""
    pytest.skip("Awaiting DraftService implementation")


@then("Phil sees a draft with milestone-based deliverables")
def verify_milestone_deliverables(drafting_context):
    """Verify SOW has milestones."""
    pytest.skip("Awaiting DraftService implementation")


@then("the draft uses active voice and future tense")
def verify_contractual_language(drafting_context):
    """Verify SOW language style."""
    pytest.skip("Awaiting DraftService implementation")


@then(parsers.parse("Phil sees a draft for {section_name}"))
def verify_section_draft(drafting_context, section_name):
    """Verify a specific section was drafted."""
    pytest.skip("Awaiting DraftService implementation")


@then("Phil sees a scorecard with strengths and weaknesses")
def verify_scorecard(drafting_context):
    """Verify scorecard produced."""
    pytest.skip("Awaiting ReviewService implementation")


@then(
    "each finding includes location, severity, and specific suggestion"
)
def verify_finding_structure(drafting_context):
    """Verify findings are actionable."""
    pytest.skip("Awaiting ReviewService implementation")


@then("the scorecard is written to the review artifacts")
def verify_scorecard_written(drafting_context):
    """Verify scorecard persisted."""
    pytest.skip("Awaiting ReviewService implementation")


@then(
    "the review flags any matching weakness patterns from debrief history"
)
def verify_debrief_pattern_match(drafting_context):
    """Verify debrief patterns checked."""
    pytest.skip("Awaiting ReviewService implementation")


@then("the compliance matrix shows all items addressed")
def verify_full_compliance(drafting_context):
    """Verify full compliance coverage."""
    pytest.skip("Awaiting ReviewService implementation")


@then("a full scorecard is produced across all sections")
def verify_full_scorecard(drafting_context):
    """Verify full proposal scorecard."""
    pytest.skip("Awaiting ReviewService implementation")


@then("Phil can approve the draft to proceed to formatting")
def verify_approve_option(drafting_context):
    """Verify approval option at checkpoint."""
    pytest.skip("Awaiting ReviewService implementation")


@then("the writer addresses the review findings")
def verify_findings_addressed(drafting_context):
    """Verify findings addressed in iteration."""
    pytest.skip("Awaiting DraftService implementation")


@then("unchanged content is preserved")
def verify_content_preserved(drafting_context):
    """Verify approved content preserved during revision."""
    pytest.skip("Awaiting DraftService implementation")


@then("the revised section is submitted for re-review")
def verify_resubmitted(drafting_context):
    """Verify revised section submitted for review."""
    pytest.skip("Awaiting DraftService implementation")


@then(
    "each prior finding shows whether it was addressed or remains open"
)
def verify_finding_tracking(drafting_context):
    """Verify finding resolution tracking."""
    pytest.skip("Awaiting ReviewService implementation")


@then("updated ratings reflect the improvements")
def verify_updated_ratings(drafting_context):
    """Verify ratings updated after revision."""
    pytest.skip("Awaiting ReviewService implementation")


@then("Phil sees unresolved findings escalated for human decision")
def verify_escalation(drafting_context):
    """Verify escalation after max review cycles."""
    pytest.skip("Awaiting ReviewService implementation")


@then("Phil can accept the section as-is or provide final revisions")
def verify_escalation_options(drafting_context):
    """Verify human decision options at escalation."""
    pytest.skip("Awaiting ReviewService implementation")


@then(parsers.parse('Phil sees "{message}"'))
def verify_drafting_message(drafting_context, message):
    """Verify user-facing message."""
    error = drafting_context.get("error", "")
    assert message.lower() in error.lower(), (
        f"Expected '{message}' in error message, got: '{error}'"
    )


@then("Phil sees guidance to complete Wave 3 outline approval first")
def verify_outline_guidance(drafting_context):
    """Verify guidance points to outline approval."""
    pytest.skip("Awaiting DraftService implementation")


@then("Phil sees guidance to update the outline first")
def verify_update_outline_guidance(drafting_context):
    """Verify guidance to update outline."""
    pytest.skip("Awaiting DraftService implementation")


@then("Phil sees guidance to draft the section first")
def verify_draft_section_guidance(drafting_context):
    """Verify guidance to draft section."""
    pytest.skip("Awaiting ReviewService implementation")


@then("Phil sees a warning that the section exceeds its page budget")
def verify_budget_warning(drafting_context):
    """Verify page budget warning."""
    pytest.skip("Awaiting DraftService implementation")


@then("Phil sees suggestions to cut content or reallocate pages")
def verify_budget_suggestions(drafting_context):
    """Verify budget reduction suggestions."""
    pytest.skip("Awaiting DraftService implementation")


@then(
    parsers.parse(
        'Phil sees "{count:d} compliance items not addressed in technical approach"'
    )
)
def verify_unaddressed_items(drafting_context, count):
    """Verify unaddressed compliance items flagged."""
    pytest.skip("Awaiting DraftService implementation")


@then("the unaddressed items are listed by ID")
def verify_items_listed(drafting_context):
    """Verify unaddressed items enumerated."""
    pytest.skip("Awaiting DraftService implementation")


@then(
    'the review notes "No debrief history available for pattern matching"'
)
def verify_no_debrief_note(drafting_context):
    """Verify absence of debrief noted."""
    pytest.skip("Awaiting ReviewService implementation")


@then("the review proceeds using evaluation criteria alone")
def verify_criteria_only_review(drafting_context):
    """Verify review without debrief patterns."""
    pytest.skip("Awaiting ReviewService implementation")


@then(
    parsers.parse('the review flags "{message}"')
)
def verify_review_flag(drafting_context, message):
    """Verify specific review finding."""
    pytest.skip("Awaiting ReviewService implementation")


@then("the finding suggests defining on first use")
def verify_acronym_suggestion(drafting_context):
    """Verify acronym definition suggestion."""
    pytest.skip("Awaiting ReviewService implementation")


@then(
    "the finding suggests creating the figure or updating the reference"
)
def verify_figure_suggestion(drafting_context):
    """Verify figure reference fix suggestion."""
    pytest.skip("Awaiting ReviewService implementation")


@then("the section addresses at least one compliance item")
def verify_compliance_tracing_property(drafting_context):
    """Property: every section traces to compliance."""
    pytest.skip("Awaiting DraftService implementation")


@then("every finding includes a location and severity level")
def verify_finding_completeness_property(drafting_context):
    """Property: findings are complete."""
    pytest.skip("Awaiting ReviewService implementation")


@then("Phil sees a draft addressing compliance items with word count")
def verify_draft_with_count(drafting_context):
    """Walking skeleton: draft with compliance and word count."""
    pytest.skip("Awaiting DraftService implementation")


@then("Phil sees a scorecard with actionable findings")
def verify_actionable_scorecard(drafting_context):
    """Walking skeleton: scorecard is actionable."""
    pytest.skip("Awaiting ReviewService implementation")


@then(
    "the revised section preserves approved content and addresses findings"
)
def verify_revision_quality(drafting_context):
    """Walking skeleton: revision quality."""
    pytest.skip("Awaiting DraftService implementation")
