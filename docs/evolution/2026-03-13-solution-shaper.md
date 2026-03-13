# Evolution: Solution Shaper

**Date**: 2026-03-13
**Feature**: solution-shaper
**Waves Completed**: DISCOVER > DISCUSS > DESIGN > DISTILL > DELIVER

## Summary

Implemented the Solution Shaper feature: a pre-strategy approach selection step that sits between Wave 0 (Go/No-Go) and Wave 1 (Strategy). Deep-reads the solicitation, generates 3-5 candidate technical approaches, scores each against company-specific dimensions, converges on a recommendation, and checkpoints for human approval. Produces `approach-brief.md` consumed by Wave 1+ agents.

## Key Decisions

- **Wave 0 extension, not new wave** (ADR-019): Approach selection extends Wave 0 rather than creating a new wave. Avoids disrupting existing wave numbering.
- **Single skill file**: approach-evaluation.md covers generation patterns, scoring rubrics, brief schema, and commercialization quick-assessment in one file (~240 lines). Within guidelines; splitting would create artificial boundaries.
- **Five-dimension scoring model**: Personnel alignment (0.25), Past performance (0.20), Technical readiness (0.20), Solicitation fit (0.20), Commercialization potential (0.15).
- **Markdown-only implementation**: No new Python services. Feature is 1 agent + 1 skill + 1 command + 2 integration updates.
- **Backward compatible strategist integration**: Strategist reads approach-brief.md when available, proceeds without it for existing proposals.

## Components Delivered

### Agent
- `agents/sbir-solution-shaper.md` -- 5-phase workflow: DEEP READ, APPROACH GENERATION, APPROACH SCORING, CONVERGENCE, CHECKPOINT. Supports revision mode via `--revise` flag.

### Skill
- `skills/solution-shaper/approach-evaluation.md` -- Scoring dimension rubrics with configurable weights, three generation patterns (forward/reverse/prior-art), commercialization quick-assessment framework, approach-brief.md schema.

### Command
- `commands/sbir-proposal-shape.md` -- `/proposal shape` and `/proposal shape --revise`. Dispatches to @sbir-solution-shaper.

### Integration Updates
- `skills/orchestrator/wave-agent-mapping.md` -- Solution-shaper added to Wave 0 agents, command routing table, and checkpoint definitions.
- `agents/sbir-strategist.md` -- Phase 1 GATHER updated to read approach-brief.md when available (backward compatible).

## Test Coverage

| Category | Count |
|----------|-------|
| Acceptance tests (scoring model) | 7 passed |
| Acceptance tests (brief schema/structure) | 5 passed |
| Walking skeletons | 1 skipped (tiebreaker -- agent behavior) |
| **Total** | **12 passed, 1 skipped** |

## Roadmap Steps (4 steps, 2 phases)

1. **01-01**: Solution-shaper agent with 5-phase approach selection workflow
2. **01-02**: Approach-evaluation skill with scoring rubrics and brief schema
3. **01-03**: Shape command with revise flag and agent dispatch
4. **02-01**: Wave-agent-mapping update and strategist integration

## Discovery Artifacts

- Problem validation: 5 evidence sources, 100% confirmation
- Opportunity tree: 8 opportunities, top 3 scored 19/18/17
- Lean Canvas: All 4 risks GREEN, GO decision
- JTBD: 6 job stories, 4 forces mapped, 8 outcomes scored
- User stories: US-SS-001 (6 scenarios), US-SS-002 (3 scenarios)
- Architecture: C4 L1/L2 diagrams, ADR-019
