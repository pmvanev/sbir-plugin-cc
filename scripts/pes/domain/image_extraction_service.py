"""Image extraction service -- orchestrates extraction, classification, dedup, and registry.

Application service (driving port) for image extraction during corpus ingestion.
Delegates to ImageExtractorPort for document parsing and ImageRegistryPort for persistence.
Classification uses pure caption/context heuristics -- no ML, no external API.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from pes.domain.corpus_image import ImageEntry, QualityLevel
from pes.ports.image_extractor_port import ImageExtractorPort
from pes.ports.image_registry_port import ImageRegistryPort

# Figure type classification heuristics -- caption keyword mapping
_TYPE_INDICATORS: dict[str, list[str]] = {
    "system-diagram": ["system architecture", "block diagram", "system overview"],
    "trl-roadmap": ["trl", "technology readiness", "maturation"],
    "org-chart": ["organization", "team structure", "management"],
    "schedule": ["schedule", "timeline", "gantt", "milestone"],
    "concept-illustration": ["concept", "illustration", "deployment", "scenario"],
    "data-chart": ["chart", "graph", "performance data", "results"],
    "process-flow": ["process", "workflow", "flow", "sequence"],
}


@dataclass(frozen=True)
class ExtractionReport:
    """Result of extracting images from a single document."""

    total_extracted: int = 0
    new_count: int = 0
    skipped_duplicates: int = 0
    total_failed: int = 0
    counts_by_type: dict[str, int] = field(default_factory=dict)
    counts_by_quality: dict[str, int] = field(default_factory=dict)


class ImageExtractionService:
    """Driving port: extracts, classifies, deduplicates, and registers images.

    Constructor-injected collaborators:
    - extractor: ImageExtractorPort (driven) for document image extraction
    - registry: ImageRegistryPort (driven) for persistence and dedup
    """

    def __init__(
        self,
        extractor: ImageExtractorPort,
        registry: ImageRegistryPort,
    ) -> None:
        self._extractor = extractor
        self._registry = registry

    @staticmethod
    def classify_figure_type(caption: str, surrounding_text: str) -> str:
        """Classify figure type from caption and surrounding text heuristics.

        Pure function -- no side effects, no infrastructure dependencies.
        Returns one of the defined figure types or 'unclassified'.
        """
        search_text = caption.lower()
        for fig_type, indicators in _TYPE_INDICATORS.items():
            if any(ind in search_text for ind in indicators):
                return fig_type

        # Fall back to surrounding text if caption yields no match
        context_text = surrounding_text.lower()
        for fig_type, indicators in _TYPE_INDICATORS.items():
            if any(ind in context_text for ind in indicators):
                return fig_type

        return "unclassified"

    def extract_from_document(
        self,
        file_path: Path,
        source_proposal: str,
    ) -> ExtractionReport:
        """Extract images from a document, classify, dedup, and register.

        Returns an ExtractionReport with counts by type and quality.
        """
        result = self._extractor.extract(file_path)

        counts_by_type: dict[str, int] = {}
        counts_by_quality: dict[str, int] = {}
        new_count = 0
        skipped_duplicates = 0

        for img in result.images:
            figure_type = self.classify_figure_type(
                img.caption, img.surrounding_text
            )
            quality = QualityLevel.from_dpi(img.dpi)
            content_hash = hashlib.sha256(img.image_bytes).hexdigest()

            entry = ImageEntry(
                id=f"{source_proposal.lower()}-p{img.page_number:02d}-img{img.position_index:02d}",
                source_proposal=source_proposal,
                page_number=img.page_number,
                caption=img.caption,
                figure_type=figure_type,
                dpi=img.dpi,
                content_hash=content_hash,
                quality_level=quality,
            )

            if self._registry.add(entry):
                new_count += 1
            else:
                skipped_duplicates += 1

            # Accumulate type counts
            counts_by_type[figure_type] = counts_by_type.get(figure_type, 0) + 1

            # Accumulate quality counts
            quality_key = quality.value
            counts_by_quality[quality_key] = (
                counts_by_quality.get(quality_key, 0) + 1
            )

        return ExtractionReport(
            total_extracted=len(result.images),
            new_count=new_count,
            skipped_duplicates=skipped_duplicates,
            total_failed=len(result.failures),
            counts_by_type=counts_by_type,
            counts_by_quality=counts_by_quality,
        )
