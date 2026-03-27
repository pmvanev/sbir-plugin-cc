Feature: PES Outline Gate Enforcement Walking Skeleton
  As Dr. Rafael Moreno, a PI writing an SBIR proposal,
  I want PES to prevent drafting before the approved outline exists
  So that the writer agent cannot fabricate section structure without the approved plan

  @walking_skeleton
  Scenario: Writer is blocked from drafting a section when no approved outline exists
    Given Dr. Moreno's proposal "SF25D-T1201" is at Wave 4 (drafting)
    And no approved outline has been created in the outline directory
    And the enforcement rules are loaded from the standard configuration
    When the writer agent attempts to write a draft section to the drafting directory
    Then the action is blocked
    And the block reason explains that the proposal outline must be completed first
    And the block is recorded in the audit trail
