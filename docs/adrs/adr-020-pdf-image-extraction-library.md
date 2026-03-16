# ADR-020: PyMuPDF for PDF Image Extraction

## Status

Accepted

## Context

The corpus image reuse feature requires extracting embedded images from PDF files during `corpus add` ingestion. Requirements:

- Extract raster images (PNG, JPEG) with page number and position metadata
- Read DPI and resolution for quality assessment
- Handle common PDF image encodings (DCT, Flate, LZW)
- Log extraction failures for unsupported encodings without blocking other images
- Solo developer on Windows (Git Bash), Python 3.12+

The codebase already has `python-docx` for DOCX handling but no PDF image extraction library.

## Decision

Use **PyMuPDF (fitz)** >= 1.24 for PDF image extraction.

## Alternatives Considered

### Alternative 1: pdfplumber (MIT)

- **Pros**: MIT license, good text extraction, used in many Python projects
- **Cons**: Image extraction is limited -- relies on pdfminer which extracts image references but not reliable image bytes. No direct DPI metadata. Would require Pillow post-processing for every image to determine resolution.
- **Rejected**: Image extraction quality insufficient for the primary use case. pdfplumber is text-first; images are secondary.

### Alternative 2: PyPDF2 / pypdf (BSD)

- **Pros**: BSD license, lightweight, pure Python
- **Cons**: Image extraction is basic -- only handles DCT (JPEG) and FlateDecode (PNG) natively. JBIG2, CCITT, and JPX require external decoders. API requires manual reconstruction of image bytes from PDF stream objects. No DPI metadata in extraction output.
- **Rejected**: Too much manual work to reconstruct images reliably. The user stories include 40+ proposal batch ingestion (Marcus Chen persona) -- extraction must be robust across encoding types.

### Alternative 3: pdf2image + Poppler (GPL)

- **Pros**: Renders full pages as images, handles any encoding
- **Cons**: GPL license (Poppler), requires Poppler system binary installation on Windows, renders entire pages not individual figures, no metadata about figure boundaries.
- **Rejected**: Page rendering is the wrong abstraction -- we need individual embedded images, not page screenshots. Poppler installation burden on Windows is significant.

## Consequences

### Positive

- Robust image extraction across PDF encoding types (DCT, Flate, JBIG2, CCITT, JPX)
- Direct access to image DPI and resolution metadata via `fitz.Pixmap`
- Fast extraction -- C library bindings, handles 40+ document batches efficiently
- Page number and position metadata available per image
- Active maintenance (monthly releases, 20k+ GitHub stars)

### Negative

- **AGPL-3.0 license**: PyMuPDF uses AGPL-3.0 for the open-source version. This is acceptable because:
  1. The SBIR plugin is distributed as an open-source Claude Code plugin (not proprietary SaaS)
  2. PyMuPDF is used as a library dependency, not modified
  3. A commercial license is available if license requirements change
  4. The adapter pattern isolates PyMuPDF behind a port -- replacing it requires only a new adapter
- **Binary dependency**: PyMuPDF includes compiled MuPDF bindings. `pip install PyMuPDF` handles this on Windows/Mac/Linux. No system package installation required.
- **Larger dependency footprint**: ~30MB installed size vs ~5MB for pypdf

### Quality Attribute Impact

- **Testability**: PyMuPDF is isolated behind the `ImageExtractor` port. Unit tests use in-memory stubs, never touch PyMuPDF directly.
- **Maintainability**: Adapter pattern means swapping to another library requires only a new adapter implementation.
- **Time-to-market**: PyMuPDF's mature API reduces implementation effort vs. manual PDF stream parsing with pypdf.
