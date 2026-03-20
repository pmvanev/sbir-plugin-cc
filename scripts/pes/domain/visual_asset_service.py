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

    def write_figure(
        self,
        figure: GeneratedFigure,
        content: str,
        pdf_preview: bytes | None = None,
    ) -> None: ...

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
    generation_method: str = ""
    original_method: str = ""
    prompt_hash: str = ""
    iteration_count: int = 0


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
        - corpus-reuse -> skip generation, return pending-manual-review
        - external -> ExternalBrief written to port
        - Mermaid (default) -> SVG via FigureGenerator
        """
        method = placeholder.generation_method.lower()
        if method == "corpus-reuse":
            return self._corpus_reuse(placeholder)
        if method == "external":
            return self._create_external_brief(placeholder)
        if method == "tikz":
            return self._generate_tikz(placeholder)
        return self._generate_mermaid(placeholder)

    def validate_cross_references(
        self,
        generated_figures: list[GeneratedFigure],
        text_references: list[dict],
        corpus_reused_figures: list[FigureGenerationResult] | None = None,
    ) -> CrossReferenceLog:
        """Validate that all text references point to existing figures.

        Includes both generated and corpus-reused figures in the lookup.
        Returns CrossReferenceLog with orphaned references flagged.
        Persists the log via the driven port.
        """
        existing_numbers = {f.figure_number for f in generated_figures}
        if corpus_reused_figures:
            existing_numbers |= {f.figure_number for f in corpus_reused_figures}
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

    def approve_figure(
        self,
        result: FigureGenerationResult,
    ) -> FigureGenerationResult:
        """Approve a figure for document assembly.

        Returns a new result with status changed to approved.
        """
        return FigureGenerationResult(
            figure_number=result.figure_number,
            section_id=result.section_id,
            file_path=result.file_path,
            format=result.format,
            review_status="approved",
            review_options=result.review_options,
            generation_method=result.generation_method,
            original_method=result.original_method,
        )

    def replace_corpus_reuse(
        self,
        result: FigureGenerationResult,
        new_method: str,
    ) -> FigureGenerationResult:
        """Replace a corpus-reuse figure with standard generation.

        Returns a new result with the generation method changed and
        original method recorded for audit.
        """
        return FigureGenerationResult(
            figure_number=result.figure_number,
            section_id=result.section_id,
            file_path=result.file_path,
            format=result.format,
            review_status="pending",
            review_options=result.review_options,
            generation_method=new_method,
            original_method=result.generation_method,
        )

    def _corpus_reuse(
        self,
        placeholder: FigurePlaceholder,
    ) -> FigureGenerationResult:
        """Handle corpus-reuse: skip generation, present for review."""
        return FigureGenerationResult(
            figure_number=placeholder.figure_number,
            section_id=placeholder.section_id,
            file_path="",
            format="corpus-reuse",
            review_status="pending-manual-review",
            review_options=["approve", "revise", "replace"],
            generation_method="corpus-reuse",
        )

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

    def _generate_tikz(
        self,
        placeholder: FigurePlaceholder,
    ) -> FigureGenerationResult:
        """Generate TikZ figure specification (pending compilation)."""
        file_name = f"figure-{placeholder.figure_number}.tex"
        return FigureGenerationResult(
            figure_number=placeholder.figure_number,
            section_id=placeholder.section_id,
            file_path=file_name,
            format="tikz",
            generation_method="tikz",
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
