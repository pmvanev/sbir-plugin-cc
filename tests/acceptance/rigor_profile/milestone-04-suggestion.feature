Feature: Contextual Rigor Suggestion at Proposal Creation
  As an SBIR proposal author creating a new proposal
  I want a contextual suggestion based on my proposal metadata
  So that I discover the rigor feature naturally and make informed choices

  # --- Happy Path ---

  Scenario: High-value Phase II proposal receives thorough suggestion
    Given a proposal is created with fit score 85 and phase "II"
    When the rigor suggestion is computed
    Then the suggestion recommends "thorough"

  Scenario: Low-value Phase I proposal receives lean suggestion
    Given a proposal is created with fit score 64 and phase "I"
    When the rigor suggestion is computed
    Then the suggestion recommends "lean"

  Scenario: Mid-range proposal receives no suggestion
    Given a proposal is created with fit score 75 and phase "I"
    When the rigor suggestion is computed
    Then no rigor suggestion is provided

  # --- Boundary Cases ---

  Scenario: Fit score exactly at 80 with Phase II triggers thorough suggestion
    Given a proposal is created with fit score 80 and phase "II"
    When the rigor suggestion is computed
    Then the suggestion recommends "thorough"

  Scenario: Fit score exactly at 70 with Phase I gives no suggestion
    Given a proposal is created with fit score 70 and phase "I"
    When the rigor suggestion is computed
    Then no rigor suggestion is provided

  Scenario: Fit score 69 with Phase I triggers lean suggestion
    Given a proposal is created with fit score 69 and phase "I"
    When the rigor suggestion is computed
    Then the suggestion recommends "lean"

  # --- Error / Edge Paths ---

  Scenario: High fit score with Phase I gives no suggestion
    Given a proposal is created with fit score 90 and phase "I"
    When the rigor suggestion is computed
    Then no rigor suggestion is provided

  Scenario: Low fit score with Phase II gives no suggestion
    Given a proposal is created with fit score 60 and phase "II"
    When the rigor suggestion is computed
    Then no rigor suggestion is provided

  Scenario: Default profile is always standard regardless of suggestion
    Given a proposal is created with fit score 85 and phase "II"
    When the rigor suggestion is computed
    Then the suggestion recommends "thorough"
    And the default profile remains "standard"
