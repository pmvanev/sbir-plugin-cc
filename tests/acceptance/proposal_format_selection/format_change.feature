Feature: Change Output Format Mid-Proposal
  As an engineer who chose an output format during proposal setup
  I want to change the format later if I reconsider
  So that I can correct an early decision with awareness of rework impact

  Background:
    Given Phil Santos has an active proposal for topic "AF243-001"

  # Walking Skeleton: clean format change before drafting
  @walking_skeleton @US_PFS_002
  Scenario: Engineer changes format before drafting and state updates cleanly
    Given the proposal is in Wave 1
    And the current output format is "docx"
    When Phil Santos changes the output format to "latex"
    Then the proposal state contains output format "latex"
    And no rework warning is raised

  # Happy path: DOCX to LaTeX before Wave 3
  @US_PFS_002
  Scenario: Format changed from DOCX to LaTeX before Wave 3
    Given the proposal is in Wave 2
    And the current output format is "docx"
    When Phil Santos changes the output format to "latex"
    Then the proposal state contains output format "latex"
    And no rework warning is raised

  # Happy path: LaTeX to DOCX before Wave 3
  @US_PFS_002
  Scenario: Format changed from LaTeX to DOCX before Wave 3
    Given the proposal is in Wave 1
    And the current output format is "latex"
    When Phil Santos changes the output format to "docx"
    Then the proposal state contains output format "docx"
    And no rework warning is raised

  # Edge case: Wave 3 boundary -- warning threshold
  @US_PFS_002
  Scenario: Format change at Wave 3 triggers rework warning
    Given the proposal is in Wave 3
    And the current output format is "docx"
    When Phil Santos requests a format change to "latex"
    Then a rework warning is raised
    And the warning mentions that outline work may need adjustment

  # Happy path: Wave 4 triggers warning
  @US_PFS_002
  Scenario: Format change at Wave 4 triggers rework warning
    Given the proposal is in Wave 4
    And the current output format is "docx"
    When Phil Santos requests a format change to "latex"
    Then a rework warning is raised

  # Edge case: Wave 6 triggers warning
  @US_PFS_002
  Scenario: Format change at Wave 6 triggers rework warning
    Given the proposal is in Wave 6
    And the current output format is "docx"
    When Phil Santos requests a format change to "latex"
    Then a rework warning is raised

  # Error: invalid format value
  @US_PFS_002
  Scenario: Invalid format value rejected with error message
    Given the proposal is in Wave 1
    When Phil Santos changes the output format to "pdf"
    Then the format change is rejected
    And the error message lists valid format options "latex" and "docx"

  # Error: empty format value
  @US_PFS_002
  Scenario: Empty format value rejected
    Given the proposal is in Wave 1
    When Phil Santos submits a blank format value
    Then the format change is rejected

  # Edge case: same format is a no-op
  @US_PFS_002
  Scenario: Format change to same value succeeds without warning
    Given the proposal is in Wave 4
    And the current output format is "latex"
    When Phil Santos changes the output format to "latex"
    Then the proposal state contains output format "latex"
    And no rework warning is raised

  # Boundary: Wave 2 is the last wave without warning
  @US_PFS_002
  Scenario: Format change at Wave 2 proceeds without warning
    Given the proposal is in Wave 2
    And the current output format is "latex"
    When Phil Santos changes the output format to "docx"
    Then the proposal state contains output format "docx"
    And no rework warning is raised

  # Happy path: warning includes context
  @US_PFS_002
  Scenario: Rework warning includes wave context
    Given the proposal is in Wave 5
    And the current output format is "docx"
    When Phil Santos requests a format change to "latex"
    Then a rework warning is raised
    And the warning mentions the current wave number

  # Property: case-insensitive format acceptance
  @US_PFS_002 @property
  Scenario: Valid format values are always accepted regardless of case
    Given the proposal is in Wave 1
    When Phil Santos changes the output format to "LATEX"
    Then the proposal state contains output format "latex"
