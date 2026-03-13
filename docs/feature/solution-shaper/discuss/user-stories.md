<!-- markdownlint-disable MD024 -->

# User Stories -- Solution Shaper

Scope: Approach selection feature (pre-Wave-1 step). All stories trace to JTBD job stories in `jtbd-job-stories.md` and opportunities in `jtbd-opportunity-scores.md`.

---

## US-SS-001: Approach Generation, Scoring, and Selection

### Problem

Phil Santos is a defense tech engineer who writes 3-5 SBIR proposals per year. After making a Go decision on a solicitation topic, he jumps directly to strategy (Wave 1) without systematically evaluating what technical approach to propose. He defaults to his first idea, which works for topics in his core expertise but fails for adjacent topics where multiple viable approaches exist. The approach decision is implicit, undocumented, and impossible to reconstruct during debriefs. He recently lost a proposal where a different approach would have better leveraged his team's fiber laser experience.

### Who

- Technical founder / proposal writer | Decided to pursue a solicitation topic | Needs a systematic, evidence-backed approach selection before investing weeks in proposal writing

### Solution

An agent-driven workflow that deep-reads the solicitation, generates 3-5 candidate technical approaches, scores each against the company's specific personnel, past performance, TRL position, solicitation fit, and commercialization potential, then converges on a recommended approach with documented rationale. Produces an approach-brief.md artifact consumed by Wave 1.

### Domain Examples

#### 1: Happy Path -- Phil selects a fiber laser approach for AF243-001

Phil Santos made a Go decision on topic AF243-001 ("Compact Directed Energy for Maritime UAS Defense"). He runs `/sbir:proposal shape`. The agent reads the full solicitation (4 objectives, 40% technical merit weighting) and his company profile (Dr. Sarah Chen with 12 years fiber laser experience, AF241-087 Phase I past performance). It generates 4 approaches: fiber laser array, DPSSL, hybrid RF-optical, and direct semiconductor. Scoring shows the fiber laser array at 0.79 composite (highest personnel alignment at 0.85, strongest past performance at 0.80). Phil reviews the recommendation, sees the runner-up (hybrid at 0.68), and approves. The approach brief is written to `./artifacts/wave-0-intelligence/approach-brief.md`.

#### 2: Edge Case -- Phil overrides the recommendation for N244-012

Phil runs `/sbir:proposal shape` for topic N244-012 ("Autonomous Underwater Vehicle Navigation"). The agent generates 3 approaches and recommends inertial-acoustic fusion (0.72). But Phil knows from a recent TPOC conversation that the Navy is specifically interested in quantum sensing approaches. He selects "revise" at the checkpoint, adjusts the approach to quantum magnetometry, and the brief is regenerated with Phil's override rationale documented.

#### 3: Error/Boundary -- All approaches score low for AF243-099

Phil runs `/sbir:proposal shape` for topic AF243-099 ("Hypersonic Thermal Protection Systems"). All 4 generated approaches score below 0.40 composite -- the company has no key personnel with thermal protection expertise and no relevant past performance. The agent surfaces a warning: "All approaches scored below 0.40. Reconsider the Go decision for this topic." Phil decides to archive the proposal as No-Go.

### UAT Scenarios (BDD)

#### Scenario: Generate and score candidate approaches from solicitation and company profile

Given Phil Santos has an active proposal for topic AF243-001 with go_no_go "go"
And a company profile exists at ~/.sbir/company-profile.json with Dr. Sarah Chen (fiber laser, 12 years) and AF241-087 (fiber laser Phase I)
When Phil runs "/sbir:proposal shape"
Then the agent extracts solicitation objectives, evaluation criteria, and constraints
And generates 3-5 technically distinct candidate approaches
And scores each approach across personnel alignment, past performance, technical readiness, solicitation fit, and commercialization
And presents a ranked scoring matrix with composite scores
And recommends the highest-scoring approach with rationale

#### Scenario: Approve approach and produce approach brief

Given the agent has recommended "High-Power Fiber Laser Array" with composite score 0.79
And Phil reviews the scoring matrix and recommendation
When Phil selects "(a) approve" at the checkpoint
Then the agent writes approach-brief.md to ./artifacts/wave-0-intelligence/
And the brief contains: solicitation summary, selected approach, scoring matrix, runner-up analysis, discrimination angles, risks, and Phase III quick assessment
And proposal-state.json is updated with approach_selection.status "approved" and approach_selection.approach_name "High-Power Fiber Laser Array"

#### Scenario: Override recommendation with user's preferred approach

Given the agent has recommended "Inertial-Acoustic Fusion" for N244-012
When Phil selects "(r) revise" at the checkpoint
And Phil provides feedback "Use quantum magnetometry -- TPOC indicated Navy interest in quantum sensing"
Then the agent regenerates the approach brief with quantum magnetometry as selected approach
And documents Phil's override rationale in the brief
And presents the revised brief for another review round

#### Scenario: Low scores trigger No-Go reconsideration warning

Given Phil runs "/sbir:proposal shape" for topic AF243-099
And all generated approaches score below 0.40 composite
Then the agent displays a warning: "All approaches scored below 0.40. Reconsider the Go decision."
And suggests "/sbir:proposal status" to review Go/No-Go rationale

#### Scenario: Missing company profile blocks approach scoring

Given no company profile exists at ~/.sbir/company-profile.json
When Phil runs "/sbir:proposal shape"
Then the agent displays: "Company profile required for approach scoring"
And suggests "/sbir:company-profile setup"
And does not proceed to approach generation

#### Scenario: Narrow score spread triggers tiebreaker guidance

Given the agent has scored 3 approaches for topic N244-012
And the score spread is less than 10 percentage points (0.62 to 0.68)
Then the agent notes "Multiple viable approaches -- no clear winner by composite score"
And presents tiebreaker considerations: strongest single discriminator, lowest technical risk, most compelling narrative
And suggests using "(e) explore" to compare top approaches in depth

### Acceptance Criteria

- [ ] Agent extracts solicitation objectives, evaluation criteria, and constraints from full solicitation text
- [ ] Agent generates 3-5 technically distinct candidate approaches using forward mapping (solicitation needs), reverse mapping (company strengths), and prior art awareness
- [ ] Each approach is scored across 5 dimensions: personnel alignment (0.25), past performance (0.20), technical readiness (0.20), solicitation fit (0.20), commercialization (0.15)
- [ ] Scoring references specific data from company profile (personnel names, past performance contract IDs)
- [ ] Composite score and ranking are presented in a clear matrix
- [ ] Recommendation includes rationale, runner-up analysis, discrimination angles, risks, and Phase III quick assessment
- [ ] Human checkpoint offers approve, revise, explore, restart, and quit options
- [ ] Approved approach writes approach-brief.md to ./artifacts/wave-0-intelligence/
- [ ] Proposal state updated with approach selection status and approach name
- [ ] Low-scoring approaches trigger No-Go reconsideration warning
- [ ] Missing company profile produces actionable error, not crash

### Technical Notes

- Implemented as markdown agent (sbir-solution-shaper.md) + skill (approach-evaluation.md) + command
- Reads from: proposal-state.json (topic data, go_no_go), company-profile.json (personnel, past performance, capabilities)
- Writes to: ./artifacts/wave-0-intelligence/approach-brief.md, proposal-state.json (approach_selection)
- Scoring weights configurable in approach-evaluation skill (not hardcoded in agent)
- Depends on: US-002 (Go decision in proposal-state.json), company-profile-builder feature (company-profile.json)
- PES integration: Wave 1 gated on approach_selection.status = "approved" (extends existing wave ordering)

---

## US-SS-002: Approach Revision After New Information

### Problem

Phil Santos sometimes learns new information after selecting an approach -- a TPOC call reveals different priorities, Wave 2 research surfaces a competing approach with strong prior art, or a teaming partner brings new capabilities. He finds it disruptive to restart the entire approach selection process when only the scoring inputs have changed. Today, approach revisions are entirely mental with no documented trail.

### Who

- Technical founder / proposal writer | Mid-proposal with new information | Needs to efficiently re-evaluate the approach decision without starting over

### Solution

A revision capability that allows Phil to re-run approach scoring with updated inputs (new TPOC insights, revised company profile, or manual scoring overrides) and regenerate the approach brief. The original selection and revision rationale are both preserved.

### Domain Examples

#### 1: Happy Path -- Phil revises after TPOC call for AF243-001

Phil selected the fiber laser approach for AF243-001. Three days later, his TPOC call reveals that the Navy is specifically interested in approaches that work in degraded GPS environments. He runs `/sbir:proposal shape --revise` with the note "TPOC emphasized GPS-denied operation." The agent re-scores approaches with this new constraint. The hybrid RF-optical approach gains points on solicitation fit. The fiber laser remains top-ranked but with a closer spread. Phil re-approves the fiber laser with the GPS-denied requirement noted as a risk.

#### 2: Edge Case -- Phil revises after a teaming partner joins

Phil selected an approach for N244-012 but then secures a teaming partner (NavTech Corp) with quantum sensing expertise. He revises with updated personnel and capabilities. The quantum magnetometry approach jumps from 0.45 to 0.72 composite. Phil switches approaches and the brief is regenerated.

#### 3: Error/Boundary -- Phil revises but no original brief exists

Phil tries to run `/sbir:proposal shape --revise` but no approach brief exists yet. The tool displays: "No prior approach selection found. Run /sbir:proposal shape first."

### UAT Scenarios (BDD)

#### Scenario: Revise approach scoring with new TPOC insights

Given Phil approved "High-Power Fiber Laser Array" for AF243-001
And Phil has new TPOC insights about GPS-denied operation requirements
When Phil runs "/sbir:proposal shape --revise" with note "TPOC emphasized GPS-denied operation"
Then the agent re-scores all approaches with the new constraint
And presents the updated scoring matrix
And preserves the original selection in approach-brief.md revision history

#### Scenario: Switch approach after teaming partner joins

Given Phil approved "Inertial-Acoustic Fusion" for N244-012
And Phil has updated company-profile.json with NavTech Corp teaming partner capabilities
When Phil runs "/sbir:proposal shape --revise"
Then the agent re-scores approaches using the updated company profile
And the quantum magnetometry approach reflects the new personnel and capabilities
And Phil can approve the new top-ranked approach

#### Scenario: Revision with no prior approach selection

Given no approach-brief.md exists for the active proposal
When Phil runs "/sbir:proposal shape --revise"
Then the tool displays "No prior approach selection found"
And suggests "/sbir:proposal shape"

### Acceptance Criteria

- [ ] Revision re-scores all approaches with updated inputs (TPOC insights, revised company profile, or manual overrides)
- [ ] Original approach selection is preserved in revision history within the brief
- [ ] Updated approach brief documents the revision rationale
- [ ] Revision updates proposal-state.json with new approach if changed
- [ ] Revision without prior selection produces helpful error

### Technical Notes

- `--revise` flag on the shape command triggers revision mode
- Revision history stored as a section in approach-brief.md (append-only)
- Re-reads company-profile.json and proposal-state.json for updated inputs
- Depends on: US-SS-001 (initial approach selection must have occurred)

---

## Story Dependency Map

```
US-002 (New Proposal / Go Decision)
  |
  +-- US-SS-001 (Approach Generation, Scoring, Selection)
  |     |
  |     +-- US-SS-002 (Approach Revision After New Information)
  |     |
  |     +-- US-009 (Strategy Brief) -- reads approach-brief.md
  |
  +-- company-profile-builder feature -- provides company-profile.json
```

---

## Story Sizing Summary

| Story | Scenarios | Est. Days | Right-Sized? |
|-------|-----------|-----------|-------------|
| US-SS-001 | 6 | 2-3 | Yes |
| US-SS-002 | 3 | 1-2 | Yes |

Total: 9 scenarios, 3-5 days estimated effort.
