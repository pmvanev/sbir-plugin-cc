Feature: PDC Gate Enforcement (US-PEW-001)
  As Phil Santos, preparing an SBIR proposal under tight deadlines,
  I want the system to block Wave 5 entry when pre-draft checklist items are unresolved
  So that I never waste effort drafting sections with missing prerequisites

  # --- Happy Path ---

  Scenario: All GREEN checklist items allow Wave 5 entry
    Given Phil's proposal "AF243-001" has all pre-draft checklist sections at GREEN for Tier 1 and Tier 2
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts to begin Wave 5 drafting work
    Then the action is allowed

  # --- Error Paths ---

  Scenario: RED Tier 1 item blocks Wave 5 entry
    Given Phil's proposal "AF243-001" has a pre-draft checklist with section "technical_approach" showing Tier 1 RED for "TRL justification missing"
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts to begin Wave 5 drafting work
    Then the action is blocked
    And the block reason mentions "Section technical_approach: Tier 1 RED (TRL justification missing)"

  Scenario: RED Tier 2 item blocks Wave 5 entry
    Given Phil's proposal "AF243-001" has a pre-draft checklist with section "budget" showing Tier 2 RED for "Cost volume incomplete"
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts to begin Wave 5 drafting work
    Then the action is blocked
    And the block reason mentions "Section budget: Tier 2 RED (Cost volume incomplete)"

  # --- Boundary/Edge ---

  Scenario: Non-Wave-5 tool is not affected by pre-draft checklist gate
    Given Phil's proposal "AF243-001" has a pre-draft checklist with section "technical_approach" showing Tier 1 RED for "TRL justification missing"
    And the enforcement rules are loaded from the standard configuration
    When Phil uses a non-drafting tool
    Then the action is allowed

  Scenario: Missing pre-draft checklist data does not block Wave 5
    Given Phil's proposal "AF243-001" has no pre-draft checklist data
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts to begin Wave 5 drafting work
    Then the action is allowed
