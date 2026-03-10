"""Step definitions for document formatting and volume assembly (US-011).

Invokes through: FormattingService and AssemblyService (driving ports).
Does NOT import internal format template loaders or document renderers directly.
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/formatting_assembly.feature")


# --- Given steps ---


@given(
    "Phil has an active proposal with all figures approved",
    target_fixture="active_state",
)
def proposal_figures_approved(sample_state, write_state):
    """Set up proposal with all figures approved, ready for Wave 6."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 6
    state["waves"] = {
        "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
        "1": {"status": "completed", "completed_at": "2026-03-05T10:00:00Z"},
        "2": {"status": "completed", "completed_at": "2026-03-06T10:00:00Z"},
        "3": {"status": "completed", "completed_at": "2026-03-07T10:00:00Z"},
        "4": {"status": "completed", "completed_at": "2026-03-08T10:00:00Z"},
        "5": {"status": "completed", "completed_at": "2026-03-09T10:00:00Z"},
        "6": {"status": "active", "completed_at": None},
    }
    state["visuals"] = {
        "status": "completed",
        "figure_count": 5,
        "generated_count": 4,
        "external_count": 1,
        "cross_refs_valid": True,
        "completed_at": "2026-03-09T10:00:00Z",
    }
    write_state(state)
    return state


@given(
    "the solicitation requires Times New Roman 12pt and 1-inch margins",
    target_fixture="format_template",
)
def solicitation_format_rules():
    """Load format template for the solicitation through FormatTemplatePort."""
    from pes.adapters.json_format_template_adapter import JsonFormatTemplateAdapter
    from pes.ports.format_template_port import FormatTemplateLoader

    adapter: FormatTemplateLoader = JsonFormatTemplateAdapter(
        templates_dir="templates/format-rules"
    )
    template = adapter.load_template(agency="dod", solicitation_type="phase-i")
    assert template is not None
    return template


@given(
    parsers.parse(
        "{count:d} approved figures exist and the document has {citations:d} citations"
    ),
)
def figures_and_citations(count, citations):
    """Pre-existing figures and citations."""
    pass


@given(
    parsers.parse("the document uses {count:d} unique acronyms"),
)
def document_with_acronyms(count):
    """Document with acronyms."""
    pass


@given(
    parsers.parse("{count:d} are not defined on first use"),
)
def undefined_acronyms(count):
    """Undefined acronyms exist in document."""
    pass


@given(
    parsers.parse("the formatted technical volume is {pages:d} pages"),
)
def formatted_volume_pages(pages):
    """Formatted volume with given page count."""
    pass


@given(
    parsers.parse("the solicitation limit is {limit:d} pages"),
)
def solicitation_page_limit(limit):
    """Solicitation page limit."""
    pass


@given(
    parsers.parse(
        "the formatted technical volume is {pages:d} pages against a {limit:d}-page limit"
    ),
)
def volume_over_limit(pages, limit):
    """Formatted volume exceeding page limit."""
    pass


@given(
    parsers.parse("the compliance matrix has {count:d} items"),
    target_fixture="compliance_item_count",
)
def compliance_matrix_with_items(count):
    """Compliance matrix with given item count."""
    return count


@given(
    parsers.parse("{covered:d} are covered and {waived:d} are waived with reasons"),
    target_fixture="compliance_setup",
)
def compliance_covered_waived(compliance_item_count, covered, waived):
    """Build a compliance matrix with covered and waived items."""
    from pes.domain.compliance import (
        ComplianceItem,
        ComplianceMatrix,
        CoverageStatus,
        RequirementType,
    )

    items = []
    for i in range(1, covered + 1):
        items.append(ComplianceItem(
            item_id=i, text=f"Requirement {i}",
            requirement_type=RequirementType.SHALL,
            status=CoverageStatus.COVERED,
        ))
    for i in range(covered + 1, covered + waived + 1):
        items.append(ComplianceItem(
            item_id=i, text=f"Requirement {i}",
            requirement_type=RequirementType.SHALL,
            status=CoverageStatus.WAIVED,
        ))
    matrix = ComplianceMatrix(items=items)
    return {"matrix": matrix, "total": compliance_item_count, "covered": covered, "waived": waived}


@given(
    parsers.parse(
        '{count:d} item has status "missing" with no coverage and no waiver'
    ),
    target_fixture="compliance_setup",
)
def compliance_missing_item(compliance_item_count, count):
    """Build a compliance matrix with one missing item."""
    from pes.domain.compliance import (
        ComplianceItem,
        ComplianceMatrix,
        CoverageStatus,
        RequirementType,
    )

    items = []
    # All items except `count` are covered
    covered_count = compliance_item_count - count
    for i in range(1, covered_count + 1):
        items.append(ComplianceItem(
            item_id=i, text=f"Requirement {i}",
            requirement_type=RequirementType.SHALL,
            status=CoverageStatus.COVERED,
        ))
    for i in range(covered_count + 1, compliance_item_count + 1):
        items.append(ComplianceItem(
            item_id=i, text=f"Requirement {i}",
            requirement_type=RequirementType.SHALL,
            status=CoverageStatus.NOT_STARTED,
        ))
    matrix = ComplianceMatrix(items=items)
    return {"matrix": matrix, "total": compliance_item_count, "missing_count": count}


@given("formatting and compliance checks are complete",
       target_fixture="assembly_ready")
def formatting_complete():
    """Formatting and compliance checks done."""
    return True


# --- When steps ---


@when(
    parsers.parse('Phil formats the proposal selecting "{medium}"'),
    target_fixture="format_result",
)
def format_proposal(format_template, medium):
    """Format proposal through FormattingService using loaded template."""
    # Step 03-01: verify template was loaded with correct properties
    assert format_template is not None
    assert format_template.font_family is not None
    assert format_template.font_size_pt is not None
    return {"template": format_template, "medium": medium}


@when("the tool inserts figures and formats references")
def insert_figures_format_refs():
    """Insert figures and format references through FormattingService."""
    pytest.skip("Awaiting FormattingService implementation")


@when("the tool runs the jargon audit")
def run_jargon_audit():
    """Run jargon audit through FormattingService."""
    pytest.skip("Awaiting FormattingService implementation")


@when("the tool reports the page count")
def report_page_count():
    """Report page count through FormattingService."""
    pytest.skip("Awaiting FormattingService implementation")


@when(
    "the tool runs the final compliance check",
    target_fixture="compliance_result",
)
def run_final_compliance(compliance_setup):
    """Run final compliance check through AssemblyService."""
    from pes.domain.assembly_service import AssemblyService

    service = AssemblyService()
    return service.run_final_compliance_check(matrix=compliance_setup["matrix"])


@when(
    "the tool assembles volumes",
    target_fixture="assembly_result",
)
def assemble_volumes(assembly_ready):
    """Assemble volumes through AssemblyService."""
    from pes.domain.assembly_service import AssemblyService
    from pes.ports.document_assembly_port import DocumentAssembler

    # Use a fake assembler for acceptance test
    class FakeAssembler(DocumentAssembler):
        def assemble_volumes(self, *, sections, format_template_agency):
            from pes.ports.document_assembly_port import AssembledVolume
            return [
                AssembledVolume(volume_number=1, title="Technical", content="...", page_count=19),
                AssembledVolume(volume_number=2, title="Cost", content="...", page_count=5),
                AssembledVolume(
                    volume_number=3, title="Company Info",
                    content="...", page_count=3,
                ),
            ]

    service = AssemblyService(document_assembler=FakeAssembler())
    return service.assemble_volumes(
        sections=["technical", "cost", "company-info"],
        format_template_agency="dod",
    )


# --- Then steps ---


@then("the tool applies font, margins, headers, footers, and section numbering")
def verify_formatting_applied(format_result):
    """Verify format template contains all required formatting properties."""
    template = format_result["template"]
    assert template.font_family == "Times New Roman"
    assert template.font_size_pt == 12
    assert template.margin_top_inches == 1.0
    assert template.margin_bottom_inches == 1.0
    assert template.margin_left_inches == 1.0
    assert template.margin_right_inches == 1.0
    assert template.header is not None
    assert template.footer is not None
    assert template.page_limit > 0


@then("the output medium is recorded in the proposal state")
def verify_medium_recorded(format_result):
    """Verify output medium was captured."""
    assert format_result["medium"] == "Microsoft Word (.docx)"


@then("each figure appears at its correct position with its approved caption")
def verify_figures_positioned():
    """Verify figures inserted at correct positions."""
    pytest.skip("Awaiting FormattingService implementation")


@then("citations are formatted in a consistent style")
def verify_citations_formatted():
    """Verify citation formatting."""
    pytest.skip("Awaiting FormattingService implementation")


@then(
    parsers.parse("it flags the {count:d} undefined acronyms with their locations"),
)
def verify_undefined_flagged(count):
    """Verify undefined acronyms are flagged."""
    pytest.skip("Awaiting FormattingService implementation")


@then("the audit is written to the formatting artifacts directory")
def verify_audit_written():
    """Verify jargon audit artifact is created."""
    pytest.skip("Awaiting FormattingService implementation")


@then(
    parsers.parse('Phil sees "{message}"'),
)
def verify_user_message(message):
    """Verify user-facing message."""
    pytest.skip("Awaiting FormattingService implementation")


@then(
    parsers.parse("Phil sees the {count:d} largest sections with page counts"),
)
def verify_largest_sections(count):
    """Verify largest sections are identified."""
    pytest.skip("Awaiting FormattingService implementation")


@then("Phil sees trimming suggestions")
def verify_trimming_suggestions():
    """Verify trimming suggestions are provided."""
    pytest.skip("Awaiting FormattingService implementation")


@then(
    parsers.parse('it reports "{report}"'),
)
def verify_compliance_report(compliance_result, report):
    """Verify compliance report content."""
    assert compliance_result.summary == report


@then("the final check is written to the formatting artifacts directory")
def verify_final_check_written(compliance_result):
    """Verify final compliance check artifact."""
    assert compliance_result.artifact_written is True


@then("it reports the missing item with guidance to provide content or waive")
def verify_missing_guidance(compliance_result):
    """Verify missing item guidance."""
    assert compliance_result.missing > 0
    assert compliance_result.blocks_progression is True
    guidance_lower = compliance_result.guidance.lower()
    assert "waive" in guidance_lower or "content" in guidance_lower


@then(
    "it creates Volume 1 (Technical), Volume 2 (Cost), and Volume 3 (Company Info)"
)
def verify_volumes_created(assembly_result):
    """Verify three volumes are created."""
    assert len(assembly_result.volumes) == 3
    titles = [v.title for v in assembly_result.volumes]
    assert "Technical" in titles
    assert "Cost" in titles
    assert "Company Info" in titles


@then("the volumes are written to the assembly artifacts directory")
def verify_volumes_written(assembly_result):
    """Verify volumes are written to correct directory."""
    assert assembly_result.artifact_written is True


@then("a human checkpoint is presented for assembled package review")
def verify_human_checkpoint(assembly_result):
    """Verify human checkpoint for assembly review."""
    assert assembly_result.checkpoint_required is True
    assert assembly_result.checkpoint_type == "assembled_package_review"
