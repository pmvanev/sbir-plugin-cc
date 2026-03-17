Feature: PES Enforcement Wiring
  As Phil Santos, a small business engineer managing SBIR proposals,
  I want the 4 dormant PES evaluators activated via config rules
  so that the system automatically enforces proposal safety invariants.

  Background:
    Given the PES enforcement engine loads rules from pes-config.json
    And the hook adapter translates PreToolUse events to engine.evaluate()

  # --- PDC Gate ---

  Scenario: PDC gate blocks Wave 5 entry when RED Tier 1 items exist
    Given Phil's proposal "AF243-001" has pdc_status with section "technical_approach" having tier_1 "RED"
    And the red_items include "TRL justification missing"
    And the pes-config.json contains a pdc_gate rule targeting wave 5 with requires_pdc_green true
    When Phil invokes a tool named "wave_5_draft"
    Then PES returns BLOCK with exit_code 1
    And the message includes "RED PDC items: Section technical_approach: Tier 1 RED (TRL justification missing)"

  Scenario: PDC gate blocks Wave 5 entry when RED Tier 2 items exist
    Given Phil's proposal "AF243-001" has pdc_status with section "budget" having tier_2 "RED"
    And the red_items include "Cost volume incomplete"
    And the pes-config.json contains a pdc_gate rule targeting wave 5 with requires_pdc_green true
    When Phil invokes a tool named "wave_5_draft"
    Then PES returns BLOCK with exit_code 1
    And the message includes "Section budget: Tier 2 RED (Cost volume incomplete)"

  Scenario: PDC gate allows Wave 5 when all PDC items are GREEN
    Given Phil's proposal "AF243-001" has pdc_status with all sections having tier_1 "GREEN" and tier_2 "GREEN"
    And the pes-config.json contains a pdc_gate rule targeting wave 5 with requires_pdc_green true
    When Phil invokes a tool named "wave_5_draft"
    Then PES returns ALLOW with exit_code 0

  Scenario: PDC gate does not trigger for non-Wave-5 tools
    Given Phil's proposal has pdc_status with section "technical_approach" having tier_1 "RED"
    And the pes-config.json contains a pdc_gate rule targeting wave 5 with requires_pdc_green true
    When Phil invokes a tool named "wave_3_outline"
    Then PES returns ALLOW with exit_code 0

  Scenario: PDC gate allows when pdc_status is empty
    Given Phil's proposal has no pdc_status data
    And the pes-config.json contains a pdc_gate rule targeting wave 5 with requires_pdc_green true
    When Phil invokes a tool named "wave_5_draft"
    Then PES returns ALLOW with exit_code 0

  # --- Deadline Blocking ---

  Scenario: Deadline blocking blocks non-essential wave within critical threshold
    Given Phil's proposal "AF243-001" has deadline "2026-04-15"
    And today is "2026-04-13" (2 days remaining)
    And Phil's current_wave is 2
    And the pes-config.json contains a deadline_blocking rule with critical_days 3 and non_essential_waves [2, 3]
    When Phil invokes a tool named "wave_2_research"
    Then PES returns BLOCK with exit_code 1
    And the message includes "2 days remaining until deadline"
    And the message includes "submit with available work or skip non-essential waves"

  Scenario: Deadline blocking allows essential waves within critical threshold
    Given Phil's proposal "AF243-001" has deadline "2026-04-15"
    And today is "2026-04-13" (2 days remaining)
    And Phil's current_wave is 5
    And the pes-config.json contains a deadline_blocking rule with critical_days 3 and non_essential_waves [2, 3]
    When Phil invokes a tool named "wave_5_draft"
    Then PES returns ALLOW with exit_code 0

  Scenario: Deadline blocking allows non-essential waves outside critical threshold
    Given Phil's proposal "AF243-001" has deadline "2026-04-15"
    And today is "2026-04-05" (10 days remaining)
    And Phil's current_wave is 2
    And the pes-config.json contains a deadline_blocking rule with critical_days 3 and non_essential_waves [2, 3]
    When Phil invokes a tool named "wave_2_research"
    Then PES returns ALLOW with exit_code 0

  Scenario: Deadline blocking allows when no deadline is set
    Given Phil's proposal has no deadline in topic
    And Phil's current_wave is 2
    And the pes-config.json contains a deadline_blocking rule with critical_days 3 and non_essential_waves [2, 3]
    When Phil invokes a tool named "wave_2_research"
    Then PES returns ALLOW with exit_code 0

  # --- Submission Immutability ---

  Scenario: Submission immutability blocks writes on submitted immutable proposal
    Given Phil's proposal "AF243-001" has submission status "submitted" and immutable true
    And the pes-config.json contains a submission_immutability rule with requires_immutable true
    When Phil invokes any tool
    Then PES returns BLOCK with exit_code 1
    And the message includes "Proposal AF243-001 is submitted. Artifacts are read-only."

  Scenario: Submission immutability allows writes when not submitted
    Given Phil's proposal "AF243-001" has submission status "draft" and immutable false
    And the pes-config.json contains a submission_immutability rule with requires_immutable true
    When Phil invokes any tool
    Then PES returns ALLOW with exit_code 0

  Scenario: Submission immutability allows when submission field is absent
    Given Phil's proposal has no submission field in state
    And the pes-config.json contains a submission_immutability rule with requires_immutable true
    When Phil invokes any tool
    Then PES returns ALLOW with exit_code 0

  # --- Corpus Integrity ---

  Scenario: Corpus integrity blocks outcome tag modification
    Given Phil's proposal has learning outcome "win"
    And Phil requests to change outcome to "loss"
    And the pes-config.json contains a corpus_integrity rule with append_only_tags true
    When Phil invokes a tool named "record_outcome"
    Then PES returns BLOCK with exit_code 1

  Scenario: Corpus integrity allows first outcome tag assignment
    Given Phil's proposal has no existing learning outcome
    And Phil requests to set outcome to "win"
    And the pes-config.json contains a corpus_integrity rule with append_only_tags true
    When Phil invokes a tool named "record_outcome"
    Then PES returns ALLOW with exit_code 0

  Scenario: Corpus integrity allows when tool is not outcome-related
    Given Phil's proposal has learning outcome "win"
    And the pes-config.json contains a corpus_integrity rule with append_only_tags true
    When Phil invokes a tool named "wave_3_outline"
    Then PES returns ALLOW with exit_code 0

  Scenario: Corpus integrity allows same-value outcome assignment
    Given Phil's proposal has learning outcome "win"
    And Phil requests to change outcome to "win" (same value)
    And the pes-config.json contains a corpus_integrity rule with append_only_tags true
    When Phil invokes a tool named "record_outcome"
    Then PES returns ALLOW with exit_code 0
