# JTBD Analysis: PES Enforcement Wiring

## Job Classification

**Job Type**: Brownfield (Job 2) -- existing evaluator code needs configuration wiring.
**Research Depth**: Lightweight -- evaluators are implemented and tested; only config rules are missing.

---

## Job Story 1: Proposal Safety Net

**When** I am deep in the proposal lifecycle making rapid changes under deadline pressure,
**I want to** be automatically prevented from actions that would compromise proposal integrity,
**so I can** work fast without worrying that I will accidentally corrupt the proposal, violate process gates, or lose historical data.

### Functional Job
Prevent destructive or invalid actions at the enforcement layer before they reach the proposal state.

### Emotional Job
Feel safe making rapid changes -- the system catches mistakes I would miss under time pressure.

### Social Job
Demonstrate to reviewers and agency evaluators that the proposal process has built-in quality controls.

### Forces Analysis
- **Push**: Manual vigilance under deadline pressure leads to mistakes -- Phil once accidentally overwrote a submitted proposal section
- **Pull**: Automatic enforcement catches errors instantly, even at 2 AM the night before deadline
- **Anxiety**: "Will PES block me when I need to work fast?" -- false positives could slow Phil down
- **Habit**: Phil currently relies on mental checklists and careful manual review before each wave transition

### Assessment
- Switch likelihood: High (PES infrastructure already exists, just needs activation)
- Key blocker: False positives creating friction
- Key enabler: Evaluators already match Phil's mental model of proposal safety rules
- Design implication: Block messages must be specific and actionable -- tell Phil exactly what to fix

---

## Job Story 2: Compliance Enforcement Confidence

**When** I am transitioning between proposal waves or recording outcomes after submission,
**I want to** know that process gates are enforced automatically by the system,
**so I can** trust that the proposal follows the required workflow and no shortcuts slip through unnoticed.

### Functional Job
Enforce wave transition prerequisites, deadline awareness, submission finality, and corpus data integrity.

### Emotional Job
Feel confident that the proposal process is rigorous -- if I reach the end, the process was followed correctly.

### Social Job
Present a clean audit trail showing systematic compliance to agency reviewers.

### Forces Analysis
- **Push**: Phil forgot to check PDC items before entering Wave 5 on a previous proposal, causing rework
- **Pull**: Automatic gate enforcement means Phil can focus on content quality, not process compliance
- **Anxiety**: "What if the system blocks me and I do not understand why?"
- **Habit**: Phil currently reviews a paper checklist at each wave transition

### Assessment
- Switch likelihood: High
- Key blocker: Opaque block messages
- Key enabler: Each evaluator maps to a real process rule Phil already follows manually
- Design implication: Every BLOCK must explain what is wrong, why it matters, and what to do next

---

## Outcome Statements

1. Minimize the likelihood of entering Wave 5 with unresolved RED PDC items
2. Minimize the likelihood of working on non-essential waves when the deadline is critically close
3. Minimize the likelihood of accidentally modifying a submitted proposal
4. Minimize the likelihood of overwriting historical win/loss outcome tags
5. Minimize the time to understand why PES blocked an action and how to resolve it
