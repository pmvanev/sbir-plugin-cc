# ADR-024: PES Evaluator Activation via Config-Only Wiring

## Status

Proposed

## Context

Four PES evaluators (PDC gate, deadline blocking, submission immutability, corpus integrity) are fully implemented in Python, registered in the enforcement engine, and unit-tested -- but never fire because `templates/pes-config.json` contains no rules with their `rule_type` values. The evaluators are dormant.

The engine's `_rule_triggers()` dispatches by `rule_type` string match. Adding rules to the config `rules` array is sufficient to activate each evaluator. No Python code changes are needed.

The integration risk is that a typo in `rule_type` or `condition` field names would silently fail -- the evaluator would never trigger, and existing unit tests (which use fake rule loaders) would not catch the mismatch.

## Decision

Activate all 4 evaluators by adding rule entries to `templates/pes-config.json`. Close the integration gap with tests that load the real config file through `JsonRuleAdapter` and verify end-to-end rule evaluation.

No Python domain code, engine code, or adapter code will be modified.

## Alternatives Considered

### Alternative 1: Hardcode evaluators in engine (no config needed)

- **What**: Remove config-driven dispatch; always run all evaluators.
- **Why Rejected**: Violates the existing extensibility design (ADR-002). Rules should be configurable -- users may want to disable evaluators per project. Hardcoding removes that flexibility.

### Alternative 2: Feature flags in enforcement section

- **What**: Add boolean flags (`pdc_gate: true`, `deadline_blocking: true`) to the `enforcement` section instead of rule entries.
- **Why Rejected**: The engine already iterates the `rules` array. Feature flags would require a second dispatch path. The `rules` array approach is consistent with existing `wave_ordering` rules and supports per-rule condition tuning (e.g., different `critical_days` values).

### Alternative 3: Config-only, no integration tests

- **What**: Add rules, rely on existing unit tests.
- **Why Rejected**: Unit tests use fake rule loaders. A field name mismatch between config and evaluator code would not be caught. The shared artifacts registry identifies this as HIGH integration risk.

## Consequences

- **Positive**: Zero Python changes. Minimal risk of regression. Evaluators activate immediately.
- **Positive**: Integration tests prove the full pipeline (config -> adapter -> engine -> evaluator -> decision).
- **Positive**: Consistent with existing pattern (wave_ordering rules already in config).
- **Negative**: None identified. This is the simplest viable approach.
