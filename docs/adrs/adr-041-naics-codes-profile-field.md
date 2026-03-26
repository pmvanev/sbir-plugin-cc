# ADR-041: NAICS Codes as Top-Level Profile Field

## Status

Accepted

## Context

The SAM.gov Entity API returns NAICS codes (primary + all registered) for every entity. NAICS codes are relevant for SBIR topic matching -- many solicitations specify preferred NAICS codes. The current `company-profile-schema.json` has no field for NAICS codes. The question is where to store them: as a new top-level field, nested under certifications, or as informational metadata in sources.

The `sbir-topic-scout` agent currently does not use NAICS codes for scoring, but the data has clear future value for topic-to-company matching.

## Decision

Add `naics_codes` as a new top-level optional array field in `company-profile-schema.json`. Each entry is an object with `code` (string), `primary` (boolean), and optional `description` (string).

The field is NOT added to the `required` array, making the schema extension backward-compatible. Existing profiles without NAICS codes remain valid.

## Alternatives Considered

### Alternative 1: Store in certifications.sam_gov object

- **Evaluation**: Logically, NAICS codes come from SAM.gov registration. Nesting under `certifications.sam_gov` groups them with their source.
- **Rejection**: NAICS codes are not certifications -- they are industry classification codes. Nesting them under certifications misrepresents their nature. Additionally, NAICS codes have future use independent of SAM.gov status (e.g., matching against solicitation-specified NAICS).

### Alternative 2: Store in sources.enrichment_metadata (informational only)

- **Evaluation**: Treat NAICS codes as enrichment metadata rather than profile data. No schema change required.
- **Rejection**: NAICS codes are first-class profile data that topic-scout should use for matching. Burying them in metadata makes them inaccessible to the scoring algorithm without special handling. The data belongs in the profile, not in provenance metadata.

### Alternative 3: Flat string array (just codes, no structure)

- **Evaluation**: `"naics_codes": ["334511", "541715", "334220"]`. Simpler schema.
- **Rejection**: Loses the primary/secondary distinction that SAM.gov provides. The primary NAICS code is the most relevant for topic matching and should be distinguishable.

## Consequences

### Positive

- Topic-scout can use NAICS codes for topic matching (future enhancement)
- Primary code distinguished from secondary codes
- Backward-compatible (optional field)
- Clean semantic placement (industry codes are a profile attribute, not a certification)

### Negative

- Schema change requires updating `company-profile-schema.json`
- Existing profiles do not have this field (acceptable -- it is optional)
- Topic-scout does not consume this field yet (future work)
