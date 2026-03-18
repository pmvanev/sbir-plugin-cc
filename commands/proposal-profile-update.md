---
description: "Update an existing company profile for SBIR/STTR fit scoring"
argument-hint: "- No arguments required"
---

# /proposal profile update

Update an existing company profile by modifying specific sections.

## Usage

```
/proposal profile update
```

## Flow

1. **Load existing** -- Read current profile from ~/.sbir/company-profile.json
2. **Select sections** -- Choose which sections to update (capabilities, personnel, certifications, past performance, or research partners)
3. **Gather updates** -- Collect new data for selected sections with fit scoring context
4. **Preview** -- Display the merged profile with all fields in human-readable format
5. **Validate** -- Run schema validation; failures show field name, current value, and expected format
6. **Save** -- Requires explicit user confirmation after validation passes; writes atomically with backup of previous version

## Preview Format

The preview displays all profile fields in readable format, highlighting updated sections:

```
Company: Acme Defense Inc.
Employees: 45
Capabilities: directed energy, RF engineering, machine learning
Key Personnel: 3 entries
SAM.gov: active (CAGE: 1AB2C, UEI: J7K8L9M0N1P2Q)
Socioeconomic: 8(a), HUBZone
Security Clearance: SECRET
ITAR: registered
Past Performance: 4 entries
Research Partners: MIT Lincoln Laboratory
```

## Validation Error Format

When validation fails, each error shows the field, current value, and expected format:

```
- employee_count: expected integer, got string "five hundred"
- cage_code: expected 5 alphanumeric characters, got "1AB"
```

## Prerequisites

- Existing profile at ~/.sbir/company-profile.json (if none exists, use `/proposal profile setup` first)

## Implementation

This command invokes the profile builder agent which orchestrates:
- `JsonProfileAdapter.metadata()` to load existing profile
- `validate_profile()` for schema validation before save
- `JsonProfileAdapter.write()` for atomic file writes with backup of previous version

## Agent Invocation

@sbir-profile-builder

Update the existing company profile. Load the current profile, present overwrite protection options (fresh start with backup, update specific sections, or cancel), gather updates for selected sections, preview the merged profile in human-readable format, validate against schema, and save only after explicit user confirmation.
