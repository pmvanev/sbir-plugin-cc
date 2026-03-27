# PES Figure Pipeline Enforcement -- Component Boundaries

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
| FigurePipelineGateEvaluator | Decides if figure-specs.md prerequisite is satisfied for a given write | Receives pre-resolved data (file_path string, artifacts_present list). No filesystem calls. |
| StyleProfileGateEvaluator | Decides if style analysis prerequisite is satisfied for a given write | Receives pre-resolved data + reads `style_analysis_skipped` from state dict. No filesystem calls. |
| EnforcementEngine | Dispatches rules to evaluators, aggregates decisions | Owns evaluator registry. Passes tool_context through to evaluators. |
| EnforcementRule | Value object for rule config | Immutable frozen dataclass. Unchanged. |

### Adapter Layer (infrastructure access allowed)

| Component | Responsibility | Boundary |
|---|---|---|
| Hook Adapter | Extracts file_path from hook input. Resolves artifact directory. Checks file existence. Builds tool_context dict. | Only place that touches filesystem for prerequisite checks. |
| JsonRuleAdapter | Loads rules from pes-config.json | Unchanged. |
| FileAuditAdapter | Writes audit entries | Unchanged. |

## Artifact Existence Resolution (Adapter Responsibility)

The hook adapter performs the following before calling `engine.evaluate()`:

1. Extract `file_path` from `hook_input["tool"]["file_path"]`
2. If file_path contains `wave-5-visuals/`, resolve the artifact directory
3. Check for prerequisite files in that directory
4. Build `tool_context = {"file_path": file_path, "artifacts_present": [...]}`

This keeps evaluators as pure decision logic operating on pre-resolved data.
