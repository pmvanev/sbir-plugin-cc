Feature: Output Format Selection During Proposal Setup
  As an engineer setting up a new SBIR proposal
  I want to declare my preferred output format (LaTeX or DOCX)
  So that the downstream pipeline is tailored to my chosen medium from the start

  # Walking Skeleton: end-to-end format selection and persistence
  @walking_skeleton @US_PFS_001
  Scenario: Engineer sets up proposal and format choice persists in state
    Given Phil Santos creates a new proposal for topic "AF243-001"
    And Phil Santos selects "latex" as the output format
    When the proposal state is saved
    Then the proposal state contains output format "latex"
    And the proposal state is valid against the schema

  # Happy path: default format
  @US_PFS_001
  Scenario: New proposal includes output format defaulting to DOCX
    Given Phil Santos creates a new proposal for topic "AF243-001"
    When the proposal state is saved with no explicit format selection
    Then the proposal state contains output format "docx"

  # Happy path: explicit LaTeX selection
  @US_PFS_001
  Scenario: Format set to LaTeX is recorded in proposal state
    Given Phil Santos creates a new proposal for topic "AF243-001"
    And Phil Santos selects "latex" as the output format
    When the proposal state is saved
    Then the proposal state contains output format "latex"

  # Edge case: legacy state without output_format field
  @US_PFS_001
  Scenario: Missing output format defaults to DOCX on read
    Given an existing proposal state without an output format field
    When the format configuration service reads the current format
    Then the effective output format is "docx"

  # Error: invalid format in state
  @US_PFS_001 @property
  Scenario: Schema rejects invalid format value in state
    Given a proposal state with output format set to "pdf"
    When the state is validated against the schema
    Then validation rejects the state with a format error
