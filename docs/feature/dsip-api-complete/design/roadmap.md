# Roadmap: dsip-api-complete

## Metadata

- **Feature**: dsip-api-complete
- **Steps**: 5
- **Production files**: 6 (2 adapters, 1 port, 1 CLI, 1 domain module, 1 port dataclass update)
- **Markdown files**: 3 (2 skills, 1 agent)
- **Step ratio**: 5/6 = 0.83 (well under 2.5 threshold)
- **Delivery surfaces**: Python TDD (steps 01-04), Markdown forge (step 05)
- **Paradigm**: OOP with ports-and-adapters

## Baseline Measurements

| Metric | Current | Target |
|--------|---------|--------|
| Topics returned for "Open" filter | 32,638 (all history) | ~24 (current cycle only) |
| Data types in enrichment output | 1 of 4 (description from PDF) | 4 of 4 (description, Q&A, solicitation instructions, component instructions) |
| Structured fields available | 0 (title-only from search) | 8+ (keywords, technology_areas, focus_areas, itar, cmmc_level, objective, phase descriptions) |
| Q&A entries retrieved | 0 | All published Q&A per topic |

---

## Phase 01: Search and Port Foundation

### Step 01-01: Fix search query format and normalize new fields

**Description**: Fix DsipApiAdapter to use JSON `searchParam` with `topicReleaseStatus` IDs, `size` pagination. Update `_normalize_topic` to capture hash ID, cycle_name, release_number, component, published_qa_count. Update CLI `_build_filters` to map status names to IDs.

**Acceptance Criteria**:
- Search requests use JSON `searchParam` format with `size` pagination
- Status "Open" maps to `[592]`, "Pre-Release" to `[591]`, no filter to `[591, 592]`
- Normalized topics include cycle_name, release_number, published_qa_count
- Topic IDs are hash format (contain underscore)
- Existing pagination, retry, and rate-limiting behavior preserved

**Architectural Constraints**:
- TopicFetchPort interface unchanged
- Filter interpretation is adapter-internal logic

**Test Fixtures**: `tests/fixtures/dsip_live/raw_api_search_correct_format.json`

---

### Step 01-02: Widen enrichment port signature and update integration points

**Description**: Change `TopicEnrichmentPort.enrich()` from `topic_ids: list[str]` to `topics: list[dict]`. Update `EnrichmentResult.completeness` to track 4 data types. Update FinderService and `combine_topics_with_enrichment` to pass full topic dicts and merge new fields.

**Acceptance Criteria**:
- Enrichment port accepts topic dicts with topic_id, cycle_name, release_number, component, published_qa_count
- Completeness metrics track descriptions, qa, solicitation_instructions, component_instructions separately
- Combined topics include all new enrichment fields
- Completeness report messages include all 4 data types

**Architectural Constraints**:
- ADR-DSIP-01 governs this change
- FinderService passes full candidate dicts to enrich()

---

## Phase 02: Enrichment Data Sources

### Step 02-01: API-first enrichment (details + Q&A + instruction PDFs)

**Description**: Replace PDF-only enrichment with 3 API data sources: `/details` for structured descriptions, `/questions` for Q&A, instruction PDF download with text extraction. Add per-cycle+component instruction caching. Remove dead PDF parsing code.

**Acceptance Criteria**:
- Details endpoint returns description, objective, keywords (list), technology_areas, focus_areas, itar, cmmc_level
- Q&A entries parsed with double-JSON answer format; malformed answers fall back to raw string
- Q&A skipped for topics with published_qa_count == 0
- Instruction PDFs downloaded per cycle+component, text extracted via pypdf, cached within batch
- Per-endpoint failure isolated: one failing data source does not block others for same or different topics
- Enrichment status "partial" when any data source fails for a topic

**Architectural Constraints**:
- ADR-DSIP-02 governs this change
- pypdf retained only for instruction PDF extraction
- All HTTP calls use existing User-Agent header and retry/backoff pattern

**Test Fixtures**: `raw_api_details_response.json`, `raw_api_qa_response.json`, `raw_component_instructions_army.pdf`, `raw_solicitation_instructions.pdf`

---

## Phase 03: CLI Integration

### Step 03-01: CLI output and detail command update

**Description**: Update CLI output to include all new enrichment fields. Update `detail` command to use enrichment adapter with hash ID. Update completeness metrics display for 4 data types.

**Acceptance Criteria**:
- Enriched topic JSON includes: objective, keywords, technology_areas, focus_areas, itar, cmmc_level, qa_entries, qa_count, solicitation_instructions, component_instructions, enrichment_status
- Detail command works with hash ID format
- Completeness metrics show all 4 data type counts
- Existing fetch/enrich/score commands work with updated adapters

**Architectural Constraints**:
- No new CLI flags -- existing interface preserved
- CLI remains a thin wiring layer

---

## Phase 04: Skills and Agent Update

### Step 04-01: Update skills and agent for new data availability

**Description**: Update dsip-cli-usage skill with new fields, hash ID examples, 4 data types. Update dsip-enrichment skill with API-first strategy, new endpoints, updated completeness levels. Update sbir-topic-scout agent for new data in recommendations.

**Acceptance Criteria**:
- dsip-cli-usage shows hash ID format in examples and documents all new output fields
- dsip-enrichment describes API-first strategy with details/Q&A/instructions endpoints
- Topic scout agent references Q&A, technology_areas, itar in recommendation logic
- No stale references to numeric topic IDs or PDF-only enrichment

**Architectural Constraints**:
- Markdown forge validation (not TDD)
- Skills are agent-facing documentation, not user-facing

---

## Dependency Graph

```
01-01 (search fix) --> 01-02 (port widening) --> 02-01 (enrichment sources) --> 03-01 (CLI) --> 04-01 (skills/agent)
```

All steps are sequential. Each depends on the previous.

## Implementation Scope

### Python TDD (steps 01-01 through 03-01)

| File | Action |
|------|--------|
| `scripts/pes/adapters/dsip_api_adapter.py` | Fix query format, update _normalize_topic |
| `scripts/pes/ports/topic_enrichment_port.py` | Widen enrich() signature |
| `scripts/pes/adapters/dsip_enrichment_adapter.py` | Replace PDF with API-first, add instruction cache |
| `scripts/pes/domain/topic_enrichment.py` | Handle new fields in combine and report |
| `scripts/pes/domain/finder_service.py` | Pass full topic dicts to enrich() |
| `scripts/dsip_cli.py` | Update filters, output, detail command |

### Markdown Forge (step 04-01)

| File | Action |
|------|--------|
| `skills/topic-scout/dsip-cli-usage.md` | New fields, hash ID examples |
| `skills/topic-scout/dsip-enrichment.md` | API-first strategy, new endpoints |
| `agents/sbir-topic-scout.md` | New data types in recommendation |

## Validation

- Unit tests: mock HTTP transport for all 4 endpoints
- Live fixtures: recorded API responses in `tests/fixtures/dsip_live/`
- Integration: CLI end-to-end with mocked adapters
- Mutation testing: scope to modified adapter files
