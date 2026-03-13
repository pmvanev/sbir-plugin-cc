# Company Profile Builder -- Data Models

## Company Profile Schema

Location: `~/.sbir/company-profile.json`
Schema source of truth: `templates/company-profile-schema.json`

### Profile Structure

```json
{
  "company_name": "Radiant Defense Systems, LLC",
  "capabilities": [
    "directed energy",
    "RF systems",
    "power electronics",
    "thermal management",
    "embedded firmware"
  ],
  "certifications": {
    "sam_gov": {
      "active": true,
      "cage_code": "7X2K9",
      "uei": "DKJF84NXLE73"
    },
    "socioeconomic": ["8(a)", "HUBZone"],
    "security_clearance": "secret",
    "itar_registered": true
  },
  "employee_count": 23,
  "key_personnel": [
    {
      "name": "Rafael Medina",
      "role": "CEO / Chief Engineer",
      "expertise": ["directed energy", "systems engineering"]
    }
  ],
  "past_performance": [
    {
      "agency": "Air Force",
      "topic_area": "Compact Directed Energy",
      "outcome": "awarded"
    }
  ],
  "research_institution_partners": [
    "Georgia Tech Research Institute"
  ]
}
```

### Field Definitions

| Field | Type | Required | Constraints | Fit Scoring Impact |
|-------|------|----------|-------------|-------------------|
| `company_name` | string | Yes | Non-empty | Display only |
| `capabilities` | string[] | Yes | >= 1 entry | SME dimension (weight 0.35) -- matched against solicitation keywords |
| `certifications` | object | Yes | See sub-fields | Cert dimension (weight 0.15) |
| `certifications.sam_gov` | object | Yes | See sub-fields | active=false -> cert score 0.0 -> automatic no-go |
| `certifications.sam_gov.active` | boolean | Yes | true/false | Disqualifying if false |
| `certifications.sam_gov.cage_code` | string | Conditional | 5 alphanumeric chars; required if active=true | Eligibility verification |
| `certifications.sam_gov.uei` | string | Conditional | Non-empty; required if active=true | Eligibility verification |
| `certifications.socioeconomic` | string[] | Yes | Each from: "8(a)", "HUBZone", "WOSB", "SDVOSB", "VOSB"; empty array valid | Set-aside topic matching |
| `certifications.security_clearance` | string | Yes | Enum: "none", "confidential", "secret", "top_secret" | Classified topic eligibility |
| `certifications.itar_registered` | boolean | Yes | true/false | ITAR topic eligibility |
| `employee_count` | integer | Yes | > 0 | Phase eligibility (< 500 for SBIR) |
| `key_personnel` | object[] | Yes | >= 0 entries | SME dimension (expertise keywords) |
| `key_personnel[].name` | string | Yes | Non-empty | Display only |
| `key_personnel[].role` | string | Yes | Non-empty | Display only |
| `key_personnel[].expertise` | string[] | Yes | >= 1 entry | Matched against solicitation keywords |
| `past_performance` | object[] | Yes | >= 0 entries | PP dimension (weight 0.25) |
| `past_performance[].agency` | string | Yes | Non-empty | Agency-specific scoring |
| `past_performance[].topic_area` | string | Yes | Non-empty | Domain matching |
| `past_performance[].outcome` | string | Yes | Non-empty (e.g., "awarded", "submitted", "completed") | Win/loss weighting |
| `research_institution_partners` | string[] | Yes | >= 0 entries | STTR dimension (weight 0.10) |

### Validation Rules

**Structural (JSON Schema enforced):**
- All required fields present
- Correct types (string, boolean, integer, array, object)
- Nested object structure matches schema

**Business rules (custom validation):**
- `cage_code`: exactly 5 alphanumeric characters (when `sam_gov.active` = true)
- `uei`: non-empty string (when `sam_gov.active` = true)
- `security_clearance`: one of ["none", "confidential", "secret", "top_secret"]
- `socioeconomic` entries: each from ["8(a)", "HUBZone", "WOSB", "SDVOSB", "VOSB"]
- `employee_count`: positive integer (> 0)
- `capabilities`: at least one entry

---

## Validation Result Model

Returned by the profile validation service.

```
ProfileValidationResult:
  valid: boolean
  errors: list of ProfileFieldError

ProfileFieldError:
  field: string (dot-notation path, e.g., "certifications.sam_gov.cage_code")
  value: any (the actual value found)
  expected: string (human-readable description of valid format)
  message: string (e.g., "CAGE code '7X2K' is 4 characters (expected 5 alphanumeric)")
```

---

## Profile Metadata Model

Used by overwrite protection (US-CPB-005).

```
ProfileMetadata:
  exists: boolean
  company_name: string | null (from existing profile)
  last_modified: datetime | null (file system metadata)
  file_path: string
```

---

## File System Artifacts

| Artifact | Path | Lifecycle |
|----------|------|-----------|
| Company profile | `~/.sbir/company-profile.json` | Created on first setup, updated on subsequent runs |
| Backup | `~/.sbir/company-profile.json.bak` | Created before each write (overwritten each time) |
| Temp file | `~/.sbir/company-profile.json.tmp` | Exists only during atomic write, then renamed |
| Schema template | `templates/company-profile-schema.json` | Shipped with plugin, read-only |

---

## Schema Evolution Strategy

The profile schema may need new fields in future (e.g., facility descriptions, NAICS codes, revenue range). Forward compatibility strategy:

- Validation preserves unknown top-level fields during update (US-CPB-004) -- read existing profile, modify selected section, write back without stripping unrecognized fields
- Schema template version tracked via `$schema` property or `schema_version` field if needed
- New required fields added as optional first, then promoted to required in a subsequent release with migration guidance
