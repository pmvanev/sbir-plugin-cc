# Enrichment Domain Skill

Domain knowledge for the profile builder's ENRICHMENT phase. Covers CLI invocation, output parsing, source attribution display, and error handling.

## CLI Interface

The enrichment subsystem is invoked via `scripts/pes/enrichment_cli.py`. All output is JSON to stdout. Set `PYTHONPATH=scripts` before invocation.

### validate-key

Check if an API key is stored for a service.

```bash
PYTHONPATH=scripts python scripts/pes/enrichment_cli.py validate-key --service sam_gov
```

Response:
```json
{"valid": true, "service": "sam_gov"}
```

### enrich

Run the three-API cascade (SAM.gov, SBIR.gov, USASpending.gov) for a UEI.

```bash
PYTHONPATH=scripts python scripts/pes/enrichment_cli.py enrich --uei DKJF84NXLE73
```

Response:
```json
{
  "uei": "DKJF84NXLE73",
  "fields": [
    {
      "field_path": "company_name",
      "value": "Acme Defense Corp",
      "source": {
        "api_name": "SAM.gov",
        "api_url": "https://api.sam.gov/entity-information/v3/entities?ueiSAM=DKJF84NXLE73",
        "accessed_at": "2026-03-26T14:00:00Z"
      },
      "confidence": "high"
    }
  ],
  "missing_fields": ["key_personnel", "capabilities"],
  "sources_attempted": ["SAM.gov", "SBIR.gov", "USASpending.gov"],
  "sources_succeeded": ["SAM.gov", "SBIR.gov"],
  "errors": []
}
```

### diff

Compare enrichment results against an existing profile.

```bash
PYTHONPATH=scripts python scripts/pes/enrichment_cli.py diff --uei DKJF84NXLE73 --profile-path ~/.sbir/company-profile.json
```

Response:
```json
{
  "has_changes": true,
  "additions": [{"field_path": "naics_codes", "new_value": [...], "old_value": null, "source": "SAM.gov"}],
  "changes": [{"field_path": "certifications.sam_gov.cage_code", "new_value": "2DEF3", "old_value": "1ABC2", "source": "SAM.gov"}],
  "matches": [{"field_path": "company_name", "new_value": "Acme", "old_value": "Acme", "source": "SAM.gov"}],
  "api_missing": [{"field_path": "capabilities", "new_value": null, "old_value": ["directed energy"], "source": null}]
}
```

### save-key

Save an API key (reads from stdin).

```bash
echo "your-api-key" | PYTHONPATH=scripts python scripts/pes/enrichment_cli.py save-key --service sam_gov
```

## Source Attribution Display

Every enriched field MUST show its source API in brackets when displayed to the user. This is a core trust principle -- users need to know where data comes from before confirming it.

Format: `{Field Label}: {value}  [{source API}]`

Examples:
- `Legal Name: Acme Defense Corp  [SAM.gov]`
- `Past Performance: 3 awards  [SBIR.gov]`
- `Federal Awards: $2.4M total  [USASpending.gov]`

For diff display, show old and new values:
- `CAGE Code: 1ABC2 -> 2DEF3  [SAM.gov]`

## Field Path Mapping

The CLI returns `field_path` values that map to profile schema locations:

| field_path | Display Label | Source API |
|-----------|--------------|------------|
| `company_name` | Legal Name | SAM.gov |
| `certifications.sam_gov.cage_code` | CAGE Code | SAM.gov |
| `certifications.sam_gov.uei` | UEI | SAM.gov |
| `certifications.sam_gov.active` | SAM.gov Active | SAM.gov |
| `certifications.sam_gov.registration_expiration` | Reg. Expiration | SAM.gov |
| `naics_codes` | NAICS Codes | SAM.gov |
| `certifications.socioeconomic` | Socioeconomic | SAM.gov |
| `past_performance` | Past Performance | SBIR.gov |
| `federal_awards.total_amount` | Federal Awards | USASpending.gov |

## Error Handling

### API Key Missing

If `validate-key` returns `{"valid": false}`, skip enrichment silently. Do not prompt the user to set up an API key during the profile build flow -- key setup is handled by the `/sbir:setup` command.

### UEI Validation Error

If the CLI returns a validation error for the UEI:
```json
{"error": true, "message": "UEI must be exactly 12 alphanumeric characters", "type": "validation_error"}
```

Ask the user to correct the UEI. UEIs are 12 uppercase alphanumeric characters (e.g., `DKJF84NXLE73`). Offer to skip enrichment if the user does not have a UEI.

### API Errors

If the CLI returns with errors for specific APIs:
```json
{"errors": [{"api_name": "SBIR.gov", "error_type": "timeout", "message": "Request timed out after 30s", "http_status": null}]}
```

Display which APIs succeeded and which failed. The user can still confirm fields from successful APIs. Failed API data simply remains unpopulated -- the RESEARCH and GATHER phases will fill gaps.

### Runtime Errors

If the CLI exits with code 1 and a runtime error, display the error message and offer to skip enrichment. Never block the profile build flow due to enrichment failures.

## Enrichment Metadata

After enrichment is complete and the user has confirmed fields, record enrichment metadata in the profile:

```json
{
  "enrichment_metadata": {
    "enriched_at": "2026-03-26T14:00:00Z",
    "uei_used": "DKJF84NXLE73",
    "sources_attempted": ["SAM.gov", "SBIR.gov", "USASpending.gov"],
    "sources_succeeded": ["SAM.gov", "SBIR.gov"],
    "fields_enriched": 8,
    "fields_confirmed_by_user": 6
  }
}
```

This metadata is stored at the profile top level and tracks what was enriched, when, and how many fields the user actually accepted.

## Confidence Levels

The CLI assigns confidence levels to enriched fields:

- **high**: Exact match from authoritative API (e.g., CAGE code from SAM.gov entity record)
- **medium**: Inferred or derived value (e.g., socioeconomic status mapped from business type codes)
- **low**: Corroboration from secondary source (e.g., USASpending.gov confirming SAM.gov data)

Display confidence only when "review" mode is selected (per-field confirmation). For "accept all" mode, confidence is not shown to avoid information overload.
