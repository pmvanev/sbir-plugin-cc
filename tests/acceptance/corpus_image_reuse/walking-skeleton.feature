Feature: Corpus Image Reuse Walking Skeleton
  As a PI with past proposals containing reusable figures
  I want to extract, find, assess, adapt, and reuse images from my corpus
  So that I can build new proposals faster using proven visual assets

  # Walking Skeleton 1: Extract images during corpus ingestion and find them
  # Validates: corpus add -> extraction -> registry -> search -> results
  @walking_skeleton
  Scenario: PI extracts images from past proposals and finds them by search
    Given Dr. Vasquez has ingested proposal "AF243-001" containing 3 embedded figures
    And the figures include a system diagram captioned "Figure 3: CDES System Architecture"
    When Dr. Vasquez searches for "system architecture" images
    Then 1 matching image is returned
    And the match shows source proposal "AF243-001" with caption containing "System Architecture"

  # Walking Skeleton 2: Assess image fitness and select for reuse
  # Validates: search -> show -> fitness assessment -> use -> adapted caption -> figure inventory
  @walking_skeleton @skip
  Scenario: PI assesses a corpus image and selects it for reuse in a new proposal
    Given Dr. Vasquez has a corpus image from proposal "AF243-001" at 300 DPI extracted 8 months ago
    And her current proposal targets agency "USAF"
    When Dr. Vasquez views the fitness assessment for that image
    Then quality shows "PASS" and freshness shows "OK"
    And agency match shows "YES"
    When Dr. Vasquez selects the image for reuse as Figure 3 in "technical-approach"
    Then the image is copied to the proposal artifacts
    And the caption is adapted with proposal-specific term "CDES" removed
    And the figure inventory records the entry with method "corpus-reuse"

  # Walking Skeleton 3: Formatter routes corpus-reused figure to review
  # Validates: figure inventory -> formatter routing -> review -> approve -> ready for assembly
  @walking_skeleton @skip
  Scenario: Formatter presents corpus-reused figure for review instead of generating it
    Given the figure inventory has Figure 3 with method "corpus-reuse" and status "pending-manual-review"
    When the formatter processes the figure inventory
    Then Figure 3 is not sent to generation
    And Figure 3 is presented for review with options to approve, revise, or replace
    When Dr. Vasquez approves Figure 3
    Then Figure 3 status changes to "approved"
    And Figure 3 is ready for document assembly
