# Corpus Image Reuse -- Acceptance Test Design

## Summary

42 acceptance scenarios across 4 feature files covering all 5 user stories (US-CIR-001 through US-CIR-005). Tests invoke through driving ports (domain services) with in-memory fakes for driven ports (image extraction, image registry).

## Scenario Inventory

| Feature File | Scenarios | Walking Skeletons | Focused | Error/Edge | Property |
|---|---|---|---|---|---|
| walking-skeleton.feature | 3 | 3 | 0 | 0 | 0 |
| milestone-01-extraction.feature | 14 | 0 | 6 | 4 | 1 |
| milestone-02-search-and-fitness.feature | 15 | 0 | 6 | 5 | 1 |
| milestone-03-adaptation-and-formatter.feature | 12 | 0 | 7 | 4 | 0 |
| **Total** | **44 (42 unique)** | **3** | **19** | **13** | **2** |

Note: Walking skeleton scenarios 2 and 3 are also referenced from extraction/adaptation steps but mapped uniquely.

## Error Path Ratio

13 error/edge scenarios out of 42 total = **31%**. Below the 40% target. Additional error scenarios can be added during DELIVER if needed, but current coverage addresses all error paths from all 5 user stories.

**Error scenarios covered:**
- Unsupported image encoding (JBIG2)
- Text-only document (zero images)
- Re-ingestion deduplication
- Search with no matches
- Empty catalog
- Stale image (freshness WARNING/STALE)
- Low-resolution image (quality FAIL)
- Unknown attribution (compliance notice)
- Compliance-flagged image blocked from reuse
- Image not found in catalog
- Missing image file (orphaned reference)
- Freshness boundaries (12mo, 24mo)

## Story-to-Scenario Traceability

| Story | Scenarios | Feature File |
|---|---|---|
| US-CIR-001 | 14 (+ WS1) | walking-skeleton, milestone-01 |
| US-CIR-002 | 5 (+ WS1 partial) | milestone-02 |
| US-CIR-003 | 10 | milestone-02 |
| US-CIR-004 | 5 (+ WS2) | milestone-03, walking-skeleton |
| US-CIR-005 | 7 (+ WS3) | milestone-03, walking-skeleton |

## Implementation Sequence

One-at-a-time, remove `@skip` in this order:

1. **WS1**: `PI extracts images from past proposals and finds them by search` (ENABLED)
2. Extract embedded images from a PDF during corpus ingestion
3. Extract embedded images from a DOCX during corpus ingestion
4. Classify extracted images using caption and context
5. High-resolution image assessed as high quality
6. Identical images from different proposals stored once
7. Unsupported image encoding fails gracefully
8. Text-only document reports zero images without error
9. Re-ingesting a directory does not duplicate existing images
10. Batch ingestion extracts images from all documents
11. List images filtered by figure type
12. Search returns relevance-ranked results favoring agency match
13. Search with no matches suggests browsing by type
14. Empty image catalog suggests adding proposals first
15. High-quality recent image from same agency passes all fitness checks
16. Caption analysis warns about proposal-specific terminology
17. Image from 26-month-old proposal shows freshness warning
18. Low-resolution image fails quality assessment
19. Flag image with compliance concern
20. Image with unknown origin shows compliance notice
21. Freshness boundary scenarios (12mo, 24mo)
22. **WS2**: PI assesses and selects for reuse
23. Select image for reuse with adapted caption
24. Generic caption reused with only figure number updated
25. Compliance-flagged image cannot be selected for reuse
26. Manual review items listed for diagram
27. **WS3**: Formatter presents corpus-reused figure for review
28. Formatter skips generation for corpus-reuse figures
29. Approved corpus-reuse figure is ready for assembly
30. Replace corpus-reuse figure with standard generation
31. Cross-reference validation resolves corpus-reuse references
32. Missing corpus-reuse file detected during validation
33. Standard generation methods continue to work alongside corpus-reuse
34. Property tests (content hash, quality level)

## Mandate Compliance Evidence

### CM-A: Hexagonal Boundary Enforcement

All step definition files import through driving port equivalents (domain services) and in-memory fakes for driven ports. No imports of PyMuPDF, python-docx, filesystem adapters, or JSON I/O in step definitions.

**Driving ports tested through:**
- ImageExtractionService (via InMemoryImageExtractorAdapter)
- ImageSearchService (via InMemoryImageRegistryAdapter)
- ImageFitnessService (via InMemoryImageRegistryAdapter)
- ImageAdaptationService (via InMemoryImageRegistryAdapter)

### CM-B: Business Language Purity

Zero technical terms in Gherkin. All scenarios use domain language:
- "corpus", "image catalog", "proposal", "ingestion", "extraction"
- "quality", "freshness", "agency match", "compliance flag"
- "caption adaptation", "figure inventory", "document assembly"

No HTTP verbs, JSON, database, API, status codes, or class names in feature files.

### CM-C: Walking Skeleton + Focused Scenario Counts

- 3 walking skeletons (user-value E2E)
- 39 focused scenarios (boundary tests with in-memory fakes)
- 2 property-tagged scenarios (signals for hypothesis-based testing)

## Test Infrastructure

```
tests/acceptance/corpus_image_reuse/
  __init__.py
  conftest.py                    -- Fixtures: adapters, sample data, context
  fakes.py                       -- In-memory fakes for driven ports
  walking-skeleton.feature       -- 3 walking skeletons
  milestone-01-extraction.feature       -- 14 extraction scenarios
  milestone-02-search-and-fitness.feature  -- 15 search/fitness scenarios
  milestone-03-adaptation-and-formatter.feature  -- 12 adaptation/formatter scenarios
  steps/
    __init__.py
    conftest.py                  -- Shared step imports
    image_common_steps.py        -- Shared Given/Then steps
    image_extraction_steps.py    -- Extraction + walking skeleton steps
    image_search_fitness_steps.py    -- Search, browse, fitness steps
    image_adaptation_formatter_steps.py  -- Adaptation + formatter steps
```
