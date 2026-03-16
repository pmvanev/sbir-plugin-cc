Feature: Image Adaptation and Formatter Integration
  As a PI selecting a corpus image for my new proposal
  I want the caption adapted and the formatter to handle corpus-reused figures
  So that reused images integrate seamlessly without manual caption errors

  Background:
    Given the image extraction system is available

  # --- US-CIR-004: Image Adaptation and Reuse Selection ---

  # Happy path: adapt caption and copy image for reuse
  @skip
  Scenario: Select image for reuse with adapted caption
    Given Dr. Vasquez has reviewed image "af243-001-p07-img01" with caption "Figure 3: CDES System Architecture"
    And "CDES" is identified as a proposal-specific term
    When she selects it for reuse as Figure 3 in section "technical-approach"
    Then the image file is copied to the proposal artifacts directory
    And the adapted caption reads "Figure 3: System Architecture"
    And the original and adapted captions are presented for comparison
    And the figure inventory gains an entry with method "corpus-reuse"
    And the figure log records source attribution from "AF243-001"

  # Happy path: generic caption needs no adaptation
  @skip
  Scenario: Generic caption reused with only figure number updated
    Given an image has caption "Figure 4: Organization Chart"
    And no proposal-specific terms are detected
    When Dr. Vasquez selects it for reuse as Figure 2
    Then the adapted caption reads "Figure 2: Organization Chart"
    And no caption change warnings are generated

  # Happy path: manual review items listed for embedded text
  @skip
  Scenario: Manual review items listed for diagram with embedded labels
    Given Dr. Vasquez has selected a system diagram for reuse
    And the diagram is classified as "system-diagram"
    When adaptation generates review items
    Then potential label review items are listed
    And the review advises opening the image in an editor for label changes

  # Error path: compliance-flagged image blocked from reuse
  @skip
  Scenario: Compliance-flagged image cannot be selected for reuse
    Given image "darpa-hr22-p05-img02" is flagged as "possible government-furnished"
    When Dr. Vasquez attempts to select it for reuse
    Then the selection is blocked with message "Image is flagged for compliance review"
    And suggests clearing the flag after verification before reuse

  # Error path: image not found in registry
  @skip
  Scenario: Selecting a nonexistent image returns clear error
    Given the image catalog does not contain image "nonexistent-id"
    When Dr. Vasquez attempts to select "nonexistent-id" for reuse
    Then the result shows "Image not found in catalog"

  # --- US-CIR-005: Formatter Integration ---

  # Happy path: formatter routes corpus-reuse to review instead of generation
  @skip
  Scenario: Formatter skips generation for corpus-reuse figures
    Given the figure inventory has Figure 3 with method "corpus-reuse"
    And Figure 5 has method "svg" for standard generation
    When the formatter processes the figure inventory
    Then Figure 3 is not sent to the figure generator
    And Figure 5 is sent to the figure generator as usual
    And Figure 3 is presented for human review

  # Happy path: approve corpus-reused figure
  @skip
  Scenario: Approved corpus-reuse figure is ready for document assembly
    Given Figure 3 has method "corpus-reuse" and status "pending-manual-review"
    When Dr. Vasquez approves Figure 3
    Then Figure 3 status changes to "approved"
    And Figure 3 is ready for document assembly

  # Happy path: replace corpus-reuse with generated figure
  @skip
  Scenario: Replace corpus-reuse figure with standard generation
    Given Figure 3 has method "corpus-reuse" and status "pending-manual-review"
    When Dr. Vasquez chooses to replace Figure 3
    Then Figure 3 method changes to standard generation
    And the figure log records the original corpus-reuse as "replaced"

  # Happy path: cross-reference validation includes corpus-reused figures
  @skip
  Scenario: Cross-reference validation resolves corpus-reuse figure references
    Given Figure 3 is approved with method "corpus-reuse"
    And the technical approach section references "Figure 3"
    When cross-reference validation runs
    Then the reference to Figure 3 resolves successfully

  # Error path: orphaned reference to deleted corpus-reuse file
  @skip
  Scenario: Missing corpus-reuse file detected during cross-reference validation
    Given Figure 3 has method "corpus-reuse" and status "approved"
    And the image file for Figure 3 has been deleted from artifacts
    When cross-reference validation runs
    Then Figure 3 is flagged as an orphaned reference
    And the validation warns about the missing image file

  # Edge case: existing generation methods unaffected by corpus-reuse routing
  @skip
  Scenario: Standard generation methods continue to work alongside corpus-reuse
    Given the figure inventory has Figure 1 method "svg", Figure 2 method "mermaid", Figure 3 method "corpus-reuse"
    When the formatter processes all figures
    Then Figure 1 and Figure 2 are sent to generation
    And Figure 3 is routed to review
    And all three figures appear in the cross-reference log
