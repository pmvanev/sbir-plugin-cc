"""Integration tests for FileVisualAssetAdapter -- TikZ persistence.

Adapter tests use real filesystem (tmp_path), no mocks.
Verifies TikZ source (.tex) and preview (.pdf) write/read behavior.

Test Budget: 2 behaviors x 2 = 4 max integration tests

Behaviors:
1. write_figure persists TikZ .tex source and .pdf preview when format is 'tikz'
2. Existing write_figure behavior unchanged for non-tikz formats
"""

from __future__ import annotations

from pathlib import Path

from pes.adapters.file_visual_asset_adapter import FileVisualAssetAdapter
from pes.domain.visual_asset import GeneratedFigure


class TestWriteFigureTikzPersistence:
    """write_figure writes both .tex source and .pdf preview for tikz format."""

    def test_writes_tex_source_and_pdf_preview(self, tmp_path: Path) -> None:
        adapter = FileVisualAssetAdapter(tmp_path)
        figure = GeneratedFigure(
            figure_number=1,
            section_id="3.1",
            file_path="figure-1.tex",
            format="tikz",
        )
        tex_content = r"\begin{tikzpicture}\draw (0,0) -- (1,1);\end{tikzpicture}"
        pdf_content = b"%PDF-1.4 fake preview bytes"

        adapter.write_figure(figure, tex_content, pdf_preview=pdf_content)

        figures_dir = tmp_path / "figures"
        tex_file = figures_dir / "figure-1.tex"
        pdf_file = figures_dir / "figure-1.pdf"

        assert tex_file.exists()
        assert tex_file.read_text(encoding="utf-8") == tex_content
        assert pdf_file.exists()
        assert pdf_file.read_bytes() == pdf_content

    def test_writes_only_tex_when_no_pdf_preview(self, tmp_path: Path) -> None:
        adapter = FileVisualAssetAdapter(tmp_path)
        figure = GeneratedFigure(
            figure_number=2,
            section_id="3.2",
            file_path="figure-2.tex",
            format="tikz",
        )
        tex_content = r"\begin{tikzpicture}\node {Hello};\end{tikzpicture}"

        adapter.write_figure(figure, tex_content)

        figures_dir = tmp_path / "figures"
        tex_file = figures_dir / "figure-2.tex"
        pdf_file = figures_dir / "figure-2.pdf"

        assert tex_file.exists()
        assert tex_file.read_text(encoding="utf-8") == tex_content
        assert not pdf_file.exists()


class TestWriteFigureExistingBehaviorUnchanged:
    """Existing write_figure for non-tikz formats unchanged."""

    def test_writes_svg_content_as_text(self, tmp_path: Path) -> None:
        adapter = FileVisualAssetAdapter(tmp_path)
        figure = GeneratedFigure(
            figure_number=3,
            section_id="3.3",
            file_path="figure-3.svg",
            format="svg",
        )
        svg_content = "<svg><rect width='100' height='100'/></svg>"

        adapter.write_figure(figure, svg_content)

        figures_dir = tmp_path / "figures"
        svg_file = figures_dir / "figure-3.svg"

        assert svg_file.exists()
        assert svg_file.read_text(encoding="utf-8") == svg_content
