<!-- markdownlint-disable MD024 -->

# Corpus Image Reuse -- User Stories

Scope: Full image reuse capability chain -- extraction, indexing, search, assessment, adaptation, and formatter integration.
All stories trace to JTBD analysis in `jtbd-analysis.md` and journey steps in `journey-corpus-image-reuse.yaml`.

---

## US-CIR-001: Image Extraction During Corpus Ingestion

### Problem

Dr. Elena Vasquez is a PI at a 25-person defense tech startup who has 4 past proposals with system architecture diagrams and TRL roadmaps she wants to reuse. She finds it wasteful to know these images exist inside her ingested PDFs but have zero access to them through the plugin. Today she manually opens each PDF, screenshots or exports figures, and saves them in a personal folder -- a process that takes 30-60 minutes per proposal.

### Who

- PI with past proposals | Ingesting proposals into corpus | Wants images extracted automatically alongside text

### Solution

Extend the existing `corpus add` command to extract embedded images from PDF and DOCX files during ingestion. Store extracted images in `.sbir/corpus/images/` with metadata sidecars in `.sbir/corpus/image-registry.json`. Classify each image by figure type. Assess image quality (DPI). Deduplicate by content hash. Report image extraction results alongside document ingestion results.

### Domain Examples

#### 1: Happy Path -- Elena ingests 4 proposals with mixed figures

Dr. Elena Vasquez runs `corpus add ~/proposals/2024-Q1/` on a directory containing AF243-001.pdf (WIN, 8 images including system architecture on page 7), N244-012.pdf (LOSS, 6 images), DARPA-HR-22.pdf (WIN, 9 images), and a text-only budget.docx (0 images). The system ingests 4 documents, extracts 23 images, classifies them (8 system diagrams, 4 TRL roadmaps, 3 org charts, etc.), and reports quality breakdown: 19 high, 3 medium, 1 low.

#### 2: Edge Case -- Marcus ingests 40 proposals in batch

Marcus Chen runs `corpus add ~/proposals/` on his firm's full proposal archive of 40 documents. The system processes all 40, extracts 180+ images across the batch, and reports progress. Two new proposals are added later; re-running `corpus add` ingests only the 2 new ones and extracts only their images.

#### 3: Error Path -- Extraction failure on JBIG2-encoded image

Dr. Vasquez ingests a PDF containing one image encoded in JBIG2 format (not supported by extraction library). The system extracts 7 of 8 images successfully, logs the failure for page 14 with the specific encoding issue, and reports: "7 images extracted. 1 extraction failed (JBIG2 encoding on page 14)."

### UAT Scenarios (BDD)

#### Scenario: Extract images from PDF during corpus ingestion

Given Dr. Vasquez has a directory containing AF243-001.pdf with 8 embedded images
When she runs "corpus add ~/proposals/2024-Q1/"
Then the system ingests the document into the text corpus registry
And extracts 8 embedded images to .sbir/corpus/images/
And creates 8 entries in .sbir/corpus/image-registry.json
And the ingestion report shows "8 images extracted"

#### Scenario: Classify extracted images by figure type

Given the system has extracted an image from AF243-001.pdf page 7
And the surrounding text mentions "system architecture" and the caption reads "Figure 3: CDES System Architecture"
When classification runs
Then the image is classified as "system-diagram"

#### Scenario: Assess quality and record DPI

Given an extracted image has resolution 2048x1536 at 300 DPI
When quality assessment runs
Then quality level is "high"
And DPI and resolution are recorded in the image registry entry

#### Scenario: Deduplicate identical images across proposals

Given AF243-001.pdf and DARPA-HR-22.pdf both contain the same facilities photo (identical content hash)
When both are ingested
Then the image file is stored once
And both proposals are recorded as sources in the registry entry

#### Scenario: Handle extraction failure gracefully

Given a PDF contains a JBIG2-encoded image on page 14
When the system attempts extraction
Then the failure is logged with page number and encoding type
And other images in the PDF are extracted successfully

### Acceptance Criteria

- [ ] `corpus add` extracts embedded images from PDF and DOCX files alongside text ingestion
- [ ] Each extracted image is stored in `.sbir/corpus/images/` with deterministic filename
- [ ] Each image has a complete metadata entry in `.sbir/corpus/image-registry.json`
- [ ] Images are classified by figure type using caption and context analysis
- [ ] Quality assessment records DPI and resolution; levels: high (>=300), medium (150-299), low (<150)
- [ ] Identical images deduplicated by content hash; multiple sources tracked
- [ ] Extraction failures logged per-page without blocking other image extraction
- [ ] Ingestion report includes image extraction summary

### Technical Notes

- PDF image extraction requires PyPDF2 or pdfplumber (dependency decision for DESIGN wave)
- python-docx provides DOCX image extraction
- Image files stored as-extracted (PNG, JPEG) -- no format conversion at ingestion
- Content hash uses SHA-256 (consistent with existing text corpus deduplication)
- Image registry is a new JSON file; schema must be defined in DESIGN wave
- Existing `CorpusIngestionService` and `FilesystemCorpusAdapter` need extension (not replacement)

### Dependencies

- Extends existing corpus domain model (`scripts/pes/domain/corpus.py`)
- Extends existing `FilesystemCorpusAdapter` (`scripts/pes/adapters/filesystem_corpus_adapter.py`)
- Extends existing `CorpusScanner` port (`scripts/pes/ports/corpus_port.py`)
- No dependency on other CIR stories (can be delivered first)

---

## US-CIR-002: Image Search and Browsing

### Problem

Dr. Elena Vasquez knows she had a great system architecture diagram in her winning Air Force proposal from 2024, but she cannot find it through the plugin. The corpus has her text indexed but no way to search for images. She resorts to opening PDFs one by one, scanning for the figure she remembers -- a process that takes 15-30 minutes when she has 4+ past proposals.

### Who

- PI drafting a new proposal | Searching for reusable figures from past work | Wants to find the right image in seconds, not minutes

### Solution

Add `corpus images list` and `corpus images search` commands. List supports filtering by figure type, source proposal, outcome, and agency. Search accepts a text query and returns relevance-ranked results combining caption match, agency match, outcome preference, and recency.

### Domain Examples

#### 1: Happy Path -- Elena searches for a directed energy diagram

Dr. Elena Vasquez is drafting a USAF proposal and needs a system architecture figure. She runs `corpus images search "directed energy system architecture" --agency USAF`. The system returns 3 matches: AF243-001 Fig 3 (score 0.92, WIN, 8 months old), AF243-001 Fig 5 (score 0.71, WIN), and DARPA-HR-22 Fig 2 (score 0.45, WIN, different agency).

#### 2: Edge Case -- Marcus browses by type to inventory his firm's assets

Marcus Chen runs `corpus images list --type org-chart` to see all org charts across 40+ proposals. The system returns 12 org charts with source, agency, quality, and outcome for each.

#### 3: Error Path -- Search with no results

Dr. Vasquez searches for "quantum computing sensor array" but no corpus images match. The system responds: "No matching images found. Try: corpus images list --type system-diagram to see all system diagrams."

### UAT Scenarios (BDD)

#### Scenario: List images with type and outcome filters

Given the image registry contains 23 images from 3 proposals
And 8 are system diagrams, 17 are from WIN proposals
When Dr. Vasquez runs "corpus images list --type system-diagram --outcome win"
Then only system diagrams from winning proposals are displayed
And each row shows source, agency, caption, quality, and page

#### Scenario: Search with relevance ranking

Given Dr. Vasquez has an active USAF directed energy proposal
And the image registry contains system diagrams from AF243-001 (USAF, WIN) and DARPA-HR-22 (DARPA, WIN)
When she searches "directed energy system architecture" --agency USAF
Then AF243-001 results score higher than DARPA-HR-22
And results are sorted by descending relevance score

#### Scenario: Search with no matches returns guidance

Given no images match the query "quantum entanglement sensor"
When Dr. Vasquez searches for that phrase
Then the system displays "No matching images found"
And suggests listing images by type

#### Scenario: Empty catalog displays onboarding guidance

Given the image registry is empty
When Dr. Vasquez runs "corpus images list"
Then the system displays "No images in catalog"
And suggests running "corpus add" first

### Acceptance Criteria

- [ ] `corpus images list` displays all images or filtered subset in tabular format
- [ ] Filters supported: `--type`, `--source`, `--outcome`, `--agency`
- [ ] `corpus images search` accepts text query and returns relevance-ranked results
- [ ] Relevance scoring combines: caption text match, agency match, outcome preference (WIN boost), recency
- [ ] Each result shows: relevance score, source proposal, figure type, caption, outcome, age
- [ ] Empty results include actionable guidance
- [ ] Empty catalog includes onboarding guidance

### Technical Notes

- Search operates on caption text and surrounding text excerpt stored in image registry
- Relevance scoring weights are configurable (decision for DESIGN wave)
- Current proposal context (agency, topic) read from `.sbir/proposal-state.json` for agency matching
- List and search share the same image registry data source

### Dependencies

- Depends on US-CIR-001 (image registry must exist with entries)
- Reads from existing proposal state for agency/topic matching

---

## US-CIR-003: Image Fitness Assessment

### Problem

Dr. Elena Vasquez found a system architecture diagram from a past proposal through search, but she is not sure if it is actually usable. Is the resolution high enough for a government submission? Is it from the same agency? Has the content gone stale since the original proposal? Might it contain government-furnished material she cannot reuse? She needs to evaluate fitness before committing to reuse, and today she has to make these judgments entirely by memory and manual inspection.

### Who

- PI evaluating a candidate image for reuse | Needs quality, freshness, compliance, and context data | Wants confidence to proceed or skip without wasting time

### Solution

Add `corpus images show <id>` command displaying full image details: source provenance, image metadata, original context (caption + surrounding text), fitness assessment (quality, freshness, agency match, domain match), label warnings, and attribution/compliance notes. Add `corpus images flag <id>` to mark images for compliance review.

### Domain Examples

#### 1: Happy Path -- Elena assesses a high-quality match

Dr. Vasquez runs `corpus images show 1` for the AF243-001 system architecture diagram. The system shows: 300 DPI (quality PASS), 8 months old (freshness OK), same agency USAF (match YES), domain match HIGH. Caption warns "CDES" is a proposal-specific name. Attribution: company-created, no restrictions.

#### 2: Edge Case -- Stale image from 26-month-old proposal

Dr. Vasquez views an image from a proposal submitted 26 months ago. Freshness shows WARNING with note about potential team/approach changes. She decides to use it but flags it for careful review.

#### 3: Error Path -- Possible government-furnished image

Dr. Vasquez views an image whose origin is unknown (extracted from a proposal section about government-provided test data). The system shows attribution UNKNOWN with a compliance warning. She flags it with `corpus images flag 7 --reason possible-gov-furnished`.

### UAT Scenarios (BDD)

#### Scenario: Display full fitness assessment for a high-quality match

Given Dr. Vasquez runs "corpus images show 1" for an AF243-001 image at 300 DPI, 8 months old
And her current proposal is USAF directed energy
When the assessment runs
Then quality shows "PASS (300 DPI)"
And freshness shows "OK (8 months old)"
And agency match shows "YES (same agency: USAF)"
And label warnings identify proposal-specific terms in the caption

#### Scenario: Warn about stale content

Given an image is from a proposal submitted 26 months ago
When Dr. Vasquez views its details
Then freshness shows "WARNING (26 months old)"
And the warning mentions potential changes to team or approach

#### Scenario: Flag image for compliance review

Given Dr. Vasquez suspects image 7 may be government-furnished
When she runs "corpus images flag 7 --reason possible-gov-furnished"
Then the registry marks image 7 with the compliance flag
And the image shows a compliance warning in future listings

#### Scenario: Low-resolution image fails quality check

Given an image has 72 DPI resolution
When Dr. Vasquez views its details
Then quality shows "FAIL (72 DPI -- below 300 DPI minimum)"
And suggests generating a new figure based on this design

### Acceptance Criteria

- [ ] `corpus images show` displays: source provenance, image metadata, context, fitness assessment, attribution
- [ ] Quality thresholds: high (>=300 DPI), medium (150-299), low (<150); PASS requires >=300
- [ ] Freshness thresholds: OK (<=12 months), WARNING (12-24 months), STALE (>24 months)
- [ ] Caption analysis identifies proposal-specific terms and generates label warnings
- [ ] Attribution shows origin type (company-created, unknown, government-furnished)
- [ ] `corpus images flag` records compliance concern in registry
- [ ] Flagged images display compliance warning in all listing/search contexts

### Technical Notes

- Freshness calculated from extraction_date relative to current date
- Caption analysis for proposal-specific terms uses simple heuristic: terms appearing only in the source proposal context
- Attribution origin_type defaults to "company-created"; user can reclassify via flag

### Dependencies

- Depends on US-CIR-001 (image registry entries)
- Depends on US-CIR-002 (show is typically reached via list/search)
- Reads from existing proposal state for current proposal context

---

## US-CIR-004: Image Adaptation and Reuse Selection

### Problem

Dr. Elena Vasquez has decided to reuse a system architecture diagram from her winning Air Force proposal. But the original caption says "CDES System Architecture" -- her current proposal is about a different system. The diagram labels inside the image may also reference the old system name. She needs the plugin to help adapt the textual elements (caption, figure number, cross-references) and flag the image-internal elements that need manual editing. Today she copies the image and forgets to update the caption, or updates the caption but misses a label inside the diagram.

### Who

- PI selecting a corpus image for reuse | Needs caption adaptation and label change warnings | Wants seamless integration into the current proposal's figure plan

### Solution

Add `corpus images use <id> --section <section> --figure-number <n>` command. Copies image to artifacts directory, generates adapted caption (removing proposal-specific references), lists manual review items for embedded text, records attribution in figure log, and creates a figure inventory entry with method "corpus-reuse".

### Domain Examples

#### 1: Happy Path -- Elena adapts a system diagram

Dr. Vasquez runs `corpus images use 1 --section technical-approach --figure-number 3`. The image is copied to `./artifacts/wave-5-visuals/figure-3-system-architecture.png`. Caption changes from "Figure 3: CDES System Architecture..." to "Figure 3: System Architecture..." with note that "CDES" was removed. Manual review warns about possible system name labels in the diagram. Figure log records: source AF243-001, Figure 3, method corpus-reuse.

#### 2: Edge Case -- Generic org chart needs no adaptation

Dr. Vasquez selects an org chart with caption "Figure 4: Organization Chart" -- no proposal-specific terms. The caption is reused with only the figure number updated. No warnings generated.

#### 3: Error Path -- Attempting to reuse a flagged image

Dr. Vasquez tries to use image 7 which is flagged as "possible-gov-furnished". The system blocks the reuse with a clear message and suggests clearing the flag after compliance verification.

### UAT Scenarios (BDD)

#### Scenario: Select image with adapted caption

Given Dr. Vasquez has reviewed image 1 (AF243-001, "CDES System Architecture")
And her current proposal is for topic AF245-007
When she runs "corpus images use 1 --section technical-approach --figure-number 3"
Then the image is copied to ./artifacts/wave-5-visuals/figure-3-system-architecture.png
And the caption replaces "CDES" with a generic reference
And the figure log records source attribution
And the figure inventory gains an entry with method "corpus-reuse"

#### Scenario: Generic caption needs no adaptation

Given an org chart image has caption "Figure 4: Organization Chart"
When Dr. Vasquez selects it for reuse as Figure 2
Then the caption becomes "Figure 2: Organization Chart"
And no caption change warnings are generated

#### Scenario: Block reuse of compliance-flagged image

Given image 7 is flagged as "possible-gov-furnished"
When Dr. Vasquez runs "corpus images use 7"
Then the system blocks with "Image 7 is flagged for compliance review"
And suggests clearing the flag after verification

#### Scenario: Manual review items listed for embedded text

Given a system diagram image contains labeled component boxes
When Dr. Vasquez selects it for reuse
Then the system lists potential label review items
And advises opening the image in an editor

### Acceptance Criteria

- [ ] `corpus images use` copies image file to `./artifacts/wave-5-visuals/` with appropriate filename
- [ ] Caption is adapted: proposal-specific terms identified and removed/genericized
- [ ] Adapted caption presented alongside original for human review
- [ ] Manual review items listed for possible embedded text in the image
- [ ] Figure log records: source proposal, original figure number, method "corpus-reuse"
- [ ] Figure inventory adds entry with `generation_method: "corpus-reuse"`, `status: "pending-manual-review"`
- [ ] Compliance-flagged images blocked from reuse with clear error and remediation

### Technical Notes

- Caption adaptation is heuristic: removes terms unique to the source proposal context
- Manual review warnings are advisory -- the plugin cannot modify embedded image text
- Figure inventory entry must be compatible with existing `FigurePlaceholder` schema (needs `generation_method` extension)
- File copy preserves original format (PNG, JPEG) -- no conversion

### Dependencies

- Depends on US-CIR-001 (image registry), US-CIR-003 (fitness assessment informs selection)
- Extends existing `FigurePlaceholder` domain object with "corpus-reuse" method
- Extends existing figure log format with attribution fields

---

## US-CIR-005: Formatter Integration for Corpus-Reused Figures

### Problem

Dr. Elena Vasquez has selected a corpus image for reuse in her proposal. When the formatter agent runs Wave 5 (visual asset generation), it currently attempts to generate all figures from scratch. It does not know that Figure 3 is a pre-existing image that was selected from the corpus. The formatter would either skip it (losing the figure) or try to regenerate it (ignoring the proven asset). The formatter needs to recognize "corpus-reuse" as a valid generation method and route those figures to review rather than generation.

### Who

- PI moving from figure selection to document assembly | Needs corpus-reused figures handled alongside generated figures | Wants the formatter review checkpoint to apply uniformly

### Solution

Extend the formatter's generation routing to recognize `generation_method: "corpus-reuse"` in the figure inventory. For these figures, skip generation and present directly for human review (approve/revise/replace). Include corpus-reused figures in cross-reference validation. Preserve attribution through Wave 6 assembly.

### Domain Examples

#### 1: Happy Path -- Formatter presents corpus-reuse figure for review

The figure inventory has Figure 3 with method "corpus-reuse" and status "pending-manual-review". During Wave 5, the formatter presents Figure 3 for review showing the image, its corpus source, and options: approve, revise, replace. Dr. Vasquez approves it. Status changes to "approved". Cross-references validate successfully.

#### 2: Edge Case -- User decides to replace rather than reuse

Dr. Vasquez sees the corpus-reused Figure 3 but decides the embedded labels need too many changes. She selects "replace". The formatter treats Figure 3 as requiring generation and proceeds with SVG/Mermaid/Gemini. The figure log records the original corpus-reuse as "replaced".

#### 3: Error Path -- Cross-reference to missing corpus-reuse figure

The technical approach section references "Figure 3" but the corpus-reused image file was accidentally deleted from the artifacts directory. Cross-reference validation flags Figure 3 as an orphaned reference.

### UAT Scenarios (BDD)

#### Scenario: Formatter routes corpus-reuse to review

Given the figure inventory has Figure 3 with method "corpus-reuse"
When the formatter processes the inventory for Wave 5
Then it does not attempt to generate Figure 3
And it presents Figure 3 for review with approve/revise/replace options

#### Scenario: Approve corpus-reused figure

Given Figure 3 is presented for review
When Dr. Vasquez approves it
Then status changes to "approved"
And the figure is ready for Wave 6 insertion

#### Scenario: Replace corpus-reused figure with generated one

Given Figure 3 is presented for review with method "corpus-reuse"
When Dr. Vasquez selects "replace"
Then the formatter proceeds with standard generation for Figure 3
And the figure log records the original as "replaced"

#### Scenario: Cross-reference validation includes corpus-reused figures

Given Figure 3 is approved with method "corpus-reuse"
And the technical approach section references "Figure 3"
When cross-reference validation runs
Then Figure 3 is included in the cross-reference log
And the reference resolves successfully

### Acceptance Criteria

- [ ] Formatter recognizes `generation_method: "corpus-reuse"` and skips generation
- [ ] Corpus-reuse figures presented for review with approve/revise/replace options
- [ ] "Approve" changes status to "approved" for Wave 6 insertion
- [ ] "Replace" converts figure to standard generation with method change logged
- [ ] Cross-reference validation includes corpus-reused figures
- [ ] Attribution from figure log preserved through Wave 6 assembly
- [ ] Existing generation methods (SVG, Mermaid, Graphviz, Gemini) unaffected

### Technical Notes

- Extends `VisualAssetService.generate_figure()` routing: "corpus-reuse" skips `FigureGenerator` port
- `FigurePlaceholder.generation_method` gains "corpus-reuse" as a valid value
- `FigureGenerationResult` for corpus-reuse: file_path from copied image, review_status "pending-manual-review"
- No change to `FigureGenerator` port interface -- corpus-reuse never invokes it

### Dependencies

- Depends on US-CIR-004 (figure inventory entries with corpus-reuse method)
- Extends existing `VisualAssetService` (`scripts/pes/domain/visual_asset_service.py`)
- Extends existing `FigurePlaceholder` (`scripts/pes/domain/visual_asset.py`)
- No external dependencies

---

## Definition of Ready Validation

### US-CIR-001: Image Extraction During Corpus Ingestion

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | PI wastes 30-60 min manually exporting figures from PDFs; corpus has text but zero image access |
| User/persona identified | PASS | Dr. Elena Vasquez, PI, 25-person defense tech startup, 4 past proposals |
| 3+ domain examples | PASS | Happy path (4 proposals, 23 images), batch (Marcus, 40 proposals), error (JBIG2 failure) |
| UAT scenarios (3-7) | PASS | 5 scenarios: extract, classify, quality, dedup, failure handling |
| AC derived from UAT | PASS | 8 criteria mapping to scenario outcomes |
| Right-sized | PASS | ~2-3 days (extraction logic + registry schema + adapter extension), 5 scenarios |
| Technical notes | PASS | PyPDF2/pdfplumber dependency, SHA-256 hashing, existing adapter extension |
| Dependencies tracked | PASS | Extends corpus.py, FilesystemCorpusAdapter, CorpusScanner port; no external blockers |

### DoR Status: PASSED

---

### US-CIR-002: Image Search and Browsing

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | PI spends 15-30 min opening PDFs to find a remembered figure; no image search exists |
| User/persona identified | PASS | Dr. Elena Vasquez (search), Marcus Chen (browse/inventory) |
| 3+ domain examples | PASS | Search with results (Elena), browse by type (Marcus), no results (Elena) |
| UAT scenarios (3-7) | PASS | 4 scenarios: filtered list, relevance search, no results, empty catalog |
| AC derived from UAT | PASS | 7 criteria covering list, search, ranking, guidance |
| Right-sized | PASS | ~2 days (list + search commands, relevance scoring), 4 scenarios |
| Technical notes | PASS | Caption-based search, configurable weights, proposal-state.json for context |
| Dependencies tracked | PASS | Depends on US-CIR-001 (image registry must exist) |

### DoR Status: PASSED

---

### US-CIR-003: Image Fitness Assessment

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | PI cannot evaluate quality, freshness, compliance of candidate images without manual inspection |
| User/persona identified | PASS | Dr. Elena Vasquez evaluating candidate images for reuse |
| 3+ domain examples | PASS | High-quality match (Elena), stale image (26-month warning), gov-furnished (compliance flag) |
| UAT scenarios (3-7) | PASS | 4 scenarios: full assessment, stale warning, compliance flag, low resolution |
| AC derived from UAT | PASS | 7 criteria covering quality thresholds, freshness, caption analysis, flagging |
| Right-sized | PASS | ~2 days (show command, fitness logic, flag command), 4 scenarios |
| Technical notes | PASS | Freshness calculation, caption heuristics, origin_type defaults |
| Dependencies tracked | PASS | Depends on US-CIR-001, US-CIR-002 |

### DoR Status: PASSED

---

### US-CIR-004: Image Adaptation and Reuse Selection

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | PI forgets to update captions/labels when copying figures from past proposals |
| User/persona identified | PASS | Dr. Elena Vasquez adapting a selected image for her current proposal |
| 3+ domain examples | PASS | System diagram adaptation (Elena), generic org chart (no changes), flagged image (blocked) |
| UAT scenarios (3-7) | PASS | 4 scenarios: adapted caption, generic caption, flagged block, manual review items |
| AC derived from UAT | PASS | 7 criteria covering copy, adaptation, review items, logging, blocking |
| Right-sized | PASS | ~2 days (use command, caption adaptation, figure log/inventory integration), 4 scenarios |
| Technical notes | PASS | Heuristic caption adaptation, FigurePlaceholder extension, file copy |
| Dependencies tracked | PASS | Depends on US-CIR-001, US-CIR-003; extends FigurePlaceholder |

### DoR Status: PASSED

---

### US-CIR-005: Formatter Integration for Corpus-Reused Figures

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Formatter would skip or regenerate corpus-reused figures; no routing for corpus-reuse method |
| User/persona identified | PASS | Dr. Elena Vasquez moving from figure selection to document assembly |
| 3+ domain examples | PASS | Approve reuse (Elena), replace with generation (Elena), cross-ref validation |
| UAT scenarios (3-7) | PASS | 4 scenarios: routing, approve, replace, cross-reference |
| AC derived from UAT | PASS | 7 criteria covering routing, review, status changes, cross-refs, attribution |
| Right-sized | PASS | ~1-2 days (routing logic + FigurePlaceholder extension), 4 scenarios |
| Technical notes | PASS | VisualAssetService routing, FigurePlaceholder method extension, no FigureGenerator change |
| Dependencies tracked | PASS | Depends on US-CIR-004; extends VisualAssetService, FigurePlaceholder |

### DoR Status: PASSED

---

## Story Dependency Graph

```
US-CIR-001 (Extraction)
    |
    +---> US-CIR-002 (Search/Browse)
    |         |
    |         +---> US-CIR-003 (Fitness Assessment)
    |                    |
    |                    +---> US-CIR-004 (Adaptation/Reuse Selection)
    |                                |
    |                                +---> US-CIR-005 (Formatter Integration)
```

Linear dependency chain. Each story delivers independently demonstrable value, but full end-to-end reuse requires all 5.

## MoSCoW Classification

| Story | MoSCoW | Rationale |
|-------|--------|-----------|
| US-CIR-001 | Must Have | Foundation -- without extraction, no images exist in the system |
| US-CIR-002 | Must Have | Without search/browse, extracted images are inaccessible |
| US-CIR-003 | Must Have | Without fitness assessment, users cannot make informed reuse decisions |
| US-CIR-004 | Should Have | Caption adaptation and figure integration. Could be done manually but error-prone |
| US-CIR-005 | Should Have | Formatter integration. Without it, users manually add figures during Wave 6 |

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PDF image extraction quality varies by encoding | Medium | High | Support common encodings first; log failures for unsupported formats |
| Figure type classification accuracy | Medium | Medium | Start with caption-based heuristics; accept "unclassified" as valid type |
| Image registry schema evolution | Low | High | Define schema as a domain object with explicit versioning |
| Stale content reuse without review | Low | High | Mandatory "pending-manual-review" status; never auto-approve |
| Government-furnished image compliance | Low | High | Attribution tracking + flag mechanism + blocked reuse for flagged images |
