"""Common steps shared across all Corpus Image Reuse acceptance features.

These steps handle shared preconditions like system availability
and registry setup.
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, then

from tests.acceptance.corpus_image_reuse.fakes import (
    InMemoryImageRegistryAdapter,
)


@given("the image extraction system is available")
def image_system_available():
    """System availability -- satisfied by test fixtures.

    In acceptance tests, the system is 'available' when the extraction service,
    registry adapter, and extractor adapter are instantiated with test fixtures.
    """
    pass


@given(
    parsers.parse(
        'the image catalog contains {count:d} images from {n:d} proposals'
    ),
)
def catalog_has_n_images(
    count: int,
    n: int,
    image_registry: InMemoryImageRegistryAdapter,
    image_context: dict[str, Any],
):
    """Populate the registry with N images from M proposals."""
    # Store expected counts for later assertions
    image_context["expected_total"] = count
    image_context["expected_proposals"] = n


@given("the image catalog is empty")
def catalog_is_empty(
    image_registry: InMemoryImageRegistryAdapter,
):
    """Ensure the registry has no entries."""
    assert image_registry.entry_count == 0


@given(
    parsers.parse(
        'the image catalog does not contain image "{image_id}"'
    ),
)
def catalog_missing_image(
    image_id: str,
    image_registry: InMemoryImageRegistryAdapter,
):
    """Ensure a specific image ID is not in the registry."""
    assert image_registry.get_by_id(image_id) is None


# --- Shared Then steps ---


@then(parsers.parse('the result shows "{message}"'))
def result_shows_message(message: str, image_context: dict[str, Any]):
    """Verify a specific message in the operation result."""
    result = image_context.get("result")
    assert result is not None, "No result captured in context"
    result_message = str(result.get("message", ""))
    assert message.lower() in result_message.lower(), (
        f"Expected '{message}' in result message: '{result_message}'"
    )


@then(parsers.parse('the ingestion report shows "{message}"'))
def ingestion_report_shows(message: str, image_context: dict[str, Any]):
    """Verify the ingestion report contains a specific message."""
    report = image_context.get("ingestion_report", "")
    assert message.lower() in str(report).lower(), (
        f"Expected '{message}' in ingestion report: '{report}'"
    )
