"""Unit tests for PdfImageExtractorAdapter.

Tests the PDF adapter through the ImageExtractorPort interface,
mocking PyMuPDF (fitz) at the import boundary.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def _make_fitz_image_info(
    xref: int = 1,
    smask: int = 0,
    width: int = 2048,
    height: int = 1536,
    bpc: int = 8,
    colorspace: str = "DeviceRGB",
    cs_name: str = "png",
) -> tuple:
    """Build a tuple matching fitz page.get_images() output."""
    return (xref, smask, width, height, bpc, colorspace, "", cs_name, "")


def _make_fitz_page(
    images: list[tuple] | None = None,
    page_number: int = 0,
    text: str = "Section content about the proposed system.",
) -> MagicMock:
    """Build a mock fitz page."""
    page = MagicMock()
    page.number = page_number
    page.get_images.return_value = images or []
    page.get_text.return_value = text
    return page


def _make_fitz_pixmap(
    width: int = 2048,
    height: int = 1536,
    xres: int = 300,
    yres: int = 300,
    samples: bytes = b"\x00" * 100,
) -> MagicMock:
    """Build a mock fitz Pixmap."""
    pix = MagicMock()
    pix.width = width
    pix.height = height
    pix.xres = xres
    pix.yres = yres
    pix.tobytes.return_value = samples
    pix.samples = samples
    pix.n = 3
    return pix


class TestPdfImageExtractorAdapter:
    """PDF extraction via ImageExtractorPort interface."""

    def test_extracts_images_with_page_number_and_position(self):
        """AC: PDF extraction returns images with page number, position, surrounding text."""
        fitz_module = MagicMock()
        doc = MagicMock()
        page = _make_fitz_page(
            images=[_make_fitz_image_info(xref=10)],
            page_number=6,
            text="Figure 3: System Architecture\nThe proposed approach leverages...",
        )
        doc.__iter__ = MagicMock(return_value=iter([page]))
        doc.__len__ = MagicMock(return_value=1)
        fitz_module.open.return_value = doc

        pixmap = _make_fitz_pixmap(xres=300, yres=300)
        fitz_module.Pixmap.return_value = pixmap

        with patch.dict("sys.modules", {"fitz": fitz_module}):
            from pes.adapters.pdf_image_extractor_adapter import PdfImageExtractorAdapter

            adapter = PdfImageExtractorAdapter()
            result = adapter.extract(Path("proposal.pdf"))

        assert len(result.images) == 1
        img = result.images[0]
        assert img.page_number == 7  # 1-indexed from fitz 0-indexed
        assert img.position_index == 1
        assert img.surrounding_text != ""
        assert img.dpi == 300
        assert img.width == 2048
        assert img.height == 1536
        assert len(result.failures) == 0

    def test_extracts_multiple_images_across_pages(self):
        """AC: PDF extraction returns all images from multi-page document."""
        fitz_module = MagicMock()
        doc = MagicMock()

        page0 = _make_fitz_page(
            images=[_make_fitz_image_info(xref=10), _make_fitz_image_info(xref=11)],
            page_number=0,
        )
        page1 = _make_fitz_page(
            images=[_make_fitz_image_info(xref=12)],
            page_number=1,
        )
        doc.__iter__ = MagicMock(return_value=iter([page0, page1]))
        doc.__len__ = MagicMock(return_value=2)
        fitz_module.open.return_value = doc

        pixmap = _make_fitz_pixmap()
        fitz_module.Pixmap.return_value = pixmap

        with patch.dict("sys.modules", {"fitz": fitz_module}):
            from pes.adapters.pdf_image_extractor_adapter import PdfImageExtractorAdapter

            adapter = PdfImageExtractorAdapter()
            result = adapter.extract(Path("multi-page.pdf"))

        assert len(result.images) == 3
        # Page numbers are 1-indexed
        assert result.images[0].page_number == 1
        assert result.images[1].page_number == 1
        assert result.images[2].page_number == 2
        # Position indices are per-page
        assert result.images[0].position_index == 1
        assert result.images[1].position_index == 2
        assert result.images[2].position_index == 1

    def test_unsupported_encoding_logged_without_blocking(self):
        """AC: Unsupported encodings logged per-image without blocking other extractions."""
        fitz_module = MagicMock()
        doc = MagicMock()

        page = _make_fitz_page(
            images=[
                _make_fitz_image_info(xref=10),
                _make_fitz_image_info(xref=11),
            ],
            page_number=0,
        )
        doc.__iter__ = MagicMock(return_value=iter([page]))
        doc.__len__ = MagicMock(return_value=1)
        fitz_module.open.return_value = doc

        good_pixmap = _make_fitz_pixmap()
        # Second image extraction raises
        call_count = 0

        def pixmap_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise RuntimeError("unsupported encoding")
            return good_pixmap

        fitz_module.Pixmap.side_effect = pixmap_side_effect

        with patch.dict("sys.modules", {"fitz": fitz_module}):
            from pes.adapters.pdf_image_extractor_adapter import PdfImageExtractorAdapter

            adapter = PdfImageExtractorAdapter()
            result = adapter.extract(Path("mixed.pdf"))

        assert len(result.images) == 1
        assert len(result.failures) == 1
        assert result.failures[0].page_number == 1
        assert "unsupported encoding" in result.failures[0].reason.lower()

    def test_text_only_document_returns_empty(self):
        """AC: Text-only PDF returns zero images, no errors."""
        fitz_module = MagicMock()
        doc = MagicMock()

        page = _make_fitz_page(images=[], page_number=0)
        doc.__iter__ = MagicMock(return_value=iter([page]))
        doc.__len__ = MagicMock(return_value=1)
        fitz_module.open.return_value = doc

        with patch.dict("sys.modules", {"fitz": fitz_module}):
            from pes.adapters.pdf_image_extractor_adapter import PdfImageExtractorAdapter

            adapter = PdfImageExtractorAdapter()
            result = adapter.extract(Path("text-only.pdf"))

        assert len(result.images) == 0
        assert len(result.failures) == 0

    def test_preserves_image_format_no_conversion(self):
        """AC: Images stored as-extracted (PNG, JPEG) -- no format conversion."""
        fitz_module = MagicMock()
        doc = MagicMock()

        page = _make_fitz_page(
            images=[_make_fitz_image_info(xref=10, cs_name="png")],
            page_number=0,
        )
        doc.__iter__ = MagicMock(return_value=iter([page]))
        doc.__len__ = MagicMock(return_value=1)
        fitz_module.open.return_value = doc

        png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
        pixmap = _make_fitz_pixmap()
        pixmap.tobytes.return_value = png_bytes
        fitz_module.Pixmap.return_value = pixmap

        with patch.dict("sys.modules", {"fitz": fitz_module}):
            from pes.adapters.pdf_image_extractor_adapter import PdfImageExtractorAdapter

            adapter = PdfImageExtractorAdapter()
            result = adapter.extract(Path("format-test.pdf"))

        assert len(result.images) == 1
        assert result.images[0].format == "png"
        assert result.images[0].image_bytes == png_bytes

    @pytest.mark.parametrize(
        "dpi,expected_level",
        [(300, "high"), (200, "medium"), (72, "low")],
    )
    def test_quality_assessment_from_dpi(self, dpi: int, expected_level: str):
        """AC: Quality assessment records DPI; levels: high/medium/low."""
        fitz_module = MagicMock()
        doc = MagicMock()

        page = _make_fitz_page(
            images=[_make_fitz_image_info(xref=10)],
            page_number=0,
        )
        doc.__iter__ = MagicMock(return_value=iter([page]))
        doc.__len__ = MagicMock(return_value=1)
        fitz_module.open.return_value = doc

        pixmap = _make_fitz_pixmap(xres=dpi, yres=dpi)
        fitz_module.Pixmap.return_value = pixmap

        with patch.dict("sys.modules", {"fitz": fitz_module}):
            from pes.adapters.pdf_image_extractor_adapter import PdfImageExtractorAdapter

            adapter = PdfImageExtractorAdapter()
            result = adapter.extract(Path("quality-test.pdf"))

        assert len(result.images) == 1
        assert result.images[0].dpi == dpi
