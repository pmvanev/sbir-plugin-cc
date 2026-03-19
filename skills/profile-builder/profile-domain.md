---
name: profile-domain
description: Company profile field-by-field fit scoring explanations, schema reference, validation rules, and interview guidance for the profile builder agent
---

# Profile Domain Knowledge

## Profile Schema

The company profile at `~/.sbir/company-profile.json` feeds directly into the five-dimension fit scoring system. Every field maps to one or more scoring dimensions.

```json
{
  "company_name": "string",
  "capabilities": ["keyword1", "keyword2"],
  "certifications": {
    "sam_gov": {
      "active": true,
      "cage_code": "string (5 alphanumeric)",
      "uei": "string"
    },
    "socioeconomic": ["8(a)", "HUBZone", "WOSB", "SDVOSB", "VOSB"],
    "security_clearance": "none | confidential | secret | top_secret",
    "itar_registered": false
  },
  "employee_count": 15,
  "key_personnel": [
    {
      "name": "string",
      "role": "PI | Co-PI | Lead Engineer | etc.",
      "expertise": ["keyword1", "keyword2"]
    }
  ],
  "past_performance": [
    {
      "agency": "string",
      "topic_area": "string",
      "outcome": "WIN | LOSS | ONGOING"
    }
  ],
  "research_institution_partners": [
    {
      "name": "string",
      "type": "university | federally_funded_rdc | nonprofit_research"
    }
  ],
  "sources": {
    "web_references": [
      { "url": "https://sam.gov/entity/...", "label": "SAM.gov entity page", "accessed_at": "ISO-8601" }
    ],
    "documents_scanned": [
      { "path": "/path/to/capability-statement.pdf", "label": "Capability statement", "scanned_at": "ISO-8601" }
    ],
    "directories_scanned": [
      { "path": "/path/to/past-proposals/", "file_count": 8, "scanned_at": "ISO-8601" }
    ]
  }
}
```

## Source Provenance

The `sources` field records where profile data came from. It is populated automatically during research and document extraction phases. Not used for scoring — purely for traceability so the user can revisit original references.

- **web_references**: URLs consulted during Phase 2 (RESEARCH). Includes SAM.gov pages, sbir.gov award records, company websites, LinkedIn pages, etc.
- **documents_scanned**: Local files the user provided during Phase 3 (GATHER) in document or both mode. Capability statements, SAM.gov exports, past proposal excerpts, etc.
- **directories_scanned**: Directories scanned during corpus ingestion that fed data into the profile. Records the path and number of files found.

The `sources` field is optional — profiles created before this feature lack it. Agents should handle missing `sources` gracefully.

## Field-by-Field Fit Scoring Explanations

### company_name

**Scoring impact**: None (display only).
**What to collect**: Legal company name as registered with SAM.gov.
**Interview guidance**: "This is your company name as it will appear in proposals. Use the name registered in SAM.gov for consistency."

### capabilities

**Scoring impact**: Subject Matter Expertise dimension (weight 0.35). Capabilities keywords are matched against solicitation topic descriptions using keyword overlap analysis. Higher overlap = higher SME score. This is the single most influential dimension in composite scoring.
**What to collect**: Technical competency keywords. Specific beats generic: "millimeter-wave radar signal processing" scores better than "engineering" because solicitations use specific language.
**Interview guidance**: "List your core technical competencies as keywords or short phrases. Be specific -- 'directed energy systems' is more useful than 'defense technology'. These keywords are matched against solicitation descriptions. The more precisely they mirror how agencies describe your domain, the better your fit scores."
**Common mistakes**: Too broad ("software development"), too few (only 2-3 keywords when the company has 10+ competencies), mixing business capabilities ("project management") with technical capabilities.

### certifications.sam_gov

**Scoring impact**: Certifications dimension (weight 0.15). `active: false` produces a certification score of 0.0, which triggers an automatic no-go recommendation regardless of composite score. This is a hard gate.
**What to collect**: Active registration status, CAGE code (5 alphanumeric characters), and UEI (Unique Entity Identifier).
**Interview guidance**: "SAM.gov active registration is REQUIRED for all federal contracts. Without it, every topic recommendation will be no-go. Is your SAM.gov registration active? If yes, provide your CAGE code (5 alphanumeric characters, found on your SAM.gov entity page) and your UEI."
**Validation**: CAGE code must be exactly 5 alphanumeric characters. UEI must be a non-empty string.

### certifications.sam_gov.cage_code

**Scoring impact**: Eligibility verification. Used to confirm identity in federal contracting systems.
**What to collect**: 5-character alphanumeric code assigned by DLA.
**Validation**: Exactly 5 characters, alphanumeric only (e.g., "1ABC2").

### certifications.sam_gov.uei

**Scoring impact**: Eligibility verification. The UEI replaced the DUNS number as the primary entity identifier.
**What to collect**: The Unique Entity Identifier from SAM.gov.
**Validation**: Non-empty string.

### certifications.socioeconomic

**Scoring impact**: Certifications dimension. Socioeconomic certifications enable matching against set-aside topics. An 8(a) company can bid on 8(a) set-aside SBIR topics that have reduced competition. HUBZone, WOSB, SDVOSB, and VOSB similarly open dedicated solicitation pools.
**What to collect**: Array of applicable certifications from the valid set.
**Interview guidance**: "Socioeconomic certifications open access to set-aside topics with less competition. Do you hold any of these: 8(a), HUBZone, WOSB (Women-Owned Small Business), SDVOSB (Service-Disabled Veteran-Owned), or VOSB (Veteran-Owned)? List all that apply, or 'none'."
**Valid values**: `8(a)`, `HUBZone`, `WOSB`, `SDVOSB`, `VOSB`. Empty array if none.

### certifications.security_clearance

**Scoring impact**: Certifications dimension. Classified topics require a specific clearance level. A company with no clearance scores 0.0 on classified topics. Higher clearance levels (secret, top_secret) enable more topic eligibility but do not boost scoring on unclassified topics.
**What to collect**: Facility clearance level.
**Interview guidance**: "What is your company's facility security clearance level? This determines eligibility for classified SBIR topics. Options: none, confidential, secret, or top_secret. Most small businesses start with 'none' -- that is fine for the majority of SBIR topics."
**Valid values**: `none`, `confidential`, `secret`, `top_secret`.

### certifications.itar_registered

**Scoring impact**: Certifications dimension. ITAR-controlled topics require registration with the Directorate of Defense Trade Controls (DDTC). Without registration, ITAR topics are ineligible.
**What to collect**: Boolean -- registered or not.
**Interview guidance**: "Are you registered with DDTC for ITAR compliance? This is required for topics involving controlled defense articles or technical data. Answer yes or no."

### employee_count

**Scoring impact**: Phase Eligibility dimension (weight 0.15). SBIR requires fewer than 500 employees. Companies near the threshold (400-499) receive a cautious 0.5 eligibility score rather than 1.0 because headcount changes could disqualify mid-proposal.
**What to collect**: Integer headcount.
**Interview guidance**: "How many employees does your company currently have? SBIR eligibility requires fewer than 500. This number is verified during award processing."
**Validation**: Must be a positive integer.

### key_personnel

**Scoring impact**: Subject Matter Expertise dimension (weight 0.35). Key personnel expertise keywords are combined with capabilities keywords for SME scoring. A topic mentioning "machine learning for radar" scores higher when both the capabilities list and a key person's expertise include those terms.
**What to collect**: Array of personnel objects with name, role, and expertise keywords.
**Interview guidance**: "List your key technical personnel who would appear on proposals. For each person, provide:
- Name
- Role (PI, Co-PI, Lead Engineer, Subject Matter Expert, etc.)
- Expertise keywords (same specificity guidance as capabilities)

Focus on people with domain expertise relevant to your target solicitation areas."
**Common mistakes**: Listing only leadership without technical expertise keywords. Omitting the PI/Co-PI who will be named on proposals.

### past_performance

**Scoring impact**: Past Performance dimension (weight 0.25). Agency-specific history is powerful: a WIN with the Air Force significantly boosts scoring for the next Air Force topic. Outcomes are weighted: WIN=1.0, ONGOING=0.7, LOSS=0.5 (losing still demonstrates agency experience), none=0.0.
**What to collect**: Array of performance records with agency, topic area, and outcome.
**Interview guidance**: "List your past SBIR/STTR awards and submissions. For each, provide:
- Agency (Air Force, Navy, DARPA, DoE, NASA, etc.)
- Topic area (brief technical description)
- Outcome: WIN, LOSS, or ONGOING

Include losses too -- they demonstrate agency experience and still contribute to scoring."
**Common mistakes**: Omitting losses (they have value). Listing only the most recent award. Using inconsistent agency names ("USAF" vs "Air Force").

### research_institution_partners

**Scoring impact**: STTR dimension (weight 0.10). For SBIR topics, this dimension scores 1.0 automatically (no partner needed). For STTR topics, having an established partner is critical -- STTR requires the research institution to perform at least 30% of Phase I work.
**What to collect**: Array of partner institutions with name and type.
**Interview guidance**: "Do you have partnerships with universities or research institutions? These are required for STTR proposals (the institution must perform at least 30% of Phase I work). For each partner, provide the institution name and type: university, federally funded R&D center, or nonprofit research organization. If none, say 'none' -- this only affects STTR topic scoring."
**Valid types**: `university`, `federally_funded_rdc`, `nonprofit_research`.

## Dimension-to-Field Mapping Summary

| Dimension | Weight | Primary Fields | Impact |
|-----------|--------|---------------|--------|
| Subject Matter Expertise | 0.35 | capabilities, key_personnel.expertise | Keyword match against solicitation |
| Past Performance | 0.25 | past_performance | Agency + domain match, outcome weighted |
| Certifications | 0.15 | sam_gov, socioeconomic, security_clearance, itar_registered | Eligibility gates and set-aside access |
| Phase Eligibility | 0.15 | employee_count | Hard gate at 500 employees |
| STTR Requirements | 0.10 | research_institution_partners | Required for STTR topics only |

## Validation Rules

The profile is validated by `pes.domain.profile_validation.validate_profile()` before saving. Key rules:

1. `company_name` must be a non-empty string
2. `employee_count` must be a positive integer
3. `capabilities` must be a non-empty array of strings
4. `certifications.sam_gov.active` must be boolean
5. `certifications.sam_gov.cage_code` must be 5 alphanumeric characters (when sam_gov.active is true)
6. `certifications.sam_gov.uei` must be non-empty string (when sam_gov.active is true)
7. `certifications.security_clearance` must be one of: none, confidential, secret, top_secret
8. `certifications.itar_registered` must be boolean
9. `key_personnel` entries must have name, role, and expertise array
10. `past_performance` entries must have agency, topic_area, and outcome (WIN/LOSS/ONGOING)
11. `research_institution_partners` entries must have name and valid type

## Document Extraction Guidance

### Extraction Strategy

When processing documents, extract fields that map to the profile schema. Not every document contains every field -- extractions are partial by design. The merge logic combines multiple partial extractions into a complete draft.

### Field Extraction by Document Type

**Capability Statements / Corporate Brochures**: company_name, capabilities (from technical competency descriptions), key_personnel (from team/leadership sections), past_performance (from contract/award history sections).

**SAM.gov Entity Pages / Registration Data**: company_name, certifications.sam_gov.active, certifications.sam_gov.cage_code, certifications.sam_gov.uei, certifications.socioeconomic (from socioeconomic indicators), employee_count (if listed).

**Research Partnership Documents**: research_institution_partners (names and types of partner institutions).

**Resumes / CV**: key_personnel entries (name, role inferred from title, expertise from skills/publications).

### Extraction Merge Rules

- Multiple documents are additive -- each new extraction merges into the existing draft
- Nested dicts (certifications) are deep-merged
- Lists (capabilities, key_personnel) are concatenated with deduplication
- Scalars (company_name, employee_count) from later documents overwrite earlier values
- The merge service is at `pes.domain.profile_merge` (assemble_draft, merge_extractions, check_completeness)

### Post-Extraction Verification

After extraction, always:
1. Display all extracted fields with their values for user verification
2. Run completeness check to identify missing sections
3. Present missing sections as a targeted list to drive interview for remaining gaps
4. Let the user confirm, correct, or reject extracted values before entering draft state

### Unsupported Formats

If the user provides a file in an unsupported format (.xlsx, .pptx, images, etc.), respond with:
"Unsupported file format. Supported: PDF (.pdf), text (.txt), Word (.doc/.docx), or URL. Try converting to PDF or pasting the text content directly."

## Overwrite Protection Protocol

Before any write operation:

1. Check `adapter.metadata()` for existing profile
2. If exists: present backup/update/cancel options
3. If "fresh": adapter creates .bak backup before overwriting
4. If "update": load existing profile, merge user changes, validate merged result
5. If "cancel": exit immediately, no file operations

The JsonProfileAdapter handles atomic writes (write to .tmp, rename to target). The agent must never write directly to the profile path.

## Empty and Default Values

When a user skips a section, use these defaults:
- `capabilities`: `[]` (empty array -- will produce SME score of 0.0)
- `key_personnel`: `[]` (empty array)
- `past_performance`: `[]` (empty array -- will produce PP score of 0.0)
- `research_institution_partners`: `[]` (empty array -- STTR score will be 0.0 for STTR topics)
- `certifications.socioeconomic`: `[]` (empty array)
- `certifications.security_clearance`: `"none"`
- `certifications.itar_registered`: `false`
- `certifications.sam_gov.active`: `false` (WARNING: triggers automatic no-go)

Always warn the user when a skipped field will produce a 0.0 score in a dimension. They should know the downstream impact.
