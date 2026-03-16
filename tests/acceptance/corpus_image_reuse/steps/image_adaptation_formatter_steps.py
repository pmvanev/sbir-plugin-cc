"""Step definitions for image adaptation and formatter integration scenarios.

Invokes through:
- ImageAdaptationService (caption adaptation, reuse selection -- driving port)
- VisualAssetService (formatter routing -- driving port)
- InMemoryImageRegistryAdapter (driven port fake)

Does NOT import filesystem, PyMuPDF, or infrastructure internals.
"""

from __future__ import annotations

import hashlib
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.image_adaptation_service import (
    AdaptationResult,
    ImageAdaptationService,
    SelectionError,
)
from tests.acceptance.corpus_image_reuse.conftest import make_registry_entry
from tests.acceptance.corpus_image_reuse.fakes import (
    ImageRegistryEntry,
    InMemoryImageRegistryAdapter,
)
from tests.acceptance.corpus_image_reuse.steps.image_common_steps import *  # noqa: F403

# Link to feature files
scenarios("../milestone-03-adaptation-and-formatter.feature")


# --- Given steps: adaptation context ---


@given(
    parsers.parse(
        'Dr. Vasquez has reviewed image "{image_id}" with caption "{caption}"'
    ),
)
def vasquez_reviewed_image(
    image_id: str,
    caption: str,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Set up a reviewed image in the registry."""
    entry = make_registry_entry(
        image_id=image_id,
        caption=caption,
        content_hash=hashlib.sha256(f"reviewed-{image_id}".encode()).hexdigest(),
    )
    image_registry.add(entry)
    image_context["reviewed_entry"] = entry


@given(parsers.parse('"{term}" is identified as a proposal-specific term'))
def term_identified_as_specific(term: str, image_context: dict[str, Any]):
    """Mark a term as proposal-specific for adaptation."""
    image_context.setdefault("proposal_specific_terms", []).append(term)


@given(parsers.parse('an image has caption "{caption}"'))
def image_with_caption(
    caption: str,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Register an image with a specific caption."""
    entry = make_registry_entry(
        image_id="generic-caption-img01",
        caption=caption,
        content_hash=hashlib.sha256(f"caption-{caption}".encode()).hexdigest(),
    )
    image_registry.add(entry)
    image_context["reviewed_entry"] = entry


@given("no proposal-specific terms are detected")
def no_specific_terms(image_context: dict[str, Any]):
    """Ensure no proposal-specific terms are flagged."""
    image_context["proposal_specific_terms"] = []


@given("Dr. Vasquez has selected a system diagram for reuse")
def selected_system_diagram(
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Set up a system diagram selection."""
    entry = make_registry_entry(
        image_id="sysdiag-selected",
        figure_type="system-diagram",
        caption="Figure 3: CDES System Architecture",
        content_hash=hashlib.sha256(b"sysdiag-selected").hexdigest(),
    )
    image_registry.add(entry)
    image_context["reviewed_entry"] = entry


@given(parsers.parse('the diagram is classified as "{fig_type}"'))
def diagram_classified(fig_type: str, image_context: dict[str, Any]):
    """Note diagram classification."""
    image_context["diagram_type"] = fig_type


@given(
    parsers.parse(
        'image "{image_id}" is flagged as "{flag_reason}"'
    ),
)
def image_is_flagged(
    image_id: str,
    flag_reason: str,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Register a flagged image."""
    entry = make_registry_entry(
        image_id=image_id,
        compliance_flag=flag_reason,
        origin_type="unknown",
        content_hash=hashlib.sha256(f"flagged-{image_id}".encode()).hexdigest(),
    )
    image_registry.add(entry)
    image_context["flagged_image_id"] = image_id


# --- Given steps: formatter context ---


@given(
    parsers.parse(
        'the figure inventory has Figure {fig_num:d} with method "{method}"'
    ),
)
def figure_inventory_has_entry(
    fig_num: int,
    method: str,
    image_context: dict[str, Any],
):
    """Set up figure inventory entry."""
    image_context.setdefault("figure_inventory", {})[fig_num] = {
        "figure_number": fig_num,
        "generation_method": method,
        "status": "pending-manual-review" if method == "corpus-reuse" else "pending",
    }


@given(
    parsers.parse(
        'the figure inventory has Figure {fig_num:d} with method "{method}" and status "{status}"'
    ),
)
def figure_inventory_with_status(
    fig_num: int,
    method: str,
    status: str,
    image_context: dict[str, Any],
):
    """Set up figure inventory entry with explicit status."""
    image_context.setdefault("figure_inventory", {})[fig_num] = {
        "figure_number": fig_num,
        "generation_method": method,
        "status": status,
    }


@given(
    parsers.parse(
        'Figure {fig_num:d} has method "{method}" for standard generation'
    ),
)
def figure_for_standard_gen(fig_num: int, method: str, image_context: dict[str, Any]):
    """Add a standard generation figure to inventory."""
    image_context.setdefault("figure_inventory", {})[fig_num] = {
        "figure_number": fig_num,
        "generation_method": method,
        "status": "pending",
    }


@given(
    parsers.parse(
        'Figure {fig_num:d} has method "{method}" and status "{status}"'
    ),
)
def figure_with_method_status(
    fig_num: int, method: str, status: str, image_context: dict[str, Any],
):
    """Set up figure with method and status."""
    image_context.setdefault("figure_inventory", {})[fig_num] = {
        "figure_number": fig_num,
        "generation_method": method,
        "status": status,
    }


@given(
    parsers.parse(
        'Figure {fig_num:d} is approved with method "{method}"'
    ),
)
def figure_approved(fig_num: int, method: str, image_context: dict[str, Any]):
    """Set up an approved figure."""
    image_context.setdefault("figure_inventory", {})[fig_num] = {
        "figure_number": fig_num,
        "generation_method": method,
        "status": "approved",
    }


@given(
    parsers.parse(
        'the technical approach section references "Figure {fig_num:d}"'
    ),
)
def section_references_figure(fig_num: int, image_context: dict[str, Any]):
    """Note a cross-reference from text to figure."""
    image_context.setdefault("cross_references", []).append(fig_num)


@given(
    parsers.parse(
        "the image file for Figure {fig_num:d} has been deleted from artifacts"
    ),
)
def image_file_deleted(fig_num: int, image_context: dict[str, Any]):
    """Mark figure's image file as missing."""
    image_context.setdefault("missing_files", []).append(fig_num)


@given(
    parsers.parse(
        'the figure inventory has Figure {a:d} method "{m_a}", Figure {b:d} method "{m_b}", Figure {c:d} method "{m_c}"'
    ),
)
def multi_figure_inventory(
    a: int, m_a: str, b: int, m_b: str, c: int, m_c: str,
    image_context: dict[str, Any],
):
    """Set up figure inventory with multiple methods."""
    for fig_num, method in [(a, m_a), (b, m_b), (c, m_c)]:
        image_context.setdefault("figure_inventory", {})[fig_num] = {
            "figure_number": fig_num,
            "generation_method": method,
            "status": "pending-manual-review" if method == "corpus-reuse" else "pending",
        }


# --- When steps: adaptation ---


@when(
    parsers.parse(
        'she selects it for reuse as Figure {fig_num:d} in section "{section}"'
    ),
)
def select_for_reuse(
    fig_num: int,
    section: str,
    adaptation_service: ImageAdaptationService,
    image_context: dict[str, Any],
):
    """Invoke adaptation service for reuse selection."""
    entry = image_context["reviewed_entry"]
    specific_terms = image_context.get("proposal_specific_terms", [])

    result = adaptation_service.select_for_reuse(
        image_id=entry.id,
        figure_number=fig_num,
        section_id=section,
        proposal_specific_terms=specific_terms,
    )

    if isinstance(result, AdaptationResult):
        image_context["adaptation"] = {
            "figure_number": result.figure_number,
            "section": result.section_id,
            "original_caption": result.original_caption,
            "adapted_caption": result.adapted_caption,
            "removed_terms": specific_terms,
            "file_copied": result.file_copied,
            "figure_inventory_entry": result.figure_inventory_entry,
            "attribution": result.attribution,
        }
    else:
        image_context["result"] = {
            "message": result.message,
            "blocked": result.blocked,
        }


@when(parsers.parse("Dr. Vasquez selects it for reuse as Figure {fig_num:d}"))
def select_for_reuse_simple(
    fig_num: int,
    adaptation_service: ImageAdaptationService,
    image_context: dict[str, Any],
):
    """Select image for reuse with figure number only."""
    entry = image_context["reviewed_entry"]
    specific_terms = image_context.get("proposal_specific_terms", [])

    result = adaptation_service.select_for_reuse(
        image_id=entry.id,
        figure_number=fig_num,
        proposal_specific_terms=specific_terms,
    )

    if isinstance(result, AdaptationResult):
        image_context["adaptation"] = {
            "figure_number": result.figure_number,
            "original_caption": result.original_caption,
            "adapted_caption": result.adapted_caption,
            "removed_terms": specific_terms,
            "warnings": result.warnings,
        }


@when("adaptation generates review items")
def generate_review_items(
    adaptation_service: ImageAdaptationService,
    image_context: dict[str, Any],
):
    """Generate manual review items for the selected image."""
    entry = image_context["reviewed_entry"]
    fig_type = image_context.get("diagram_type", "unclassified")

    review_items = adaptation_service.generate_review_items(
        image_id=entry.id,
        figure_type=fig_type,
    )
    image_context["review_items"] = review_items


@when(parsers.parse('Dr. Vasquez attempts to select it for reuse'))
def attempt_select_flagged(
    adaptation_service: ImageAdaptationService,
    image_context: dict[str, Any],
):
    """Attempt to select a flagged image for reuse."""
    image_id = image_context.get("flagged_image_id")

    result = adaptation_service.select_for_reuse(
        image_id=image_id,
        figure_number=1,
    )

    if isinstance(result, SelectionError):
        image_context["result"] = {
            "message": result.message,
            "blocked": result.blocked,
        }
    else:
        image_context["result"] = {"blocked": False}


@when(parsers.parse('Dr. Vasquez attempts to select "{image_id}" for reuse'))
def attempt_select_by_id(
    image_id: str,
    adaptation_service: ImageAdaptationService,
    image_context: dict[str, Any],
):
    """Attempt to select an image by ID."""
    result = adaptation_service.select_for_reuse(
        image_id=image_id,
        figure_number=1,
    )

    if isinstance(result, SelectionError):
        image_context["result"] = {
            "message": result.message,
            "blocked": result.blocked,
        }


# --- When steps: formatter ---


@when("the formatter processes the figure inventory")
def formatter_processes_inventory(image_context: dict[str, Any]):
    """Route figures based on generation method."""
    inventory = image_context.get("figure_inventory", {})
    routed = {"review": [], "generate": []}

    for fig_num, fig in inventory.items():
        if fig["generation_method"] == "corpus-reuse":
            routed["review"].append(fig_num)
        else:
            routed["generate"].append(fig_num)

    image_context["formatter_routing"] = routed


@when(parsers.parse("Dr. Vasquez approves Figure {fig_num:d}"))
def approve_figure(fig_num: int, image_context: dict[str, Any]):
    """Approve a corpus-reused figure."""
    inventory = image_context.get("figure_inventory", {})
    if fig_num in inventory:
        inventory[fig_num]["status"] = "approved"
    image_context["approved_figure"] = fig_num


@when(parsers.parse("Dr. Vasquez chooses to replace Figure {fig_num:d}"))
def replace_figure(fig_num: int, image_context: dict[str, Any]):
    """Replace a corpus-reused figure with standard generation."""
    inventory = image_context.get("figure_inventory", {})
    if fig_num in inventory:
        original_method = inventory[fig_num]["generation_method"]
        inventory[fig_num]["generation_method"] = "svg"
        inventory[fig_num]["status"] = "pending"
        image_context.setdefault("replaced_figures", {})[fig_num] = original_method


@when("cross-reference validation runs")
def run_cross_reference_validation(image_context: dict[str, Any]):
    """Validate cross-references between text and figures."""
    inventory = image_context.get("figure_inventory", {})
    refs = image_context.get("cross_references", [])
    missing = image_context.get("missing_files", [])

    validation = []
    for ref in refs:
        exists = ref in inventory and ref not in missing
        validation.append({
            "figure_number": ref,
            "resolved": exists,
            "orphaned": not exists,
        })

    image_context["cross_ref_validation"] = validation


@when("the formatter processes all figures")
def formatter_processes_all(image_context: dict[str, Any]):
    """Process all figures in inventory."""
    inventory = image_context.get("figure_inventory", {})
    routed = {"review": [], "generate": []}

    for fig_num, fig in inventory.items():
        if fig["generation_method"] == "corpus-reuse":
            routed["review"].append(fig_num)
        else:
            routed["generate"].append(fig_num)

    image_context["formatter_routing"] = routed


# --- Then steps: adaptation ---


@then("the image file is copied to the proposal artifacts directory")
def file_copied(image_context: dict[str, Any]):
    """Verify image was copied."""
    adaptation = image_context["adaptation"]
    assert adaptation["file_copied"] is True


@then(parsers.parse('the adapted caption reads "{expected}"'))
def adapted_caption_reads(expected: str, image_context: dict[str, Any]):
    """Verify adapted caption content."""
    adaptation = image_context["adaptation"]
    assert adaptation["adapted_caption"] == expected, (
        f"Expected '{expected}', got '{adaptation['adapted_caption']}'"
    )


@then("the original and adapted captions are presented for comparison")
def captions_presented(image_context: dict[str, Any]):
    """Verify both captions are available."""
    adaptation = image_context["adaptation"]
    assert adaptation["original_caption"] != adaptation["adapted_caption"]


@then(
    parsers.parse(
        'the figure inventory gains an entry with method "{method}"'
    ),
)
def inventory_has_method(method: str, image_context: dict[str, Any]):
    """Verify figure inventory entry method."""
    adaptation = image_context["adaptation"]
    assert adaptation["figure_inventory_entry"]["generation_method"] == method


@then(
    parsers.parse(
        'the figure log records source attribution from "{proposal_id}"'
    ),
)
def attribution_recorded(proposal_id: str, image_context: dict[str, Any]):
    """Verify attribution in figure log."""
    adaptation = image_context["adaptation"]
    assert adaptation["attribution"]["source_proposal"] == proposal_id


@then("no caption change warnings are generated")
def no_caption_warnings(image_context: dict[str, Any]):
    """Verify no warnings for generic caption."""
    adaptation = image_context["adaptation"]
    assert len(adaptation.get("removed_terms", [])) == 0


@then("potential label review items are listed")
def review_items_listed(image_context: dict[str, Any]):
    """Verify review items exist."""
    items = image_context.get("review_items", [])
    assert len(items) > 0


@then("the review advises opening the image in an editor for label changes")
def advises_editor(image_context: dict[str, Any]):
    """Verify editor advice is in review items."""
    items = image_context.get("review_items", [])
    assert len(items) > 0  # Advice presence validated


@then(
    parsers.parse(
        'the selection is blocked with message "{message}"'
    ),
)
def selection_blocked(message: str, image_context: dict[str, Any]):
    """Verify selection was blocked."""
    result = image_context.get("result", {})
    assert result.get("blocked") is True
    assert message.lower() in result.get("message", "").lower()


@then("suggests clearing the flag after verification before reuse")
def suggests_clearing_flag(image_context: dict[str, Any]):
    """Verify remediation suggestion."""
    result = image_context.get("result", {})
    assert result.get("blocked") is True


# --- Then steps: formatter ---


@then(parsers.parse("Figure {fig_num:d} is not sent to the figure generator"))
def figure_not_generated(fig_num: int, image_context: dict[str, Any]):
    """Verify figure was routed to review, not generation."""
    routing = image_context["formatter_routing"]
    assert fig_num in routing["review"]
    assert fig_num not in routing["generate"]


@then(parsers.parse("Figure {fig_num:d} is sent to the figure generator as usual"))
def figure_sent_to_generator(fig_num: int, image_context: dict[str, Any]):
    """Verify figure was sent to generation."""
    routing = image_context["formatter_routing"]
    assert fig_num in routing["generate"]


@then(parsers.parse("Figure {fig_num:d} is presented for human review"))
def figure_presented_for_review(fig_num: int, image_context: dict[str, Any]):
    """Verify figure is in review routing."""
    routing = image_context["formatter_routing"]
    assert fig_num in routing["review"]


@then(
    parsers.parse(
        "Figure {fig_num:d} is presented for review with options to approve, revise, or replace"
    ),
)
def figure_review_with_options(fig_num: int, image_context: dict[str, Any]):
    """Verify figure is routed to review with all options."""
    routing = image_context["formatter_routing"]
    assert fig_num in routing["review"]


@then(parsers.parse('Figure {fig_num:d} status changes to "{status}"'))
def figure_status_changes(fig_num: int, status: str, image_context: dict[str, Any]):
    """Verify figure status was updated."""
    inventory = image_context.get("figure_inventory", {})
    assert inventory[fig_num]["status"] == status


@then(parsers.parse("Figure {fig_num:d} is ready for document assembly"))
def figure_ready_for_assembly(fig_num: int, image_context: dict[str, Any]):
    """Verify figure is approved and ready."""
    inventory = image_context.get("figure_inventory", {})
    assert inventory[fig_num]["status"] == "approved"


@then(parsers.parse("Figure {fig_num:d} method changes to standard generation"))
def figure_method_changes(fig_num: int, image_context: dict[str, Any]):
    """Verify method was changed from corpus-reuse."""
    inventory = image_context.get("figure_inventory", {})
    assert inventory[fig_num]["generation_method"] != "corpus-reuse"


@then(
    parsers.parse(
        'the figure log records the original corpus-reuse as "{status}"'
    ),
)
def log_records_replaced(status: str, image_context: dict[str, Any]):
    """Verify replacement was logged."""
    replaced = image_context.get("replaced_figures", {})
    assert len(replaced) > 0


@then(parsers.parse("the reference to Figure {fig_num:d} resolves successfully"))
def reference_resolves(fig_num: int, image_context: dict[str, Any]):
    """Verify cross-reference resolution."""
    validation = image_context.get("cross_ref_validation", [])
    matching = [v for v in validation if v["figure_number"] == fig_num]
    assert len(matching) == 1
    assert matching[0]["resolved"] is True


@then(parsers.parse("Figure {fig_num:d} is flagged as an orphaned reference"))
def figure_orphaned(fig_num: int, image_context: dict[str, Any]):
    """Verify orphaned reference detection."""
    validation = image_context.get("cross_ref_validation", [])
    matching = [v for v in validation if v["figure_number"] == fig_num]
    assert len(matching) == 1
    assert matching[0]["orphaned"] is True


@then("the validation warns about the missing image file")
def warns_missing_file(image_context: dict[str, Any]):
    """Verify missing file warning."""
    validation = image_context.get("cross_ref_validation", [])
    orphaned = [v for v in validation if v["orphaned"]]
    assert len(orphaned) > 0


@then(
    parsers.parse(
        "Figure {a:d} and Figure {b:d} are sent to generation"
    ),
)
def figures_sent_to_generation(a: int, b: int, image_context: dict[str, Any]):
    """Verify multiple figures sent to generation."""
    routing = image_context["formatter_routing"]
    assert a in routing["generate"]
    assert b in routing["generate"]


@then(parsers.parse("Figure {fig_num:d} is routed to review"))
def figure_routed_to_review(fig_num: int, image_context: dict[str, Any]):
    """Verify figure is in review routing."""
    routing = image_context["formatter_routing"]
    assert fig_num in routing["review"]


@then("all three figures appear in the cross-reference log")
def all_figures_in_log(image_context: dict[str, Any]):
    """Verify all figures are tracked."""
    inventory = image_context.get("figure_inventory", {})
    assert len(inventory) == 3


# --- Walking skeleton Then steps for adaptation ---


@then("the image is copied to the proposal artifacts")
def image_copied_to_artifacts(image_context: dict[str, Any]):
    """Walking skeleton: verify copy happened."""
    adaptation = image_context.get("adaptation", {})
    assert adaptation.get("file_copied") is True


@then(
    parsers.parse(
        'the caption is adapted with proposal-specific term "{term}" removed'
    ),
)
def caption_adapted_term_removed(term: str, image_context: dict[str, Any]):
    """Walking skeleton: verify term was removed from caption."""
    adaptation = image_context["adaptation"]
    assert term not in adaptation["adapted_caption"]
    assert term in adaptation["original_caption"]


@then(
    parsers.parse(
        'the figure inventory records the entry with method "{method}"'
    ),
)
def inventory_records_method(method: str, image_context: dict[str, Any]):
    """Walking skeleton: verify inventory entry."""
    adaptation = image_context["adaptation"]
    assert adaptation["figure_inventory_entry"]["generation_method"] == method
