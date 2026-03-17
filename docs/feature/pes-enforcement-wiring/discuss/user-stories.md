<!-- markdownlint-disable MD024 -->

# User Stories: PES Enforcement Wiring

## US-PEW-001: PDC Gate Enforcement

### Problem
Phil Santos is a small business engineer preparing SBIR proposals under tight deadlines. He finds it risky to enter Wave 5 (drafting) without verifying that all Pre-Draft Checklist items are resolved, because starting a draft with RED Tier 1 or Tier 2 items leads to rework and wasted hours.

### Who
- Phil Santos | Entering Wave 5 drafting phase | Wants assurance that all PDC prerequisites are met before investing drafting effort

### Solution
Add a `pdc_gate` rule to `pes-config.json` that activates the existing `PdcGateEvaluator`, blocking Wave 5 entry when any proposal section has RED Tier 1 or Tier 2 PDC items.

### Domain Examples

#### 1: RED Tier 1 blocks Wave 5 entry
Phil is working on proposal AF243-001 for "Compact Directed Energy for Maritime UAS Defense." The technical_approach section has Tier 1 status RED with red_items ["TRL justification missing"]. Phil invokes `wave_5_draft`. PES blocks with message: "Wave 5 requires all PDC items to be GREEN. RED PDC items: Section technical_approach: Tier 1 RED (TRL justification missing)."

#### 2: All GREEN allows Wave 5 entry
Phil's proposal AF243-001 has all PDC sections with tier_1 GREEN and tier_2 GREEN. Phil invokes `wave_5_draft`. PES allows the action (exit_code 0), and Phil begins drafting.

#### 3: RED Tier 2 also blocks
Phil's proposal has the budget section with tier_2 RED and red_items ["Cost volume incomplete"]. Even though all Tier 1 items are GREEN, PES blocks Wave 5 entry because Tier 2 RED items also indicate unresolved prerequisites.

#### 4: Non-Wave-5 tools unaffected
Phil has RED PDC items but invokes `wave_3_outline`. PES allows the action because the PDC gate only protects Wave 5 entry.

#### 5: Empty pdc_status does not block
Phil's proposal has no pdc_status data yet (early in lifecycle). PES allows Wave 5 tools because there are no RED items to block on.

### UAT Scenarios (BDD)

#### Scenario: RED Tier 1 blocks Wave 5
Given Phil's proposal "AF243-001" has pdc_status with section "technical_approach" having tier_1 "RED" and red_items ["TRL justification missing"]
And pes-config.json contains a pdc_gate rule with target_wave 5 and requires_pdc_green true
When Phil invokes tool "wave_5_draft"
Then PES returns BLOCK with exit_code 1
And the message contains "Section technical_approach: Tier 1 RED (TRL justification missing)"

#### Scenario: RED Tier 2 blocks Wave 5
Given Phil's proposal has pdc_status with section "budget" having tier_2 "RED" and red_items ["Cost volume incomplete"]
And pes-config.json contains a pdc_gate rule with target_wave 5 and requires_pdc_green true
When Phil invokes tool "wave_5_draft"
Then PES returns BLOCK with exit_code 1
And the message contains "Section budget: Tier 2 RED"

#### Scenario: All GREEN allows Wave 5
Given Phil's proposal has pdc_status with all sections having tier_1 "GREEN" and tier_2 "GREEN"
And pes-config.json contains a pdc_gate rule with target_wave 5 and requires_pdc_green true
When Phil invokes tool "wave_5_draft"
Then PES returns ALLOW with exit_code 0

#### Scenario: Non-Wave-5 tool not blocked by PDC gate
Given Phil's proposal has pdc_status with RED Tier 1 items
And pes-config.json contains a pdc_gate rule with target_wave 5
When Phil invokes tool "wave_3_outline"
Then PES returns ALLOW with exit_code 0

#### Scenario: Empty pdc_status does not block
Given Phil's proposal has no pdc_status data
And pes-config.json contains a pdc_gate rule with target_wave 5 and requires_pdc_green true
When Phil invokes tool "wave_5_draft"
Then PES returns ALLOW with exit_code 0

### Acceptance Criteria
- [ ] pes-config.json contains a rule with rule_type "pdc_gate", target_wave 5, and requires_pdc_green true
- [ ] Wave 5 tools are blocked when any section has RED Tier 1 or Tier 2 PDC status
- [ ] Block message lists each RED section with tier level and specific red items
- [ ] Non-Wave-5 tools are not affected by the PDC gate rule
- [ ] Missing or empty pdc_status does not cause a block (graceful default)

### Technical Notes
- Rule is added to the existing `rules` array in `templates/pes-config.json`
- `PdcGateEvaluator` is already implemented in `scripts/pes/domain/pdc_gate.py` and registered in `engine.py`
- State field `pdc_status` must be populated by upstream Wave 4 PDC review agent
- The evaluator checks tool_name for `wave_{target_wave}` string match

### Dependencies
- `PdcGateEvaluator` class (exists in `scripts/pes/domain/pdc_gate.py`)
- Engine dispatch for `pdc_gate` rule_type (exists in `scripts/pes/domain/engine.py`)
- Proposal state schema must support `pdc_status` field (schema v2.0.0)

---

## US-PEW-002: Deadline Blocking Enforcement

### Problem
Phil Santos is a small business engineer who sometimes loses track of deadlines while working on research or outline waves. He finds it dangerous to spend time on non-essential waves when the submission deadline is 3 days away, because that time should be spent on finalizing and submitting.

### Who
- Phil Santos | Working on non-essential waves near deadline | Wants automatic redirection toward essential submission work

### Solution
Add a `deadline_blocking` rule to `pes-config.json` that activates the existing `DeadlineBlockingEvaluator`, blocking non-essential wave work within the critical deadline threshold.

### Domain Examples

#### 1: Non-essential wave blocked within critical threshold
Phil is working on proposal AF243-001 with deadline 2026-04-15. Today is 2026-04-13 (2 days remaining). Phil's current_wave is 2 (research). He invokes `wave_2_research`. PES blocks: "Deadline approaching: non-essential waves blocked. 2 days remaining until deadline. Consider: submit with available work or skip non-essential waves."

#### 2: Essential wave allowed within critical threshold
Phil's proposal AF243-001 has 2 days until deadline. His current_wave is 5 (drafting). He invokes `wave_5_draft`. PES allows because Wave 5 is not in the non_essential_waves list.

#### 3: Non-essential wave allowed outside threshold
Phil's proposal has 10 days until deadline. His current_wave is 2. He invokes `wave_2_research`. PES allows because 10 > 3 (critical_days).

#### 4: No deadline set -- no blocking
Phil's proposal has no deadline in the topic field. He invokes `wave_2_research`. PES allows because there is no deadline to compare against.

### UAT Scenarios (BDD)

#### Scenario: Non-essential wave blocked near deadline
Given Phil's proposal "AF243-001" has deadline "2026-04-15" and today is 2 days before deadline
And Phil's current_wave is 2
And pes-config.json contains a deadline_blocking rule with critical_days 3 and non_essential_waves [2, 3]
When Phil invokes tool "wave_2_research"
Then PES returns BLOCK with exit_code 1
And the message contains "2 days remaining until deadline"

#### Scenario: Essential wave allowed near deadline
Given Phil's proposal "AF243-001" has deadline "2026-04-15" and today is 2 days before deadline
And Phil's current_wave is 5
And pes-config.json contains a deadline_blocking rule with critical_days 3 and non_essential_waves [2, 3]
When Phil invokes tool "wave_5_draft"
Then PES returns ALLOW with exit_code 0

#### Scenario: Non-essential wave allowed outside threshold
Given Phil's proposal "AF243-001" has deadline "2026-04-15" and today is 10 days before deadline
And Phil's current_wave is 2
And pes-config.json contains a deadline_blocking rule with critical_days 3 and non_essential_waves [2, 3]
When Phil invokes tool "wave_2_research"
Then PES returns ALLOW with exit_code 0

#### Scenario: No deadline means no blocking
Given Phil's proposal has no deadline in topic
And Phil's current_wave is 2
And pes-config.json contains a deadline_blocking rule with critical_days 3 and non_essential_waves [2, 3]
When Phil invokes tool "wave_2_research"
Then PES returns ALLOW with exit_code 0

#### Scenario: Invalid deadline format does not block
Given Phil's proposal has deadline "not-a-date" in topic
And Phil's current_wave is 2
And pes-config.json contains a deadline_blocking rule with critical_days 3 and non_essential_waves [2, 3]
When Phil invokes tool "wave_2_research"
Then PES returns ALLOW with exit_code 0

### Acceptance Criteria
- [ ] pes-config.json contains a rule with rule_type "deadline_blocking", critical_days 3, and non_essential_waves [2, 3]
- [ ] Non-essential wave tools are blocked when days-to-deadline is at or below critical_days threshold
- [ ] Block message includes days remaining and actionable suggestion to submit or skip
- [ ] Essential waves (not in non_essential_waves list) are never blocked by this rule
- [ ] Missing or invalid deadline does not cause a block or error

### Technical Notes
- Rule is added to the existing `rules` array in `templates/pes-config.json`
- `DeadlineBlockingEvaluator` is already implemented in `scripts/pes/domain/deadline_blocking.py` and registered in `engine.py`
- The evaluator uses `date.today()` for current date -- this is the actual system date
- The evaluator checks both `current_wave in non_essential_waves` AND `wave_{current_wave} in tool_name`
- The `non_essential_waves` list value (which waves are "non-essential") is a product decision

### Dependencies
- `DeadlineBlockingEvaluator` class (exists in `scripts/pes/domain/deadline_blocking.py`)
- Engine dispatch for `deadline_blocking` rule_type (exists in `scripts/pes/domain/engine.py`)
- State field `topic.deadline` populated during `/proposal new`
- `deadlines.critical_days` in pes-config.json enforcement section (already exists, value: 3)

---

## US-PEW-003: Submission Immutability Enforcement

### Problem
Phil Santos is a small business engineer who sometimes re-opens a Claude Code session days after submitting a proposal. He finds it risky that there is no protection against accidentally modifying a submitted proposal's artifacts, because changes after submission would create inconsistency between what was submitted and what is on disk.

### Who
- Phil Santos | Returning to a project after proposal submission | Wants protection against accidental modification of submitted work

### Solution
Add a `submission_immutability` rule to `pes-config.json` that activates the existing `SubmissionImmutabilityEvaluator`, blocking all write operations when a proposal is submitted and marked immutable.

### Domain Examples

#### 1: All writes blocked after submission
Phil submitted proposal AF243-001 last week. He opens the project in Claude Code and invokes any tool. PES blocks: "Proposal AF243-001 is submitted. Artifacts are read-only."

#### 2: Writes allowed while still drafting
Phil's proposal AF243-001 has submission status "draft" and immutable false. He invokes tools freely. PES allows all actions.

#### 3: No submission field -- no blocking
Phil's proposal is early in lifecycle and has no submission field in state. PES allows all actions because there is nothing to protect.

### UAT Scenarios (BDD)

#### Scenario: All writes blocked after submission
Given Phil's proposal "AF243-001" has submission status "submitted" and immutable true
And pes-config.json contains a submission_immutability rule with requires_immutable true
When Phil invokes any tool
Then PES returns BLOCK with exit_code 1
And the message is "Proposal AF243-001 is submitted. Artifacts are read-only."

#### Scenario: Writes allowed when not submitted
Given Phil's proposal "AF243-001" has submission status "draft" and immutable false
And pes-config.json contains a submission_immutability rule with requires_immutable true
When Phil invokes any tool
Then PES returns ALLOW with exit_code 0

#### Scenario: Submitted but not immutable allows writes
Given Phil's proposal "AF243-001" has submission status "submitted" and immutable false
And pes-config.json contains a submission_immutability rule with requires_immutable true
When Phil invokes any tool
Then PES returns ALLOW with exit_code 0

#### Scenario: Missing submission field allows writes
Given Phil's proposal has no submission field in state
And pes-config.json contains a submission_immutability rule with requires_immutable true
When Phil invokes any tool
Then PES returns ALLOW with exit_code 0

#### Scenario: Block message falls back when topic.id is missing
Given Phil's proposal has submission status "submitted" and immutable true but no topic.id
And pes-config.json contains a submission_immutability rule with requires_immutable true
When Phil invokes any tool
Then PES returns BLOCK with exit_code 1
And the message is the rule's configured message text

### Acceptance Criteria
- [ ] pes-config.json contains a rule with rule_type "submission_immutability" and requires_immutable true
- [ ] All tool invocations are blocked when submission.status is "submitted" and submission.immutable is true
- [ ] Block message includes the proposal topic ID when available
- [ ] Both conditions (status AND immutable) must be true for blocking -- either alone does not block
- [ ] Missing or non-dict submission field does not cause a block or error

### Technical Notes
- Rule is added to the existing `rules` array in `templates/pes-config.json`
- `SubmissionImmutabilityEvaluator` is already implemented in `scripts/pes/domain/submission_immutability.py` and registered in `engine.py`
- This evaluator does NOT check tool_name -- it blocks ALL tools when triggered
- The `submission` state field must be populated by the submission agent at submit time

### Dependencies
- `SubmissionImmutabilityEvaluator` class (exists in `scripts/pes/domain/submission_immutability.py`)
- Engine dispatch for `submission_immutability` rule_type (exists in `scripts/pes/domain/engine.py`)
- State field `submission` populated by submission agent (not yet implemented -- tracked dependency)

---

## US-PEW-004: Corpus Integrity Enforcement

### Problem
Phil Santos is a small business engineer who records win/loss outcomes after proposal decisions. He finds it critical that historical outcome tags cannot be changed after recording, because the corpus learning system depends on accurate, immutable outcome data to improve future proposals.

### Who
- Phil Santos | Recording or reviewing proposal outcomes | Wants assurance that recorded outcomes cannot be accidentally overwritten

### Solution
Add a `corpus_integrity` rule to `pes-config.json` that activates the existing `CorpusIntegrityEvaluator`, blocking modification of existing win/loss outcome tags while allowing first-time assignment.

### Domain Examples

#### 1: Outcome tag modification blocked
Phil's proposal AF243-001 was tagged "win" after the agency awarded the contract. Phil accidentally tries to record outcome "loss". PES blocks because the existing "win" outcome cannot be changed.

#### 2: First outcome assignment allowed
Phil's proposal AF243-001 has no recorded outcome (learning.outcome is null). Phil records outcome "win". PES allows because there is no existing tag to protect.

#### 3: Non-outcome tools unaffected
Phil's proposal has outcome "win" recorded. Phil invokes `wave_3_outline` for a different proposal task. PES allows because the tool name does not contain "outcome" or "record_outcome".

#### 4: Same-value assignment allowed
Phil's proposal has outcome "win". Phil runs the outcome recording again with value "win" (idempotent). PES allows because the requested value matches the existing value.

### UAT Scenarios (BDD)

#### Scenario: Outcome tag modification blocked
Given Phil's proposal has learning outcome "win"
And Phil requests to change outcome to "loss" (requested_outcome_change = "loss")
And pes-config.json contains a corpus_integrity rule with append_only_tags true
When Phil invokes tool "record_outcome"
Then PES returns BLOCK with exit_code 1

#### Scenario: First outcome assignment allowed
Given Phil's proposal has no learning outcome (outcome is null)
And pes-config.json contains a corpus_integrity rule with append_only_tags true
When Phil invokes tool "record_outcome"
Then PES returns ALLOW with exit_code 0

#### Scenario: Non-outcome tools unaffected
Given Phil's proposal has learning outcome "win"
And pes-config.json contains a corpus_integrity rule with append_only_tags true
When Phil invokes tool "wave_3_outline"
Then PES returns ALLOW with exit_code 0

#### Scenario: Same-value assignment allowed
Given Phil's proposal has learning outcome "win"
And Phil requests to change outcome to "win" (same value)
And pes-config.json contains a corpus_integrity rule with append_only_tags true
When Phil invokes tool "record_outcome"
Then PES returns ALLOW with exit_code 0

#### Scenario: Missing learning field does not block
Given Phil's proposal has no learning field in state
And pes-config.json contains a corpus_integrity rule with append_only_tags true
When Phil invokes tool "record_outcome"
Then PES returns ALLOW with exit_code 0

### Acceptance Criteria
- [ ] pes-config.json contains a rule with rule_type "corpus_integrity" and append_only_tags true
- [ ] Outcome tools are blocked when an existing outcome tag would be changed to a different value
- [ ] First-time outcome assignment (no existing tag) is allowed
- [ ] Same-value re-assignment is allowed (idempotent)
- [ ] Non-outcome tools are never affected by this rule
- [ ] Missing or non-dict learning field does not cause a block or error

### Technical Notes
- Rule is added to the existing `rules` array in `templates/pes-config.json`
- `CorpusIntegrityEvaluator` is already implemented in `scripts/pes/domain/corpus_integrity.py` and registered in `engine.py`
- Tool name must contain "outcome" or "record_outcome" for this evaluator to check
- The evaluator compares `learning.outcome` (existing) with `requested_outcome_change` (incoming)
- Note: `CorpusIntegrityEvaluator` does NOT have a `build_block_message()` method -- the engine falls through to `rule.message`

### Dependencies
- `CorpusIntegrityEvaluator` class (exists in `scripts/pes/domain/corpus_integrity.py`)
- Engine dispatch for `corpus_integrity` rule_type (exists in `scripts/pes/domain/engine.py`)
- State fields `learning.outcome` and `requested_outcome_change` populated by debrief analyst agent
- Note: `engine._build_message()` does not have a `corpus_integrity` case -- it falls through to `return rule.message` (this is correct behavior, not a bug)
