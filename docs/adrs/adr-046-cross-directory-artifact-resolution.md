# ADR-046: Cross-Directory Artifact Resolution for Outline Gate

## Status

Accepted

## Context

Existing PES evaluators check artifacts in one of two scopes:
1. **Same-directory**: FigurePipelineGateEvaluator and StyleProfileGateEvaluator check wave-5-visuals/ for figure-specs.md and style-profile.yaml (ADR-044)
2. **Global**: WritingStyleGateEvaluator checks ~/.sbir/ for quality-preferences.json (ADR-045)

The new OutlineGateEvaluator needs a third scope: **cross-directory**. The target is wave-4-drafting/ but the prerequisite (proposal-outline.md) is in the sibling wave-3-outline/ directory. The evaluator is a pure domain object with no filesystem imports. The hook adapter must resolve the sibling directory path and check file existence.

Three design questions:
1. How to derive the sibling wave-3-outline/ path from a wave-4-drafting/ target
2. How to represent cross-directory artifacts in tool_context
3. Whether to generalize or keep it specific

## Decision

**Part 1 -- Path derivation**: The adapter uses the existing `_find_wave_dir()` helper to locate the wave-4-drafting/ directory in the file path, then replaces the `wave-4-drafting` segment with `wave-3-outline` to get the sibling path. This works for both multi-proposal (`artifacts/{topic-id}/wave-4-drafting/` -> `artifacts/{topic-id}/wave-3-outline/`) and legacy (`artifacts/wave-4-drafting/` -> `artifacts/wave-3-outline/`) layouts because the segment replacement is position-independent.

**Part 2 -- Separate field**: Add `outline_artifacts_present` list to `tool_context` alongside existing `artifacts_present` and `global_artifacts_present`. This keeps each artifact scope semantically distinct and avoids polluting existing fields.

**Part 3 -- Specific over general**: Use a dedicated field (`outline_artifacts_present`) rather than a generic `sibling_artifacts` dict. This feature adds one cross-directory check. Generalization can happen when a second cross-directory gate is needed.

## Alternatives Considered

### Alternative A: Generic sibling_artifacts dict

- **What**: Build a `sibling_artifacts: {"wave-3-outline": ["proposal-outline.md"]}` dict in tool_context, keyed by sibling wave directory. Evaluator looks up what it needs.
- **Expected Impact**: Would support future cross-wave gates without adapter changes.
- **Why Insufficient**: Over-engineering for one use case. Adds a dict lookup pattern different from the flat lists used by all other evaluators. YAGNI -- generalize when a second cross-directory gate arrives.

### Alternative B: Extend artifacts_present with cross-directory prefixes

- **What**: Add entries like `"wave-3-outline/proposal-outline.md"` to the existing `artifacts_present` list.
- **Expected Impact**: No new field. Evaluator pattern-matches on the prefix.
- **Why Insufficient**: Conflates same-directory and cross-directory artifacts in a single list. Existing evaluators (FigurePipelineGateEvaluator, StyleProfileGateEvaluator) check for bare filenames like `"figure-specs.md"` -- adding prefixed entries changes the contract. Evaluator must parse directory prefixes, coupling it to path conventions.

### Alternative C: Evaluator resolves path via injected port

- **What**: Create a `SiblingArtifactPort` injected into the evaluator. Evaluator calls `port.exists("wave-3-outline", "proposal-outline.md")`.
- **Expected Impact**: Keeps resolution logic in the evaluator, testable via port mock.
- **Why Insufficient**: Breaks the established pattern where all evaluators receive pre-resolved data as plain values in tool_context (ADR-044). Requires constructor injection, changing the simple `_evaluators` dict registration pattern. Over-complicated for a boolean check.

## Consequences

- Positive: Evaluator remains pure domain -- no filesystem imports
- Positive: Existing `artifacts_present` and `global_artifacts_present` fields unaffected
- Positive: Adapter leverages existing `_find_wave_dir()` and wave-4 detection code
- Positive: Path derivation works identically for multi-proposal and legacy layouts
- Negative: Hook adapter gains a third resolution path (same-directory, global, cross-directory) -- acceptable given low rate of new gates
- Negative: Dedicated field name (`outline_artifacts_present`) is specific -- would need renaming if generalized later
