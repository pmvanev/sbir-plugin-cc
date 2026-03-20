Feature: Engineered Prompt Generation
  As a solo SBIR proposal writer
  I want prompts that include composition, style, labels, and resolution directives
  So that generated figures look like professional technical illustrations

  Background:
    Given the visual asset service is available

  # --- US-VAQ-1: Prompt Template Rendering ---

  # Happy path: prompt template renders with all sections
  @us-vaq-1
  Scenario: Prompt template renders all five sections from figure specification
    Given a prompt template with placeholders for composition, style, labels, avoid, and resolution
    And figure type is "system-diagram" with description "Compact DE weapon system architecture"
    And the style profile has palette primary "#003366" and tone "technical-authoritative"
    When the prompt template is rendered
    Then the rendered prompt contains a COMPOSITION section
    And the rendered prompt contains a STYLE section with "#003366"
    And the rendered prompt contains a LABELS section
    And the rendered prompt contains an AVOID section
    And the rendered prompt contains a RESOLUTION section

  # Happy path: style profile values injected into prompt
  @us-vaq-1
  Scenario: Style profile palette colors appear in the rendered prompt
    Given a prompt template for figure type "concept"
    And the style profile has palette primary "#003366" and secondary "#6B7B8D"
    When the prompt template is rendered
    Then the rendered prompt includes both "#003366" and "#6B7B8D"

  # Happy path: figure plan metadata injected
  @us-vaq-1
  Scenario: Figure description from plan appears in rendered prompt
    Given a prompt template for figure type "block-diagram"
    And the figure description is "Three-tier sensor processing pipeline"
    When the prompt template is rendered
    Then the rendered prompt includes "Three-tier sensor processing pipeline"

  # Edge: resolution defaults when not specified
  @us-vaq-1
  Scenario: Default resolution and aspect ratio used when not specified
    Given a prompt template for figure type "system-diagram"
    And no resolution or aspect ratio is specified in the figure plan
    When the prompt template is rendered
    Then the rendered prompt includes resolution "2K"
    And the rendered prompt includes aspect ratio "16:9"

  # Error: template rendering with missing style profile
  @us-vaq-1
  Scenario: Prompt rendered without style profile uses generic defaults
    Given a prompt template for figure type "concept"
    And no style profile exists
    When the prompt template is rendered
    Then the rendered prompt contains a STYLE section with generic professional defaults
    And no rendering error occurs

  # Error: empty figure description
  @us-vaq-1
  Scenario: Prompt rendered with empty description omits description gracefully
    Given a prompt template for figure type "system-diagram"
    And the figure description is empty
    When the prompt template is rendered
    Then the rendered prompt does not contain an empty LABELS section
    And the COMPOSITION section still contains figure-type directives

  # --- US-VAQ-1: Prompt Hash for Audit ---

  # Happy path: prompt hash is deterministic
  @us-vaq-1
  Scenario: Same prompt text produces the same hash
    Given a rendered prompt with text "Technical illustration of directed energy system"
    When the prompt hash is computed twice
    Then both hash values are identical

  # Boundary: different prompts produce different hashes
  @us-vaq-1
  Scenario: Different prompt text produces different hashes
    Given prompt A with text "Technical illustration of directed energy system"
    And prompt B with text "Technical illustration of radar processing unit"
    When the prompt hashes are computed
    Then the two hashes are different
