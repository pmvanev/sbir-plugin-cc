"""PDF image extractor adapter using PyMuPDF (fitz).

Implements ImageExtractorPort to extract embedded images from PDF files.
Unsupported encodings are captured as failures without blocking other images.
"""

from __future__ import annotations

import logging
from pathlib import Path

import fitz  # PyMuPDF

from pes.ports.image_extractor_port import (
    ExtractionFailure,
    ExtractionResult,
    ImageExtractorPort,
    RawImage,
)

logger = logging.getLogger(__name__)


class PdfImageExtractorAdapter(ImageExtractorPort):
    """Extract images from PDF files via PyMuPDF."""

    def extract(self, file_path: Path) -> ExtractionResult:
        """Extract all images from a PDF document.

        Iterates pages, extracts each embedded image with metadata.
        Per-image failures logged without blocking other extractions.
        """
        images: list[RawImage] = []
        failures: list[ExtractionFailure] = []

        doc = fitz.open(str(file_path))
        for page in doc:
            page_num = page.number + 1  # Convert 0-indexed to 1-indexed
            page_text = page.get_text()
            page_images = page.get_images()

            for idx, img_info in enumerate(page_images, start=1):
                xref = img_info[0]
                try:
                    pix = fitz.Pixmap(doc, xref)
                    dpi = pix.xres if pix.xres > 0 else 72

                    # Determine format from image data
                    img_bytes = pix.tobytes("png")
                    fmt = _detect_format(img_info)

                    raw = RawImage(
                        image_bytes=img_bytes,
                        format=fmt,
                        page_number=page_num,
                        position_index=idx,
                        width=pix.width,
                        height=pix.height,
                        dpi=dpi,
                        caption=_extract_caption(page_text, idx),
                        surrounding_text=page_text.strip(),
                    )
                    images.append(raw)
                except Exception as exc:
                    reason = str(exc) if str(exc) else "unsupported encoding"
                    logger.warning(
                        "Failed to extract image xref=%d on page %d: %s",
                        xref, page_num, reason,
                    )
                    failures.append(ExtractionFailure(
                        page_number=page_num,
                        reason=reason,
                    ))

        return ExtractionResult(images=images, failures=failures)


def _detect_format(img_info: tuple) -> str:
    """Detect image format from fitz image info tuple."""
    # img_info[7] is the colorspace name hint, but not reliable for format.
    # Use the extension hint from img_info if available.
    cs_name = img_info[7] if len(img_info) > 7 else ""
    cs_lower = cs_name.lower()
    if cs_lower in ("png", "jpeg", "jpg"):
        return "jpeg" if cs_lower == "jpg" else cs_lower
    return "png"  # Default to PNG for extracted pixmaps


def _extract_caption(page_text: str, position: int) -> str:
    """Extract a figure caption from page text, if present."""
    lines = page_text.strip().split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("figure"):
            return stripped
    return ""
