"""Formatting service -- driving port for document formatting operations.

Orchestrates: format template loading, figure insertion, reference formatting,
jargon audit, and page count reporting.
Delegates to FormatTemplateLoader and DocumentAssembler driven ports.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from pes.domain.formatting import (
    AcronymFlag,
    DocumentContent,
    FigureInsertionResult,
    FormatTemplateResult,
    JargonAuditResult,
    PageCountReport,
    SectionPageCount,
)
from pes.ports.format_template_port import FormatTemplateLoader

if TYPE_CHECKING:
    pass


class DocumentAssemblerPort(Protocol):
    """Protocol for document assembly operations -- driven port."""

    def insert_figures(
        self, figures: list[dict[str, Any]], document: DocumentContent
    ) -> FigureInsertionResult: ...

    def format_references(self, citations: list[dict[str, Any]], style: str) -> int: ...

    def get_page_count(self) -> int: ...

    def get_section_page_counts(self) -> list[SectionPageCount]: ...

    def write_jargon_audit(self, audit: JargonAuditResult) -> None: ...


class FormattingService:
    """Driving port: loads format templates, inserts figures, audits jargon, reports pages.

    Delegates to FormatTemplateLoader and DocumentAssemblerPort driven ports.
    """

    def __init__(
        self,
        format_template_loader: FormatTemplateLoader,
        document_assembler: DocumentAssemblerPort | None = None,
    ) -> None:
        self._loader = format_template_loader
        self._assembler = document_assembler

    def load_format_template(
        self, *, agency: str, solicitation_type: str
    ) -> FormatTemplateResult:
        """Load format template for the given agency and solicitation type.

        Returns FormatTemplateResult with template or error details.
        """
        template = self._loader.load_template(
            agency=agency, solicitation_type=solicitation_type
        )

        if template is None:
            return FormatTemplateResult(
                error=f"No format template found for agency '{agency}' "
                f"with solicitation type '{solicitation_type}'"
            )

        return FormatTemplateResult(template=template)

    def insert_figures(
        self,
        *,
        figures: list[dict[str, Any]],
        document: DocumentContent,
    ) -> FigureInsertionResult:
        """Insert figures at their correct positions with captions.

        Delegates to DocumentAssemblerPort for actual document manipulation.
        """
        if self._assembler is None:
            msg = "DocumentAssembler required for figure insertion"
            raise RuntimeError(msg)
        return self._assembler.insert_figures(figures, document)

    def format_references(
        self, *, citations: list[dict[str, Any]], style: str
    ) -> int:
        """Format citations in a consistent style.

        Returns the number of citations formatted.
        """
        if self._assembler is None:
            msg = "DocumentAssembler required for reference formatting"
            raise RuntimeError(msg)
        return self._assembler.format_references(citations, style)

    def run_jargon_audit(
        self,
        *,
        acronyms: dict[str, str],
        defined_acronyms: set[str],
    ) -> JargonAuditResult:
        """Run jargon audit to flag undefined acronyms with locations.

        Returns JargonAuditResult with flagged acronyms.
        Writes audit to formatting artifacts via assembler.
        """
        flagged = [
            AcronymFlag(acronym=acr, location=loc)
            for acr, loc in sorted(acronyms.items())
            if acr not in defined_acronyms
        ]
        result = JargonAuditResult(
            flagged=flagged,
            total_acronyms=len(acronyms),
            defined_count=len(defined_acronyms),
        )
        if self._assembler is not None:
            self._assembler.write_jargon_audit(result)
        return result

    def report_page_count(self, *, page_limit: int) -> PageCountReport:
        """Report page count vs solicitation limit.

        When within limit: shows margin info.
        When over limit: shows largest sections and trimming suggestions.
        """
        if self._assembler is None:
            msg = "DocumentAssembler required for page count reporting"
            raise RuntimeError(msg)

        current_pages = self._assembler.get_page_count()
        within_limit = current_pages <= page_limit

        if within_limit:
            margin = page_limit - current_pages
            margin_text = f"{margin} page margin" if margin == 1 else f"{margin} pages margin"
            summary = f"{current_pages}/{page_limit} -- within limit ({margin_text})"
            return PageCountReport(
                current_pages=current_pages,
                page_limit=page_limit,
                within_limit=True,
                summary=summary,
            )

        # Over limit
        over_by = current_pages - page_limit
        summary = f"{current_pages}/{page_limit} -- OVER LIMIT by {over_by} pages"

        section_counts = self._assembler.get_section_page_counts()
        sorted_sections = sorted(section_counts, key=lambda s: s.page_count, reverse=True)
        largest_3 = sorted_sections[:3]

        trimming_suggestions = self._generate_trimming_suggestions(largest_3, over_by)

        return PageCountReport(
            current_pages=current_pages,
            page_limit=page_limit,
            within_limit=False,
            summary=summary,
            largest_sections=largest_3,
            trimming_suggestions=trimming_suggestions,
        )

    @staticmethod
    def _generate_trimming_suggestions(
        largest_sections: list[SectionPageCount], over_by: int
    ) -> list[str]:
        """Generate trimming suggestions based on largest sections and overage."""
        suggestions = []
        if largest_sections:
            top = largest_sections[0]
            suggestions.append(
                f"Consider condensing '{top.title}' ({top.page_count} pages) "
                f"-- largest section"
            )
        suggestions.append(
            f"Reduce content by {over_by} pages to meet the solicitation limit"
        )
        suggestions.append(
            "Review figures and tables for opportunities to consolidate or resize"
        )
        return suggestions
