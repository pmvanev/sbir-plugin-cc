# /proposal debrief

Post-submission lifecycle command for Wave 9. Records outcomes, drafts debrief request letters, ingests debrief feedback, and generates lessons learned.

## Usage

```
/proposal debrief outcome <win|loss|no-decision|withdrawn>
/proposal debrief request-letter
/proposal debrief ingest <path-to-debrief-document>
/proposal debrief lessons
```

## Prerequisites

- Proposal submitted (Wave 8 complete) for all modes
- Outcome recorded before `request-letter` (loss triggers debrief request offer)
- Outcome recorded before `lessons` (needs outcome context)
- Debrief ingested before `lessons` produces full analysis (partial analysis available without)

## Modes

### outcome

Record the proposal result: `win`, `loss`, `no-decision`, or `withdrawn`. Updates proposal state with outcome tag and timestamp. For wins, archives the proposal and extracts discriminators. For losses, offers to draft a debrief request letter.

### request-letter

Draft an agency-specific debrief request letter. Selects template based on agency: FAR 15.505 for DoD (Air Force, Army, Navy), NASA-specific for NASA, DoD default for others. Reads company profile from `~/.sbir/company-profile.json` for contact information. Writes draft to `./artifacts/wave-9-debrief/`. Presents for human review -- drafts are never sent automatically.

### ingest [path]

Parse a debrief feedback document. Extracts evaluator scores (numeric and adjectival), maps strength and weakness comments to proposal sections, classifies loss root cause (technical, cost, strategic, past performance, or compliance), and updates the known weakness profile with new entries or incremented frequency counts.

### lessons

Generate a lessons-learned summary from all available debrief data. Synthesizes actionable insights, updates win/loss pattern analysis, computes per-agency metrics, and presents at human checkpoint for review. Writes summary to `./artifacts/wave-9-debrief/`.

## Output

All human-facing artifacts written to `./artifacts/wave-9-debrief/`:
- `outcome-{topic_id}.json` -- outcome archive (wins)
- `debrief-request-{topic_id}.md` -- draft debrief request letter
- `debrief-analysis.json` -- parsed debrief scores and critique map
- `{topic_id}-loss-analysis.md` -- loss analysis with root cause
- `{topic_id}-win-analysis.md` -- win analysis with discriminators
- `{topic_id}-lessons-learned.md` -- lessons learned summary
- `pattern-analysis.json` -- cumulative win/loss patterns

Machine-readable state updates written to `.sbir/proposal-state.json`.

## Implementation

This command dispatches to `sbir-debrief-analyst` agent, which loads skills from `skills/debrief-analyst/` and `skills/corpus-librarian/`.

**Domain services invoked by the agent:**

| Mode | Service | Method |
|------|---------|--------|
| outcome | `OutcomeService` | `record_outcome()` |
| request-letter | `OutcomeService` | `generate_debrief_letter()` |
| ingest | `DebriefService` | `ingest_debrief()` |
| lessons | `OutcomeService` | `update_pattern_analysis()`, `present_lessons_learned()` |

**Templates:** `templates/debrief-request/dod-far-15-505.md`, `templates/debrief-request/nasa-debrief.md`

**Skills loaded by agent:** `debrief-domain-knowledge`, `win-loss-analyzer`, `proposal-archive-reader`
