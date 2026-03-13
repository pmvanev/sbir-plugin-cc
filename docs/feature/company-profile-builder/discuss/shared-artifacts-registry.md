# Shared Artifacts Registry: Company Profile Builder

## Artifacts

### profile_path

- **Source of truth**: Hardcoded default `~/.sbir/company-profile.json`; overridable with `--output` flag
- **Consumers**: Step 1 (setup display), Step 5 (save confirmation), error messages, sbir-topic-scout Phase 3 SCORE
- **Owner**: company-profile-builder agent
- **Integration risk**: HIGH -- if the path shown in Step 1 differs from where the file is actually saved, the user will look in the wrong place and the topic scout will not find the profile.
- **Validation**: Path displayed in Step 1 must equal the path used in Step 5 file write. Topic scout reads from the same path.

### company_name

- **Source of truth**: Extracted from user document or entered during interview
- **Consumers**: Step 2 (extraction display), Step 4 (preview), Step 5 (saved JSON field `company_name`), existing profile overwrite warning (Step 1 error path E2)
- **Owner**: company-profile-builder agent
- **Integration risk**: MEDIUM -- name must be consistent across extraction, preview, and saved file. Encoding issues (special characters, unicode) could cause mismatches.
- **Validation**: String comparison between extraction output, preview display, and saved JSON value.

### capabilities_list

- **Source of truth**: Extracted from user document, supplemented or corrected during interview
- **Consumers**: Step 2 (extraction display), Step 4 (preview), Step 5 (saved JSON array `capabilities`), sbir-topic-scout SME scoring
- **Owner**: company-profile-builder agent
- **Integration risk**: HIGH -- capabilities are the primary input to subject matter expertise scoring (weight 0.35 in fit scoring). Incorrect or missing keywords directly degrade scoring accuracy.
- **Validation**: Array in saved JSON must contain all keywords shown in preview. Topic scout must be able to iterate the array for keyword matching.

### certifications_data

- **Source of truth**: User responses during interview or extracted from SAM.gov page
- **Consumers**: Step 3 (interview), Step 4 (preview), Step 5 (saved JSON object `certifications`), sbir-topic-scout cert scoring
- **Owner**: company-profile-builder agent
- **Integration risk**: HIGH -- certifications = 0.0 (no SAM.gov) produces automatic "no-go" recommendation in fit scoring. This is a disqualifying factor.
- **Validation**: `certifications.sam_gov.active` must be boolean. `certifications.security_clearance` must be one of: "none", "confidential", "secret", "top_secret". CAGE code must be 5 alphanumeric characters. UEI must match SAM.gov format.

### validation_status

- **Source of truth**: Schema validation result computed in Step 4
- **Consumers**: Step 4 (preview display), Step 5 (save gate -- must be "PASSED" to proceed)
- **Owner**: company-profile-builder agent (validation logic)
- **Integration risk**: MEDIUM -- if validation passes but the saved file does not match the expected schema, the topic scout will fail at runtime.
- **Validation**: Validation must check the same schema constraints that the topic scout expects. Schema definition is in `skills/topic-scout/fit-scoring-methodology.md` under "Company Profile Schema".

### saved_profile_json

- **Source of truth**: Written file at `~/.sbir/company-profile.json`
- **Consumers**: sbir-topic-scout (Phase 3 SCORE, reads entire file), sbir-topic-scout (Example 3 -- missing profile warning)
- **Owner**: company-profile-builder agent (writes), sbir-topic-scout (reads)
- **Integration risk**: HIGH -- this is the primary integration point. The saved file must match the exact schema expected by `sbir-topic-scout`. Field names, nesting structure, and data types must match.
- **Validation**: Load saved file with JSON parser. Verify all top-level keys match schema. Verify nested `certifications` object structure. Verify `key_personnel` and `past_performance` are arrays of objects with expected fields.

### profile_backup

- **Source of truth**: `~/.sbir/company-profile.json.bak` (created during overwrite or atomic write)
- **Consumers**: Error recovery, user rollback
- **Owner**: company-profile-builder agent
- **Integration risk**: LOW -- backup is a safety net, not consumed by other agents.
- **Validation**: Backup file must be a valid copy of the previous profile. If backup fails, the save operation must not proceed.

---

## Integration Checkpoints

### Checkpoint 1: Pre-Setup Verification (Step 1)
- `~/.sbir/` directory exists or can be created
- Check for existing profile (triggers overwrite protection)
- Verify file system write permissions

### Checkpoint 2: Post-Extraction Completeness (Step 2 -> Step 3)
- Track which schema fields were extracted vs. missing
- Missing fields list drives interview question targeting in Step 3
- No field should be asked about if already extracted (avoids redundancy)

### Checkpoint 3: Pre-Save Schema Validation (Step 4)
- All required fields present with correct types
- CAGE code is 5 alphanumeric characters
- Employee count is positive integer
- Security clearance is valid enum value
- Arrays (capabilities, key_personnel, past_performance, socioeconomic, research_institution_partners) are properly structured
- Nested objects (sam_gov, certifications) have required sub-fields

### Checkpoint 4: Post-Save Integration Verification (Step 5)
- Saved file is parseable JSON
- Saved file matches the schema expected by sbir-topic-scout
- If atomic write pattern used: .tmp file cleaned up, .bak file preserved

### Checkpoint 5: Cross-Agent Compatibility
- sbir-topic-scout reads `~/.sbir/company-profile.json` in Phase 3 SCORE
- sbir-topic-scout expects specific field names: `company_name`, `capabilities`, `certifications`, `employee_count`, `key_personnel`, `past_performance`, `research_institution_partners`
- sbir-topic-scout expects `certifications.sam_gov.active` as boolean for no-go scoring
- FitScoring dataclass maps: `capabilities` -> SME dimension, `past_performance` -> PP dimension, `certifications` -> cert+elig+sttr dimensions
