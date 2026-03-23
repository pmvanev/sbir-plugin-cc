# Requirements -- Rigor Profile

Feature: rigor-profile
Date: 2026-03-23
Phase: 3 -- Requirements Crafting
Traces to: jtbd-job-stories.md, jtbd-four-forces.md, jtbd-opportunity-scores.md

---

## Scope Summary

The rigor profile is a quality/cost dial that lets SBIR proposal authors configure how hard the plugin works on each proposal. It controls model tier, review depth, critique loop iterations, and iteration caps across all 18 agents and 10 waves. It does not add new waves or artifacts -- it changes how existing waves execute.

### MVP (Phase 1)

Jobs addressed: J1 (Right-Size Quality), J2 (Control Costs), J6 (Understand What Rigor Changes)

Three capabilities:

1. Named profiles with transparent configuration
2. Enforcement mechanism ensuring agents respect the active profile
3. Safe mutability so rigor can change without losing work

### Phase 2

Job addressed: J4 (Manage Multiple Proposals at Different Priority Levels)

One capability: per-proposal rigor differentiation integrated into multi-proposal workspace dashboard and switch.

### Deferred

Jobs deferred: J3 (Fast Iteration), J5 (Recover Quality -- per-section overrides)

---

## Functional Requirements

### FR-01: Named Rigor Profiles

**Traces to**: J6 (Understand), J1 (Right-Size), J2 (Control Costs)
**Opportunity outcomes**: #1 (time to determine tradeoff), #4 (understand config), #7 (time to select), #8 (minimize decisions)

The system provides four named rigor profiles: lean, standard, thorough, exhaustive. Each profile defines model tier per agent role, review pass count, critique loop iteration cap, and writer-reviewer iteration cap. Profile definitions are read-only plugin-level configuration, not user-editable.

**Business rules**:

- "standard" is the default for all new proposals
- Profile names are the complete set: lean, standard, thorough, exhaustive
- Each profile assigns a model tier (basic, standard, strongest) per agent role
- Agent roles are: strategist, writer, reviewer, researcher, topic-scout, compliance, visual-assets, formatter
- Profiles are ordered by quality/cost: lean < standard < thorough < exhaustive

### FR-02: Profile Comparison Display

**Traces to**: J6 (Understand)
**Opportunity outcomes**: #4 (understand config), #1 (time to determine tradeoff)

The user can view a summary comparison of all profiles showing quality level, cost range per wave, review passes, and critique iterations. The user can view a detailed breakdown of a specific profile showing model tier per agent role, review depth, critique loop limits, iteration caps, and estimated cost per wave.

**Business rules**:

- Summary comparison is the default view (progressive disclosure)
- Detail view is available on demand for a specific profile
- Cost ranges are displayed, not exact prices (model pricing changes over time)
- Agent roles are displayed, not internal agent names (users think in roles)
- The active profile is indicated in the display header

### FR-03: Profile Selection and Change

**Traces to**: J1 (Right-Size), J2 (Control Costs)
**Opportunity outcomes**: #7 (time to select), #10 (applying wrong level), #18 (change mid-proposal), #19 (no lost work)

The user can set or change the rigor profile for the active proposal at any point in the lifecycle. When changing, a diff is displayed showing what changed from the previous profile. Existing artifacts are preserved -- no automatic re-run. Rigor change applies to subsequent waves only.

**Business rules**:

- An active proposal is required (error if none)
- Profile name must be valid (error with available profiles listed if not)
- Setting the same profile is a no-op with confirmation message
- Change is metadata-only: update rigor-profile.json, no re-run triggered
- History array appended with from/to/timestamp/wave-number on every change
- Forward-application message tells the user which waves will use the new profile
- Actionable guidance offered for re-processing earlier sections if desired

### FR-04: Contextual Rigor Suggestion at Proposal Creation

**Traces to**: J6 (Understand), J1 (Right-Size), J2 (Control Costs)
**Opportunity outcomes**: #6 (not knowing feature exists), #8 (minimize decisions)

When a new proposal is created, the output includes the default rigor profile and a contextual suggestion based on proposal metadata. High fit score (>=80) and Phase II contract value suggest "thorough." Moderate fit score (<70) and Phase I suggest "lean" for exploratory screening. The suggestion is non-blocking -- the user can ignore it and proceed.

**Business rules**:

- Default profile is always "standard" regardless of suggestion
- Suggestion logic reads fit_score, contract_value, and phase from proposal-state.json
- Suggestion thresholds: fit_score >= 80 AND Phase II -> suggest thorough; fit_score < 70 AND Phase I -> suggest lean
- No blocking prompt -- suggestion is informational only
- Suggestion includes how to compare profiles (`/proposal rigor show`)

### FR-05: Agent Model Resolution from Rigor Profile

**Traces to**: J1 (Right-Size), J2 (Control Costs)
**Opportunity outcomes**: #12 (agent respects rigor -- highest at 16.5), #13 (apply across agents)

Every agent resolves its model tier from the active proposal's rigor profile, not from hardcoded frontmatter. The resolution path is: read active proposal -> read rigor-profile.json -> look up agent role in rigor-profiles.json -> use specified model tier.

**Business rules**:

- All 18 agents must participate in rigor resolution
- Agent frontmatter `model: inherit` is resolved through the rigor profile chain
- If rigor-profile.json is missing or malformed, agents fall back to "standard" profile behavior
- Reviewer agent uses the configured review pass count
- Visual assets agent uses the configured critique loop iteration cap
- Formatter agent uses the configured model tier (formatting is less sensitive to model quality)

### FR-06: Rigor Display in Wave Execution

**Traces to**: J1 (Right-Size)
**Opportunity outcomes**: #12 (agent respects rigor), #13 (apply across agents)

Wave execution output shows the active rigor level in the wave header and model tier per step. This provides evidence that rigor is active and controlling agent behavior, addressing the "placebo dial" anxiety from the Four Forces analysis.

**Business rules**:

- Wave header includes "Rigor: {profile_name}"
- Per-step progress shows model tier (basic/standard/strongest) and depth setting
- Model tier names are displayed, not specific model names (Opus, Sonnet, Haiku)

### FR-07: Rigor Display in Status Output

**Traces to**: J4 (Multi-Proposal)
**Opportunity outcomes**: #15 (see current level), #16 (track active level)

The proposal status command includes the rigor level for the active proposal and for all other proposals in the workspace portfolio view.

**Business rules**:

- Active proposal line includes "Rigor: {profile_name}"
- Other proposals in summary each include their rigor level
- Rigor is displayed alongside fit score and contract value for portfolio context

### FR-08: Rigor in Proposal Switch

**Traces to**: J4 (Multi-Proposal)
**Opportunity outcomes**: #15 (see current level)

When switching proposals, the target proposal's rigor level is loaded and displayed. Subsequent commands use the target proposal's rigor settings.

**Business rules**:

- Switch reads rigor-profile.json from the target proposal namespace
- Displayed rigor is the target proposal's profile, not the source's
- No rigor "bleed" between proposals

### FR-09: Rigor Summary in Debrief

**Traces to**: J1 (Right-Size)
**Opportunity outcomes**: #21 (review settings used), #22 (debrief informs future)

After proposal completion, the debrief includes a rigor summary showing profile used, total review cycles, critique loop statistics, and any profile changes during the lifecycle.

**Business rules**:

- Summary reads from rigor-profile.json (profile + history) and proposal-state.json (review/critique counts)
- Profile changes annotated with wave number where change occurred
- Data preserved as a feedback loop for future rigor decisions

---

## Non-Functional Requirements

### NFR-01: Rigor Resolution Latency

Rigor profile resolution must add negligible latency to agent invocation. The resolution is a file read (rigor-profile.json) plus a dictionary lookup (rigor-profiles.json). No network calls, no computation.

**Measurable**: Rigor resolution adds < 100ms to agent startup.

### NFR-02: Rigor State Durability

Rigor profile state follows the same atomic write protocol as proposal-state.json: write to .tmp, backup to .bak, rename .tmp to target. A crash during rigor change must not corrupt the file.

**Measurable**: After any interruption, rigor-profile.json is either the old value or the new value, never partial.

### NFR-03: Profile Definition Extensibility

New profiles can be added to rigor-profiles.json by plugin maintainers without code changes. Agents read profile definitions dynamically.

**Measurable**: Adding a fifth profile to rigor-profiles.json requires zero Python or markdown agent changes.

### NFR-04: Backward Compatibility

Proposals created before the rigor feature must work without modification. Missing rigor-profile.json is treated as "standard" profile.

**Measurable**: Existing proposals in `.sbir/proposals/` that lack rigor-profile.json behave identically to pre-rigor behavior.

---

## Business Rules Summary

| Rule | Description | Source |
|------|-------------|--------|
| BR-01 | Default profile is "standard" for all new proposals | FR-04, J6 Forces (habit: reduce decisions) |
| BR-02 | Valid profiles: lean, standard, thorough, exhaustive | FR-01 |
| BR-03 | Rigor change is metadata-only, no re-run | FR-03, Outcome #19 (no lost work) |
| BR-04 | All agents resolve model tier from rigor profile | FR-05, Outcome #12 (highest priority) |
| BR-05 | History is append-only, never truncated | FR-03, FR-09 |
| BR-06 | Suggestion thresholds: fit >= 80 + Phase II -> thorough; fit < 70 + Phase I -> lean | FR-04 |
| BR-07 | Missing rigor-profile.json defaults to "standard" behavior | NFR-04 |
| BR-08 | Cost ranges displayed, not exact prices | FR-02, J6 Forces (anxiety: overload) |

---

## Error Handling Requirements

| Error | Trigger | Response | Source |
|-------|---------|----------|--------|
| E1 | Unknown profile name | List available profiles, suggest `/proposal rigor show` | Journey E1 |
| E2 | No active proposal | Guide to `/proposal new` or `/proposal switch` | Journey E2 |
| E3 | Profile already active | Confirm current state, no changes made, no history entry | Journey E3 |
| E4 | Malformed rigor-profile.json | Fall back to "standard," log warning to audit | NFR-04 |
| E5 | Missing rigor-profiles.json (plugin config) | Fatal error -- plugin installation incomplete | FR-01 |

---

## Traceability Matrix

| Requirement | Job Stories | Opportunity Outcomes | Journey Steps |
|-------------|-----------|---------------------|---------------|
| FR-01 | J6, J1, J2 | #1, #4, #7, #8 | 2 |
| FR-02 | J6 | #4, #1 | 2 |
| FR-03 | J1, J2, J4 | #7, #10, #18, #19 | 2, 5 |
| FR-04 | J6, J1, J2 | #6, #8 | 1 |
| FR-05 | J1, J2 | #12, #13 | 3 |
| FR-06 | J1 | #12, #13 | 3 |
| FR-07 | J4 | #15, #16 | 4 |
| FR-08 | J4 | #15 | 4 |
| FR-09 | J1 | #21, #22 | 7 |
