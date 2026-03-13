# Evolution: Solicitation Finder

**Date**: 2026-03-13
**Feature**: solicitation-finder
**Waves Completed**: DISCOVER > DISCUSS > DESIGN > DISTILL > DELIVER

## Summary

Implemented the Solicitation Finder feature: an automated tool that fetches SBIR/STTR topics from the DSIP public API, pre-filters by company profile capabilities, scores candidates using a five-dimension fit model, and presents ranked results with GO/EVALUATE/NO-GO recommendations.

## Key Decisions

- **DSIP API as primary data source** (ADR-016): Unauthenticated JSON API at dodsbirsttr.mil/topics/api/public/topics/search provides 32,000+ topics. BAA PDF fallback for offline use.
- **Two-pass matching** (ADR-017): Fast keyword pre-filter in Python reduces candidates before expensive LLM scoring.
- **httpx for HTTP client** (ADR-018): Async-ready, modern HTTP/2 support, better timeout/retry control than requests.
- **Five-dimension scoring**: SME (0.35), Past Performance (0.25), Certifications (0.15), Eligibility (0.15), STTR (0.10).

## Components Delivered

### Domain Services (scripts/pes/domain/)
- `keyword_prefilter.py` — Pure domain logic for topic-capability matching
- `finder_service.py` — Application orchestrator: fetch → pre-filter → persist
- `topic_scoring.py` — Five-dimension fit scoring with disqualifier detection
- `topic_pursue_service.py` — Topic pursuit validation and proposal handoff

### Ports (scripts/pes/ports/)
- `topic_fetch_port.py` — TopicFetchPort ABC with FetchResult dataclass
- `finder_results_port.py` — FinderResultsPort ABC for results persistence

### Adapters (scripts/pes/adapters/)
- `dsip_api_adapter.py` — DSIP API adapter with pagination, retry, rate limiting
- `baa_pdf_adapter.py` — BAA PDF fallback adapter
- `json_finder_results_adapter.py` — Atomic JSON file adapter (.tmp → .bak → rename)

### Agent/Command/Skill
- `agents/sbir-topic-scout.md` — Extended with batch scoring workflow
- `commands/sbir-solicitation-find.md` — `/sbir:solicitation find` command
- `skills/topic-scout/finder-batch-scoring.md` — Batch scoring skill

## Test Coverage

| Category | Count |
|----------|-------|
| Acceptance tests | 27 passed, 3 skipped (walking skeletons) |
| Unit tests (original) | 22 |
| Unit tests (mutation-killing) | 152 |
| **Total** | **204 passed, 3 skipped** |

## Mutation Testing Results

| File | Total | Killed | Kill Rate |
|------|-------|--------|-----------|
| keyword_prefilter.py | 33 | 30 | 90.9% |
| topic_pursue_service.py | 32 | 28 | 87.5% |
| finder_service.py | 115 | 100 | 87.0% |
| topic_scoring.py | 291 | 235 | 80.8% |
| **Total** | **471** | **393** | **83.4%** |

All files exceed the 80% kill rate gate.

## Bug Fixed During Mutation Testing

- `topic_scoring.py:272` — `best_score = None` was a bug introduced during initial implementation. Should be `best_score = max(best_score, score)`. Would cause TypeError when different-agency strong-domain-overlap past performance was encountered. Fixed and verified by targeted tests.

## Roadmap Steps (7 steps, 3 phases)

1. **01-01**: Topic fetch port and DSIP API adapter
2. **01-02**: Keyword pre-filter and profile integration
3. **01-03**: Finder results port and JSON adapter
4. **01-04**: BAA PDF fallback adapter and profile-missing handling
5. **02-01**: Finder orchestration service
6. **02-02**: Agent batch scoring and results display
7. **03-01**: Solicitation find command and topic selection flow
