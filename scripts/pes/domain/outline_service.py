"""Outline service -- driving port for proposal outline generation.

Orchestrates: proposal outline generation from discrimination table and compliance
matrix context. Validates preconditions (approved discrimination table required),
delegates to OutlineGenerator driven port, and detects unmapped compliance items.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from pes.domain.outline import ProposalOutline


class OutlineGenerator(Protocol):
    """Driven port: generates proposal outline from discrimination and compliance context."""

    def generate(
        self,
        discrimination_table: dict[str, Any],
        compliance_matrix: dict[str, Any],
        *,
        page_limit: float,
    ) -> ProposalOutline: ...


class DiscriminationApprovalRequiredError(Exception):
    """Raised when outline generation is attempted without an approved discrimination table."""


@dataclass
class OutlineResult:
    """Result of outline generation including the outline and any unmapped items."""

    outline: ProposalOutline
    unmapped_item_ids: list[str]


class OutlineService:
    """Driving port: generates proposal outline and detects compliance gaps.

    Delegates to OutlineGenerator driven port for actual outline production.
    Validates preconditions (discrimination table must be approved) and
    identifies any compliance items not mapped to outline sections.
    """

    def __init__(self, outline_generator: OutlineGenerator) -> None:
        self._generator = outline_generator

    def generate_outline(
        self,
        discrimination_table: dict[str, Any] | None,
        compliance_matrix: dict[str, Any],
        page_limit: float,
    ) -> OutlineResult:
        """Generate proposal outline from discrimination table and compliance matrix.

        Raises DiscriminationApprovalRequiredError if discrimination table is None
        or not approved (approved_at is None).
        Returns OutlineResult with outline and list of unmapped compliance item IDs.
        """
        if discrimination_table is None or discrimination_table.get("approved_at") is None:
            raise DiscriminationApprovalRequiredError(
                "Approved discrimination table required before outline generation. "
                "Complete and approve the discrimination table first."
            )

        outline = self._generator.generate(
            discrimination_table,
            compliance_matrix,
            page_limit=page_limit,
        )

        # Detect unmapped compliance items
        all_item_ids = {
            item["id"] for item in compliance_matrix.get("items", [])
        }
        mapped_ids: set[str] = set()
        for section in outline.sections:
            mapped_ids.update(section.compliance_item_ids)

        unmapped = sorted(all_item_ids - mapped_ids)

        return OutlineResult(outline=outline, unmapped_item_ids=unmapped)
