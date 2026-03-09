"""Outline service -- driving port for proposal outline generation and checkpoint.

Orchestrates: proposal outline generation from discrimination table and compliance
matrix context, and outline checkpoint lifecycle (approve/revise/skip).
Validates preconditions (approved discrimination table required),
delegates to OutlineGenerator driven port, and detects unmapped compliance items.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
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
        feedback: str | None = None,
    ) -> ProposalOutline: ...


class DiscriminationApprovalRequiredError(Exception):
    """Raised when outline generation is attempted without an approved discrimination table."""


class OutlineNotFoundError(Exception):
    """Raised when checkpoint action is attempted without a generated outline."""


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

    def approve_outline(
        self,
        outline: ProposalOutline | None,
    ) -> dict[str, object]:
        """Approve proposal outline, recording approval and unlocking Wave 4.

        Raises OutlineNotFoundError if outline is None.
        Returns state update dict with approval timestamp and wave unlock.
        """
        if outline is None:
            raise OutlineNotFoundError(
                "No proposal outline to approve. Generate an outline first."
            )

        return {
            "outline_status": "approved",
            "approved_at": datetime.now(tz=UTC).isoformat(),
            "wave_4_unlocked": True,
        }

    def revise_outline(
        self,
        outline: ProposalOutline | None,
        discrimination_table: dict[str, Any],
        compliance_matrix: dict[str, Any],
        page_limit: float,
        feedback: str,
    ) -> ProposalOutline:
        """Revise proposal outline incorporating user feedback.

        Raises OutlineNotFoundError if outline is None.
        Regenerates outline via OutlineGenerator with feedback context.
        """
        if outline is None:
            raise OutlineNotFoundError(
                "No proposal outline to revise. Generate an outline first."
            )

        return self._generator.generate(
            discrimination_table,
            compliance_matrix,
            page_limit=page_limit,
            feedback=feedback,
        )

    def skip_outline(self) -> dict[str, object]:
        """Skip outline, marking as deferred and unlocking Wave 4.

        Does not require existing outline. Returns state update dict.
        """
        return {
            "outline_status": "deferred",
            "wave_4_unlocked": True,
        }
