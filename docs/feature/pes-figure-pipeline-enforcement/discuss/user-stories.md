<!-- markdownlint-disable MD024 -->

# PES Figure Pipeline Enforcement -- User Stories

## US-FPIPE-01: Figure Pipeline Gate Evaluator

### Problem

Dr. Rafael Moreno is a defense tech PI writing a DoD SBIR proposal (SF25D-T1201) for autonomous sensor fusion. He relies on the plugin's formatter agent to produce professional figures for Wave 5. During his last proposal session, the formatter agent hand-coded raw inline SVGs directly into wave-5-visuals/ without first creating a figure specification plan -- skipping tool detection, the tiered generation method hierarchy, and structured critique. The resulting figures were inconsistent and looked amateurish. Markdown agent instructions ("never bypass the pipeline") were already present but the agent ignored them.

### Who

- SBIR Principal Investigator | Writing a competitive proposal under deadline pressure | Needs professional-quality figures produced through a rigorous pipeline
- Plugin Maintainer | Observing agent behavior bypass markdown instructions | Needs hard enforcement at the PES hook layer that the agent cannot override

### Solution

A new PES evaluator (FigurePipelineGateEvaluator) that blocks Write and Edit operations targeting files in wave-5-visuals/ when figure-specs.md does not exist in that directory. The evaluator allows writes to figure-specs.md itself (prerequisite creation). This ensures the formatter agent must complete Phase 1 (figure planning) before generating any figures.

### Domain Examples

#### 1: Formatter tries to write SVG without specs -- Dr. Rafael Moreno, SF25D-T1201

Dr. Rafael Moreno's proposal for topic SF25D-T1201 (autonomous sensor fusion, Air Force) is at Wave 5. The formatter agent receives the dispatch and immediately attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg" -- a hand-coded inline SVG of the system architecture. PES fires the PreToolUse hook. The FigurePipelineGateEvaluator checks: the target path contains "wave-5-visuals/", the file is not figure-specs.md, and figure-specs.md does not exist. Decision: BLOCK. The agent receives the message: "Cannot write figure files to wave-5-visuals/ before creating figure specifications. Required: artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md."

#### 2: Formatter creates figure-specs.md -- Dr. Elena Vasquez, af263-042

Dr. Elena Vasquez's Army proposal (af263-042, battlefield communications) is at Wave 5. The formatter agent correctly begins Phase 1: reads the figure plan from wave-3-outline/figure-plan.md, checks tool availability (mmdc available, dot available, no GEMINI_API_KEY), and attempts to Write "artifacts/af263-042/wave-5-visuals/figure-specs.md". PES fires PreToolUse. The evaluator sees the target IS figure-specs.md -- the prerequisite artifact itself. Decision: ALLOW.

#### 3: Formatter writes figure after specs exist -- Dr. Rafael Moreno, SF25D-T1201

After the block in Example 1, the formatter agent follows the correct workflow: creates figure-specs.md, completes style analysis (writes style-profile.yaml). Now the agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg" again. PES fires PreToolUse. The evaluator checks: figure-specs.md exists. The style profile gate also checks: style-profile.yaml exists. Both gates pass. Decision: ALLOW.

#### 4: Edit operation also blocked -- legacy workspace

A legacy single-proposal workspace (no topic-id subdirectory). The formatter attempts to Edit "artifacts/wave-5-visuals/figure-2-timeline.svg" to modify an existing figure. figure-specs.md does not exist. PES fires PreToolUse. The evaluator checks: target path contains "wave-5-visuals/", file is not figure-specs.md, figure-specs.md does not exist at "artifacts/wave-5-visuals/figure-specs.md". Decision: BLOCK.

### UAT Scenarios (BDD)

#### Scenario: Block SVG write when figure-specs.md does not exist

Given Dr. Rafael Moreno's proposal "SF25D-T1201" is at Wave 5
And "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md" does not exist
When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg"
Then PES returns decision BLOCK
And the block message includes "figure specifications"
And the block message includes the path to figure-specs.md

#### Scenario: Allow writing figure-specs.md itself

Given Dr. Elena Vasquez's proposal "af263-042" is at Wave 5
And "artifacts/af263-042/wave-5-visuals/figure-specs.md" does not exist
When the formatter agent attempts to Write "artifacts/af263-042/wave-5-visuals/figure-specs.md"
Then PES returns decision ALLOW

#### Scenario: Allow figure write after specs exist

Given Dr. Rafael Moreno's proposal "SF25D-T1201" is at Wave 5
And "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md" exists
And "artifacts/sf25d-t1201/wave-5-visuals/style-profile.yaml" exists
When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg"
Then PES returns decision ALLOW

#### Scenario: Block Edit when figure-specs.md does not exist

Given a legacy single-proposal workspace at Wave 5
And "artifacts/wave-5-visuals/figure-specs.md" does not exist
When the formatter agent attempts to Edit "artifacts/wave-5-visuals/figure-2-timeline.svg"
Then PES returns decision BLOCK

#### Scenario: Gate does not affect writes outside wave-5-visuals

Given Dr. Rafael Moreno's proposal "SF25D-T1201" is at Wave 4
When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-1.md"
Then the figure pipeline gate is not evaluated
And PES returns decision ALLOW

### Acceptance Criteria

- [ ] Writes to wave-5-visuals/ are blocked when figure-specs.md does not exist in that directory
- [ ] Writing figure-specs.md itself is always allowed (prerequisite creation)
- [ ] Both Write and Edit tool operations are subject to the gate
- [ ] Gate handles multi-proposal path layout (artifacts/{topic-id}/wave-5-visuals/)
- [ ] Gate handles legacy single-proposal path layout (artifacts/wave-5-visuals/)
- [ ] Writes to directories other than wave-5-visuals/ are not affected by this gate
- [ ] Block message includes clear guidance on what to do (create figure-specs.md first)
- [ ] Blocked and allowed decisions are recorded in the audit log

### Technical Notes

- New evaluator class: FigurePipelineGateEvaluator following existing pattern (triggers + build_block_message)
- New rule_type: "figure_pipeline_gate" registered in EnforcementEngine._evaluators
- New rule in templates/pes-config.json with rule_id "figure-pipeline-requires-specs"
- Evaluator needs file_path from hook input, not just tool_name -- the evaluator interface may need to be extended or the file_path passed via state/condition
- Artifact existence check is a filesystem operation -- evaluator needs the resolved artifact directory path
- Dependency: hook adapter must pass file_path information to the engine for these evaluators to inspect

---

## US-FPIPE-02: Style Profile Gate Evaluator

### Problem

Dr. Rafael Moreno is writing a DoD SBIR proposal (SF25D-T1201). During his last session, the formatter agent skipped style analysis entirely -- never asked about visual preferences, never looked up agency style conventions, never created a style-profile.yaml. Figures were generated with default styling that did not match Air Force visual expectations. The plugin's visual-style-intelligence skill has an agency style database, but the agent never loaded or used it because it jumped straight to figure generation.

### Who

- SBIR Principal Investigator | Has agency-specific visual expectations | Needs to be consulted about style before figures are produced
- Plugin Maintainer | Built the style intelligence skill | Needs enforcement that the style conversation happens (or is consciously skipped)

### Solution

A new PES evaluator (StyleProfileGateEvaluator) that blocks Write and Edit operations targeting figure files in wave-5-visuals/ when neither style-profile.yaml exists in that directory NOR a style_analysis_skipped marker is set in proposal state. The evaluator allows writes to style-profile.yaml itself and to figure-specs.md (which is already gated by US-FPIPE-01). This ensures the user either approves a style profile or explicitly opts out before figure generation begins.

### Domain Examples

#### 1: Figure generation blocked without style profile -- Dr. Rafael Moreno, SF25D-T1201

Dr. Moreno's proposal has figure-specs.md (Phase 1 planning complete) but no style-profile.yaml and no skip marker in state. The formatter attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg". PES fires PreToolUse. The figure pipeline gate passes (figure-specs.md exists). The StyleProfileGateEvaluator checks: style-profile.yaml does not exist at "artifacts/sf25d-t1201/wave-5-visuals/style-profile.yaml", and state does not contain style_analysis_skipped: true. Decision: BLOCK. Message: "Cannot generate figures before style analysis."

#### 2: Figure generation allowed with style profile -- Dr. Elena Vasquez, af263-042

Dr. Vasquez's Army proposal has both figure-specs.md and style-profile.yaml (she approved a military-professional palette). The formatter attempts to Write "artifacts/af263-042/wave-5-visuals/figure-1-comms-arch.svg". Both gates pass. Decision: ALLOW.

#### 3: Figure generation allowed with explicit skip -- Dr. James Park, navy-fy26-001

Dr. Park's Navy proposal has figure-specs.md but no Nano Banana figures are planned (all figures are Mermaid flowcharts). The formatter offered style analysis, Dr. Park chose "skip style analysis". The formatter recorded style_analysis_skipped: true in proposal state. The formatter attempts to Write a Mermaid-generated SVG. The style profile gate checks: style-profile.yaml does not exist, BUT state contains style_analysis_skipped: true. Decision: ALLOW.

#### 4: Writing style-profile.yaml itself is allowed

Dr. Moreno's proposal has figure-specs.md but no style-profile.yaml. The formatter runs the style conversation and attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/style-profile.yaml". The evaluator sees the target IS style-profile.yaml -- the prerequisite artifact itself. Decision: ALLOW.

### UAT Scenarios (BDD)

#### Scenario: Block figure generation without style profile or skip

Given Dr. Rafael Moreno's proposal "SF25D-T1201" is at Wave 5
And "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md" exists
And "artifacts/sf25d-t1201/wave-5-visuals/style-profile.yaml" does not exist
And the proposal state does not contain "style_analysis_skipped"
When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/figure-1-system-arch.svg"
Then PES returns decision BLOCK
And the block message includes "style analysis"

#### Scenario: Allow figure generation with style-profile.yaml present

Given Dr. Elena Vasquez's proposal "af263-042" is at Wave 5
And "artifacts/af263-042/wave-5-visuals/figure-specs.md" exists
And "artifacts/af263-042/wave-5-visuals/style-profile.yaml" exists
When the formatter agent attempts to Write "artifacts/af263-042/wave-5-visuals/figure-1-comms-arch.svg"
Then PES returns decision ALLOW

#### Scenario: Allow figure generation when user explicitly skipped style analysis

Given Dr. James Park's proposal "navy-fy26-001" is at Wave 5
And "artifacts/navy-fy26-001/wave-5-visuals/figure-specs.md" exists
And "artifacts/navy-fy26-001/wave-5-visuals/style-profile.yaml" does not exist
And the proposal state contains "style_analysis_skipped" set to true
When the formatter agent attempts to Write "artifacts/navy-fy26-001/wave-5-visuals/figure-1-flow.svg"
Then PES returns decision ALLOW

#### Scenario: Allow writing style-profile.yaml itself

Given Dr. Rafael Moreno's proposal "SF25D-T1201" is at Wave 5
And "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md" exists
And "artifacts/sf25d-t1201/wave-5-visuals/style-profile.yaml" does not exist
When the formatter agent attempts to Write "artifacts/sf25d-t1201/wave-5-visuals/style-profile.yaml"
Then PES returns decision ALLOW

#### Scenario: Block message includes guidance on completing style analysis

Given "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md" exists
And neither style-profile.yaml nor skip marker exists
When the formatter agent attempts to Write a figure file
Then the block message mentions "style-profile.yaml" as one resolution path
And the block message mentions "style analysis skip" as an alternative resolution path

### Acceptance Criteria

- [ ] Figure file writes to wave-5-visuals/ are blocked when neither style-profile.yaml exists nor style_analysis_skipped is true in state
- [ ] Writing style-profile.yaml itself is always allowed (prerequisite creation)
- [ ] Writing figure-specs.md is not affected by this gate (already gated by US-FPIPE-01)
- [ ] The skip marker (style_analysis_skipped: true in proposal state) is a valid alternative to style-profile.yaml
- [ ] Gate handles multi-proposal and legacy path layouts
- [ ] Block message includes both resolution paths (create profile OR record skip)
- [ ] Blocked and allowed decisions are recorded in the audit log

### Technical Notes

- New evaluator class: StyleProfileGateEvaluator following existing pattern
- New rule_type: "style_profile_gate" registered in EnforcementEngine._evaluators
- New rule in templates/pes-config.json with rule_id "figure-generation-requires-style"
- Evaluator reads proposal state for the style_analysis_skipped field
- Evaluator checks artifact directory for style-profile.yaml existence
- Same file_path access consideration as US-FPIPE-01 -- evaluator needs the Write/Edit target path
- Dependency: US-FPIPE-01 (figure pipeline gate must also pass for figure writes)
- The two evaluators are independent rules in config -- both are evaluated by the engine for every PreToolUse event. A figure file write must pass BOTH gates.

---

## US-FPIPE-03: Evaluator Integration with Engine and Config

### Problem

Phil, the plugin maintainer, needs the two new evaluators (FigurePipelineGateEvaluator, StyleProfileGateEvaluator) to be wired into the existing PES architecture. The engine dispatches rules to evaluators by rule_type string. If the new evaluators are not registered in the engine and the new rules are not added to pes-config.json, the enforcement is silently absent -- the engine returns ALLOW for unknown rule_types, and no block ever fires.

### Who

- Plugin Maintainer | Maintaining the PES enforcement system | Needs new evaluators to follow existing hexagonal architecture patterns exactly

### Solution

Register both new evaluators in EnforcementEngine._evaluators dict. Add two new rules to templates/pes-config.json. Ensure the evaluator interface handles the file_path information needed by these path-checking evaluators (unlike existing evaluators that only inspect tool_name and state).

### Domain Examples

#### 1: Engine dispatches figure_pipeline_gate rule to correct evaluator

Phil adds rule_type "figure_pipeline_gate" to the engine's _evaluators dict mapped to FigurePipelineGateEvaluator(). When pes-config.json contains a rule with rule_type "figure_pipeline_gate", the engine's _rule_triggers method calls evaluator.triggers(rule, state, tool_name). The evaluator receives the rule condition and can inspect the file_path to determine if the write targets wave-5-visuals/.

#### 2: Config rule structure follows existing pattern

Phil adds a new rule to pes-config.json: `{"rule_id": "figure-pipeline-requires-specs", "description": "...", "rule_type": "figure_pipeline_gate", "condition": {"target_directory": "wave-5-visuals", "required_artifact": "figure-specs.md"}, "message": "..."}`. This follows the same structure as existing rules (wave-1-requires-go, wave-5-requires-pdc-green).

#### 3: Unknown rule_type is silently ignored (existing safety behavior)

If the new evaluators are not yet registered but the rules are added to config, the engine's _rule_triggers returns False for unknown rule_types (existing behavior in engine.py line 283). This is safe degradation but means enforcement is silently absent. Integration testing must verify both registration and config.

### UAT Scenarios (BDD)

#### Scenario: Engine dispatches figure_pipeline_gate to correct evaluator

Given PES config contains a rule with rule_type "figure_pipeline_gate"
And the engine has FigurePipelineGateEvaluator registered for "figure_pipeline_gate"
When the engine evaluates a PreToolUse event
Then the FigurePipelineGateEvaluator.triggers method is called with the rule

#### Scenario: Engine dispatches style_profile_gate to correct evaluator

Given PES config contains a rule with rule_type "style_profile_gate"
And the engine has StyleProfileGateEvaluator registered for "style_profile_gate"
When the engine evaluates a PreToolUse event
Then the StyleProfileGateEvaluator.triggers method is called with the rule

#### Scenario: Both rules present in pes-config.json

Given the plugin is installed with default configuration
When the PES config is loaded from templates/pes-config.json
Then the config contains a rule with rule_id "figure-pipeline-requires-specs"
And the config contains a rule with rule_id "figure-generation-requires-style"

### Acceptance Criteria

- [ ] FigurePipelineGateEvaluator is registered in EnforcementEngine._evaluators with key "figure_pipeline_gate"
- [ ] StyleProfileGateEvaluator is registered in EnforcementEngine._evaluators with key "style_profile_gate"
- [ ] templates/pes-config.json contains rule with rule_id "figure-pipeline-requires-specs" and rule_type "figure_pipeline_gate"
- [ ] templates/pes-config.json contains rule with rule_id "figure-generation-requires-style" and rule_type "style_profile_gate"
- [ ] Evaluators follow existing interface pattern (triggers method, optional build_block_message method)
- [ ] Evaluators are pure domain objects with no infrastructure imports

### Technical Notes

- Engine _evaluators dict registration pattern: see existing entries in engine.py lines 38-44
- Config rule structure: see existing rules in templates/pes-config.json
- The evaluator interface currently passes (rule, state, tool_name) to triggers(). These new evaluators need file_path. Design decision needed: pass file_path via state dict, via an extended tool_context parameter, or via the rule condition. This is a DESIGN wave decision.
- Dependency: US-FPIPE-01, US-FPIPE-02 (the evaluators that get registered)
