"""Formatting domain model -- format templates and document formatting value objects."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FormatTemplate:
    """Format template specifying document formatting rules for a solicitation."""

    agency: str
    solicitation_type: str
    font_family: str
    font_size_pt: int
    margin_top_inches: float
    margin_bottom_inches: float
    margin_left_inches: float
    margin_right_inches: float
    header: str
    footer: str
    page_limit: int
    line_spacing: float


@dataclass
class FormatTemplateResult:
    """Outcome of loading a format template."""

    template: FormatTemplate | None = None
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.template is not None and self.error is None


@dataclass(frozen=True)
class DocumentContent:
    """Input document content for formatting operations."""

    sections: list[str]
    text: str


@dataclass(frozen=True)
class FigureInsertionResult:
    """Result of inserting figures into a document."""

    figures_inserted: int
    positions: list[str]
    captions: list[str]


@dataclass(frozen=True)
class AcronymFlag:
    """A single undefined acronym flagged by the jargon audit."""

    acronym: str
    location: str


@dataclass
class JargonAuditResult:
    """Result of running a jargon audit on a document."""

    flagged: list[AcronymFlag] = field(default_factory=list)
    total_acronyms: int = 0
    defined_count: int = 0


@dataclass(frozen=True)
class SectionPageCount:
    """Page count for a single section of the document."""

    section_id: str
    title: str
    page_count: int


@dataclass
class PageCountReport:
    """Report of document page count vs solicitation limit."""

    current_pages: int
    page_limit: int
    within_limit: bool
    summary: str
    largest_sections: list[SectionPageCount] = field(default_factory=list)
    trimming_suggestions: list[str] = field(default_factory=list)
