---
name: dsip-enrichment
description: Domain knowledge for interpreting DSIP topic detail structure, Q&A format, completeness assessment, and enrichment data used in semantic scoring
---

# DSIP Topic Enrichment

## DSIP Topic Detail Structure

Each DSIP topic has a detail page/PDF containing structured sections beyond the listing metadata. The enrichment process downloads per-topic PDFs via `GET /topics/api/public/topics/{hash_id}/download/PDF` and extracts these sections.

### Primary Sections

| Section | Content | Scoring Value |
|---------|---------|---------------|
| Description | Full technical description with background, objectives, TRL expectations | High -- primary input for subject matter expertise scoring |
| Phase I Expected Deliverables | Scope, duration (typically 6 months), funding ceiling, deliverable expectations | Medium -- phase eligibility and feasibility assessment |
| Phase II Expected Deliverables | Follow-on scope, duration (typically 24 months), funding ceiling | Medium -- long-term alignment assessment |
| Phase III Potential | Commercialization and transition pathway expectations | Low-Medium -- strategic fit indicator |
| Keywords | Agency-assigned technical keywords for the topic | High -- direct input for keyword matching and pre-filter validation |
| References | Published papers, standards, and prior work cited by the topic author | Medium -- indicates expected technical depth and relevant literature |
| TPOC (Technical Point of Contact) | Name, email, phone of the topic author | Low -- informational, not used in scoring |

### Supplementary Sections (When Present)

| Section | Content | Notes |
|---------|---------|-------|
| Submission Instructions | Agency- or component-specific submission guidance | May override default BAA instructions |
| Component Instructions | Branch- or lab-specific requirements (e.g., AFRL, ONR, DARPA) | May include unique formatting, page limits, or evaluation criteria |
| ITAR/Export Control | Indicates if topic involves controlled technology | Critical for eligibility dimension scoring |
| Security Classification | Required clearance level (Unclassified, Secret, TS/SCI) | Disqualifier if company lacks required clearance |

## Q&A Format and Parsing

DSIP topics may have a Q&A section where proposers ask questions and the topic author responds. Q&A is published during the pre-release or open period.

### Q&A Structure
- Each entry: question text, answer text, date posted
- Questions often clarify: scope boundaries, acceptable approaches, TRL expectations, teaming requirements
- Answers from the TPOC provide authoritative interpretation of the topic description

### Parsing Guidance
- Q&A may be embedded in the topic PDF or available via a separate API endpoint
- The DSIP Angular app loads Q&A dynamically; PDF extraction may not capture all Q&A
- When Q&A is not extractable from PDF, the enrichment adapter degrades gracefully (records as missing in completeness metrics)
- Q&A content supplements the description for semantic scoring but is not required for a valid enrichment

## Submission Instructions Structure

Submission instructions define the procedural requirements for a proposal:
- Page limits per volume (Technical Volume, Cost Volume, Company Commercialization Report)
- Font and formatting requirements
- Required sections and their order
- Submission portal and deadline details
- Any component-specific overrides to the default BAA instructions

### Component-Specific Instructions
Some DoD components (AFRL, ONR, DARPA, MDA, SOCOM) publish additional instructions that supplement or override the base BAA:
- Additional evaluation criteria or weighting changes
- Technology readiness level expectations specific to the component
- Teaming or subcontracting preferences
- Data rights expectations

## Completeness Assessment Criteria

After enrichment, assess completeness across three dimensions. Report metrics in the format:
```
Descriptions N/M | Instructions N/M | Q&A N/M
```

Where N = successfully extracted count, M = total candidates attempted.

### Completeness Levels

| Level | Description Extraction | Instruction Extraction | Q&A Extraction |
|-------|----------------------|----------------------|----------------|
| Full | N/M = M/M | N/M = M/M | N/M = M/M |
| Adequate | N/M >= 80% | N/M >= 50% | Any (best-effort) |
| Degraded | N/M < 80% | N/M < 50% | N/A |
| Failed | N/M = 0/M | N/M = 0/M | N/A |

### Assessment Rules
- **Descriptions** are the critical enrichment component. Below 80% extraction rate warrants a warning: scoring accuracy is reduced for topics without descriptions.
- **Instructions** are important but not scoring-critical. Missing instructions do not affect fit scoring, but the user should be informed before proposal writing.
- **Q&A** is best-effort. Many topics have no Q&A (especially pre-release topics). Missing Q&A is expected and does not trigger warnings.
- Per-topic failures are isolated. A single topic failing enrichment does not invalidate the batch.

## Known API Endpoints and Parameters

### Topic Listing (Existing -- DsipApiAdapter)
```
GET /topics/api/public/topics/search
Parameters: keyword, agency, phase, status, page, size
Response: { total: int, data: [{ topicId, title, agency, phase, ... }] }
```

### Topic Detail PDF (Enrichment -- DsipEnrichmentAdapter)
```
GET /topics/api/public/topics/{hash_id}/download/PDF
Response: PDF binary content
Content-Type: application/pdf
```

### Rate Limiting
- DSIP API does not publish rate limits
- Enrichment adapter uses configurable delay between requests (default: respectful pacing)
- Exponential backoff on 429 or 5xx responses (reuses DsipApiAdapter retry pattern)

## Enriched Data in Semantic Scoring

Enriched descriptions enable deeper semantic scoring in Phase 3 (SCORE):
- **Title-only scoring** (pre-enrichment): limited to keyword overlap with short title text. Misses TRL expectations, teaming requirements, and phase-specific technical detail.
- **Enriched scoring** (post-enrichment): full description text enables LLM semantic comparison against company capabilities, past performance narratives, and key personnel expertise. Produces higher-confidence subject matter expertise scores.

When enriched descriptions are available, the topic scout agent should use them as the primary input for the Subject Matter Expertise dimension (weight 0.35 of composite score). When descriptions are missing for specific topics, fall back to title-only scoring for those topics and note reduced confidence in the per-topic detail drilldown.
