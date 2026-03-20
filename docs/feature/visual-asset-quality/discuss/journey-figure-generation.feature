Feature: High-Quality Figure Generation
  As a solo SBIR proposal writer targeting DoD/NASA agencies,
  Phil needs to produce professional, domain-appropriate visual assets
  through engineered prompts, structured critique, and optional TikZ generation
  so that his proposal figures enhance rather than undermine evaluator impressions.

  Background:
    Given Phil has a solicitation for topic "N241-033" targeting Navy directed energy systems
    And the figure plan from Wave 3 contains 6 planned figures
    And GEMINI_API_KEY is set for Nano Banana generation
    And the proposal format is LaTeX with pdflatex available

  # Step 1: Style Analysis (JS-3: Domain-Aware Visual Style)

  Scenario: Recommend visual style from solicitation analysis
    When Phil runs "/proposal wave visuals"
    Then the system analyzes the solicitation agency and domain
    And recommends a "maritime/naval" visual style
    And the palette includes navy blue and steel gray tones
    And the tone is "technical-authoritative"
    And TikZ is listed as available

  Scenario: Phil adjusts recommended palette
    Given the system recommended a maritime/naval palette
    When Phil selects "adjust palette" and replaces ocean teal with signal green
    Then the style profile is updated with the new palette
    And subsequent prompts use the adjusted colors

  Scenario: Skip style analysis for non-Nano-Banana proposals
    Given all 4 figures use Mermaid or SVG generation methods
    When Phil runs "/proposal wave visuals"
    Then style analysis is offered but marked as optional
    And Phil can skip to figure specifications without a style profile

  # Step 2: Prompt Preview (JS-1: Professional Figure Generation)

  Scenario: Engineered prompt shown before Nano Banana generation
    Given Phil approved the maritime/naval visual style
    And Figure 3 is a system architecture diagram for section 3.1
    When Phil runs "/proposal draft figure system-architecture"
    Then the system displays an engineered prompt with composition, style, label, and avoid sections
    And the prompt uses the approved palette colors "#003366" and "#6B7B8D"
    And Phil can edit the prompt before generation

  Scenario: Phil edits prompt to add specific component
    Given the engineered prompt for Figure 3 is displayed
    When Phil adds "Include fiber-optic data bus connecting all subsystems" to the prompt
    Then the updated prompt includes the fiber-optic data bus instruction
    And generation proceeds with Phil's addition

  Scenario: TikZ method offered for diagram figures in LaTeX proposals
    Given the proposal format is LaTeX
    And Figure 2 is a system block diagram
    When Phil views the prompt preview for Figure 2
    Then both Nano Banana and TikZ are listed as available methods
    And Phil can switch to TikZ before generation

  # Step 3: Generate (JS-1, JS-4)

  Scenario: Nano Banana figure generated with engineered prompt
    Given Phil confirmed the prompt for Figure 3
    When the system generates the figure via Nano Banana
    Then a PNG file is written to "wave-5-visuals/system-architecture.png"
    And the figure log records method "nano-banana" and the prompt hash
    And the figure is presented for structured critique

  Scenario: TikZ figure compiled and verified
    Given Phil chose TikZ for Figure 2 "System Block Diagram"
    When the system generates TikZ code and compiles with pdflatex
    Then compilation completes with 0 errors and 0 warnings
    And a PDF preview is rendered for review
    And the .tex source file is saved alongside the preview

  Scenario: TikZ compilation fails with SVG fallback offered
    Given Phil chose TikZ for Figure 2
    When the system generates TikZ code that fails to compile
    Then the compilation error message is displayed
    And Phil is offered: "edit TikZ source", "switch to SVG", or "defer to external"
    And no broken figure is written to the artifacts directory

  # Step 4: Structured Critique (JS-2: Iterative Figure Refinement)

  Scenario: Structured critique with five categories
    Given Figure 3 has been generated via Nano Banana
    When Phil reviews the figure
    Then the system presents 5 critique categories: composition, labels, accuracy, style match, scale
    And each category accepts a 1-5 rating
    And Phil can add free-text notes for specific issues

  Scenario: Low-rated categories flagged for refinement
    Given Phil rated Figure 3 labels 2/5 and scale 3/5
    And Phil noted "Labels too small and overlapping"
    When Phil submits the critique
    Then categories Labels and Scale are flagged for refinement
    And the system prepares targeted prompt adjustments

  Scenario: All categories rated 3+ triggers approval option
    Given Phil rated all 5 categories 3 or higher for Figure 1
    When Phil submits the critique
    Then "approve as-is" is prominently offered
    And refinement is available but not required

  # Step 5: Refine (JS-2: Iterative Figure Refinement)

  Scenario: Prompt refined based on critique feedback
    Given Phil rated Labels 2/5 with note "too small, overlap"
    When the system prepares refinement round 1 of 3
    Then the prompt adds "large clear sans-serif labels, no overlap, minimum 12pt equivalent"
    And the prompt removes the original "10pt" label instruction
    And the adjustments are shown to Phil before regeneration

  Scenario: Refinement preserves well-rated elements
    Given Phil rated Style Match 5/5 and Composition 4/5
    When the system prepares prompt adjustments
    Then the style and composition sections of the prompt are unchanged
    And only flagged categories receive prompt modifications

  Scenario: Maximum 3 refinement iterations then escape
    Given Phil has completed 3 refinement rounds for Figure 6
    And the figure Labels category is still rated 2/5
    When the 3rd iteration result is presented
    Then Phil is offered: approve current, replace method, or defer to external
    And no 4th refinement round is offered
    And the system suggests "For complex labeling, TikZ or external editing may be more precise"

  # Step 6: Approve

  Scenario: Figure approved after successful refinement
    Given Phil completed 2 refinement rounds for Figure 3
    And all categories now rate 3 or higher
    When Phil approves Figure 3
    Then the figure log status changes to "approved"
    And quality ratings are recorded: composition 4, labels 4, accuracy 4, style 5, scale 4
    And Phil is presented with the next figure in the plan

  Scenario: Approve on first attempt without refinement
    Given Phil rated all categories 4 or 5 for Figure 4 on first review
    When Phil selects "approve as-is"
    Then Figure 4 status changes to "approved" with 0 iterations
    And the system proceeds to Figure 5

  # Step 7: Conclude

  Scenario: Quality summary with style consistency check
    Given all 6 figures have been approved
    And 3 figures were generated via Nano Banana with the maritime/naval style
    And 1 figure was generated via TikZ
    And 2 figures were generated via Mermaid
    When the system produces the Wave 5 quality summary
    Then style consistency is "PASS" for all Nano Banana figures
    And cross-reference validation shows all_valid = true
    And the average quality score across critiqued figures is displayed
    And the figure log is complete with all methods, iterations, and statuses

  Scenario: Style inconsistency detected at conclusion
    Given 3 Nano Banana figures were approved
    And Figure 6 was regenerated after a style profile change
    When the system checks style consistency
    Then style consistency is "WARN" with note "Figure 6 uses updated palette"
    And Phil is offered to regenerate Figure 6 with the original approved style
