---
name: fit-scoring-methodology
description: Domain knowledge for five-dimension company fit scoring against SBIR/STTR solicitation topics -- scoring rubrics, company profile integration, composite scoring, and recommendation thresholds
---

# Fit Scoring Methodology

## Five Scoring Dimensions

Each dimension scores 0.0 to 1.0. The composite score is a weighted average.

### 1. Subject Matter Expertise (weight: 0.35)

Match company technical capabilities against the solicitation topic.

| Score Range | Criteria |
|------------|---------|
| 0.8-1.0 | Core competency. Multiple team members with deep expertise. Published work or patents in the area. |
| 0.5-0.7 | Adjacent competency. Team has related experience, could credibly pivot. |
| 0.2-0.4 | Tangential. Some relevant skills but significant capability gap. |
| 0.0-0.1 | No match. Topic outside company's technical domain. |

Scoring inputs:
- Company profile `capabilities` field keywords vs. solicitation description keywords
- Corpus documents in same technical domain (content analysis)
- Key personnel expertise alignment

### 2. Past Performance Relevance (weight: 0.25)

Corpus-backed assessment of prior work in the same agency and domain.

| Score Range | Criteria |
|------------|---------|
| 0.8-1.0 | Winning proposal with same agency in same domain. Multiple relevant past performances. |
| 0.5-0.7 | Past work in same domain, different agency. Or same agency, adjacent domain. |
| 0.2-0.4 | Limited past performance. One tangentially related effort. |
| 0.0 | No corpus data available or no relevant past work found. |

Scoring inputs:
- Corpus search results: count and relevance of matches
- Win/loss data: win rate by agency and domain
- Recency: more recent past performance weighted higher

### 3. Certifications and Registrations (weight: 0.15)

Administrative eligibility and competitive advantages from certifications.

| Score Range | Criteria |
|------------|---------|
| 1.0 | Active SAM.gov registration + all required certifications for this topic. |
| 0.7-0.9 | Active SAM.gov + most certifications. Minor gaps addressable before deadline. |
| 0.3-0.6 | Active SAM.gov but missing key certifications (e.g., required clearance). |
| 0.0 | No SAM.gov registration (disqualifying for federal contracts). |

Certifications to check (from company profile):
- SAM.gov registration (required for all SBIR/STTR)
- Socioeconomic status: 8(a), HUBZone, WOSB, SDVOSB, VOSB
- Security clearances: if topic requires classified work
- ITAR compliance: if topic involves controlled technology
- Small business size standard: under 500 employees (SBIR requirement)

### 4. Phase Eligibility (weight: 0.15)

Structural eligibility requirements for the specific phase.

| Score Range | Criteria |
|------------|---------|
| 1.0 | Fully eligible. All phase requirements met. |
| 0.5 | Likely eligible but needs verification (e.g., employee count near threshold). |
| 0.0 | Ineligible. Disqualifying factor present. |

Phase-specific checks:
- **Phase I**: small business status (< 500 employees), US ownership/control
- **Phase II**: typically requires prior Phase I award in same topic (check for Direct-to-Phase-II exceptions)
- **Direct-to-Phase-II**: verify agency offers this path, check eligibility criteria
- **SBIR vs STTR**: SBIR requires 2/3 work by small business; STTR requires research institution partner performing at least 30% of work

### 5. STTR Research Institution Requirements (weight: 0.10)

Only applicable to STTR topics. For SBIR topics, score 1.0 (no institution required).

| Score Range | Criteria |
|------------|---------|
| 1.0 | SBIR topic (no institution needed) OR established research institution partnership. |
| 0.5-0.7 | Potential institution partners identified but no formal agreement. |
| 0.2-0.4 | No current institution partner, topic requires one. Acquisition feasible. |
| 0.0 | STTR topic with no path to research institution partnership. |

## Composite Score Calculation

```
composite = (sme * 0.35) + (pp * 0.25) + (cert * 0.15) + (elig * 0.15) + (sttr * 0.10)
```

## Recommendation Thresholds

| Recommendation | Criteria |
|---------------|---------|
| **go** | composite >= 0.6 AND no dimension at 0.0 (except past_performance when corpus is empty) |
| **evaluate** | composite 0.3-0.6 OR any non-eligibility dimension at 0.0 OR sparse data |
| **no-go** | composite < 0.3 OR eligibility = 0.0 (disqualifying) OR certifications = 0.0 (no SAM.gov) |

Override rules:
- Eligibility = 0.0 always produces "no-go" regardless of composite
- Certifications = 0.0 (no SAM.gov) always produces "no-go"
- Empty corpus degrades past_performance to 0.0 but recommendation caps at "evaluate" (not "no-go" from data absence alone)
- Deadline within 3 days: append "URGENT" flag to any recommendation

## Company Profile Schema

Expected fields in `~/.sbir/company-profile.json`:

```json
{
  "company_name": "string",
  "capabilities": ["keyword1", "keyword2"],
  "certifications": {
    "sam_gov": { "active": true, "cage_code": "string", "uei": "string" },
    "socioeconomic": ["8(a)", "HUBZone", "WOSB"],
    "security_clearance": "none | confidential | secret | top_secret",
    "itar_registered": false
  },
  "employee_count": 15,
  "key_personnel": [
    { "name": "string", "role": "string", "expertise": ["keyword1"] }
  ],
  "past_performance": [
    { "agency": "string", "topic_area": "string", "outcome": "string" }
  ],
  "research_institution_partners": []
}
```

When the company profile is missing or incomplete:
- Score certifications and eligibility as 0.0
- Score subject matter from solicitation analysis only
- Warn that accuracy is degraded
- Recommend creating profile: "Run /sbir:proposal profile setup to create your company profile."

## Partnership-Aware Scoring

When a partner profile is available (from `~/.sbir/partners/{slug}.json`), display **dual-column scoring** showing both solo and partnership results.

### How Partnership Affects Dimensions

| Dimension | Partnership Effect |
|-----------|-------------------|
| SME (0.35) | Union of company + partner capabilities (deduplicated) |
| Past Performance (0.25) | Company PP only (partner's independent PP is not our data) |
| Certifications (0.15) | Company certifications only (partner doesn't affect SAM.gov) |
| Eligibility (0.15) | Company eligibility only (employee count, phase) |
| STTR (0.10) | Partner type used for STTR research institution check |

### Dual-Column Display Format

When partner profiles exist, show both columns and the delta:

```
Topic: N244-012 -- Autonomous UUV Navigation and Sensing (STTR)
           Solo    Partnership   Delta
SME:       0.12    0.65         +0.53
PP:        0.30    0.30          0.00
Cert:      1.00    1.00          0.00
Elig:      1.00    1.00          0.00
STTR:      0.00    1.00         +1.00
─────────────────────────────────────
Composite: 0.32    0.68         +0.36
Recommend: EVALUATE GO           ▲ ELEVATED
```

### Score Delta and Elevation

- **Delta**: partnership_score - solo_score per dimension
- **Elevation**: When recommendation changes (e.g., EVALUATE -> GO), mark with ▲ ELEVATED
- **Minimal impact**: When delta < 0.05 on all dimensions, note "Partnership has minimal impact on this topic"

### When to Show Partnership Scoring

- Partner profiles exist at `~/.sbir/partners/` -> always show dual columns
- No partner profiles -> solo scoring only (current behavior)
- STTR topic with no partner -> solo column shows NO-GO with disqualifier, suggest `/proposal partner-setup`

## Recording Scores to State

Map scores to `FitScoring` dataclass (from `scripts/pes/domain/proposal_service.py`):

```python
FitScoring(
    subject_matter=0.85,       # SME dimension score
    past_performance=0.60,     # PP dimension score
    certifications=1.0,        # Cert dimension score (not stored separately)
    recommendation="go"        # Overall recommendation string
)
```

Note: The `FitScoring` dataclass has four fields. The five-dimension scores map as:
- `subject_matter` -> SME dimension
- `past_performance` -> PP dimension
- `certifications` -> max(certifications, eligibility, sttr) as a proxy
- `recommendation` -> the overall recommendation string
