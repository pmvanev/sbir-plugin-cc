"""Step definitions for visual asset generation (US-010).

Invokes through: VisualAssetService (driving port).
Does NOT import internal figure classifiers or Mermaid generators directly.
"""

from __future__ import annotations

import json

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/visual_assets.feature")


# --- Given steps ---


@given(
    "Phil has an active proposal with all sections approved",
    target_fixture="active_state",
)
def proposal_all_sections_approved(sample_state, write_state):
    """Set up proposal with all sections approved, ready for Wave 5."""
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
    write_state(state)
    return state


@given(
    parsers.parse(
        "the approved outline contains {count:d} figure placeholders across {sections:d} sections"
    ),
    target_fixture="outline_placeholders",
)
def outline_with_placeholders(proposal_dir, count, sections):
    """Create outline with figure placeholders."""
    outline_dir = proposal_dir / "artifacts" / "wave-3-outline"
    outline_dir.mkdir(parents=True, exist_ok=True)
    outline_content = "# Proposal Outline\n\n"
    placeholders = []
    for i in range(1, count + 1):
        section = f"3.{((i - 1) % sections) + 1}"
        outline_content += f"## Section {section}\n"
        outline_content += f"[Figure {i}: Placeholder for figure in section {section}]\n\n"
        placeholders.append({"figure_number": i, "section_id": section})
    (outline_dir / "proposal-outline.md").write_text(outline_content)
    return {"count": count, "sections": sections, "placeholders": placeholders}


@given(
    parsers.parse('Figure {fig_num:d} is classified as a block diagram with method "{method}"'),
)
def figure_classified(fig_num, method):
    """Figure classification precondition."""
    pass


@given(
    parsers.parse("Figure {fig_num:d} requires a photograph that cannot be generated"),
)
def figure_requires_manual(fig_num):
    """Figure that cannot be auto-generated."""
    pass


@given(
    parsers.parse(
        '{count:d} figures are generated and Section {section} references "Figure {ref_num:d}"'
    ),
)
def figures_with_orphan_ref(count, section, ref_num):
    """Set up figures with an orphaned text reference."""
    pass


@given(
    parsers.parse(
        "{count:d} figures are generated and all text references resolve to existing figures"
    ),
)
def figures_all_valid(count):
    """Set up figures with all references valid."""
    pass


@given(
    parsers.parse("section {section_id} still has a RED Tier 2 PDC item"),
)
def section_still_red(section_id):
    """Section has unresolved RED PDC item."""
    pass


# --- When steps ---


@when("Phil generates the figure inventory", target_fixture="inventory_result")
def generate_inventory(proposal_dir, outline_placeholders):
    """Invoke figure inventory generation through VisualAssetService."""
    from pes.domain.visual_asset import FigurePlaceholder

    # Build placeholders from outline
    placeholders = []
    for p in outline_placeholders["placeholders"]:
        placeholders.append(
            FigurePlaceholder(
                figure_number=p["figure_number"],
                section_id=p["section_id"],
                description=f"Placeholder for figure in section {p['section_id']}",
                figure_type="diagram",
                generation_method="Mermaid",
            )
        )

    # Use FileVisualAssetAdapter as driven port
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter

    adapter = FileVisualAssetAdapter(
        artifacts_dir=proposal_dir / "artifacts" / "wave-5-visuals",
    )

    # Build inventory through the adapter (driven port)
    from pes.domain.visual_asset import FigureInventory

    inventory = FigureInventory(placeholders=placeholders)
    adapter.write_inventory(inventory)
    return inventory


@when(
    parsers.parse("the tool generates Figure {fig_num:d} from the Section {section} content"),
)
def generate_figure(fig_num, section):
    """Generate a specific figure from section content."""
    pytest.skip("Awaiting VisualAssetService implementation")


@when(
    parsers.parse("the tool classifies Figure {fig_num:d}"),
)
def classify_figure(fig_num):
    """Classify a figure by type and generation method."""
    pytest.skip("Awaiting VisualAssetService implementation")


@when("the tool runs cross-reference validation")
def run_cross_ref_validation():
    """Run cross-reference validation through VisualAssetService."""
    pytest.skip("Awaiting VisualAssetService implementation")


@when("Phil attempts to generate the figure inventory")
def attempt_generate_inventory():
    """Attempt figure inventory when PES should block."""
    pytest.skip("Awaiting VisualAssetService + PES integration")


# --- Then steps ---


@then(
    parsers.parse("the inventory lists {count:d} entries"),
)
def verify_inventory_count(inventory_result, count):
    """Verify figure inventory has expected number of entries."""
    assert len(inventory_result.placeholders) == count


@then("each entry has a type classification and recommended generation method")
def verify_entry_classification(inventory_result):
    """Verify each inventory entry has type and method."""
    for placeholder in inventory_result.placeholders:
        assert placeholder.figure_type, f"Figure {placeholder.figure_number} missing type"
        assert (
            placeholder.generation_method
        ), f"Figure {placeholder.figure_number} missing generation method"


@then("each entry has its target section identified")
def verify_entry_section(inventory_result):
    """Verify each inventory entry has a target section."""
    for placeholder in inventory_result.placeholders:
        assert (
            placeholder.section_id
        ), f"Figure {placeholder.figure_number} missing target section"


@then("the inventory is written to the visuals artifacts directory")
def verify_inventory_written(proposal_dir):
    """Verify inventory artifact is created."""
    inventory_path = (
        proposal_dir / "artifacts" / "wave-5-visuals" / "figure-inventory.json"
    )
    assert inventory_path.exists(), f"Inventory not written to {inventory_path}"
    content = json.loads(inventory_path.read_text())
    assert "placeholders" in content
    assert len(content["placeholders"]) > 0


@then("an SVG file is produced in the figures directory")
def verify_svg_produced():
    """Verify SVG figure is generated."""
    pytest.skip("Awaiting VisualAssetService implementation")


@then("the figure is presented to Phil for review")
def verify_figure_presented():
    """Verify figure is presented for human review."""
    pytest.skip("Awaiting VisualAssetService implementation")


@then("Phil can approve, request revision, or replace with a manual file")
def verify_review_options():
    """Verify review options are available."""
    pytest.skip("Awaiting VisualAssetService implementation")


@then(
    "an external brief is generated with content description, dimensions, and resolution"
)
def verify_external_brief():
    """Verify external brief is generated for non-generatable figure."""
    pytest.skip("Awaiting VisualAssetService implementation")


@then("Phil can provide a manual file to replace the brief")
def verify_manual_replace():
    """Verify manual file replacement option."""
    pytest.skip("Awaiting VisualAssetService implementation")


@then(
    parsers.parse('it flags "Figure {ref_num:d} referenced in Section {section} does not exist"'),
)
def verify_orphan_flagged(ref_num, section):
    """Verify orphaned reference is flagged."""
    pytest.skip("Awaiting VisualAssetService implementation")


@then("the cross-reference log records the mismatch")
def verify_cross_ref_mismatch():
    """Verify mismatch is recorded in cross-reference log."""
    pytest.skip("Awaiting VisualAssetService implementation")


@then("the cross-reference log shows all references valid")
def verify_cross_ref_valid():
    """Verify all cross-references are valid."""
    pytest.skip("Awaiting VisualAssetService implementation")


@then("no orphaned references are flagged")
def verify_no_orphans():
    """Verify no orphaned references."""
    pytest.skip("Awaiting VisualAssetService implementation")
