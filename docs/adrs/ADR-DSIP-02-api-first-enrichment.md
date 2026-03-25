# ADR-DSIP-02: API-First Enrichment Strategy

## Status
Proposed

## Context
The current enrichment adapter downloads per-topic PDFs and parses them with pypdf for descriptions, instructions, and Q&A. The DSIP API provides structured JSON endpoints (`/details`, `/questions`) that return richer data (technology_areas, focus_areas, itar, keywords as structured fields) and a separate instruction PDF download endpoint. PDF parsing is lossy (loses HTML structure, misses structured fields) and cannot extract Q&A at all.

Quality attributes: Correctness (structured data > lossy PDF parsing), Maintainability (JSON parsing more robust than PDF section detection).

## Decision
Shift enrichment to API-first: use `/details` for descriptions and structured fields, `/questions` for Q&A, and instruction PDF download for solicitation/component instructions. Remove per-topic PDF download as the primary enrichment mechanism. Keep pypdf only for instruction PDF text extraction.

## Alternatives Considered

### Alternative A: Supplement PDF with API calls (keep PDF as primary, add Q&A from API)
- Pro: Minimal change to existing code
- Con: PDF parsing remains lossy for descriptions. Two code paths for description extraction. Instructions still from PDF section parsing (unreliable).
- Rejected: The `/details` endpoint returns strictly more data than the PDF. Keeping PDF parsing adds maintenance burden for inferior results.

### Alternative B: Cache API responses as JSON files instead of parsing on each call
- Pro: Offline access to enrichment data
- Con: Cache invalidation complexity. Topics are time-bound (solicitation cycles). Over-engineering for the problem size.
- Rejected: The existing `JsonTopicCacheAdapter` already caches combined results. Adding a second caching layer is unnecessary.

## Consequences
- **Positive**: Structured fields (technology_areas, itar, keywords) available for scoring. Q&A accessible for first time. HTML preserved in descriptions. Instruction PDFs downloaded separately with cycle+component caching.
- **Negative**: Per-topic PDF download method (`_download_pdf`, `_extract_from_pdf`, `_parse_sections`, `_parse_qa`) becomes dead code and should be removed. Existing tests that mock PDF responses must be rewritten for JSON API mocks.
- **Risk**: If `/details` or `/questions` endpoints become unavailable, enrichment degrades. Mitigated by per-endpoint failure isolation (same pattern as existing per-topic isolation).
