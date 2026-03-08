# ADR-003: Claude Code Native File Reading for Corpus Search

## Status

Accepted

## Context

The corpus librarian agent must search past proposals, debriefs, and TPOC logs for relevant content. The search mechanism must support semantic similarity (not just keyword matching) while respecting the 10-15 hour per-proposal time budget -- any ingestion overhead must be near-zero.

Three options: (a) Claude Code reads files directly and uses LLM reasoning for relevance, (b) local vector database (ChromaDB, FAISS) with embeddings, (c) file-based indexing with keyword metadata.

## Decision

Option (a): Claude Code reads corpus files directly using its built-in file reading tools. The LLM reasons about relevance using its own context window. No separate indexing, no vector database, no embedding pipeline.

Corpus ingestion records file paths and content hashes in `proposal-state.json` for deduplication. Files remain in their original location. Claude Code reads them on demand.

## Alternatives Considered

### Local vector database (ChromaDB)
- What: Embed corpus documents into ChromaDB vectors. Query by similarity.
- Expected Impact: Better precision on large corpora (100+ documents). Sub-second retrieval.
- Why Rejected: At 2-3 proposals/year, the corpus grows slowly. After 5 years: ~15-20 documents. Vector DB adds a dependency (Python package, database files), embedding pipeline, and maintenance overhead that is unjustified for this scale. If corpus grows significantly, this decision can be revisited.

### File-based keyword index
- What: Extract keywords and metadata per document. Search by keyword overlap.
- Expected Impact: Fast keyword retrieval without LLM cost.
- Why Rejected: Keyword search misses semantic relationships (e.g., "directed energy" related to "laser weapons"). The whole point of corpus search is semantic similarity, which the LLM provides natively.

## Consequences

- **Positive:** Zero ingestion overhead beyond pointing at a directory. Near-zero setup.
- **Positive:** No additional dependencies (no vector DB, no embedding model).
- **Positive:** LLM provides genuine semantic understanding, not just keyword matching.
- **Negative:** Context window limits constrain how many documents can be searched simultaneously. For 15-20 documents this is fine; for 100+ it would degrade.
- **Negative:** Each search incurs LLM token cost (reading files). Acceptable for 2-3 proposals/year.
- **Negative:** No persistent index -- search is re-done each time. Acceptable for small corpus.
- **Migration path:** If corpus exceeds ~50 documents, add ChromaDB embedding layer as an adapter behind the same corpus search port. No agent changes required.
