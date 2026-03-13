# ADR-016: DSIP Public API as Primary Data Source

## Status

Accepted

## Context

The solicitation finder needs to retrieve open SBIR/STTR topics for batch scoring. The primary user pain point is manually browsing 300-500 topics on dodsbirsttr.mil per solicitation cycle (2-6 hours).

Three data access approaches were evaluated during the DISCOVER wave (solution-testing.md, 2026-03-13):

1. The DoD SBIR/STTR Innovation Portal (DSIP) at dodsbirsttr.mil exposes a public, unauthenticated JSON API that the Angular frontend uses.
2. BAA (Broad Agency Announcement) PDFs are published documents containing all topics for a solicitation cycle.
3. Users can manually download individual topic files.

Constraints: no authentication available, no API key, must work offline as fallback, agency format variation across BAAs.

## Decision

Use the DSIP public API (`GET /topics/api/public/topics/search`) as the primary data source for topic listings. Use BAA PDF extraction as an automatic fallback when the API is unavailable.

**API details** (confirmed 2026-03-13):
- Listing: `GET /topics/api/public/topics/search` -- JSON, paginated, 32,640+ topics in database
- Topic detail: `GET /topics/api/public/topics/{hash_id}/download/PDF` -- individual topic as PDF
- Query params: `topicStatus`, `numPerPage`, `baa`
- Authentication: None required

**Fallback trigger**: Connection timeout, HTTP 5xx, or rate limiting after retries. User sees clear message and `--file` flag suggestion.

## Alternatives Considered

### Alternative 1: BAA PDF only (user always provides file)

- **Evaluation**: Eliminates the automated discovery value. User must still manually find and download the BAA. Covers scoring but not fetching. Format varies by agency -- parsing is fragile without LLM.
- **Rejection**: The core value proposition is automating discovery. Confirmed API access makes this unnecessarily manual.

### Alternative 2: Web scraping the Topics App HTML

- **Evaluation**: The Topics App is an Angular SPA with client-side rendering. Scraping would require a headless browser (Playwright/Puppeteer), adding heavy dependencies and fragility.
- **Rejection**: The app's own backend API is public and returns structured JSON. Scraping the frontend is strictly worse -- more complex, more fragile, same data.

### Alternative 3: SBIR.gov API

- **Evaluation**: SBIR.gov has a separate API but with different schema, incomplete DoD coverage, and less timely updates than DSIP.
- **Rejection**: DSIP is the authoritative DoD source. SBIR.gov could be added as a supplementary source in v2 for non-DoD agencies.

## Consequences

### Positive

- Zero-cost access to all DoD SBIR/STTR topics (32,640+ historical, ~300-500 per cycle)
- Structured JSON eliminates parsing fragility
- Pagination and filtering supported server-side
- BAA PDF fallback provides resilience against API changes or downtime

### Negative

- Undocumented API: no SLA, no versioning guarantee, could change without notice
- Topic listings contain metadata only -- full descriptions require individual PDF downloads
- Rate limiting behavior is undocumented (mitigated by 1-2 second delays between requests)
- Single-source dependency on DSIP for DoD topics (mitigated by BAA fallback)
