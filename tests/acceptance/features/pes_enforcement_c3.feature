Feature: PES C3 Enforcement -- Production and Submission Invariants (US-014)
  As an engineer working through proposal production and submission
  I want structural guarantees that production integrity is maintained
  So I never format unapproved content, modify submitted proposals, or corrupt learning data

  Background:
    Given the proposal plugin is active

  # --- PDC Gate: Wave 5 Entry ---

  Scenario: PDC gate blocks Wave 5 when a section has RED Tier 2 PDC items
    Given Phil has an active proposal with all sections drafted
    And section 3.2 has 1 RED Tier 2 PDC item
    When Phil attempts to start Wave 5 visual asset work
    Then the enforcement system blocks the action
    And Phil sees the specific section and PDC items that remain RED

  Scenario: PDC gate allows Wave 5 when all sections have GREEN PDCs
    Given Phil has an active proposal with all sections drafted
    And all sections have Tier 1 and Tier 2 PDCs GREEN
    When Phil starts Wave 5 visual asset work
    Then the action proceeds normally

  # --- Deadline Blocking ---

  Scenario: Deadline blocking surfaces critical warning
    Given Phil has an active proposal in Wave 5
    And 3 days remain until the deadline
    And Wave 5 is not complete
    When Phil checks proposal status
    Then Phil sees a critical deadline warning
    And Phil sees a suggestion to submit with available work or skip non-essential waves

  Scenario: Deadline blocking does not trigger above critical threshold
    Given Phil has an active proposal in Wave 5
    And 14 days remain until the deadline
    When Phil checks proposal status
    Then no deadline blocking warning is displayed

  # --- Submission Immutability ---

  @skip
  Scenario: Submission immutability prevents edits to submitted artifacts
    Given AF243-001 has been submitted with confirmation recorded
    When Phil attempts to write to any file under the proposal artifact directories
    Then the enforcement system blocks the write operation
    And the blocked attempt is recorded in the audit log

  @skip
  Scenario: Submission immutability allows reads of submitted artifacts
    Given AF243-001 has been submitted with confirmation recorded
    When Phil reads a submitted artifact
    Then the read proceeds normally

  # --- Corpus Integrity ---

  @skip
  Scenario: Corpus integrity blocks modification of win/loss tags
    Given AF243-001 has a win/loss tag of "not_selected"
    When any process attempts to change the tag to "awarded"
    Then the enforcement system blocks the modification
    And Phil sees "Win/loss tags are append-only and cannot be modified"

  @skip
  Scenario: Corpus integrity allows appending new outcome tags
    Given AF243-001 has no outcome tag recorded
    When the outcome is recorded as "not_selected"
    Then the outcome tag is appended successfully

  # --- Audit Log ---

  @skip
  Scenario: PES audit log records all C3 enforcement actions
    Given PES has blocked 3 actions during Waves 5-8
    When Phil reviews the audit log
    Then all 3 blocked actions are recorded with timestamps, rule names, and details

  # --- Configuration ---

  @skip
  @property
  Scenario: All C3 enforcement rules are configurable
    Given any C3 enforcement rule defined in pes-config.json
    When the rule is enabled or disabled via configuration
    Then the enforcement engine respects the configuration setting
    And existing C1 invariants continue to function
