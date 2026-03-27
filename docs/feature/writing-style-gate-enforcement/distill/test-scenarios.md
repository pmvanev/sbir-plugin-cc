# Writing Style Gate Enforcement -- Test Scenarios

## Scenario Inventory

| # | Feature File | Scenario | Category | Status |
|---|---|---|---|---|
| 1 | walking-skeleton.feature | Writer blocked from drafting when no quality preferences and no skip | Walking skeleton | Active (FAILS -- evaluator not implemented) |
| 2 | writing_style_gate.feature | Block draft write when quality-preferences.json missing and no skip marker | Gate - block | @skip |
| 3 | writing_style_gate.feature | Block Edit to existing draft when no style selection | Gate - block | @skip |
| 4 | writing_style_gate.feature | Block message includes both resolution paths | Gate - block | @skip |
| 5 | writing_style_gate.feature | Allow draft write when quality-preferences.json exists | Gate - allow | @skip |
| 6 | writing_style_gate.feature | Allow draft write when user explicitly skipped style selection | Gate - allow | @skip |
| 7 | writing_style_gate.feature | Allow writing quality-preferences.json itself | Gate - allow | @skip |
| 8 | integration_checkpoints.feature | Gate works with multi-proposal workspace path layout | Path resolution | @skip |
| 9 | integration_checkpoints.feature | Gate works with legacy single-proposal path layout | Path resolution | @skip |
| 10 | integration_checkpoints.feature | Gate does not affect writes outside wave-4-drafting | Non-interference | @skip |
| 11 | integration_checkpoints.feature | Gate does not affect Read operations | Non-interference | @skip |
| 12 | integration_checkpoints.feature | Gate does not affect writes to wave-5-visuals | Non-interference | @skip |
| 13 | integration_checkpoints.feature | Blocked draft write is recorded in audit log | Audit trail | @skip |
| 14 | integration_checkpoints.feature | Allowed draft write after style selection is recorded in audit log | Audit trail | @skip |

## Coverage Metrics

- Total scenarios: 14
- Walking skeletons: 1
- Focused scenarios: 13
- Block/error scenarios: 7 (50%)
- Allow/success scenarios: 7 (50%)
- Error path ratio: 50% (exceeds 40% target)

## Story Coverage

| Story | Scenarios | AC Covered |
|---|---|---|
| US-WSTYLE-01 (WritingStyleGateEvaluator) | #1-#9 | All 8 AC |
| US-WSTYLE-02 (Writer Style Checkpoint) | None -- markdown only, no pytest | N/A |
| US-WSTYLE-03 (Engine + Config + Hook Adapter) | #10-#14 | All 6 AC |

## Key Design Decisions

1. **global_artifacts_present in tool_context**: Unlike figure pipeline tests that use `artifacts_present` (local), writing style gate uses `global_artifacts_present` for ~/.sbir/ artifacts. Both fields included in tool_context.

2. **Skip marker key**: `writing_style_selection_skipped` in proposal state (distinct from `style_analysis_skipped` used by figure pipeline).

3. **Wave 4 base state**: All tests default to Wave 4 (drafting), not Wave 5 (visuals).

## Implementation Sequence

Enable one scenario at a time, in this order:

1. Walking skeleton (#1) -- implement WritingStyleGateEvaluator + register in engine
2. Block with Write (#2) -- verify specific file path blocking
3. Block with Edit (#3) -- verify Edit tool also blocked
4. Allow with preferences (#5) -- implement global_artifacts_present check
5. Allow with skip (#6) -- implement skip marker check
6. Allow prerequisite (#7) -- allow writing quality-preferences.json itself
7. Block message (#4) -- implement resolution path messaging
8. Multi-proposal (#8) -- verify path resolution
9. Legacy layout (#9) -- verify legacy path resolution
10. Non-interference (#10-#12) -- verify gate doesn't trigger outside scope
11. Audit trail (#13-#14) -- verify audit logging
