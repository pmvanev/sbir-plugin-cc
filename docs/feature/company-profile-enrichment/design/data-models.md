# Data Models: Company Profile Enrichment

## Enrichment Domain Types

### EnrichedField

Represents a single profile field populated from an external API.

| Attribute | Type | Description |
|-----------|------|-------------|
| field_path | str | Profile schema path, e.g., `"certifications.sam_gov.cage_code"` |
| value | Any | The enriched value (str, list, dict, bool) |
| source | FieldSource | Which API provided this value |
| confidence | str | `"high"` (exact match), `"medium"` (inferred), `"low"` (corroboration) |

### FieldSource

Provenance for a single enriched field.

| Attribute | Type | Description |
|-----------|------|-------------|
| api_name | str | `"SAM.gov"`, `"SBIR.gov"`, or `"USASpending.gov"` |
| api_url | str | Exact URL queried |
| accessed_at | str | ISO-8601 timestamp of the API call |

### EnrichmentResult

Complete output of the three-API enrichment cascade.

| Attribute | Type | Description |
|-----------|------|-------------|
| uei | str | UEI used for enrichment |
| fields | list[EnrichedField] | All enriched fields from all sources |
| missing_fields | list[str] | Schema required fields not populated by any API |
| sources_attempted | list[str] | API names that were called |
| sources_succeeded | list[str] | API names that returned data |
| disambiguation_needed | list[CompanyCandidate] | SBIR.gov matches when multiple found |
| errors | list[SourceError] | Per-source error details |

### CompanyCandidate

Returned when SBIR.gov finds multiple company matches.

| Attribute | Type | Description |
|-----------|------|-------------|
| company_name | str | Company name from SBIR.gov |
| city | str | City |
| state | str | State |
| award_count | int | Number of SBIR awards |
| firm_id | str | SBIR.gov firm identifier for subsequent award query |

### SourceError

Per-API error information.

| Attribute | Type | Description |
|-----------|------|-------------|
| api_name | str | Which API failed |
| error_type | str | `"timeout"`, `"auth_failed"`, `"not_found"`, `"server_error"` |
| message | str | Human-readable error description |
| http_status | int or None | HTTP status code if available |

### ProfileDiff

Result of comparing enrichment data against an existing profile.

| Attribute | Type | Description |
|-----------|------|-------------|
| additions | list[DiffEntry] | Fields in API data but not in current profile |
| changes | list[DiffEntry] | Fields that differ between API and profile |
| matches | list[str] | Field paths that are identical |
| api_missing | list[str] | Field paths in profile but not available from APIs |

### DiffEntry

A single difference between enrichment and existing profile.

| Attribute | Type | Description |
|-----------|------|-------------|
| field_path | str | Profile schema path |
| current_value | Any | Value currently in the profile |
| api_value | Any | Value from the API |
| source | FieldSource | Which API provided the new value |

---

## SAM.gov Entity API Response Mapping

| SAM.gov JSON Path | Profile Schema Path | Notes |
|-------------------|---------------------|-------|
| `entityRegistration.legalBusinessName` | `company_name` | Direct mapping |
| `entityRegistration.cageCode` | `certifications.sam_gov.cage_code` | Direct mapping |
| `entityRegistration.ueiSAM` | `certifications.sam_gov.uei` | Direct mapping |
| `entityRegistration.registrationStatus` | `certifications.sam_gov.active` | Map "Active" -> true |
| `entityRegistration.registrationExpirationDate` | `certifications.sam_gov.registration_expiration` | New schema field |
| `entityRegistration.entityStructure` | `certifications.sam_gov.entity_structure` | New schema field |
| `assertions.goodsAndServices.naicsCode` | `naics_codes[0]` (primary) | New schema field |
| `entityRegistration.naicsCode` (all listed) | `naics_codes[1..n]` | New schema field |
| `assertions.goodsAndServices.businessTypeCode` contains `A8` | `certifications.socioeconomic` includes "8(a)" | Code-to-name mapping |
| `assertions.goodsAndServices.businessTypeCode` contains `QF` | `certifications.socioeconomic` includes "HUBZone" | Code-to-name mapping |
| `assertions.goodsAndServices.businessTypeCode` contains `A5` | `certifications.socioeconomic` includes "WOSB" | Code-to-name mapping |
| `assertions.goodsAndServices.businessTypeCode` contains `QE` | `certifications.socioeconomic` includes "SDVOSB" | Code-to-name mapping |
| `assertions.goodsAndServices.businessTypeCode` contains `A9` | `certifications.socioeconomic` includes "VOSB" | Code-to-name mapping |

**Note**: Exact SAM.gov JSON paths should be validated with a test API call during implementation. The OpenAPI spec at open.gsa.gov/api/entity-api/ is the authoritative reference. The mapping table above is based on documentation analysis and may need adjustment.

### Business Type Code Mapping

| SAM.gov Code | Socioeconomic Certification | Profile Value |
|-------------|----------------------------|---------------|
| A8 | 8(a) Business Development | `"8(a)"` |
| QF | HUBZone | `"HUBZone"` |
| A5 | Woman-Owned Small Business | `"WOSB"` |
| QE | Service-Disabled Veteran-Owned | `"SDVOSB"` |
| A9 | Veteran-Owned Small Business | `"VOSB"` |
| 27 | Self-Certified Small Disadvantaged Business | `"SDB"` |
| LJ | EDWOSB | `"EDWOSB"` |

---

## SBIR.gov API Response Mapping

### Company API Response

| SBIR.gov Field | Usage |
|---------------|-------|
| `company_name` | Verification against SAM.gov legal name |
| `uei` | Cross-check against input UEI |
| `hubzone_owned` | Corroborates SAM.gov HUBZone certification |
| `woman_owned` | Corroborates SAM.gov WOSB certification |
| `socially_economically_disadvantaged` | Corroborates SAM.gov SDB/8(a) |
| `number_awards` | Total SBIR/STTR award count |

### Awards API Response

| SBIR.gov Field | Profile Schema Path | Notes |
|---------------|---------------------|-------|
| `agency` | `past_performance[n].agency` | Direct mapping |
| `award_title` or `topic_area` | `past_performance[n].topic_area` | Use title as topic area |
| `phase` | `past_performance[n].outcome` | Map phase to outcome string |
| `award_amount` | Informational | Not stored in profile, displayed for context |
| `abstract` | Informational | Not stored in profile, displayed for context |

---

## USASpending.gov API Response Mapping

### Autocomplete Response

| USASpending Field | Usage |
|------------------|-------|
| `results[n].recipient_id` | Used to fetch full recipient detail |
| `results[n].name` | Verification against SAM.gov legal name |

### Recipient Detail Response

| USASpending Field | Usage | Notes |
|------------------|-------|-------|
| `total_transaction_amount` | Displayed as "total federal awards" | Informational, not stored in profile |
| `total_transactions` | Displayed as transaction count | Informational, not stored in profile |
| `business_types` | Cross-check against SAM.gov certifications | Corroboration only |
| `name` | Verification | Should match SAM.gov legal name |
| `uei` | Cross-check | Should match input UEI |

---

## Profile Schema Extensions

### naics_codes (NEW top-level field)

```json
"naics_codes": {
  "type": "array",
  "description": "NAICS codes from SAM.gov registration",
  "items": {
    "type": "object",
    "required": ["code"],
    "properties": {
      "code": { "type": "string", "pattern": "^[0-9]{2,6}$" },
      "primary": { "type": "boolean", "default": false },
      "description": { "type": "string" }
    }
  }
}
```

Not added to `required` array -- backward compatible. Existing profiles without NAICS codes remain valid.

### certifications.sam_gov extensions (NEW optional fields)

```json
"registration_expiration": {
  "type": "string",
  "format": "date",
  "description": "SAM.gov registration expiration date (YYYY-MM-DD)"
},
"entity_structure": {
  "type": "string",
  "description": "Legal entity structure from SAM.gov (e.g., LLC, Corporation)"
}
```

### sources.enrichment_metadata (NEW optional object)

```json
"enrichment_metadata": {
  "type": "object",
  "description": "Metadata about the most recent API enrichment",
  "properties": {
    "enriched_at": { "type": "string", "format": "date-time" },
    "uei_used": { "type": "string" },
    "sources_attempted": { "type": "array", "items": { "type": "string" } },
    "sources_succeeded": { "type": "array", "items": { "type": "string" } },
    "fields_enriched": { "type": "integer" },
    "fields_confirmed_by_user": { "type": "integer" }
  }
}
```

### sources.web_references extension

Enrichment API URLs added to the existing `web_references` array with an additional optional field:

```json
{
  "url": "https://api.sam.gov/entity-information/v3/entities?ueiSAM=DKJF84NXLE73",
  "label": "SAM.gov Entity API - enrichment",
  "accessed_at": "2026-03-26T14:00:00Z",
  "fields_populated": ["company_name", "certifications.sam_gov.cage_code", "naics_codes"]
}
```

The `fields_populated` property is optional and does not break existing schema consumers.
