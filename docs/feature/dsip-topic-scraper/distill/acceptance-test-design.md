# Acceptance Test Design: DSIP Topic Scraper

Feature: `dsip-topic-scraper`
Wave: DISTILL
Date: 2026-03-19

---

## Driving Ports (Test Entry Points)

All acceptance tests invoke through these driving ports exclusively:

| Driving Port | Role | Location |
|---|---|---|
| `FinderService` | Application orchestrator for fetch, pre-filter, cache, enrich, persist | `scripts/pes/domain/finder_service.py` |
| `TopicEnrichmentPort` | Enrichment abstraction (NEW -- to be created in DELIVER step 01-01) | `scripts/pes/ports/topic_enrichment_port.py` |
| `TopicCachePort` | Cache abstraction (NEW -- to be created in DELIVER step 01-02) | `scripts/pes/ports/topic_cache_port.py` |
| `TopicFetchPort` | Topic source abstraction (existing) | `scripts/pes/ports/topic_fetch_port.py` |

## Driven Port Fakes (Test Doubles)

| Fake | Replaces | Behavior |
|---|---|---|
| `InMemoryTopicFetchAdapter` | `DsipApiAdapter` | Configurable topics, pagination, rate limiting, structural changes |
| `InMemoryTopicEnrichmentAdapter` | `DsipEnrichmentAdapter` (NEW) | Configurable enrichment data, per-topic failures, timeouts |
| `InMemoryTopicCacheAdapter` | `JsonTopicCacheAdapter` (NEW) | In-memory TTL cache with configurable corruption |

All fakes are in `tests/acceptance/dsip_topic_scraper/fakes.py`.

## Test Organization

```
tests/acceptance/dsip_topic_scraper/
  __init__.py
  conftest.py                       # Fixtures: profiles, topics, cache data, scored results
  fakes.py                          # In-memory fake adapters
  walking-skeleton.feature          # 3 walking skeletons (user-centric E2E)
  milestone-01-enrichment.feature   # 9 enrichment scenarios (US-DSIP-002)
  milestone-01-cache.feature        # 8 cache scenarios (US-DSIP-003)
  milestone-02-pipeline.feature     # 7 pipeline integration scenarios (US-DSIP-001, US-DSIP-003)
  milestone-02-resilience.feature   # 8 resilience scenarios (US-DSIP-004)
  steps/
    __init__.py
    conftest.py                     # Imports common steps
    scraper_common_steps.py         # Shared steps: system availability, profile, messages
    enrichment_steps.py             # Steps for enrichment + walking skeleton scenarios
    cache_steps.py                  # Steps for cache scenarios
    pipeline_steps.py               # Steps for pipeline integration scenarios
    resilience_steps.py             # Steps for resilience scenarios
```

## Scenario Counts

| Category | Count |
|---|---|
| Walking skeletons | 3 |
| Happy path | 12 |
| Error path | 13 |
| Edge case | 7 |
| **Total** | **35** |
| Error path ratio | 37% (13/35) |

Note: Including the 1 `@property`-tagged scenario, the ratio is 40% (14/35).

## Walking Skeleton Identification

1. **Proposal writer discovers and enriches DSIP topics for evaluation** -- Fetch -> filter -> enrich -> completeness report -> cache. Answers: "Can Phil get enriched topic data from DSIP without manual browsing?"
2. **Proposal writer sees scored and ranked DSIP topics with enriched descriptions** -- Score -> rank -> display table. Answers: "Can Phil see which topics to pursue based on enriched scoring?"
3. **Proposal writer reuses cached DSIP data without re-scraping** -- Cache check -> reuse -> scoring. Answers: "Can Phil re-run scoring without waiting for another full scrape?"

## Story-to-Scenario Traceability

| Story | Scenarios | Feature Files |
|---|---|---|
| US-DSIP-001 | 4 | pipeline.feature |
| US-DSIP-002 | 9 | enrichment.feature |
| US-DSIP-003 | 11 | cache.feature, pipeline.feature |
| US-DSIP-004 | 8 | resilience.feature |
| Cross-story | 3 | walking-skeleton.feature |

## Implementation Sequence (One at a Time)

The software-crafter should enable and implement in this order:

### Phase 01: Enrichment Infrastructure
1. `test_enrich_topic_with_full_description_instructions_and_qa` (walking skeleton 1 simplified)
2. `test_handle_topic_with_no_qa_entries_gracefully`
3. `test_continue_enrichment_after_individual_topic_extraction_failure`
4. `test_enrich_batch_of_candidate_topics_with_progress_indication`
5. `test_handle_topic_detail_download_failure_without_stopping_batch`
6. `test_enrichment_times_out_for_a_slow_topic_without_blocking_others`
7. `test_report_enrichment_completeness_metrics_after_batch_enrichment`
8. `test_capture_componentspecific_instructions_when_available`
9. `test_cache_enriched_topic_data_after_enrichment_completes`
10. `test_cache_recognized_as_fresh_within_the_ttl_window`
11. `test_cache_recognized_as_stale_after_ttl_window_expires`
12. `test_cache_write_uses_atomic_tempbackuprename_pattern`
13. `test_missing_cache_file_triggers_fresh_fetch_without_error`
14. `test_corrupt_cache_file_triggers_fresh_fetch_with_warning`
15. `test_cache_invalidated_when_search_filters_differ_from_cached_filters`
16. `test_rescore_cached_data_after_company_profile_update`

### Phase 02: Pipeline Integration
17. `test_endtoend_scrape_to_scored_and_ranked_results`
18. `test_paginated_fetch_collects_all_topics_across_multiple_pages`
19. `test_use_cached_enriched_data_for_immediate_scoring`
20. `test_topics_with_missing_required_fields_reported_without_blocking_valid_topics`
21. `test_unreachable_topic_source_produces_actionable_guidance`
22. `test_partial_fetch_results_are_enriched_and_scored_when_available`
23. `test_pursue_a_dsipsourced_topic_and_transition_to_proposal_creation`
24. `test_progress_reported_during_each_phase_of_the_scraping_pipeline`
25. `test_automatic_retry_succeeds_after_transient_failure`
26. `test_retry_uses_exponential_backoff_between_attempts`
27. `test_connection_timeout_is_configurable_with_sensible_default`
28. `test_structural_change_in_topic_source_response_detected_and_reported`
29. `test_all_retries_exhausted_produces_clear_failure_message`
30. `test_rate_limiting_signal_from_topic_source_is_respected`
31. `test_error_messages_always_follow_the_whatwhydo_pattern`

### Walking Skeletons (after infrastructure)
32. `test_proposal_writer_discovers_and_enriches_dsip_topics_for_evaluation`
33. `test_proposal_writer_sees_scored_and_ranked_dsip_topics_with_enriched_descriptions`
34. `test_proposal_writer_reuses_cached_dsip_data_without_rescraping`

## Mandate Compliance Evidence

### CM-A: Hexagonal Boundary Enforcement

All step definition files import through driving ports:
- `enrichment_steps.py`: imports `InMemoryTopicEnrichmentAdapter` (fake for `TopicEnrichmentPort`)
- `cache_steps.py`: imports `InMemoryTopicCacheAdapter` (fake for `TopicCachePort`)
- `pipeline_steps.py`: imports `FinderService` (driving port), `InMemoryTopicFetchAdapter` (fake)
- `resilience_steps.py`: imports `InMemoryTopicFetchAdapter` (fake for `TopicFetchPort`)

Zero internal component imports (no direct `DsipApiAdapter`, `DsipEnrichmentAdapter`, `JsonTopicCacheAdapter`, `httpx`, or `pypdf` imports).

### CM-B: Business Language Purity

Gherkin contains zero technical terms. All scenarios use business language:
- "topic source" not "DSIP API endpoint"
- "enrichment service" not "PDF download adapter"
- "cache" not "JSON file persistence"
- "scrape date" not "ISO-8601 timestamp"
- "detail document" not "PDF"

### CM-C: Walking Skeleton + Focused Scenario Counts

- Walking skeletons: 3 (user-centric E2E value)
- Focused scenarios: 31 (boundary tests with test doubles)
- Ratio: 3:31 (within recommended 2-5 skeletons per feature)
