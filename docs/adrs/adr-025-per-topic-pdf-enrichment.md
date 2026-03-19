# ADR-025: Per-Topic PDF Download for Enrichment

## Status

Proposed

## Context

The DSIP API search endpoint (`/topics/api/public/topics/search`) returns topic metadata only: topic ID, title, status, component, dates. Meaningful scoring (US-DSIP-002) requires full descriptions, submission instructions, component instructions, and Q&A. The user currently spends 3-5 minutes per topic clicking through the portal to read these details.

Three enrichment approaches exist:

1. The DSIP API exposes per-topic PDF download at `/topics/api/public/topics/{hash_id}/download/PDF` (confirmed via network inspection, ADR-016).
2. The Angular SPA renders topic details via DOM expansion (used by the prototype `python_topic_scraper/scrape_dsip.py`).
3. BAA PDFs contain all topics for a solicitation cycle but with agency-specific formatting.

Constraints: no Playwright/headless browser dependency desired (ADR-016 chose API-first to avoid it), must work on Windows and in Docker, must handle 20-50 topics per enrichment run.

## Decision

Use the per-topic PDF download endpoint (`GET /topics/api/public/topics/{hash_id}/download/PDF`) for enrichment. Extract description text from the PDF using pypdf (BSD-3-Clause). Parse the extracted text for description sections, submission instructions, component instructions, and Q&A blocks.

Rate-limit enrichment requests (configurable delay, default 1-2 seconds between requests). Report progress per topic. Log and skip failures per topic without stopping the batch.

Q&A data may not be present in the PDF. If the DSIP API exposes a separate Q&A endpoint, the adapter should use it. Otherwise, Q&A is extracted from PDF content on a best-effort basis.

## Alternatives Considered

### Alternative 1: DOM scraping via Playwright

- **Evaluation**: The prototype uses Playwright to expand topic rows and extract text from the rendered DOM. Captures descriptions and Q&A.
- **Rejection**: Adds ~200MB Playwright + Chromium dependency. Fragile against Angular template changes. Slow (2-3 second waits per topic for rendering). ADR-016 explicitly chose API-first to avoid headless browser dependency. The API provides the same data via PDF download without DOM rendering.

### Alternative 2: BAA PDF parsing (solicitation-level document)

- **Evaluation**: A single PDF per solicitation cycle contains all topics. Parse once, extract all topics.
- **Rejection**: BAA format varies significantly by agency. Already implemented as fallback (`BaaPdfAdapter`). Does not provide Q&A or component-specific instructions. Good fallback but insufficient as primary enrichment source.

### Alternative 3: No enrichment (title-only scoring)

- **Evaluation**: Skip enrichment entirely. Score topics on title + metadata from the search API.
- **Rejection**: Titles are insufficient for go/no-go decisions. "Compact Directed Energy for C-UAS" does not reveal TRL expectations, teaming requirements, or phase deliverables. This is the core user pain point that US-DSIP-002 addresses.

## Consequences

### Positive

- No Playwright/Chromium dependency (stays API-only, consistent with ADR-016)
- pypdf is lightweight, pure Python, BSD-3-Clause, well-maintained (8K+ GitHub stars)
- Per-topic PDF download provides structured content (description, phase expectations, references)
- Rate limiting and per-topic isolation make the enrichment resilient
- Pre-filter before enrichment limits requests to 20-50 topics (not 300-500)

### Negative

- One HTTP request per candidate topic (20-50 requests, 30-100 seconds with rate limiting)
- PDF text extraction quality depends on PDF structure (some topics may have unusual formatting)
- Q&A may not be available in PDFs (best-effort extraction)
- pypdf is a new dependency (mitigated: pure Python, no native extensions, BSD-3-Clause)
