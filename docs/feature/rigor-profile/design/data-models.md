# Data Models -- Rigor Profile

Feature: rigor-profile
Date: 2026-03-23
Phase: 4 -- Architecture Design

---

## rigor-profiles.json (Plugin-Level, Read-Only)

Location: `config/rigor-profiles.json`
Owner: Plugin maintainers
Created by: Plugin installation
Modified by: Plugin updates only

```json
{
  "schema_version": "1.0.0",
  "profiles": {
    "lean": {
      "description": "Fast screening with minimal cost",
      "quality_label": "Basic",
      "cost_range": "$2-5/wave",
      "agent_roles": {
        "strategist":    { "model_tier": "basic" },
        "writer":        { "model_tier": "basic" },
        "reviewer":      { "model_tier": "basic", "passes": 1 },
        "researcher":    { "model_tier": "basic" },
        "topic-scout":   { "model_tier": "basic" },
        "compliance":    { "model_tier": "basic" },
        "visual-assets": { "model_tier": "basic", "critique_iterations": 0 },
        "formatter":     { "model_tier": "basic" }
      },
      "review_passes": 1,
      "critique_max_iterations": 0,
      "iteration_cap": 1
    },
    "standard": {
      "description": "Balanced quality for most proposal work",
      "quality_label": "Balanced",
      "cost_range": "$8-15/wave",
      "agent_roles": {
        "strategist":    { "model_tier": "standard" },
        "writer":        { "model_tier": "standard" },
        "reviewer":      { "model_tier": "standard", "passes": 2 },
        "researcher":    { "model_tier": "standard" },
        "topic-scout":   { "model_tier": "standard" },
        "compliance":    { "model_tier": "standard" },
        "visual-assets": { "model_tier": "standard", "critique_iterations": 2 },
        "formatter":     { "model_tier": "standard" }
      },
      "review_passes": 2,
      "critique_max_iterations": 2,
      "iteration_cap": 2
    },
    "thorough": {
      "description": "Deep quality for must-win proposals",
      "quality_label": "Deep",
      "cost_range": "$20-35/wave",
      "agent_roles": {
        "strategist":    { "model_tier": "strongest" },
        "writer":        { "model_tier": "strongest" },
        "reviewer":      { "model_tier": "strongest", "passes": 2 },
        "researcher":    { "model_tier": "standard" },
        "topic-scout":   { "model_tier": "standard" },
        "compliance":    { "model_tier": "strongest" },
        "visual-assets": { "model_tier": "strongest", "critique_iterations": 3 },
        "formatter":     { "model_tier": "standard" }
      },
      "review_passes": 2,
      "critique_max_iterations": 3,
      "iteration_cap": 3
    },
    "exhaustive": {
      "description": "Maximum quality for critical bids",
      "quality_label": "Maximum",
      "cost_range": "$40-60/wave",
      "agent_roles": {
        "strategist":    { "model_tier": "strongest" },
        "writer":        { "model_tier": "strongest" },
        "reviewer":      { "model_tier": "strongest", "passes": 3 },
        "researcher":    { "model_tier": "strongest" },
        "topic-scout":   { "model_tier": "standard" },
        "compliance":    { "model_tier": "strongest" },
        "visual-assets": { "model_tier": "strongest", "critique_iterations": 4 },
        "formatter":     { "model_tier": "standard" }
      },
      "review_passes": 3,
      "critique_max_iterations": 4,
      "iteration_cap": 4
    }
  }
}
```

### Profile Schema Rules

- `profiles` keys are the complete valid set: lean, standard, thorough, exhaustive
- Every profile must define all 8 agent roles
- `model_tier` must be one of: basic, standard, strongest
- `passes` (reviewer) overrides `review_passes` at role level when present
- `critique_iterations` (visual-assets) overrides `critique_max_iterations` at role level
- `iteration_cap` controls writer-reviewer cycles per section
- Adding a new profile requires only a new key in `profiles` -- no code changes

### Agent Role to Agent Name Mapping

| Agent Role | Agent Name(s) | Notes |
|-----------|---------------|-------|
| strategist | sbir-strategist | Strategy brief synthesis |
| writer | sbir-writer, sbir-solution-shaper | Prose generation |
| reviewer | sbir-reviewer | Quality assurance |
| researcher | sbir-researcher | Evidence gathering |
| topic-scout | sbir-topic-scout, sbir-fit-scorer | Solicitation analysis |
| compliance | sbir-compliance-sheriff | Compliance matrix |
| visual-assets | sbir-quality-discoverer | Figure generation/critique |
| formatter | sbir-formatter | Document assembly |

Unmapped agents (use orchestrator's own model tier): sbir-orchestrator, sbir-corpus-librarian, sbir-tpoc-analyst, sbir-setup-wizard, sbir-partner-builder, sbir-profile-builder, sbir-submission-agent, sbir-debrief-analyst, sbir-continue.

---

## model-tiers.json (Plugin-Level, User-Overridable)

Location: `config/model-tiers.json` (default), `.sbir/model-tiers.json` (user override)
Owner: Plugin maintainers (default), user (override)
Resolution: `.sbir/model-tiers.json` if exists, else `config/model-tiers.json`

```json
{
  "schema_version": "1.0.0",
  "tiers": {
    "basic": {
      "model_id": "claude-haiku-4-20250506",
      "description": "Fast, cost-efficient for screening"
    },
    "standard": {
      "model_id": "claude-sonnet-4-20250514",
      "description": "Balanced capability for most work"
    },
    "strongest": {
      "model_id": "claude-opus-4-20250514",
      "description": "Maximum capability for critical proposals"
    }
  }
}
```

### Tier Schema Rules

- Three tiers required: basic, standard, strongest
- `model_id` must be a valid Claude API model identifier
- User override in `.sbir/model-tiers.json` completely replaces plugin defaults
- If user lacks Opus access, they can map "strongest" to Sonnet

---

## rigor-profile.json (Per-Proposal)

Location: `.sbir/proposals/{topic-id}/rigor-profile.json`
Owner: Rigor profile feature
Created by: `/proposal new` (default "standard")
Modified by: `/proposal rigor set <profile>`
Atomic write protocol: .tmp -> .bak -> rename

```json
{
  "schema_version": "1.0.0",
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

### Per-Proposal Schema Rules

- `profile` must be a valid key in rigor-profiles.json
- `set_at` is ISO-8601 timestamp of last change
- `history` is append-only (never truncated)
- Each history entry records: from, to, timestamp, wave number at time of change
- Default creation: `{ "profile": "standard", "set_at": "<now>", "history": [] }`
- Missing file (pre-rigor proposals) treated as `{ "profile": "standard", "history": [] }`

---

## RigorProfile Domain Value Object (PES Domain Layer)

New file: `scripts/pes/domain/rigor.py`

Frozen dataclass representing a resolved rigor configuration for a single agent dispatch. Pure domain object -- no infrastructure imports.

Fields:
- `profile_name`: str (lean/standard/thorough/exhaustive)
- `model_tier`: str (basic/standard/strongest)
- `review_passes`: int
- `critique_max_iterations`: int
- `iteration_cap`: int

Used by: rigor resolution service (application layer), suggestion service.

---

## RigorProfilePort (Driven Port)

New file: `scripts/pes/ports/rigor_port.py`

Abstract interfaces for rigor profile persistence:
- `RigorProfileReader.load(proposal_dir) -> dict` -- read per-proposal rigor selection
- `RigorProfileWriter.save(proposal_dir, data) -> None` -- write per-proposal rigor selection (atomic)
- `RigorDefinitionsReader.load_definitions() -> dict` -- read plugin-level profile definitions
- `ModelTierReader.load_tiers() -> dict` -- read tier-to-model mapping (with user override resolution)

---

## FileSystemRigorAdapter (Adapter)

New file: `scripts/pes/adapters/filesystem_rigor_adapter.py`

Implements all four port interfaces. Reads/writes JSON files. Follows existing JsonStateAdapter pattern:
- Atomic write for per-proposal file
- Plugin root resolution for definition files
- `.sbir/model-tiers.json` override detection

---

## Rigor Suggestion Thresholds

Embedded in the rigor command/skill (not in rigor-profiles.json -- these are UX logic, not profile definitions):

| Condition | Suggestion |
|-----------|-----------|
| fit_score >= 80 AND phase == "II" | Suggest "thorough" |
| fit_score < 70 AND phase == "I" | Suggest "lean" |
| Otherwise | No suggestion (standard is appropriate) |

---

## Resolution Chain Summary

```
/proposal rigor set thorough
    |
    v
rigor-profile.json              per-proposal selection
    |                            profile: "thorough"
    v
rigor-profiles.json             plugin-level definitions
    |                            thorough.agent_roles.writer.model_tier: "strongest"
    v
model-tiers.json                tier-to-model mapping
    |                            strongest.model_id: "claude-opus-4-20250514"
    v
Task tool invocation            orchestrator dispatches
                                model: "claude-opus-4-20250514"
```
