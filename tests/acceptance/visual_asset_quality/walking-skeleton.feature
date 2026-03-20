Feature: Visual Asset Quality Walking Skeleton
  As a solo SBIR proposal writer generating figures
  I want engineered prompts, structured critique, and TikZ support
  So that my proposal figures look professional and match my domain

  # Walking Skeleton 1: TikZ generation routed and result recorded
  # Validates: placeholder with tikz method -> VisualAssetService -> TikZ result with format and tracking fields
  # Driving port: VisualAssetService (domain service)
  @walking_skeleton
  Scenario: Phil generates a block diagram as TikZ and receives a tracked result
    Given Phil has a figure planned as "System Block Diagram" in section 3.1 using TikZ
    When Phil generates the figure through the visual asset service
    Then the result indicates the figure was generated as TikZ format
    And the result includes a prompt hash for audit traceability
    And the result includes the iteration count

  # Walking Skeleton 2: Style profile parsed and validated
  # Validates: YAML style profile -> parsing -> validation of required fields
  # Driving port: style profile parser (new domain utility)
  @walking_skeleton
  Scenario: Phil's approved style profile is loaded and all fields are present
    Given Phil has an approved style profile for agency "Navy" with domain "maritime/naval"
    And the palette includes primary "#003366" and secondary "#6B7B8D"
    When the style profile is loaded from disk
    Then the profile contains agency "Navy" and domain "maritime/naval"
    And the palette has at least primary and secondary colors
    And the detail level is one of "low", "medium", or "high"

  # Walking Skeleton 3: Critique ratings validated and low-rated categories identified
  # Validates: rating dict -> critique model -> flagged categories
  # Driving port: critique rating model (new domain utility)
  @walking_skeleton
  Scenario: Phil's critique identifies categories needing refinement
    Given Phil has rated Figure 3 with composition 4, labels 2, accuracy 4, style match 5, and scale 3
    When the critique ratings are evaluated
    Then "labels" is flagged for refinement
    And "composition", "accuracy", "style_match", and "scale_proportion" are not flagged
    And the average rating across all categories is 3.6
