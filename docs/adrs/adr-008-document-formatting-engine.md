# ADR-008: Document Formatting Engine Selection

## Status

Accepted

## Context

Wave 6 requires producing formatted documents from approved proposal content. The DISCUSS wave established that formatting must be template-based (not LLM layout control). Solicitations require specific fonts, margins, headers, page limits, and volume structures. Output mediums needed: Microsoft Word (.docx) and PDF. LaTeX is optional for technically dense proposals.

Constraints: solo developer, local execution only, OSS preferred, Python 3.12+, no cloud services.

## Decision

**python-docx** (MIT license) as the primary formatting engine for Word output. **WeasyPrint** (BSD license) for PDF generation from HTML/CSS templates. LaTeX output deferred to future phase -- low demand, high complexity.

Format rules are data-driven: JSON template files per agency in `templates/format-rules/`. The DocumentAssemblyPort abstracts the output medium; adapters implement per format.

## Alternatives Considered

### Alternative 1: Jinja2 + LaTeX pipeline
- **What**: Jinja2 templates producing LaTeX source, compiled to PDF via pdflatex
- **Expected impact**: High-fidelity PDF output with precise layout control
- **Why rejected**: Requires LaTeX installation on user machine (200+ MB). Solo developer does not use LaTeX regularly. Installation friction violates zero-setup principle. Phil's primary output medium is Word, not PDF.

### Alternative 2: python-docx only (no PDF)
- **What**: Generate Word only; Phil exports to PDF manually from Word
- **Expected impact**: Covers 90% of use cases (Phil submits .docx or manually exports)
- **Why rejected**: Some portals require PDF upload. Manual export adds a step and risks formatting drift. WeasyPrint adds PDF capability at minimal cost.

### Alternative 3: LibreOffice headless conversion
- **What**: Generate .docx via python-docx, convert to PDF via LibreOffice CLI
- **Expected impact**: Exact Word-to-PDF fidelity
- **Why rejected**: Requires LibreOffice installation. Conversion fidelity is inconsistent across versions. Adds external dependency to a plugin that should be self-contained.

## Consequences

- **Positive**: python-docx is mature (MIT, 4k+ GitHub stars, active maintenance), lightweight, pure Python. Both are pip-installable.
- **Positive**: Template-driven approach means new agencies added by creating a JSON file, not changing code.
- **Negative**: python-docx has limited orphan/widow control. This is acknowledged in the user story (NFR-004: 90% automated, 10% flagged for manual adjustment).
- **Negative**: WeasyPrint PDF output may not match Word layout pixel-for-pixel. Acceptable because portals accept either format.
- **Negative**: WeasyPrint requires cairo system library. Graceful degradation: if cairo not installed, PDF output is unavailable and plugin reports the dependency with installation instructions. Word output (python-docx) always works.
- **Trade-off**: LaTeX deferred. If Phil needs LaTeX output in future, a LatexAdapter can be added behind the same DocumentAssemblyPort.
