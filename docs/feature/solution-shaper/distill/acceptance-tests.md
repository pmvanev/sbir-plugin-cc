# Acceptance Tests -- Solution Shaper

## Scenario Inventory

| Feature File | Scenarios | Executable | Agent Behavior (@skip) |
|-------------|-----------|------------|----------------------|
| walking-skeleton.feature | 3 | 0 | 3 |
| milestone-01-approach-scoring.feature | 7 | 6 | 1 |
| milestone-01b-brief-and-structure.feature | 6 | 6 | 0 |
| milestone-02-agent-workflow.feature | 17 | 0 | 17 |
| **Total** | **33** | **12** | **21** |

Walking skeletons: 3 (all @skip @agent_behavior -- LLM-mediated workflows).
Error/edge path ratio: 14/33 = 42% (exceeds 40% target).

## Story Traceability

| Story | Scenarios | Coverage |
|-------|-----------|----------|
| US-SS-001 (Approach Generation, Scoring, Selection) | 26 | All 11 acceptance criteria covered |
| US-SS-002 (Approach Revision After New Information) | 6 | All 5 acceptance criteria covered |
| Cross-cutting (strategist integration) | 2 | Backward compatibility verified |
| Cross-cutting (file structure validation) | 3 | Agent, skill, command structure |

## Implementation Sequence

### Milestone 1: Executable Python Tests (12 scenarios)

Enable one at a time in this order:

1. Composite score reflects weighted sum (scoring model core)
2. Scoring weights always sum to 1.00 (weight validation)
3. Dimension scores are always between 0.00 and 1.00 (score range)
4. Composite score is never negative (safety invariant)
5. Scoring differentiates between approaches (differentiation)
6. Identical dimension scores produce equal composites (edge case)
7. Approach brief contains all required sections (brief schema)
8. Scoring matrix covers all approaches and dimensions (matrix structure)
9. Brief missing required section fails validation (error path)
10. Agent markdown file has required frontmatter (file structure)
11. Approach-evaluation skill file has required content (file structure)
12. Shape command file has correct dispatch configuration (file structure)

### Milestone 2: Documented Agent Behavior (21 scenarios)

Tagged @skip @agent_behavior. Validated during agent implementation by manual walkthrough. Not automated.

## Mandate Compliance Evidence

- **CM-A**: No internal component imports. Scoring steps use pure domain functions. File validation reads markdown directly. No adapter or infrastructure imports.
- **CM-B**: Zero technical terms in Gherkin. All scenarios use business language: "approach scoring", "composite score", "approach brief", "personnel alignment".
- **CM-C**: 3 walking skeletons (user value E2E) + 12 executable focused scenarios + 20 documented agent behavior scenarios.
