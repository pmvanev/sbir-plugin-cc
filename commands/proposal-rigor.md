---
description: "View and manage rigor profile for the active proposal"
argument-hint: "[show|set] [profile-name] - View profiles or set active rigor level"
---

# /proposal rigor [show|set]

View, compare, and change the rigor profile controlling model tier, review depth, and critique loops for the active proposal.

## Usage

```
/proposal rigor
/proposal rigor show
/proposal rigor show <profile>
/proposal rigor set <profile>
```

## Subcommands

| Subcommand | Description |
|------------|-------------|
| *(no args)* | Interactive: show comparison table, prompt user to select |
| `show` | Comparison table of all 4 profiles (lean/standard/thorough/exhaustive), active profile highlighted |
| `show <profile>` | Detail view for one profile: all agent roles with tier, behavioral parameters. If different from current, shows what would change |
| `set <profile>` | Validate profile name, update via RigorService, show diff of changes. Applies to future waves only |

## Profiles

| Profile | Cost Range | Use Case |
|---------|-----------|----------|
| lean | $2-5/wave | Exploratory screening, low-fit Phase I |
| standard | $8-15/wave | Default for most proposals |
| thorough | $20-35/wave | High-fit Phase II, must-win opportunities |
| exhaustive | $40-60/wave | Maximum quality, cost secondary |

## Flow

### /proposal rigor show

1. Read active proposal from `.sbir/active-proposal`
2. Load rigor-resolution skill for rendering logic
3. Read `config/rigor-profiles.json` for all profile definitions
4. Read `.sbir/proposals/{topic-id}/rigor-profile.json` for active profile (default: standard)
5. Render comparison table using tier names (basic/standard/strongest), not model IDs
6. Highlight active profile with `>>` marker

### /proposal rigor show <profile>

1. Validate profile name against known set (lean/standard/thorough/exhaustive)
2. Render detail view: all agent roles with tier, behavioral parameters, cost range
3. If requested profile differs from active, append diff section showing what would change

### /proposal rigor set <profile>

1. Validate profile name
2. Invoke RigorService.set_profile() via Python (Bash tool): `python -c "from pes.domain.rigor_service import RigorService; ..."`
3. Render diff of what changes (per-agent-role and behavioral parameters)
4. Confirm change applied
5. Note: applies to future waves only, existing artifacts preserved

### /proposal rigor (no args)

1. Show comparison table (same as `show`)
2. Prompt user: "Select a profile to view details or set as active"

## Prerequisites

- Active proposal selected (`.sbir/active-proposal` exists), except for `show` which works without one (no active indicator shown)

## Agent Invocation

@sbir-orchestrator

Handle the `/proposal rigor` command with subcommand: {subcommand} {args}.

Read the active proposal's rigor-profile.json and config/rigor-profiles.json. For `show`, render the comparison table or detail view. For `set`, invoke RigorService via Python to update the profile and render the diff. For no args, show the comparison table and prompt for selection.

SKILL_LOADING: Load `skills/orchestrator/rigor-resolution.md` before processing. This skill contains the comparison table format, detail view format, diff rendering rules, and agent-role mapping.
