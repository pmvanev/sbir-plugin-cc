<!-- markdownlint-disable MD024 -->

# Outline Gate Enforcement -- User Stories

## US-OGATE-01: Outline Gate Evaluator

### Problem

Dr. Rafael Moreno is a defense tech PI writing a DoD SBIR proposal (SF25D-T1201) for autonomous sensor fusion. He spent significant effort in Wave 3 developing a detailed outline with section structure, page budgets, compliance item mapping, thesis statements, and a discrimination table. During Wave 4 drafting, the writer agent began writing section files directly to wave-4-drafting/ without referencing the approved outline in wave-3-outline/. The agent fabricated section structure that did not match the approved plan -- page budgets were ignored, compliance items were missed, and the discrimination table was not reflected in the narrative. Markdown agent instructions ("read the approved outline") were already present but the agent ignored them.

### Who

- SBIR Principal Investigator | Writing a competitive proposal with an approved outline | Needs draft sections to follow the approved structure with correct page budgets and compliance mapping
- Plugin Maintainer | Observing agent behavior bypass markdown instructions | Needs hard enforcement at the PES hook layer that the agent cannot override

### Solution

A new PES evaluator (OutlineGateEvaluator) that blocks Write and Edit operations targeting files in wave-4-drafting/ when proposal-outline.md does not exist in the sibling wave-3-outline/ directory. This is a cross-directory artifact check: the target is wave-4-drafting/ but the prerequisite is in wave-3-outline/. The adapter derives the sibling directory path from the target path.

### Domain Examples

#### 1: Writer tries to draft without outline -- Dr. Rafael Moreno, SF25D-T1201

Dr. Rafael Moreno's proposal for topic SF25D-T1201 (autonomous sensor fusion, Air Force) is at Wave 4. The writer agent receives the dispatch and immediately attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md" -- a draft of the Technical Approach section. PES fires the PreToolUse hook. The OutlineGateEvaluator checks: the target path contains "wave-4-drafting/", and proposal-outline.md does not exist at "artifacts/sf25d-t1201/wave-3-outline/proposal-outline.md". Decision: BLOCK. The agent receives the message: "Cannot write draft sections to wave-4-drafting/ before the proposal outline is approved. Required: artifacts/sf25d-t1201/wave-3-outline/proposal-outline.md."

#### 2: Writer drafts after outline exists -- Dr. Elena Vasquez, af263-042

Dr. Elena Vasquez's Army proposal (af263-042, battlefield communications) completed Wave 3 with an approved outline in wave-3-outline/proposal-outline.md. The writer agent attempts to Write "artifacts/af263-042/wave-4-drafting/section-1-technical-approach.md". PES fires PreToolUse. The evaluator checks: proposal-outline.md exists at "artifacts/af263-042/wave-3-outline/proposal-outline.md". Decision: ALLOW. The writer reads the outline and follows the approved section structure.

#### 3: Edit operation also blocked -- legacy workspace

A legacy single-proposal workspace (no topic-id subdirectory). The writer attempts to Edit "artifacts/wave-4-drafting/section-2-schedule.md" to modify an existing draft. proposal-outline.md does not exist at "artifacts/wave-3-outline/proposal-outline.md". PES fires PreToolUse. The evaluator checks: target path contains "wave-4-drafting/", proposal-outline.md does not exist in the sibling wave-3-outline/ directory. Decision: BLOCK.

#### 4: Cross-directory path resolution -- Dr. James Park, navy-fy26-001

Dr. James Park's Navy proposal (navy-fy26-001) has an approved outline. The writer attempts to Write "artifacts/navy-fy26-001/wave-4-drafting/section-3-management-plan.md". The adapter detects "wave-4-drafting/" in the target path, replaces it with "wave-3-outline/" to get "artifacts/navy-fy26-001/wave-3-outline/", and checks for proposal-outline.md at that path. File exists. Decision: ALLOW.

### UAT Scenarios (BDD)

#### Scenario: Block draft section write when proposal-outline.md does not exist

Given Dr. Rafael Moreno's proposal "SF25D-T1201" is at Wave 4
And "artifacts/sf25d-t1201/wave-3-outline/proposal-outline.md" does not exist
When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-4-drafting/section-1-technical-approach.md"
Then PES returns decision BLOCK
And the block message includes "proposal outline"
And the block message includes the path to wave-3-outline/

#### Scenario: Allow draft section write when proposal-outline.md exists

Given Dr. Elena Vasquez's proposal "af263-042" is at Wave 4
And "artifacts/af263-042/wave-3-outline/proposal-outline.md" exists
When the writer agent attempts to Write "artifacts/af263-042/wave-4-drafting/section-1-technical-approach.md"
Then PES returns decision ALLOW

#### Scenario: Block Edit when proposal-outline.md does not exist

Given a legacy single-proposal workspace at Wave 4
And "artifacts/wave-3-outline/proposal-outline.md" does not exist
When the writer agent attempts to Edit "artifacts/wave-4-drafting/section-2-schedule.md"
Then PES returns decision BLOCK

#### Scenario: Gate does not affect writes outside wave-4-drafting

Given Dr. Rafael Moreno's proposal "SF25D-T1201" is at Wave 3
When the writer agent attempts to Write "artifacts/sf25d-t1201/wave-3-outline/notes.md"
Then the outline gate is not evaluated
And PES returns decision ALLOW

#### Scenario: Cross-directory resolution for multi-proposal layout

Given Dr. James Park's proposal "navy-fy26-001" is at Wave 4
And "artifacts/navy-fy26-001/wave-3-outline/proposal-outline.md" exists
When the writer agent attempts to Write "artifacts/navy-fy26-001/wave-4-drafting/section-3-management-plan.md"
Then PES returns decision ALLOW

### Acceptance Criteria

- [ ] Writes to wave-4-drafting/ are blocked when proposal-outline.md does not exist in the sibling wave-3-outline/ directory
- [ ] Both Write and Edit tool operations are subject to the gate
- [ ] Gate handles multi-proposal path layout (artifacts/{topic-id}/wave-4-drafting/ -> wave-3-outline/)
- [ ] Gate handles legacy single-proposal path layout (artifacts/wave-4-drafting/ -> wave-3-outline/)
- [ ] Writes to directories other than wave-4-drafting/ are not affected by this gate
- [ ] Block message includes clear guidance (complete the outline in Wave 3 first)
- [ ] Block message includes the path to the required proposal-outline.md
- [ ] Blocked and allowed decisions are recorded in the audit log

### Technical Notes

- New evaluator class: OutlineGateEvaluator following existing pattern (triggers + build_block_message)
- New rule_type: "outline_gate" registered in EnforcementEngine._evaluators
- New rule in templates/pes-config.json with rule_id "drafting-requires-outline"
- Cross-directory artifact check: adapter derives wave-3-outline/ from wave-4-drafting/ target path (new adapter pattern)
- Evaluator needs file_path from hook input -- same interface consideration as FigurePipelineGateEvaluator
- No prerequisite creation exception needed (unlike figure-specs.md): the writer agent never writes to wave-3-outline/, only the outliner does
- Simpler than figure pipeline gate: no skip marker, no same-directory prerequisite exception -- just existence check in a sibling directory

---

## US-OGATE-02: Evaluator Integration with Engine and Config

### Problem

Phil, the plugin maintainer, needs the new OutlineGateEvaluator to be wired into the existing PES architecture. The engine dispatches rules to evaluators by rule_type string. If the new evaluator is not registered in the engine and the new rule is not added to pes-config.json, the enforcement is silently absent -- the engine returns ALLOW for unknown rule_types, and no block ever fires. Additionally, the hook adapter needs to support the new cross-directory artifact check pattern (deriving wave-3-outline/ from wave-4-drafting/ target paths).

### Who

- Plugin Maintainer | Maintaining the PES enforcement system with 8 existing evaluators | Needs the 9th evaluator to follow existing hexagonal architecture patterns and extend the adapter for cross-directory checks

### Solution

Register the OutlineGateEvaluator in EnforcementEngine._evaluators dict. Add a new rule to templates/pes-config.json. Extend the hook adapter to support cross-directory artifact resolution: when a wave-4-drafting/ path is detected, derive the sibling wave-3-outline/ path and check for proposal-outline.md.

### Domain Examples

#### 1: Engine dispatches outline_gate rule to correct evaluator

Phil adds rule_type "outline_gate" to the engine's _evaluators dict mapped to OutlineGateEvaluator(). When pes-config.json contains a rule with rule_type "outline_gate", the engine's _rule_triggers method calls evaluator.triggers(rule, state, tool_name). The evaluator receives the rule condition and can inspect whether proposal-outline.md exists.

#### 2: Config rule structure follows existing pattern

Phil adds a new rule to pes-config.json: `{"rule_id": "drafting-requires-outline", "description": "Block Wave 4 drafting without approved outline", "rule_type": "outline_gate", "condition": {"target_directory": "wave-4-drafting", "required_artifact": "proposal-outline.md", "required_artifact_directory": "wave-3-outline"}, "message": "..."}`. This follows the same structure as existing rules.

#### 3: Adapter cross-directory resolution for multi-proposal workspace

The hook adapter receives a PreToolUse event with file_path "artifacts/af263-042/wave-4-drafting/section-1-approach.md". The adapter detects "wave-4-drafting/" in the path. It derives the sibling path by replacing "wave-4-drafting" with "wave-3-outline": "artifacts/af263-042/wave-3-outline/". It checks for "proposal-outline.md" at that path and passes the result to the evaluator.

#### 4: Adapter cross-directory resolution for legacy workspace

The hook adapter receives file_path "artifacts/wave-4-drafting/section-1-approach.md". The adapter detects "wave-4-drafting/" in the path. It derives "artifacts/wave-3-outline/" and checks for "proposal-outline.md". Same resolution logic, different base path.

### UAT Scenarios (BDD)

#### Scenario: Engine dispatches outline_gate to correct evaluator

Given PES config contains a rule with rule_type "outline_gate"
And the engine has OutlineGateEvaluator registered for "outline_gate"
When the engine evaluates a PreToolUse event
Then the OutlineGateEvaluator.triggers method is called with the rule

#### Scenario: Rule present in pes-config.json

Given the plugin is installed with default configuration
When the PES config is loaded from templates/pes-config.json
Then the config contains a rule with rule_id "drafting-requires-outline"
And the rule has rule_type "outline_gate"

#### Scenario: Adapter resolves cross-directory path for multi-proposal workspace

Given a PreToolUse event with file_path "artifacts/af263-042/wave-4-drafting/section-1.md"
When the adapter processes the event
Then the adapter checks for "artifacts/af263-042/wave-3-outline/proposal-outline.md"

#### Scenario: Adapter resolves cross-directory path for legacy workspace

Given a PreToolUse event with file_path "artifacts/wave-4-drafting/section-1.md"
When the adapter processes the event
Then the adapter checks for "artifacts/wave-3-outline/proposal-outline.md"

### Acceptance Criteria

- [ ] OutlineGateEvaluator is registered in EnforcementEngine._evaluators with key "outline_gate"
- [ ] templates/pes-config.json contains rule with rule_id "drafting-requires-outline" and rule_type "outline_gate"
- [ ] Evaluator follows existing interface pattern (triggers method, build_block_message method)
- [ ] Evaluator is a pure domain object with no infrastructure imports
- [ ] Hook adapter derives wave-3-outline/ path from wave-4-drafting/ target path
- [ ] Adapter handles both multi-proposal and legacy path layouts for cross-directory resolution

### Technical Notes

- Engine _evaluators dict registration pattern: see existing entries in engine.py
- Config rule structure: see existing rules in templates/pes-config.json
- Cross-directory resolution is an adapter concern (infrastructure), not domain. The evaluator receives the result of the check, not the raw file path.
- Same file_path interface consideration as figure pipeline gate evaluators -- evaluator needs hook context, not just tool_name
- Dependency: US-OGATE-01 (the evaluator that gets registered)
- This is the first cross-directory artifact check in PES. The figure pipeline gate checks same-directory (wave-5-visuals/ for figure-specs.md). This pattern may be reused for future cross-wave gates.
