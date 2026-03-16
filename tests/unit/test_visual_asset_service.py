"""Unit tests for VisualAssetService (driving port) -- visual asset generation and review.

Test Budget: 11 behaviors x 2 = 22 unit tests max.
Tests enter through driving port (VisualAssetService).
Driven ports (FigureGenerator, VisualAssetPort) mocked at port boundary.
Domain objects (FigurePlaceholder, GeneratedFigure, etc.) are real collaborators.

Behaviors:
1. Generate Mermaid figure produces SVG via FigureGenerator driven port
2. Create external brief for non-generatable figure with dimensions and resolution
3. Figure generation returns review-pending result with approve/revise/replace options
4. Cross-reference validation detects orphaned references
5. Cross-reference validation passes when all references valid
6. PES PDC gate blocks Wave 5 when sections have RED PDCs
7. Manual file replacement updates generated figure path
8. Corpus-reuse figure skips generation and returns pending-manual-review
9. Approve corpus-reuse figure changes status to approved
10. Replace corpus-reuse figure converts to standard generation with log
11. Cross-reference validation includes corpus-reused figures
"""

from __future__ import annotations

import pytest

from pes.domain.visual_asset import (
    CrossReferenceLog,
    ExternalBrief,
    FigurePlaceholder,
    GeneratedFigure,
)
from pes.domain.visual_asset_service import (
    FigureGenerationResult,
    PdcGateBlockedError,
    VisualAssetService,
)

# ---------------------------------------------------------------------------
# Fake driven ports at port boundary
# ---------------------------------------------------------------------------


class FakeFigureGenerator:
    """Fake driven port: produces deterministic figure output."""

    def __init__(self, *, svg_content: str = "<svg>test</svg>") -> None:
        self._svg_content = svg_content
        self.generate_called_with: dict | None = None

    def generate_svg(
        self,
        placeholder: FigurePlaceholder,
    ) -> str:
        self.generate_called_with = {"placeholder": placeholder}
        return self._svg_content


class FakeVisualAssetPort:
    """Fake driven port: in-memory persistence for visual assets."""

    def __init__(self) -> None:
        self.written_figures: list[GeneratedFigure] = []
        self.written_briefs: list[ExternalBrief] = []
        self.written_cross_ref_log: CrossReferenceLog | None = None
        self.figures_dir_files: dict[str, str] = {}

    def write_figure(self, figure: GeneratedFigure, content: str) -> None:
        self.written_figures.append(figure)
        self.figures_dir_files[figure.file_path] = content

    def write_external_brief(self, brief: ExternalBrief) -> None:
        self.written_briefs.append(brief)

    def write_cross_reference_log(self, log: CrossReferenceLog) -> None:
        self.written_cross_ref_log = log

    def replace_figure(self, figure_number: int, new_path: str) -> GeneratedFigure:
        return GeneratedFigure(
            figure_number=figure_number,
            section_id="replaced",
            file_path=new_path,
            format=new_path.split(".")[-1],
        )


class FakePdcChecker:
    """Fake driven port: checks PDC status for sections."""

    def __init__(self, *, all_green: bool = True, red_items: list[dict] | None = None) -> None:
        self._all_green = all_green
        self._red_items = red_items or []

    def all_sections_pdc_green(self) -> bool:
        return self._all_green

    def get_red_pdc_items(self) -> list[dict]:
        return self._red_items


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_service(
    generator: FakeFigureGenerator | None = None,
    port: FakeVisualAssetPort | None = None,
    pdc_checker: FakePdcChecker | None = None,
) -> tuple[VisualAssetService, FakeFigureGenerator, FakeVisualAssetPort, FakePdcChecker]:
    g = generator or FakeFigureGenerator()
    p = port or FakeVisualAssetPort()
    c = pdc_checker or FakePdcChecker()
    return (
        VisualAssetService(
            figure_generator=g,
            visual_asset_port=p,
            pdc_checker=c,
        ),
        g,
        p,
        c,
    )


def _mermaid_placeholder(*, figure_number: int = 1, section_id: str = "3.1") -> FigurePlaceholder:
    return FigurePlaceholder(
        figure_number=figure_number,
        section_id=section_id,
        description="System architecture block diagram",
        figure_type="block_diagram",
        generation_method="Mermaid",
    )


def _manual_placeholder(*, figure_number: int = 5, section_id: str = "3.4") -> FigurePlaceholder:
    return FigurePlaceholder(
        figure_number=figure_number,
        section_id=section_id,
        description="Photograph of hardware prototype",
        figure_type="photograph",
        generation_method="external",
    )


def _corpus_reuse_placeholder(*, figure_number: int = 3, section_id: str = "3.2") -> FigurePlaceholder:
    return FigurePlaceholder(
        figure_number=figure_number,
        section_id=section_id,
        description="Reused system architecture from AF243-001",
        figure_type="system-diagram",
        generation_method="corpus-reuse",
    )


# ---------------------------------------------------------------------------
# Behavior 1: Generate Mermaid figure produces SVG via driven port
# ---------------------------------------------------------------------------


class TestGenerateMermaidFigure:
    def test_produces_svg_via_figure_generator(self):
        service, gen, _port, _ = _make_service()
        placeholder = _mermaid_placeholder()

        result = service.generate_figure(placeholder=placeholder)

        assert result.file_path.endswith(".svg")
        assert gen.generate_called_with is not None
        assert gen.generate_called_with["placeholder"] == placeholder

    def test_writes_svg_to_figures_directory_via_port(self):
        service, _, port, _ = _make_service()
        placeholder = _mermaid_placeholder()

        service.generate_figure(placeholder=placeholder)

        assert len(port.written_figures) == 1
        assert port.written_figures[0].format == "svg"


# ---------------------------------------------------------------------------
# Behavior 2: External brief for non-generatable figure
# ---------------------------------------------------------------------------


class TestExternalBrief:
    def test_creates_brief_with_dimensions_and_resolution(self):
        service, _, port, _ = _make_service()
        placeholder = _manual_placeholder()

        service.generate_figure(placeholder=placeholder)

        assert len(port.written_briefs) == 1
        brief = port.written_briefs[0]
        assert brief.figure_number == 5
        assert brief.dimensions is not None
        assert brief.resolution is not None

    def test_brief_includes_content_description(self):
        service, _, port, _ = _make_service()
        placeholder = _manual_placeholder()

        service.generate_figure(placeholder=placeholder)

        brief = port.written_briefs[0]
        assert brief.content_description == placeholder.description


# ---------------------------------------------------------------------------
# Behavior 3: Figure generation returns review-pending result
# ---------------------------------------------------------------------------


class TestFigureReviewLifecycle:
    def test_generation_result_has_pending_review_status(self):
        service, _, _, _ = _make_service()
        placeholder = _mermaid_placeholder()

        result = service.generate_figure(placeholder=placeholder)

        assert result.review_status == "pending"

    def test_generation_result_has_approve_revise_replace_options(self):
        service, _, _, _ = _make_service()
        placeholder = _mermaid_placeholder()

        result = service.generate_figure(placeholder=placeholder)

        assert "approve" in result.review_options
        assert "revise" in result.review_options
        assert "replace" in result.review_options


# ---------------------------------------------------------------------------
# Behavior 4: Cross-reference validation detects orphaned references
# ---------------------------------------------------------------------------


class TestCrossRefOrphaned:
    def test_flags_orphaned_figure_reference(self):
        service, _, _port, _ = _make_service()
        generated = [
            GeneratedFigure(
                figure_number=i,
                section_id=f"3.{i}",
                file_path=f"fig-{i}.svg",
                format="svg",
            )
            for i in range(1, 6)
        ]
        text_references = [
            {"section_id": "3.3", "referenced_figure": 6},  # orphan
        ]

        log = service.validate_cross_references(
            generated_figures=generated,
            text_references=text_references,
        )

        assert not log.all_valid
        orphans = log.orphaned_references
        assert len(orphans) == 1
        assert orphans[0].referenced_figure == 6
        assert orphans[0].section_id == "3.3"

    def test_writes_cross_ref_log_to_port(self):
        service, _, port, _ = _make_service()
        generated = [
            GeneratedFigure(
                figure_number=1,
                section_id="3.1",
                file_path="fig-1.svg",
                format="svg",
            ),
        ]
        text_references = [
            {"section_id": "3.3", "referenced_figure": 6},
        ]

        service.validate_cross_references(
            generated_figures=generated,
            text_references=text_references,
        )

        assert port.written_cross_ref_log is not None


# ---------------------------------------------------------------------------
# Behavior 5: Cross-reference validation passes when all valid
# ---------------------------------------------------------------------------


class TestCrossRefAllValid:
    def test_all_valid_when_references_match(self):
        service, _, _, _ = _make_service()
        generated = [
            GeneratedFigure(
                figure_number=i,
                section_id=f"3.{i}",
                file_path=f"fig-{i}.svg",
                format="svg",
            )
            for i in range(1, 4)
        ]
        text_references = [
            {"section_id": "3.1", "referenced_figure": 1},
            {"section_id": "3.2", "referenced_figure": 2},
        ]

        log = service.validate_cross_references(
            generated_figures=generated,
            text_references=text_references,
        )

        assert log.all_valid
        assert log.orphaned_references == []


# ---------------------------------------------------------------------------
# Behavior 6: PES PDC gate blocks Wave 5 entry
# ---------------------------------------------------------------------------


class TestPdcGate:
    def test_blocks_when_sections_have_red_pdcs(self):
        pdc_checker = FakePdcChecker(
            all_green=False,
            red_items=[{"section_id": "3.2", "tier": 2, "item": "Risk mitigation"}],
        )
        service, _, _, _ = _make_service(pdc_checker=pdc_checker)

        with pytest.raises(PdcGateBlockedError) as exc_info:
            service.check_pdc_gate()

        assert "tier 1+2 pdcs green" in str(exc_info.value).lower()

    def test_passes_when_all_pdcs_green(self):
        pdc_checker = FakePdcChecker(all_green=True)
        service, _, _, _ = _make_service(pdc_checker=pdc_checker)

        # Should not raise
        service.check_pdc_gate()


# ---------------------------------------------------------------------------
# Behavior 7: Manual file replacement
# ---------------------------------------------------------------------------


class TestManualReplacement:
    def test_replaces_figure_with_manual_file(self):
        service, _, _port, _ = _make_service()

        result = service.replace_figure(figure_number=5, new_path="custom-photo.png")

        assert result.file_path == "custom-photo.png"
        assert result.format == "png"


# ---------------------------------------------------------------------------
# Behavior 8: Corpus-reuse figure skips generation, returns pending-manual-review
# ---------------------------------------------------------------------------


class TestCorpusReuseSkipsGeneration:
    def test_returns_pending_manual_review_status(self):
        service, gen, port, _ = _make_service()
        placeholder = _corpus_reuse_placeholder()

        result = service.generate_figure(placeholder=placeholder)

        assert result.review_status == "pending-manual-review"
        assert gen.generate_called_with is None  # Never invoked generator
        assert len(port.written_figures) == 0  # No figure written

    def test_does_not_invoke_figure_generator(self):
        service, gen, _, _ = _make_service()
        placeholder = _corpus_reuse_placeholder()

        service.generate_figure(placeholder=placeholder)

        assert gen.generate_called_with is None


# ---------------------------------------------------------------------------
# Behavior 9: Approve corpus-reuse figure changes status to approved
# ---------------------------------------------------------------------------


class TestApproveCorpusReuseFigure:
    def test_approve_changes_status_to_approved(self):
        service, _, _, _ = _make_service()
        placeholder = _corpus_reuse_placeholder()

        result = service.generate_figure(placeholder=placeholder)
        approved = service.approve_figure(result)

        assert approved.review_status == "approved"

    def test_approved_figure_retains_figure_number(self):
        service, _, _, _ = _make_service()
        placeholder = _corpus_reuse_placeholder()

        result = service.generate_figure(placeholder=placeholder)
        approved = service.approve_figure(result)

        assert approved.figure_number == placeholder.figure_number


# ---------------------------------------------------------------------------
# Behavior 10: Replace corpus-reuse converts to standard generation with log
# ---------------------------------------------------------------------------


class TestReplaceCorpusReuseFigure:
    def test_replace_changes_method_to_standard(self):
        service, _, _, _ = _make_service()
        placeholder = _corpus_reuse_placeholder()

        result = service.generate_figure(placeholder=placeholder)
        replaced = service.replace_corpus_reuse(result, new_method="svg")

        assert replaced.generation_method == "svg"
        assert replaced.original_method == "corpus-reuse"

    def test_replace_logs_method_change(self):
        service, _, _, _ = _make_service()
        placeholder = _corpus_reuse_placeholder()

        result = service.generate_figure(placeholder=placeholder)
        replaced = service.replace_corpus_reuse(result, new_method="mermaid")

        assert replaced.original_method == "corpus-reuse"
        assert replaced.generation_method == "mermaid"


# ---------------------------------------------------------------------------
# Behavior 11: Cross-reference validation includes corpus-reused figures
# ---------------------------------------------------------------------------


class TestCrossRefIncludesCorpusReuse:
    def test_corpus_reused_figure_resolves_references(self):
        service, _, _, _ = _make_service()
        # Mix of generated and corpus-reused figures
        generated = [
            GeneratedFigure(
                figure_number=1,
                section_id="3.1",
                file_path="fig-1.svg",
                format="svg",
            ),
        ]
        corpus_reused = [
            FigureGenerationResult(
                figure_number=3,
                section_id="3.2",
                file_path="fig-3-reused.png",
                format="png",
                review_status="approved",
            ),
        ]
        text_references = [
            {"section_id": "3.1", "referenced_figure": 1},
            {"section_id": "3.2", "referenced_figure": 3},
        ]

        log = service.validate_cross_references(
            generated_figures=generated,
            text_references=text_references,
            corpus_reused_figures=corpus_reused,
        )

        assert log.all_valid

    def test_missing_corpus_reused_figure_detected_as_orphan(self):
        service, _, _, _ = _make_service()
        generated = [
            GeneratedFigure(
                figure_number=1,
                section_id="3.1",
                file_path="fig-1.svg",
                format="svg",
            ),
        ]
        text_references = [
            {"section_id": "3.2", "referenced_figure": 3},  # no corpus-reused fig 3
        ]

        log = service.validate_cross_references(
            generated_figures=generated,
            text_references=text_references,
            corpus_reused_figures=[],
        )

        assert not log.all_valid
        assert log.orphaned_references[0].referenced_figure == 3
