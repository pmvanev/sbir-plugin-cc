---
name: continue-detection
description: State detection priority, wave-to-command mapping, display patterns, and error handling for the sbir-continue agent
---

# Continue Detection

## State Detection Priority

Evaluate in this exact order. Stop at the first match.

| Priority | Check | Classification | Route |
|----------|-------|---------------|-------|
| 0 | `.sbir/proposals/` directory exists | multi_proposal | Load multi-proposal-dashboard skill, render dashboard |
| 1 | No profile at `~/.sbir/company-profile.json` AND no `.sbir/proposal-state.json` | no_setup | Welcome + suggest /sbir:setup |
| 2 | Profile exists but no corpus (0 files in `.sbir/corpus/`) AND no proposal state | partial_setup | Setup checklist + options |
| 3 | Profile exists, setup functionally complete, no `.sbir/proposal-state.json` | no_proposal | Profile summary + suggest find/new |
| 4 | Proposal state has `archived: true` OR `go_no_go: "no-go"` | archived | Decline notice + suggest new |
| 5 | Proposal state has `go_no_go: "deferred"` | deferred | Deferred notice + resume or new |
| 6 | All `waves.{0-9}.status` are "completed" | lifecycle_complete | Completion + suggest new |
| 7 | `waves.8.status` is "completed" AND `waves.9.status` is "not_started" | post_submission | Submission confirmed + debrief guidance |
| 8 | `waves.{current_wave-1}.status` is "completed" AND `waves.{current_wave}.status` is "not_started" | between_waves | Wave transition guidance |
| 9 | `waves.{current_wave}.status` is "active" or "in_progress" | mid_wave | Within-wave progress + next task |

## Setup Completeness

Setup is **functionally complete** when:
- Profile exists at `~/.sbir/company-profile.json` (required)
- Corpus has >= 1 document in `.sbir/corpus/` (required for "complete", optional for "usable")

API key (GEMINI_API_KEY) is optional -- used only in Wave 5 for concept figure generation.

**Partial setup** = profile exists but corpus empty AND no proposal state. If profile exists and proposal state exists, skip partial setup check (user already started a proposal).

## Wave Names and Descriptions

| Wave | Name | Description | Entry Command |
|------|------|-------------|---------------|
| 0 | Intelligence & Fit | Topic analysis, fit scoring, Go/No-Go decision | /sbir:proposal new <solicitation> |
| 1 | Requirements & Strategy | Compliance extraction, TPOC analysis, strategy brief | /sbir:proposal wave strategy |
| 2 | Research | Technical landscape, prior art, competitive analysis | /sbir:proposal wave research |
| 3 | Discrimination & Outline | Discrimination table and proposal outline | /sbir:proposal wave outline |
| 4 | Drafting | Section-by-section proposal writing | /sbir:proposal draft technical |
| 5 | Visual Assets | Concept figures and diagrams | /sbir:proposal wave visuals |
| 6 | Formatting & Assembly | Document formatting and compliance check | /sbir:proposal format |
| 7 | Final Review | Comprehensive review and compliance verification | /sbir:proposal review |
| 8 | Submission | Package assembly and portal preparation | /sbir:proposal submit prep |
| 9 | Post-Submission | Evaluator debrief ingestion and lessons learned | /sbir:proposal debrief ingest <feedback-file> |

## Wave 0 Special States

Wave 0 has sub-states beyond simple active/completed:

| State Field | Value | Display | Suggested Command |
|-------------|-------|---------|-------------------|
| `go_no_go` | "pending" | Go/No-Go decision pending | Review fit scoring results |
| `go_no_go` | "go" + `approach_selection` "pending" | Approach selection pending | /sbir:proposal shape |
| `go_no_go` | "go" + `approach_selection` "approved" | Wave 0 complete | (proceed to Wave 1) |
| `go_no_go` | "no-go" | Proposal declined | Start new proposal |
| `go_no_go` | "deferred" | Decision deferred | Resume evaluation or start new |

## Wave 1 Task Checklist

| Task | State Field | Done When | Display |
|------|------------|-----------|---------|
| Compliance matrix | `compliance_matrix.item_count` | > 0 | [ok] Compliance matrix ({count} items) |
| TPOC questions | `tpoc.status` | "questions_generated" or "answers_ingested" | [ok] or [..] depending on status |
| Strategy brief | `strategy_brief.status` | "completed" or "approved" | [ok] Strategy brief |

TPOC is async and optional. If status is "questions_generated", display as `[..] TPOC (questions generated -- call pending, optional)`. Never suggest waiting for the call.

## Wave 4 Volume Tracking

| Volume | State Field | Statuses |
|--------|------------|----------|
| Technical | `volumes.technical.status` | not_started, drafting, in_review, approved |
| Management | `volumes.management.status` | not_started, drafting, in_review, approved |
| Cost | `volumes.cost.status` | not_started, drafting, in_review, approved |

For in_review volumes, also display `open_review_items` count if available. Suggest iterating volumes that are in_review before drafting volumes that are not_started.

## Mid-Wave Command Suggestions

When mid-wave, suggest the command for the first incomplete task:

| Wave | First Incomplete Task | Suggested Command |
|------|----------------------|-------------------|
| 0 | Go/No-Go pending | Review fit scoring results in artifacts/wave-0-intelligence/ |
| 0 | Approach pending | /sbir:proposal shape |
| 1 | Compliance not done | /sbir:proposal compliance check |
| 1 | Strategy not done | /sbir:proposal wave strategy |
| 4 | Technical not done | /sbir:proposal draft technical |
| 4 | Management not done | /sbir:proposal draft management (or iterate if in_review) |
| 4 | Cost not done | /sbir:proposal draft cost (or iterate if in_review) |

For other waves, use the entry command from the Wave Names table.

## Deadline Display

Compute days remaining: `topic.deadline` (ISO 8601) minus current date.

| Days Remaining | Display |
|---------------|---------|
| > 7 | Deadline: {date} ({N} days) |
| 4-7 | Deadline: {date} ({N} days) -- approaching |
| 1-3 | [!!] Deadline: {date} ({N} days) -- critical |
| 0 | [!!] Deadline: {date} -- TODAY |
| < 0 | [!!] Deadline: {date} -- passed {N} days ago |

Past-deadline is a warning, not a blocker. Still display suggested next action.

## Status Indicators

| Indicator | Meaning | Use For |
|-----------|---------|---------|
| `[ok]` | Complete / present / configured | Completed tasks, existing profile |
| `[..]` | In progress / pending external | TPOC call pending, volume in review |
| `[  ]` | Not started | Tasks not yet begun |
| `[--]` | Missing / not configured (optional) | Missing corpus, missing API key |
| `[!!]` | Warning / critical issue | Deadline critical, corrupt state |
| `[x]` | Wave completed | Wave progress list |
| `[>]` | Current wave | Wave progress list |
| `[ ]` | Future wave | Wave progress list |

## Partial Setup Display Pattern

```
Setup Status:
  [ok] Company profile ({company_name})
  [{corpus_indicator}] Corpus ({corpus_detail})
  [{api_indicator}] GEMINI_API_KEY ({api_detail})

{status_message}

Options:
  (c) continue setup  -- resume from first gap
  (s) skip to proposal -- start a proposal now
  (q) quit
```

Corpus indicator: `[ok]` if >= 1 document, `[--]` if 0 | API indicator: `[ok]` if set, `[--]` if not

## No Active Proposal Display Pattern

```
Profile: {company_name}
Corpus:  {document_count} documents indexed

No active proposal found.

Ready to start:
  /sbir:solicitation find           -- discover topics matching your profile
  /sbir:proposal new <solicitation> -- start a new proposal
```

## Error Handling

All errors use the what/why/do pattern:

### Corrupted State (invalid JSON)
```
WHAT:  Could not read proposal state.
WHY:   The state file contains invalid JSON, possibly from an interrupted write.
DO:    Run /sbir:proposal status for diagnostics.
       PES session checker may recover from the .bak backup.
```

### Schema Version Mismatch
```
WHAT:  State file uses an older schema version.
WHY:   The plugin was updated but the state file was not migrated.
DO:    Run /sbir:proposal status to check compatibility.
```

### Missing Fields in State
If required fields are missing from an otherwise valid state file, report which fields are absent and suggest `/sbir:proposal status` for diagnostics. Do not crash or display raw JSON.

## Reading State Files

### Company Profile
```bash
cat ~/.sbir/company-profile.json 2>/dev/null
```
Extract `company_name` field. If file does not exist, profile is absent.

### Proposal State
```bash
cat .sbir/proposal-state.json 2>/dev/null
```
If file exists but contains invalid JSON, classify as corrupted state error. If file does not exist, proposal state is absent.

### Corpus Count
```bash
find .sbir/corpus/ -type f 2>/dev/null | wc -l
```
If directory does not exist, count is 0.

### API Key
```bash
echo "${GEMINI_API_KEY:+configured}"
```
Outputs "configured" if set, empty if not.
