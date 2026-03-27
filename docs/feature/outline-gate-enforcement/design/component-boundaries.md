# Outline Gate Enforcement -- Component Boundaries

## Dependency Direction

```
Hook Adapter (driving adapter)
    |
    v
Enforcement Engine (application)
    |
    v
Evaluators (domain)
    ^
    |
Rule Loader Port <-- JsonRuleAdapter (driven adapter)
Audit Logger Port <-- FileAuditAdapter (driven adapter)
```

Dependencies point inward. Evaluators are pure domain objects. Infrastructure access (filesystem, config files) stays in adapters.

## Component Responsibilities

### Domain Layer (no infrastructure imports)

| Component | Responsibility | Boundary |
|---|---|---|
| OutlineGateEvaluator | Decides if proposal-outline.md prerequisite is satisfied for wave-4-drafting writes | Receives pre-resolved data (`outline_artifacts_present` list). No filesystem calls. No skip marker. No prerequisite creation exception. |
| EnforcementEngine | Dispatches rules to evaluators, aggregates decisions | Adds 9th evaluator to registry. No other changes. |
| EnforcementRule | Value object for rule config | Immutable frozen dataclass. Unchanged. |

### Adapter Layer (infrastructure access allowed)

| Component | Responsibility | Boundary |
|---|---|---|
| Hook Adapter | Derives wave-3-outline/ sibling path from wave-4-drafting/ target. Checks proposal-outline.md existence on disk. Passes `outline_artifacts_present` in tool_context. | Only place that touches filesystem for cross-directory prerequisite check. |
| JsonRuleAdapter | Loads rules from pes-config.json | Unchanged. |
| FileAuditAdapter | Writes audit entries | Unchanged. |

## Cross-Directory Artifact Resolution (Adapter Responsibility)

The hook adapter performs the following when wave-4-drafting/ is detected (extending existing wave-4 detection):

1. Detect `wave-4-drafting/` in normalized file_path (already done for global artifact resolution)
2. Derive sibling path: replace `wave-4-drafting` segment with `wave-3-outline`
3. Check for `proposal-outline.md` at the derived path
4. Add `outline_artifacts_present: ["proposal-outline.md"]` (or empty list) to tool_context

This keeps the evaluator as pure decision logic operating on pre-resolved data.

## Contrast with Existing Patterns

| Pattern | Example | This Feature |
|---|---|---|
| Same-directory prerequisite | FigurePipelineGateEvaluator checks wave-5-visuals/ for figure-specs.md | -- |
| Global artifact prerequisite | WritingStyleGateEvaluator checks ~/.sbir/ for quality-preferences.json | -- |
| **Cross-directory prerequisite** | -- | OutlineGateEvaluator checks wave-3-outline/ for proposal-outline.md when target is wave-4-drafting/ |
