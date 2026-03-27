# PES Figure Pipeline Enforcement -- Walking Skeleton

## Selected Skeleton

**Scenario**: "Formatter is blocked from generating a figure when no figure specification plan exists"

## Rationale

This walking skeleton was selected because it is the simplest end-to-end path that proves the entire enforcement chain works for the new feature:

1. **Config loaded**: The pes-config.json with the new `figure-pipeline-requires-specs` rule is parsed by JsonRuleAdapter
2. **Engine dispatches**: EnforcementEngine iterates rules, finds a `figure_pipeline_gate` rule, looks up the evaluator in `_evaluators`
3. **Evaluator triggers**: FigurePipelineGateEvaluator receives the rule, state, tool_name, and tool_context; determines that `figure-specs.md` is absent from `artifacts_present`
4. **BLOCK returned**: The engine aggregates the block message and returns `EnforcementResult(decision=Decision.BLOCK)`
5. **Audit logged**: The block event is recorded in the audit trail

## Litmus Test (from test-design-mandates)

1. **Title describes user goal**: "Formatter is blocked from generating a figure when no figure specification plan exists" -- describes what happens to the user, not technical plumbing.
2. **Given/When describe user actions**: Given sets up Dr. Moreno's proposal state and artifact absence; When describes the formatter attempting to write a figure file.
3. **Then describe user observations**: User sees the action is blocked with a reason about figure specifications, and the block is audited.
4. **Stakeholder confirmable**: A PI or plugin maintainer can confirm "yes, the formatter should be blocked if no figure plan exists."

## Why Not Other Candidates

- **"Allow figure write when both gates pass"** -- less valuable as first skeleton because it only proves ALLOW (silent success). Blocking proves the evaluator actively intervenes.
- **"Block without style profile"** -- tests the second evaluator, but the figure pipeline gate is the primary gate (must pass before style gate matters).
- **"Multi-proposal path layout"** -- path resolution detail, not core enforcement value.

## Vertical Slice Coverage

| Layer | Component | Exercised |
|---|---|---|
| Config | pes-config.json (fixture) | figure-pipeline-requires-specs rule loaded |
| Adapter | JsonRuleAdapter | Parses rules into EnforcementRule objects |
| Application | EnforcementEngine.evaluate() | Dispatches to evaluator, aggregates result |
| Domain | FigurePipelineGateEvaluator.triggers() | Inspects tool_context, returns True (block) |
| Driven | InMemoryAuditLogger | Captures audit entry for assertion |
