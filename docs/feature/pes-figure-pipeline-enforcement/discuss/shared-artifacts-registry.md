# Shared Artifacts Registry: PES Figure Pipeline Enforcement

## Artifacts

### figure-specs.md

- **Source of truth**: `artifacts/{topic-id}/wave-5-visuals/figure-specs.md`
- **Owner**: sbir-formatter Phase 1 (FIGURE PLAN)
- **Consumers**:
  - FigurePipelineGateEvaluator -- existence check before allowing figure writes
  - sbir-formatter Phase 2 -- reads specifications to generate each figure
  - Cross-reference validation -- traces figures back to specifications
- **Integration risk**: HIGH -- if this artifact is missing or mislocated, the entire pipeline gate fails open or blocks all figure work
- **Validation**: File existence check at the artifact directory path. PES evaluator checks for file on disk, not in state.

### style-profile.yaml

- **Source of truth**: `artifacts/{topic-id}/wave-5-visuals/style-profile.yaml`
- **Owner**: sbir-formatter Phase 1 (style analysis conversation)
- **Consumers**:
  - StyleProfileGateEvaluator -- existence check before allowing figure generation
  - sbir-formatter Phase 2 -- reads palette, tone, avoid list for figure styling
- **Integration risk**: MEDIUM -- if missing, the style gate blocks, but the skip marker provides an alternative path
- **Validation**: File existence check OR state field check (style_analysis_skipped)

### style_analysis_skipped (state field)

- **Source of truth**: `.sbir/proposals/{topic-id}/state.json` field `style_analysis_skipped`
- **Owner**: sbir-formatter Phase 1 (user explicit skip)
- **Consumers**:
  - StyleProfileGateEvaluator -- alternative to style-profile.yaml existence
- **Integration risk**: LOW -- clear boolean field in well-known state location
- **Validation**: State field is boolean true

### figure-plan.md (upstream dependency)

- **Source of truth**: `artifacts/{topic-id}/wave-3-outline/figure-plan.md`
- **Owner**: sbir-outliner Wave 3
- **Consumers**:
  - sbir-formatter Phase 1 -- reads plan to create figure specifications
- **Integration risk**: MEDIUM -- if figure plan is missing, formatter cannot meaningfully create figure-specs.md, but this is an upstream concern (not enforced by these new evaluators)
- **Validation**: Not enforced by this feature. Formatter agent instructions already require reading the plan.

### pes-config.json (configuration)

- **Source of truth**: `templates/pes-config.json`
- **Owner**: Plugin maintainer
- **Consumers**:
  - JsonRuleAdapter -- loads rules including new figure pipeline and style profile rules
  - EnforcementEngine -- dispatches rules to evaluators by rule_type
- **Integration risk**: HIGH -- if new rules are not added to config, evaluators are never invoked
- **Validation**: Config contains rules with rule_type "figure_pipeline_gate" and "style_profile_gate"

### EnforcementEngine evaluator registry

- **Source of truth**: `scripts/pes/domain/engine.py` `_evaluators` dict
- **Owner**: Plugin maintainer
- **Consumers**:
  - EnforcementEngine._rule_triggers -- dispatches by rule_type string
- **Integration risk**: HIGH -- if new evaluators are not registered, rules in config are silently ignored
- **Validation**: Engine `_evaluators` dict contains keys "figure_pipeline_gate" and "style_profile_gate"

## Integration Checkpoints

1. **Config-to-Engine**: Every rule_type in pes-config.json must have a corresponding evaluator registered in the engine. A rule_type with no evaluator is silently skipped (returns False from `_rule_triggers`).

2. **Artifact path resolution**: Both evaluators need the artifact directory path to check file existence. This must come from the hook input (file_path of the Write/Edit tool) or from state (proposal context). The evaluators must handle both multi-proposal (`artifacts/{topic-id}/wave-5-visuals/`) and legacy (`artifacts/wave-5-visuals/`) layouts.

3. **State access**: The style profile gate needs access to proposal state for the skip marker. State is already loaded in the engine's `evaluate()` method and passed to evaluators via the `state` parameter.

4. **Tool name vs file path**: Existing evaluators check `tool_name` (e.g., `"wave_5"` in tool_name). The new evaluators need `file_path` from the hook input, which is NOT currently passed to evaluator `triggers()`. This is a design consideration for the DESIGN wave -- the evaluator interface may need the full hook context, not just tool_name.
