# Definition of Ready Validation: DSIP Topic Scraper

## US-DSIP-001: Fetch All DSIP Topics via API

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | Phil spends 1-2 hours browsing DSIP portal manually; Angular SPA is slow and paginated |
| User/persona identified | PASS | Phil Santos, small business engineer, 2-3 proposals/year, starting new proposal cycle |
| 3+ domain examples | PASS | 4 examples: happy path (42 AF topics), pagination (247 topics), portal unreachable, API format change |
| UAT scenarios (3-7) | PASS | 4 scenarios: fetch all, pagination, unreachable, format validation |
| AC derived from UAT | PASS | 6 AC items, each traceable to a scenario |
| Right-sized | PASS | ~2 days effort, 4 scenarios, single demonstrable outcome (topics fetched and cached) |
| Technical notes | PASS | API endpoint, status IDs, pagination params, Playwright dependency, platform constraints |
| Dependencies tracked | PASS | TopicInfo schema (existing), company-profile.json (optional), Playwright/Chromium |

### DoR Status: PASSED

---

## US-DSIP-002: Enrich Topics with Descriptions, Instructions, and Q&A

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | 3-5 minutes per topic to click into detail page; 20+ topics = over an hour |
| User/persona identified | PASS | Phil Santos, evaluating multiple topics for fit, wants complete detail |
| 3+ domain examples | PASS | 3 examples: full enrichment (AF263-042 with 1847 chars, 3 Q&A), no Q&A (MDA263-009), extraction failure (N261-099) |
| UAT scenarios (3-7) | PASS | 5 scenarios: full enrichment, no Q&A, failure recovery, completeness metrics, progress indication |
| AC derived from UAT | PASS | 8 AC items covering descriptions, instructions, Q&A, error handling, completeness, progress |
| Right-sized | PASS | ~2-3 days effort, 5 scenarios, single demonstrable outcome (enriched topic data) |
| Technical notes | PASS | DOM traversal vs API, rate limiting, HTML normalization, dependency on US-DSIP-001 |
| Dependencies tracked | PASS | US-DSIP-001 (fetch), Playwright/Chromium, DSIP DOM structure |

### DoR Status: PASSED

---

## US-DSIP-003: Integrate Scraped DSIP Data into Scoring Pipeline

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | Scraped data disconnected from scoring workflow; topic-scout expects BAA PDF, not JSON |
| User/persona identified | PASS | Phil Santos, has scraped data, wants seamless pipeline to ranked results |
| 3+ domain examples | PASS | 3 examples: end-to-end scrape-to-score (12 topics scored), cached data reuse, missing field handling |
| UAT scenarios (3-7) | PASS | 4 scenarios: end-to-end, pursue flow, cache reuse, missing fields |
| AC derived from UAT | PASS | 7 AC items covering transformation, pre-filtering, display, persistence, pursue, cache, error handling |
| Right-sized | PASS | ~2 days effort, 4 scenarios, single demonstrable outcome (scored DSIP topics in ranked table) |
| Technical notes | PASS | Field mapping (DSIP -> TopicInfo), status mapping, cache TTL, existing service dependencies |
| Dependencies tracked | PASS | US-DSIP-001, US-DSIP-002, TopicScoringService (existing), FitScoring (existing), finder-results.json schema |

### DoR Status: PASSED

---

## US-DSIP-004: Scraper Resilience and Observability

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | Scraper breaks silently; no retry, no timeout handling, no progress during long operations |
| User/persona identified | PASS | Phil Santos, running scraper regularly, needs confidence in complete success or clear failure |
| 3+ domain examples | PASS | 3 examples: progress during 2-minute scrape, transient 503 with retry, structural change detected |
| UAT scenarios (3-7) | PASS | 4 scenarios: progress reporting, automatic retry, configurable timeout, diagnostic save |
| AC derived from UAT | PASS | 6 AC items covering progress, silence limit, retry, timeout, structural detection, error messages |
| Right-sized | PASS | ~2 days effort, 4 scenarios, single demonstrable outcome (resilient scraper with observability) |
| Technical notes | PASS | Retry strategy (exponential backoff), timeout hierarchy, diagnostic file, stderr for progress |
| Dependencies tracked | PASS | US-DSIP-001 (fetch infrastructure), US-DSIP-002 (enrichment infrastructure) |

### DoR Status: PASSED

---

## Summary

| Story | DoR Status | Items Passed | Estimated Effort |
|-------|-----------|-------------|-----------------|
| US-DSIP-001 | PASSED | 8/8 | 2 days |
| US-DSIP-002 | PASSED | 8/8 | 2-3 days |
| US-DSIP-003 | PASSED | 8/8 | 2 days |
| US-DSIP-004 | PASSED | 8/8 | 2 days |

All 4 stories pass Definition of Ready. Total estimated effort: 8-9 days.

### Story Dependency Graph

```
US-DSIP-001 (Fetch)
     |
     v
US-DSIP-002 (Enrich) ----+
     |                    |
     v                    v
US-DSIP-003 (Integrate)  US-DSIP-004 (Resilience)
```

US-DSIP-001 is the foundation. US-DSIP-002 depends on it. US-DSIP-003 and US-DSIP-004 can be parallelized after US-DSIP-002.

### MoSCoW Classification

| Story | Priority | Rationale |
|-------|----------|-----------|
| US-DSIP-001 | Must Have | No value without topic fetching |
| US-DSIP-002 | Must Have | Descriptions required for meaningful scoring |
| US-DSIP-003 | Must Have | Integration is the core value proposition |
| US-DSIP-004 | Should Have | Resilience can be added incrementally; initial version works without retry |
