# Shared Artifacts Registry: Company Profile Enrichment

## Artifacts

### sam_gov_api_key

- **Source of truth**: `~/.sbir/api-keys.json` (field: `sam_gov_api_key`)
- **Consumers**: Step 1 (key check/display), Step 3 (Python enrichment service passes to SAM.gov API), re-enrichment during profile update
- **Owner**: profile-builder agent (writes), enrichment service (reads)
- **Integration risk**: HIGH -- if the key file is missing, corrupted, or has wrong permissions, SAM.gov enrichment fails silently. Key must never appear in logs, command-line arguments, or conversation history beyond the masked last-4-characters display.
- **Validation**: File exists, is valid JSON, contains `sam_gov_api_key` field, key is non-empty string. Validated via test API call returning HTTP 200.

### uei_input

- **Source of truth**: User input during enrichment flow
- **Consumers**: Step 2 (display and validation), Step 3 (SAM.gov query parameter `ueiSAM`), Step 3 (SBIR.gov query filter after name resolution), Step 3 (USASpending query), profile draft `certifications.sam_gov.uei`
- **Owner**: profile-builder agent
- **Integration risk**: HIGH -- UEI is the primary lookup key for all three APIs. A wrong UEI returns data for the wrong entity. Must be validated as 12 alphanumeric characters before any API call.
- **Validation**: Length is 12, all characters alphanumeric. Same value used in all API calls and stored in profile.

### enrichment_result

- **Source of truth**: Python enrichment service JSON output (structured dict)
- **Consumers**: Step 3 (results display), Step 4 (field-by-field review), Step 5 (merge into profile draft)
- **Owner**: Python enrichment service (produces), profile-builder agent (consumes)
- **Integration risk**: HIGH -- this is the primary data transfer artifact between the Python adapter and the agent. Field names must map to `company-profile-schema.json` paths. If the mapping is wrong, enrichment data lands in the wrong profile fields.
- **Validation**: JSON structure matches expected schema mapping. Each field has `value`, `source`, and `confidence` attributes. Field names correspond to profile schema paths.

### source_attribution

- **Source of truth**: Enrichment service tags each field with `{api_name}` at retrieval time
- **Consumers**: Step 4 (displayed next to each field during review), Step 5 (preserved in profile draft metadata), profile `sources.web_references` array, preview display
- **Owner**: enrichment service (produces), profile-builder agent (displays and persists)
- **Integration risk**: MEDIUM -- if source labels are wrong or missing, user cannot verify data provenance. Critical for trust but does not affect data correctness.
- **Validation**: Every enriched field has a non-empty source string. Source is one of: "SAM.gov", "SBIR.gov", "USASpending.gov", or "user (overriding {api_name})".

### missing_fields_list

- **Source of truth**: Computed by enrichment service (schema required fields minus API-populated fields)
- **Consumers**: Step 3 (not-found display), Step 5 (drives interview targeting), existing profile builder Step 3 (INTERVIEW only asks about these fields)
- **Owner**: enrichment service (computes), profile-builder agent (uses to filter interview questions)
- **Integration risk**: HIGH -- if a field is incorrectly marked as "populated" when it was not, the interview skips it and the profile has a gap. If marked as "missing" when it was populated, the user is asked redundantly.
- **Validation**: Union of missing_fields_list and enriched fields must equal the complete set of schema required fields. No field appears in both lists.

### confirmed_enrichment

- **Source of truth**: User confirmation decisions during Step 4 review
- **Consumers**: Step 5 (merge logic), profile draft, profile `sources` metadata
- **Owner**: profile-builder agent
- **Integration risk**: MEDIUM -- if a field the user rejected is still merged, enrichment overwrites user intent. If a field the user confirmed is not merged, enrichment data is lost.
- **Validation**: Every enriched field has exactly one status: confirmed, edited, or skipped. Confirmed fields appear in profile draft. Skipped fields appear in missing_fields_list. Edited fields use user's value.

### profile_draft (extended)

- **Source of truth**: In-memory draft maintained by profile-builder agent (now includes enrichment data)
- **Consumers**: Existing Step 3 INTERVIEW (reads populated fields to skip questions), existing Step 4 PREVIEW (displays complete draft), existing Step 5 SAVE (writes to disk)
- **Owner**: profile-builder agent
- **Integration risk**: HIGH -- this is the central integration point between enrichment and the existing profile builder flow. The draft must be in the exact format the existing INTERVIEW, PREVIEW, and SAVE steps expect.
- **Validation**: Draft contains all schema-required fields (some populated from enrichment, some pending). Format matches what existing journey steps consume. Enrichment metadata (sources) stored alongside but does not interfere with schema validation.

### api_keys_file_path

- **Source of truth**: Hardcoded default `~/.sbir/api-keys.json`
- **Consumers**: Step 1 (key check), Python enrichment service (reads key), API key save operation
- **Owner**: profile-builder agent
- **Integration risk**: MEDIUM -- separate from `company-profile.json` for security hygiene. If the path is inconsistent between the agent and the Python service, the service cannot find the key.
- **Validation**: Path used by agent and Python service is identical. File permissions are owner-only (600 on Unix).

---

## Integration Checkpoints

### Checkpoint 1: API Key Availability (Step 1)
- `~/.sbir/api-keys.json` exists with `sam_gov_api_key` field
- Key validated with test call to SAM.gov (HTTP 200)
- If key not found or invalid: user can provide key or skip enrichment
- SBIR.gov and USASpending.gov require no key (always available)

### Checkpoint 2: UEI Validation (Step 2)
- UEI is 12 alphanumeric characters
- Same UEI value passed to all three API calls
- UEI stored in enrichment result for later persistence in profile

### Checkpoint 3: Enrichment Result Completeness (Step 3)
- Enrichment result is valid JSON with expected structure
- Each populated field has value, source, and confidence
- Missing fields list computed correctly (schema fields minus populated fields)
- Partial results acceptable (some APIs may fail)

### Checkpoint 4: User Confirmation Completeness (Step 4)
- Every enriched field has a user decision (confirmed/edited/skipped)
- No enriched field enters the profile without explicit user approval
- Edited values override API values with updated source attribution

### Checkpoint 5: Draft Integration with Existing Flow (Step 5)
- Profile draft after enrichment merge is compatible with existing INTERVIEW step
- INTERVIEW step receives correct missing_fields_list (no duplicates, no omissions)
- PREVIEW step displays enrichment-sourced fields with source labels
- SAVE step writes the complete profile including enrichment metadata in sources section

### Checkpoint 6: Cross-Feature Compatibility
- Enrichment adds `naics_codes` to profile data -- verify `sbir-topic-scout` can consume this field or it is informational only
- `sources.web_references` array extended with API URLs used during enrichment
- Existing profile builder US-CPB-001 through US-CPB-005 behavior unchanged when enrichment is skipped
- US-CPB-004 (Selective Update) supports re-enrichment as an update mode

### Checkpoint 7: Security
- SAM.gov API key never appears in command-line arguments, logs, or full conversation display
- `~/.sbir/api-keys.json` has restrictive file permissions
- API key is separate from company profile (different file)
- UEI is sensitive but not secret -- displayed in enrichment flow and stored in profile
