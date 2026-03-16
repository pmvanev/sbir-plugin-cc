# ADR-022: Heuristic Figure Type Classification

## Status

Accepted

## Context

Extracted images need figure type classification (system-diagram, trl-roadmap, org-chart, etc.) for search and browse filtering. Classification accuracy impacts search quality -- the #1 user priority (JTBD score 18.0). Options range from simple keyword matching to ML-based image classification.

## Decision

Use **caption and surrounding text keyword matching** for figure type classification. Accept "unclassified" as a valid type when no keywords match.

## Alternatives Considered

### Alternative 1: ML-based image classification

- **What**: Use a pre-trained image classifier (e.g., CLIP, ResNet) to classify figure types from pixel content
- **Pros**: Could classify images without captions, potentially higher accuracy for ambiguous figures
- **Cons**: Requires ML model dependency (~500MB+), GPU beneficial for batch processing, training data needed for SBIR-specific figure types (system diagrams vs. concept illustrations), adds significant complexity for a solo developer, classification accuracy for technical diagrams is unproven
- **Rejected**: Complexity disproportionate to benefit. SBIR figures almost always have captions ("Figure N: ..."). Caption-based classification handles the common case. ML adds a large dependency and maintenance burden for marginal accuracy improvement.

### Alternative 2: User-provided classification during ingestion

- **What**: Prompt user to classify each image during `corpus add`
- **Pros**: 100% accuracy, no heuristic errors
- **Cons**: 23 images from 4 proposals means 23 classification prompts. 180 images from 40 proposals (Marcus Chen) is unusable. Destroys batch ingestion UX. Violates JTBD #5 "minimize time to catalog visual assets at scale" (score 15.5).
- **Rejected**: Manual classification at scale defeats the purpose of automated extraction and indexing.

## Consequences

### Positive

- Zero additional dependencies -- keyword matching is stdlib Python
- Deterministic and testable -- same caption always produces same classification
- Fast -- O(1) per image regardless of corpus size
- "Unclassified" is transparent -- user sees when classification fails and can mentally filter

### Negative

- Accuracy depends on caption quality -- images without captions default to "unclassified"
- Caption text in extracted PDFs may be imprecise (OCR artifacts, truncated captions)
- Keyword list requires maintenance as new figure types emerge
- Cannot distinguish visually similar types (e.g., block diagram vs. system diagram) without caption cues

### Quality Attribute Impact

- **Maintainability**: Keyword list is a simple data structure, easy to extend
- **Time-to-market**: No ML infrastructure, no training data, no model serving
- **Testability**: Pure function (caption string -> classification string), trivially testable

### Mitigation

- Users can reclassify images via `corpus images flag` or a future `corpus images reclassify` command
- Classification keywords are configurable (stored in domain, not hardcoded in adapter)
- Search also matches caption text directly, so misclassified images are still findable by content
