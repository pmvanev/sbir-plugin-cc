# DSIP API Reference

How the DoD SBIR/STTR Innovation Portal (dodsbirsttr.mil) API actually works, discovered through manual testing on 2026-03-24.

## Key Discovery

The DSIP search API has **two query formats**. The simple format (flat query params) is broken — the Angular topics-app uses a JSON-encoded `searchParam` format that actually works.

### Broken format (returns all 32K topics, ignores filters)

```
GET /topics/api/public/topics/search?numPerPage=10&page=0&topicStatus=Open
```

Returns all 32,638 topics from 1983 onward regardless of filters. The `topicStatus`, `component`, `keyword`, and `sort` params are silently ignored. The `topicId` field returns a numeric ID (e.g., `68490`).

### Working format (used by the Angular app)

```
GET /topics/api/public/topics/search?searchParam={JSON}&size=10&page=0
```

The `searchParam` value is URL-encoded JSON:

```json
{
  "searchText": null,
  "components": null,
  "programYear": null,
  "solicitationCycleNames": ["openTopics"],
  "releaseNumbers": [],
  "topicReleaseStatus": [591, 592],
  "modernizationPriorities": null,
  "sortBy": "finalTopicCode,asc"
}
```

- **Status IDs**: `591` = Pre-Release, `592` = Open
- **Pagination**: `size` (not `numPerPage`) and `page` (0-indexed)
- **Returns**: only matching topics (e.g., 24 for current cycle)
- **topicId**: returns the **hash ID** (e.g., `7051b2da4a1e4c52bd0e7daf80d514f7_86352`), not a numeric ID

## Endpoints

All endpoints require `User-Agent: Mozilla/5.0` header or they return 403.

### Topic Search

```
GET /topics/api/public/topics/search?searchParam={JSON}&size={N}&page={N}
```

Returns `{ "total": N, "data": [...] }`. Each topic in `data` includes:
- `topicId` (hash ID), `topicCode`, `topicTitle`, `topicStatus`
- `component`, `program`, `cycleName`, `solicitationNumber`, `releaseNumber`
- `topicStartDate`, `topicEndDate` (Unix milliseconds)
- `noOfPublishedQuestions`, `topicQAStatus`, `topicQAOpen`
- `baaInstructions` array with `uploadId`, `fileName`, `uploadTypeCode`
- `cmmcLevel`, `phaseHierarchy`

### Topic Details

```
GET /topics/api/public/topics/{hash_id}/details
```

Returns structured JSON with HTML content:
- `description`, `objective` (HTML strings)
- `phase1Description`, `phase2Description`, `phase3Description` (HTML)
- `keywords` (semicolon-separated string)
- `technologyAreas` (string array), `focusAreas` (string array)
- `referenceDocuments` (array of `{uploadId, referenceType, referenceTitle, url}`)
- `cmmcLevel`, `itar` (boolean)

### Topic Q&A

```
GET /topics/api/public/topics/{hash_id}/questions
```

Returns JSON array of Q&A entries. Each entry:
- `questionId`, `questionNo`, `questionStatus`, `questionStatusDisplay`
- `question` (HTML string)
- `questionSubmittedOn` (Unix milliseconds)
- `answers` array, each with `answerId` and `answer` (JSON string containing `{"content": "<HTML>"}`)

### Topic PDF Download

```
GET /topics/api/public/topics/{hash_id}/download/PDF
```

Returns PDF binary. Contains description, phases, references, TPOC — same content as the details endpoint but as a formatted PDF document.

### Solicitation Instructions (BAA Preface)

```
GET /submissions/api/public/download/solicitationDocuments?solicitation={cycle_name}&release={release_number}&documentType=RELEASE_PREFACE
```

Example: `?solicitation=DOD_SBIR_2025_P1_C4&release=12&documentType=RELEASE_PREFACE`

Returns PDF binary (the BAA preface document with general submission instructions).

Parameters come from the search response: `cycleName` and `releaseNumber`.

### Component Instructions

```
GET /submissions/api/public/download/solicitationDocuments?solicitation={cycle_name}&documentType=INSTRUCTIONS&component={component}&release={release_number}
```

Example: `?solicitation=DOD_SBIR_2025_P1_C4&documentType=INSTRUCTIONS&component=ARMY&release=12`

Returns PDF binary (component-specific submission instructions, e.g., ARMY annex).

Parameters come from the search response: `cycleName`, `component`, `releaseNumber`.

### TPOC (does NOT work via API)

```
GET /topics/api/public/topics/{hash_id}/tpocs
```

Returns HTTP 500. TPOC name is visible on the rendered Angular page but not available via this API endpoint. The TPOC name does appear in the topic PDF download.

### Dropdown/Reference Data

```
GET /core/api/public/dropdown/lookup?type=topics.release_status&excludeLookupItem=INACTIVE,READY_FOR_RELEASE,READY_TO_CERTIFY,READY_TO_REVIEW,REVISION_REQUESTED
GET /core/api/public/dropdown/components?includeArchived=true
GET /core/api/public/dropdown/focusAreas
GET /core/api/public/dropdown/technologyAreas
GET /topics/api/public/topics/solicitations
```

These return reference data the Angular app uses for filter dropdowns.

## Search Parameter Options

### topicReleaseStatus

| ID | Status |
|----|--------|
| 591 | Pre-Release |
| 592 | Open |

To get all active topics: `"topicReleaseStatus": [591, 592]`

### solicitationCycleNames

Use `["openTopics"]` for current active solicitations. Specific cycle names (e.g., `DOD_SBIR_2025_P1_C4`) can also be used.

### components

Array of component names: `["ARMY", "NAVY", "USAF", "DARPA", "CBD", "DHA", "MDA", "SOCOM", "OSD", "DTRA", "NGA", "DLA", "DCSA"]`

### sortBy

`"finalTopicCode,asc"` (default in Angular app)

## Constructing Instruction Download URLs

From a topic in the search response:
- `cycleName` → `solicitation` param (e.g., `DOD_SBIR_2025_P1_C4`)
- `releaseNumber` → `release` param (e.g., `12`)
- `component` → `component` param (e.g., `ARMY`)
- `baaInstructions[].uploadTypeCode` tells you what documents exist:
  - `COMPONENT_FINAL_DOCUMENT_UPLOAD` → component instructions available
  - Other types may indicate solicitation-level documents

## Recorded Fixtures

Live API responses recorded on 2026-03-24 in `tests/fixtures/dsip_live/`:
- `raw_api_search_correct_format.json` — search with correct `searchParam` format (3 topics)
- `raw_api_details_response.json` — topic detail for A254-049
- `raw_api_qa_response.json` — Q&A for A254-049 (7 entries)
- `raw_component_instructions_army.pdf` — ARMY component instructions (990KB)
- `raw_solicitation_instructions.pdf` — BAA preface (658KB)
