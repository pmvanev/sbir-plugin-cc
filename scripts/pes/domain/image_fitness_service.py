"""Image fitness assessment service -- quality, freshness, agency match, and compliance.

Application service (driving port) for evaluating image reuse fitness.
Delegates to ImageRegistryPort for entry lookup and compliance flag updates.
Assessment logic is pure computation -- no infrastructure dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class FitnessAssessment:
    """Result of a fitness assessment on a single image."""

    quality_status: str  # PASS, WARN, FAIL
    quality_detail: str  # e.g. "300 DPI"
    freshness_status: str  # OK, WARNING, STALE
    freshness_detail: str  # e.g. "8 months"
    agency_match: str  # YES, NO


@dataclass(frozen=True)
class CaptionAnalysisResult:
    """Result of caption analysis for proposal-specific terms."""

    flagged_terms: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ImageFitnessService:
    """Driving port: assesses image fitness for reuse in new proposals.

    Constructor-injected collaborators:
    - registry: provides get_by_id and update_flag (duck-typed driven port)
    """

    def __init__(self, registry: object) -> None:
        self._registry = registry

    def assess(
        self,
        image_id: str,
        current_agency: str = "",
        reference_date: datetime | None = None,
    ) -> FitnessAssessment:
        """Assess fitness of an image for reuse.

        Looks up the image in the registry, evaluates quality (DPI),
        freshness (extraction age), and agency match.
        """
        entry = self._registry.get_by_id(image_id)  # type: ignore[union-attr]
        if entry is None:
            raise ValueError(f"Image not found: {image_id}")

        ref = reference_date or datetime.now()

        quality_status = self._assess_quality(entry.dpi)
        quality_detail = f"{entry.dpi} DPI"

        freshness_status, months = self._assess_freshness(
            entry.extraction_date, ref
        )
        freshness_detail = f"{months} months"

        agency = getattr(entry, "agency", "")
        agency_match = "YES" if agency and agency == current_agency else "NO"

        return FitnessAssessment(
            quality_status=quality_status,
            quality_detail=quality_detail,
            freshness_status=freshness_status,
            freshness_detail=freshness_detail,
            agency_match=agency_match,
        )

    @staticmethod
    def analyze_caption(
        caption: str,
        known_terms: list[str],
    ) -> CaptionAnalysisResult:
        """Analyze caption for proposal-specific terms.

        Pure function -- no side effects, no infrastructure dependencies.
        Returns flagged terms and warnings for terms found in the caption.
        """
        flagged: list[str] = []
        warnings: list[str] = []
        for term in known_terms:
            if term in caption:
                flagged.append(term)
                warnings.append(f"Proposal-specific term: {term}")
        return CaptionAnalysisResult(flagged_terms=flagged, warnings=warnings)

    def flag_image(self, image_id: str, reason: str) -> bool:
        """Flag an image with a compliance concern reason.

        Returns True if the image was found and flagged, False otherwise.
        """
        return self._registry.update_flag(image_id, reason)  # type: ignore[union-attr]

    def unflag_image(self, image_id: str) -> bool:
        """Clear compliance flag from an image.

        Returns True if the image was found and unflagged, False otherwise.
        """
        return self._registry.update_flag(image_id, None)  # type: ignore[union-attr]

    @staticmethod
    def _assess_quality(dpi: int) -> str:
        """Classify image quality from DPI value."""
        if dpi >= 300:
            return "PASS"
        if dpi >= 150:
            return "WARN"
        return "FAIL"

    @staticmethod
    def _assess_freshness(
        extraction_date: str, reference: datetime
    ) -> tuple[str, int]:
        """Classify freshness from extraction date.

        Returns (status, months_elapsed).
        """
        if not extraction_date:
            return "OK", 0
        try:
            extracted = datetime.strptime(extraction_date, "%Y-%m-%d")
        except ValueError:
            return "OK", 0

        delta = reference - extracted
        months = int(delta.days / 30)

        if months <= 12:
            return "OK", months
        if months <= 24:
            return "WARNING", months
        return "STALE", months
