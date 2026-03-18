---
description: "Create a new company profile for SBIR/STTR fit scoring via guided interview"
argument-hint: "- No arguments required"
---

# /proposal profile setup

Create a new company profile through a guided interview or document extraction.

## Usage

```
/proposal profile setup
```

## Flow

1. **Mode selection** -- Choose input mode: documents, interview, or both
2. **Gather data** -- Collect company basics, capabilities, key personnel, certifications, past performance, and research partners
3. **Preview** -- Display every profile field in human-readable format for review
4. **Validate** -- Run schema validation; failures show field name, current value, and expected format
5. **Save** -- Requires explicit user confirmation after validation passes; writes atomically via profile adapter

## Preview Format

The preview displays all profile fields in readable format:

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

- No existing profile at ~/.sbir/company-profile.json (if one exists, use `/proposal profile update` instead)

## Implementation

This command invokes the profile builder agent which orchestrates:
- `JsonProfileAdapter.metadata()` to check for existing profiles
- `validate_profile()` for schema validation before save
- `JsonProfileAdapter.write()` for atomic file writes with backup

## Agent Invocation

@sbir-profile-builder

Create a new company profile. Start with mode selection (documents, interview, or both), gather all profile sections with fit scoring explanations, preview the complete profile in human-readable format, validate against schema, and save only after explicit user confirmation.
