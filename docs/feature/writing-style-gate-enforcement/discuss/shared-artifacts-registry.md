# Shared Artifacts Registry: Writing Style Gate Enforcement

## Artifacts

### quality-preferences.json (global)

- **Source of truth**: `~/.sbir/quality-preferences.json`
- **Owner**: sbir-quality-discoverer (Phase 2: STYLE INTERVIEW)
- **Consumers**:
  - WritingStyleGateEvaluator -- existence check before allowing draft writes
  - sbir-writer style checkpoint -- reads tone, detail_level, evidence_style for recommendations
  - sbir-writer Phase 3 DRAFT -- applies preferences during section drafting
- **Integration risk**: HIGH -- this is the primary gate artifact. If the hook adapter cannot resolve ~/.sbir/ (global path) to check existence, the gate either fails open (dangerous) or fails closed (blocks everything). Unlike figure pipeline gate artifacts which live in the proposal artifact directory, this artifact is at a global path.
- **Validation**: File existence check at ~/.sbir/quality-preferences.json. PES evaluator checks via tool_context artifacts_present or a new global_artifacts_present field.

### winning-patterns.json (global)

- **Source of truth**: `~/.sbir/winning-patterns.json`
- **Owner**: sbir-quality-discoverer (Phase 1: PROPOSAL ARCHIVE MINING)
- **Consumers**:
  - sbir-writer style checkpoint -- agency-specific pattern recommendations
  - sbir-writer Phase 3 DRAFT -- applies winning practices as drafting guidance
- **Integration risk**: LOW -- used for recommendations, not gate enforcement. Missing file means no winning pattern suggestions.
- **Validation**: Optional file. Writer handles absence gracefully.

### writing-quality-profile.json (global)

- **Source of truth**: `~/.sbir/writing-quality-profile.json`
- **Owner**: sbir-quality-discoverer (Phase 3: EVALUATOR FEEDBACK EXTRACTION)
- **Consumers**:
  - sbir-writer style checkpoint -- quality alerts for current agency
  - sbir-writer Phase 3 DRAFT -- surfaces past evaluator feedback during drafting
- **Integration risk**: LOW -- used for alerts, not gate enforcement. Missing file means no quality alerts.
- **Validation**: Optional file. Writer handles absence gracefully.

### writing_style (per-proposal state field)

- **Source of truth**: `.sbir/proposals/{topic-id}/state.json` field `writing_style`
- **Owner**: sbir-writer style checkpoint (user's style choice)
- **Consumers**:
  - sbir-writer Phase 3 DRAFT -- determines which style skill to load (e.g., "elements" loads elements-of-style.md)
  - sbir-writer style checkpoint -- skips checkpoint if already set
- **Integration risk**: MEDIUM -- if set incorrectly, wrong style skill is loaded. Value must match an available style skill filename pattern.
- **Validation**: String value matching a known style identifier (elements, academic, conversational, standard, custom).

### writing_style_selection_skipped (per-proposal state field)

- **Source of truth**: `.sbir/proposals/{topic-id}/state.json` field `writing_style_selection_skipped`
- **Owner**: sbir-writer style checkpoint (user explicit skip)
- **Consumers**:
  - WritingStyleGateEvaluator -- alternative to quality-preferences.json existence
- **Integration risk**: LOW -- clear boolean field in well-known state location
- **Validation**: State field is boolean true

### pes-config.json (configuration)

- **Source of truth**: `templates/pes-config.json`
- **Owner**: Plugin maintainer
- **Consumers**:
  - JsonRuleAdapter -- loads rules including new writing style gate rule
  - EnforcementEngine -- dispatches rules to evaluators by rule_type
- **Integration risk**: HIGH -- if new rule is not added to config, evaluator is never invoked
- **Validation**: Config contains rule with rule_type "writing_style_gate"

### EnforcementEngine evaluator registry

- **Source of truth**: `scripts/pes/domain/engine.py` `_evaluators` dict
- **Owner**: Plugin maintainer
- **Consumers**:
  - EnforcementEngine._rule_triggers -- dispatches by rule_type string
- **Integration risk**: HIGH -- if new evaluator is not registered, rule in config is silently ignored
- **Validation**: Engine `_evaluators` dict contains key "writing_style_gate"

## Integration Checkpoints

1. **Global path resolution**: The writing style gate evaluator checks ~/.sbir/quality-preferences.json, a global path not relative to the proposal. The hook adapter currently resolves artifacts in the proposal artifact directory (artifacts/{topic-id}/). It must be extended to also check global artifacts at ~/.sbir/. This is the primary new integration challenge compared to the figure pipeline gate.

2. **Config-to-Engine**: The rule_type "writing_style_gate" in pes-config.json must have a corresponding WritingStyleGateEvaluator registered in the engine. A rule_type with no evaluator is silently skipped (returns False from `_rule_triggers`).

3. **State access for skip marker**: The writing style gate needs access to per-proposal state for the writing_style_selection_skipped field. State is already loaded in the engine's `evaluate()` method and passed to evaluators via the `state` parameter. Same pattern as style_analysis_skipped in the style profile gate.

4. **Writer agent checkpoint before PES gate**: The writer's style checkpoint (agent-level, Step 2) should fire BEFORE any Write attempt to wave-4-drafting/. If the checkpoint works correctly, the PES gate (Step 4) should rarely fire. The PES gate is the safety net for cases where the agent checkpoint is bypassed or malfunctions.

5. **Style skill loading**: The writing_style value in per-proposal state must match an available skill file in skills/writer/. Currently only "elements" maps to elements-of-style.md. If a user chooses a style for which no skill exists, the writer should use standard prose defaults and not error.
