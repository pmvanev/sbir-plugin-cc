# Requirements -- Solution Shaper

## Business Context

The solution-shaper fills a structural gap in the SBIR proposal plugin workflow between Wave 0 (Go/No-Go decision) and Wave 1 (Strategy). No agent currently owns the question "what should we actually propose?" The approach decision is implicit, undocumented, and impossible to reconstruct during debriefs.

### Business Rules

1. **Approach selection is optional but recommended**: Phil can skip directly to Wave 1 if he already knows his approach. The solution-shaper is not a hard prerequisite for Wave 1 unless the user has invoked it (in which case, approval is required before proceeding).

2. **Scoring dimensions are configurable**: Weights for the 5 scoring dimensions (personnel 0.25, past performance 0.20, technical readiness 0.20, solicitation fit 0.20, commercialization 0.15) are defined in the approach-evaluation skill, not hardcoded. They can be adjusted per proposal or per agency emphasis.

3. **Approach brief is the contract artifact**: The approach-brief.md is the single artifact consumed by downstream agents. Its schema is the integration contract between solution-shaper and Wave 1-3 agents.

4. **Checkpoint pattern is mandatory**: No approach selection is final without human approval at the checkpoint. The agent recommends; the human decides.

5. **Revision preserves history**: When an approach is revised, the original selection and rationale are preserved in the brief. Revisions are append-only.

---

## Functional Requirements

### FR-1: Solicitation Deep Read

The agent extracts from the full solicitation text:
- Problem statement (1-2 sentences)
- Key objectives (bulleted list)
- Evaluation criteria with weights
- Technical constraints (ITAR, TRL range, SWaP requirements)
- Format requirements (page limits, font, margins)
- Ambiguities flagged for TPOC questions

Example: For AF243-001, extraction yields 4 objectives, evaluation weights (40/30/20/10), ITAR restriction, TRL 3-5 requirement, 200 lb weight limit, and 3 ambiguities.

### FR-2: Candidate Approach Generation

The agent generates 3-5 technically distinct approaches using three methods:
1. **Forward mapping**: Solicitation requirements + known technical approaches in the domain
2. **Reverse mapping**: Company capabilities, IP, and personnel expertise mapped to possible approaches
3. **Prior art awareness**: Known approaches from the problem domain, including emerging/non-obvious combinations

Each approach includes: name, 2-3 sentence description, key technical elements, and required capabilities.

Example: For AF243-001, generation produces fiber laser array, DPSSL, hybrid RF-optical, and direct semiconductor -- four distinct technical paths to the same solicitation objective.

### FR-3: Approach-Level Scoring

Each candidate approach is scored against 5 dimensions:

| Dimension | Weight | Source |
|-----------|--------|--------|
| Personnel alignment | 0.25 | company-profile.json key_personnel.expertise vs. approach needs |
| Past performance | 0.20 | company-profile.json past_performance vs. approach domain |
| Technical readiness | 0.20 | Estimated TRL for this approach given company's current state |
| Solicitation fit | 0.20 | How directly this approach addresses stated objectives |
| Commercialization | 0.15 | Phase III pathway strength, dual-use potential, market size |

Scores are 0.00-1.00 per dimension. Composite is weighted sum. Scoring references specific company data (personnel names, contract numbers) for traceability.

Example: Fiber laser scores 0.85 on personnel (Dr. Sarah Chen, 12 years), 0.80 on past performance (AF241-087), 0.70 on TRL, 0.80 on solicitation fit, 0.75 on commercialization. Composite: 0.79.

### FR-4: Convergence and Recommendation

The agent produces a structured recommendation containing:
- Selected approach name and rationale
- Runner-up with rationale for non-selection and conditions for reconsideration
- Discrimination angles (3+) for Wave 3 discrimination table
- Risks and open questions assigned to Wave 1-2 for validation
- Phase III quick assessment (pathway, target programs, market relevance)

### FR-5: Human Checkpoint

Checkpoint follows existing plugin pattern:
- Options: approve, revise, explore, restart, quit
- Approve: writes approach-brief.md and updates proposal-state.json
- Revise: accepts feedback, regenerates brief, re-presents
- Explore: deep-dive on a specific approach (additional detail, risks, trade study)
- Restart: regenerate candidate approaches from scratch
- Quit: save state and exit

### FR-6: Approach Brief Artifact

Written to `./artifacts/wave-0-intelligence/approach-brief.md` with sections:
- Solicitation Summary (agency, problem, objectives, eval criteria)
- Selected Approach (name, description, technical elements, rationale)
- Approach Scoring Matrix (all approaches x all dimensions)
- Runner-Up (name, why not selected, when to reconsider)
- Discrimination Angles (for Wave 3)
- Risks and Open Questions (assigned to validation wave)
- Phase III Quick Assessment (pathway, target programs, market relevance)

### FR-7: Approach Revision

Revision mode (`--revise` flag) allows re-scoring with updated inputs:
- New TPOC insights (text input)
- Updated company profile (re-reads company-profile.json)
- Manual scoring overrides (user adjusts specific dimension scores)

Original selection preserved in revision history section of approach-brief.md.

---

## Non-Functional Requirements

### NFR-1: Performance

- Solicitation deep read and approach generation complete within 60 seconds
- Scoring matrix computed within 30 seconds
- First output (solicitation analysis) visible within 5 seconds of command invocation

### NFR-2: CLI UX Compliance

- All output follows existing plugin checkpoint pattern (consistent with Wave 0-10 agents)
- NO_COLOR environment variable respected
- Error messages follow what/why/what-to-do pattern
- Progressive disclosure: default output shows summary; `--verbose` shows full scoring detail

### NFR-3: Data Safety

- Approach brief written atomically (write to temp, rename)
- Proposal state updated atomically (existing pattern)
- No company profile data leaves the local machine

### NFR-4: Graceful Degradation

- Missing company profile: blocks with actionable error (not crash)
- Missing proposal state: blocks with actionable error
- Vague solicitation: proceeds with ambiguity warnings, suggests TPOC questions
- Low scores across all approaches: warns about Go reconsideration, does not force No-Go

---

## Domain Glossary

| Term | Definition |
|------|-----------|
| Approach | A specific technical path to addressing a solicitation's stated problem. Distinct from "strategy" (which is how to present the approach in a proposal). |
| Approach Brief | The structured markdown artifact produced by the solution-shaper, consumed by downstream agents. |
| Composite Score | Weighted sum of dimension scores for a candidate approach (0.00-1.00). |
| Discrimination Angle | A specific way the selected approach differentiates from alternatives or incumbents. |
| Forward Mapping | Generating approaches from solicitation requirements (need → solution). |
| Reverse Mapping | Generating approaches from company capabilities (strength → application). |
| Phase III Pathway | The commercialization plan for transitioning SBIR research into production or commercial use. |
| Runner-Up | The second-highest-scoring approach, documented with conditions for reconsideration. |
| Scoring Dimension | One of 5 evaluation axes: personnel alignment, past performance, technical readiness, solicitation fit, commercialization. |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| LLM generates trivial/incoherent approaches | Medium | High | Approach-evaluation skill encodes domain-specific generation patterns; user checkpoint catches bad output |
| Scoring dimensions do not differentiate meaningfully | Low | Medium | Test with 2-3 real solicitations during implementation; adjust weights if spread < 20% |
| Phil skips the step for most proposals | Medium | Medium | Make the step fast (<10 min) and skippable; prove value on first real use |
| Approach brief schema does not match what strategist needs | Low | Low | We control both agents; iterate schema during implementation |
| Company profile lacks data for meaningful scoring | Low | Medium | Validation check at start; graceful degradation for missing fields |

---

## Traceability Matrix

| Requirement | Job Story | Opportunity | User Story | Scenario |
|------------|-----------|-------------|------------|----------|
| FR-1 | JS-1 | O1 (13) | US-SS-001 | Scenario 1 |
| FR-2 | JS-2 | O2 (18) | US-SS-001 | Scenario 1 |
| FR-3 | JS-3 | O3 (19) | US-SS-001 | Scenario 1 |
| FR-4 | JS-5 | O5 (17), O6 (13) | US-SS-001 | Scenario 2 |
| FR-5 | JS-5 | O5 (17) | US-SS-001 | Scenarios 2, 3 |
| FR-6 | JS-6 | O7 (11) | US-SS-001 | Scenario 2 |
| FR-7 | JS-5 | O8 (12) | US-SS-002 | Scenarios 1, 2 |
| NFR-1 | -- | -- | US-SS-001 | (property) |
| NFR-2 | -- | -- | US-SS-001 | (property) |
| NFR-3 | -- | -- | US-SS-001 | (property) |
| NFR-4 | -- | -- | US-SS-001 | Scenarios 4, 5, 6 |
