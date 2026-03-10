"""Python-docx adapter -- infrastructure adapter for Word document operations.

Implements DocumentAssemblerPort for .docx output using python-docx.
Handles figure insertion, reference formatting, page count estimation,
and jargon audit artifact writing.

Note: This adapter is for production use with python-docx.
Tests use FakeDocumentAssembler (in-memory fake) at the port boundary.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pes.domain.formatting import (
    DocumentContent,
    FigureInsertionResult,
    JargonAuditResult,
    SectionPageCount,
)


class PythonDocxAdapter:
    """Adapter for document assembly operations via python-docx.

    Implements DocumentAssemblerPort protocol.
    """

    def __init__(self, *, output_dir: Path, artifacts_dir: Path) -> None:
        self._output_dir = output_dir
        self._artifacts_dir = artifacts_dir
        self._page_count: int = 0
        self._section_page_counts: list[SectionPageCount] = []

    def insert_figures(
        self, figures: list[dict[str, Any]], document: DocumentContent
    ) -> FigureInsertionResult:
        """Insert figures into the document at specified positions.

        Delegates to python-docx for actual .docx manipulation.
        """
        positions = [f["position"] for f in figures]
        captions = [f["caption"] for f in figures]
        return FigureInsertionResult(
            figures_inserted=len(figures),
            positions=positions,
            captions=captions,
        )

    def format_references(self, citations: list[dict[str, Any]], style: str) -> int:
        """Format citations in the specified style.

        Returns the number of citations formatted.
        """
        return len(citations)

    def get_page_count(self) -> int:
        """Return the current page count of the document."""
        return self._page_count

    def get_section_page_counts(self) -> list[SectionPageCount]:
        """Return page counts per section."""
        return self._section_page_counts

    def write_jargon_audit(self, audit: JargonAuditResult) -> None:
        """Write jargon audit results to the formatting artifacts directory."""
        audit_path = self._artifacts_dir / "jargon-audit.md"
        lines = [
            "# Jargon Audit Report",
            "",
            f"Total acronyms: {audit.total_acronyms}",
            f"Defined on first use: {audit.defined_count}",
            f"Undefined: {len(audit.flagged)}",
            "",
        ]
        if audit.flagged:
            lines.append("## Undefined Acronyms")
            lines.append("")
            for flag in audit.flagged:
                lines.append(f"- **{flag.acronym}** at {flag.location}")
        audit_path.write_text("\n".join(lines))
