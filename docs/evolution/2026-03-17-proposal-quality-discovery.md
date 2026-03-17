# Evolution: Proposal Quality Discovery

**Date**: 2026-03-17
**Feature**: proposal-quality-discovery
**Waves Completed**: DISCUSS > DESIGN > DISTILL > DELIVER

## Summary

Added a quality discovery workflow that captures institutional knowledge about proposal writing quality. A new agent (sbir-quality-discoverer) guides users through rating past proposals, capturing writing style preferences, and categorizing evaluator feedback. Produces three JSON artifacts at ~/.sbir/ consumed by downstream agents (strategist, writer, reviewer) to improve future proposals.

## Key Decisions

- **Markdown-first, no new Python code** (ADR-025): Quality discovery is entirely implemented as markdown agents, commands, and skills. The existing atomic write pattern and agent-skill-command architecture handle all needs. Zero Python production code added.
- **Dedicated agent over extending setup wizard** (ADR-025): Setup wizard already at ~180 lines. Quality discovery has its own lifecycle (initial setup, post-cycle updates, independent invocation) that doesn't fit within setup.
- **Company-level artifacts at ~/.sbir/** (ADR-026): Quality artifacts persist at company level (not per-proposal) because writing patterns transcend individual proposals.
- **Keyword-based auto-categorization** (ADR-027): Simple keyword matching separates meta-writing feedback from content feedback. No NLP library needed -- evaluator comments are short and keyword-rich.

## Components Delivered

### New Components
- `agents/sbir-quality-discoverer.md` -- 4-phase guided Q&A agent (past proposal review, style interview, feedback extraction, artifact assembly) plus update mode
- `skills/quality-discoverer/quality-discovery-domain.md` -- Domain knowledge: artifact schemas, feedback taxonomy, auto-categorization keywords, confidence thresholds
- `commands/sbir-proposal-quality-discover.md` -- Entry point for full quality discovery
- `commands/sbir-proposal-quality-update.md` -- Incremental update from Wave 9 debrief
- `commands/sbir-proposal-quality-status.md` -- Display current artifact status

### Modified Components (Additive Only)
- `agents/sbir-strategist.md` -- Reads winning-patterns.json in Phase 1 GATHER, filters by agency
- `agents/sbir-writer.md` -- Loads all three artifacts in Phase 3 DRAFT, surfaces quality alerts
- `agents/sbir-reviewer.md` -- Checks quality profile in Phases 1-2, produces [QUALITY PROFILE MATCH] findings
- `agents/sbir-debrief-analyst.md` -- Suggests quality update in Phase 4 SYNTHESIZE
- `agents/sbir-setup-wizard.md` -- Offers quality discovery after corpus setup

### Quality Artifacts Produced
- `~/.sbir/quality-preferences.json` -- Tone, detail, evidence style, organization, practices
- `~/.sbir/winning-patterns.json` -- Proposal ratings, winning practices, confidence levels
- `~/.sbir/writing-quality-profile.json` -- Categorized evaluator feedback, agency patterns

## Test Coverage

| Category | Count |
|----------|-------|
| Schema validation scenarios | 21 |
| Persistence scenarios | 13 |
| Confidence calculation scenarios | 8 |
| Downstream consumption scenarios | 11 |
| **Total** | **53 BDD acceptance tests** |

Error path coverage: 23/53 = 43% (exceeds 40% target).

## Delivery Statistics

- Roadmap steps: 9 (3 phases)
- Execution log events: 45 (5 phases x 9 steps)
- All steps: markdown-only (RED_ACCEPTANCE/RED_UNIT skipped as NOT_APPLICABLE)
- Adversarial review: APPROVED (1 low-severity defect -- agent 482 lines, 20% over 400 convention)
- Mutation testing: N/A (no Python files modified)
