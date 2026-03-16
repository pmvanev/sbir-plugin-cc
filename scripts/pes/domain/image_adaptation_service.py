"""Image adaptation service -- caption adaptation and reuse selection.

Application service (driving port) for adapting corpus images for reuse.
Handles caption adaptation, file copy tracking, figure inventory entry,
attribution, and compliance blocking.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AdaptationResult:
    """Result of adapting a corpus image for reuse."""

    original_caption: str
    adapted_caption: str
    figure_number: int
    section_id: str
    file_copied: bool
    manual_review_items: list[str] = field(default_factory=list)
    figure_inventory_entry: dict = field(default_factory=dict)
    attribution: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SelectionError:
    """Error when image cannot be selected for reuse."""

    message: str
    blocked: bool = True
    suggestion: str = ""


# Figure types that may contain embedded text needing manual review
_DIAGRAM_TYPES_WITH_EMBEDDED_TEXT = frozenset({"system-diagram", "process-flow"})


class ImageAdaptationService:
    """Driving port: adapts corpus images for reuse in new proposals.

    Constructor-injected collaborators:
    - registry: provides get_by_id (duck-typed driven port)
    """

    def __init__(self, registry: object) -> None:
        self._registry = registry

    def select_for_reuse(
        self,
        image_id: str,
        figure_number: int,
        section_id: str = "",
        proposal_specific_terms: list[str] | None = None,
    ) -> AdaptationResult | SelectionError:
        """Select an image for reuse, adapting its caption.

        Returns AdaptationResult on success, SelectionError on failure.
        Blocks compliance-flagged images. Returns error for missing images.
        """
        entry = self._registry.get_by_id(image_id)  # type: ignore[union-attr]
        if entry is None:
            return SelectionError(
                message="Image not found in catalog",
                blocked=True,
            )

        compliance_flag = getattr(entry, "compliance_flag", None)
        if compliance_flag is not None:
            return SelectionError(
                message="Image is flagged for compliance review",
                blocked=True,
                suggestion="Clear the flag after verification before reuse",
            )

        terms = proposal_specific_terms or []
        original_caption = entry.caption
        adapted_caption = self._adapt_caption(original_caption, figure_number, terms)

        warnings: list[str] = []
        for term in terms:
            if term in original_caption:
                warnings.append(f"Removed proposal-specific term: {term}")

        return AdaptationResult(
            original_caption=original_caption,
            adapted_caption=adapted_caption,
            figure_number=figure_number,
            section_id=section_id,
            file_copied=True,
            figure_inventory_entry={
                "figure_number": figure_number,
                "generation_method": "corpus-reuse",
                "status": "pending-manual-review",
            },
            attribution={
                "source_proposal": entry.source_proposal,
                "original_figure": original_caption,
            },
            warnings=warnings,
        )

    def generate_review_items(
        self,
        image_id: str,
        figure_type: str = "",
    ) -> list[str]:
        """Generate manual review items for an image.

        Returns list of items human should check, particularly for
        diagrams that may contain embedded proposal-specific text.
        """
        items: list[str] = []
        if figure_type in _DIAGRAM_TYPES_WITH_EMBEDDED_TEXT:
            items.append(
                "Check embedded component labels for proposal-specific names"
            )
            items.append(
                "Verify system name labels match current proposal"
            )
        return items

    @staticmethod
    def _adapt_caption(
        caption: str,
        figure_number: int,
        terms: list[str],
    ) -> str:
        """Adapt caption by removing terms and updating figure number."""
        adapted = caption
        for term in terms:
            # Remove term followed by a space (e.g., "CDES " -> "")
            adapted = adapted.replace(term + " ", "")
        # Update figure number
        adapted = re.sub(r"Figure \d+:", f"Figure {figure_number}:", adapted)
        return adapted
