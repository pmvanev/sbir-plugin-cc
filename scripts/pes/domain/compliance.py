"""Compliance matrix domain model -- requirements extracted from solicitation text."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RequirementType(Enum):
    """Category of extracted requirement."""

    SHALL = "shall"
    FORMAT = "format"
    IMPLICIT = "implicit"
    MANUAL = "manual"


class CoverageStatus(Enum):
    """Coverage tracking for a compliance item."""

    NOT_STARTED = "not_started"
    PARTIAL = "partial"
    COVERED = "covered"
    WAIVED = "waived"


@dataclass
class ComplianceItem:
    """A single requirement extracted from solicitation text."""

    item_id: int
    text: str
    requirement_type: RequirementType
    proposal_section: str | None = None
    ambiguity: str | None = None
    status: CoverageStatus = CoverageStatus.NOT_STARTED


@dataclass
class ComplianceMatrix:
    """Collection of compliance items with generation metadata."""

    items: list[ComplianceItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def item_count(self) -> int:
        return len(self.items)

    def coverage_summary(self) -> str:
        """Return coverage breakdown string."""
        covered = sum(1 for i in self.items if i.status == CoverageStatus.COVERED)
        partial = sum(1 for i in self.items if i.status == CoverageStatus.PARTIAL)
        not_started = sum(
            1 for i in self.items if i.status == CoverageStatus.NOT_STARTED
        )
        total = self.item_count
        return f"{covered}/{total} covered | {partial} partial | {not_started} not started"
