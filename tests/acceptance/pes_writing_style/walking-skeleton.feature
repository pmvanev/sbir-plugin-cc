Feature: PES Writing Style Gate Enforcement Walking Skeleton
  As Dr. Rafael Moreno, a PI writing an SBIR proposal,
  I want PES to enforce writing style selection before drafting
  So that the writer agent cannot bypass the style conversation and produce inconsistent prose

  @walking_skeleton
  Scenario: Writer is blocked from drafting a section when no quality preferences exist and style selection was not skipped
    Given Dr. Moreno's proposal "SF25D-T1201" is at Wave 4 (drafting)
    And no quality preferences file exists at the global configuration location
    And the proposal does not have a writing style selection skip marker
    And the enforcement rules are loaded from the standard configuration
    When the writer agent attempts to write a section draft to the drafting directory
    Then the action is blocked
    And the block reason explains that writing style selection must be completed first
    And the block is recorded in the audit trail
