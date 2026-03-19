---
description: "Create or update a research institution partner profile for SBIR/STTR proposals"
argument-hint: "- Optional: partner name (e.g., 'CU Boulder')"
---

# /proposal partner-setup

Create a new partner profile or update an existing one through guided interview or document extraction.

## Usage

```
/proposal partner-setup
/proposal partner-setup "CU Boulder"
```

## Flow

1. **Mode selection** -- Choose input mode: documents, interview, or both
2. **Web research** -- Search for partner institution data to pre-populate draft
3. **Gather data** -- Collect partner basics, capabilities, key personnel, facilities, past collaborations, and STTR eligibility
4. **Preview** -- Display partner profile with combined capability analysis (company + partner)
5. **Validate** -- Run schema validation; failures show field name, current value, and expected format
6. **Save** -- Requires explicit user confirmation; writes atomically to ~/.sbir/partners/{slug}.json

## Preview Format

The preview includes a combined capability analysis showing how the partner extends your company's capability footprint:

```
Partner: University of Colorado Boulder
Type: university
Capabilities: autonomous navigation, underwater acoustics, sensor fusion
Key Personnel: 2 entries
Facilities: 1 entry
Past Collaborations: 1 entry
STTR Eligible: yes (minimum effort capable)

COMBINED CAPABILITIES
---------------------
Company only:    directed energy, RF engineering
Partner only:    autonomous navigation, underwater acoustics, sensor fusion
Overlap:         machine learning
Combined total:  6 unique capabilities
```

## Prerequisites

- Company profile at ~/.sbir/company-profile.json (for combined capability analysis)
- If partner name provided, checks for existing profile at ~/.sbir/partners/{slug}.json

## Agent Invocation

@sbir-partner-builder

Create or update a partner profile. Start with mode selection, research the partner institution, gather all profile sections with downstream impact explanations, preview with combined capability analysis, validate against schema, and save only after explicit user confirmation.
