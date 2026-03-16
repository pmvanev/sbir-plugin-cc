"""Unit tests for DocxImageExtractorAdapter.

Tests the DOCX adapter through the ImageExtractorPort interface,
mocking python-docx at the import boundary.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def _make_image_part(
    content_type: str = "image/png",
    blob: bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50,
    partname: str = "/word/media/image1.png",
) -> MagicMock:
    """Build a mock docx image part."""
    part = MagicMock()
    part.content_type = content_type
    part.blob = blob
    part.partname = partname
    return part


def _make_inline_shape(
    rel_id: str = "rId1",
    width_emu: int = 6_096_000,  # ~2048px at 300 DPI
    height_emu: int = 4_572_000,  # ~1536px at 300 DPI
) -> MagicMock:
    """Build a mock docx inline shape."""
    shape = MagicMock()
    shape.width = width_emu
    shape.height = height_emu
    # The inline shape's _inline element
    inline = MagicMock()
    blip = MagicMock()
    blip.get.return_value = rel_id
    inline.findall.return_value = [blip]
    shape._inline = inline
    return shape


class TestDocxImageExtractorAdapter:
    """DOCX extraction via ImageExtractorPort interface."""

    def test_extracts_embedded_images_with_metadata(self):
        """AC: DOCX extraction returns embedded images with relationship metadata."""
        docx_module = MagicMock()
        doc = MagicMock()

        # Set up image parts
        img_part = _make_image_part(
            content_type="image/png",
            blob=b"\x89PNG" + b"\x00" * 60,
            partname="/word/media/image1.png",
        )

        # Set up relationships
        rel = MagicMock()
        rel.rId = "rId1"
        rel.target_part = img_part
        rel.reltype = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"

        doc_part = MagicMock()
        doc_part.rels = {"rId1": rel}
        doc.part = doc_part

        # Set up paragraphs for context extraction
        para1 = MagicMock()
        para1.text = "Figure 1: System Overview"
        para2 = MagicMock()
        para2.text = "The system consists of three components."
        doc.paragraphs = [para1, para2]

        # Set up inline shapes
        doc.inline_shapes = [_make_inline_shape(rel_id="rId1")]

        docx_module.Document.return_value = doc

        with patch.dict("sys.modules", {"docx": docx_module}):
            from pes.adapters.docx_image_extractor_adapter import DocxImageExtractorAdapter

            adapter = DocxImageExtractorAdapter()
            result = adapter.extract(Path("proposal.docx"))

        assert len(result.images) == 1
        img = result.images[0]
        assert img.format == "png"
        assert img.image_bytes == b"\x89PNG" + b"\x00" * 60
        assert img.page_number >= 1
        assert img.position_index == 1
        assert len(result.failures) == 0

    def test_extracts_multiple_images(self):
        """AC: Multiple embedded images extracted with correct positions."""
        docx_module = MagicMock()
        doc = MagicMock()

        parts = []
        rels = {}
        shapes = []
        for i in range(4):
            part = _make_image_part(
                content_type="image/jpeg" if i % 2 else "image/png",
                blob=f"image-{i}".encode(),
                partname=f"/word/media/image{i+1}.{'jpeg' if i % 2 else 'png'}",
            )
            parts.append(part)
            rel = MagicMock()
            rel.rId = f"rId{i+1}"
            rel.target_part = part
            rel.reltype = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
            rels[f"rId{i+1}"] = rel
            shapes.append(_make_inline_shape(rel_id=f"rId{i+1}"))

        doc_part = MagicMock()
        doc_part.rels = rels
        doc.part = doc_part
        doc.paragraphs = []
        doc.inline_shapes = shapes

        docx_module.Document.return_value = doc

        with patch.dict("sys.modules", {"docx": docx_module}):
            from pes.adapters.docx_image_extractor_adapter import DocxImageExtractorAdapter

            adapter = DocxImageExtractorAdapter()
            result = adapter.extract(Path("multi-image.docx"))

        assert len(result.images) == 4
        # Position indices should increment
        for i, img in enumerate(result.images):
            assert img.position_index == i + 1

    def test_text_only_docx_returns_empty(self):
        """AC: DOCX with no images returns empty result."""
        docx_module = MagicMock()
        doc = MagicMock()
        doc_part = MagicMock()
        doc_part.rels = {}
        doc.part = doc_part
        doc.paragraphs = [MagicMock(text="Just text.")]
        doc.inline_shapes = []

        docx_module.Document.return_value = doc

        with patch.dict("sys.modules", {"docx": docx_module}):
            from pes.adapters.docx_image_extractor_adapter import DocxImageExtractorAdapter

            adapter = DocxImageExtractorAdapter()
            result = adapter.extract(Path("text-only.docx"))

        assert len(result.images) == 0
        assert len(result.failures) == 0

    def test_unsupported_image_type_logged_as_failure(self):
        """AC: Unsupported image encodings logged without blocking."""
        docx_module = MagicMock()
        doc = MagicMock()

        # Good image
        good_part = _make_image_part(content_type="image/png", blob=b"good-png")
        good_rel = MagicMock()
        good_rel.rId = "rId1"
        good_rel.target_part = good_part
        good_rel.reltype = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"

        # Bad image -- accessing blob raises
        bad_part = MagicMock()
        bad_part.content_type = "image/x-wmf"
        type(bad_part).blob = property(
            lambda self: (_ for _ in ()).throw(ValueError("unsupported encoding"))
        )
        bad_part.partname = "/word/media/image2.wmf"

        bad_rel = MagicMock()
        bad_rel.rId = "rId2"
        bad_rel.target_part = bad_part
        bad_rel.reltype = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"

        doc_part = MagicMock()
        doc_part.rels = {"rId1": good_rel, "rId2": bad_rel}
        doc.part = doc_part
        doc.paragraphs = []
        doc.inline_shapes = [
            _make_inline_shape(rel_id="rId1"),
            _make_inline_shape(rel_id="rId2"),
        ]

        docx_module.Document.return_value = doc

        with patch.dict("sys.modules", {"docx": docx_module}):
            from pes.adapters.docx_image_extractor_adapter import DocxImageExtractorAdapter

            adapter = DocxImageExtractorAdapter()
            result = adapter.extract(Path("mixed.docx"))

        assert len(result.images) == 1
        assert len(result.failures) == 1
        assert "unsupported" in result.failures[0].reason.lower()
