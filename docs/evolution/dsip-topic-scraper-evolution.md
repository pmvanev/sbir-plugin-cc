# Feature Evolution: dsip-topic-scraper

## Summary

Integrated DSIP topic scraping into the SBIR proposal plugin's solicitation discovery pipeline. Topics are fetched via the DSIP public API, pre-filtered by company capabilities, enriched with per-topic PDF content (descriptions, instructions, Q&A), cached with TTL, and scored for fit.

## Key Decisions

- **No Playwright dependency**: The prototype's DOM scraping approach was fully superseded by API-first fetching + per-topic PDF download. Eliminated ~200MB Playwright+Chromium dependency.
- **Pre-filter before enrich**: Fetch 300-500 topics cheaply via API, keyword pre-filter to 20-50 candidates, then enrich only candidates. Keeps enrichment latency under 2 minutes.
- **Cache at enrichment layer**: Cached data is enriched but unscored, allowing re-scoring against updated profiles without re-downloading.
- **Graceful degradation**: Partial enrichment failures produce usable results with completeness metrics.

## Components Delivered

### New (5 files)
| Component | File | Purpose |
|-----------|------|---------|
| TopicEnrichmentPort | `scripts/pes/ports/topic_enrichment_port.py` | Driven port for per-topic detail fetching |
| DsipEnrichmentAdapter | `scripts/pes/adapters/dsip_enrichment_adapter.py` | Downloads topic PDFs, extracts text via pypdf, retry with backoff |
| TopicCachePort | `scripts/pes/ports/topic_cache_port.py` | Driven port for topic data caching with TTL |
| JsonTopicCacheAdapter | `scripts/pes/adapters/json_topic_cache_adapter.py` | Atomic file-based cache at .sbir/dsip_topics.json |
| topic_enrichment | `scripts/pes/domain/topic_enrichment.py` | Pure domain: combine topics with enrichment data, completeness reports |

### Modified (2 files)
| Component | File | Change |
|-----------|------|--------|
| FinderService | `scripts/pes/domain/finder_service.py` | Added search_and_enrich() orchestration method |
| Topic Scout Agent | `agents/sbir-topic-scout.md` | Updated INGEST phase with cache check + enrichment workflow |

### New Skill
| Skill | File | Purpose |
|-------|------|---------|
| DSIP Enrichment | `skills/topic-scout/dsip-enrichment.md` | Topic detail structure knowledge for the scout agent |

## ADRs
- ADR-025: Per-Topic PDF Download for Enrichment
- ADR-026: File-Based Topic Cache with TTL

## Quality Gates

| Gate | Result |
|------|--------|
| TDD (5-phase) | All 5 steps COMMIT/PASS |
| L1-L4 Refactoring | 4 files improved |
| Adversarial Review | REJECTED → fixed D1-D5 → passed |
| Mutation Testing | topic_enrichment.py: 100% kill rate |
| DES Integrity | All 5 steps verified |

## Delivery Timeline

| Phase | Steps | Commits |
|-------|-------|---------|
| 01 Enrichment Infrastructure | 01-01, 01-02 | 2 commits |
| 02 Pipeline Integration | 02-01, 02-02 | 2 commits |
| 03 Agent & Skill | 03-01 | 1 commit |
| Refactoring | L1-L4 pass | 1 commit |
| Review Fix | D1-D5 blockers | 1 commit |
| Mutation Tests | topic_enrichment.py coverage | 1 commit |

## Observations

- Parallel step execution (01-01 and 01-02) worked well — no conflicts since they touched different files.
- Parallel step execution (02-01 and 02-02) required careful resumption — both modified finder_service.py.
- Adversarial review caught a real type contract violation (CacheResult vs dict) that would have failed in production.
- Mutation testing in Docker requires sequential runs — parallel containers share the volume mount and corrupt each other's mutated files.
