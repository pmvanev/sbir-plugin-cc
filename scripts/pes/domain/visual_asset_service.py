"""Visual asset service -- driving port for figure generation and review lifecycle.

Orchestrates: figure generation routed by method, human review checkpoint per figure,
cross-reference validation, manual replacement, and PES PDC gate enforcement.
Delegates to FigureGenerator driven port for SVG production.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from pes.domain.visual_asset import (
    CrossReferenceEntry,
    CrossReferenceLog,
    ExternalBrief,
    FigurePlaceholder,
    GeneratedFigure,
)


class FigureGenerator(Protocol):
    """Driven port: generates SVG content from a figure placeholder."""

    def generate_svg(self, placeholder: FigurePlaceholder) -> str: ...


class FigurePersistence(Protocol):
    """Driven port: persists figure artifacts and cross-reference logs."""

    def write_figure(self, figure: GeneratedFigure, content: str) -> None: ...

    def write_external_brief(self, brief: ExternalBrief) -> None: ...

    def write_cross_reference_log(self, log: CrossReferenceLog) -> None: ...

    def replace_figure(self, figure_number: int, new_path: str) -> GeneratedFigure: ...


class PdcChecker(Protocol):
    """Driven port: checks PDC status for wave gate enforcement."""

    def all_sections_pdc_green(self) -> bool: ...

    def get_red_pdc_items(self) -> list[dict]: ...


class PdcGateBlockedError(Exception):
    """Raised when Wave 5 entry is blocked by RED PDC items."""


@dataclass
class FigureGenerationResult:
    """Result of generating or classifying a figure, pending human review."""

    figure_number: int
    section_id: str
    file_path: str
    format: str
    review_status: str = "pending"
    review_options: list[str] = field(
        default_factory=lambda: ["approve", "revise", "replace"],
    )


class VisualAssetService:
    """Driving port: orchestrates visual asset generation and review lifecycle.

    Routes generation by FigurePlaceholder.generation_method:
    - "Mermaid": delegates to FigureGenerator for SVG production
    - "external": creates an ExternalBrief with dimensions and resolution
    """

    def __init__(
        self,
        figure_generator: FigureGenerator,
        visual_asset_port: FigurePersistence,
        pdc_checker: PdcChecker,
    ) -> None:
        self._generator = figure_generator
        self._port = visual_asset_port
        self._pdc_checker = pdc_checker

    def generate_figure(
        self,
        placeholder: FigurePlaceholder,
    ) -> FigureGenerationResult:
        """Generate a figure from its placeholder specification.

        Routes by generation_method:
        - Mermaid -> SVG via FigureGenerator
        - external -> ExternalBrief written to port
        """
        if placeholder.generation_method.lower() == "external":
            return self._create_external_brief(placeholder)
        return self._generate_mermaid(placeholder)

    def validate_cross_references(
        self,
        generated_figures: list[GeneratedFigure],
        text_references: list[dict],
    ) -> CrossReferenceLog:
        """Validate that all text references point to existing figures.

        Returns CrossReferenceLog with orphaned references flagged.
        Persists the log via the driven port.
        """
        existing_numbers = {f.figure_number for f in generated_figures}
        entries = []
        for ref in text_references:
            fig_num = ref["referenced_figure"]
            entries.append(
                CrossReferenceEntry(
                    section_id=ref["section_id"],
                    referenced_figure=fig_num,
                    exists=fig_num in existing_numbers,
                )
            )
        log = CrossReferenceLog(entries=entries)
        self._port.write_cross_reference_log(log)
        return log

    def check_pdc_gate(self) -> None:
        """Enforce PES PDC gate before Wave 5 entry.

        Raises PdcGateBlockedError if any section has RED Tier 1+2 PDC items.
        """
        if not self._pdc_checker.all_sections_pdc_green():
            raise PdcGateBlockedError("Wave 5 requires all sections to have Tier 1+2 PDCs GREEN")

    def replace_figure(
        self,
        figure_number: int,
        new_path: str,
    ) -> GeneratedFigure:
        """Replace a generated figure with a manual file.

        Delegates to the driven port for persistence.
        """
        return self._port.replace_figure(figure_number, new_path)

    def _generate_mermaid(
        self,
        placeholder: FigurePlaceholder,
    ) -> FigureGenerationResult:
        """Generate SVG from Mermaid specification."""
        svg_content = self._generator.generate_svg(placeholder)
        file_name = f"figure-{placeholder.figure_number}.svg"
        figure = GeneratedFigure(
            figure_number=placeholder.figure_number,
            section_id=placeholder.section_id,
            file_path=file_name,
            format="svg",
        )
        self._port.write_figure(figure, svg_content)
        return FigureGenerationResult(
            figure_number=placeholder.figure_number,
            section_id=placeholder.section_id,
            file_path=file_name,
            format="svg",
        )

    def _create_external_brief(
        self,
        placeholder: FigurePlaceholder,
    ) -> FigureGenerationResult:
        """Create an external brief for a non-generatable figure."""
        brief = ExternalBrief(
            figure_number=placeholder.figure_number,
            section_id=placeholder.section_id,
            content_description=placeholder.description,
            dimensions="6.5in x 4.5in",
            resolution="300 DPI",
        )
        self._port.write_external_brief(brief)
        file_name = f"figure-{placeholder.figure_number}-brief.json"
        return FigureGenerationResult(
            figure_number=placeholder.figure_number,
            section_id=placeholder.section_id,
            file_path=file_name,
            format="brief",
        )
