---
name: proposal-archive-reader
description: Domain knowledge for ingesting and retrieving past proposals from corpus -- file scanning, deduplication workflow, wave-tailored retrieval strategies, and boilerplate extraction patterns
---

# Proposal Archive Reader

## Ingestion Pipeline

The ingestion pipeline follows the ports-and-adapters pattern in `scripts/pes/`:

```
User provides directory path
  -> FilesystemCorpusAdapter.scan(directory)
     -> filter by SUPPORTED_EXTENSIONS (.pdf, .docx, .txt, .md)
     -> compute SHA-256 hash per file (hashlib.sha256(content).hexdigest())
     -> create CorpusEntry(path, content_hash, file_type, size_bytes)
  -> CorpusRegistry.register(entry) per scanned file
     -> check content_hash against _known_hashes set
     -> if new: add to registry, return True
     -> if duplicate: skip, return False
  -> IngestionResult(new_entries, skipped_existing, skipped_unsupported)
```

State update after ingestion -- patch `.sbir/proposal-state.json`:
- `corpus.directories_ingested`: append directory path if not already present
- `corpus.document_count`: update total
- `corpus.file_hashes`: add new hash -> path mappings

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty directory | "No supported documents found. Supported types: .docx, .md, .pdf, .txt." |
| All duplicates | "No new documents. N already in corpus." |
| Non-existent path | "Directory not found: {path}" |
| Not a directory | "Not a directory: {path}" |
| Mixed supported/unsupported | Report both counts: "Ingested N documents. Skipped M unsupported files." |
| Identical content at different paths | Deduplicated (same hash). Only first occurrence kept. |
| Modified version of same file | Different hash -- both versions kept. Correct for tracking revisions. |

## Wave-Tailored Retrieval

Different waves need different retrieval strategies:

### Wave 0 -- Intelligence & Fit
**Purpose**: Assess company fit against a new solicitation topic.
**Retrieve**: Past proposals in same technical domain and agency. Win/loss outcomes for fit scoring.
**Rank by**: Agency match > technical domain match > outcome (WIN highest) > recency.
**Output format**: Relevance-scored list with outcome tags and brief topic summaries.

### Wave 1 -- Requirements & Strategy
**Purpose**: Inform strategy brief with past institutional knowledge.
**Retrieve**: Past proposals with debrief feedback in related domains. TPOC Q&A logs for same agency.
**Rank by**: Debrief availability > agency match > technical relevance.
**Output format**: Debrief excerpts mapped to strategy dimensions (approach, team, cost, schedule).

### Wave 3 -- Discrimination & Outline
**Purpose**: Provide structural exemplars for proposal outline.
**Retrieve**: Winning proposals with clear section structures. Discrimination tables from past proposals.
**Rank by**: WIN outcome (required) > same agency > same phase > structural clarity.
**Output format**: Section headings with page budgets, figure/table counts, thesis statement patterns.

### Wave 4 -- Drafting
**Purpose**: Tone, voice, and content reference for section writing.
**Retrieve**: Specific sections matching the section being drafted. Boilerplate for facilities/bios/past performance.
**Rank by**: Section type match > WIN outcome > same agency > same phase.
**Output format**: Relevant passages with source attribution and boilerplate flags.

### Wave 9 -- Post-Submission & Learning
**Purpose**: Archive current proposal and extract lessons learned.
**Retrieve**: Similar past proposals for comparative analysis. Debrief patterns for trend identification.
**Rank by**: Same agency > same topic area > temporal proximity.
**Output format**: Comparative table (current vs. past proposals on same topic/agency).

## Boilerplate Identification Heuristics

Content qualifies as a boilerplate candidate when it:
- Appears across 2+ proposals with high textual similarity (>80% overlap)
- Describes organizational capabilities rather than project-specific work
- Falls into standard categories: facilities, key personnel bios, past performance narratives, corporate capability statements, quality management descriptions, security clearance statements

Extraction workflow:
1. Identify repeated content blocks across proposals using Grep
2. Compare similarity by overlapping phrases (exact match or near-match)
3. Tag by boilerplate category
4. Present to human with: source locations, similarity assessment, recommended category
5. Human approves or rejects each candidate -- never auto-promote

## Corpus Content Categories

| Category | Contents | Retrieval Value |
|----------|----------|----------------|
| Past proposals | Technical volumes, cost volumes, cover letters | Reusable structure, technical language, scope framing |
| Debriefs | Score sheets, evaluator comments, debrief letters | Weakness patterns, scoring criteria insights |
| TPOC logs | Q&A transcripts, call notes, email threads | Agency preferences, topic clarifications |
| Boilerplate | Facilities, bios, past performance, capability statements | Direct reuse candidates (highest ROI) |
| Win/loss records | Outcome per proposal with metadata | Pattern database for strategy decisions |
