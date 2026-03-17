# Evolution: PES Enforcement Wiring

**Date**: 2026-03-17
**Feature**: pes-enforcement-wiring
**Waves Completed**: DISCOVER > DISCUSS > DESIGN > DISTILL > DELIVER

## Summary

Activated 4 dormant PES evaluators (PDC gate, deadline blocking, submission immutability, corpus integrity) by adding rule entries to `templates/pes-config.json`. All evaluators were already implemented, registered in `engine.py`, and unit-tested -- but never fired because no rules in the config matched their `rule_type`. This was a config-only wiring change with integration tests to prove the full pipeline works end-to-end.

## Key Decisions

- **Config-only wiring, no Python changes** (ADR-024): All 4 evaluators were already implemented, imported, and dispatched in the engine. Adding JSON rule entries to `pes-config.json` was sufficient to activate them. Zero Python code modified.
- **Integration tests over acceptance tests**: Chose lightweight integration tests loading the real `pes-config.json` through `JsonRuleAdapter` into `EnforcementEngine`, rather than full BDD acceptance tests (which are the acceptance-designer's responsibility in the DISTILL wave).
- **Rejected simpler alternatives**: Config-only without integration tests was rejected due to HIGH integration risk -- a typo in `rule_type` or `condition` field would silently fail. Hardcoding evaluators in the engine was rejected because it violates the extensible config-driven design (ADR-002).

## Components Delivered

### Configuration
- `templates/pes-config.json` -- 4 new rules added to the existing `rules` array (8 rules total: 4 wave_ordering + 4 new evaluator rules):
  - `wave-5-requires-pdc-green` (rule_type: `pdc_gate`) -- blocks Wave 5 entry when any section has RED Tier 1/2 PDC items
  - `deadline-critical-blocking` (rule_type: `deadline_blocking`) -- blocks non-essential waves (2, 3) within 3 critical days of deadline
  - `submission-immutability` (rule_type: `submission_immutability`) -- blocks all tool invocations when proposal is submitted and immutable
  - `corpus-outcome-integrity` (rule_type: `corpus_integrity`) -- blocks modification of existing win/loss outcome tags (append-only)

### Integration Tests
- `tests/integration/test_pes_config_wiring.py` -- 17 integration tests verifying end-to-end wiring from real config through engine to evaluator decisions

## Test Coverage

| Category | Count |
|----------|-------|
| Acceptance tests (user stories) | 23 scenarios across 4 stories |
| Integration tests (config wiring) | 17 passed |
| **Total** | **40 tests** |

Integration test breakdown:
- Config loading: 1 test (all 8 rules loaded)
- PDC gate evaluator: 4 parametrized cases (RED tier 1, RED tier 2, all GREEN, no PDC status)
- Deadline blocking evaluator: 4 parametrized cases (wave 2 within critical, wave 3 within critical, outside critical, essential wave)
- Submission immutability evaluator: 4 parametrized cases (submitted+immutable, submitted not immutable, draft, no submission)
- Corpus integrity evaluator: 4 parametrized cases (outcome change, same outcome, no existing outcome, no outcome field)

## Roadmap Steps (2 steps, 1 phase)

1. **01-01**: Add 4 evaluator rules to pes-config.json (pdc_gate, deadline_blocking, submission_immutability, corpus_integrity)
2. **01-02**: Integration tests proving end-to-end wiring through real JsonRuleAdapter and EnforcementEngine

## User Stories

- **US-PEW-001**: PDC Gate Enforcement -- blocks Wave 5 entry when Tier 1/2 PDC items are RED (5 scenarios)
- **US-PEW-002**: Deadline Blocking Enforcement -- blocks non-essential waves within critical deadline threshold (5 scenarios)
- **US-PEW-003**: Submission Immutability Enforcement -- blocks all writes after proposal submission (5 scenarios)
- **US-PEW-004**: Corpus Integrity Enforcement -- blocks outcome tag modification on learning entries (5 scenarios)

## Discovery Artifacts

- User stories: 4 stories with 20 BDD scenarios total
- Architecture: C4 L3 component diagram (PES internals), no structural changes
- ADR-024: Config-only wiring with integration test gap closure
- Roadmap: 2 steps / 1 phase, step ratio 1.0
