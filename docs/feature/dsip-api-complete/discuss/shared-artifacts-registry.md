# Shared Artifacts Registry: dsip-api-complete

## Artifacts

### topic_hash_id

- **Source of truth**: DSIP search API response field `topicId` (e.g., `7051b2da4a1e4c52bd0e7daf80d514f7_86352`)
- **Consumers**: Details endpoint URL path, Q&A endpoint URL path, PDF download URL path
- **Owner**: DsipApiAdapter (search normalization)
- **Integration risk**: HIGH -- hash ID is the key linking search results to all enrichment endpoints. Numeric IDs (from broken format) will 404 on all detail endpoints.
- **Validation**: Hash ID format contains underscore separator (e.g., `{hex}_{numeric}`)

### cycle_name

- **Source of truth**: DSIP search API response field `cycleName` (e.g., `DOD_SBIR_2025_P1_C4`)
- **Consumers**: Solicitation instruction download URL (`solicitation` param), component instruction download URL (`solicitation` param)
- **Owner**: DsipApiAdapter (search normalization)
- **Integration risk**: HIGH -- incorrect cycle name produces 404 on instruction downloads
- **Validation**: Format matches `DOD_(SBIR|STTR)_\d{4}_P\d+_C\d+`

### release_number

- **Source of truth**: DSIP search API response field `releaseNumber` (e.g., `12`)
- **Consumers**: Solicitation instruction download URL (`release` param), component instruction download URL (`release` param)
- **Owner**: DsipApiAdapter (search normalization)
- **Integration risk**: MEDIUM -- integer from search response, used as string in URL param
- **Validation**: Positive integer

### component

- **Source of truth**: DSIP search API response field `component` (e.g., `ARMY`)
- **Consumers**: Component instruction download URL (`component` param), normalized topic output
- **Owner**: DsipApiAdapter (search normalization)
- **Integration risk**: MEDIUM -- must match exactly (case-sensitive) for instruction download
- **Validation**: One of known components (ARMY, NAVY, USAF, DARPA, CBD, DHA, MDA, SOCOM, OSD, DTRA, NGA, DLA, DCSA)

### published_qa_count

- **Source of truth**: DSIP search API response field `noOfPublishedQuestions`
- **Consumers**: Q&A fetch skip optimization (skip when count is 0)
- **Owner**: DsipApiAdapter (search normalization)
- **Integration risk**: LOW -- optimization only; if wrong, Q&A endpoint returns empty array
- **Validation**: Non-negative integer

### baa_instructions_metadata

- **Source of truth**: DSIP search API response field `baaInstructions` (array of upload metadata)
- **Consumers**: Instruction availability check (determine which document types exist before downloading)
- **Owner**: DsipApiAdapter (search normalization)
- **Integration risk**: LOW -- used for optimization; if missing, adapter attempts download and handles 404
- **Validation**: Array of objects with `uploadTypeCode` field

## Integration Checkpoints

| Checkpoint | Validates | Failure Indicator |
|-----------|-----------|-------------------|
| Search returns hash IDs | `topic_hash_id` format | ID is purely numeric (old format) |
| Search includes cycle metadata | `cycle_name`, `release_number` present | Fields are null or missing |
| Details endpoint accepts hash ID | `topic_hash_id` used correctly | HTTP 404 on details call |
| Instruction URL construction | `cycle_name` + `release_number` + `component` combined | HTTP 404 on instruction download |
| Q&A skip optimization | `published_qa_count` is 0 | Unnecessary Q&A calls for topics without questions |
