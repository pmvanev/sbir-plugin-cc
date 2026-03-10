"""Unit tests for formatting through FormattingService driving port.

Test Budget: 7 behaviors x 2 = 14 unit tests max.
Current count: 12 tests (within budget).

Tests verify through driving port (FormattingService):
1. Loads format template with all required fields by agency + solicitation type
2. Returns None when template not found for unknown agency/type
3. Multiple agencies loadable without code changes (extensibility)
4. Insert figures at correct positions with captions and format references
5. Jargon audit flags undefined acronyms with locations, writes audit artifact
6. Page count within limit reports margin info
7. Page count over limit reports largest sections and trimming guidance
"""

from __future__ import annotations

import pytest

from pes.domain.formatting import (
    AcronymFlag,
    DocumentContent,
    FigureInsertionResult,
    FormatTemplate,
    JargonAuditResult,
    SectionPageCount,
)
from pes.domain.formatting_service import FormattingService
from pes.ports.format_template_port import FormatTemplateLoader

# --- In-memory fake for FormatTemplateLoader driven port ---


class InMemoryFormatTemplateLoader(FormatTemplateLoader):
    """Fake driven port for testing -- loads templates from in-memory dict."""

    def __init__(self, templates: dict[tuple[str, str], FormatTemplate]) -> None:
        self._templates = templates

    def load_template(
        self, *, agency: str, solicitation_type: str
    ) -> FormatTemplate | None:
        return self._templates.get((agency, solicitation_type))


# --- Fixtures ---


DOD_TEMPLATE = FormatTemplate(
    agency="dod",
    solicitation_type="phase-i",
    font_family="Times New Roman",
    font_size_pt=12,
    margin_top_inches=1.0,
    margin_bottom_inches=1.0,
    margin_left_inches=1.0,
    margin_right_inches=1.0,
    header="SBIR Phase I Proposal",
    footer="Page {page_number}",
    page_limit=20,
    line_spacing=1.0,
)

NASA_TEMPLATE = FormatTemplate(
    agency="nasa",
    solicitation_type="phase-i",
    font_family="Times New Roman",
    font_size_pt=12,
    margin_top_inches=1.0,
    margin_bottom_inches=1.0,
    margin_left_inches=1.0,
    margin_right_inches=1.0,
    header="NASA SBIR Phase I",
    footer="Page {page_number}",
    page_limit=25,
    line_spacing=1.5,
)


@pytest.fixture()
def formatting_service():
    loader = InMemoryFormatTemplateLoader({
        ("dod", "phase-i"): DOD_TEMPLATE,
        ("nasa", "phase-i"): NASA_TEMPLATE,
    })
    return FormattingService(format_template_loader=loader)


# ---------------------------------------------------------------------------
# Behavior 1: Loads format template with all required fields
# ---------------------------------------------------------------------------


class TestLoadFormatTemplate:
    def test_loads_template_with_all_formatting_fields(self, formatting_service):
        result = formatting_service.load_format_template(
            agency="dod", solicitation_type="phase-i"
        )

        assert result.success
        template = result.template
        assert template.font_family == "Times New Roman"
        assert template.font_size_pt == 12
        assert template.margin_top_inches == 1.0
        assert template.margin_bottom_inches == 1.0
        assert template.margin_left_inches == 1.0
        assert template.margin_right_inches == 1.0
        assert template.header == "SBIR Phase I Proposal"
        assert template.footer == "Page {page_number}"
        assert template.page_limit == 20
        assert template.line_spacing == 1.0

    @pytest.mark.parametrize(
        "agency,solicitation_type,expected_header,expected_page_limit",
        [
            ("dod", "phase-i", "SBIR Phase I Proposal", 20),
            ("nasa", "phase-i", "NASA SBIR Phase I", 25),
        ],
    )
    def test_loads_template_by_agency_and_solicitation_type(
        self,
        formatting_service,
        agency,
        solicitation_type,
        expected_header,
        expected_page_limit,
    ):
        result = formatting_service.load_format_template(
            agency=agency, solicitation_type=solicitation_type
        )

        assert result.success
        assert result.template.header == expected_header
        assert result.template.page_limit == expected_page_limit


# ---------------------------------------------------------------------------
# Behavior 2: Template not found returns error result
# ---------------------------------------------------------------------------


class TestTemplateNotFound:
    def test_returns_error_for_unknown_agency(self, formatting_service):
        result = formatting_service.load_format_template(
            agency="unknown", solicitation_type="phase-i"
        )

        assert not result.success
        assert result.template is None
        assert result.error is not None
        assert "unknown" in result.error.lower()


# ---------------------------------------------------------------------------
# Behavior 3: Templates extensible without code changes
# ---------------------------------------------------------------------------


class TestTemplateExtensibility:
    def test_new_agency_works_by_adding_to_loader(self):
        """New agency template works by adding data, no code changes needed."""
        custom_template = FormatTemplate(
            agency="doe",
            solicitation_type="phase-i",
            font_family="Arial",
            font_size_pt=11,
            margin_top_inches=1.0,
            margin_bottom_inches=1.0,
            margin_left_inches=1.0,
            margin_right_inches=1.0,
            header="DOE SBIR Phase I",
            footer="Page {page_number} of {total_pages}",
            page_limit=15,
            line_spacing=1.15,
        )
        loader = InMemoryFormatTemplateLoader({
            ("doe", "phase-i"): custom_template,
        })
        service = FormattingService(format_template_loader=loader)

        result = service.load_format_template(
            agency="doe", solicitation_type="phase-i"
        )

        assert result.success
        assert result.template.agency == "doe"
        assert result.template.font_family == "Arial"


# ---------------------------------------------------------------------------
# Fake driven port for document assembly (figures, references, page count)
# ---------------------------------------------------------------------------


class FakeDocumentAssembler:
    """Fake driven port: in-memory document assembly for testing."""

    def __init__(
        self,
        *,
        page_count: int = 10,
        section_page_counts: list[SectionPageCount] | None = None,
    ) -> None:
        self._page_count = page_count
        self._section_page_counts = section_page_counts or []
        self.inserted_figures: list[dict] = []
        self.formatted_references: list[dict] = []
        self.written_audit: JargonAuditResult | None = None

    def insert_figures(
        self, figures: list[dict], document: DocumentContent
    ) -> FigureInsertionResult:
        self.inserted_figures = figures
        return FigureInsertionResult(
            figures_inserted=len(figures),
            positions=[f["position"] for f in figures],
            captions=[f["caption"] for f in figures],
        )

    def format_references(
        self, citations: list[dict], style: str
    ) -> int:
        self.formatted_references = citations
        return len(citations)

    def get_page_count(self) -> int:
        return self._page_count

    def get_section_page_counts(self) -> list[SectionPageCount]:
        return self._section_page_counts

    def write_jargon_audit(self, audit: JargonAuditResult) -> None:
        self.written_audit = audit


# ---------------------------------------------------------------------------
# Fixtures for step 03-02 tests
# ---------------------------------------------------------------------------


def _make_formatting_service(
    *,
    page_count: int = 10,
    section_page_counts: list[SectionPageCount] | None = None,
) -> tuple[FormattingService, FakeDocumentAssembler]:
    loader = InMemoryFormatTemplateLoader({
        ("dod", "phase-i"): DOD_TEMPLATE,
    })
    assembler = FakeDocumentAssembler(
        page_count=page_count,
        section_page_counts=section_page_counts,
    )
    service = FormattingService(
        format_template_loader=loader,
        document_assembler=assembler,
    )
    return service, assembler


# ---------------------------------------------------------------------------
# Behavior 4: Insert figures at positions with captions, format references
# ---------------------------------------------------------------------------


class TestInsertFiguresAndFormatReferences:
    def test_inserts_figures_at_correct_positions_with_captions(self):
        service, _assembler = _make_formatting_service()
        figures = [
            {"figure_number": i, "position": f"section-3.{i}", "caption": f"Figure {i}"}
            for i in range(1, 6)
        ]
        document = DocumentContent(
            sections=["section-3.1", "section-3.2", "section-3.3", "section-3.4", "section-3.5"],
            text="proposal body text",
        )

        result = service.insert_figures(figures=figures, document=document)

        assert result.figures_inserted == 5
        assert len(result.positions) == 5
        assert len(result.captions) == 5
        assert result.captions[0] == "Figure 1"

    def test_formats_citations_in_consistent_style(self):
        service, assembler = _make_formatting_service()
        citations = [{"id": i, "text": f"Reference {i}"} for i in range(1, 24)]

        count = service.format_references(citations=citations, style="ieee")

        assert count == 23
        assert len(assembler.formatted_references) == 23


# ---------------------------------------------------------------------------
# Behavior 5: Jargon audit flags undefined acronyms with locations
# ---------------------------------------------------------------------------


class TestJargonAudit:
    def test_flags_undefined_acronyms_with_locations(self):
        service, _ = _make_formatting_service()
        # 15 acronyms total, 13 defined on first use, 2 not defined
        acronyms = {f"ACR{i}": f"section-{i}" for i in range(1, 16)}
        defined_acronyms = {f"ACR{i}" for i in range(1, 14)}  # 13 defined

        result = service.run_jargon_audit(
            acronyms=acronyms,
            defined_acronyms=defined_acronyms,
        )

        assert len(result.flagged) == 2
        assert all(isinstance(f, AcronymFlag) for f in result.flagged)
        assert {f.acronym for f in result.flagged} == {"ACR14", "ACR15"}
        # Each flag has a location
        assert all(f.location is not None for f in result.flagged)

    def test_writes_audit_to_formatting_artifacts(self):
        service, assembler = _make_formatting_service()
        acronyms = {"LIDAR": "section-2", "GPS": "section-3"}
        defined_acronyms = {"GPS"}

        service.run_jargon_audit(
            acronyms=acronyms,
            defined_acronyms=defined_acronyms,
        )

        assert assembler.written_audit is not None
        assert len(assembler.written_audit.flagged) == 1


# ---------------------------------------------------------------------------
# Behavior 6: Page count within solicitation limit
# ---------------------------------------------------------------------------


class TestPageCountWithinLimit:
    def test_reports_within_limit_with_margin(self):
        service, _ = _make_formatting_service(page_count=19)

        report = service.report_page_count(page_limit=20)

        assert report.current_pages == 19
        assert report.page_limit == 20
        assert report.within_limit is True
        assert "19/20" in report.summary
        assert "within limit" in report.summary.lower()
        assert "1 page margin" in report.summary.lower()


# ---------------------------------------------------------------------------
# Behavior 7: Page count over limit with guidance
# ---------------------------------------------------------------------------


class TestPageCountOverLimit:
    def test_reports_over_limit_message(self):
        section_counts = [
            SectionPageCount(section_id="3.1", title="Technical Approach", page_count=8),
            SectionPageCount(section_id="3.2", title="Key Personnel", page_count=6),
            SectionPageCount(section_id="3.3", title="Management Plan", page_count=5),
            SectionPageCount(section_id="3.4", title="Past Performance", page_count=3),
        ]
        service, _ = _make_formatting_service(
            page_count=22, section_page_counts=section_counts,
        )

        report = service.report_page_count(page_limit=20)

        assert report.current_pages == 22
        assert report.within_limit is False
        assert "22/20" in report.summary
        assert "OVER LIMIT" in report.summary
        assert "2 pages" in report.summary

    def test_shows_largest_sections_and_trimming_suggestions(self):
        section_counts = [
            SectionPageCount(section_id="3.1", title="Technical Approach", page_count=8),
            SectionPageCount(section_id="3.2", title="Key Personnel", page_count=6),
            SectionPageCount(section_id="3.3", title="Management Plan", page_count=5),
            SectionPageCount(section_id="3.4", title="Past Performance", page_count=3),
        ]
        service, _ = _make_formatting_service(
            page_count=22, section_page_counts=section_counts,
        )

        report = service.report_page_count(page_limit=20)

        assert len(report.largest_sections) == 3
        # Sorted by page count descending
        assert report.largest_sections[0].page_count >= report.largest_sections[1].page_count
        assert report.trimming_suggestions is not None
        assert len(report.trimming_suggestions) > 0
