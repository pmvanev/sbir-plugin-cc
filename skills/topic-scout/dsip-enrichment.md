---
name: dsip-enrichment
description: Domain knowledge for interpreting DSIP topic detail structure, Q&A format, completeness assessment, and enrichment data used in semantic scoring
---

# DSIP Topic Enrichment

## Data Sources

Enrichment uses 3 DSIP API endpoints per topic, plus instruction PDF downloads. No browser or PDF-only extraction — all data comes from structured API responses.

| Source | Endpoint | Data |
|--------|----------|------|
| Topic Details | `GET /topics/{hash_id}/details` | Description, objective, phases, keywords, technology areas, ITAR, CMMC |
| Q&A | `GET /topics/{hash_id}/questions` | Structured question/answer entries with HTML content |
| Solicitation Instructions | `GET /submissions/download/solicitationDocuments?documentType=RELEASE_PREFACE&...` | BAA preface PDF (text extracted) |
| Component Instructions | `GET /submissions/download/solicitationDocuments?documentType=INSTRUCTIONS&component={comp}&...` | Component-specific PDF (text extracted) |

Full API reference: `docs/dsip-api-reference.md`

## Topic Detail Fields

From the `/details` endpoint (structured JSON with HTML content):

| Field | Type | Scoring Value |
|-------|------|---------------|
| `description` | HTML string | High — primary input for subject matter expertise scoring |
| `objective` | HTML string | High — concise statement of what the government wants |
| `phase1_description` | HTML string | Medium — Phase I scope, duration, funding ceiling |
| `phase2_description` | HTML string | Medium — Phase II follow-on expectations |
| `phase3_description` | HTML string | Low-Medium — commercialization pathway |
| `keywords` | string list | High — direct input for keyword matching |
| `technology_areas` | string list | Medium — broad technical categorization |
| `focus_areas` | string list | Medium — modernization priorities |
| `itar` | boolean | Critical — disqualifier if company lacks clearance |
| `cmmc_level` | string | Critical — cybersecurity maturity requirement |
| `reference_documents` | list of dicts | Low — cited papers and standards |

## Q&A Format

From the `/questions` endpoint (JSON array):

Each entry contains:
- `question_no` — sequential number
- `question` — HTML string with the proposer's question
- `answer` — HTML string with the TPOC's response (parsed from nested JSON `{"content": "..."}`)
- `submitted_on` — Unix timestamp of when the question was submitted

Q&A significance for scoring:
- Clarifies scope boundaries and acceptable technical approaches
- May narrow or expand the topic beyond what the description states
- TPOC answers are authoritative interpretations
- Topics with 0 Q&A are normal (especially pre-release topics)

When `published_qa_count` from the search response is 0, the Q&A API call is skipped (no network request).

## Instruction Documents

### Solicitation Instructions (BAA Preface)
- Downloaded as PDF, text extracted via pypdf
- Contains: page limits, formatting requirements, evaluation criteria, submission portal details
- Shared across all topics in a solicitation cycle
- Cached by (cycle_name, release_number) — one download per cycle

### Component Instructions
- Downloaded as PDF, text extracted via pypdf
- Contains: component-specific submission rules, additional evaluation criteria, TRL expectations
- Cached by (cycle_name, component, release_number) — one download per component per cycle
- Components: ARMY, NAVY, USAF, DARPA, CBD, DHA, MDA, SOCOM, OSD, DTRA, NGA, DLA, DCSA

## Completeness Assessment

After enrichment, the CLI reports completeness for all 4 data types:

```
Descriptions: 24/24
Q&A: 18/24 (6 topics had no Q&A posted)
Solicitation Instructions: 24/24
Component Instructions: 24/24
```

| Level | Descriptions | Q&A | Instructions |
|-------|-------------|-----|-------------|
| Full | N/M = M/M | Any (variable) | N/M = M/M |
| Adequate | >= 80% | Any | >= 50% |
| Degraded | < 80% | Any | < 50% |

- **Descriptions** are critical. Below 80% warrants investigation (API may have changed).
- **Q&A** is inherently variable — many topics have 0 Q&A. This is normal, not a failure.
- **Instructions** should be near 100% for active solicitations. Failures indicate download issues.
- Per-topic failures set `enrichment_status: "partial"` — the topic still has other data.

## Enriched Data in Scoring

With full enrichment, the topic-scout agent has:
- **Description + objective** for deep semantic matching against company capabilities
- **Keywords + technology_areas** for precise keyword overlap scoring
- **Q&A entries** for scope refinement (e.g., "Phase I can use simulated data")
- **ITAR flag** for eligibility disqualification
- **CMMC level** for cybersecurity maturity gating
- **Instructions** for advising on page limits, formatting, and evaluation criteria

This is a complete picture. The agent should not need to send the user to dodsbirsttr.mil for any topic-level information.
