# ADR-019: Pre-Proposal Approach Selection as Distinct Wave 0 Step

## Status

Accepted

## Context

After Wave 0 Go/No-Go and before Wave 1 Strategy, there is no structured step for determining WHAT technical approach to propose. The strategist assumes an approach exists; the researcher validates after the fact. The approach decision is implicit, undocumented, and impossible to reconstruct during debriefs.

Five evidence points confirm this gap:
1. No agent owns approach generation or selection
2. Strategist, researcher, and discrimination-table all reference "the approach" without generating it
3. Fit scoring stops at company level, not approach level
4. Commercialization assessment happens in Wave 2 (too late to inform approach selection)
5. User explicitly stated: "help me figure out what I should actually propose"

Design decisions required:
- Where does approach selection fit in the wave structure?
- What artifacts does it produce and where?
- Is it mandatory or optional?
- Does it require new PES enforcement rules?

## Decision

Implement approach selection as a **distinct step within Wave 0**, extending the existing wave rather than creating a new wave. Implemented as markdown artifacts (1 agent, 1 skill, 1 command) with no new Python services.

Key design choices:
- **Wave 0 extension**: Approach selection writes to `./artifacts/wave-0-intelligence/` alongside existing Wave 0 output
- **Optional but gated**: If invoked, must reach approved/skipped before Wave 1. If never invoked, Wave 1 proceeds as before.
- **Single artifact contract**: `approach-brief.md` is the integration point consumed by Wave 1-3 agents
- **Existing PES pattern**: Extends wave-ordering rule rather than adding new rule class

## Alternatives Considered

### Alternative 1: Fold into Wave 1 Strategist

- **What**: Add approach generation and scoring to the strategist agent's Phase 1 GATHER
- **Expected Impact**: Addresses ~60% of the gap (generation + scoring) without new components
- **Why Rejected**: Violates ADR-005 (one agent per domain role). The strategist's job is to frame and present the approach, not to select it. Combining selection and strategy in one agent creates a 500+ line agent and conflates two distinct cognitive tasks. The approach decision should be made before strategy framing begins, not during it.

### Alternative 2: New Wave 0.5

- **What**: Insert a new wave between Wave 0 and Wave 1 with its own number
- **Expected Impact**: Clean separation with its own wave number and artifact directory
- **Why Rejected**: Disrupts all existing wave numbering. Waves 1-9 would need renumbering or the numbering becomes non-sequential. Every reference to wave numbers in agents, commands, skills, PES rules, and documentation would need updating. The benefit (clean separation) does not justify the churn.

### Alternative 3: Standalone Tool Outside Wave Structure

- **What**: A separate command not tied to any wave, invocable at any time
- **Expected Impact**: Maximum flexibility -- user runs it whenever they want
- **Why Rejected**: Loses integration with PES enforcement and wave ordering. The approach brief would not be gated before Wave 1, meaning the strategist might generate a strategy brief without the approach brief available. Also loses the orchestrator's ability to suggest the step after Go decision.

## Consequences

### Positive
- No disruption to existing wave numbering or agent structure
- Backward compatible: proposals without approach selection proceed as before
- Single artifact (`approach-brief.md`) provides clean integration contract
- Optional-but-gated pattern prevents partial completion from confusing downstream agents
- Extends proven patterns (agent, skill, command, checkpoint) with no new architectural concepts

### Negative
- Wave 0 now has two logical steps (fit scoring + approach selection) which may confuse users expecting one step per wave
- The wave-agent-mapping skill needs an update to include solution-shaper in Wave 0
- Strategist agent needs a minor update to read approach-brief.md in Phase 1 GATHER (backward-compatible: no-op if file missing)
