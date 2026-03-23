# Shared Artifacts Registry -- Rigor Profile

Feature: rigor-profile
Date: 2026-03-23
Phase: 2 -- Journey Visualization

---

## Artifact Registry

### rigor-profile.json (per-proposal)

- **Source of truth**: `.sbir/proposals/{topic-id}/rigor-profile.json`
- **Owner**: rigor-profile feature
- **Created by**: `/proposal new` (with default "standard" profile)
- **Modified by**: `/proposal rigor set <profile>`
- **Integration risk**: HIGH -- every agent reads this to resolve model tier and behavior settings. If missing or malformed, agents fall back to undefined behavior.

**Schema** (conceptual):

```json
{
  "profile": "thorough",
  "set_at": "2026-04-01T14:30:00Z",
  "history": [
    {
      "from": "standard",
      "to": "thorough",
      "at": "2026-04-01T14:30:00Z",
      "wave": 0
    }
  ]
}
```

**Consumers**:

| Consumer | Field Used | Purpose |
|----------|-----------|---------|
| `/proposal new` output | `profile` | Display default rigor after creation |
| `/proposal rigor show` | `profile` | Show active profile in header |
| `/proposal rigor set` | `profile`, `history` | Read current, write new, append history |
| `/proposal status` | `profile` | Display rigor per proposal |
| `/proposal switch` | `profile` (of target) | Display rigor after switch |
| Wave execution (all waves) | `profile` | Resolve model tier and behavior per agent role |
| `/proposal debrief` | `profile`, `history` | Rigor summary in debrief output |
| Rigor suggestion logic | `profile` | Determine if suggestion needed |

**Validation**: Profile value must be one of: lean, standard, thorough, exhaustive. History array must be append-only (never truncated).

---

### rigor-profiles.json (plugin-level, read-only)

- **Source of truth**: `config/rigor-profiles.json` (shipped with plugin)
- **Owner**: plugin maintainers
- **Created by**: Plugin installation
- **Modified by**: Plugin updates only (not user-editable)
- **Integration risk**: HIGH -- defines what each profile name means. If profile definitions and agent resolution logic disagree, rigor becomes a placebo dial.

**Schema** (conceptual):

```json
{
  "profiles": {
    "lean": {
      "description": "Fast screening with minimal cost",
      "quality_label": "Basic",
      "cost_range": "$2-5/wave",
      "agent_roles": {
        "strategist": { "model_tier": "basic" },
        "writer": { "model_tier": "basic" },
        "reviewer": { "model_tier": "basic", "passes": 1 },
        "researcher": { "model_tier": "basic" },
        "compliance": { "model_tier": "basic" },
        "visual_assets": { "model_tier": "basic", "critique_iterations": 0 }
      },
      "review_passes": 1,
      "critique_max_iterations": 0,
      "iteration_cap": 1
    },
    "standard": { "..." : "..." },
    "thorough": { "..." : "..." },
    "exhaustive": { "..." : "..." }
  }
}
```

**Consumers**:

| Consumer | Field Used | Purpose |
|----------|-----------|---------|
| `/proposal rigor show` | All profile definitions | Render comparison table |
| `/proposal rigor show <profile>` | Specific profile detail | Render detail view |
| `/proposal rigor set` | Profile names list | Validate profile name input |
| Agent model resolution | `agent_roles.{role}.model_tier` | Determine which model tier to use |
| Agent behavior resolution | `review_passes`, `critique_max_iterations`, `iteration_cap` | Configure agent execution parameters |

**Validation**: All four profiles must be defined. Each profile must specify all agent roles. Model tiers must be from set: basic, standard, strongest.

---

### proposal-state.json (per-proposal, pre-existing)

- **Source of truth**: `.sbir/proposals/{topic-id}/proposal-state.json`
- **Owner**: multi-proposal workspace feature (pre-existing)
- **Modified by**: Various commands throughout proposal lifecycle
- **Integration risk**: MEDIUM -- rigor feature reads from this but does not own it. Changes to proposal-state schema by other features could affect rigor suggestion logic.

**Fields consumed by rigor feature**:

| Field | Consumed By | Purpose |
|-------|-------------|---------|
| `fit_score` | `/proposal new` rigor suggestion | Suggest thorough for high fit |
| `contract_value` | `/proposal new` rigor suggestion | Suggest thorough for Phase II |
| `phase` | `/proposal new` rigor suggestion | Phase II weight in suggestion |
| `current_wave` | `/proposal rigor set` | Annotate which wave the change happened at |
| `review_cycles` | `/proposal debrief` | Count total review cycles for rigor summary |
| `critique_loops` | `/proposal debrief` | Count critique loops for rigor summary |

**Validation**: fit_score must be numeric 0-100. current_wave must be integer 0-9. These fields are owned by other features and must not be written by rigor commands.

---

### active-proposal (workspace-level, pre-existing)

- **Source of truth**: `.sbir/active-proposal`
- **Owner**: multi-proposal workspace feature (pre-existing)
- **Integration risk**: LOW -- rigor feature reads this to determine which proposal's rigor-profile.json to load. Standard indirection through existing workspace resolution.

**Consumed by rigor feature**: All `/proposal rigor` commands use this to find the active proposal namespace, then load `.sbir/proposals/{namespace}/rigor-profile.json`.

---

## Integration Checkpoints

### Checkpoint 1: Profile Creation at Proposal New

- **When**: `/proposal new` completes Go/No-Go with "go" decision
- **Verify**: `rigor-profile.json` exists in `.sbir/proposals/{topic-id}/` with `profile: "standard"` and empty history
- **Failure mode**: If rigor-profile.json is not created, all subsequent rigor commands fail with "file not found" instead of "no active proposal"

### Checkpoint 2: Agent Model Resolution

- **When**: Any agent is invoked during wave execution
- **Verify**: Agent reads active proposal's rigor-profile.json, looks up its role in rigor-profiles.json, and uses the specified model tier
- **Failure mode**: Agent ignores rigor and uses hardcoded model from frontmatter (outcome #12 -- highest-scoring opportunity at 16.5)
- **This is the critical integration point.** If this fails, the entire feature is a placebo.

### Checkpoint 3: Status Display Consistency

- **When**: `/proposal status` is rendered
- **Verify**: Rigor level shown for active proposal matches rigor-profile.json. Rigor level shown for other proposals matches their respective rigor-profile.json files.
- **Failure mode**: Status shows stale or wrong rigor level, breaking user trust in the display

### Checkpoint 4: Switch Preserves Per-Proposal Rigor

- **When**: `/proposal switch <topic-id>` executes
- **Verify**: After switch, rigor commands read from the target proposal's rigor-profile.json, not the previous proposal's
- **Failure mode**: Switch changes active proposal but rigor commands still read the old proposal's profile

### Checkpoint 5: History Append on Rigor Change

- **When**: `/proposal rigor set <profile>` changes the profile
- **Verify**: History array in rigor-profile.json is appended (not replaced) with from/to/timestamp/wave entry
- **Failure mode**: History lost, debrief cannot show rigor changes

### Checkpoint 6: Debrief Reads Complete History

- **When**: `/proposal debrief` renders rigor summary
- **Verify**: Debrief reads rigor-profile.json history and proposal-state.json review/critique counts. All data present and consistent.
- **Failure mode**: Debrief shows incomplete rigor summary or wrong change count

---

## Cross-Feature Dependencies

| Dependency | Direction | Risk | Notes |
|-----------|-----------|------|-------|
| Multi-proposal workspace | Rigor depends on | LOW | Rigor uses existing namespace resolution and switch mechanism |
| proposal-state.json schema | Rigor reads from | MEDIUM | Rigor reads fit_score, contract_value, current_wave. Schema changes could break suggestion logic. |
| Agent frontmatter (18 agents) | Rigor modifies behavior of | HIGH | All agents must resolve model from rigor profile instead of hardcoded frontmatter. This is the largest integration surface. |
| `/proposal status` command | Rigor extends | LOW | Status output needs a rigor field added to display. Additive change. |
| `/proposal switch` command | Rigor integrates with | LOW | Switch already loads per-proposal state. Rigor follows the same pattern. |
| `/proposal new` command | Rigor integrates with | MEDIUM | New must create rigor-profile.json and show contextual suggestion. Modifies existing flow. |
| `/proposal debrief` command | Rigor extends | LOW | Debrief output needs rigor summary section. Additive change. |
| Visual asset critique loops | Rigor controls | MEDIUM | Critique iteration cap comes from rigor profile. Visual asset agent must read this. |
| PES hooks | Rigor may interact with | LOW | PES enforcement may need to be aware of rigor settings for audit logging. |
