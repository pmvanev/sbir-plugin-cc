# ADR-026: File-Based Topic Cache with TTL

## Status

Proposed

## Context

The solicitation finder pipeline (fetch -> pre-filter -> enrich -> score) takes 1-3 minutes due to API calls and per-topic enrichment. Users may run `/solicitation find` multiple times per day (refining filters, re-scoring after profile updates, pursuing topics). Repeating the full pipeline each time wastes time and DSIP API bandwidth.

US-DSIP-003 requires: "Cached data can be reused within a configurable TTL to avoid unnecessary re-scraping."

The existing project uses JSON files for all state persistence (ADR-004). The atomic write pattern (temp + backup + rename) is established in `JsonFinderResultsAdapter`.

## Decision

Cache enriched topic data to `.sbir/dsip_topics.json` with a TTL (time-to-live) freshness check. Default TTL: 24 hours. Configurable per invocation.

Cache schema:
```json
{
  "scrape_date": "ISO-8601",
  "source": "dsip_api",
  "ttl_hours": 24,
  "total_topics": 247,
  "filters_applied": {"agency": "Air Force"},
  "enrichment_completeness": {
    "descriptions": 41,
    "instructions": 38,
    "qa": 29,
    "total": 42
  },
  "topics": [...]
}
```

When `/solicitation find` is invoked:
1. Check cache freshness: `scrape_date + ttl_hours > now`
2. If fresh: offer user choice (use cache or re-scrape)
3. If stale or absent: proceed with full pipeline, write results to cache

Cache is written after enrichment (step 5 in pipeline), not after scoring. This separates the expensive data-gathering from the fast scoring, allowing re-scoring on cached data without re-enrichment.

## Alternatives Considered

### Alternative 1: No cache (always re-fetch)

- **Evaluation**: Simplest. Every invocation runs the full pipeline.
- **Rejection**: 1-3 minutes per run is acceptable once but frustrating when refining filters or re-scoring. DSIP rate limiting risk increases with repeated full fetches. The user story explicitly requires cache reuse.

### Alternative 2: SQLite cache

- **Evaluation**: Structured storage with query support. Could enable partial cache updates and filter-specific caching.
- **Rejection**: Adds SQLite dependency. Inconsistent with project convention (all state is JSON files, ADR-004). Over-engineering for a cache that stores 50-500 topic records. JSON file with atomic writes is sufficient.

### Alternative 3: Cache after scoring (not after enrichment)

- **Evaluation**: Cache the fully scored results, not just enriched topics.
- **Rejection**: Scoring depends on the company profile, which may change between runs. Caching scored results would serve stale scores after profile updates. Caching enriched (pre-scored) data allows re-scoring against an updated profile without re-enrichment.

## Consequences

### Positive

- Eliminates redundant API calls within the TTL window
- Re-scoring against updated profile is instant (cached enriched data, fresh scoring)
- Human-readable JSON cache file (inspectable, debuggable)
- Consistent with existing project patterns (JSON files, atomic writes)
- Cache invalidation is simple: delete `.sbir/dsip_topics.json` or wait for TTL expiry

### Negative

- Cache may serve stale topic data if DSIP updates topics within the TTL window (mitigated: user can force re-scrape)
- Filter mismatch: cache from `--agency "Air Force"` is invalid for `--agency "Navy"` (mitigated: store `filters_applied` in cache, invalidate on filter change)
- Cache file size: 50-500 topics with enriched descriptions = 500KB-5MB (acceptable for local disk)
