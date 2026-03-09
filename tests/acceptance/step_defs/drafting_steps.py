"""Step definitions for Wave 4 drafting, review, and iteration.

Invokes through: DraftService (driving port).
Does NOT import internal section writers, jargon auditors, or
cross-reference checkers directly.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.draft import SectionDraft
from pes.domain.draft_service import (
    ApprovedOutlineRequiredError,
    DraftResult,
    DraftService,
    SectionNotInOutlineError,
)
from pes.domain.outline import OutlineSection, ProposalOutline
from pes.domain.review import ReviewFinding, ReviewScorecard
from pes.domain.review_service import (
    EscalationResult,
    FullReviewResult,
    NoDraftExistsError,
    ReviewResult,
    ReviewService,
)
from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/drafting.feature")


# ---------------------------------------------------------------------------
# Fake driven port (SectionDrafter) for acceptance tests
# ---------------------------------------------------------------------------


class FakeSectionDrafter:
    """Fake driven port producing deterministic section drafts."""

    def __init__(self, *, word_count: int = 500) -> None:
        self._word_count = word_count

    def draft(
        self,
        section: OutlineSection,
        *,
        iteration: int = 1,
    ) -> SectionDraft:
        # Build content with requested word count
        words = ["word"] * self._word_count
        content = " ".join(words)
        return SectionDraft(
            section_id=section.section_id,
            content=content,
            compliance_item_ids=section.compliance_item_ids,
            iteration=iteration,
        )


class FakeDraftReviewer:
    """Fake driven port producing deterministic review scorecards."""

    def __init__(
        self,
        *,
        findings: list[ReviewFinding] | None = None,
        strengths: list[str] | None = None,
        weaknesses: list[str] | None = None,
    ) -> None:
        self._findings = findings or [
            ReviewFinding(
                location="section-1.para-2",
                severity="major",
                suggestion="Strengthen TRL advancement methodology",
            ),
            ReviewFinding(
                location="section-1.para-5",
                severity="minor",
                suggestion="Add quantitative metrics",
            ),
        ]
        self._strengths = strengths or ["Clear technical narrative"]
        self._weaknesses = weaknesses or ["Weak risk mitigation"]

    def review(
        self,
        draft: SectionDraft,
        *,
        prior_findings: list[ReviewFinding] | None = None,
    ) -> ReviewScorecard:
        if prior_findings:
            # On re-review, resolve the first finding, keep rest
            return ReviewScorecard(
                findings=self._findings[1:],
                strengths=[*self._strengths, "Addressed prior findings"],
                weaknesses=[],
            )
        return ReviewScorecard(
            findings=list(self._findings),
            strengths=list(self._strengths),
            weaknesses=list(self._weaknesses),
        )


class FakeFullDraftReviewer:
    """Fake reviewer for full draft review -- all compliance covered."""

    def review(
        self,
        draft: SectionDraft,
        *,
        prior_findings: list[ReviewFinding] | None = None,
    ) -> ReviewScorecard:
        return ReviewScorecard(
            findings=[],
            strengths=["All compliance items addressed"],
            weaknesses=[],
        )


class PartialComplianceDrafter:
    """Fake drafter that omits some compliance items from the draft."""

    def __init__(self, *, omit_ids: list[str]) -> None:
        self._omit_ids = omit_ids

    def draft(
        self,
        section: OutlineSection,
        *,
        iteration: int = 1,
    ) -> SectionDraft:
        addressed = [cid for cid in section.compliance_item_ids if cid not in self._omit_ids]
        content = "This section addresses compliance items " + ", ".join(addressed)
        return SectionDraft(
            section_id=section.section_id,
            content=content,
            compliance_item_ids=addressed,
            iteration=iteration,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_approved_outline(
    *,
    sections: list[OutlineSection] | None = None,
) -> ProposalOutline:
    """Build an approved outline with default sections."""
    if sections is None:
        sections = [
            OutlineSection(
                section_id="technical-approach",
                title="Technical Approach",
                compliance_item_ids=["CI-001", "CI-002", "CI-003"],
                page_budget=8.0,
                figure_placeholders=["fig-1"],
                thesis_statement="Novel approach to beam-steering",
            ),
            OutlineSection(
                section_id="statement-of-work",
                title="Statement of Work",
                compliance_item_ids=["CI-004", "CI-005"],
                page_budget=4.0,
                figure_placeholders=[],
                thesis_statement="Milestone-based deliverables",
            ),
        ]
    return ProposalOutline(sections=sections)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def drafting_context() -> dict[str, Any]:
    """Mutable context to pass data between steps."""
    return {}


# --- Given steps (Background) ---


@given("Phil has an active proposal with an approved proposal outline")
def proposal_with_approved_outline(drafting_context):
    """Background: proposal has an approved outline ready for Wave 4."""
    drafting_context["proposal_active"] = True
    drafting_context["outline_approved"] = True


# --- Given steps ---


@given(
    "an approved outline with a technical approach section and 8-page budget"
)
def outline_with_tech_approach(drafting_context):
    """Approved outline includes technical approach section."""
    drafting_context["outline"] = _make_approved_outline()
    drafting_context["outline_available"] = True
    drafting_context["tech_approach_pages"] = 8


@given("an approved outline with a statement of work section")
def outline_with_sow(drafting_context):
    """Approved outline includes SOW section."""
    drafting_context["outline"] = _make_approved_outline()
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
    outline = _make_approved_outline()
    drafter = FakeSectionDrafter(word_count=500)
    service = DraftService(section_drafter=drafter)
    result = service.draft_section(
        outline=outline,
        section_id="technical-approach",
    )
    drafting_context["outline"] = outline
    drafting_context["draft_result"] = result
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
    """Technical approach has been revised once -- produce a draft for re-review."""
    outline = _make_approved_outline()
    drafter = FakeSectionDrafter(word_count=500)
    service = DraftService(section_drafter=drafter)
    result = service.draft_section(outline=outline, section_id="technical-approach")
    drafting_context["outline"] = outline
    drafting_context["draft_result"] = result
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
    drafting_context["outline"] = None


@given(
    'an approved outline that does not include an "executive summary" section'
)
def outline_without_exec_summary(drafting_context):
    """Outline does not have executive summary."""
    drafting_context["outline"] = _make_approved_outline()
    drafting_context["outline_available"] = True
    drafting_context["missing_section"] = "executive summary"


@given("no draft exists for the past performance section")
def no_past_performance_draft(drafting_context):
    """No draft for past performance."""
    drafting_context["past_performance_drafted"] = False


@given("the technical approach has an 8-page budget")
def tech_approach_budget(drafting_context):
    """Technical approach page budget is 8."""
    outline = _make_approved_outline()
    drafting_context["outline"] = outline
    drafting_context["tech_approach_pages"] = 8


@given(
    "2 compliance items mapped to technical approach are not addressed "
    "in the draft"
)
def unaddressed_compliance_items(drafting_context):
    """Draft misses 2 compliance items."""
    drafting_context["unaddressed_items"] = 2
    drafting_context["omit_ids"] = ["CI-002", "CI-003"]


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
    draft_result: DraftResult = drafting_context["draft_result"]
    reviewer = FakeDraftReviewer()
    service = ReviewService(draft_reviewer=reviewer)
    review_result = service.review_section(
        draft=draft_result.draft,
        review_round=1,
    )
    drafting_context["review_result"] = review_result


@when("the full draft review is requested")
def request_full_review(drafting_context):
    """Invoke full draft review through ReviewService driving port."""
    outline = _make_approved_outline()
    reviewer = FakeFullDraftReviewer()
    drafter = FakeSectionDrafter(word_count=500)
    draft_service = DraftService(section_drafter=drafter)
    # Draft all sections
    drafts = []
    for section in outline.sections:
        result = draft_service.draft_section(
            outline=outline, section_id=section.section_id
        )
        drafts.append(result.draft)

    review_service = ReviewService(draft_reviewer=reviewer)
    full_result = review_service.full_draft_review(
        drafts=drafts,
        outline=outline,
    )
    drafting_context["full_review_result"] = full_result


@when("Phil requests iteration on the technical approach section")
def iterate_tech_approach(drafting_context):
    """Invoke iteration through DraftService driving port."""
    pytest.skip("Awaiting DraftService implementation")


@when("the revised section is re-reviewed")
def re_review_section(drafting_context):
    """Invoke re-review through ReviewService driving port."""
    draft_result: DraftResult = drafting_context["draft_result"]
    prior_findings = [
        ReviewFinding(
            location="section-1.para-2",
            severity="major",
            suggestion="Strengthen TRL advancement methodology",
        ),
        ReviewFinding(
            location="section-1.para-5",
            severity="minor",
            suggestion="Add quantitative metrics",
        ),
    ]
    reviewer = FakeDraftReviewer()
    service = ReviewService(draft_reviewer=reviewer)
    review_result = service.review_section(
        draft=draft_result.draft,
        review_round=2,
        prior_findings=prior_findings,
    )
    drafting_context["review_result"] = review_result


@when("a third review cycle is requested")
def request_third_review(drafting_context):
    """Invoke third review cycle -- expects escalation."""
    outline = _make_approved_outline()
    drafter = FakeSectionDrafter(word_count=500)
    draft_service = DraftService(section_drafter=drafter)
    draft_result = draft_service.draft_section(
        outline=outline, section_id="technical-approach"
    )
    unresolved = [
        ReviewFinding(
            location="section-1.para-2",
            severity="major",
            suggestion="Strengthen TRL advancement methodology",
        ),
        ReviewFinding(
            location="section-1.para-5",
            severity="minor",
            suggestion="Add quantitative metrics",
        ),
    ]
    reviewer = FakeDraftReviewer()
    service = ReviewService(draft_reviewer=reviewer)
    result = service.review_section(
        draft=draft_result.draft,
        review_round=3,
        prior_findings=unresolved,
    )
    drafting_context["review_result"] = result


@when("Phil attempts to draft a section")
def attempt_draft_without_outline(drafting_context):
    """Attempt drafting without outline -- expects ApprovedOutlineRequiredError."""
    drafter = FakeSectionDrafter()
    service = DraftService(section_drafter=drafter)
    try:
        service.draft_section(outline=None, section_id="technical-approach")
    except ApprovedOutlineRequiredError as exc:
        drafting_context["error"] = str(exc)
        return
    pytest.fail("Expected ApprovedOutlineRequiredError was not raised")


@when(
    parsers.parse(
        'Phil attempts to draft an "{section_name}" section'
    )
)
def attempt_draft_missing_section(drafting_context, section_name):
    """Attempt drafting a section not in outline."""
    drafting_context["attempted_section"] = section_name
    drafter = FakeSectionDrafter()
    service = DraftService(section_drafter=drafter)
    outline = drafting_context.get("outline")
    try:
        service.draft_section(outline=outline, section_id=section_name)
    except SectionNotInOutlineError as exc:
        drafting_context["error"] = str(exc)
        return
    pytest.fail("Expected SectionNotInOutlineError was not raised")


@when("Phil requests review of the past performance section")
def request_review_no_draft(drafting_context):
    """Attempt review of un-drafted section -- expects NoDraftExistsError."""
    reviewer = FakeDraftReviewer()
    service = ReviewService(draft_reviewer=reviewer)
    try:
        service.review_section(
            draft=None, review_round=1, section_id="past performance",
        )
    except NoDraftExistsError as exc:
        drafting_context["error"] = str(exc)
        return
    pytest.fail("Expected NoDraftExistsError was not raised")


@when("Phil's draft reaches approximately 5200 words")
def draft_over_budget(drafting_context):
    """Draft exceeds page budget -- 5200 words exceeds 8-page budget (2000 words)."""
    outline = drafting_context.get("outline", _make_approved_outline())
    drafter = FakeSectionDrafter(word_count=5200)
    service = DraftService(section_drafter=drafter)
    result = service.draft_section(
        outline=outline,
        section_id="technical-approach",
    )
    drafting_context["draft_result"] = result


@when("the compliance check runs against the section")
def check_section_compliance(drafting_context):
    """Run compliance check against drafted section via DraftService."""
    outline = drafting_context.get("outline", _make_approved_outline())
    omit_ids = drafting_context.get("omit_ids", [])
    drafter = PartialComplianceDrafter(omit_ids=omit_ids)
    service = DraftService(section_drafter=drafter)
    result = service.draft_section(
        outline=outline,
        section_id="technical-approach",
    )
    drafting_context["draft_result"] = result
    # Generate user-facing message for compliance gaps
    if result.unaddressed_item_ids:
        count = len(result.unaddressed_item_ids)
        drafting_context["error"] = (
            f"{count} compliance items not addressed in technical approach"
        )


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
    result: ReviewResult = drafting_context["review_result"]
    assert len(result.scorecard.strengths) > 0, "Expected strengths in scorecard"
    assert len(result.scorecard.weaknesses) > 0 or len(result.scorecard.findings) > 0, (
        "Expected weaknesses or findings in scorecard"
    )


@then(
    "each finding includes location, severity, and specific suggestion"
)
def verify_finding_structure(drafting_context):
    """Verify findings are actionable."""
    result: ReviewResult = drafting_context["review_result"]
    assert len(result.scorecard.findings) > 0, "Expected findings"
    for finding in result.scorecard.findings:
        assert finding.location, f"Finding missing location: {finding}"
        assert finding.severity, f"Finding missing severity: {finding}"
        assert finding.suggestion, f"Finding missing suggestion: {finding}"


@then("the scorecard is written to the review artifacts")
def verify_scorecard_written(drafting_context):
    """Verify scorecard present in result (persistence is adapter concern)."""
    result: ReviewResult = drafting_context["review_result"]
    assert result.scorecard is not None, "Scorecard must be present in review result"


@then(
    "the review flags any matching weakness patterns from debrief history"
)
def verify_debrief_pattern_match(drafting_context):
    """Verify debrief patterns checked."""
    pytest.skip("Awaiting ReviewService implementation")


@then("the compliance matrix shows all items addressed")
def verify_full_compliance(drafting_context):
    """Verify full compliance coverage."""
    result: FullReviewResult = drafting_context["full_review_result"]
    assert result.all_compliance_addressed, (
        f"Expected all compliance addressed, unaddressed: {result.unaddressed_item_ids}"
    )


@then("a full scorecard is produced across all sections")
def verify_full_scorecard(drafting_context):
    """Verify full proposal scorecard."""
    result: FullReviewResult = drafting_context["full_review_result"]
    assert len(result.section_scorecards) > 0, "Expected section scorecards"


@then("Phil can approve the draft to proceed to formatting")
def verify_approve_option(drafting_context):
    """Verify approval option at checkpoint."""
    result: FullReviewResult = drafting_context["full_review_result"]
    assert result.can_approve, "Expected approval option when all compliance addressed"


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
    result: ReviewResult = drafting_context["review_result"]
    assert result.addressed_findings is not None, "Expected addressed findings tracking"
    assert result.open_findings is not None, "Expected open findings tracking"
    total = len(result.addressed_findings) + len(result.open_findings)
    assert total > 0, "Expected at least one tracked finding"


@then("updated ratings reflect the improvements")
def verify_updated_ratings(drafting_context):
    """Verify ratings updated after revision."""
    result: ReviewResult = drafting_context["review_result"]
    # After re-review, some findings should be addressed
    assert len(result.addressed_findings) > 0, "Expected at least one addressed finding"


@then("Phil sees unresolved findings escalated for human decision")
def verify_escalation(drafting_context):
    """Verify escalation after max review cycles."""
    result = drafting_context["review_result"]
    assert isinstance(result, EscalationResult), (
        f"Expected EscalationResult, got {type(result).__name__}"
    )
    assert len(result.unresolved_findings) > 0, "Expected unresolved findings in escalation"


@then("Phil can accept the section as-is or provide final revisions")
def verify_escalation_options(drafting_context):
    """Verify human decision options at escalation."""
    result: EscalationResult = drafting_context["review_result"]
    assert "accept" in result.options or "revise" in result.options, (
        f"Expected accept/revise options, got: {result.options}"
    )


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
    error = drafting_context.get("error", "")
    assert "wave 3" in error.lower() or "outline approval" in error.lower(), (
        f"Expected Wave 3 outline guidance in: '{error}'"
    )


@then("Phil sees guidance to update the outline first")
def verify_update_outline_guidance(drafting_context):
    """Verify guidance to update outline."""
    error = drafting_context.get("error", "")
    assert "update" in error.lower() or "outline" in error.lower(), (
        f"Expected outline update guidance in: '{error}'"
    )


@then("Phil sees guidance to draft the section first")
def verify_draft_section_guidance(drafting_context):
    """Verify guidance to draft section."""
    error = drafting_context.get("error", "")
    assert "draft" in error.lower(), (
        f"Expected draft guidance in: '{error}'"
    )


@then("Phil sees a warning that the section exceeds its page budget")
def verify_budget_warning(drafting_context):
    """Verify page budget warning."""
    result: DraftResult = drafting_context["draft_result"]
    assert result.budget_warning is not None, "Expected budget warning but got None"
    assert "exceeds" in result.budget_warning.lower()


@then("Phil sees suggestions to cut content or reallocate pages")
def verify_budget_suggestions(drafting_context):
    """Verify budget reduction suggestions."""
    result: DraftResult = drafting_context["draft_result"]
    assert result.budget_warning is not None
    assert "cut" in result.budget_warning.lower() or "reallocate" in result.budget_warning.lower()


@then(
    parsers.parse(
        'Phil sees "{count:d} compliance items not addressed in technical approach"'
    )
)
def verify_unaddressed_items(drafting_context, count):
    """Verify unaddressed compliance items flagged."""
    result: DraftResult = drafting_context["draft_result"]
    assert len(result.unaddressed_item_ids) == count, (
        f"Expected {count} unaddressed items, got {len(result.unaddressed_item_ids)}"
    )


@then("the unaddressed items are listed by ID")
def verify_items_listed(drafting_context):
    """Verify unaddressed items enumerated."""
    result: DraftResult = drafting_context["draft_result"]
    assert len(result.unaddressed_item_ids) > 0
    for item_id in result.unaddressed_item_ids:
        assert item_id.startswith("CI-"), f"Expected compliance item ID format, got: {item_id}"


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
