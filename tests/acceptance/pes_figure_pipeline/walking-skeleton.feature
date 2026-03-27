Feature: PES Figure Pipeline Enforcement Walking Skeleton
  As Dr. Rafael Moreno, a PI writing an SBIR proposal,
  I want PES to prevent figure generation before planning is complete
  So that the formatter agent follows the rigorous pipeline and produces professional figures

  @walking_skeleton
  Scenario: Formatter is blocked from generating a figure when no figure specification plan exists
    Given Dr. Moreno's proposal "SF25D-T1201" is at Wave 5 (visual assets)
    And no figure specification plan has been created in the visual assets directory
    And the enforcement rules are loaded from the standard configuration
    When the formatter agent attempts to write a figure file to the visual assets directory
    Then the action is blocked
    And the block reason explains that figure specifications must be created first
    And the block is recorded in the audit trail
