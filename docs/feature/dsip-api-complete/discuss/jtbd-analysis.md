# JTBD Analysis: dsip-api-complete

## Job Classification

**Job Type**: Job 2 -- Improve Existing System (Brownfield)
**Workflow**: `[research] -> baseline -> roadmap -> split -> execute -> review`
**Rationale**: System exists and is understood. Problem is identified (wrong API format). No discovery phase needed -- we know what the correct API looks like from recorded responses.

## Primary Job Story

**When** the sbir-topic-scout agent runs `python scripts/dsip_cli.py enrich --status Open` to gather intelligence for a GO/EVALUATE/NO-GO recommendation,
**I want to** receive complete topic data including descriptions, Q&A exchanges, solicitation instructions, and component instructions as structured JSON,
**so I can** make an accurate, data-driven recommendation without Dr. Sarah Chen having to manually browse dodsbirsttr.mil for the missing pieces.

## Job Dimensions

### Functional Job
Retrieve all 4 data types (topic descriptions, Q&A, solicitation instructions, component instructions) from the DSIP API using the correct JSON `searchParam` format, and deliver them as structured JSON to stdout.

### Emotional Job
The agent (and indirectly Dr. Sarah Chen) needs to feel confident that the data is complete. Today the agent silently returns partial data -- descriptions from PDF parsing, zero Q&A, no instructions -- and the confidence in GO/NO-GO recommendations is undermined. After the fix, the agent should feel that "I have everything I need to make this call."

### Social Job
Dr. Sarah Chen needs to trust the plugin's recommendations enough to skip manual DSIP browsing. If she has to double-check every recommendation on the portal, the plugin has failed its social contract -- it should be seen as a reliable intelligence source, not a rough first draft.

## Forces Analysis

### Demand-Generating

- **Push**: The current adapter uses the wrong query format (flat params with `numPerPage`). The API silently returns all 32,638 topics from 1983 onward, ignoring filters. The enrichment adapter only downloads topic PDFs and parses them with pypdf -- it gets descriptions but zero Q&A (Q&A is not in the PDF) and no solicitation or component instructions. The agent's recommendations are based on incomplete data.

- **Pull**: The correct API format is now fully documented. All 4 data types are available via pure HTTP -- no browser scraping. The `/details` endpoint returns structured JSON with HTML (richer than PDF parsing). The `/questions` endpoint returns structured Q&A. Instruction PDFs are downloadable via a simple URL constructed from search response fields (`cycleName`, `releaseNumber`, `component`). Recorded live fixtures prove all endpoints work.

### Demand-Reducing

- **Anxiety**: Changing the adapter could break existing tests and cached data. The `_normalize_topic` function maps different field names (the correct format returns `topicId` as hash ID, not numeric). Instruction PDFs need pypdf parsing that may be fragile. The Q&A endpoint returns HTML-in-JSON-in-JSON (nested `answer` field containing `{"content": "<HTML>"}`), which needs careful parsing.

- **Habit**: The current PDF-based enrichment "works" for descriptions. Existing tests use mocked responses with the old field names. The CLI skill documents the old behavior. Switching means updating adapters, tests, fixtures, CLI, and the agent skill.

### Assessment

- **Switch likelihood**: High -- the push is strong (data is provably incomplete), pull is concrete (working API endpoints documented with live fixtures), and anxiety is manageable (ports-and-adapters architecture isolates changes).
- **Key blocker**: Test fixture migration and ensuring the nested Q&A JSON parsing is robust.
- **Key enabler**: Live recorded fixtures prove exactly what the API returns.
- **Design implication**: Fix adapters behind existing port interfaces. No architecture change needed. Enrichment adapter shifts from PDF-only to API-first (details + Q&A as JSON, instructions as PDF).

## 8-Step Job Map

| Step | Current State | Target State |
|------|--------------|--------------|
| 1. **Define** | Agent decides to scan for open topics | No change -- agent uses same CLI commands |
| 2. **Locate** | Agent calls `dsip_cli.py fetch --status Open` | Same command, but adapter uses correct `searchParam` JSON format returning only matching topics with hash IDs |
| 3. **Prepare** | Adapter builds flat query params (`numPerPage`, `topicStatus`) | Adapter builds JSON `searchParam` with `topicReleaseStatus`, `solicitationCycleNames`, `size` |
| 4. **Confirm** | No validation -- silently returns 32K topics regardless of filters | Adapter validates response has correct shape (hash IDs, `cycleName` present). Agent sees realistic topic count (e.g., 24) |
| 5. **Execute** | Enrichment downloads topic PDF, parses with pypdf. Gets description only. | Enrichment calls `/details` for structured JSON + `/questions` for Q&A + instruction PDF endpoints. Gets all 4 data types. |
| 6. **Monitor** | Completeness metrics report descriptions only | Completeness metrics report all 4 types: descriptions, Q&A, solicitation instructions, component instructions |
| 7. **Modify** | No recovery for missing Q&A or instructions -- data simply absent | Per-endpoint failure isolation: if Q&A endpoint fails, description and instructions still returned. Each data type independently retried. |
| 8. **Conclude** | Agent gets partial JSON, makes recommendation with incomplete data | Agent gets complete JSON, makes confident GO/EVALUATE/NO-GO with full topic intelligence |

## Outcome Statements

1. Minimize the likelihood that topic search returns unfiltered results (today: 100% -- all 32K returned regardless of status filter)
2. Minimize the number of data types missing from enriched topic output (today: 2 of 4 missing -- Q&A and instructions)
3. Minimize the time to retrieve complete topic intelligence for a solicitation cycle (today: impossible -- Q&A never retrieved)
4. Maximize the likelihood that GO/EVALUATE/NO-GO recommendations are based on complete data
5. Minimize the likelihood that Dr. Sarah Chen needs to manually browse dodsbirsttr.mil to fill gaps

## Related Jobs (Out of Scope)

- **TPOC retrieval**: The `/tpocs` endpoint returns HTTP 500. TPOC name is available in the topic PDF but not via API. Not blocking -- current PDF enrichment already captures TPOC from PDF text.
- **Solicitation dropdown data**: Reference data endpoints exist but are not needed for the core fix.
- **Topic PDF download**: The `/download/PDF` endpoint works and is already implemented. This fix does not remove it -- it supplements PDF-only enrichment with structured API data.
