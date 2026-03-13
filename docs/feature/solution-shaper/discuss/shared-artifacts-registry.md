# Shared Artifacts Registry -- Solution Shaper

## Registry

### topic_id

- **Source of truth**: `.sbir/proposal-state.json` (field: `topic.id`)
- **Consumers**: Solicitation deep-read display, approach brief header, approach-brief.md filename, checkpoint display
- **Owner**: topic-scout (Wave 0)
- **Integration risk**: LOW -- read-only from established state file
- **Validation**: Value must match across all solution-shaper output artifacts

### topic_title

- **Source of truth**: `.sbir/proposal-state.json` (field: `topic.title`)
- **Consumers**: Solicitation deep-read display, approach brief header, checkpoint display
- **Owner**: topic-scout (Wave 0)
- **Integration risk**: LOW -- read-only from established state file
- **Validation**: Value must match proposal-state.json exactly

### company_profile

- **Source of truth**: `~/.sbir/company-profile.json`
- **Consumers**: Approach scoring (personnel alignment, past performance, IP/capabilities), approach generation (reverse mapping from company strengths)
- **Owner**: company-profile-builder
- **Integration risk**: MEDIUM -- if company profile schema changes, scoring dimensions may break
- **Validation**: Profile must contain `key_personnel`, `past_performance`, and `capabilities` sections

### eval_criteria

- **Source of truth**: Solicitation text (parsed in Step 1: Deep Read)
- **Consumers**: Approach scoring (solicitation fit dimension), approach brief (solicitation summary section), strategy brief (Wave 1)
- **Owner**: solution-shaper (Step 1)
- **Integration risk**: MEDIUM -- downstream agents reference evaluation criteria weights
- **Validation**: Criteria weights must sum to 100%

### candidate_approaches

- **Source of truth**: Solution-shaper agent (Step 2: Generation)
- **Consumers**: Scoring matrix (Step 3), convergence recommendation (Step 4), approach brief artifact
- **Owner**: solution-shaper
- **Integration risk**: LOW -- internal to solution-shaper workflow
- **Validation**: 3-5 approaches, each with name, description, and key technical elements

### scoring_matrix

- **Source of truth**: Solution-shaper agent (Step 3: Scoring)
- **Consumers**: Convergence recommendation (Step 4), approach brief artifact, checkpoint display
- **Owner**: solution-shaper
- **Integration risk**: LOW -- internal to solution-shaper workflow
- **Validation**: All approaches scored across all 5 dimensions; composite calculated with correct weights

### selected_approach

- **Source of truth**: `./artifacts/wave-0-intelligence/approach-brief.md` (Section: Selected Approach)
- **Consumers**: Wave 1 strategist (reads approach for strategy brief), Wave 2 researcher (focuses research on selected approach), Wave 3 discrimination table (compares selected approach vs. alternatives)
- **Owner**: solution-shaper
- **Integration risk**: HIGH -- three downstream agents depend on this artifact
- **Validation**: Approach brief must exist and contain all required sections before Wave 1 can start

### checkpoint_decision

- **Source of truth**: `.sbir/proposal-state.json` (field: `approach_selection.status`)
- **Consumers**: PES wave ordering (Wave 1 gated on approach approval), status command display
- **Owner**: solution-shaper (checkpoint)
- **Integration risk**: HIGH -- Wave 1 is gated on this decision
- **Validation**: Value must be one of: approved, revised, pending

### approach_brief_path

- **Source of truth**: `./artifacts/wave-0-intelligence/approach-brief.md`
- **Consumers**: Wave 1 strategist (reads as input), Wave 2 researcher (reads for research focus), status command (displays path)
- **Owner**: solution-shaper
- **Integration risk**: HIGH -- file must exist at expected path for downstream consumption
- **Validation**: File exists, is valid markdown, contains all required sections

---

## Integration Checkpoints

### IC-1: Pre-Condition -- Wave 0 Complete

- **Check**: `proposal-state.json` has `go_no_go: "go"` and topic data populated
- **Failure**: "Wave 0 Go decision required before approach selection. Run /sbir:proposal status."
- **Severity**: BLOCKING

### IC-2: Pre-Condition -- Company Profile Available

- **Check**: `~/.sbir/company-profile.json` exists and is parseable
- **Failure**: "Company profile required for approach scoring. Run /sbir:company-profile setup."
- **Severity**: BLOCKING

### IC-3: Post-Condition -- Approach Brief Written

- **Check**: `./artifacts/wave-0-intelligence/approach-brief.md` exists with all required sections
- **Failure**: "Approach brief not found or incomplete. Solution shaper did not complete successfully."
- **Severity**: BLOCKING for Wave 1

### IC-4: Post-Condition -- State Updated

- **Check**: `proposal-state.json` updated with `approach_selection.status: "approved"` and `approach_selection.approach_name`
- **Failure**: "Proposal state not updated with approach selection. Checkpoint may not have been reached."
- **Severity**: BLOCKING for Wave 1

### IC-5: Consistency -- Approach Brief Matches State

- **Check**: The approach named in `approach-brief.md` matches `proposal-state.json.approach_selection.approach_name`
- **Failure**: "Approach brief and proposal state disagree on selected approach."
- **Severity**: HIGH (data integrity)

---

## Artifact Flow Diagram

```
~/.sbir/company-profile.json ──────────────────────────────┐
                                                            │
.sbir/proposal-state.json ──┐                               │
  topic.id                  │                               │
  topic.title               │                               │
  go_no_go: "go"            │                               │
                            ▼                               ▼
                    ┌───────────────────────────────────────────┐
                    │           SOLUTION SHAPER                  │
                    │                                           │
                    │  Step 1: Deep Read  ─→ eval_criteria      │
                    │  Step 2: Generate   ─→ candidate_approaches│
                    │  Step 3: Score      ─→ scoring_matrix     │
                    │  Step 4: Converge   ─→ selected_approach  │
                    │  Step 5: Checkpoint ─→ checkpoint_decision│
                    │                                           │
                    └────────────────┬──────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
        approach-brief.md   proposal-state.json   Wave 1 unlocked
        (wave-0-intelligence)  (approach_selection)
                    │                                │
                    ▼                                ▼
            ┌───────────┐                    ┌───────────┐
            │ Strategist │                    │ Researcher │
            │ (Wave 1)   │                    │ (Wave 2)   │
            └───────────┘                    └───────────┘
```
