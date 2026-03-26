# Component Boundaries: Company Profile Enrichment

## Boundary Map

```
scripts/pes/
  ports/
    enrichment_port.py      -- EnrichmentSourcePort (driven port)
    api_key_port.py         -- ApiKeyPort (driven port)
  domain/
    enrichment.py           -- Value objects, UEI validation, field mapping
    profile_diff.py         -- Diff logic for re-enrichment
    enrichment_service.py   -- Application service: cascade orchestration
  adapters/
    sam_gov_adapter.py      -- SAM.gov Entity API v3
    sbir_gov_adapter.py     -- SBIR.gov Company + Awards API
    usa_spending_adapter.py -- USASpending.gov autocomplete + recipient
    json_api_key_adapter.py -- ~/.sbir/api-keys.json read/write
  enrichment_cli.py         -- CLI entry point (at scripts/pes/ level)

agents/
  sbir-profile-builder.md   -- MODIFIED: new ENRICHMENT phase

skills/
  profile-builder/
    enrichment-domain.md    -- NEW: enrichment flow knowledge

templates/
  company-profile-schema.json -- MODIFIED: naics_codes, registration_expiration
```

## Dependency Direction

```
                    INWARD
                      |
    adapters/ ------> ports/ <------ domain/
    (infra)          (interfaces)    (pure logic)
                      |
                      v
              enrichment_cli.py
              (composition root)
```

- **Domain** imports nothing from adapters or ports (pure Python, no I/O)
- **Ports** define abstract interfaces (ABC classes)
- **Adapters** implement ports, import from ports and domain
- **CLI** is the composition root: wires adapters to service, calls service, outputs JSON
- **Agent** is external: invokes CLI via Bash tool, receives JSON output

## Port Interfaces

### EnrichmentSourcePort (Driven Port)

Responsibility: Fetch company data from a single external API source.

Contract:
- Input: company identifier (UEI or company name depending on source)
- Output: list of EnrichedField value objects, each with value + source attribution
- Failure: returns empty list with error indicator (not exceptions)

Implementations:
- `SamGovAdapter` -- calls SAM.gov Entity API v3
- `SbirGovAdapter` -- calls SBIR.gov Company + Awards APIs
- `UsaSpendingAdapter` -- calls USASpending.gov autocomplete + recipient detail

### ApiKeyPort (Driven Port)

Responsibility: Manage API key persistence and validation.

Contract:
- `read_key(service_name) -> str | None` -- read stored key
- `write_key(service_name, key) -> None` -- save key with restricted permissions
- `validate_sam_key(key) -> bool` -- test key with SAM.gov API

Implementation:
- `JsonApiKeyAdapter` -- reads/writes `~/.sbir/api-keys.json`

### Reused Ports (No Changes)

- `ProfilePort` + `JsonProfileAdapter` -- profile read/write (existing)
- Profile validation via `ProfileValidationService` -- schema validation (existing)

## Domain Value Objects

### EnrichedField
- `field_path`: str -- maps to company-profile-schema.json path (e.g., "certifications.sam_gov.cage_code")
- `value`: Any -- the enriched value
- `source`: FieldSource -- which API provided this value
- `confidence`: str -- "high" (exact match), "medium" (fuzzy match), "low" (corroboration only)

### FieldSource
- `api_name`: str -- "SAM.gov", "SBIR.gov", "USASpending.gov"
- `api_url`: str -- exact URL queried
- `accessed_at`: str -- ISO-8601 timestamp

### EnrichmentResult
- `uei`: str -- the UEI used for enrichment
- `fields`: list[EnrichedField] -- all enriched fields
- `missing_fields`: list[str] -- schema fields not populated by any API
- `sources_attempted`: list[str] -- which APIs were called
- `sources_succeeded`: list[str] -- which APIs returned data
- `disambiguation_needed`: list[dict] -- SBIR.gov candidates if multiple matches
- `errors`: list[dict] -- per-source error details

### ProfileDiff (for re-enrichment)
- `additions`: list[DiffEntry] -- fields in API but not in profile
- `changes`: list[DiffEntry] -- fields that differ between API and profile
- `matches`: list[str] -- fields that are identical
- `api_missing`: list[str] -- fields in profile but not available from APIs (user-entered)

### DiffEntry
- `field_path`: str
- `current_value`: Any
- `api_value`: Any
- `source`: FieldSource

## Service Responsibilities

### CompanyEnrichmentService

Owns: cascade orchestration, result merging, missing field computation.

Does NOT own:
- HTTP calls (delegated to adapters via port)
- Field-by-field user confirmation (agent responsibility)
- Profile persistence (agent uses existing ProfilePort)
- Diff display format (agent responsibility)

### Cascade Order

1. SAM.gov (primary) -- provides company name for steps 2-3
2. SBIR.gov (augments) -- uses company name from step 1
3. USASpending (augments) -- uses company name from step 1

If SAM.gov fails, steps 2-3 cannot proceed. Service marks all fields as unavailable.

## Agent Integration Points

The agent (sbir-profile-builder.md) interacts with enrichment exclusively through CLI invocations:

| Agent Action | CLI Command | Response |
|-------------|-------------|----------|
| Check for API key | `python enrichment_cli.py --mode validate-key` | `{valid: bool}` |
| Save API key | `echo KEY \| python enrichment_cli.py --mode save-key` | `{saved: bool}` |
| Run enrichment | `python enrichment_cli.py --mode enrich --uei UEI` | EnrichmentResult JSON |
| Run diff (re-enrichment) | `python enrichment_cli.py --mode diff --uei UEI --profile-path PATH` | ProfileDiff JSON |

The agent parses JSON responses and drives the conversational review flow. The Python side has no knowledge of the agent or conversation state.
