---
name: multi-proposal-dashboard
description: Enumeration patterns, display templates, corruption handling, and deadline sorting for the multi-proposal dashboard in sbir-continue
---

# Multi-Proposal Dashboard

## Multi-Proposal Detection

Insert before existing detection priorities in continue-detection. Evaluate before single-proposal checks.

| Priority | Check | Classification | Route |
|----------|-------|---------------|-------|
| 0 | `.sbir/proposals/` directory exists | multi_proposal | Load this skill, render dashboard |

If `.sbir/proposals/` exists, multi-proposal mode is active. Skip single-proposal detection priorities and render the dashboard instead.

## Enumeration Pattern

### Discovery

```bash
# Glob for all proposal state files
.sbir/proposals/*/proposal-state.json
```

### Reading Each Proposal

For each discovered `proposal-state.json`:

1. Attempt to parse as JSON
2. On success: extract `topic.id`, `topic.title`, `current_wave`, `topic.deadline`, wave statuses, `archived`, `go_no_go`
3. On failure (invalid JSON): record as corrupted, continue to next proposal

### Active Proposal Indicator

```bash
cat .sbir/active-proposal 2>/dev/null
```

The content is the lowercase topic ID of the currently active proposal. Mark this proposal with `>` prefix in the dashboard table.

## Dashboard Display Template

### Active Proposals

```
Active Proposals:
| Topic ID    | Title                          | Wave | Deadline   | Days | Status      |
|-------------|--------------------------------|------|------------|------|-------------|
| > af263-042 | Compact Directed Energy        | 3    | 2026-04-15 | 27   | Outlining   |
|   n244-012  | AUV Navigation                 | 0    | 2026-05-30 | 72   | Fit Scoring |
```

- `>` prefix marks the currently active proposal
- Days computed as: `topic.deadline` minus current date
- Status derived from wave name and sub-state (see Wave Names in continue-detection skill)
- Title truncated to 30 characters if longer

### Completed Proposals

```
Completed Proposals:
| Topic ID    | Title                | Submitted  | Outcome |
|-------------|----------------------|------------|---------|
|   da-25-001 | Sensor Fusion        | 2026-01-10 | Awarded |
```

- Submitted date from Wave 8 completion timestamp
- Outcome: "Submitted", "Archived", "No-Go", or "Awarded" (if debrief recorded)

### No Active Proposals

When all proposals are completed:

```
No active proposals.

Completed Proposals:
| Topic ID    | Title                | Submitted  | Outcome |
|-------------|----------------------|------------|---------|
|   af263-042 | Compact Directed     | 2026-04-14 | Submitted |
|   n244-012  | AUV Navigation       | 2026-05-01 | Submitted |

Start a new proposal with /sbir:proposal new <solicitation>
or switch to a completed proposal for debrief: /sbir:proposal switch <topic-id>
```

### Single Proposal in Multi-Proposal Layout

When only one proposal exists under `.sbir/proposals/`, render the familiar single-proposal display from continue-detection skill (not the table). This keeps the experience consistent until the user actually has multiple proposals.

## Completion Determination

A proposal is **completed** when any of these conditions is true:

- `waves["8"]["status"] == "completed"` (submitted)
- `archived == true`
- `go_no_go == "no-go"`

All other proposals are **active**.

## Active/Completed Separation

1. Enumerate all proposals
2. Classify each as active or completed using completion determination rules
3. Sort active proposals by deadline ascending (closest deadline first)
4. Sort completed proposals by submission date descending (most recent first)
5. Render active section first, then completed section
6. Omit a section entirely if it has zero entries (except: if zero active, show the "No active proposals" message)

## Deadline Sorting and Suggestion Logic

### Sorting

Active proposals are sorted by `topic.deadline` ascending. The proposal with the closest deadline appears first in the table.

### Deadline Display

Apply the same deadline display rules from continue-detection skill:

| Days Remaining | Display |
|---------------|---------|
| > 7 | {N} days |
| 4-7 | {N} days -- approaching |
| 1-3 | {N} days -- critical |
| 0 | TODAY |
| < 0 | passed {N} days ago |

### Suggestion Pattern

After the dashboard table, suggest switching to the closest-deadline proposal if it is not currently active:

```
AF263-042 has the closest deadline (27 days). Consider: /sbir:proposal switch af263-042
```

If the closest-deadline proposal is already active, suggest the next action for that proposal using the mid-wave command suggestions from continue-detection skill:

```
Currently active: af263-042 (Compact Directed Energy) -- Wave 3, 27 days to deadline
Next: /sbir:proposal wave outline
```

If only one active proposal exists, do not suggest switching. Show the standard next-action suggestion.

## Corruption Handling

### Per-Proposal Error Isolation

If `proposal-state.json` is invalid JSON for a given proposal:

1. Do **not** crash or abort the dashboard
2. Show an error row in the active proposals table:

```
| [!!] af263-042 | State corrupted    | --   | --         | --   | Error       |
```

3. After the table, show recovery guidance:

```
[!!] af263-042: State file corrupted (invalid JSON).
     Run /sbir:proposal switch af263-042 then /sbir:proposal status for recovery.
     PES session checker may recover from the .bak backup.
```

### Other Error Cases

| Error | Handling |
|-------|----------|
| Missing `topic.id` field | Show namespace directory name as topic ID, flag `[!!] Missing topic ID` |
| Missing `topic.deadline` | Show `--` for deadline and days, sort to end of list |
| Missing `current_wave` | Show `--` for wave, derive status as "Unknown" |
| `.sbir/active-proposal` missing | Show all proposals without `>` indicator, add warning: "No active proposal set. Run /sbir:proposal switch <topic-id>" |
| `.sbir/active-proposal` references nonexistent proposal | Show warning: "Active proposal '{id}' not found. Run /sbir:proposal switch <topic-id>" |

## Status Derivation

Derive the human-readable status from wave state:

| Wave | Sub-State | Status Label |
|------|-----------|-------------|
| 0 | `go_no_go == "pending"` | Fit Scoring |
| 0 | `go_no_go == "go"`, `approach_selection == "pending"` | Shaping |
| 0 | `go_no_go == "go"`, `approach_selection == "approved"` | Wave 0 Complete |
| 0 | `go_no_go == "deferred"` | Deferred |
| 1 | active | Strategy |
| 2 | active | Research |
| 3 | active | Outlining |
| 4 | active | Drafting |
| 5 | active | Visuals |
| 6 | active | Formatting |
| 7 | active | Review |
| 8 | active | Submission |
| 9 | active | Debrief |
