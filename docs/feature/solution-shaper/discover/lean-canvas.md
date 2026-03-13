# Lean Canvas: Solution Shaper

## Discovery Context

| Field | Value |
|-------|-------|
| Feature | solution-shaper |
| Date | 2026-03-13 |
| Phase | 4 -- Market Viability |
| User | Phil (solo SBIR proposal writer, small defense tech company) |
| Product type | Feature within an existing Claude Code plugin (not standalone product) |

---

## Lean Canvas

### 1. Problem

Top 3 problems (validated in Phase 1):

1. **No structured approach selection**: After picking a solicitation (Wave 0 Go), the user jumps to strategy (Wave 1) without systematically evaluating what technical approach to propose. The approach decision is implicit and undocumented.

2. **Company fit stops at company level**: The topic-scout scores whether the company fits the topic, but does not evaluate which of several possible approaches best leverages the company's specific personnel, past performance, and IP.

3. **Commercialization assessment is too late**: TAM/SAM/SOM and Phase III pathway analysis happens in Wave 2, after the approach is already decided in Wave 1. Different approaches to the same problem can have dramatically different commercialization potential.

### 2. Customer Segments

**Primary segment (by JTBD)**: Solo SBIR proposal writers at small defense tech companies who need to make a defensible approach selection decision for each solicitation they pursue.

**Segment characteristics**:
- Writes 3-5 SBIR proposals per year
- Technical founder who is also the proposal writer
- Company has 10-50 employees with diverse technical capabilities
- Pursues topics adjacent to (not always squarely in) core expertise
- Values speed but also values documented rationale for approach decisions

### 3. Unique Value Proposition

**Turn "what should we propose?" from a gut decision into a structured, scored, documented recommendation in under 10 minutes.**

The solution-shaper is the only step in the SBIR proposal workflow that generates and evaluates candidate approaches against company-specific capabilities before committing to a strategy.

### 4. Solution

Top 3 features for top 3 problems:

| Problem | Feature |
|---------|---------|
| No structured approach selection | Agent-driven approach generation + scoring workflow producing approach-brief.md |
| Company fit at approach level | Approach-level fit matrix scoring personnel, past performance, TRL, and solicitation fit per candidate |
| Commercialization too late | Quick commercialization assessment per approach as a scoring dimension (before Wave 2 deep dive) |

### 5. Channels

**Path to user**: This is a feature within an existing Claude Code plugin. The channel is:
- Plugin command: `/sbir:proposal shape` (or equivalent)
- Orchestrator integration: automatically suggested or dispatched after Wave 0 Go decision
- Documentation in plugin README / command help

No external distribution channel needed -- the user already has the plugin installed.

### 6. Revenue Streams

**N/A** -- This is an open-source Claude Code plugin feature. No direct monetization.

**Indirect value**: Every proposal Phil writes generates $50K-$750K in SBIR awards if won. Improving the approach selection step improves win probability, which directly improves revenue for Phil's company. The feature pays for itself if it contributes to even a single additional win over time.

### 7. Cost Structure

**Development cost**: Markdown agent + skill + command authoring. No new Python services required.
- Agent: `sbir-solution-shaper.md` (~200-400 lines)
- Skill: `approach-evaluation.md` (~100-200 lines)
- Command: YAML frontmatter + dispatch (~30-50 lines)
- Integration: Update `wave-agent-mapping.md`, orchestrator routing
- Tests: Integration scenarios (BDD features)

**Estimated effort**: Small feature -- comparable to company-profile-builder or topic-scout.

**Ongoing cost**: Maintenance as the plugin evolves. The agent reads company-profile.json and proposal-state.json -- if those schemas change, the agent may need updates.

### 8. Key Metrics

| Metric | Target | How Measured |
|--------|--------|-------------|
| Approach generation quality | 3+ distinct, technically coherent approaches per topic | Manual review of output |
| Scoring differentiation | 20%+ spread across candidates | Score variance in approach matrix |
| Time to approach selection | Under 10 minutes for standard topics | Wall-clock time from command to checkpoint |
| Downstream consumption | Strategist uses approach brief without re-asking user | Check if Wave 1 strategy brief references approach brief |
| User adoption | Phil uses the step for at least 3 of next 5 proposals | Usage count |

### 9. Unfair Advantage

**Integration with the full proposal lifecycle**: The solution-shaper is not a standalone tool -- it reads the company profile, reads the scored solicitation, and feeds the strategist. This contextual integration is what makes it valuable. A generic "help me brainstorm approaches" tool cannot leverage the company-specific scoring.

**Existing domain knowledge**: The plugin already encodes SBIR domain expertise in 20+ skill files and 13 agents. The solution-shaper skill inherits this knowledge base.

---

## 4 Big Risks Assessment

### Value Risk: Will the user want this?

| Signal | Assessment |
|--------|-----------|
| User explicitly described the gap | Strong positive signal |
| Gap confirmed by codebase structural analysis | Strong positive signal |
| User currently makes approach decisions implicitly | Confirms workaround exists |
| Risk: user may prefer intuition over structured process | Moderate risk -- mitigated by making the step fast (<10 min) and skippable |

**Verdict**: GREEN -- the user asked for this capability in their own words.

### Usability Risk: Can the user use this?

| Signal | Assessment |
|--------|-----------|
| Same interaction pattern as all other agents (read, generate, checkpoint) | Low risk |
| 5-step flow with clear checkpoint | Consistent with existing UX |
| No new concepts -- approach scoring extends familiar fit scoring | Low risk |
| Risk: output may be too long or verbose | Moderate risk -- keep approach brief concise |

**Verdict**: GREEN -- follows proven patterns from 13 existing agents.

### Feasibility Risk: Can we build this?

| Signal | Assessment |
|--------|-----------|
| Markdown agent/skill/command -- same as all other features | Low risk |
| No new Python services required | Low risk |
| Reads existing data structures (company profile, proposal state) | Low risk |
| LLM approach generation quality is the main technical unknown | Moderate risk -- but LLM reasoning about technical approaches is a core LLM strength |
| Risk: approach scoring rubric may need iteration | Low risk -- can adjust skill file without code changes |

**Verdict**: GREEN -- architecture is proven, implementation is markdown.

### Viability Risk: Does this work for the business?

| Signal | Assessment |
|--------|-----------|
| Open-source plugin, no revenue model needed | N/A for direct viability |
| Development cost is small (markdown artifacts) | Low cost risk |
| Maintenance cost is proportional to existing agents | Sustainable |
| Indirect value: better approach selection -> higher win rate -> real revenue | Strong alignment |
| Risk: feature adds complexity to an already 10-wave workflow | Moderate risk -- mitigated by making it optional and lightweight |

**Verdict**: GREEN -- low cost, high indirect value, sustainable maintenance.

---

## Phase 4 Completion Checklist

- [x] G1: Problem validated (5 evidence sources, 100% confirmation)
- [x] G2: Opportunities prioritized (8 opportunities, top 3 scored 19/18/17)
- [x] G3: Solution tested (concept validated against codebase architecture and proven agent patterns; H4 deferred to implementation)
- [x] G4: Viability confirmed (all 4 risks GREEN, Lean Canvas complete)

---

## Go / No-Go Decision

**Decision: GO**

**Rationale**:
1. The problem is real and explicitly stated by the user
2. The structural gap in the workflow is confirmed by codebase analysis
3. The solution leverages proven patterns (markdown agents, skills, commands, checkpoints)
4. All four risks are GREEN
5. Development cost is small (markdown artifacts, no new Python services)
6. The feature fills the last major gap in the pre-proposal workflow (company profile -> solicitation scoring -> [approach selection] -> strategy)

**Open items for design phase**:
- Exact command name and routing (`/sbir:proposal shape` vs. alternative)
- Whether solution-shaper is a new "Wave 0.5" or extends Wave 0
- Approach brief artifact location (`wave-0-intelligence/` vs. new directory)
- Whether the orchestrator auto-dispatches after Go or the user invokes manually
- Skill file structure: single skill vs. split into approach-generation and approach-scoring
- Integration with PES hooks: does the approach brief need state tracking?

**Recommended next step**: Hand off to product-owner for DISCUSS wave -- user stories, journey mapping, and architectural design decisions.
