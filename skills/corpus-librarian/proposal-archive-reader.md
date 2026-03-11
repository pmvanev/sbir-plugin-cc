---
name: proposal-archive-reader
description: Domain knowledge for reading submitted/archived SBIR proposals -- submission domain models, archive directory layout, immutability constraints, portal-specific packaging, and corpus ingestion/retrieval strategies
---

# Proposal Archive Reader

## Submission Archive Domain Model

The submission domain in `scripts/pes/domain/submission.py` defines four core types:

| Type | Purpose | Frozen? |
|------|---------|---------|
| `PortalRules` | Portal-specific rules (naming, size limits, required files, guidance) | Yes |
| `PackageFile` | A file in the submission package with original name, category, size, portal name | No |
| `PackageResult` | Result of `prepare_package` -- portal ID, files, size check results, missing files, guidance | No |
| `SubmissionRecord` | Confirmation number, timestamp, archive path, immutable flag | Yes |

`ConfirmationPrompt` is an intermediate type used for human confirmation before submission.

## Archive Directory Layout

After submission, artifacts are archived under the proposal's artifact directory:

```
artifacts/wave-8-submission/
  submission-manifest.md          # Portal, timestamp, confirmation number, file checksums
  submitted/                      # Exact copies of submitted files (immutable)
    {category}_{proposal_id}.pdf  # Named per portal convention
    ...
  confirmation/
    confirmation-receipt.md       # Portal confirmation number and timestamp
    screenshot.png                # Optional portal screenshot
```

The `SubmissionService.record_submission()` method creates this archive by delegating to `ArchiveCreator.create_archive(package_dir, archive_dir)`. The archive creator copies all regular files from the package directory into the archive -- no subdirectories.

## Immutability Enforcement

Once a proposal is submitted (`submission.status == "submitted"` and `submission.immutable == True` in proposal state), PES blocks all write operations to the submitted artifacts.

The enforcement chain:
1. `SubmissionImmutabilityEvaluator.triggers()` checks if the rule has `requires_immutable` in its condition
2. If triggered, checks proposal state for `submission.status == "submitted"` AND `submission.immutable == True`
3. `build_block_message()` includes the topic ID if available: "Proposal {topic_id} is submitted. Artifacts are read-only."

When reading archived proposals, agents operate in read-only mode. Use Read, Glob, and Grep tools only -- never Write or Edit against submitted archive paths.

## Portal Identification and Packaging

The `SubmissionService.prepare_package()` method orchestrates portal-specific packaging:

1. **Identify portal**: `PortalRulesLoader.identify_portal(agency)` maps agency string to portal ID (DSIP, Grants.gov, NSPIRES)
2. **Load rules**: `PortalRulesLoader.load_rules_for_portal(portal_id)` returns `PortalRules` with naming, size limits, required files
3. **Apply naming**: Replaces `{category}` and `{proposal_id}` in the portal's naming convention template
4. **Verify sizes**: Compares each file's `size_bytes` against `max_file_size_mb * 1_000_000` (strict `>=` comparison)
5. **Check required files**: Compares provided file categories against `required_files` list; missing files block submission

Portal rules are loaded from JSON files in `templates/portal-rules/` by the `JsonPortalRulesAdapter`:

| Portal | File | Agency Patterns |
|--------|------|-----------------|
| DSIP | `dsip.json` | Air Force, Army, Navy, DARPA, DLA, MDA, SOCOM, CBD, DTRA |
| Grants.gov | `grants-gov.json` | Multi-agency (NSF, ED, DOT, EPA, SBA) |
| NSPIRES | `nspires.json` | NASA |

New portals are added by creating a JSON file -- no code changes required.

## Reading an Archived Proposal

To read and analyze a submitted proposal archive:

1. **Locate the archive**: Check `.sbir/proposal-state.json` for `submission.archive_path`
2. **Read the manifest**: `artifacts/wave-8-submission/submission-manifest.md` contains the file inventory with SHA-256 checksums
3. **Verify immutability**: Confirm `submission.immutable == True` in proposal state before proceeding (if false, archive may be incomplete)
4. **Read submitted files**: Use Read tool on files in the `submitted/` subdirectory
5. **Cross-reference confirmation**: Check `confirmation/confirmation-receipt.md` for portal confirmation number and submission timestamp

When comparing archived proposals across projects:
- Match by `portal_id` for portal-specific comparisons
- Match by agency pattern for cross-portal analysis
- Use `submitted_at` timestamp for temporal ordering
- Use SHA-256 checksums from manifest to detect identical files across archives

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
