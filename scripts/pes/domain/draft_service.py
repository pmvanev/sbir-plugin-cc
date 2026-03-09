"""Draft service -- driving port for section-by-section drafting with compliance tracking.

Orchestrates: section drafting from approved outline, compliance coverage
checking per section, and page budget monitoring.
Validates preconditions (approved outline required),
delegates to SectionDrafter driven port, and detects unaddressed compliance items.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from pes.domain.draft import SectionDraft
from pes.domain.outline import OutlineSection, ProposalOutline

# Words per page constant for budget calculations
WORDS_PER_PAGE = 250


class SectionDrafter(Protocol):
    """Driven port: drafts a section from an outline section."""

    def draft(
        self,
        section: OutlineSection,
        *,
        iteration: int = 1,
    ) -> SectionDraft: ...


class ApprovedOutlineRequiredError(Exception):
    """Raised when drafting is attempted without an approved outline."""


class SectionNotInOutlineError(Exception):
    """Raised when drafting a section that does not exist in the outline."""


@dataclass
class DraftResult:
    """Result of section drafting with compliance and budget tracking."""

    draft: SectionDraft
    word_count: int
    page_budget: float
    pages_used: float
    budget_warning: str | None
    unaddressed_item_ids: list[str]


class DraftService:
    """Driving port: drafts proposal sections with compliance tracking.

    Delegates to SectionDrafter driven port for actual content generation.
    Validates preconditions (outline must be approved) and tracks
    compliance coverage and page budget usage per section.
    """

    def __init__(self, section_drafter: SectionDrafter) -> None:
        self._drafter = section_drafter

    def draft_section(
        self,
        outline: ProposalOutline | None,
        section_id: str,
    ) -> DraftResult:
        """Draft a section from the approved outline.

        Raises ApprovedOutlineRequiredError if outline is None.
        Raises SectionNotInOutlineError if section_id not in outline.
        Returns DraftResult with draft, word count, budget info, and compliance gaps.
        """
        if outline is None:
            raise ApprovedOutlineRequiredError(
                "Approved outline required before drafting. "
                "Complete Wave 3 outline approval first."
            )

        # Find the requested section
        section = self._find_section(outline, section_id)

        # Delegate to driven port
        draft = self._drafter.draft(section, iteration=1)

        # Calculate page budget usage
        word_count = draft.word_count
        pages_used = word_count / WORDS_PER_PAGE
        page_budget = section.page_budget

        # Generate budget warning if exceeding
        budget_warning = None
        if pages_used > page_budget:
            budget_warning = (
                f"Section '{section_id}' exceeds its page budget: "
                f"{pages_used:.1f} pages used vs {page_budget:.1f} budget. "
                f"Consider cutting content or reallocating pages from other sections."
            )

        # Detect unaddressed compliance items
        required_ids = set(section.compliance_item_ids)
        addressed_ids = set(draft.compliance_item_ids)
        unaddressed = sorted(required_ids - addressed_ids)

        return DraftResult(
            draft=draft,
            word_count=word_count,
            page_budget=page_budget,
            pages_used=pages_used,
            budget_warning=budget_warning,
            unaddressed_item_ids=unaddressed,
        )

    def _find_section(
        self, outline: ProposalOutline, section_id: str
    ) -> OutlineSection:
        """Find a section in the outline by ID, or raise with guidance."""
        for section in outline.sections:
            if section.section_id == section_id:
                return section

        available_ids = [s.section_id for s in outline.sections]
        raise SectionNotInOutlineError(
            f"Section '{section_id}' is not in the approved outline. "
            f"Available sections: {', '.join(available_ids)}. "
            f"Update the outline to include this section first."
        )
