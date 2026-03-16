---
name: corpus-image-reuse
description: Domain knowledge for corpus image reuse -- search strategies, fitness assessment interpretation, caption adaptation heuristics, compliance flagging guidance, and the reuse workflow
---

# Corpus Image Reuse

## Image Search Strategies

### When to Filter by Type
Use `--type` when the figure plan specifies a known figure type (system-diagram, schedule, org-chart). This narrows results to structurally compatible images. Best for: replacing a planned figure with an existing one of the same type.

### When to Filter by Agency
Use `--agency` when reusing figures for the same agency. Evaluators recognize familiar visual styles. An Air Force proposal benefits from reusing Air Force WIN figures because the visual conventions (labeling, color use, detail level) align with evaluator expectations.

### When to Filter by Outcome
Use `--outcome WIN` as the default search strategy. Winning proposals contain figures that passed evaluator scrutiny. LOSS-outcome figures may still be reusable if the figure itself was not a weakness (check debrief feedback).

### When to Search Broadly
Search without filters when:
- The corpus is small (<20 images) -- filtering over-restricts
- The technical domain is niche -- same-agency matches may not exist
- Exploring what is available before narrowing

### Relevance Scoring Weights

| Factor | Weight | Rationale |
|--------|--------|-----------|
| Caption match | 0.40 | Strongest signal -- caption describes what the figure shows |
| Agency match | 0.25 | Same-agency figures align with evaluator visual expectations |
| Outcome boost | 0.20 | WIN figures passed scrutiny; LOSS figures are lower confidence |
| Recency | 0.15 | Recent figures use current technology terms and visual standards |

## Fitness Assessment Interpretation

### Quality (DPI-based)

| Level | DPI Range | Print Suitability | Action |
|-------|-----------|-------------------|--------|
| HIGH | >= 300 | Print-ready. Meets all agency requirements. | Use as-is |
| MEDIUM | 150-299 | Acceptable for screen review. May degrade in print. | Use with caution; consider upscaling or replacement if print submission |
| LOW | < 150 | Unsuitable for print. May appear pixelated. | Replace with de novo generation or find higher-resolution source |

Resolution context: Most SBIR solicitations require 300 DPI for raster figures. Vector formats (SVG) are resolution-independent and always HIGH quality.

### Freshness (Age-based)

| Level | Age | Meaning | Action |
|-------|-----|---------|--------|
| OK | <= 12 months | Current technology landscape. Terms and visual conventions are up-to-date. | Use without freshness concern |
| WARNING | 12-24 months | May reference outdated terms, TRL levels, or program names. | Review for outdated content before reuse |
| STALE | > 24 months | Likely contains outdated references. Evaluators may notice. | Prefer de novo generation. Use only if no alternative and content is still accurate. |

### Agency Match

An image sourced from the same agency as the current proposal receives an agency match boost. Cross-agency reuse is valid but review for:
- Agency-specific terminology (DoD vs. NASA vs. civilian)
- Visual style expectations (DoD tends toward clean technical diagrams; NASA favors detailed system visualizations)
- Classification marking conventions

### Label Warnings

The fitness assessment flags proposal-specific terms found in captions or embedded text:
- Proposal IDs (e.g., "AF243-001")
- Topic numbers (e.g., "Topic N123-456")
- Program-specific acronyms (e.g., "CDES" from a prior proposal)
- Company-specific internal project names

These require caption adaptation before reuse. Embedded text in the image itself requires manual review -- the system cannot edit raster image content.

## Caption Adaptation Heuristics

### What Gets Adapted
Caption text is genericized by removing or replacing proposal-specific terms:

| Pattern | Original Example | Adapted Example |
|---------|-----------------|-----------------|
| Proposal ID in caption | "Figure 3: CDES Architecture for AF243-001" | "Figure 3: System Architecture Overview" |
| Topic number reference | "...addressing Topic AF243-001" | "...addressing the solicitation topic" |
| Prior program acronym | "CDES Phase I system" | "[Program Name] Phase I system" or generic description |
| Specific contract number | "under contract FA8750-24-C-0001" | Removed entirely |
| Prior company name (if different entity) | "Acme Corp's approach" | "The proposed approach" |

### What Stays Unchanged
- Technical terms common to the domain (e.g., "directed energy", "phased array")
- Standard acronyms defined in the current proposal (e.g., "UAS", "C2")
- Figure type descriptors (e.g., "System Architecture", "Project Timeline")
- Component labels that match current proposal content

### Manual Review Items
When the adaptation service identifies embedded text in the image (text rendered as pixels, not metadata), it flags these for human review. The system presents: the image, the identified embedded text regions, and a recommendation to verify relevance. The user decides whether the embedded text is acceptable or requires image editing outside the system.

## Compliance Flagging Guidance

### When to Flag

| Reason | Description | Risk |
|--------|-------------|------|
| Government-furnished | Image provided by a government agency as GFI/GFE. Ownership unclear. | Reuse without permission may violate contract terms |
| ITAR-marked | Image or source document contains ITAR markings or export-controlled content | Reuse in a different program may violate export controls |
| Classified markings | Image or context contains classification markings (CUI, FOUO, SECRET) | Reuse outside original classification context is prohibited |
| Unverified ownership | Image source is ambiguous -- may be from a subcontractor, teaming partner, or third party | Copyright/IP risk |
| Contains PII | Image contains personally identifiable information (names, contact info on org charts) | Privacy risk if reused without consent |

### Flag Lifecycle
1. Any user can flag an image: `corpus images flag <id> --reason "<text>"`
2. Flagged images appear with a compliance warning in all listings and search results
3. Flagged images are blocked from `corpus images use` -- the system returns a clear error
4. A user resolves the concern externally (reviews contract, obtains permission, redacts content)
5. User removes the flag: `corpus images unflag <id>`
6. The unflag action is logged but does not require justification in the system

### Default Unflagged
Images extracted from company-owned past proposals are unflagged by default. The `origin_type` field distinguishes:
- `company-created`: Unflagged. Standard reuse candidate.
- `government-furnished`: Auto-flagged at extraction if detected via document metadata or markings.
- `third-party`: Auto-flagged at extraction if source attribution indicates external origin.

## Reuse Workflow

The end-to-end workflow for reusing a corpus image in a new proposal:

```
1. SEARCH: corpus images search "<query>" [--filters]
   -> Ranked results with relevance scores

2. ASSESS: corpus images show <id>
   -> Provenance, quality, freshness, agency match, label warnings, compliance status

3. ADAPT: corpus images use <id> --section <section> --figure-number <N>
   -> Side-by-side caption comparison, manual review items listed
   -> Human approves or rejects

4. REVIEW (Wave 5): Formatter presents corpus-reuse figure with approve/revise/replace options
   -> Approve: figure accepted for Wave 6 insertion
   -> Revise: caption or placement adjusted
   -> Replace: figure removed from corpus-reuse, switched to de novo generation

5. ASSEMBLE (Wave 6): Approved corpus-reuse figure inserted at specified position
   -> Cross-reference validated
   -> Attribution recorded in figure log
```

### Decision Points

| Decision | Criteria | Outcome |
|----------|----------|---------|
| Use corpus image vs. generate new | Image exists at HIGH quality, same type, relevant content, no compliance flags | Reuse saves generation time |
| Flag vs. proceed | Any doubt about ownership, markings, or classification | Flag first, investigate, then decide |
| Adapt caption vs. use as-is | Caption contains proposal-specific terms or prior program references | Adapt; never reuse a caption referencing another proposal |
| Approve vs. replace at Wave 5 | Image quality adequate, caption adapted, content relevant to current narrative | Approve if all three criteria met; replace otherwise |
