# Acceptance Test Design: PES Enforcement Wiring

## Summary

23 acceptance scenarios prove that 4 dormant PES evaluators (PDC gate, deadline blocking, submission immutability, corpus integrity) are correctly wired through real pes-config.json to the enforcement engine. Tests use real services throughout -- real JsonRuleAdapter, real EnforcementEngine, real evaluators. No mocks at acceptance level.

## Scenario Inventory

| Feature File | Walking Skeletons | Happy Path | Error Path | Boundary/Edge | Total |
|---|---|---|---|---|---|
| walking-skeleton.feature | 3 | - | - | - | 3 |
| pdc_gate.feature | - | 1 | 2 | 2 | 5 |
| deadline_blocking.feature | - | 1 | 2 | 2 | 5 |
| submission_immutability.feature | - | 1 | 2 | 2 | 5 |
| corpus_integrity.feature | - | 1 | 1 | 3 | 5 |
| **Totals** | **3** | **4** | **7** | **9** | **23** |

Error + boundary ratio: 16/23 = 70% (target >= 40%)

## User Story Coverage

| Story | Scenarios | AC Covered |
|---|---|---|
| US-PEW-001 (PDC Gate) | 5 focused + 1 walking skeleton | All 5 AC |
| US-PEW-002 (Deadline Blocking) | 5 focused | All 5 AC |
| US-PEW-003 (Submission Immutability) | 5 focused + 1 walking skeleton | All 5 AC |
| US-PEW-004 (Corpus Integrity) | 5 focused + 1 walking skeleton | All 6 AC |

## Driving Port

All tests invoke through a single driving port:

- `EnforcementEngine.evaluate(state, tool_name)` -- the engine dispatches to evaluators internally

No evaluator is imported or invoked directly in any step definition.

## Implementation Sequence

All 23 scenarios are enabled and passing. The evaluators already exist and are implemented -- this feature only wires them via config. No skip/ignore markers needed.

Recommended delivery order:
1. Add 4 rules to `templates/pes-config.json` (production config)
2. Verify all 23 acceptance tests still pass against production config path
3. Update existing `tests/acceptance/conftest.py` pes_config fixture if needed

## Mandate Compliance Evidence

### CM-A: Hexagonal Boundary Enforcement
All step definition files import only:
- `pes.domain.rules.Decision` (for assertion)
- `pes.adapters.json_rule_adapter.JsonRuleAdapter` (in conftest only, to construct driving port)
- `pes.domain.engine.EnforcementEngine` (driving port)

Zero imports of: `PdcGateEvaluator`, `DeadlineBlockingEvaluator`, `SubmissionImmutabilityEvaluator`, `CorpusIntegrityEvaluator`.

### CM-B: Business Language Purity
Gherkin contains zero technical terms. All scenarios use domain language:
- "pre-draft checklist" (not pdc_status)
- "finalized" (not immutable)
- "recorded outcome" (not learning.outcome)
- "block reason" (not messages array)

### CM-C: Walking Skeleton + Focused Scenario Counts
- Walking skeletons: 3 (PDC gate block, submission immutability block, corpus integrity block)
- Focused scenarios: 20
- Ratio: 3/20 = within recommended range
