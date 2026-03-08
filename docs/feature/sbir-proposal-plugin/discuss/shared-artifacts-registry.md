# Shared Artifacts Registry -- SBIR Proposal Lifecycle

## Purpose

Every `${variable}` in TUI mockups and every data value that appears in multiple waves must have a single source of truth. This registry documents each shared artifact, its canonical source, and all consumers.

## Registry

### proposal-state.json (Master State)

The single source of truth for all proposal metadata and wave status.

| Artifact | Source Path | Consumers | Integration Risk |
|----------|------------|-----------|-----------------|
| `${topic_id}` | `proposal-state.json#topic.id` | Status display, all checkpoint headers, artifact filenames, PES enforcement rules | HIGH -- mismatch breaks all displays |
| `${topic_title}` | `proposal-state.json#topic.title` | Status display, checkpoint headers | LOW |
| `${agency}` | `proposal-state.json#topic.agency` | Status display, corpus agency preference modeling | LOW |
| `${deadline}` | `proposal-state.json#topic.deadline` | Status display (as days remaining), PES deadline warnings, temporal invariants | HIGH -- wrong deadline = wrong urgency |
| `${days_to_deadline}` | Computed from `${deadline}` | Status display, PES warnings | HIGH -- derived value, must be recomputed each session |
| `${current_wave}` | `proposal-state.json#current_wave` | Status display, PES wave ordering enforcement | HIGH -- wrong wave = wrong gates |
| `${go_no_go}` | `proposal-state.json#go_no_go` | Status display, PES gate (blocks Wave 1 if not "go") | HIGH -- gate logic depends on this |
| `${tpoc_status}` | `proposal-state.json#tpoc_insights` (presence/absence) | Status display ("PENDING CALL" / "COMPLETED") | MEDIUM -- display only, does not block |
| `${phase}` | `proposal-state.json#phase` | Status display, budget defaults, page limit defaults | MEDIUM |

### Living Artifacts (Updated Across Waves)

| Artifact | Source of Truth | Created | Updated By | Consumers | Integration Risk |
|----------|----------------|---------|------------|-----------|-----------------|
| Compliance matrix | `./artifacts/wave-1-strategy/compliance-matrix.md` | Wave 1 | Waves 1, 4, 6, 7 (living document) | Drafting (section mapping), formatting (final check), final review, PES compliance gate | HIGH -- single file must be THE matrix |
| Strategy brief | `./artifacts/wave-1-strategy/strategy-brief.md` | Wave 1 | Wave 1 only (approved once) | Research direction, discrimination table, drafting context | MEDIUM -- referenced but not mutated |
| Discrimination table | `./artifacts/wave-3-outline/discrimination-table.md` | Wave 3 | Wave 3 only (approved once) | Drafting (every section), PDC Tier 3 checks, final review | HIGH -- every discriminator must be evidenced |
| Proposal outline | `./artifacts/wave-3-outline/proposal-outline.md` | Wave 3 | Wave 3 only (approved once) | Drafting (section structure and page budgets), PES section validation | HIGH -- defines what sections exist |
| PDC files | `./pdcs/*.pdc` | Wave 3 (via /proposal:distill) | Wave 4 iteration loop | /proposal:check runner, final review | HIGH -- PDCs drive the entire drafting loop |

### Corpus Artifacts (Append-Only)

| Artifact | Source of Truth | Write Policy | Consumers | Integration Risk |
|----------|----------------|-------------|-----------|-----------------|
| Past proposals | `./state/corpus/` | Append-only; submitted/awarded are read-only | Fit scoring (Wave 0), exemplar retrieval (Waves 3-4), voice/style extraction | MEDIUM -- read-only after tagging |
| Debrief feedback | `./state/corpus/` annotations | Append-only; annotates but never modifies source | Win/loss analysis, known weakness profile, reviewer agent heuristics | MEDIUM -- annotations layer |
| TPOC Q&A logs | `./artifacts/wave-1-strategy/tpoc-qa-log.md` | Write-once after ingestion | Strategy brief, compliance matrix updates, solicitation delta | LOW -- immutable after creation |
| Win/loss tags | `proposal-state.json#volumes.*.outcome` | Append-only; cannot be overwritten | Corpus librarian pattern analysis | LOW -- append-only by PES |

### Command Names (CLI Vocabulary)

| Command | Canonical Definition | Consumers | Integration Risk |
|---------|---------------------|-----------|-----------------|
| `/proposal new` | Plugin command registry | Help text, documentation, status suggestions | HIGH -- name mismatch = undiscoverable |
| `/proposal status` | Plugin command registry | Help text, re-entry guidance | HIGH |
| `/proposal wave <name>` | Plugin command registry | Help text, status display | HIGH |
| `/proposal corpus add <dir>` | Plugin command registry | Help text, empty corpus message | HIGH |
| `/proposal compliance check` | Plugin command registry | Help text, PES suggestions | HIGH |
| `/proposal tpoc questions` | Plugin command registry | Help text, status suggestions | HIGH |
| `/proposal tpoc ingest` | Plugin command registry | Help text, status suggestions | HIGH |
| `/proposal draft <section>` | Plugin command registry | Help text, PDC workflow | HIGH |
| `/proposal:check <section>` | Plugin command registry | Help text, PDC workflow | HIGH |
| `/proposal:distill` | Plugin command registry | Help text, PDC workflow | HIGH |
| `/proposal format` | Plugin command registry | Help text | MEDIUM |
| `/proposal submit prep` | Plugin command registry | Help text | MEDIUM |
| `/proposal debrief ingest` | Plugin command registry | Help text | MEDIUM |

## Validation Rules

### Rule 1: Single Source of Truth

Every artifact in this registry has exactly one canonical source. No consumer may create its own copy. Violations produce stale data that diverges silently.

### Rule 2: Living Documents Are Versioned

The compliance matrix is updated across waves but remains a single file. Changes are tracked via git (the user's repo) or PES audit log. There is never a "wave 1 compliance matrix" and a "wave 4 compliance matrix" -- there is THE compliance matrix.

### Rule 3: Immutability After Approval

Submitted proposals, TPOC logs, and win/loss tags are immutable after their creation event. PES enforces this at the write level. Debrief feedback annotates but never modifies the source document.

### Rule 4: Command Names Are Contract

Once published, command names are a user-facing API contract. Renaming a command requires a migration path (alias + deprecation warning).

## Integration Checkpoints

| Checkpoint | Validation | Failure Action |
|------------|-----------|---------------|
| Wave 0 -> Wave 1 | `${go_no_go}` == "go" in proposal-state.json | Block Wave 1 entry |
| Wave 1 -> Wave 2 | Strategy brief approved; compliance matrix exists | Block Wave 2 entry |
| Wave 3 -> Wave 4 | Discrimination table approved; outline approved; PDCs generated | Block drafting |
| Wave 4 -> Wave 5 | All sections have Tier 1+2 PDCs GREEN; at least one human review per section | Block visual assets |
| Wave 6 -> Wave 7 | All compliance items covered or waived; all figures exist | Block final review |
| Wave 7 -> Wave 8 | Final sign-off recorded | Block submission |
| Any wave | `${days_to_deadline}` <= critical threshold | PES warning (optional block) |
