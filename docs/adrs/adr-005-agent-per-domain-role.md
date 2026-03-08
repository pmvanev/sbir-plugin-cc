# ADR-005: One Agent per Domain Role from Day One

## Status

Accepted

## Context

The specification defines 13 agents across all phases. Phase C1 uses 7 agents: orchestrator, corpus-librarian, compliance-sheriff, tpoc-analyst, topic-scout, fit-scorer, strategist. Some agents do relatively little in C1 (topic-scout parses a URL, fit-scorer scores one profile). The question is whether to collapse agents for the walking skeleton or define all 7 as separate files.

## Decision

Define all 7 Phase C1 agents as separate markdown files from day one. Do not collapse roles.

Agent files are cheap (markdown, 200-400 lines each). The cost of creating a focused agent file is lower than the cost of later splitting a combined agent and updating all command references.

## Alternatives Considered

### Collapsed agents (3 instead of 7)
- What: Combine topic-scout + fit-scorer into "proposal-evaluator". Combine compliance-sheriff + tpoc-analyst into "requirements-analyst".
- Expected Impact: Fewer files in C1 (3 agents instead of 7).
- Why Rejected: Creates artificial coupling. When Phase C2 adds researcher and writer agents, the collapsed agents would need to be split, requiring command rewiring. The spec clearly separates these roles with different design patterns (topic-scout is sequential, fit-scorer is react, tpoc-analyst is reflection).

### Orchestrator handles everything in C1
- What: Single orchestrator agent handles all C1 functionality. Split into specialists later.
- Expected Impact: 1 agent file for C1.
- Why Rejected: Orchestrator would exceed 400 lines. Violates nWave convention. Would be a "god agent" that combines coordination with domain expertise.

## Consequences

- **Positive:** Each agent has a clear, bounded responsibility. Single Reason to Change.
- **Positive:** No rewiring when C2 adds agents. Existing agents unchanged.
- **Positive:** Each agent loads only its relevant skills. No skill loading bloat.
- **Positive:** Agent design patterns (sequential, react, reflection) are applied correctly per role.
- **Negative:** 7 markdown files to create and maintain in C1. Acceptable overhead for clarity.
- **Negative:** Some agents are very thin in C1 (topic-scout, fit-scorer). They will grow in C2/C3.
