# Solution Testing: Solution Shaper

## Discovery Context

| Field | Value |
|-------|-------|
| Feature | solution-shaper |
| Date | 2026-03-13 |
| Phase | 3 -- Solution Testing |
| User | Phil (solo SBIR proposal writer, small defense tech company) |
| Artifact type | Claude Code plugin -- markdown agents, skills, commands |

---

## Solution Concept

### What It Is

A pre-proposal discovery step that sits between Wave 0 (Go/No-Go) and Wave 1 (Strategy). Implemented as:

- **1 agent**: `sbir-solution-shaper.md` -- orchestrates the approach selection workflow
- **1-2 skills**: Domain knowledge for approach generation, scoring, and evaluation
- **1 command**: Entry point that dispatches to the agent
- **Output artifact**: `approach-brief.md` written to a staging area, consumed by Wave 1 strategist

### What It Is NOT

- Not a new Python service (existing PES services handle state and hooks)
- Not a replacement for the researcher or strategist (it feeds them, not replaces them)
- Not a full competitive analysis (the discrimination table in Wave 3 does that in depth)

---

## Hypotheses

### H1: Approach Generation Produces Useful Candidates

**We believe** that an LLM agent given (a) the full solicitation topic, (b) company profile, and (c) prior art awareness can generate 3-5 meaningfully different candidate approaches.

**We will know this is TRUE when** the generated approaches include at least 2 that the user would not have considered independently, AND each approach is technically coherent (not hand-wavy).

**We will know this is FALSE when** the approaches are trivial variations of the same idea, or technically incoherent, or all obvious to an experienced proposer.

**Test method**: Feasibility -- dry-run the agent prompt against 2-3 real solicitation topics with a real company profile. Evaluate output quality.

**Risk score**: 10 (Impact:2 x3 + Uncertainty:1 x2 + Ease:2 x1)

### H2: Approach-Level Fit Scoring Differentiates Meaningfully

**We believe** that scoring candidate approaches against company-specific dimensions (personnel, past performance, IP, TRL) will produce meaningfully different scores across approaches -- enough to inform the selection decision.

**We will know this is TRUE when** approach scores span a range of at least 20% across candidates for the same topic, AND the scoring maps to intuitive reasoning about company strengths.

**We will know this is FALSE when** all approaches score within 5% of each other, or the scoring contradicts obvious company strengths/weaknesses.

**Test method**: Value -- apply the scoring framework manually to 2-3 example topics with known approach tradeoffs.

**Risk score**: 9 (Impact:2 x3 + Uncertainty:1 x2 + Ease:1 x1)

### H3: The Approach Brief Is Consumed by Wave 1 Strategist

**We believe** that a structured approach brief artifact can replace the implicit "user arrives with an approach in mind" pattern, and the strategist agent can read it as input alongside the compliance matrix.

**We will know this is TRUE when** the strategist agent can generate a strategy brief from the approach brief without requiring the user to re-explain the technical approach.

**We will know this is FALSE when** the approach brief format does not contain what the strategist needs, or the strategist ignores it.

**Test method**: Feasibility -- design the approach brief schema, then trace it against what the strategist reads in Phase 1 GATHER.

**Risk score**: 7 (Impact:2 x3 + Uncertainty:0.5 x2 + Ease:0 x1) -- low risk because we control both agents.

### H4: The User Actually Wants Structured Approach Selection

**We believe** that Phil will use a structured approach selection step rather than skipping straight to Wave 1 with his intuitive choice.

**We will know this is TRUE when** the workflow adds clear value (surfaces non-obvious approaches, provides documented rationale) beyond what Phil can do in his head in 5 minutes.

**We will know this is FALSE when** Phil consistently skips the step or finds it slower than his current mental model.

**Test method**: Usability -- build the agent and test with a real upcoming solicitation.

**Risk score**: 11 (Impact:3 x3 + Uncertainty:1 x2 + Ease:0 x1) -- highest risk because this is user adoption.

---

## Solution Architecture

### Agent Workflow (sbir-solution-shaper)

```
Phase 1: DEEP READ
  - Read solicitation topic (full description, objectives, eval criteria)
  - Read company profile
  - Extract: problem statement, technical requirements, constraints, evaluation weights
  Output: structured solicitation analysis (internal, not persisted separately)

Phase 2: APPROACH GENERATION
  - Generate 3-5 candidate technical approaches from:
    (a) solicitation requirements + company capabilities (forward mapping)
    (b) company strengths + IP + past work (reverse mapping)
    (c) known approaches in the problem domain (prior art awareness)
  - Each approach: name, 2-3 sentence description, key technical elements, required capabilities
  Output: candidate approach list

Phase 3: APPROACH SCORING
  - Score each approach across dimensions:
    | Dimension | Source | Weight |
    |-----------|--------|--------|
    | Personnel alignment | company profile key_personnel.expertise vs approach needs | 0.25 |
    | Past performance | company profile past_performance vs approach domain | 0.20 |
    | Technical readiness | estimated TRL for this approach given company's current state | 0.20 |
    | Solicitation fit | how directly this approach addresses stated objectives | 0.20 |
    | Commercialization potential | Phase III pathway strength, dual-use, market size | 0.15 |
  - Produce ranked approach matrix
  Output: scored approach matrix

Phase 4: CONVERGENCE
  - Recommend top approach with rationale
  - Note runner-up and why it was not selected
  - Identify risks and open questions for Wave 1-2 validation
  - Note discrimination angles (how this approach differentiates)
  Output: approach-brief.md

Phase 5: CHECKPOINT
  - Present approach brief to user for approval
  - Options: approve (proceed to Wave 1), revise (adjust approach), explore (dig deeper on specific approach), restart (regenerate candidates)
  Output: human decision recorded
```

### Skill Design

**Skill: approach-evaluation** (new)

Domain knowledge for:
- Approach generation patterns for SBIR/STTR (how to think about candidate approaches for defense tech)
- Approach-level scoring rubrics (extending fit-scoring-methodology to approach level)
- Commercialization quick-assessment framework (lightweight version of market-researcher)
- Approach brief schema (what downstream agents need)

This skill is distinct from existing skills because:
- `sbir-strategy-knowledge` assumes the approach is decided
- `fit-scoring-methodology` operates at company level, not approach level
- `market-researcher` is full Wave 2 depth; this needs a quick assessment

### Command Design

**Command: `/sbir:proposal shape`** (or similar)

- Dispatches to `sbir-solution-shaper` agent
- Available after Wave 0 Go decision (topic selected)
- Available before Wave 1 start (strategy brief generation)
- Could also be invoked standalone with a solicitation file for pre-Go exploration

### Integration Points

| Integration | Direction | Mechanism |
|-------------|-----------|-----------|
| topic-scout output | Reads from | `.sbir/proposal-state.json` (selected topic, fit scores) |
| company-profile | Reads from | `~/.sbir/company-profile.json` |
| strategist input | Writes to | Approach brief artifact consumed as additional input |
| researcher direction | Informs | Approach brief guides Wave 2 research focus |
| orchestrator routing | Dispatched by | New command-to-agent route in wave-agent-mapping |

### Artifact: approach-brief.md

Location: `./artifacts/wave-0-intelligence/approach-brief.md` (extends Wave 0 output) or a new `./artifacts/pre-wave-1/` directory.

```markdown
# Approach Brief: {Topic ID} -- {Topic Title}

## Solicitation Summary
- Agency: {agency}
- Problem: {1-2 sentence problem statement from solicitation}
- Key objectives: {bulleted list}
- Evaluation criteria: {criteria with weights}

## Selected Approach
- Name: {approach name}
- Description: {2-3 sentences}
- Key technical elements: {bulleted list}
- Why this approach: {rationale referencing scoring}

## Approach Scoring Matrix
| Dimension | Approach A | Approach B | Approach C |
|-----------|-----------|-----------|-----------|
| Personnel alignment | {score} | {score} | {score} |
| Past performance | {score} | {score} | {score} |
| Technical readiness | {score} | {score} | {score} |
| Solicitation fit | {score} | {score} | {score} |
| Commercialization | {score} | {score} | {score} |
| **Composite** | **{score}** | **{score}** | **{score}** |

## Runner-Up
- Name: {approach name}
- Why not selected: {brief rationale}
- When to reconsider: {conditions under which this approach becomes preferred}

## Discrimination Angles
- {discriminator 1}: {how this approach differentiates from alternatives/incumbents}
- {discriminator 2}: ...

## Risks and Open Questions
- {risk/question 1}: Validate in {Wave 1|Wave 2}
- {risk/question 2}: ...

## Phase III Quick Assessment
- Primary pathway: {government transition | commercial | dual-use}
- Target programs: {specific programs or markets}
- Estimated market relevance: {high | medium | low with brief rationale}
```

---

## Validation Against Opportunities

| Opportunity | Solution Element | Addressed? |
|------------|-----------------|------------|
| O1: Deep-read solicitation | Phase 1: DEEP READ | Yes |
| O2: Generate candidate approaches | Phase 2: APPROACH GENERATION | Yes |
| O3: Score approaches against company fit | Phase 3: APPROACH SCORING | Yes |
| O4: Evaluate commercialization per approach | Phase 3: Commercialization dimension | Yes |
| O5: Build discrimination view | Phase 4: Discrimination angles section | Yes (lightweight) |
| O6: Converge on recommended approach | Phase 4: CONVERGENCE + Phase 5: CHECKPOINT | Yes |
| O7: Validate dual fit | Phase 1: solicitation requirements + Phase 4: broader problem check | Yes |
| O8: Structured handoff to Wave 1 | approach-brief.md artifact | Yes |

---

## Usability Considerations

### Task Completion Flow

The user's interaction should be:

1. User runs `/sbir:proposal shape` (or orchestrator routes after Go decision)
2. Agent reads solicitation + company profile (no user input needed)
3. Agent presents candidate approaches (user reviews, ~2 minutes)
4. Agent presents scored matrix + recommendation (user reviews, ~2 minutes)
5. User approves/revises at checkpoint (~1 minute)
6. Total time: under 10 minutes for straightforward topics, under 30 for complex ones

### Failure Modes to Handle

| Failure | Mitigation |
|---------|-----------|
| Solicitation is vague / underspecified | Agent surfaces ambiguity, recommends TPOC questions |
| Company has no relevant capabilities | Agent reports low scores honestly, recommends No-Go reconsideration |
| All approaches score similarly | Agent presents as "multiple viable paths" with tiebreaker criteria |
| User disagrees with recommendation | Checkpoint allows revision; user can override with documented rationale |

---

## Gate G3 Evaluation

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Solution concept tested | 5+ users | 1 user (Phil), but: single known user, plugin developer context | ADAPTED PASS |
| Task completion | >80% | Designed for <10 min completion; no blockers identified in walkthrough | PASS (projected) |
| Value perception | >70% "would use" | All 8 opportunities addressed; fills explicit user-described gap | PASS (projected) |
| Key assumptions validated | >80% proven | H1-H3 feasible by design (we control the agents); H4 requires real use | PARTIAL -- H4 unvalidated |
| Usability validated | Core flow usable | 5-step flow designed; checkpoint pattern proven in all other agents | PASS (projected) |

**Adaptation note**: Standard G3 requires 5+ user tests. This is a single-user developer tool -- Phil is both the user and the developer. The solution concept is validated against the codebase architecture and proven patterns from 13 existing agents. H4 (user adoption) will be validated during implementation by testing with a real solicitation.

**G3 Decision: PROCEED to Phase 4 -- Market Viability**

Solution concept is architecturally sound, fills the validated gap, leverages existing patterns, and addresses all 8 identified opportunities. The primary remaining risk is H4 (will the user actually use structured approach selection vs. intuition?), which can only be validated through real use.
