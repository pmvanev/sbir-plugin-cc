# Outline Gate Enforcement -- Walking Skeleton

## Walking Skeleton Identification

**Scenario**: Writer is blocked from drafting a section when no approved outline exists

**File**: `tests/acceptance/pes_outline_gate/walking-skeleton.feature`

## Litmus Test

1. **Title describes user goal**: "Writer is blocked from drafting a section when no approved outline exists" -- describes what happens to the user (writer blocked), not technical flow.
2. **Given/When describe user actions**: Dr. Moreno's proposal at Wave 4, writer attempts to draft -- user context, not system internals.
3. **Then describe user observations**: Action is blocked, block reason explains outline needed, block recorded -- observable outcomes the PI would see.
4. **Stakeholder confirmation**: A non-technical stakeholder can confirm "yes, we need the outline to exist before drafting starts."

## What It Proves

This walking skeleton validates the simplest complete user journey through the outline gate:

1. **Config loading**: Real pes-config.json with the "drafting-requires-outline" rule loads correctly
2. **Engine dispatch**: EnforcementEngine routes outline_gate rule_type to OutlineGateEvaluator
3. **Evaluator decision**: OutlineGateEvaluator checks outline_artifacts_present and returns BLOCK
4. **Block message**: User receives actionable guidance about the missing outline
5. **Audit trail**: Decision is recorded for traceability

## Driving Port

`EnforcementEngine.evaluate(state, tool_name="Write", tool_context=...)` -- the single entry point for all PES enforcement decisions.

## Why This Scenario First

- Simplest path: one precondition (no outline), one action (write), one outcome (block)
- Exercises full vertical slice: config -> engine -> evaluator -> audit
- Matches the incident that motivated this feature (SF25D-T1201 writer fabricating structure)
- Block is the more important behavior (the whole point of the gate)
