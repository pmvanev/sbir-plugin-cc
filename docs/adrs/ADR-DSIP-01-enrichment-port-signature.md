# ADR-DSIP-01: Enrichment Port Signature Change

## Status
Proposed

## Context
`TopicEnrichmentPort.enrich()` currently accepts `topic_ids: list[str]`. The instruction document download requires `cycle_name`, `release_number`, and `component` from the search response to construct the download URL. Passing only topic IDs forces the enrichment adapter to re-fetch search data or requires a separate lookup mechanism.

Quality attributes: Correctness (construct valid URLs), Maintainability (single enrichment call per topic batch).

## Decision
Change `enrich()` signature from `topic_ids: list[str]` to `topics: list[dict[str, Any]]`. Each dict contains at minimum: `topic_id`, `cycle_name`, `release_number`, `component`, `published_qa_count`. The adapter extracts what it needs.

## Alternatives Considered

### Alternative A: Keep `topic_ids` and add a separate `set_context(cycle_name, release_number)` method
- Pro: No signature break
- Con: Stateful adapter (set context before enrich). Breaks if batch spans multiple cycles. Adds coupling between calls.
- Rejected: Statefulness adds complexity for no benefit.

### Alternative B: Pass a separate `metadata: dict[str, dict]` mapping topic_id -> context
- Pro: Keeps topic_ids as primary param
- Con: Two parallel data structures that must stay in sync. Caller must build the metadata dict separately.
- Rejected: Topic dicts already contain all needed fields. Splitting is artificial.

## Consequences
- **Positive**: Single data structure, no statefulness, adapter extracts what it needs
- **Negative**: Breaking change to port interface. FinderService and all tests must update. Existing `DsipEnrichmentAdapter` tests use `topic_ids` -- must migrate.
- **Migration**: FinderService already has full topic dicts from fetch. Change `enrich(topic_ids=[t["topic_id"] for t in candidates])` to `enrich(topics=candidates)`.
