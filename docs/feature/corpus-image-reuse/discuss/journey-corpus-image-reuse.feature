Feature: Corpus Image Reuse
  As a PI who writes multiple SBIR proposals,
  I want to extract, search, and reuse images from past proposals
  so I can save hours of figure recreation and leverage proven visual assets.

  Background:
    Given Dr. Elena Vasquez has a corpus with past proposals
    And proposal AF243-001 ("Compact Directed Energy") has outcome WIN
    And proposal N244-012 ("Autonomous UUV Navigation") has outcome LOSS
    And proposal DARPA-HR-22 ("Multi-Agent Autonomy") has outcome WIN

  # ──────────────────────────────────────────────────────────
  # Step 1: Image Extraction During Corpus Ingestion
  # Job Story: JS-1 (Recall and Retrieve), JS-4 (Build Library)
  # ──────────────────────────────────────────────────────────

  Scenario: Extract images from PDF during corpus ingestion
    Given Dr. Vasquez has a directory ~/proposals/2024-Q1/ containing 4 PDFs
    And AF243-001.pdf contains 8 embedded images including a system architecture diagram on page 7
    And N244-012.pdf contains 6 embedded images including a TRL roadmap on page 10
    When she runs "corpus add ~/proposals/2024-Q1/"
    Then the system ingests 4 documents into the text corpus registry
    And the system extracts 23 embedded images total
    And each extracted image is stored in .sbir/corpus/images/ with a deterministic filename
    And each image has a metadata entry in .sbir/corpus/image-registry.json
    And the ingestion report shows document counts and image extraction summary

  Scenario: Classify extracted images by figure type
    Given the system has extracted 23 images from proposal documents
    When classification runs on each extracted image
    Then each image is assigned a figure type from: system-diagram, block-diagram, trl-roadmap, org-chart, concept-illustration, market-landscape, chart, process-flow, comparison-table, unclassified
    And the classification uses surrounding text context and caption text as input
    And the ingestion summary groups images by figure type

  Scenario: Assess image quality during extraction
    Given the system has extracted an image from AF243-001.pdf page 7
    And the image has a resolution of 2048x1536 pixels at 300 DPI
    When quality assessment runs
    Then the quality level is "high" (>= 300 DPI)
    And the resolution dimensions and DPI are recorded in the image registry

  Scenario: Handle low-resolution image during extraction
    Given the system has extracted an image from N244-012.pdf page 15
    And the image has a resolution of 640x480 pixels at 72 DPI
    When quality assessment runs
    Then the quality level is "low" (< 150 DPI)
    And the image is still stored and indexed but flagged as low quality

  Scenario: Deduplicate identical images across proposals
    Given AF243-001.pdf contains a facilities photo on page 20
    And DARPA-HR-22.pdf contains the same facilities photo on page 18
    When both proposals are ingested
    Then the image is stored once (deduplicated by content hash)
    And both source proposals are recorded as containing the image

  Scenario: Handle extraction failures gracefully
    Given a PDF contains an image encoded in JBIG2 format
    When the system attempts to extract images from this PDF
    Then the extraction failure is logged with the specific page and encoding
    And other images in the same document are still extracted successfully
    And the ingestion report shows the failure count and affected pages

  Scenario: Extract images from DOCX files
    Given Dr. Vasquez has a directory containing 3 DOCX files with embedded images
    When she runs "corpus add" on that directory
    Then images embedded in DOCX files are extracted alongside PDF images
    And DOCX image metadata includes the image's position context from the document

  Scenario: Ingest directory with no extractable images
    Given Dr. Vasquez has a directory with 5 text-only PDF files
    When she runs "corpus add" on that directory
    Then the system ingests 5 documents into the text corpus
    And the report shows "0 images found"
    And no image registry entries are created for these documents

  # ──────────────────────────────────────────────────────────
  # Step 2: Browse Image Catalog
  # Job Story: JS-4 (Build Library at Scale)
  # ──────────────────────────────────────────────────────────

  Scenario: List all images in the catalog
    Given the image registry contains 23 images from 3 proposals
    When Dr. Vasquez runs "corpus images list"
    Then the system displays a table with all 23 images
    And each row shows: source proposal, agency, caption, quality level, and page number

  Scenario: Filter images by figure type
    Given the image registry contains 8 system diagrams, 4 TRL roadmaps, and 11 other types
    When Dr. Vasquez runs "corpus images list --type system-diagram"
    Then the system displays only the 8 system diagram images

  Scenario: Filter images by outcome
    Given the image registry contains 17 images from WIN proposals and 6 from LOSS proposals
    When Dr. Vasquez runs "corpus images list --outcome win"
    Then the system displays only the 17 images from winning proposals

  Scenario: Combined filters narrow results
    Given the image registry contains images from multiple proposals
    When Dr. Vasquez runs "corpus images list --type system-diagram --outcome win --source AF243-001"
    Then only system diagrams from winning proposal AF243-001 are displayed

  Scenario: Empty catalog displays guidance
    Given the image registry contains 0 images
    When Dr. Vasquez runs "corpus images list"
    Then the system displays "No images in catalog"
    And suggests "Run 'corpus add <directory>' to ingest proposals with embedded images"

  # ──────────────────────────────────────────────────────────
  # Step 3: Search for Relevant Images
  # Job Story: JS-1 (Recall and Retrieve)
  # ──────────────────────────────────────────────────────────

  Scenario: Search images by text query with relevance ranking
    Given the image registry contains images with captions about directed energy systems
    And Dr. Vasquez has an active proposal for a USAF directed energy topic
    When she searches "directed energy system architecture"
    Then results are ranked by relevance score (0 to 1)
    And each result shows: score, source proposal, figure type, caption, outcome, and age
    And results are sorted by descending relevance score

  Scenario: Search with agency filter boosts same-agency results
    Given the image registry contains system diagrams from AF243-001 (USAF) and DARPA-HR-22 (DARPA)
    When Dr. Vasquez searches "system architecture" with --agency USAF
    Then AF243-001 images rank higher than DARPA-HR-22 images due to agency match

  Scenario: Search prefers images from winning proposals
    Given the image registry contains similar system diagrams from AF243-001 (WIN) and N244-012 (LOSS)
    When Dr. Vasquez searches "system architecture"
    Then AF243-001 images rank higher due to WIN outcome preference

  Scenario: Search returns no results with guidance
    Given the image registry contains images but none match "quantum entanglement sensor"
    When Dr. Vasquez searches "quantum entanglement sensor"
    Then the system displays "No matching images found"
    And suggests broadening the search or listing all images of a related type

  # ──────────────────────────────────────────────────────────
  # Step 4: Assess Image Fitness
  # Job Story: JS-2 (Assess Figure Fitness), JS-5 (Compliance)
  # ──────────────────────────────────────────────────────────

  Scenario: View full image details with fitness assessment
    Given Dr. Vasquez is reviewing search result #1 (AF243-001, Fig 3)
    And the image has 300 DPI resolution and was submitted 8 months ago
    And the current proposal is for the same agency (USAF)
    When she runs "corpus images show 1"
    Then the system displays source provenance (proposal, agency, outcome, page)
    And displays image metadata (file path, type, resolution, quality level)
    And displays context (original caption and surrounding text excerpt)
    And displays fitness assessment (quality PASS, freshness OK, agency match YES)

  Scenario: Fitness assessment warns about stale content
    Given an image was extracted from a proposal submitted 26 months ago
    When Dr. Vasquez views its details
    Then freshness shows "WARNING (26 months old)"
    And a warning states team members or technical approach may have changed

  Scenario: Fitness assessment flags low resolution
    Given an image has resolution 640x480 at 72 DPI
    When Dr. Vasquez views its details
    Then quality assessment shows "FAIL (72 DPI -- below 300 DPI minimum)"
    And the system recommends generating a new figure based on this design

  Scenario: Fitness assessment shows label warnings from caption analysis
    Given an image has caption "Figure 3: CDES System Architecture"
    And "CDES" is a proposal-specific system name not in the current proposal
    When Dr. Vasquez views its details
    Then a warning states: caption references "CDES" -- verify system name matches current proposal
    And a warning states: labels may contain proposal-specific text -- manual review recommended

  Scenario: Attribution shows unknown origin with compliance warning
    Given an image's origin cannot be confirmed as company-created
    When Dr. Vasquez views its details
    Then attribution shows "UNKNOWN -- source cannot be confirmed"
    And a warning states: may be government-furnished material, do not reuse without permission
    And the system suggests flagging with "corpus images flag <id>"

  Scenario: Flag image for compliance review
    Given Dr. Vasquez suspects image 7 may be government-furnished
    When she runs "corpus images flag 7 --reason possible-gov-furnished"
    Then the image registry marks image 7 with flag "possible-gov-furnished"
    And the image appears with a compliance warning in all future listings and searches

  # ──────────────────────────────────────────────────────────
  # Step 5: Adapt and Select for Reuse
  # Job Story: JS-3 (Adapt and Insert)
  # ──────────────────────────────────────────────────────────

  Scenario: Select image for reuse with adapted caption
    Given Dr. Vasquez has reviewed image 1 (AF243-001, Fig 3: "CDES System Architecture")
    And her current proposal is for topic AF245-007 ("Maritime Phased Array Defense")
    When she runs "corpus images use 1 --section technical-approach --figure-number 3"
    Then the image file is copied to ./artifacts/wave-5-visuals/figure-3-system-architecture.png
    And the caption is adapted to remove the "CDES" reference
    And the adapted caption is presented for review alongside the original
    And the figure log records source attribution (AF243-001, Figure 3, corpus-reuse)
    And the figure inventory adds an entry with method "corpus-reuse" and status "pending-manual-review"

  Scenario: Manual review items listed for embedded text
    Given Dr. Vasquez has selected a system diagram that contains labeled components
    When the system prepares the image for reuse
    Then it lists potential manual review items: "system name labels", "component names"
    And advises opening the image in an editor to verify and update labels

  Scenario: Reuse a figure that needs no caption adaptation
    Given Dr. Vasquez selects an org chart image with generic caption "Figure 4: Organization Chart"
    And the caption contains no proposal-specific references
    When she runs "corpus images use" with appropriate parameters
    Then the caption is reused as-is with only the figure number updated
    And no caption warnings are generated

  Scenario: Prevent reuse of flagged image
    Given image 7 has been flagged as "possible-gov-furnished"
    When Dr. Vasquez runs "corpus images use 7 --section technical-approach --figure-number 2"
    Then the system blocks the reuse with message: "Image 7 is flagged for compliance review"
    And suggests: "Clear the flag with 'corpus images unflag 7' after compliance verification"

  # ──────────────────────────────────────────────────────────
  # Step 6: Formatter Integration
  # Job Story: JS-3 (Adapt and Insert)
  # ──────────────────────────────────────────────────────────

  Scenario: Formatter routes corpus-reuse figures to review
    Given the figure inventory contains Figure 3 with method "corpus-reuse"
    And Figure 3 has status "pending-manual-review"
    When the formatter processes the figure inventory for Wave 5
    Then the formatter does not attempt to generate Figure 3
    And the formatter presents Figure 3 for human review
    And review options are: approve, revise, replace

  Scenario: Approve a corpus-reused figure
    Given Figure 3 is presented for review with method "corpus-reuse"
    When Dr. Vasquez approves Figure 3
    Then the figure status changes to "approved"
    And the figure is ready for insertion during Wave 6 formatting
    And the figure log records approval with timestamp

  Scenario: Replace a corpus-reused figure with new generation
    Given Figure 3 is presented for review with method "corpus-reuse"
    And Dr. Vasquez decides the reused image needs too many label changes
    When she selects "replace"
    Then the system treats Figure 3 as a regular figure requiring generation
    And the original corpus-reuse attribution is preserved in the figure log as "replaced"
    And the formatter proceeds with standard generation methods (SVG, Mermaid, etc.)

  Scenario: Cross-reference validation includes corpus-reused figures
    Given Figure 3 was reused from corpus and approved
    And the technical approach section references "Figure 3"
    When the formatter validates cross-references
    Then Figure 3 is included in the cross-reference log
    And the reference from technical approach to Figure 3 resolves successfully

  # ──────────────────────────────────────────────────────────
  # Batch Operations (Secondary Persona: Marcus Chen)
  # Job Story: JS-4 (Build Library at Scale)
  # ──────────────────────────────────────────────────────────

  Scenario: Batch ingest 40 proposals with image extraction
    Given Marcus Chen has a corpus directory with 40 past proposals (mix of PDF and DOCX)
    When he runs "corpus add ~/proposals/" on the full directory
    Then all 40 proposals are ingested into the text corpus
    And images are extracted from all documents containing embedded images
    And the image registry contains all extracted images with metadata
    And the ingestion report shows total document and image counts
    And the operation completes within a reasonable time with progress indication

  Scenario: Incremental re-ingestion skips already-extracted images
    Given Marcus Chen previously ingested 40 proposals with images
    And 2 new proposals have been added to the directory
    When he re-runs "corpus add ~/proposals/"
    Then only the 2 new proposals are ingested (40 skipped as duplicates)
    And only images from the 2 new proposals are extracted
    And the report shows "2 new documents, 40 already in corpus"

  # ──────────────────────────────────────────────────────────
  # Properties (ongoing quality invariants)
  # ──────────────────────────────────────────────────────────

  @property
  Scenario: Every extracted image has complete metadata
    Given images have been extracted from corpus documents
    Then every image in the registry has: source_proposal, page_number, figure_type, quality_level, content_hash, file_path, extraction_date
    And no image entry has null or empty required fields

  @property
  Scenario: Image deduplication is consistent
    Given the same image appears in multiple source documents
    Then the image file is stored once in .sbir/corpus/images/
    And all source proposals referencing the image are tracked in the registry

  @property
  Scenario: Attribution tracking is complete for all reused images
    Given a corpus image has been selected for reuse in a proposal
    Then the figure log contains: source proposal ID, original figure number, method "corpus-reuse", and selection timestamp
    And this attribution persists through to Wave 6 assembly
