"""Outline domain models -- value objects for proposal outline structure.

Pure domain objects with no infrastructure imports.
OutlineSection captures a single section with compliance mapping and page budget.
ProposalOutline aggregates sections with page budget validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OutlineSection:
    """A single outline section with compliance mapping and page budget.

    Frozen value object -- immutable after creation.
    """

    section_id: str
    title: str
    compliance_item_ids: list[str]
    page_budget: float
    figure_placeholders: list[str]
    thesis_statement: str


@dataclass
class ProposalOutline:
    """Collection of outline sections with page budget validation."""

    sections: list[OutlineSection] = field(default_factory=list)

    @property
    def total_page_budget(self) -> float:
        """Sum of all section page budgets."""
        return sum(s.page_budget for s in self.sections)

    def validates_page_budget(self, limit: float) -> bool:
        """True when total page budget does not exceed the given limit."""
        return self.total_page_budget <= limit
