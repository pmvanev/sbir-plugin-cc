---
name: partner-domain
description: Partner profile field-by-field interview guidance, schema reference, validation rules, STTR eligibility, and combined capability analysis for the partner builder agent
---

# Partner Domain Knowledge

## Partner Profile Schema

Partner profiles at `~/.sbir/partners/{slug}.json` capture research institution data for partnership-aware proposal generation. Every field feeds into one or more downstream agents.

```json
{
  "partner_name": "string",
  "partner_slug": "string (lowercase, hyphens, derived from name)",
  "partner_type": "university | federally_funded_rdc | nonprofit_research",
  "capabilities": ["keyword1", "keyword2"],
  "key_personnel": [
    {
      "name": "string",
      "role": "Co-PI | Researcher | Lab Director | etc.",
      "expertise": ["keyword1", "keyword2"]
    }
  ],
  "facilities": [
    {
      "name": "string",
      "description": "string (optional)"
    }
  ],
  "past_collaborations": [
    {
      "agency": "string",
      "topic_area": "string",
      "outcome": "WIN | LOSS | ONGOING",
      "year": "integer (optional)"
    }
  ],
  "sttr_eligibility": {
    "qualifies": true,
    "minimum_effort_capable": true,
    "notes": "string (optional)"
  },
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

## Field-by-Field Interview Guidance

### partner_name
**Downstream impact**: Display name used in strategy briefs, proposal drafts, and scoring reports. Must match how the institution is formally known.
**Interview guidance**: "What is the full formal name of the research institution? Use the name as it would appear on a teaming agreement -- e.g., 'University of Colorado Boulder', not 'CU Boulder'."

### partner_type
**Downstream impact**: STTR eligibility validation. Only `university`, `federally_funded_rdc`, and `nonprofit_research` qualify as STTR research institutions per SBA rules.
**Interview guidance**: "What type of research institution is this? Options: university, federally funded R&D center (FFRDC), or nonprofit research organization. This determines STTR eligibility -- STTR requires one of these three types."

### capabilities
**Downstream impact**: Combined with company capabilities for topic scoring (SME dimension, weight 0.35). Union of company + partner keywords is matched against solicitation requirements. More specific keywords = more accurate scoring.
**Interview guidance**: "List the partner's core technical capabilities as keywords -- e.g., 'autonomous navigation', 'underwater acoustics', 'sensor fusion'. These are combined with your company's capabilities when scoring topics. Focus on capabilities that complement yours rather than duplicate them."

### key_personnel
**Downstream impact**: Named in strategy brief teaming section and proposal drafts. Expertise keywords feed combined SME scoring. Role determines proposal positioning (Co-PI is most common for research partners).
**Interview guidance**: "For each key person at the partner institution who would appear on proposals: provide their name, role (typically Co-PI or Researcher), and expertise keywords. Focus on the PI and 1-2 key researchers."

### facilities
**Downstream impact**: Referenced in strategy brief and proposal facilities sections. Critical for proposals requiring specialized lab access, test environments, or equipment.
**Interview guidance**: "What specialized facilities does the partner have that are relevant to proposals? Examples: 'underwater acoustics lab', 'GPU compute cluster', 'anechoic chamber'. Include a brief description if the facility name isn't self-explanatory."

### past_collaborations
**Downstream impact**: Strengthens past performance narrative in proposals. Joint history with the same agency is especially valuable. Feeds debrief analyst for win/loss tracking.
**Interview guidance**: "List any previous proposals or contracts you've worked on together. For each: the sponsoring agency, topic area, and outcome (WIN, LOSS, or ONGOING). Include the year if you remember it. This strengthens the 'established team' narrative in proposals."

### sttr_eligibility
**Downstream impact**: Binary gate for STTR topics. If `qualifies` is false, partner cannot be used for STTR. If `minimum_effort_capable` is false, partner may not be able to meet 30% Phase I / 40% Phase II work requirements.
**Interview guidance**: "Does this institution qualify as an STTR research institution? (Must be a university, FFRDC, or nonprofit research org.) Can they commit to performing at least 30% of Phase I work and 40% of Phase II work? Any notes on capacity constraints?"

## Slug Generation

The partner slug is deterministic from the partner name:
1. Lowercase the name
2. Replace spaces and special characters with hyphens
3. Collapse multiple hyphens
4. Trim leading/trailing hyphens

Examples:
- "University of Colorado Boulder" -> "university-of-colorado-boulder"
- "Southwest Research Institute" -> "southwest-research-institute"
- "North Dakota State University" -> "north-dakota-state-university"

## Partner Type Definitions

| Type | SBA Definition | Examples |
|------|---------------|----------|
| `university` | Accredited institution of higher education | CU Boulder, MIT, Stanford, NDSU |
| `federally_funded_rdc` | Federally funded research and development center | SWRI, MITRE, Sandia, Los Alamos |
| `nonprofit_research` | Nonprofit scientific or educational institution | SRI International, Battelle |

## Combined Capability Analysis

When displaying partner profile previews, show the combined capability analysis:

```
COMBINED CAPABILITIES
---------------------
Company only:    directed energy, RF engineering
Partner only:    autonomous navigation, underwater acoustics, sensor fusion
Overlap:         machine learning
Combined total:  6 unique capabilities
```

This helps the user see how the partnership extends their capability footprint for topic scoring.

## STTR Work Split Rules

- Phase I: Research institution must perform >= 30% of work
- Phase II: Research institution must perform >= 40% of work
- The SBC (small business) must perform the "primary" research
- Work split is tracked in strategy brief and approach generation, not in the partner profile itself

## Validation Rules

1. `partner_name` must be non-empty
2. `partner_slug` must match pattern `^[a-z0-9]+(-[a-z0-9]+)*$`
3. `partner_type` must be one of the three enumerated values
4. `capabilities` must have at least 1 entry
5. Each `key_personnel` entry must have name, role, and at least 1 expertise keyword
6. `facilities` entries must have a name (description is optional)
7. `past_collaborations` entries must have agency, topic_area, and outcome
8. `sttr_eligibility` must have qualifies and minimum_effort_capable booleans
9. `created_at` and `updated_at` must be valid ISO-8601 timestamps

## File Safety

- Partner profiles are stored one-per-file at `~/.sbir/partners/{slug}.json`
- Always check for existing profile before writing (overwrite protection)
- Atomic writes: write to `.tmp`, rename to target
- Back up existing profile to `.bak` before overwrite
- Cancel at any point writes no files

## Screening Mode

The partner builder can operate in screening mode (invoked via `/proposal partner-screen`). In screening mode:

1. Ask 5 readiness questions (timeline, bandwidth, SBIR experience, POC assignment, scope agreement)
2. Each signal rates as: ok, caution, or unknown
3. Produce recommendation: PROCEED, PROCEED WITH CAUTION, or DO NOT PROCEED
4. Results saved to `.sbir/partner-screenings/{slug}.json` (project-level, not global)
5. On PROCEED, offer to transition to `/proposal partner-setup` for full profile creation
