Feature: Agent Model Tier Resolution from Rigor Profile
  As an SBIR proposal author who has set a rigor level
  I want every agent to resolve its model tier from my rigor setting
  So that the quality dial actually controls agent behavior

  # --- Happy Path ---

  @skip
  Scenario: Writer resolves strongest at thorough rigor
    Given Elena has an active proposal "AF243-001" at "thorough" rigor
    When the model tier is resolved for the "writer" role
    Then the resolved model tier is "strongest"

  @skip
  Scenario: Researcher resolves standard at thorough rigor
    Given Elena has an active proposal "AF243-001" at "thorough" rigor
    When the model tier is resolved for the "researcher" role
    Then the resolved model tier is "standard"

  @skip
  Scenario: All agent roles resolve basic at lean rigor
    Given Marcus has an active proposal "N244-015" at "lean" rigor
    When the model tier is resolved for each agent role
    Then every agent role resolves to "basic" model tier

  @skip
  Scenario: Formatter resolves standard at thorough rigor
    Given Elena has an active proposal "AF243-001" at "thorough" rigor
    When the model tier is resolved for the "formatter" role
    Then the resolved model tier is "standard"

  # --- Behavioral Parameters ---

  @skip
  Scenario: Thorough profile provides 2 review passes
    Given Elena has an active proposal "AF243-001" at "thorough" rigor
    When the review configuration is resolved
    Then the review pass count is 2

  @skip
  Scenario: Lean profile provides 1 review pass
    Given Marcus has an active proposal "N244-015" at "lean" rigor
    When the review configuration is resolved
    Then the review pass count is 1

  @skip
  Scenario: Exhaustive profile provides 3 review passes
    Given Elena has an active proposal "AF243-001" at "exhaustive" rigor
    When the review configuration is resolved
    Then the review pass count is 3

  @skip
  Scenario: Thorough profile caps critique loops at 3 iterations
    Given Elena has an active proposal "AF243-001" at "thorough" rigor
    When the critique loop configuration is resolved
    Then the maximum critique iterations is 3

  @skip
  Scenario: Lean profile skips critique loops entirely
    Given Marcus has an active proposal "N244-015" at "lean" rigor
    When the critique loop configuration is resolved
    Then the maximum critique iterations is 0

  # --- Fallback Behavior ---

  @skip
  Scenario: Missing rigor configuration defaults to standard resolution
    Given Phil has a proposal "DA244-007" with no rigor configuration
    When the model tier is resolved for the "writer" role
    Then the resolved model tier is "standard"

  @skip
  Scenario: Missing rigor configuration provides standard review passes
    Given Phil has a proposal "DA244-007" with no rigor configuration
    When the review configuration is resolved
    Then the review pass count is 2

  # --- Property-Shaped ---

  @property
  @skip
  Scenario: Every profile defines a valid model tier for every agent role
    Given any valid rigor profile name
    When the profile definition is loaded
    Then every agent role has a model tier of basic, standard, or strongest

  @property
  @skip
  Scenario: Resolution chain is deterministic for any profile and role combination
    Given any valid rigor profile and agent role
    When the model tier is resolved
    Then the result is always the same for the same profile and role
