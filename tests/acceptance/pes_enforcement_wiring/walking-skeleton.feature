Feature: PES Enforcement Wiring Walking Skeletons
  As Phil Santos, a small business engineer preparing SBIR proposals,
  I want the enforcement system to automatically protect me from risky actions
  So that I avoid wasted effort, corrupted data, and accidental post-submission changes

  # Walking Skeleton 1: PDC gate blocks drafting when prerequisites are incomplete
  # Validates: real config -> rule loader -> engine dispatch -> PDC evaluator -> BLOCK
  @walking_skeleton
  Scenario: Engineer is blocked from drafting when pre-draft checklist items are incomplete
    Given Phil's proposal "AF243-001" has a pre-draft checklist with section "technical_approach" showing Tier 1 RED for "TRL justification missing"
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts to begin Wave 5 drafting work
    Then the action is blocked
    And Phil sees "Section technical_approach: Tier 1 RED (TRL justification missing)" in the block reason

  # Walking Skeleton 2: Submitted proposal is locked from all modifications
  # Validates: real config -> rule loader -> engine dispatch -> submission evaluator -> BLOCK
  @walking_skeleton
  Scenario: Engineer cannot modify a submitted proposal
    Given Phil's proposal "AF243-001" has been submitted and marked as finalized
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts any action on the proposal
    Then the action is blocked
    And Phil sees "Proposal AF243-001 is submitted. Artifacts are read-only."

  # Walking Skeleton 3: Outcome tag is protected from accidental overwrite
  # Validates: real config -> rule loader -> engine dispatch -> corpus evaluator -> BLOCK
  @walking_skeleton
  Scenario: Engineer cannot accidentally overwrite a recorded proposal outcome
    Given Phil's proposal "AF243-001" has a recorded outcome of "win"
    And Phil requests to change the outcome to "loss"
    And the enforcement rules are loaded from the standard configuration
    When Phil attempts to record a different outcome
    Then the action is blocked
    And Phil sees "Win/loss tags are append-only and cannot be modified"
