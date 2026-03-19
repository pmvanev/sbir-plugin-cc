Feature: Partner Designation in Proposal State (US-PM-006)
  As an SBIR proposal writer starting a partnered proposal
  I want the designated partner recorded in proposal state
  So that all downstream agents use the correct partner automatically

  Background:
    Given the partner designation service is available

  # --- Happy Path: Designation ---

  @skip
  Scenario: STTR proposal records designated partner in proposal state
    Given partner profiles exist for "CU Boulder" and "NDSU"
    And Phil is starting a proposal for STTR topic "N244-012"
    When Phil designates "CU Boulder" as the partner
    Then the proposal state records partner slug as "cu-boulder"
    And the proposal state records the designation timestamp

  @skip
  Scenario: Non-partnered SBIR proposal has null partner designation
    Given Phil is starting a proposal for SBIR topic "AF243-001"
    When Phil creates the proposal without a partner
    Then the proposal state partner field is null
    And the proposal proceeds with solo scoring

  # --- Happy Path: Downstream Consumption ---

  @skip
  Scenario: Scoring service reads designated partner from proposal state
    Given Phil has a proposal with CU Boulder designated as partner
    When the scoring service loads partner context
    Then the scoring service uses the CU Boulder profile
    And Phil does not need to specify the partner separately

  # --- Error Path: Missing Partner ---

  @skip
  Scenario: STTR proposal with no partner profiles prompts setup
    Given no partner profiles exist on disk
    And Phil is starting a proposal for an STTR topic
    When the tool checks for available partners
    Then the tool reports no partner profiles found
    And the tool suggests running partner setup

  @skip
  Scenario: Designated partner file missing falls back to solo behavior
    Given proposal state designates partner "cu-boulder"
    And the partner profile file for "cu-boulder" does not exist on disk
    When the scoring service loads partner context
    Then the scoring service falls back to solo scoring
    And a warning notes the missing partner profile

  # --- Error Path: Mid-Proposal Changes ---

  @skip
  Scenario: Changing partner mid-proposal warns about stale artifacts
    Given Phil has a proposal with CU Boulder designated
    And an approach brief references CU Boulder capabilities
    When Phil changes the designated partner to NDSU
    Then the tool warns that existing artifacts reference CU Boulder
    And the tool suggests regenerating the approach brief and strategy brief

  # --- Boundary: Backward Compatibility ---

  @skip
  Scenario: Existing proposal state without partner field works as non-partnered
    Given a proposal state file exists without a partner field
    When the partner designation is read from proposal state
    Then the partner designation is treated as null
    And all agents use non-partnered behavior

  @property @skip
  Scenario: Partner designation is always either a valid slug or null
    Given any proposal state
    When the partner field is read
    Then the value is either a non-empty string matching slug format or null
