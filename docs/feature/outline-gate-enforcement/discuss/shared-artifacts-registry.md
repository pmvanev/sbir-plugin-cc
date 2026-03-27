# Shared Artifacts Registry: Outline Gate Enforcement

## Artifacts

### proposal-outline.md

- **Source of truth**: `artifacts/{topic-id}/wave-3-outline/proposal-outline.md`
- **Owner**: sbir-outliner Wave 3
- **Consumers**:
  - OutlineGateEvaluator -- existence check in sibling wave-3-outline/ directory before allowing wave-4-drafting/ writes
  - sbir-writer Wave 4 -- reads outline for section structure, page budgets, compliance mapping, thesis statements, discrimination table
- **Integration risk**: HIGH -- if this artifact is missing or mislocated, the gate blocks all drafting work. If the gate is not wired, drafting proceeds without the outline and fabricated structure results.
- **Validation**: File existence check at the sibling wave-3-outline/ directory path. PES evaluator checks for file on disk, not in state.

### pes-config.json (configuration)

- **Source of truth**: `templates/pes-config.json`
- **Owner**: Plugin maintainer
- **Consumers**:
  - JsonRuleAdapter -- loads rules including new outline gate rule
  - EnforcementEngine -- dispatches rules to evaluators by rule_type
- **Integration risk**: HIGH -- if the new rule is not added to config, the evaluator is never invoked
- **Validation**: Config contains a rule with rule_type "outline_gate"

### EnforcementEngine evaluator registry

- **Source of truth**: `scripts/pes/domain/engine.py` `_evaluators` dict
- **Owner**: Plugin maintainer
- **Consumers**:
  - EnforcementEngine._rule_triggers -- dispatches by rule_type string
- **Integration risk**: HIGH -- if new evaluator is not registered, the rule in config is silently ignored
- **Validation**: Engine `_evaluators` dict contains key "outline_gate"

## Cross-Directory Resolution

This feature introduces a new pattern: **cross-directory artifact check**. Unlike the FigurePipelineGateEvaluator (which checks for figure-specs.md in the same wave-5-visuals/ directory), the OutlineGateEvaluator checks for proposal-outline.md in a **sibling** wave directory.

### Path Derivation

| Target Path | Prerequisite Path |
|-------------|-------------------|
| `artifacts/{topic-id}/wave-4-drafting/` | `artifacts/{topic-id}/wave-3-outline/proposal-outline.md` |
| `artifacts/wave-4-drafting/` (legacy) | `artifacts/wave-3-outline/proposal-outline.md` |

The adapter replaces the wave directory component (`wave-4-drafting`) with the prerequisite wave directory (`wave-3-outline`) in the same parent directory.

### Adapter Responsibility

This is an adapter concern (infrastructure), not domain. The evaluator receives information about whether proposal-outline.md exists. The adapter is responsible for:
1. Detecting that the target path contains `wave-4-drafting/`
2. Deriving the sibling `wave-3-outline/` path
3. Checking if `proposal-outline.md` exists at that path
4. Passing the result to the evaluator

## Integration Checkpoints

1. **Config-to-Engine**: The rule_type "outline_gate" in pes-config.json must have a corresponding evaluator registered in the engine. A rule_type with no evaluator is silently skipped.

2. **Cross-directory path resolution**: The adapter must derive the wave-3-outline/ path from the wave-4-drafting/ target path. This must work for both multi-proposal (`artifacts/{topic-id}/wave-4-drafting/`) and legacy (`artifacts/wave-4-drafting/`) layouts.

3. **Tool name vs file path**: The evaluator needs file_path from the hook input to determine if the write targets wave-4-drafting/. This is the same interface consideration raised in the figure pipeline gate feature -- the evaluator needs the full hook context, not just tool_name.
