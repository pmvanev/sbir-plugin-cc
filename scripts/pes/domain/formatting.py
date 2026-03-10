"""Formatting domain model -- format templates for solicitation documents."""

from __future__ import annotations

from dataclasses import dataclass


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
