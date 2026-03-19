# Test Scenarios: DSIP Topic Scraper

Feature: `dsip-topic-scraper`
Wave: DISTILL
Date: 2026-03-19
Scenarios: 35 (3 walking skeletons + 32 focused)

---

## Walking Skeletons

### WS-1: Proposal writer discovers and enriches DSIP topics for evaluation
- **Story**: Cross-story (US-DSIP-001, US-DSIP-002, US-DSIP-003)
- **User goal**: Fetch, filter, enrich, and cache DSIP topics in one workflow
- **Observable outcome**: Candidate topics with descriptions, completeness report, cached data

### WS-2: Proposal writer sees scored and ranked DSIP topics with enriched descriptions
- **Story**: Cross-story (US-DSIP-001, US-DSIP-002, US-DSIP-003)
- **User goal**: View ranked recommendations based on enriched topic data
- **Observable outcome**: Ranked table with GO/EVALUATE/NO-GO, completeness metrics

### WS-3: Proposal writer reuses cached DSIP data without re-scraping
- **Story**: US-DSIP-003
- **User goal**: Re-score topics without waiting for full re-scrape
- **Observable outcome**: Immediate scoring from cache, no new source requests

---

## US-DSIP-001: Fetch All DSIP Topics via API

| # | Scenario | Type | File |
|---|---|---|---|
| 1 | End-to-end scrape to scored and ranked results | Happy | pipeline |
| 2 | Paginated fetch collects all topics | Happy | pipeline |
| 3 | Unreachable topic source produces actionable guidance | Error | pipeline |
| 4 | Partial fetch results enriched and scored | Error | pipeline |

## US-DSIP-002: Enrich Topics with Descriptions, Instructions, and Q&A

| # | Scenario | Type | File |
|---|---|---|---|
| 5 | Enrich topic with full description, instructions, and Q&A | Happy | enrichment |
| 6 | Enrich batch with progress indication | Happy | enrichment |
| 7 | Report enrichment completeness metrics | Happy | enrichment |
| 8 | Handle topic with no Q&A entries | Edge | enrichment |
| 9 | Capture component-specific instructions | Edge | enrichment |
| 10 | Continue enrichment after extraction failure | Error | enrichment |
| 11 | Handle topic detail download failure | Error | enrichment |
| 12 | Enrichment times out without blocking others | Error | enrichment |

## US-DSIP-003: Integrate Scraped Data into Scoring Pipeline

| # | Scenario | Type | File |
|---|---|---|---|
| 13 | Use cached enriched data for immediate scoring | Happy | pipeline |
| 14 | Pursue DSIP-sourced topic for proposal creation | Happy | pipeline |
| 15 | Cache enriched topic data after enrichment | Happy | cache |
| 16 | Cache recognized as fresh within TTL | Happy | cache |
| 17 | Re-score cached data after profile update | Happy | cache |
| 18 | Topics with missing required fields reported | Error | pipeline |
| 19 | Cache recognized as stale after TTL expires | Edge | cache |
| 20 | Cache invalidated on filter change | Edge | cache |
| 21 | Atomic cache write pattern | Edge | cache |
| 22 | Missing cache file triggers fresh fetch | Error | cache |
| 23 | Corrupt cache file triggers fresh fetch | Error | cache |

## US-DSIP-004: Scraper Resilience and Observability

| # | Scenario | Type | File |
|---|---|---|---|
| 24 | Progress reported during each pipeline phase | Happy | resilience |
| 25 | Automatic retry succeeds after transient failure | Happy | resilience |
| 26 | Retry uses exponential backoff | Edge | resilience |
| 27 | Configurable connection timeout | Edge | resilience |
| 28 | Structural change detected and reported | Error | resilience |
| 29 | All retries exhausted produces clear failure | Error | resilience |
| 30 | Rate limiting signal respected | Error | resilience |
| 31 | Error messages follow what-why-do pattern | @property | resilience |

---

## Error Path Ratio

- Happy path: 12 scenarios
- Error path: 13 scenarios
- Edge case: 7 scenarios
- Property: 1 scenario (tagged @property)
- **Error path ratio**: 37% (13/35), or 40% including @property (14/35)

## Property-Shaped Scenarios

| Tag | Scenario | Signal |
|---|---|---|
| @property | Error messages always follow the what-why-do pattern | "always" -- universal invariant |

The `@property` tag signals the DELIVER wave crafter to implement as a property-based test with generators rather than single-example assertions.
