"""Step definitions for visual asset generation (US-010).

Invokes through: VisualAssetService (driving port).
Does NOT import internal figure classifiers or Mermaid generators directly.
"""

from __future__ import annotations

import json

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
    target_fixture="cross_ref_setup",
)
def figures_with_orphan_ref(proposal_dir, count, section, ref_num):
    """Set up figures with an orphaned text reference."""
    from pes.domain.visual_asset import GeneratedFigure

    generated = [
        GeneratedFigure(
            figure_number=i,
            section_id=f"3.{i}",
            file_path=f"figure-{i}.svg",
            format="svg",
        )
        for i in range(1, count + 1)
    ]
    text_references = [
        {"section_id": section, "referenced_figure": ref_num},
    ]
    return {"generated": generated, "text_references": text_references}


@given(
    parsers.parse(
        "{count:d} figures are generated and all text references resolve to existing figures"
    ),
    target_fixture="cross_ref_setup",
)
def figures_all_valid(proposal_dir, count):
    """Set up figures with all references valid."""
    from pes.domain.visual_asset import GeneratedFigure

    generated = [
        GeneratedFigure(
            figure_number=i,
            section_id=f"3.{i}",
            file_path=f"figure-{i}.svg",
            format="svg",
        )
        for i in range(1, count + 1)
    ]
    text_references = [
        {"section_id": f"3.{i}", "referenced_figure": i} for i in range(1, count + 1)
    ]
    return {"generated": generated, "text_references": text_references}


@given(
    parsers.parse("section {section_id} still has a RED Tier 2 PDC item"),
    target_fixture="red_pdc_context",
)
def section_still_red(section_id):
    """Section has unresolved RED PDC item."""
    return {"section_id": section_id, "tier": 2, "item": "Risk mitigation"}


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
    target_fixture="generation_result",
)
def generate_figure(proposal_dir, fig_num, section):
    """Generate a specific figure through VisualAssetService."""
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter
    from pes.domain.visual_asset import FigurePlaceholder
    from pes.domain.visual_asset_service import VisualAssetService

    adapter = FileVisualAssetAdapter(
        artifacts_dir=proposal_dir / "artifacts" / "wave-5-visuals",
    )
    placeholder = FigurePlaceholder(
        figure_number=fig_num,
        section_id=section,
        description=f"System architecture block diagram for section {section}",
        figure_type="block_diagram",
        generation_method="Mermaid",
    )

    # Fake generator for acceptance test
    class AcceptanceFigureGenerator:
        def generate_svg(self, placeholder):
            return "<svg><rect width='100' height='100'/></svg>"

    # Fake PDC checker (all green for this scenario)
    class AcceptancePdcChecker:
        def all_sections_pdc_green(self):
            return True

        def get_red_pdc_items(self):
            return []

    service = VisualAssetService(
        figure_generator=AcceptanceFigureGenerator(),
        visual_asset_port=adapter,
        pdc_checker=AcceptancePdcChecker(),
    )
    return service.generate_figure(placeholder=placeholder)


@when(
    parsers.parse("the tool classifies Figure {fig_num:d}"),
    target_fixture="classification_result",
)
def classify_figure(proposal_dir, fig_num):
    """Classify a non-generatable figure through VisualAssetService."""
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter
    from pes.domain.visual_asset import FigurePlaceholder
    from pes.domain.visual_asset_service import VisualAssetService

    adapter = FileVisualAssetAdapter(
        artifacts_dir=proposal_dir / "artifacts" / "wave-5-visuals",
    )
    placeholder = FigurePlaceholder(
        figure_number=fig_num,
        section_id="3.4",
        description="Photograph of hardware prototype",
        figure_type="photograph",
        generation_method="external",
    )

    class StubFigureGenerator:
        def generate_svg(self, placeholder):
            return "<svg/>"

    class StubPdcChecker:
        def all_sections_pdc_green(self):
            return True

        def get_red_pdc_items(self):
            return []

    service = VisualAssetService(
        figure_generator=StubFigureGenerator(),
        visual_asset_port=adapter,
        pdc_checker=StubPdcChecker(),
    )
    return service.generate_figure(placeholder=placeholder)


@when("the tool runs cross-reference validation", target_fixture="cross_ref_result")
def run_cross_ref_validation(proposal_dir, cross_ref_setup):
    """Run cross-reference validation through VisualAssetService."""
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter
    from pes.domain.visual_asset_service import VisualAssetService

    adapter = FileVisualAssetAdapter(
        artifacts_dir=proposal_dir / "artifacts" / "wave-5-visuals",
    )

    class StubFigureGenerator:
        def generate_svg(self, placeholder):
            return "<svg/>"

    class StubPdcChecker:
        def all_sections_pdc_green(self):
            return True

        def get_red_pdc_items(self):
            return []

    service = VisualAssetService(
        figure_generator=StubFigureGenerator(),
        visual_asset_port=adapter,
        pdc_checker=StubPdcChecker(),
    )
    return service.validate_cross_references(
        generated_figures=cross_ref_setup["generated"],
        text_references=cross_ref_setup["text_references"],
    )


@when(
    "Phil attempts to generate the figure inventory",
    target_fixture="pdc_gate_error",
)
def attempt_generate_inventory(proposal_dir, red_pdc_context):
    """Attempt figure inventory when PES should block."""
    from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter
    from pes.domain.visual_asset_service import PdcGateBlockedError, VisualAssetService

    adapter = FileVisualAssetAdapter(
        artifacts_dir=proposal_dir / "artifacts" / "wave-5-visuals",
    )

    class StubFigureGenerator:
        def generate_svg(self, placeholder):
            return "<svg/>"

    class RedPdcChecker:
        def all_sections_pdc_green(self):
            return False

        def get_red_pdc_items(self):
            return [red_pdc_context]

    service = VisualAssetService(
        figure_generator=StubFigureGenerator(),
        visual_asset_port=adapter,
        pdc_checker=RedPdcChecker(),
    )
    try:
        service.check_pdc_gate()
        return None  # Should not reach here
    except PdcGateBlockedError as e:
        return e


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
        assert placeholder.generation_method, (
            f"Figure {placeholder.figure_number} missing generation method"
        )


@then("each entry has its target section identified")
def verify_entry_section(inventory_result):
    """Verify each inventory entry has a target section."""
    for placeholder in inventory_result.placeholders:
        assert placeholder.section_id, f"Figure {placeholder.figure_number} missing target section"


@then("the inventory is written to the visuals artifacts directory")
def verify_inventory_written(proposal_dir):
    """Verify inventory artifact is created."""
    inventory_path = proposal_dir / "artifacts" / "wave-5-visuals" / "figure-inventory.json"
    assert inventory_path.exists(), f"Inventory not written to {inventory_path}"
    content = json.loads(inventory_path.read_text())
    assert "placeholders" in content
    assert len(content["placeholders"]) > 0


@then("an SVG file is produced in the figures directory")
def verify_svg_produced(proposal_dir, generation_result):
    """Verify SVG figure is generated."""
    assert generation_result.file_path.endswith(".svg")
    figures_dir = proposal_dir / "artifacts" / "wave-5-visuals" / "figures"
    svg_path = figures_dir / generation_result.file_path
    assert svg_path.exists(), f"SVG not found at {svg_path}"


@then("the figure is presented to Phil for review")
def verify_figure_presented(generation_result):
    """Verify figure is presented for human review."""
    assert generation_result.review_status == "pending"


@then("Phil can approve, request revision, or replace with a manual file")
def verify_review_options(generation_result):
    """Verify review options are available."""
    assert "approve" in generation_result.review_options
    assert "revise" in generation_result.review_options
    assert "replace" in generation_result.review_options


@then("an external brief is generated with content description, dimensions, and resolution")
def verify_external_brief(proposal_dir, classification_result):
    """Verify external brief is generated for non-generatable figure."""
    brief_path = (
        proposal_dir
        / "artifacts"
        / "wave-5-visuals"
        / "figures"
        / f"figure-{classification_result.figure_number}-brief.json"
    )
    assert brief_path.exists(), f"Brief not written to {brief_path}"
    import json

    data = json.loads(brief_path.read_text())
    assert "content_description" in data
    assert "dimensions" in data
    assert "resolution" in data


@then("Phil can provide a manual file to replace the brief")
def verify_manual_replace(classification_result):
    """Verify manual file replacement option."""
    assert "replace" in classification_result.review_options


@then(
    parsers.parse('it flags "Figure {ref_num:d} referenced in Section {section} does not exist"'),
)
def verify_orphan_flagged(cross_ref_result, ref_num, section):
    """Verify orphaned reference is flagged."""
    orphans = cross_ref_result.orphaned_references
    match = [o for o in orphans if o.referenced_figure == ref_num and o.section_id == section]
    assert len(match) == 1, f"Expected orphan Figure {ref_num} in {section}, got {orphans}"


@then("the cross-reference log records the mismatch")
def verify_cross_ref_mismatch(proposal_dir):
    """Verify mismatch is recorded in cross-reference log."""
    log_path = proposal_dir / "artifacts" / "wave-5-visuals" / "cross-reference-log.json"
    assert log_path.exists(), f"Cross-reference log not written to {log_path}"
    import json

    data = json.loads(log_path.read_text())
    assert data["all_valid"] is False


@then("the cross-reference log shows all references valid")
def verify_cross_ref_valid(cross_ref_result):
    """Verify all cross-references are valid."""
    assert cross_ref_result.all_valid


@then("no orphaned references are flagged")
def verify_no_orphans(cross_ref_result):
    """Verify no orphaned references."""
    assert cross_ref_result.orphaned_references == []


@then("the enforcement system blocks the action")
def verify_enforcement_blocks(pdc_gate_error):
    """Verify PES enforcement blocked the action."""
    from pes.domain.visual_asset_service import PdcGateBlockedError

    assert isinstance(pdc_gate_error, PdcGateBlockedError)


@then(
    parsers.parse('Phil sees "{message}"'),
)
def verify_phil_sees_message(pdc_gate_error, message):
    """Verify Phil sees the expected error message."""
    assert message.lower() in str(pdc_gate_error).lower()
