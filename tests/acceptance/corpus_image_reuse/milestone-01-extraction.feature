Feature: Image Extraction During Corpus Ingestion
  As a PI with past proposals
  I want images automatically extracted when I add documents to my corpus
  So that I have a searchable catalog of reusable figures

  Background:
    Given the image extraction system is available

  # --- US-CIR-001: Image Extraction ---

  # Happy path: extract images from a PDF
  @skip
  Scenario: Extract embedded images from a PDF during corpus ingestion
    Given Dr. Vasquez has a PDF proposal "AF243-001" with 8 embedded images
    And the images include formats PNG and JPEG
    When she adds the proposal to her corpus
    Then 8 images are extracted and stored in the image catalog
    And each image has a registry entry with source "AF243-001"
    And the ingestion report shows "8 images extracted"

  # Happy path: extract images from a DOCX
  @skip
  Scenario: Extract embedded images from a DOCX during corpus ingestion
    Given Dr. Vasquez has a DOCX proposal "N244-012" with 4 embedded images
    When she adds the proposal to her corpus
    Then 4 images are extracted and stored in the image catalog
    And each image has a registry entry with source "N244-012"

  # Happy path: classify extracted images by figure type
  @skip
  Scenario: Classify extracted images using caption and context
    Given an image extracted from "AF243-001" page 7
    And the caption reads "Figure 3: CDES System Architecture"
    When classification runs
    Then the image is classified as "system-diagram"

  @skip
  Scenario: Classify image as TRL roadmap from caption keywords
    Given an image extracted from "AF243-001" page 12
    And the caption reads "Figure 7: Technology Readiness Level Maturation Plan"
    When classification runs
    Then the image is classified as "trl-roadmap"

  @skip
  Scenario: Image with no recognizable caption classified as unclassified
    Given an image extracted from "N244-012" page 3
    And the caption reads "Figure 2: Prototype Assembly"
    When classification runs
    Then the image is classified as "unclassified"

  # Happy path: assess quality by DPI
  @skip
  Scenario: High-resolution image assessed as high quality
    Given an extracted image has resolution 2048x1536 at 300 DPI
    When quality assessment runs
    Then quality level is "high"

  @skip
  Scenario: Medium-resolution image assessed as medium quality
    Given an extracted image has resolution 1024x768 at 200 DPI
    When quality assessment runs
    Then quality level is "medium"

  @skip
  Scenario: Low-resolution image assessed as low quality
    Given an extracted image has resolution 640x480 at 72 DPI
    When quality assessment runs
    Then quality level is "low"

  # Happy path: deduplicate identical images across proposals
  @skip
  Scenario: Identical images from different proposals stored once
    Given "AF243-001" and "DARPA-HR-22" both contain the same facilities photo
    When both proposals are ingested
    Then the image file is stored once in the catalog
    And the registry entry lists both "AF243-001" and "DARPA-HR-22" as sources

  # Error path: extraction failure for unsupported encoding
  @skip
  Scenario: Unsupported image encoding fails gracefully
    Given a PDF contains 8 images, one encoded in JBIG2 format on page 14
    When the proposal is ingested
    Then 7 images are extracted successfully
    And the failure is logged for page 14 with reason "unsupported encoding"
    And the ingestion report shows "7 images extracted, 1 failed"

  # Error path: text-only document has no images
  @skip
  Scenario: Text-only document reports zero images without error
    Given Dr. Vasquez has a PDF proposal "budget-narrative" with 0 embedded images
    When she adds the proposal to her corpus
    Then the ingestion report shows "0 images extracted"
    And no image registry entries are created for "budget-narrative"

  # Edge case: re-ingesting same directory skips existing images
  @skip
  Scenario: Re-ingesting a directory does not duplicate existing images
    Given Dr. Vasquez has already ingested "AF243-001" with 8 images
    When she ingests the same directory again
    Then no new images are extracted
    And existing registry entries remain unchanged

  # Edge case: batch ingestion across multiple proposals
  @skip
  Scenario: Batch ingestion extracts images from all documents
    Given Dr. Vasquez has a directory with 3 proposals containing 8, 6, and 9 images respectively
    When she ingests the entire directory
    Then 23 images are extracted across all proposals
    And the ingestion report shows totals by figure type and quality level

  @property @skip
  Scenario: Content hash is deterministic for identical image bytes
    Given any two images with identical byte content
    When their content hashes are computed
    Then both hashes are identical regardless of source proposal or page number
