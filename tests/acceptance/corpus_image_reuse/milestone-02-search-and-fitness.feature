Feature: Image Search, Browse, and Fitness Assessment
  As a PI drafting a new proposal
  I want to search and assess corpus images for reuse fitness
  So that I can quickly find the right proven figure and evaluate if it fits

  Background:
    Given the image extraction system is available

  # --- US-CIR-002: Image Search and Browsing ---

  # Happy path: list images with type filter
  @skip
  Scenario: List images filtered by figure type
    Given the image catalog contains 23 images from 3 proposals
    And 8 images are classified as "system-diagram"
    When Dr. Vasquez lists images filtered by type "system-diagram"
    Then 8 images are displayed
    And each result shows source proposal, agency, caption, quality, and page number

  # Happy path: list images with outcome filter
  @skip
  Scenario: List images filtered by proposal outcome
    Given the image catalog contains 23 images from 3 proposals
    And 17 images are from winning proposals
    When Dr. Vasquez lists images filtered by outcome "WIN"
    Then 17 images are displayed

  # Happy path: search with relevance ranking
  @skip
  Scenario: Search returns relevance-ranked results favoring agency match
    Given the image catalog contains system diagrams from "AF243-001" (USAF, WIN) and "DARPA-HR-22" (DARPA, WIN)
    And Dr. Vasquez is working on a USAF proposal
    When she searches for "system architecture"
    Then "AF243-001" results score higher than "DARPA-HR-22" results
    And results are sorted by descending relevance score

  # Error path: search with no matches
  @skip
  Scenario: Search with no matches suggests browsing by type
    Given the image catalog contains 23 images
    And no images match the query "quantum entanglement sensor"
    When Dr. Vasquez searches for "quantum entanglement sensor"
    Then the result shows "No matching images found"
    And suggests listing images by type as an alternative

  # Error path: empty catalog shows onboarding guidance
  @skip
  Scenario: Empty image catalog suggests adding proposals first
    Given the image catalog is empty
    When Dr. Vasquez lists all images
    Then the result shows "No images in catalog"
    And suggests running corpus add to populate the catalog

  # --- US-CIR-003: Image Fitness Assessment ---

  # Happy path: full fitness assessment for a high-quality match
  @skip
  Scenario: High-quality recent image from same agency passes all fitness checks
    Given Dr. Vasquez has a corpus image from "AF243-001" at 300 DPI extracted 8 months ago
    And the image is classified as "system-diagram" with agency "USAF"
    And her current proposal targets agency "USAF"
    When she views the fitness assessment
    Then quality shows "PASS" with "300 DPI"
    And freshness shows "OK" with "8 months"
    And agency match shows "YES"

  # Happy path: caption analysis identifies proposal-specific terms
  @skip
  Scenario: Caption analysis warns about proposal-specific terminology
    Given a corpus image has caption "Figure 3: CDES System Architecture for Maritime Defense"
    And "CDES" appears only in the source proposal context
    When caption analysis runs
    Then "CDES" is flagged as a proposal-specific term
    And a label warning is generated for the caption

  # Error path: stale image triggers freshness warning
  @skip
  Scenario: Image from 26-month-old proposal shows freshness warning
    Given a corpus image was extracted from a proposal submitted 26 months ago
    When Dr. Vasquez views the fitness assessment
    Then freshness shows "STALE" with "26 months"
    And the warning mentions potential changes to team or approach

  # Error path: low-resolution image fails quality check
  @skip
  Scenario: Low-resolution image fails quality assessment
    Given a corpus image has 72 DPI resolution
    When Dr. Vasquez views the fitness assessment
    Then quality shows "FAIL" with "72 DPI"
    And suggests generating a new figure based on this design

  # Happy path: flag image for compliance review
  @skip
  Scenario: Flag image with compliance concern
    Given Dr. Vasquez suspects image 7 may contain government-furnished material
    When she flags the image with reason "possible government-furnished"
    Then the registry marks the image with the compliance flag
    And the image shows a compliance warning in subsequent listings

  # Error path: unknown attribution triggers compliance notice
  @skip
  Scenario: Image with unknown origin shows compliance notice
    Given a corpus image has attribution type "unknown"
    When Dr. Vasquez views the fitness assessment
    Then the attribution section shows "UNKNOWN"
    And a compliance notice recommends verifying the image source

  # Edge case: freshness boundary at exactly 12 months
  @skip
  Scenario: Image at exactly 12-month boundary shows OK freshness
    Given a corpus image was extracted from a proposal submitted exactly 12 months ago
    When Dr. Vasquez views the fitness assessment
    Then freshness shows "OK"

  # Edge case: freshness boundary at exactly 24 months
  @skip
  Scenario: Image at exactly 24-month boundary shows WARNING freshness
    Given a corpus image was extracted from a proposal submitted exactly 24 months ago
    When Dr. Vasquez views the fitness assessment
    Then freshness shows "WARNING"

  @property @skip
  Scenario: Quality level is always determined by DPI thresholds
    Given any extracted image with a known DPI value
    When quality assessment runs
    Then high is assigned for 300 or above, medium for 150 to 299, and low for below 150
