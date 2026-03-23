---
name: rigor-resolution
description: Rigor profile resolution chain, agent-role mapping, and rendering logic for the orchestrator
type: domain-knowledge
---

# Rigor Resolution

## Resolution Chain

Before dispatching any agent, resolve rigor to determine model and behavioral parameters.

### Step 1: Read Active Profile

Read `.sbir/proposals/{topic-id}/rigor-profile.json` for the active proposal.
- If file is missing, default to `"standard"`.
- Extract the `profile` field (one of: lean, standard, thorough, exhaustive).

### Step 2: Look Up Profile Definition

Read `config/rigor-profiles.json` from the plugin directory.
- Find the profile key matching the active profile name.
- This gives you the `roles` map and behavioral parameters.

### Step 3: Map Agent to Role

Use the Agent-Role Mapping table below to find the role for the target agent.
- Example: dispatching `sbir-writer` -> role is `writer`.
- Unmapped agents (not in the table) use the `orchestrator` role tier.

### Step 4: Get Model Tier

From the profile definition's `roles` object, read the tier for the resolved role.
- Example: profile `thorough`, role `writer` -> tier `strongest`.
- If tier is `null` (lean reviewer), skip dispatch of that agent entirely.

### Step 5: Resolve Tier to Model ID

Read `config/model-tiers.json` (or `.sbir/model-tiers.json` if user override exists).
- Map tier name to concrete model ID.
- Example: `strongest` -> `claude-opus-4-6-20250514`.

### Step 6: Dispatch with Model Override

Pass the resolved model ID as the `model` parameter in the Task tool invocation.

```
Task(agent: "sbir-writer", model: "claude-opus-4-6-20250514", prompt: "...")
```

### Step 7: Include Behavioral Parameters

Include these parameters from the profile definition in the task prompt:
- `review_passes`: number of reviewer passes (0 = skip review)
- `critique_max_iterations`: max critique-refine loops for visual assets
- `iteration_cap`: max writer-reviewer cycles per section

Example prompt suffix:
```
Behavioral parameters for this dispatch:
- review_passes: 2
- critique_max_iterations: 3
- iteration_cap: 2
```

---

## Agent-Role Mapping

| Role | Agent(s) |
|------|----------|
| writer | sbir-writer |
| reviewer | sbir-reviewer |
| researcher | sbir-researcher |
| strategist | sbir-strategist, sbir-solution-shaper, sbir-tpoc-analyst |
| formatter | sbir-formatter |
| orchestrator | sbir-orchestrator |
| compliance | sbir-compliance-sheriff |
| analyst | sbir-debrief-analyst, sbir-topic-scout, sbir-corpus-librarian, sbir-setup-wizard, sbir-continue, sbir-profile-builder, sbir-partner-builder, sbir-quality-discoverer, sbir-submission-agent |

**Null tier handling**: If a role's tier is `null` (e.g., reviewer in lean profile), do not dispatch that agent. Skip the review step and proceed to the next phase.

---

## Comparison Table Rendering

For `/proposal rigor show` (no profile argument), render all 4 profiles side by side.

Use tier names (basic/standard/strongest), not model IDs. Highlight the active profile with `>>`.

```
Rigor Profiles                lean        standard    thorough    exhaustive
                              ----        --------    --------    ----------
>> Active profile: standard

writer                        basic       standard    strongest   strongest
reviewer                      --          basic       standard    strongest
researcher                    basic       standard    strongest   strongest
strategist                    basic       standard    strongest   strongest
formatter                     basic       standard    standard    strongest
orchestrator                  basic       standard    standard    strongest
compliance                    basic       standard    standard    strongest
analyst                       basic       standard    standard    strongest

review_passes                 0           1           2           2
critique_max_iterations       0           2           3           3
iteration_cap                 1           2           2           2

Cost range                    $2-5/wave   $8-15/wave  $20-35/wave $40-60/wave
```

Rendering rules:
- `null` tiers display as `--` (agent skipped at this rigor level).
- Active profile column header gets `>>` marker.
- Behavioral parameters appear below the role rows, separated by a blank line.
- Cost range is informational, from the profile definition.

---

## Detail View Rendering

For `/proposal rigor show <profile>`, render the single profile in detail.

```
Rigor Profile: thorough
Description: Deep quality for must-win proposals
Cost range: $20-35/wave

Agent Roles:
  writer          strongest
  reviewer        standard
  researcher      strongest
  strategist      strongest
  formatter       standard
  orchestrator    standard
  compliance      standard
  analyst         standard

Behavioral Parameters:
  review_passes              2
  critique_max_iterations    3
  iteration_cap              2
```

If the requested profile differs from the active profile, append a diff section showing what would change:

```
Changes from current (standard -> thorough):
  writer          standard -> strongest
  researcher      standard -> strongest
  strategist      standard -> strongest
  review_passes   1 -> 2
  critique_max_iterations  2 -> 3
```

Only show roles/params that differ.

---

## Suggestion Logic

During `/proposal new`, after fit scoring and Go/No-Go, suggest a rigor profile based on context.

| Condition | Suggestion | Rationale |
|-----------|-----------|-----------|
| fit_score >= 80 AND phase == "II" | "thorough" | High-fit Phase II proposals justify deeper investment |
| fit_score < 70 AND phase == "I" | "lean" | Low-fit Phase I proposals benefit from fast screening |
| Otherwise | No suggestion | "standard" is appropriate; do not nudge |

Render suggestion as an informational note, not a forced choice:

```
Rigor: standard (default)
Tip: This is a high-fit Phase II topic. Consider `/proposal rigor set thorough` for deeper quality.
```

The user can ignore the suggestion. Do not re-suggest after initial creation.

---

## Diff Rendering

When profile changes via `/proposal rigor set <profile>`, render the diff.

Show only roles and parameters that differ between old and new profiles.

```
Rigor changed: standard -> thorough

Role changes:
  writer          standard -> strongest
  researcher      standard -> strongest
  strategist      standard -> strongest

Parameter changes:
  review_passes              1 -> 2
  critique_max_iterations    2 -> 3

Changes apply to future wave dispatches only. Already-completed waves are unaffected.
```

Rendering rules:
- Group role changes and parameter changes separately.
- If no roles changed (only params), omit the role section.
- If no params changed (only roles), omit the param section.
- Always include the "future waves only" note.
- `null` tiers in diff render as `--` (e.g., `basic -> --` means agent will be skipped).
