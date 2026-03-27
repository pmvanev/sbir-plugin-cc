# Writing Style Gate Enforcement -- Component Boundaries

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

Dependencies point inward. Evaluators are pure domain objects. Infrastructure access (filesystem, config files, global path resolution) stays in adapters.

## Component Responsibilities

### Domain Layer (no infrastructure imports)

| Component | Responsibility | Boundary |
|---|---|---|
| WritingStyleGateEvaluator | Decides if writing style selection prerequisite is satisfied for a given draft write | Receives pre-resolved data (file_path string, global_artifacts_present list). Reads `writing_style_selection_skipped` from state dict. No filesystem calls. No os.path, no pathlib. |
| EnforcementEngine | Dispatches rules to evaluators, aggregates decisions | Owns evaluator registry. Passes tool_context through to evaluators. Gains one new entry in _evaluators dict. |
| EnforcementRule | Value object for rule config | Immutable frozen dataclass. Unchanged. |

### Adapter Layer (infrastructure access allowed)

| Component | Responsibility | Boundary |
|---|---|---|
| Hook Adapter | Extracts file_path from hook input. Resolves local artifact directory for wave-5-visuals/. Resolves global artifact existence at ~/.sbir/ for wave-4-drafting/. Builds tool_context dict with both artifacts_present and global_artifacts_present. | Only place that touches filesystem for prerequisite checks. |
| JsonRuleAdapter | Loads rules from pes-config.json | Unchanged. |
| FileAuditAdapter | Writes audit entries | Unchanged. |

### Markdown Layer (agent/command behavioral changes)

| Component | Responsibility | Boundary |
|---|---|---|
| sbir-writer.md | Presents style checkpoint before first section draft. Reads quality artifacts from ~/.sbir/ for recommendations. Records writing_style or writing_style_selection_skipped in proposal state. | Agent behavioral specification only. No Python code. |
| proposal-draft.md | Lists style checkpoint as prerequisite for section drafting. | Command specification only. |

## Global Artifact Resolution (Adapter Responsibility)

The hook adapter performs the following for wave-4-drafting/ targets:

1. Extract `file_path` from `hook_input["tool"]["file_path"]`
2. If file_path contains `wave-4-drafting/`, resolve global artifact directory (`~/.sbir/`)
3. Check for `quality-preferences.json` at global path
4. Add `global_artifacts_present` list to tool_context

This keeps the evaluator as pure decision logic operating on pre-resolved data.

## Separation from Existing Gates

| Gate | Target Directory | Artifact Scope | tool_context Field |
|---|---|---|---|
| FigurePipelineGateEvaluator | wave-5-visuals/ | Local (proposal artifacts) | `artifacts_present` |
| StyleProfileGateEvaluator | wave-5-visuals/ | Local (proposal artifacts) | `artifacts_present` |
| WritingStyleGateEvaluator | wave-4-drafting/ | Global (~/.sbir/) | `global_artifacts_present` |
