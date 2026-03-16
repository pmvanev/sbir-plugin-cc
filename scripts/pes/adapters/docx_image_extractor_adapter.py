"""DOCX image extractor adapter using python-docx.

Implements ImageExtractorPort to extract embedded images from DOCX files.
Reads image parts from document relationships, with per-image failure handling.
"""

from __future__ import annotations

import logging
from pathlib import Path

from docx import Document

from pes.ports.image_extractor_port import (
    ExtractionFailure,
    ExtractionResult,
    ImageExtractorPort,
    RawImage,
)

logger = logging.getLogger(__name__)

IMAGE_REL_TYPE = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
)


class DocxImageExtractorAdapter(ImageExtractorPort):
    """Extract images from DOCX files via python-docx."""

    def extract(self, file_path: Path) -> ExtractionResult:
        """Extract all embedded images from a DOCX document.

        Iterates document relationships to find image parts.
        Per-image failures logged without blocking other extractions.
        """
        images: list[RawImage] = []
        failures: list[ExtractionFailure] = []

        doc = Document(str(file_path))
        full_text = "\n".join(p.text for p in doc.paragraphs)

        # Collect image relationships
        image_rels = {
            rid: rel
            for rid, rel in doc.part.rels.items()
            if rel.reltype == IMAGE_REL_TYPE
        }

        for position, (rid, rel) in enumerate(image_rels.items(), start=1):
            try:
                part = rel.target_part
                blob = part.blob
                content_type = part.content_type
                fmt = _format_from_content_type(content_type)

                # DOCX doesn't have page numbers; use position as proxy
                page_number = 1

                # Estimate dimensions from inline shapes if available
                width, height, dpi = _dimensions_from_shapes(
                    doc, rid, position,
                )

                caption = _extract_caption_from_text(full_text, position)

                raw = RawImage(
                    image_bytes=blob,
                    format=fmt,
                    page_number=page_number,
                    position_index=position,
                    width=width,
                    height=height,
                    dpi=dpi,
                    caption=caption,
                    surrounding_text=full_text.strip(),
                )
                images.append(raw)
            except Exception as exc:
                reason = str(exc) if str(exc) else "unsupported encoding"
                partname = getattr(rel, "target_part", None)
                partname_str = getattr(partname, "partname", rid) if partname else rid
                logger.warning(
                    "Failed to extract image %s: %s",
                    partname_str, reason,
                )
                failures.append(ExtractionFailure(
                    page_number=position,
                    reason=reason,
                ))

        return ExtractionResult(images=images, failures=failures)


def _format_from_content_type(content_type: str) -> str:
    """Map MIME content type to simple format string."""
    ct_lower = content_type.lower()
    if "png" in ct_lower:
        return "png"
    if "jpeg" in ct_lower or "jpg" in ct_lower:
        return "jpeg"
    if "gif" in ct_lower:
        return "gif"
    if "bmp" in ct_lower:
        return "bmp"
    if "tiff" in ct_lower:
        return "tiff"
    # Return the subtype as-is for uncommon types
    parts = ct_lower.split("/")
    return parts[-1] if len(parts) > 1 else ct_lower


def _dimensions_from_shapes(
    doc: Document,
    rel_id: str,
    fallback_index: int,
) -> tuple[int, int, int]:
    """Extract width, height, DPI from inline shapes if available.

    Returns (width_px, height_px, dpi). Defaults to (0, 0, 72) if not found.
    """
    # EMU = English Metric Units. 914400 EMU = 1 inch.
    emu_per_inch = 914_400
    default_dpi = 72

    for shape in doc.inline_shapes:
        if shape.width and shape.height:
            width_inches = shape.width / emu_per_inch
            height_inches = shape.height / emu_per_inch
            # Estimate pixels at default DPI
            width_px = int(width_inches * default_dpi)
            height_px = int(height_inches * default_dpi)
            return width_px, height_px, default_dpi

    return 0, 0, default_dpi


def _extract_caption_from_text(full_text: str, position: int) -> str:
    """Extract a figure caption from document text."""
    lines = full_text.strip().split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("figure"):
            return stripped
    return ""
