---
name: corpus-domain-knowledge
description: Domain knowledge for SBIR/STTR corpus management -- document types, metadata schema, ingestion workflow, search strategies, and win/loss tracking patterns
---

# Corpus Domain Knowledge

## Document Taxonomy

SBIR/STTR corpus documents fall into five categories:

| Category | Contents | Value Signal |
|----------|----------|-------------|
| Past proposals | Technical volumes, cost volumes, cover letters | Reusable structure, technical language, scope framing |
| Debriefs | Score sheets, evaluator comments, debrief letters | Weakness patterns, scoring criteria insights |
| TPOC logs | Q&A transcripts, call notes, email threads | Agency preferences, topic clarifications, relationship signals |
| Boilerplate | Facilities, bios, past performance, capability statements | Direct reuse candidates (highest ROI) |
| Win/loss records | Outcome per proposal with metadata | Pattern database for strategy decisions |

## Supported File Types

Only these extensions are ingested (defined in `pes.domain.corpus.SUPPORTED_EXTENSIONS`):

- `.pdf` -- Proposals, debriefs, official documents
- `.docx` -- Draft proposals, editable boilerplate
- `.txt` -- Plain text notes, TPOC logs
- `.md` -- Structured notes, internal analyses

All other file types are skipped silently. Report the count of skipped files.

## Metadata Schema

Every `CorpusEntry` carries:

| Field | Type | Source |
|-------|------|--------|
| `path` | Path | Absolute path to source file |
| `content_hash` | str | SHA-256 hex digest of file bytes |
| `file_type` | str | Lowercase extension (e.g., `.pdf`) |
| `size_bytes` | int | File size in bytes |

Extended metadata (tracked in proposal state, not in CorpusEntry):

| Field | Source | Purpose |
|-------|--------|---------|
| `category` | User-provided or inferred | Document taxonomy classification |
| `agency` | Extracted from path or content | Agency preference modeling |
| `topic_number` | Extracted from filename/content | Links document to solicitation |
| `outcome` | User-provided | Win/loss pattern tracking |
| `proposal_id` | State-generated | Groups related documents |

## Deduplication Strategy

The `CorpusRegistry` deduplicates by SHA-256 content hash:

1. `FilesystemCorpusAdapter.scan()` computes hash for each supported file
2. `CorpusRegistry.register()` checks hash against `_known_hashes` set
3. If hash exists: skip (duplicate). If new: add to registry.
4. Previously known hashes loaded via `registry.load_hashes()` at startup

This means identical content at different paths is deduplicated. Modified versions of the same file (different hash) are both kept -- this is correct behavior for tracking proposal revisions.

## Ingestion Workflow

```
Directory → FilesystemCorpusAdapter.scan()
  → filter by SUPPORTED_EXTENSIONS
  → compute SHA-256 hash per file
  → create CorpusEntry per file
  → CorpusRegistry.register() each entry
  → IngestionResult (new, skipped_existing, skipped_unsupported)
```

Edge cases:
- Empty directory: "No supported documents found"
- All duplicates: "No new documents. N already in corpus."
- Mixed results: "N new documents ingested. M already in corpus."
- Non-directory path: "Not a directory: {path}"
- Non-existent path: "Directory not found: {path}"

## Search Strategies

When searching corpus for relevant past work:

1. **Keyword extraction**: Pull key technical terms from the solicitation topic
2. **Grep-based scan**: Search corpus files for keyword matches using Grep tool
3. **Context reading**: Read surrounding content of matches to assess relevance
4. **Outcome weighting**: Proposals with WIN outcomes are higher-value exemplars
5. **Debrief cross-reference**: If a matching proposal has debrief feedback, surface the evaluator comments -- they reveal what the agency valued

Search result ranking factors (descending priority):
- Direct topic area match
- Same agency + same technical domain
- WIN outcome (proven approach)
- Recency (more recent = more relevant boilerplate)
- Available debrief (learning opportunity)

## Boilerplate Identification

Boilerplate candidates share these characteristics:
- Appear across 2+ proposals with high textual similarity
- Describe organizational capabilities rather than project-specific work
- Common categories: facilities, key personnel bios, past performance narratives, corporate capability statements, quality management descriptions

Extraction workflow:
1. Identify repeated content blocks across proposals
2. Compare similarity (exact match or near-match)
3. Tag by boilerplate category
4. Present to human with: source locations, similarity score, recommended category
5. Human approves/rejects each candidate

## Win/Loss Pattern Database

Track per proposal:
- `proposal_id`: Unique identifier
- `agency`: DoD component or civilian agency
- `topic_number`: Solicitation topic
- `phase`: I, II, or Direct-to-Phase-II
- `outcome`: WIN, LOSS, NO_DECISION, WITHDRAWN
- `debrief_available`: Boolean
- `debrief_path`: Path to debrief document if available
- `strengths`: List extracted from debrief (if available)
- `weaknesses`: List extracted from debrief (if available)

Pattern analysis over time reveals:
- Agency-specific success factors
- Common weakness themes to proactively address
- Topic areas with highest win rates
- Evaluator scoring tendencies by agency
