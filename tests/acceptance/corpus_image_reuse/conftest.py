"""Acceptance test conftest -- fixtures for Corpus Image Reuse BDD scenarios.

All acceptance tests invoke through driving ports only:
- ImageExtractionService (extraction orchestration -- driving port)
- ImageSearchService (search/list -- driving port)
- ImageFitnessService (quality/freshness assessment -- driving port)
- ImageAdaptationService (caption adaptation, reuse selection -- driving port)

External dependencies (PyMuPDF, python-docx, filesystem) are replaced with
in-memory fakes. Domain logic uses production code.
"""

from __future__ import annotations

import hashlib
from typing import Any

import pytest

from pes.domain.image_adaptation_service import ImageAdaptationService
from tests.acceptance.corpus_image_reuse.fakes import (
    ImageRegistryEntry,
    InMemoryImageExtractorAdapter,
    InMemoryImageRegistryAdapter,
    RawExtractedImage,
)

# Synthetic image bytes for test fixtures (tiny valid-ish PNG/JPEG headers)
SYNTHETIC_PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
SYNTHETIC_JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 100


# ---------------------------------------------------------------------------
# In-Memory Adapter Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def image_extractor() -> InMemoryImageExtractorAdapter:
    """In-memory image extractor replacing PyMuPDF/python-docx adapters."""
    return InMemoryImageExtractorAdapter()


@pytest.fixture()
def image_registry() -> InMemoryImageRegistryAdapter:
    """In-memory image registry replacing filesystem JSON adapter."""
    return InMemoryImageRegistryAdapter()


@pytest.fixture()
def adaptation_service(
    image_registry: InMemoryImageRegistryAdapter,
) -> ImageAdaptationService:
    """ImageAdaptationService wired to in-memory registry."""
    return ImageAdaptationService(registry=image_registry)


# ---------------------------------------------------------------------------
# Result Context Container
# ---------------------------------------------------------------------------


@pytest.fixture()
def image_context() -> dict[str, Any]:
    """Mutable container to hold operation results across steps."""
    return {}


# ---------------------------------------------------------------------------
# Sample Image Data Fixtures
# ---------------------------------------------------------------------------


def make_raw_image(
    page: int = 7,
    index: int = 1,
    dpi: int = 300,
    width: int = 2048,
    height: int = 1536,
    caption: str = "Figure 3: CDES System Architecture",
    surrounding_text: str = "The proposed approach leverages...",
    fmt: str = "png",
    content: bytes | None = None,
) -> RawExtractedImage:
    """Build a RawExtractedImage for test scenarios."""
    return RawExtractedImage(
        image_bytes=content or SYNTHETIC_PNG_BYTES,
        format=fmt,
        page_number=page,
        position_index=index,
        width=width,
        height=height,
        dpi=dpi,
        caption=caption,
        surrounding_text=surrounding_text,
    )


def make_registry_entry(
    image_id: str = "af243-001-p07-img01",
    source_proposal: str = "AF243-001",
    agency: str = "USAF",
    outcome: str = "WIN",
    page_number: int = 7,
    caption: str = "Figure 3: CDES System Architecture",
    surrounding_text: str = "The proposed approach leverages...",
    figure_type: str = "system-diagram",
    dpi: int = 300,
    width: int = 2048,
    height: int = 1536,
    extraction_date: str = "2025-07-16",
    content_hash: str | None = None,
    origin_type: str = "company-created",
    compliance_flag: str | None = None,
) -> ImageRegistryEntry:
    """Build an ImageRegistryEntry for test scenarios."""
    if content_hash is None:
        content_hash = hashlib.sha256(SYNTHETIC_PNG_BYTES).hexdigest()
    return ImageRegistryEntry(
        id=image_id,
        source_proposal=source_proposal,
        agency=agency,
        outcome=outcome,
        page_number=page_number,
        caption=caption,
        surrounding_text=surrounding_text,
        figure_type=figure_type,
        file_path=f".sbir/corpus/images/{image_id}.png",
        content_hash=content_hash,
        resolution_width=width,
        resolution_height=height,
        dpi=dpi,
        quality_level="high" if dpi >= 300 else ("medium" if dpi >= 150 else "low"),
        size_bytes=len(SYNTHETIC_PNG_BYTES),
        extraction_date=extraction_date,
        origin_type=origin_type,
        compliance_flag=compliance_flag,
    )


@pytest.fixture()
def af243_system_diagram() -> ImageRegistryEntry:
    """AF243-001 system architecture diagram -- high quality, USAF, WIN."""
    return make_registry_entry()


@pytest.fixture()
def af243_trl_roadmap() -> ImageRegistryEntry:
    """AF243-001 TRL roadmap -- high quality, USAF, WIN."""
    return make_registry_entry(
        image_id="af243-001-p12-img01",
        page_number=12,
        caption="Figure 7: Technology Readiness Level Maturation Plan",
        figure_type="trl-roadmap",
        content_hash=hashlib.sha256(b"trl-roadmap-bytes").hexdigest(),
    )


@pytest.fixture()
def darpa_system_diagram() -> ImageRegistryEntry:
    """DARPA-HR-22 system diagram -- high quality, DARPA, WIN."""
    return make_registry_entry(
        image_id="darpa-hr22-p05-img01",
        source_proposal="DARPA-HR-22",
        agency="DARPA",
        page_number=5,
        caption="Figure 2: Advanced RF System Architecture",
        content_hash=hashlib.sha256(b"darpa-system-bytes").hexdigest(),
    )


@pytest.fixture()
def stale_image() -> ImageRegistryEntry:
    """Image from a 26-month-old proposal -- freshness WARNING/STALE."""
    return make_registry_entry(
        image_id="old-proposal-p03-img01",
        source_proposal="OLD-PROP-2024",
        extraction_date="2024-01-16",
        caption="Figure 1: Legacy System Overview",
        figure_type="system-diagram",
        content_hash=hashlib.sha256(b"stale-image-bytes").hexdigest(),
    )


@pytest.fixture()
def low_res_image() -> ImageRegistryEntry:
    """Low-resolution image -- 72 DPI, quality FAIL."""
    return make_registry_entry(
        image_id="lowres-p01-img01",
        dpi=72,
        width=640,
        height=480,
        caption="Figure 1: Thumbnail Sketch",
        figure_type="concept-illustration",
        content_hash=hashlib.sha256(b"lowres-bytes").hexdigest(),
    )


@pytest.fixture()
def flagged_image() -> ImageRegistryEntry:
    """Image flagged for compliance review."""
    return make_registry_entry(
        image_id="darpa-hr22-p05-img02",
        source_proposal="DARPA-HR-22",
        agency="DARPA",
        caption="Figure 5: Test Range Layout",
        figure_type="concept-illustration",
        compliance_flag="possible government-furnished",
        origin_type="unknown",
        content_hash=hashlib.sha256(b"flagged-bytes").hexdigest(),
    )


@pytest.fixture()
def org_chart_image() -> ImageRegistryEntry:
    """Generic org chart -- no proposal-specific terms in caption."""
    return make_registry_entry(
        image_id="af243-001-p15-img01",
        page_number=15,
        caption="Figure 4: Organization Chart",
        figure_type="org-chart",
        content_hash=hashlib.sha256(b"org-chart-bytes").hexdigest(),
    )


# ---------------------------------------------------------------------------
# Proposal Context Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def current_proposal_context() -> dict[str, Any]:
    """Current proposal context for agency/topic matching."""
    return {
        "agency": "USAF",
        "topic_id": "AF245-007",
        "title": "Next-Gen Directed Energy for Maritime Defense",
    }
