---
name: proposal-state-patterns
description: State persistence patterns, atomic writes, status rendering, and session continuity for the SBIR orchestrator
---

# Proposal State Patterns

## State File Location

- Per-project state: `.sbir/proposal-state.json`
- Global company profile: `~/.sbir/company-profile.json`
- PES config: `.sbir/pes-config.json`
- Audit log: `.sbir/audit/`

## Reading State

Read `.sbir/proposal-state.json` to determine:
1. `current_wave` -- which wave is active
2. `go_no_go` -- whether proposal passed Wave 0 gate
3. `waves.{N}.status` -- per-wave completion status
4. `tpoc.status` -- async TPOC event state
5. `topic.deadline` -- submission deadline for countdown
6. `compliance_matrix.item_count` -- compliance coverage

## Status Rendering

When `/sbir:proposal status` is invoked, render a reorientation dashboard:

```
SBIR Proposal Status
====================
Topic:    {topic.id} -- {topic.title}
Agency:   {topic.agency}
Phase:    {topic.phase}
Deadline: {topic.deadline} ({days_remaining} days)
Go/No-Go: {go_no_go}

Wave Progress:
  [x] Wave 0 -- Intelligence & Fit (completed {date})
  [>] Wave 1 -- Requirements & Strategy (active)
  [ ] Wave 2 -- Research
  ...

Current Wave Details:
  Compliance matrix: {item_count} items extracted
  TPOC: {tpoc.status}
  Strategy brief: {strategy_brief.status}

Suggested Next Action:
  {contextual recommendation based on state}

Deadline Warnings:
  {any PES deadline warnings}
```

## Atomic State Writes

The orchestrator delegates state writes to PES Python code. Pattern:
1. Write new state to `.sbir/proposal-state.json.tmp`
2. Copy existing to `.sbir/proposal-state.json.bak`
3. Rename `.tmp` to target (atomic on most filesystems)

Do not write state JSON directly from the agent. Use the PES state adapter via Bash tool.

## Session Continuity

State survives Claude Code restarts. On session start:
1. PES SessionStart hook runs integrity check automatically
2. Orchestrator reads state to determine context
3. `/sbir:proposal status` provides full reorientation

## Error Message Pattern

All errors follow what/why/what-to-do:

```
WHAT:  "{description of what failed}"
WHY:   "{explanation of likely cause}"
DO:    "{actionable next step for the user}"
```

## State Schema Version

Current schema version: `1.0.0`. The `schema_version` field enables future migration. State readers check version compatibility before processing.
