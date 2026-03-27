<!-- markdownlint-disable MD024 -->

# Writing Style Gate Enforcement -- User Stories

## US-WSTYLE-01: Writing Style Gate Evaluator

### Problem

Dr. Rafael Moreno is a defense tech PI writing a DoD SBIR proposal (SF25D-T1201) for autonomous sensor fusion. He relies on the plugin's writer agent to draft all proposal sections in Wave 4. During his last proposal session, the writer agent drafted every section without consulting him about writing style. It never asked about preferred tone, never loaded the Elements of Style skill, never surfaced winning patterns from his proposal corpus, and never checked evaluator feedback from past submissions. The quality discovery system exists and produces artifacts at ~/.sbir/ (quality-preferences.json, winning-patterns.json, writing-quality-profile.json), but the writer treats these as optional -- "when available" with graceful degradation means the agent never blocks on missing artifacts and never prompts the user to create them.

### Who

- SBIR Principal Investigator | Writing a competitive proposal with strong style preferences | Needs assurance that style selection happens before any drafting
- Plugin Maintainer | Observed writer agent ignoring quality discovery artifacts during real test | Needs hard enforcement at the PES hook layer that the agent cannot override

### Solution

A new PES evaluator (WritingStyleGateEvaluator) that blocks Write and Edit operations targeting files in wave-4-drafting/ when quality-preferences.json does not exist at ~/.sbir/ AND the per-proposal state does not contain writing_style_selection_skipped: true. This ensures the user either runs quality discovery or explicitly skips style selection before any section drafting begins.

### Domain Examples

#### 1: Writer tries to draft without quality preferences -- Dr. Rafael Moreno, SF25D-T1201

Dr. Rafael Moreno's proposal for topic SF25D-T1201 (autonomous sensor fusion, Air Force) is at Wave 4. The writer agent receives the dispatch and begins drafting the technical approach. It attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md". PES fires the PreToolUse hook. The WritingStyleGateEvaluator checks: the target path contains "wave-4-drafting/", quality-preferences.json does not exist at ~/.sbir/, and proposal state does not contain writing_style_selection_skipped: true. Decision: BLOCK. The agent receives the message: "Cannot write draft sections to wave-4-drafting/ before writing style selection. Run /proposal quality discover or skip style selection at the style checkpoint."

#### 2: Writer drafts with quality preferences present -- Dr. Elena Vasquez, af263-042

Dr. Elena Vasquez previously ran quality discovery for her company. ~/.sbir/quality-preferences.json exists with tone: "formal", detail_level: "high", evidence_style: "narrative". Her Army proposal (af263-042, battlefield communications) is at Wave 4. The writer attempts to Write "artifacts/af263-042/wave-4-drafting/sections/technical-approach.md". PES fires PreToolUse. The evaluator checks: quality-preferences.json exists at ~/.sbir/. Decision: ALLOW.

#### 3: Writer drafts after explicit skip -- Dr. Amara Okafor, navy-fy26-003

Dr. Amara Okafor is a first-time SBIR user with no quality profile. Her Navy proposal (navy-fy26-003) is at Wave 4. The writer's style checkpoint presented options; Dr. Okafor chose "skip style selection." The writer recorded writing_style_selection_skipped: true in proposal state. The writer attempts to Write "artifacts/navy-fy26-003/wave-4-drafting/sections/technical-approach.md". PES fires PreToolUse. The evaluator checks: quality-preferences.json does not exist, BUT state contains writing_style_selection_skipped: true. Decision: ALLOW.

#### 4: Edit operation also blocked -- legacy workspace

A legacy single-proposal workspace (no topic-id subdirectory). The writer attempts to Edit "artifacts/wave-4-drafting/sections/technical-approach.md" to revise a section. quality-preferences.json does not exist at ~/.sbir/ and no skip marker in state. PES fires PreToolUse. The evaluator checks: target path contains "wave-4-drafting/", quality-preferences.json absent, no skip marker. Decision: BLOCK.

### UAT Scenarios (BDD)

#### Scenario: Block draft write when quality-preferences.json missing and no skip

Given Dr. Rafael Moreno's proposal "SF25D-T1201" is at Wave 4
And "~/.sbir/quality-preferences.json" does not exist
And the proposal state does not contain "writing_style_selection_skipped"
When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/sections/technical-approach.md"
Then PES returns decision BLOCK
And the block message includes "writing style selection"
And the block message includes "quality-preferences.json"

#### Scenario: Allow draft write when quality-preferences.json exists

Given Dr. Elena Vasquez's proposal "af263-042" is at Wave 4
And "~/.sbir/quality-preferences.json" exists
When the writer agent attempts to Write "artifacts/af263-042/wave-4-drafting/sections/technical-approach.md"
Then PES returns decision ALLOW

#### Scenario: Allow draft write when user explicitly skipped style selection

Given Dr. Amara Okafor's proposal "navy-fy26-003" is at Wave 4
And "~/.sbir/quality-preferences.json" does not exist
And the proposal state contains "writing_style_selection_skipped" set to true
When the writer agent attempts to Write "artifacts/navy-fy26-003/wave-4-drafting/sections/technical-approach.md"
Then PES returns decision ALLOW

#### Scenario: Block Edit when no style selection

Given a legacy single-proposal workspace at Wave 4
And "~/.sbir/quality-preferences.json" does not exist
And the proposal state does not contain "writing_style_selection_skipped"
When the writer agent attempts to Edit "artifacts/wave-4-drafting/sections/technical-approach.md"
Then PES returns decision BLOCK

#### Scenario: Gate does not affect writes outside wave-4-drafting

Given Dr. Rafael Moreno's proposal "SF25D-T1201" is at Wave 3
And "~/.sbir/quality-preferences.json" does not exist
When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-3-outline/proposal-outline.md"
Then the writing style gate is not evaluated
And PES returns decision ALLOW

### Acceptance Criteria

- [ ] Writes to wave-4-drafting/ are blocked when quality-preferences.json does not exist at ~/.sbir/ and writing_style_selection_skipped is not true in proposal state
- [ ] Both Write and Edit tool operations are subject to the gate
- [ ] The skip marker (writing_style_selection_skipped: true in proposal state) is a valid alternative to quality-preferences.json
- [ ] Gate handles multi-proposal path layout (artifacts/{topic-id}/wave-4-drafting/)
- [ ] Gate handles legacy single-proposal path layout (artifacts/wave-4-drafting/)
- [ ] Writes to directories other than wave-4-drafting/ are not affected by this gate
- [ ] Block message includes both resolution paths (run quality discover OR skip style selection)
- [ ] Blocked and allowed decisions are recorded in the audit log

### Technical Notes

- New evaluator class: WritingStyleGateEvaluator following existing pattern (triggers + build_block_message)
- New rule_type: "writing_style_gate" registered in EnforcementEngine._evaluators
- New rule in templates/pes-config.json with rule_id "drafting-requires-style-selection"
- Evaluator checks ~/.sbir/ (global path) for quality-preferences.json -- differs from figure pipeline gate which checks proposal artifact directory. Hook adapter must resolve global artifact existence and pass via tool_context (new field: global_artifacts_present or extension of artifacts_present).
- Evaluator checks per-proposal state for writing_style_selection_skipped field (same pattern as style_analysis_skipped in StyleProfileGateEvaluator)
- Dependency: hook adapter must pass global artifact information (~/.sbir/ path) to the engine for this evaluator

---

## US-WSTYLE-02: Writer Agent Style Checkpoint

### Problem

Dr. Rafael Moreno is writing a DoD SBIR proposal (SF25D-T1201). During his last session, the writer agent jumped straight into drafting without any style discussion. It never presented available writing styles (Strunk & White, winning patterns, academic, conversational). It never showed agency-specific recommendations from his quality discovery data. It never asked how he wanted the proposal to read. The quality discovery system had produced quality-preferences.json with his preference for direct tone and inline evidence, winning-patterns.json with Air Force patterns, and writing-quality-profile.json with past evaluator feedback -- but the writer never surfaced any of this. Dr. Moreno had no opportunity to say "use Strunk & White rules" or "write like our winning Navy proposals."

### Who

- SBIR Principal Investigator | Has strong opinions about writing style | Needs to be asked about style preferences before any section is drafted
- First-time SBIR user | No quality profile exists | Needs sensible defaults presented without blocking
- Plugin Maintainer | Built the quality discovery system | Needs enforcement that the style conversation happens (or is consciously skipped)

### Solution

A mandatory style checkpoint in the writer agent's Phase 3 (DRAFT) workflow. Before drafting the first section, the writer must present available writing styles with context-aware recommendations based on quality discovery artifacts and target agency. The user chooses a style, adjusts, or skips. The choice is recorded in per-proposal state. Subsequent section drafts within the same proposal skip the checkpoint.

### Domain Examples

#### 1: Style checkpoint with quality profile -- Dr. Rafael Moreno, SF25D-T1201

Dr. Moreno's proposal for SF25D-T1201 is at Wave 4. The writer enters Phase 3 DRAFT for the first section (technical-approach). The writer reads quality artifacts: quality-preferences.json exists with tone: "direct", detail_level: "high", evidence_style: "inline". winning-patterns.json has 3 Air Force patterns with medium confidence. writing-quality-profile.json has a quality alert: "Technical approach clarity" flagged by past Air Force evaluator. The writer presents: "Your quality profile suggests: Elements of Style (concise, direct) + Air Force winning patterns. Quality alert: past evaluators noted technical approach clarity. Choose [1] Elements of Style [2] Academic [3] Conversational [4] Agency default [5] Custom [6] Skip." Dr. Moreno chooses "Elements of Style." The writer records writing_style: "elements" in proposal state and loads skills/writer/elements-of-style.md.

#### 2: Style checkpoint without quality profile -- Dr. Amara Okafor, navy-fy26-003

Dr. Okafor is a first-time user. No quality artifacts exist at ~/.sbir/. The writer enters Phase 3 DRAFT. The writer presents: "No quality profile found. You can create one with /proposal quality discover. Available styles: [1] Elements of Style [2] Academic [3] Conversational [4] Standard (recommended) [5] Skip style selection." Dr. Okafor chooses "Standard." The writer records writing_style: "standard" in proposal state.

#### 3: Style checkpoint skipped on subsequent sections -- Dr. Rafael Moreno, SF25D-T1201

Dr. Moreno already chose "Elements of Style" for the first section. Now he proceeds to the SOW section. The writer checks proposal state: writing_style is "elements." The style checkpoint is skipped. The writer loads elements-of-style.md and begins drafting SOW immediately.

#### 4: User explicitly skips style selection -- Dr. James Park, navy-fy26-001

Dr. Park is in a hurry and does not want to discuss style. The writer presents the style checkpoint. Dr. Park says "skip." The writer records writing_style_selection_skipped: true in proposal state. Drafting proceeds with standard prose defaults (no style skill loaded).

### UAT Scenarios (BDD)

#### Scenario: Style checkpoint presented with quality profile

Given Dr. Rafael Moreno's proposal "SF25D-T1201" is at Wave 4
And "~/.sbir/quality-preferences.json" exists with tone "direct" and evidence_style "inline"
And "~/.sbir/winning-patterns.json" exists with 3 Air Force winning patterns
And the proposal state does not contain "writing_style"
When the writer agent begins Phase 3 DRAFT for the first section
Then the writer presents available writing styles
And the recommendation references the quality profile tone "direct"
And the recommendation mentions Air Force winning patterns

#### Scenario: Style checkpoint presented without quality profile

Given Dr. Amara Okafor's proposal "navy-fy26-003" is at Wave 4
And "~/.sbir/quality-preferences.json" does not exist
And the proposal state does not contain "writing_style"
When the writer agent begins Phase 3 DRAFT for the first section
Then the writer presents default writing style options
And "Standard" is recommended as the default
And the writer mentions "/proposal quality discover" as an option

#### Scenario: Style checkpoint skipped when writing_style already set

Given Dr. Rafael Moreno's proposal "SF25D-T1201" is at Wave 4
And the proposal state contains "writing_style" set to "elements"
When the writer agent begins Phase 3 DRAFT for the next section
Then the writer does not present the style checkpoint
And drafting proceeds with the "elements" style skill loaded

#### Scenario: User selects skip at style checkpoint

Given Dr. James Park's proposal "navy-fy26-001" is at Wave 4
And the proposal state does not contain "writing_style"
When the writer presents the style checkpoint
And Dr. Park chooses "skip style selection"
Then the proposal state contains "writing_style_selection_skipped" set to true
And drafting proceeds with standard prose defaults

#### Scenario: Quality alerts surfaced during style checkpoint

Given Dr. Rafael Moreno's proposal "SF25D-T1201" targeting Air Force
And "~/.sbir/writing-quality-profile.json" exists with alert for Air Force technical approach clarity
When the writer presents the style checkpoint
Then the checkpoint mentions the quality alert about technical approach clarity

### Acceptance Criteria

- [ ] Writer presents style checkpoint before drafting the first section in Wave 4
- [ ] Checkpoint shows available writing styles with brief descriptions
- [ ] When quality-preferences.json exists, the recommendation uses tone and evidence_style from the profile
- [ ] When winning-patterns.json exists with patterns for the target agency, patterns are mentioned in the recommendation
- [ ] When writing-quality-profile.json has alerts for the target agency, alerts are surfaced during the checkpoint
- [ ] When no quality artifacts exist, sensible defaults are presented with a pointer to /proposal quality discover
- [ ] User's style choice (or skip) is recorded in per-proposal state.json
- [ ] Subsequent sections within the same proposal skip the checkpoint
- [ ] The chosen style skill file is loaded for all section drafting

### Technical Notes

- Modify sbir-writer.md Phase 3 DRAFT to add style checkpoint before first section draft
- Writer reads writing_style from per-proposal state.json to determine if checkpoint is needed
- Writer reads quality artifacts from ~/.sbir/ for recommendations (graceful degradation if missing)
- Writer records writing_style or writing_style_selection_skipped in per-proposal state.json
- Style skill loading: "elements" maps to skills/writer/elements-of-style.md. Other styles (academic, conversational, standard) may not have dedicated skill files yet -- writer uses inline guidance for those.
- Dependency: quality discovery must have run at least once for quality-preferences.json to exist, but this is NOT a hard dependency -- the skip path covers first-time users

---

## US-WSTYLE-03: Evaluator Integration with Engine and Config

### Problem

Phil, the plugin maintainer, needs the new WritingStyleGateEvaluator to be wired into the existing PES architecture. The engine dispatches rules to evaluators by rule_type string. If the new evaluator is not registered in the engine and the new rule is not added to pes-config.json, the enforcement is silently absent -- the engine returns ALLOW for unknown rule_types, and no block ever fires. Additionally, the hook adapter must be extended to check ~/.sbir/ (global path) for artifact existence, since this evaluator checks a global artifact rather than a proposal-directory artifact.

### Who

- Plugin Maintainer | Maintaining the PES enforcement system | Needs new evaluator to follow existing hexagonal architecture patterns exactly, plus hook adapter extension for global path resolution

### Solution

Register the new evaluator in EnforcementEngine._evaluators dict. Add one new rule to templates/pes-config.json. Extend the hook adapter to resolve global artifact existence at ~/.sbir/ and pass this information via tool_context.

### Domain Examples

#### 1: Engine dispatches writing_style_gate rule to correct evaluator

Phil adds rule_type "writing_style_gate" to the engine's _evaluators dict mapped to WritingStyleGateEvaluator(). When pes-config.json contains a rule with rule_type "writing_style_gate", the engine's _rule_triggers method calls evaluator.triggers(rule, state, tool_name, tool_context). The evaluator receives the rule condition and can inspect tool_context for global artifact existence and file_path.

#### 2: Config rule structure follows existing pattern

Phil adds a new rule to pes-config.json: `{"rule_id": "drafting-requires-style-selection", "description": "...", "rule_type": "writing_style_gate", "condition": {"target_directory": "wave-4-drafting", "required_global_artifact": "quality-preferences.json", "skip_state_field": "writing_style_selection_skipped"}, "message": "..."}`. This follows the same structure as existing rules.

#### 3: Hook adapter resolves global artifact path

When a PreToolUse event fires for a Write to wave-4-drafting/, the hook adapter now checks: (a) file_path of the target (existing behavior), (b) artifacts present in the proposal artifact directory (existing behavior from figure pipeline), and (c) whether quality-preferences.json exists at ~/.sbir/ (new behavior). The global artifact check result is passed to the evaluator via tool_context["global_artifacts_present"].

### UAT Scenarios (BDD)

#### Scenario: Engine dispatches writing_style_gate to correct evaluator

Given PES config contains a rule with rule_type "writing_style_gate"
And the engine has WritingStyleGateEvaluator registered for "writing_style_gate"
When the engine evaluates a PreToolUse event for a Write to wave-4-drafting/
Then the WritingStyleGateEvaluator.triggers method is called with the rule

#### Scenario: Rule present in pes-config.json

Given the plugin is installed with default configuration
When the PES config is loaded from templates/pes-config.json
Then the config contains a rule with rule_id "drafting-requires-style-selection"
And the rule has rule_type "writing_style_gate"

#### Scenario: Hook adapter resolves global artifact existence

Given "~/.sbir/quality-preferences.json" exists on disk
When the hook adapter processes a PreToolUse event for a Write operation
Then tool_context includes "global_artifacts_present" containing "quality-preferences.json"

### Acceptance Criteria

- [ ] WritingStyleGateEvaluator is registered in EnforcementEngine._evaluators with key "writing_style_gate"
- [ ] templates/pes-config.json contains rule with rule_id "drafting-requires-style-selection" and rule_type "writing_style_gate"
- [ ] Evaluator follows existing interface pattern (triggers method with tool_context, build_block_message method)
- [ ] Evaluator is a pure domain object with no infrastructure imports
- [ ] Hook adapter resolves ~/.sbir/quality-preferences.json existence and passes via tool_context
- [ ] Hook adapter extension does not break existing artifact resolution for figure pipeline gates

### Technical Notes

- Engine _evaluators dict registration pattern: see existing entries in engine.py
- Config rule structure: see existing rules in templates/pes-config.json
- The evaluator uses tool_context["global_artifacts_present"] for the quality-preferences.json check (new field) and state["writing_style_selection_skipped"] for the skip marker (existing state access pattern)
- Hook adapter extension: resolve Path.home() / ".sbir" / "quality-preferences.json" and add to tool_context. This is infrastructure code in the adapter, not in the domain evaluator.
- Dependency: US-WSTYLE-01 (the evaluator that gets registered)
