Feature: Quality Summary and Style Consistency
  As a solo SBIR proposal writer completing figure generation
  I want a quality summary that checks style consistency and flags outliers
  So that I can fix issues before assembling the final document

  Background:
    Given the visual asset service is available

  # --- US-VAQ-3: Style Profile Validation ---

  # Happy path: complete style profile validates
  @us-vaq-3
  Scenario: Style profile with all required fields passes validation
    Given a style profile with agency "Navy" and domain "maritime/naval"
    And palette primary "#003366" and secondary "#6B7B8D"
    And tone "technical-authoritative" and detail level "high"
    When the style profile is validated
    Then the profile passes validation

  # Error: missing primary palette color
  @us-vaq-3
  Scenario: Style profile without primary palette color fails validation
    Given a style profile with agency "Navy" and domain "maritime/naval"
    And palette with secondary "#6B7B8D" but no primary color
    When the style profile is validated
    Then a validation error indicates primary color is required

  # Error: missing secondary palette color
  @us-vaq-3
  Scenario: Style profile without secondary palette color fails validation
    Given a style profile with agency "Air Force" and domain "aerospace"
    And palette with primary "#191970" but no secondary color
    When the style profile is validated
    Then a validation error indicates secondary color is required

  # Error: invalid detail level
  @us-vaq-3
  Scenario: Style profile with invalid detail level fails validation
    Given a style profile with detail level "extreme"
    When the style profile is validated
    Then a validation error indicates detail level must be "low", "medium", or "high"

  # Edge: style profile with no avoid list is valid
  @us-vaq-3
  Scenario: Style profile with empty avoid list passes validation
    Given a style profile with all required fields
    And the avoid list is empty
    When the style profile is validated
    Then the profile passes validation

  # Edge: unknown agency with generic fallback
  @us-vaq-3
  Scenario: Style profile for unknown agency uses generic domain
    Given a style profile with agency "NIST" and domain "generic"
    And palette primary "#336699" and secondary "#999999"
    And tone "professional" and detail level "medium"
    When the style profile is validated
    Then the profile passes validation

  # --- US-VAQ-3: Style Profile YAML Persistence ---

  # Happy path: style profile roundtrip
  @us-vaq-3
  Scenario: Style profile written as YAML and read back matches original
    Given a style profile for agency "Navy" with palette primary "#003366" and secondary "#6B7B8D"
    When the style profile is saved to disk and loaded back
    Then the loaded profile matches the original

  # --- US-VAQ-5: Quality Outlier Detection ---

  # Happy path: no outliers when ratings are consistent
  @us-vaq-5
  Scenario: No quality outliers when all figures rate within 2 points of average
    Given Figure 1 has average rating 4.2
    And Figure 3 has average rating 4.0
    And Figure 6 has average rating 3.8
    When quality outliers are checked
    Then no figures are flagged as outliers

  # Happy path: outlier flagged when 2+ points below average
  @us-vaq-5
  Scenario: Figure flagged as outlier when composition is 2 points below proposal average
    Given the proposal average for composition is 4.2
    And Figure 5 has composition rated 2
    When quality outliers are checked
    Then Figure 5 is flagged as an outlier for composition

  # Edge: outlier at exact threshold (2 points below)
  @us-vaq-5
  Scenario: Figure at exactly 2 points below average is flagged
    Given the proposal average for labels is 4.0
    And Figure 3 has labels rated 2
    When quality outliers are checked
    Then Figure 3 is flagged as an outlier for labels

  # Edge: figure 1 point below average is not flagged
  @us-vaq-5
  Scenario: Figure 1 point below average is not flagged
    Given the proposal average for accuracy is 4.0
    And Figure 2 has accuracy rated 3
    When quality outliers are checked
    Then Figure 2 is not flagged as an outlier

  # --- US-VAQ-5: Style Consistency Checking ---

  # Happy path: all figures use approved palette
  @us-vaq-5
  Scenario: All figures match approved style profile palette
    Given the approved palette is "#003366, #6B7B8D, #FF6B35, #2B7A8C"
    And Figure 1 prompt contains palette colors "#003366" and "#6B7B8D"
    And Figure 3 prompt contains palette colors "#003366" and "#6B7B8D"
    When style consistency is checked
    Then style consistency is "PASS"

  # Error: figure uses unapproved color
  @us-vaq-5
  Scenario: Figure with unapproved palette color flagged as inconsistent
    Given the approved palette is "#003366, #6B7B8D, #FF6B35, #2B7A8C"
    And Figure 6 prompt contains palette color "#1A5F6D" not in the approved palette
    When style consistency is checked
    Then style consistency is "WARN" for Figure 6
    And the warning identifies "#1A5F6D" as the unapproved color
