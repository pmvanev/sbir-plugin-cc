# ADR-043: Enrichment as Optional Profile Builder Phase

## Status

Accepted

## Context

The enrichment capability (three-API cascade from SAM.gov, SBIR.gov, USASpending.gov) needs to be integrated into the existing profile builder agent flow. The profile builder currently has 5 phases: MODE SELECT, RESEARCH, GATHER, PREVIEW, SAVE. The question is how enrichment relates to these phases: replace RESEARCH, extend GATHER, or add a new phase.

The existing RESEARCH phase uses WebSearch/WebFetch to find company information on the open web. Enrichment uses structured API calls via Python CLI for authoritative government data. They serve different purposes and may both be valuable.

## Decision

Add ENRICHMENT as a new optional phase between MODE SELECT and RESEARCH in the profile builder flow. The phase is offered when a SAM.gov API key is available (or can be set up). When skipped, the profile builder continues with its existing RESEARCH -> GATHER -> PREVIEW -> SAVE flow unchanged.

Phase order: MODE SELECT -> ENRICHMENT (optional) -> RESEARCH -> GATHER -> PREVIEW -> SAVE.

Enrichment runs before RESEARCH because:
1. Enrichment provides authoritative structured data (legal name, CAGE, NAICS, certifications)
2. RESEARCH can then skip searching for data already obtained from APIs
3. GATHER can target only fields not covered by enrichment or research

## Alternatives Considered

### Alternative 1: Replace RESEARCH phase with ENRICHMENT

- **Evaluation**: Enrichment provides better data than web scraping for the fields it covers. Could eliminate RESEARCH entirely.
- **Rejection**: RESEARCH covers fields enrichment cannot (capabilities from company website, key personnel from LinkedIn, partner information from university pages). Both phases serve different data sets. Removing RESEARCH loses coverage for non-API-accessible data.

### Alternative 2: Extend GATHER phase with enrichment option

- **Evaluation**: User selects "enrich from APIs" as an input mode alongside documents and interview in GATHER.
- **Rejection**: GATHER already has three modes (documents, interview, both). Adding a fourth conflates structured API retrieval with user-driven data collection. Enrichment is a distinct action (one input, automated retrieval) that does not fit the GATHER interaction pattern.

### Alternative 3: Mandatory enrichment (no skip option)

- **Evaluation**: If user has a SAM.gov API key, always run enrichment. Simpler flow.
- **Rejection**: User may not want to wait for API calls (offline use, slow network). User may prefer to enter data manually for fields they know have changed since last SAM.gov update. JTBD analysis identified "skip enrichment" as a required option (anxiety reduction for users concerned about stale API data).

## Consequences

### Positive

- Enrichment is additive -- existing flow unchanged when skipped
- Clear phase boundary: enrichment data is confirmed before RESEARCH/GATHER
- RESEARCH and GATHER can optimize by skipping fields already populated
- User always has a choice (API key setup, enrichment, or manual)

### Negative

- One more phase in the profile builder flow (6 phases instead of 5 when enrichment is active)
- Agent markdown becomes longer with enrichment phase logic
- RESEARCH phase needs awareness of enrichment-populated fields to avoid redundant web searches
