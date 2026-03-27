# Writing Style Gate Enforcement -- Walking Skeleton

## Selected Skeleton

**Scenario**: "Writer is blocked from drafting a section when no quality preferences exist and style selection was not skipped"

## Why This Skeleton

This is the simplest end-to-end path that proves:
1. The `writing_style_gate` rule type is registered in the engine
2. The `WritingStyleGateEvaluator` is wired and evaluating
3. The evaluator reads `global_artifacts_present` from tool_context
4. The evaluator checks the `writing_style_selection_skipped` state marker
5. Block decisions flow through and are audited

## Current State

- **Status**: RED (expected)
- **Failure**: `AssertionError: Expected BLOCK but got ALLOW. Messages: []`
- **Root cause**: No evaluator registered for `rule_type: "writing_style_gate"` in `EnforcementEngine._evaluators`
- **Fix required**: Implement `WritingStyleGateEvaluator` and register it in the engine

## Expected Fix Path

1. Create `scripts/pes/domain/writing_style_gate.py` with `WritingStyleGateEvaluator`
2. Register `"writing_style_gate": WritingStyleGateEvaluator()` in `EnforcementEngine.__init__`
3. Walking skeleton turns GREEN

## Stakeholder Demo

> "When Dr. Moreno tries to draft a proposal section without having set up writing preferences, PES blocks the write and tells him to complete writing style selection first."

Non-technical stakeholder can confirm: yes, that is what we need.
