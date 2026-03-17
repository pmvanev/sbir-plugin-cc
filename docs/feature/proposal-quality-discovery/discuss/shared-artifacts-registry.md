# Shared Artifacts Registry: Proposal Quality Discovery

## Artifact Registry

### quality-preferences.json

| Field | Value |
|-------|-------|
| Source of truth | `~/.sbir/quality-preferences.json` |
| Owner | Quality discovery flow (quality-discoverer agent or embedded in setup wizard) |
| Consumers | sbir-writer (Wave 3-4 drafting), sbir-reviewer (Wave 4, 7 review), Step 4 artifact assembly display |
| Integration risk | MEDIUM -- writer and reviewer must both interpret tone/organization values consistently |
| Validation | Schema validation on write; consumer agents load with graceful fallback if missing or malformed |

### winning-patterns.json

| Field | Value |
|-------|-------|
| Source of truth | `~/.sbir/winning-patterns.json` |
| Owner | Quality discovery flow (generated from past proposal quality ratings) |
| Consumers | sbir-strategist (Wave 1 competitive positioning), sbir-writer (Wave 3-4 pattern replication), Step 5 strategist consumption |
| Integration risk | MEDIUM -- patterns must reference valid topic_ids from company-profile.json past_performance |
| Validation | topic_id cross-reference against company-profile.json; confidence_level computed from win count |

### writing-quality-profile.json

| Field | Value |
|-------|-------|
| Source of truth | `~/.sbir/writing-quality-profile.json` |
| Owner | Quality discovery flow (generated from evaluator feedback extraction) |
| Consumers | sbir-writer (Wave 3-4 quality alerts), sbir-reviewer (Wave 4, 7 quality profile match findings) |
| Integration risk | HIGH -- auto-categorization of meta-writing vs content feedback must be accurate to prevent contamination of the weakness profile |
| Validation | Each entry must link to a valid proposal topic_id and agency; category must be from the defined taxonomy |

### writing_style (proposal-state.json field)

| Field | Value |
|-------|-------|
| Source of truth | `.sbir/proposal-state.json#writing_style` |
| Owner | Proposal setup flow (populated from quality-preferences.json tone selection) |
| Consumers | sbir-writer (skill loading: loads `skills/writer/{writing_style}.md`), sbir-reviewer (skill loading: reviews against matching style) |
| Integration risk | HIGH -- writing_style value must map to an existing skill file name; invalid values cause skill load failure |
| Validation | Value must match a `.md` file in `skills/writer/` directory; null is valid (uses default) |

### past_performance entries (company-profile.json)

| Field | Value |
|-------|-------|
| Source of truth | `~/.sbir/company-profile.json#past_performance` |
| Owner | sbir-profile-builder agent |
| Consumers | Step 1 past proposal quality review (reads topic_id, agency, outcome), winning-patterns.json cross-reference |
| Integration risk | LOW -- read-only consumption; quality discovery does not modify company profile |
| Validation | Entries must have topic_id, agency, and outcome fields per company-profile-schema.json |

### weakness_profile (existing, via win-loss-analyzer)

| Field | Value |
|-------|-------|
| Source of truth | `.sbir/proposal-state.json` (per-proposal) and pattern-analysis.json (cross-proposal) |
| Owner | sbir-debrief-analyst and sbir-corpus-librarian |
| Consumers | sbir-reviewer (existing flow), Step 3 evaluator feedback extraction (content feedback routed here) |
| Integration risk | MEDIUM -- content feedback from Step 3 must be routed to weakness profile, not to writing-quality-profile, to avoid duplication |
| Validation | Content feedback entries follow existing weakness_profile schema (category, pattern, frequency, agencies) |

## Integration Checkpoints

### Checkpoint 1: Past Performance Cross-Reference
- **When**: Step 1 (past proposal review) and Step 4 (artifact assembly)
- **Validates**: Every topic_id in winning-patterns.json exists in company-profile.json past_performance
- **Failure**: Orphan pattern (references proposal not in profile) -- warn user, allow proceed

### Checkpoint 2: Writing Style Skill Mapping
- **When**: Step 2 (style interview) and Step 6 (writer consumption)
- **Validates**: writing_style value maps to an existing skill file in skills/writer/
- **Failure**: Missing skill file -- fall back to default prose conventions, warn user

### Checkpoint 3: Feedback Categorization Accuracy
- **When**: Step 3 (evaluator feedback extraction)
- **Validates**: Auto-categorization is presented to user for confirmation; user can override
- **Failure**: Miscategorized feedback -- user corrects category before storage

### Checkpoint 4: Artifact Schema Compliance
- **When**: Step 4 (artifact assembly)
- **Validates**: All three artifacts are valid JSON with required fields (schema_version, updated_at)
- **Failure**: Validation error -- present error, allow correction before save

### Checkpoint 5: Downstream Agent Load
- **When**: Steps 5-7 (strategist, writer, reviewer consumption)
- **Validates**: Agents can read quality artifacts without error; missing artifacts produce graceful degradation, not crashes
- **Failure**: Malformed artifact -- agent logs warning, proceeds with defaults

## CLI Vocabulary Consistency

| Action | Command | Notes |
|--------|---------|-------|
| Initial quality discovery | `/sbir:proposal quality discover` | Full guided Q&A flow |
| Update after proposal cycle | `/sbir:proposal quality update` | Incremental update, preserves existing data |
| View quality artifacts summary | `/sbir:proposal quality status` | Display current state of all three artifacts |

Command pattern follows existing SBIR plugin convention: `/sbir:proposal {noun} {verb}`.

## Data Flow Diagram

```
~/.sbir/company-profile.json
  |
  | past_performance entries (read-only)
  v
[Step 1: Past Proposal Review]
  |
  | quality ratings + winning practices
  v
~/.sbir/winning-patterns.json  -----> [Step 5: Strategist]
  |                                      |
  |                                      v
  |                               strategy-brief.md
  |
[Step 2: Writing Style Interview]
  |
  | tone, detail, evidence, organization, practices
  v
~/.sbir/quality-preferences.json -----> [Step 6: Writer]
  |                                      |
  | writing_style value                  v
  v                               section drafts
.sbir/proposal-state.json#writing_style
  |
  |
[Step 3: Evaluator Feedback Extraction]
  |
  |---(meta-writing)---> ~/.sbir/writing-quality-profile.json --> [Step 7: Reviewer]
  |                                                                  |
  |---(content)--------> weakness profile (existing flow)            v
                                                              review scorecards
```
