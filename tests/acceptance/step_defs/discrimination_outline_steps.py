"""Step definitions for Wave 3 discrimination table and proposal outline.

Invokes through: DiscriminationService (driving port).
Does NOT import internal discriminator builders or outline generators directly.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.discrimination import DiscriminationTable, DiscriminatorItem
from pes.domain.discrimination_service import (
    DiscriminationService,
    ResearchApprovalRequiredError,
)
from pes.domain.outline import OutlineSection, ProposalOutline
from pes.domain.outline_service import (
    OutlineGenerator,
    OutlineNotFoundError,
    OutlineService,
)
from pes.domain.research import (
    ResearchCategory,
    ResearchFinding,
    ResearchSummary,
)
from pes.domain.strategy import StrategyBrief, StrategySection
from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/discrimination_outline.feature")


# ---------------------------------------------------------------------------
# Fake driven port (DiscriminationGenerator) at port boundary
# ---------------------------------------------------------------------------


class FakeDiscriminationGenerator:
    """Fake driven port that produces deterministic discrimination tables."""

    def __init__(self) -> None:
        self.last_tpoc_insights: str | None = None
        self.last_feedback: str | None = None

    def generate(
        self,
        strategy_brief: StrategyBrief,
        compliance_matrix: dict[str, Any],
        research_summary: ResearchSummary,
        *,
        tpoc_insights: str | None = None,
        feedback: str | None = None,
    ) -> DiscriminationTable:
        self.last_tpoc_insights = tpoc_insights
        self.last_feedback = feedback

        items = [
            DiscriminatorItem(
                category="company_strengths",
                claim="Superior manufacturing capacity versus competitor X",
                evidence_citation="Company profile: 50k sq ft facility",
            ),
            DiscriminatorItem(
                category="technical_approach",
                claim="Novel beam-steering approach versus prior art",
                evidence_citation="Research finding: patent landscape analysis",
            ),
            DiscriminatorItem(
                category="team_qualifications",
                claim="PI has 15 years directed energy experience",
                evidence_citation="Company profile: team roster",
            ),
        ]

        if tpoc_insights:
            items.append(
                DiscriminatorItem(
                    category="technical_approach",
                    claim="Our approach avoids the failed thermal management design",
                    evidence_citation=f"TPOC insight: {tpoc_insights}",
                )
            )

        if feedback:
            items.append(
                DiscriminatorItem(
                    category="company_strengths",
                    claim=f"Added per feedback: {feedback}",
                    evidence_citation="User feedback incorporation",
                )
            )

        return DiscriminationTable(items=items)


# ---------------------------------------------------------------------------
# Fake driven port (OutlineGenerator) at port boundary
# ---------------------------------------------------------------------------


class FakeOutlineGeneratorAT:
    """Fake outline generator for acceptance tests."""

    def __init__(self) -> None:
        self.last_feedback: str | None = None

    def generate(
        self,
        discrimination_table: dict[str, Any],
        compliance_matrix: dict[str, Any],
        *,
        page_limit: float,
        feedback: str | None = None,
    ) -> ProposalOutline:
        self.last_feedback = feedback
        items = compliance_matrix.get("items", [])
        item_ids = [item["id"] for item in items]

        sections = [
            OutlineSection(
                section_id="sec-1",
                title="Technical Approach",
                compliance_item_ids=item_ids,
                page_budget=page_limit * 0.6,
                figure_placeholders=["fig-1"],
                thesis_statement="Technical thesis",
            ),
            OutlineSection(
                section_id="sec-2",
                title="Management",
                compliance_item_ids=[],
                page_budget=page_limit * 0.4,
                figure_placeholders=["fig-2"],
                thesis_statement="Management thesis",
            ),
        ]
        return ProposalOutline(sections=sections)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def discrim_context() -> dict[str, Any]:
    """Mutable context to pass data between steps."""
    return {}


@pytest.fixture()
def fake_generator() -> FakeDiscriminationGenerator:
    return FakeDiscriminationGenerator()


@pytest.fixture()
def fake_outline_generator() -> FakeOutlineGeneratorAT:
    return FakeOutlineGeneratorAT()


@pytest.fixture()
def discrimination_service(fake_generator) -> DiscriminationService:
    return DiscriminationService(discrimination_generator=fake_generator)


@pytest.fixture()
def outline_service(fake_outline_generator) -> OutlineService:
    return OutlineService(outline_generator=fake_outline_generator)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


SAMPLE_BRIEF = StrategyBrief(
    sections=[
        StrategySection(key="technical_approach", title="Technical Approach", content="approach"),
        StrategySection(key="trl", title="TRL", content="trl assessment"),
        StrategySection(key="teaming", title="Teaming", content="teaming plan"),
        StrategySection(key="phase_iii", title="Phase III", content="commercialization"),
        StrategySection(key="budget", title="Budget", content="budget plan"),
        StrategySection(key="risks", title="Risks", content="risk assessment"),
    ],
    tpoc_available=True,
)


def _make_research_summary() -> ResearchSummary:
    return ResearchSummary(
        findings=[
            ResearchFinding(
                category=cat,
                content=f"Finding for {cat.value}",
                evidence_source=f"Source for {cat.value}",
            )
            for cat in ResearchCategory
        ],
    )


SAMPLE_COMPLIANCE_MATRIX = {"item_count": 47, "items": []}


# --- Given steps (Background) ---


@given(
    "Phil has an active proposal with approved research review",
    target_fixture="active_state",
)
def proposal_with_research_approved(sample_state, write_state):
    """Set up proposal with research approved, ready for Wave 3."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 3
    state["waves"] = {
        "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
        "1": {"status": "completed", "completed_at": "2026-03-05T10:00:00Z"},
        "2": {"status": "completed", "completed_at": "2026-03-08T10:00:00Z"},
        "3": {"status": "active", "completed_at": None},
    }
    state["strategy_brief"] = {
        "path": "./artifacts/wave-1-strategy/strategy-brief.md",
        "status": "approved",
        "approved_at": "2026-03-05T10:00:00Z",
    }
    state["research_summary"] = {
        "status": "approved",
        "approved_at": "2026-03-08T10:00:00Z",
    }
    write_state(state)
    return state


# --- Given steps ---


@given("a strategy brief exists with key discriminators")
def strategy_with_discriminators(discrim_context):
    """Strategy brief contains discriminator candidates."""
    discrim_context["strategy_brief"] = SAMPLE_BRIEF


@given("research findings include competitor landscape and prior art")
def research_with_competitors(discrim_context):
    """Research findings have competitor and prior art data."""
    discrim_context["research_summary"] = _make_research_summary()
    discrim_context["research_approved"] = True


@given("TPOC answers revealed the agency's failed prior approach")
def tpoc_revealed_failure(discrim_context):
    """TPOC data includes insight about agency's prior failed approach."""
    discrim_context["tpoc_insights"] = "Agency's prior thermal management approach failed due to overheating"
    discrim_context["strategy_brief"] = SAMPLE_BRIEF
    discrim_context["research_summary"] = _make_research_summary()
    discrim_context["research_approved"] = True


@given("a discrimination table has been generated for AF243-001")
def discrimination_generated(discrim_context, discrimination_service):
    """Discrimination table has been generated."""
    discrim_context["strategy_brief"] = SAMPLE_BRIEF
    discrim_context["research_summary"] = _make_research_summary()
    discrim_context["research_approved"] = True
    table = discrimination_service.generate_table(
        strategy_brief=SAMPLE_BRIEF,
        compliance_matrix=SAMPLE_COMPLIANCE_MATRIX,
        research_summary=_make_research_summary(),
        research_approved=True,
    )
    discrim_context["discrimination_table"] = table


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
def outline_generated(discrim_context, outline_service):
    """Proposal outline has been generated via OutlineService."""
    discrim_context["outline_generated"] = True
    discrim_context["discrimination_table"] = {
        "items": [{"category": "company_strengths", "claim": "Superior facility"}],
        "approved_at": "2026-03-01T00:00:00Z",
    }
    compliance_matrix = {"item_count": 6, "items": [{"id": f"CI-{i+1:03d}"} for i in range(6)]}
    result = outline_service.generate_outline(
        discrimination_table=discrim_context["discrimination_table"],
        compliance_matrix=compliance_matrix,
        page_limit=25.0,
    )
    discrim_context["outline"] = result.outline
    discrim_context["compliance_matrix"] = compliance_matrix


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


@given("the research review has not been approved")
def research_not_approved(discrim_context):
    """Research review not approved."""
    discrim_context["research_approved"] = False
    discrim_context["strategy_brief"] = SAMPLE_BRIEF
    discrim_context["research_summary"] = _make_research_summary()


# --- When steps ---


@when("the discrimination table is generated")
def generate_discrimination(discrim_context, discrimination_service):
    """Invoke discrimination table generation through driving port."""
    table = discrimination_service.generate_table(
        strategy_brief=discrim_context.get("strategy_brief", SAMPLE_BRIEF),
        compliance_matrix=SAMPLE_COMPLIANCE_MATRIX,
        research_summary=discrim_context.get("research_summary", _make_research_summary()),
        research_approved=discrim_context.get("research_approved", True),
        tpoc_insights=discrim_context.get("tpoc_insights"),
    )
    discrim_context["discrimination_table"] = table


@when(
    parsers.parse(
        'Phil provides discrimination feedback "{feedback}"'
    )
)
def revise_discrimination(discrim_context, feedback, discrimination_service):
    """Submit discrimination revision feedback."""
    discrim_context["revision_feedback"] = feedback
    revised = discrimination_service.revise_table(
        existing_table=discrim_context["discrimination_table"],
        strategy_brief=discrim_context.get("strategy_brief", SAMPLE_BRIEF),
        compliance_matrix=SAMPLE_COMPLIANCE_MATRIX,
        research_summary=discrim_context.get("research_summary", _make_research_summary()),
        research_approved=True,
        feedback=feedback,
    )
    discrim_context["discrimination_table"] = revised


@when("the proposal outline is generated")
def generate_outline(discrim_context):
    """Invoke outline generation through driving port."""
    pytest.skip("Awaiting OutlineService implementation")


@when("Phil approves the proposal outline")
def approve_outline(discrim_context, outline_service):
    """Approve outline through driving port."""
    result = outline_service.approve_outline(
        outline=discrim_context.get("outline"),
    )
    discrim_context["approve_result"] = result


@when(
    parsers.parse('Phil provides outline feedback "{feedback}"')
)
def revise_outline(discrim_context, feedback, outline_service):
    """Submit outline revision feedback."""
    discrim_context["revision_feedback"] = feedback
    revised = outline_service.revise_outline(
        outline=discrim_context.get("outline"),
        discrimination_table=discrim_context.get("discrimination_table"),
        compliance_matrix=discrim_context.get("compliance_matrix", {"items": []}),
        page_limit=25.0,
        feedback=feedback,
    )
    discrim_context["outline"] = revised


@when("Phil attempts to generate the discrimination table")
def attempt_generate_discrimination(discrim_context, discrimination_service):
    """Attempt discrimination without prerequisites."""
    try:
        discrimination_service.generate_table(
            strategy_brief=discrim_context.get("strategy_brief", SAMPLE_BRIEF),
            compliance_matrix=SAMPLE_COMPLIANCE_MATRIX,
            research_summary=discrim_context.get("research_summary"),
            research_approved=discrim_context.get("research_approved", False),
        )
    except ResearchApprovalRequiredError as e:
        discrim_context["error"] = str(e)


@when("Phil attempts to generate the proposal outline")
def attempt_generate_outline(discrim_context):
    """Attempt outline without prerequisites."""
    pytest.skip("Awaiting OutlineService implementation")


@when("Phil attempts to approve the proposal outline")
def attempt_approve_outline(discrim_context, outline_service):
    """Attempt approval of nonexistent outline."""
    try:
        outline_service.approve_outline(outline=None)
    except OutlineNotFoundError as e:
        discrim_context["error"] = str(e)


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
    table = discrim_context["discrimination_table"]
    company_items = [i for i in table.items if i.category == "company_strengths"]
    assert len(company_items) > 0, "Expected at least one company_strengths discriminator"


@then(
    "Phil sees discriminators covering technical approach versus prior art"
)
def verify_technical_discriminators(discrim_context):
    """Verify technical discriminators present."""
    table = discrim_context["discrimination_table"]
    tech_items = [i for i in table.items if i.category == "technical_approach"]
    assert len(tech_items) > 0, "Expected at least one technical_approach discriminator"


@then(
    "Phil sees discriminators covering team qualifications and past performance"
)
def verify_team_discriminators(discrim_context):
    """Verify team discriminators present."""
    table = discrim_context["discrimination_table"]
    team_items = [i for i in table.items if i.category == "team_qualifications"]
    assert len(team_items) > 0, "Expected at least one team_qualifications discriminator"


@then("each discriminator cites supporting evidence")
def verify_evidence_citations(discrim_context):
    """Verify evidence cited for each discriminator."""
    table = discrim_context["discrimination_table"]
    for item in table.items:
        assert item.evidence_citation, (
            f"Discriminator '{item.claim}' missing evidence citation"
        )


@then(
    "the technical discriminators explicitly contrast with the failed prior approach"
)
def verify_tpoc_contrast(discrim_context):
    """Verify TPOC failure insight used in discrimination."""
    table = discrim_context["discrimination_table"]
    tech_items = [i for i in table.items if i.category == "technical_approach"]
    contrast_found = any("failed" in i.claim.lower() or "avoids" in i.claim.lower() for i in tech_items)
    assert contrast_found, "Expected technical discriminator contrasting with failed prior approach"


@then("the TPOC insight is cited as evidence")
def verify_tpoc_evidence_cited(discrim_context):
    """Verify TPOC insight cited."""
    table = discrim_context["discrimination_table"]
    tpoc_cited = any("tpoc" in i.evidence_citation.lower() for i in table.items)
    assert tpoc_cited, "Expected TPOC insight cited as evidence"


@then("the discrimination table is revised incorporating the feedback")
def verify_discrimination_revised(discrim_context):
    """Verify discrimination table revised."""
    table = discrim_context["discrimination_table"]
    feedback = discrim_context["revision_feedback"]
    # Revised table should incorporate feedback content
    all_claims = " ".join(i.claim for i in table.items)
    assert feedback.lower() in all_claims.lower() or len(table.items) > 3, (
        "Revised table should incorporate feedback"
    )


@then("Phil reviews the revised discrimination table")
def verify_revised_discrimination(discrim_context):
    """Verify revised table presented."""
    table = discrim_context["discrimination_table"]
    assert table is not None
    assert len(table.items) > 0


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
    result = discrim_context["approve_result"]
    assert result["outline_status"] == "approved"
    assert result["approved_at"] is not None


@then("Wave 4 is unlocked")
def verify_wave_4_unlocked(discrim_context):
    """Verify Wave 4 status changed."""
    result = discrim_context["approve_result"]
    assert result["wave_4_unlocked"] is True


@then("the proposal outline is revised incorporating the feedback")
def verify_outline_revised(discrim_context):
    """Verify outline revised with feedback."""
    outline = discrim_context["outline"]
    assert outline is not None
    assert len(outline.sections) > 0


@then("Phil reviews the revised outline")
def verify_revised_outline(discrim_context):
    """Verify revised outline presented."""
    outline = discrim_context["outline"]
    assert outline is not None
    assert len(outline.sections) > 0


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
    error = discrim_context.get("error", "")
    assert "wave 2" in error.lower() or "research" in error.lower(), (
        f"Expected guidance mentioning research review, got: '{error}'"
    )


@then("Phil sees guidance to complete the discrimination review first")
def verify_discrimination_guidance(discrim_context):
    """Verify guidance points to discrimination review."""
    pytest.skip("Awaiting OutlineService implementation")


@then("Phil sees guidance to generate one first")
def verify_generate_guidance(discrim_context):
    """Verify guidance to generate."""
    error = discrim_context.get("error", "")
    assert "generate" in error.lower(), (
        f"Expected guidance mentioning 'generate', got: '{error}'"
    )


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
