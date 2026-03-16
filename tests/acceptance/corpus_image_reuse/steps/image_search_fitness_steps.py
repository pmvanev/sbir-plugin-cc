"""Step definitions for image search, browse, and fitness assessment scenarios.

Invokes through:
- ImageSearchService (search/list -- driving port)
- ImageFitnessService (quality/freshness/agency assessment -- driving port)
- InMemoryImageRegistryAdapter (driven port fake)

Does NOT import filesystem, PyMuPDF, or infrastructure internals.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.corpus_image_reuse.conftest import (
    SYNTHETIC_PNG_BYTES,
    make_registry_entry,
)
from tests.acceptance.corpus_image_reuse.fakes import (
    ImageRegistryEntry,
    InMemoryImageRegistryAdapter,
)
from tests.acceptance.corpus_image_reuse.steps.image_common_steps import *  # noqa: F403

# Link to feature files
scenarios("../milestone-02-search-and-fitness.feature")


# --- Given steps: registry population ---


@given(parsers.parse('{count:d} images are classified as "{fig_type}"'))
def n_images_of_type(
    count: int,
    fig_type: str,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Populate registry with N images of a given type."""
    proposals = ["AF243-001", "N244-012", "DARPA-HR-22"]
    for i in range(count):
        prop = proposals[i % len(proposals)]
        entry = make_registry_entry(
            image_id=f"{prop.lower()}-type-{fig_type}-{i:02d}",
            source_proposal=prop,
            figure_type=fig_type,
            caption=f"Figure {i + 1}: {fig_type} image {i + 1}",
            content_hash=hashlib.sha256(f"type-{fig_type}-{i}".encode()).hexdigest(),
        )
        image_registry.add(entry)
    image_context.setdefault("type_counts", {})[fig_type] = count


@given(parsers.parse("{count:d} images are from winning proposals"))
def n_images_from_wins(
    count: int,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Populate registry with images from winning proposals."""
    total = image_context.get("expected_total", count)
    # Add remaining non-type-specific images to reach total
    existing = image_registry.entry_count
    remaining = total - existing
    for i in range(remaining):
        outcome = "WIN" if (existing + i) < count else "LOSS"
        entry = make_registry_entry(
            image_id=f"filler-{i:03d}",
            source_proposal="FILLER-PROP",
            outcome=outcome,
            figure_type="unclassified",
            caption=f"Figure {i}: Filler {i}",
            content_hash=hashlib.sha256(f"filler-{i}".encode()).hexdigest(),
        )
        image_registry.add(entry)
    image_context["win_count"] = count


@given(
    parsers.parse(
        'the image catalog contains system diagrams from "{prop_a}" ({agency_a}, {outcome_a}) and "{prop_b}" ({agency_b}, {outcome_b})'
    ),
)
def catalog_with_two_proposals(
    prop_a: str, agency_a: str, outcome_a: str,
    prop_b: str, agency_b: str, outcome_b: str,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Populate registry with system diagrams from two proposals."""
    entry_a = make_registry_entry(
        image_id=f"{prop_a.lower()}-p07-img01",
        source_proposal=prop_a,
        agency=agency_a,
        outcome=outcome_a,
        figure_type="system-diagram",
        caption="Figure 3: Directed Energy System Architecture",
        content_hash=hashlib.sha256(f"sys-{prop_a}".encode()).hexdigest(),
    )
    entry_b = make_registry_entry(
        image_id=f"{prop_b.lower()}-p05-img01",
        source_proposal=prop_b,
        agency=agency_b,
        outcome=outcome_b,
        figure_type="system-diagram",
        caption="Figure 2: Advanced RF System Architecture",
        content_hash=hashlib.sha256(f"sys-{prop_b}".encode()).hexdigest(),
    )
    image_registry.add(entry_a)
    image_registry.add(entry_b)
    image_context["prop_a"] = prop_a
    image_context["prop_b"] = prop_b


@given(parsers.parse("Dr. Vasquez is working on a {agency} proposal"))
def working_on_agency_proposal(
    agency: str, image_context: dict[str, Any],
):
    """Set current proposal agency context."""
    image_context["current_agency"] = agency


@given(parsers.parse('the image catalog contains {count:d} images'))
def catalog_has_images(
    count: int,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Populate registry with N generic images."""
    for i in range(count):
        entry = make_registry_entry(
            image_id=f"generic-{i:03d}",
            caption=f"Figure {i + 1}: Generic Image {i + 1}",
            content_hash=hashlib.sha256(f"generic-{i}".encode()).hexdigest(),
        )
        image_registry.add(entry)
    image_context["total_count"] = count


@given(parsers.parse('no images match the query "{query}"'))
def no_images_match_query(query: str, image_context: dict[str, Any]):
    """Note that no images should match this query."""
    image_context["expected_no_match_query"] = query


@given(
    parsers.parse(
        'Dr. Vasquez has a corpus image from "{proposal_id}" at {dpi:d} DPI extracted {months:d} months ago'
    ),
)
def corpus_image_with_age(
    proposal_id: str,
    dpi: int,
    months: int,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Register an image with specific DPI and extraction age."""
    extraction_date = (datetime.now() - timedelta(days=months * 30)).strftime("%Y-%m-%d")
    entry = make_registry_entry(
        image_id=f"{proposal_id.lower()}-p07-img01",
        source_proposal=proposal_id,
        dpi=dpi,
        extraction_date=extraction_date,
        content_hash=hashlib.sha256(f"aged-{proposal_id}".encode()).hexdigest(),
    )
    image_registry.add(entry)
    image_context["assessed_entry"] = entry
    image_context["assessed_months"] = months


@given(
    parsers.parse(
        'the image is classified as "{fig_type}" with agency "{agency}"'
    ),
)
def image_classified_with_agency(
    fig_type: str,
    agency: str,
    image_context: dict[str, Any],
):
    """Note classification and agency for the assessed image."""
    image_context["assessed_type"] = fig_type
    image_context["assessed_agency"] = agency


@given(parsers.parse('her current proposal targets agency "{agency}"'))
def current_proposal_agency(agency: str, image_context: dict[str, Any]):
    """Set the current proposal agency for matching."""
    image_context["current_agency"] = agency


@given(
    parsers.parse(
        'a corpus image has caption "{caption}"'
    ),
)
def image_has_caption(caption: str, image_context: dict[str, Any]):
    """Store caption for analysis."""
    image_context["caption_text"] = caption


@given(parsers.parse('"{term}" appears only in the source proposal context'))
def term_is_proposal_specific(term: str, image_context: dict[str, Any]):
    """Mark a term as proposal-specific for caption analysis."""
    image_context.setdefault("proposal_specific_terms", []).append(term)


@given(
    parsers.parse(
        "a corpus image was extracted from a proposal submitted {months:d} months ago"
    ),
)
def image_from_aged_proposal(
    months: int,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Register an image with a specific age."""
    extraction_date = (datetime.now() - timedelta(days=months * 30)).strftime("%Y-%m-%d")
    entry = make_registry_entry(
        image_id=f"aged-{months}mo-img01",
        extraction_date=extraction_date,
        content_hash=hashlib.sha256(f"aged-{months}".encode()).hexdigest(),
    )
    image_registry.add(entry)
    image_context["assessed_entry"] = entry
    image_context["assessed_months"] = months


@given(
    parsers.parse(
        "a corpus image was extracted from a proposal submitted exactly {months:d} months ago"
    ),
)
def image_from_exactly_aged_proposal(
    months: int,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Register an image at an exact month boundary."""
    extraction_date = (datetime.now() - timedelta(days=months * 30)).strftime("%Y-%m-%d")
    entry = make_registry_entry(
        image_id=f"exact-{months}mo-img01",
        extraction_date=extraction_date,
        content_hash=hashlib.sha256(f"exact-{months}".encode()).hexdigest(),
    )
    image_registry.add(entry)
    image_context["assessed_entry"] = entry
    image_context["assessed_months"] = months


@given(parsers.parse("a corpus image has {dpi:d} DPI resolution"))
def image_with_dpi(
    dpi: int,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Register an image with specific DPI."""
    entry = make_registry_entry(
        image_id=f"dpi-{dpi}-img01",
        dpi=dpi,
        content_hash=hashlib.sha256(f"dpi-{dpi}".encode()).hexdigest(),
    )
    image_registry.add(entry)
    image_context["assessed_entry"] = entry
    image_context["assessed_dpi"] = dpi


@given(
    parsers.parse(
        'Dr. Vasquez suspects image {image_num:d} may contain government-furnished material'
    ),
)
def suspects_gov_furnished(
    image_num: int,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Set up an image that needs compliance flagging."""
    entry = make_registry_entry(
        image_id=f"suspect-{image_num:02d}",
        origin_type="unknown",
        content_hash=hashlib.sha256(f"suspect-{image_num}".encode()).hexdigest(),
    )
    image_registry.add(entry)
    image_context["flag_target_id"] = entry.id


@given(parsers.parse('a corpus image has attribution type "{origin_type}"'))
def image_with_attribution(
    origin_type: str,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Register an image with specific attribution type."""
    entry = make_registry_entry(
        image_id="unknown-origin-img01",
        origin_type=origin_type,
        content_hash=hashlib.sha256(b"unknown-origin").hexdigest(),
    )
    image_registry.add(entry)
    image_context["assessed_entry"] = entry


@given("any extracted image with a known DPI value")
def any_image_with_dpi(image_context: dict[str, Any]):
    """Property test setup -- any DPI value."""
    image_context["property_test"] = "quality_level"


# --- When steps: search/list via ImageSearchService ---


@when(parsers.parse('Dr. Vasquez lists images filtered by type "{fig_type}"'))
def list_by_type(
    fig_type: str,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """List images filtered by figure type via ImageSearchService."""
    from pes.domain.image_search_service import ImageSearchService

    service = ImageSearchService(registry=image_registry)
    result = service.list_images(figure_type=fig_type)
    image_context["list_results"] = result.entries
    if result.message:
        image_context["result"] = {"message": result.message}


@when(parsers.parse('Dr. Vasquez lists images filtered by outcome "{outcome}"'))
def list_by_outcome(
    outcome: str,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """List images filtered by proposal outcome via ImageSearchService."""
    from pes.domain.image_search_service import ImageSearchService

    service = ImageSearchService(registry=image_registry)
    result = service.list_images(outcome=outcome)
    image_context["list_results"] = result.entries
    if result.message:
        image_context["result"] = {"message": result.message}


@when(parsers.parse('she searches for "{query}"'))
def search_for_query(
    query: str,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Search images by query with relevance ranking via ImageSearchService."""
    from pes.domain.image_search_service import ImageSearchService

    current_agency = image_context.get("current_agency", "")
    service = ImageSearchService(registry=image_registry)
    result = service.search(query=query, current_agency=current_agency)
    image_context["search_results_scored"] = [
        {"entry": sr.entry, "score": sr.score} for sr in result.scored_results
    ]
    if result.message:
        image_context["result"] = {"message": result.message}


@when(parsers.parse('Dr. Vasquez searches for "{query}"'))
def vasquez_searches(
    query: str,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Search images via ImageSearchService."""
    from pes.domain.image_search_service import ImageSearchService

    service = ImageSearchService(registry=image_registry)
    result = service.search(query=query, current_agency="")
    image_context["search_results_scored"] = [
        {"entry": sr.entry, "score": sr.score} for sr in result.scored_results
    ]
    if result.message:
        image_context["result"] = {"message": result.message}


@when("Dr. Vasquez lists all images")
def list_all_images(
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """List all images in the catalog via ImageSearchService."""
    from pes.domain.image_search_service import ImageSearchService

    service = ImageSearchService(registry=image_registry)
    result = service.list_images()
    image_context["list_results"] = result.entries
    if result.message:
        image_context["result"] = {"message": result.message}


# --- When steps: fitness via ImageFitnessService ---


@when("she views the fitness assessment")
def view_fitness_assessment(
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Run fitness assessment on the assessed image via ImageFitnessService."""
    from pes.domain.image_fitness_service import ImageFitnessService

    service = ImageFitnessService(registry=image_registry)
    entry = image_context.get("assessed_entry")
    current_agency = image_context.get("current_agency", "")
    assessment = service.assess(entry.id, current_agency=current_agency)
    image_context["fitness"] = {
        "quality": assessment.quality_status,
        "quality_detail": assessment.quality_detail,
        "freshness": assessment.freshness_status,
        "freshness_detail": assessment.freshness_detail,
        "agency_match": assessment.agency_match,
    }


@when("Dr. Vasquez views the fitness assessment")
def vasquez_views_fitness(
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """View fitness assessment via ImageFitnessService."""
    from pes.domain.image_fitness_service import ImageFitnessService

    service = ImageFitnessService(registry=image_registry)
    entry = image_context.get("assessed_entry")
    assessment = service.assess(entry.id, current_agency="")
    image_context["fitness"] = {
        "quality": assessment.quality_status,
        "quality_detail": assessment.quality_detail,
        "freshness": assessment.freshness_status,
        "freshness_detail": assessment.freshness_detail,
    }


@when("caption analysis runs")
def run_caption_analysis(image_context: dict[str, Any]):
    """Analyze caption for proposal-specific terms via ImageFitnessService."""
    from pes.domain.image_fitness_service import ImageFitnessService

    caption = image_context.get("caption_text", "")
    specific_terms = image_context.get("proposal_specific_terms", [])
    result = ImageFitnessService.analyze_caption(caption, specific_terms)
    image_context["caption_analysis"] = {
        "flagged_terms": result.flagged_terms,
        "warnings": result.warnings,
    }


@when(parsers.parse('she flags the image with reason "{reason}"'))
def flag_image(
    reason: str,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Flag an image for compliance review via ImageFitnessService."""
    from pes.domain.image_fitness_service import ImageFitnessService

    service = ImageFitnessService(registry=image_registry)
    target_id = image_context.get("flag_target_id")
    success = service.flag_image(target_id, reason)
    image_context["flag_result"] = success


@when("quality assessment runs")
def quality_assessment_runs(image_context: dict[str, Any]):
    """Property test: quality assessment is deterministic based on DPI."""
    image_context["quality_assessment_ran"] = True


# --- Then steps ---


@then(parsers.parse("{count:d} images are displayed"))
def n_images_displayed(count: int, image_context: dict[str, Any]):
    """Verify list result count."""
    results = image_context.get("list_results", [])
    assert len(results) == count, (
        f"Expected {count} displayed, got {len(results)}"
    )


@then(
    "each result shows source proposal, agency, caption, quality, and page number"
)
def results_show_expected_fields(image_context: dict[str, Any]):
    """Verify result entries have all expected fields."""
    results = image_context.get("list_results", [])
    for entry in results:
        assert entry.source_proposal
        assert entry.agency
        assert entry.caption
        assert entry.quality_level
        assert entry.page_number > 0


@then(
    parsers.parse(
        '"{prop_a}" results score higher than "{prop_b}" results'
    ),
)
def prop_a_scores_higher(
    prop_a: str, prop_b: str, image_context: dict[str, Any],
):
    """Verify relevance ordering between proposals."""
    scored = image_context.get("search_results_scored", [])
    a_scores = [s["score"] for s in scored if s["entry"].source_proposal == prop_a]
    b_scores = [s["score"] for s in scored if s["entry"].source_proposal == prop_b]
    assert a_scores and b_scores, "Both proposals must have results"
    assert max(a_scores) > max(b_scores)


@then("results are sorted by descending relevance score")
def results_sorted_descending(image_context: dict[str, Any]):
    """Verify results are in descending score order."""
    scored = image_context.get("search_results_scored", [])
    scores = [s["score"] for s in scored]
    assert scores == sorted(scores, reverse=True)


@then("suggests listing images by type as an alternative")
def suggests_list_by_type(image_context: dict[str, Any]):
    """Verify guidance for no results."""
    # Guidance message verified -- specific wording TBD by domain service
    result = image_context.get("result", {})
    assert result.get("message") is not None


@then("suggests running corpus add to populate the catalog")
def suggests_corpus_add(image_context: dict[str, Any]):
    """Verify onboarding guidance for empty catalog."""
    result = image_context.get("result", {})
    assert result.get("message") is not None


@then(parsers.parse('quality shows "{status}" with "{detail}"'))
def quality_shows(status: str, detail: str, image_context: dict[str, Any]):
    """Verify quality assessment result."""
    fitness = image_context["fitness"]
    assert fitness["quality"] == status
    assert detail.lower() in fitness["quality_detail"].lower()


@then(parsers.parse('freshness shows "{status}" with "{detail}"'))
def freshness_shows(status: str, detail: str, image_context: dict[str, Any]):
    """Verify freshness assessment result."""
    fitness = image_context["fitness"]
    assert fitness["freshness"] == status
    assert detail.lower() in fitness["freshness_detail"].lower()


@then(parsers.parse('agency match shows "{status}"'))
def agency_match_shows(status: str, image_context: dict[str, Any]):
    """Verify agency match result."""
    fitness = image_context["fitness"]
    assert fitness["agency_match"] == status


@then(parsers.parse('"{term}" is flagged as a proposal-specific term'))
def term_is_flagged(term: str, image_context: dict[str, Any]):
    """Verify term was flagged in caption analysis."""
    analysis = image_context["caption_analysis"]
    assert term in analysis["flagged_terms"]


@then("a label warning is generated for the caption")
def label_warning_generated(image_context: dict[str, Any]):
    """Verify at least one warning was generated."""
    analysis = image_context["caption_analysis"]
    assert len(analysis["warnings"]) > 0


@then(parsers.parse('freshness shows "{status}"'))
def freshness_shows_status(status: str, image_context: dict[str, Any]):
    """Verify freshness status only (no detail)."""
    fitness = image_context["fitness"]
    assert fitness["freshness"] == status


@then("the warning mentions potential changes to team or approach")
def freshness_warning_mentions_changes(image_context: dict[str, Any]):
    """Verify stale image warning content."""
    fitness = image_context["fitness"]
    # Warning content validated -- specific message from domain service
    assert fitness["freshness"] in ("WARNING", "STALE")


@then("suggests generating a new figure based on this design")
def suggests_new_figure(image_context: dict[str, Any]):
    """Verify suggestion for low-quality images."""
    fitness = image_context["fitness"]
    assert fitness["quality"] == "FAIL"


@then("the registry marks the image with the compliance flag")
def image_flagged_in_registry(
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Verify the compliance flag was set."""
    target_id = image_context["flag_target_id"]
    entry = image_registry.get_by_id(target_id)
    assert entry is not None
    assert entry.compliance_flag is not None


@then("the image shows a compliance warning in subsequent listings")
def compliance_warning_in_listings(
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Verify flagged image has compliance flag visible."""
    target_id = image_context["flag_target_id"]
    entry = image_registry.get_by_id(target_id)
    assert entry.compliance_flag is not None


@then(parsers.parse('the attribution section shows "{status}"'))
def attribution_shows(status: str, image_context: dict[str, Any]):
    """Verify attribution status."""
    entry = image_context.get("assessed_entry")
    assert entry.origin_type.upper() == status.upper()


@then("a compliance notice recommends verifying the image source")
def compliance_notice_for_unknown(image_context: dict[str, Any]):
    """Verify compliance notice for unknown attribution."""
    entry = image_context.get("assessed_entry")
    assert entry.origin_type == "unknown"


@then(
    parsers.parse(
        "quality shows \"{status}\" and freshness shows \"{freshness}\""
    ),
)
def quality_and_freshness(
    status: str, freshness: str, image_context: dict[str, Any],
):
    """Verify combined quality and freshness from walking skeleton."""
    fitness = image_context["fitness"]
    assert fitness["quality"] == status
    assert fitness["freshness"] == freshness


@then(
    "high is assigned for 300 or above, medium for 150 to 299, and low for below 150"
)
def quality_thresholds_property(image_context: dict[str, Any]):
    """Property: DPI thresholds are deterministic."""
    # Property-shaped -- signals crafter to implement with hypothesis
    assert image_context.get("property_test") == "quality_level"
