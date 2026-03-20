---
name: proposal-state-patterns
description: State persistence patterns, atomic writes, status rendering, and session continuity for the SBIR orchestrator
---

# Proposal State Patterns

## Multi-Proposal Directory Layout

The plugin supports multiple concurrent proposals under a single project. The orchestrator resolves paths and provides them to wave agents via dispatch context.

### Directory Structure

```
.sbir/
  active-proposal              # plain text file: topic ID of active proposal (e.g., "af263-042")
  pes-config.json              # shared PES configuration
  proposals/
    af263-042/
      proposal-state.json      # per-proposal state
      compliance-matrix.json   # per-proposal compliance matrix
      tpoc-answers.json        # per-proposal TPOC data
      corpus/                  # per-proposal corpus index
      audit/                   # per-proposal audit log
    n244-012/
      proposal-state.json
      ...

artifacts/
  af263-042/
    wave-0-intelligence/
    wave-1-strategy/
    wave-2-research/
    ...
  n244-012/
    wave-0-intelligence/
    ...
```

### Reading Active Proposal

1. Read `.sbir/active-proposal` to get the active topic ID
2. State path: `.sbir/proposals/{active}/proposal-state.json`
3. Artifact path: `artifacts/{active}/wave-N-name/`

### Legacy Fallback

When `.sbir/active-proposal` does not exist, fall back to legacy single-proposal paths:
- State: `.sbir/proposal-state.json`
- Artifacts: `artifacts/wave-N-name/`

This ensures backward compatibility with existing single-proposal projects.

### Dispatch Context

The orchestrator resolves paths before dispatching to wave agents:
- `state_dir`: resolved state directory (e.g., `.sbir/proposals/af263-042/` or `.sbir/` for legacy)
- `artifact_base`: resolved artifact directory (e.g., `artifacts/af263-042/` or `artifacts/` for legacy)

Wave agents use `{state_dir}` and `{artifact_base}` instead of hardcoded paths.

### Global Paths (unchanged)

These remain at fixed locations regardless of active proposal:
- Company profile: `~/.sbir/company-profile.json`
- Partner profiles: `~/.sbir/partners/{slug}.json`
- Quality artifacts: `~/.sbir/quality-preferences.json`, `~/.sbir/winning-patterns.json`, `~/.sbir/writing-quality-profile.json`
- PES config: `.sbir/pes-config.json`

## State File Location (Legacy)

- Per-project state: `.sbir/proposal-state.json` (legacy) or `.sbir/proposals/{topic-id}/proposal-state.json` (multi-proposal)
- Global company profile: `~/.sbir/company-profile.json`
- PES config: `.sbir/pes-config.json`
- Audit log: `.sbir/audit/` (legacy) or `.sbir/proposals/{topic-id}/audit/` (multi-proposal)

## Reading State

Read `{state_dir}/proposal-state.json` to determine:
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
1. Write new state to `{state_dir}/proposal-state.json.tmp`
2. Copy existing to `{state_dir}/proposal-state.json.bak`
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
