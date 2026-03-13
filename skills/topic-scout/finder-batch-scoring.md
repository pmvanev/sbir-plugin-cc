---
name: finder-batch-scoring
description: Batch scoring workflow for solicitation finder -- orchestrates five-dimension scoring of candidate topics against company profile, produces ranked results with recommendations and disqualifiers
---

# Finder Batch Scoring

## Purpose

After keyword pre-filtering produces candidate topics, batch scoring evaluates each candidate against the company profile using the five-dimension fit model. This skill provides the workflow steps, error handling, and output format for batch scoring mode.

## Batch Scoring Workflow

### Input Requirements

1. **Candidate topics**: List of topic dicts from pre-filter phase (typically 20-60 topics)
2. **Company profile**: Full profile from `~/.sbir/company-profile.json` with capabilities, certifications, past performance, key personnel, and research partners
3. **Scoring service**: `TopicScoringService` from `scripts/pes/domain/topic_scoring.py`

### Execution Steps

1. Instantiate `TopicScoringService`
2. Call `score_batch(topics, profile)` -- scores all topics, returns sorted by composite descending
3. Each `ScoredTopic` result contains: `topic_id`, `composite_score`, `dimensions` (5 scores), `recommendation`, `disqualifiers`, `warnings`, `key_personnel_match`
4. Separate results into qualified (GO/EVALUATE) and disqualified (NO-GO with disqualifiers)
5. Format ranked table for display
6. Persist results via `FinderResultsPort`

### Disqualifier Detection

Hard disqualifiers produce immediate NO-GO regardless of composite score:

- **Clearance gap**: Topic requires TS clearance but profile has Secret or lower
- **STTR without partner**: STTR program topic when `research_institution_partners` is empty

### Recommendation Logic

| Condition | Recommendation |
|-----------|---------------|
| Disqualifier present | NO-GO |
| Eligibility = 0.0 (ineligible) | NO-GO |
| Certifications = 0.0 (no SAM.gov) | NO-GO |
| Composite >= 0.60, no disqualifiers | GO |
| Composite >= 0.30 | EVALUATE |
| Composite < 0.30 | NO-GO |
| Empty past performance + composite >= 0.30 | EVALUATE (capped) |

### Output: Ranked Table

Display scored topics in two sections:

**Qualified Topics** (sorted by composite descending):
```
Rank | Topic ID    | Agency    | Title                              | Score | Rec      | Deadline
   1 | AF263-042   | Air Force | Compact Directed Energy for C-UAS  | 0.84  | GO       | 2026-05-15
   2 | N263-044    | Navy      | Shipboard RF Power Management      | 0.47  | EVALUATE | 2026-06-01
```

**Disqualified Topics** (separate section):
```
Topic ID    | Agency    | Title                           | Reason
AF263-099   | Air Force | Classified Sensor Fusion        | Requires TS clearance (profile: Secret)
N263-S05    | Navy      | Academic-Industry RF Collab      | No research institution partner
```

### Output: Detail Drilldown

Per-topic detail shows:
- All five dimension scores with rationale
- Matching key personnel from company profile
- Disqualification reasons (if any)
- Deadline with days remaining

### Performance

- Scoring is pure computation (no I/O) -- 50 topics scores in under 1 second
- The 10-minute budget is for the full pipeline including LLM-assisted scoring (future enhancement)
- Current implementation uses keyword-based heuristics, not LLM scoring

## Profile Gap Handling

When profile sections are missing:

| Missing Section | Effect |
|----------------|--------|
| `capabilities` | SME dimension = 0.0 |
| `past_performance` | PP dimension = 0.0, warning issued, recommendations capped at EVALUATE |
| `certifications` | Cert dimension = 0.0 (NO-GO if no SAM.gov) |
| `key_personnel` | No personnel matching, scoring unaffected |
| `research_institution_partners` | STTR topics disqualified |

## Integration Points

- **Upstream**: `FinderService.search_and_filter()` produces candidate topics
- **Scoring**: `TopicScoringService.score_batch()` produces scored results
- **Downstream**: `FinderResultsPort.write()` persists results for later reference
- **Display**: Agent formats results as ranked table and detail views
