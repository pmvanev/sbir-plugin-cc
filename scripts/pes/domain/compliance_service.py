"""Compliance service -- driving port for compliance matrix generation.

Orchestrates: requirement extraction, section mapping, ambiguity flagging,
low-count warnings, and manual additions.
"""

from __future__ import annotations

import re

from pes.domain.compliance import (
    ComplianceItem,
    ComplianceMatrix,
    RequirementType,
)
from pes.ports.compliance_port import ComplianceExtractor

LOW_EXTRACTION_THRESHOLD = 5


class ComplianceMatrixNotFoundError(Exception):
    """Raised when attempting to modify a matrix that does not exist."""


class ComplianceService:
    """Driving port: generates and manages compliance matrix."""

    def __init__(self, extractor: ComplianceExtractor) -> None:
        self._extractor = extractor

    def generate_matrix(self, solicitation_text: str) -> ComplianceMatrix:
        """Extract requirements and build compliance matrix.

        Returns ComplianceMatrix with items mapped to sections,
        ambiguities flagged, and low-count warnings.
        """
        items = self._extractor.extract(solicitation_text)
        warnings: list[str] = []

        if len(items) < LOW_EXTRACTION_THRESHOLD:
            warnings.append(
                f"Low extraction count ({len(items)} items found). "
                "Review solicitation manually for implicit requirements."
            )

        return ComplianceMatrix(items=items, warnings=warnings)

    def add_item(
        self, matrix: ComplianceMatrix, text: str
    ) -> ComplianceMatrix:
        """Manually add a compliance item to an existing matrix.

        Raises ComplianceMatrixNotFoundError if matrix is None.
        """
        if matrix is None:
            raise ComplianceMatrixNotFoundError("No compliance matrix found")

        next_id = max((i.item_id for i in matrix.items), default=0) + 1
        section = self._infer_section(text)

        new_item = ComplianceItem(
            item_id=next_id,
            text=text,
            requirement_type=RequirementType.MANUAL,
            proposal_section=section,
        )

        updated_items = [*matrix.items, new_item]
        return ComplianceMatrix(items=updated_items, warnings=list(matrix.warnings))

    def _infer_section(self, text: str) -> str | None:
        """Infer proposal section from requirement text."""
        match = re.search(r"[Ss]ection\s+(\d+)", text)
        if match:
            return f"Section {match.group(1)}"
        return None
