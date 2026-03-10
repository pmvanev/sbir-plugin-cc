"""Unit tests for formatting through FormattingService driving port.

Test Budget: 3 behaviors x 2 = 6 unit tests max.
Current count: 4 tests (1 parametrized x 4 + 1 + 1 = 6 within budget).

Tests verify through driving port (FormattingService):
1. Loads format template with all required fields by agency + solicitation type
2. Returns None when template not found for unknown agency/type
3. Multiple agencies loadable without code changes (extensibility)
"""

from __future__ import annotations

import pytest

from pes.domain.formatting import FormatTemplate
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
