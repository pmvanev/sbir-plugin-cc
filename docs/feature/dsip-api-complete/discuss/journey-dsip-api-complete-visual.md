# Journey: DSIP API Complete -- Visual

## Journey Flow

```
[Agent triggers scan]     [Search DSIP API]      [Enrich each topic]     [Return complete JSON]
       |                        |                        |                        |
       v                        v                        v                        v
  dsip_cli.py             searchParam JSON         4 endpoints per       Structured output
  enrich --status Open    with correct format      topic in parallel     to stdout
       |                        |                        |                        |
  Feels: Routine          Feels: Precise           Feels: Thorough       Feels: Confident
  "Time to scan"          "Only 24 topics,         "Description, Q&A,    "I have everything
                           not 32K"                 instructions -- all   for GO/NO-GO"
                                                    present"
```

## Emotional Arc

- **Start**: Routine/neutral -- agent is executing a standard scan
- **Middle**: Precision -- correct search returns only relevant topics (24 vs 32,638)
- **End**: Confidence -- all 4 data types present, recommendation is well-founded

Pattern: **Confidence Building** -- each step adds completeness, building from metadata to full intelligence.

## Step-by-Step Detail

### Step 1: Topic Search (DsipApiAdapter.fetch)

```
BEFORE (broken):
  GET /topics/api/public/topics/search?numPerPage=100&page=0&topicStatus=Open
  Response: {"total": 32638, "data": [{topicId: 68490, ...}, ...]}
             ^^^^^^^^^^^^^                         ^^^^^
             All topics since 1983                  Numeric ID (useless for details)

AFTER (fixed):
  GET /topics/api/public/topics/search
    ?searchParam={"topicReleaseStatus":[592],"solicitationCycleNames":["openTopics"],"sortBy":"finalTopicCode,asc"}
    &size=100&page=0
  Response: {"total": 24, "data": [{topicId: "7051b2da...86352", cycleName: "DOD_SBIR_2025_P1_C4",
                                     releaseNumber: 12, component: "ARMY", ...}, ...]}
             ^^^^^^^^^^              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
             Only matching topics    Hash ID + metadata for constructing instruction URLs
```

**Shared artifacts produced**: `${topic_hash_id}`, `${cycle_name}`, `${release_number}`, `${component}`

### Step 2: Topic Details (new endpoint)

```
  GET /topics/api/public/topics/${topic_hash_id}/details
  Response: {
    "description": "<p>The Test and Evaluation community has a need for...</p>",
    "objective": "<p>The objective of this topic is to provide low-cost...</p>",
    "phase1Description": "<p>This topic is for Phase I submission only...</p>",
    "phase2Description": "<p>Phase II will develop a prototype...</p>",
    "keywords": "Radar; antenna; metamaterials; scanning; array",
    "technologyAreas": ["Information Systems", "Materials"],
    "focusAreas": ["Advanced Computing and Software", ...],
    "itar": false,
    "cmmcLevel": ""
  }
```

**Replaces**: PDF download + pypdf section parsing (fragile, loses structure)
**Gains**: Structured JSON with HTML content, technology areas, focus areas, ITAR flag, CMMC level

### Step 3: Topic Q&A (new endpoint)

```
  GET /topics/api/public/topics/${topic_hash_id}/questions
  Response: [
    {
      "questionId": 9581,
      "questionNo": 1,
      "question": "<p>Which of these parameters would be of most interest...</p>",
      "answers": [{"answerId": 8258, "answer": "{\"content\": \"<p>The parameters listed...</p>\"}"}],
      "questionStatus": "COMPLETED"
    },
    ...
  ]
```

**Note**: `answer` field contains JSON string with nested `content` key holding HTML. Needs double-parse.
**Previously**: Zero Q&A data (not in topic PDF). Agent had no visibility into government clarifications.

### Step 4: Solicitation Instructions (new endpoint)

```
  GET /submissions/api/public/download/solicitationDocuments
    ?solicitation=${cycle_name}&release=${release_number}&documentType=RELEASE_PREFACE
  Response: PDF binary (658KB BAA preface document)

  GET /submissions/api/public/download/solicitationDocuments
    ?solicitation=${cycle_name}&documentType=INSTRUCTIONS&component=${component}&release=${release_number}
  Response: PDF binary (990KB component instructions, e.g., Army annex)
```

**Previously**: No instruction documents at all. Agent could not assess submission requirements.
**Shared artifacts consumed**: `${cycle_name}`, `${release_number}`, `${component}` from Step 1 search response.

### Step 5: Combine and Output

```
JSON stdout:
{
  "source": "dsip_api",
  "total": 24,
  "total_fetched": 24,
  "candidates_count": 8,
  "topics": [
    {
      "topic_id": "7051b2da...86352",
      "topic_code": "A254-049",
      "title": "Affordable Ka-Band Metamaterial-Based...",
      "status": "Pre-Release",
      "component": "ARMY",
      "description": "The Test and Evaluation community...",
      "objective": "The objective of this topic is...",
      "phase1_description": "This topic is for Phase I...",
      "keywords": ["Radar", "antenna", "metamaterials"],
      "technology_areas": ["Information Systems", "Materials"],
      "itar": false,
      "qa_entries": [
        {"question_no": 1, "question": "Which parameters...", "answer": "The parameters listed...", "status": "COMPLETED"},
        ...
      ],
      "qa_count": 7,
      "solicitation_instructions": "... (extracted from BAA preface PDF)",
      "component_instructions": "... (extracted from ARMY annex PDF)",
      "enrichment_status": "complete"
    }
  ]
}
```

## Error Path Scenarios

| Failure | Impact | Recovery |
|---------|--------|----------|
| Search API returns 403 (missing User-Agent) | No topics at all | Adapter sets `User-Agent: Mozilla/5.0` header (already present) |
| Details endpoint fails for one topic | Missing description for that topic | Isolated error; other topics unaffected. Fall back to PDF if available. |
| Q&A endpoint returns empty array | Topic has no published Q&A | Normal case for some topics (`noOfPublishedQuestions: 0`). Not an error. |
| Instruction PDF 404 | Missing instructions for that cycle/component | Isolated error. Some components may not have published instructions yet. |
| Q&A answer JSON malformed | Cannot parse nested content | Return raw answer string as fallback. Log warning. |
| Rate limit / timeout | Transient failure | Existing retry with exponential backoff (3 attempts). |

## Integration Points

| Producer | Artifact | Consumer |
|----------|----------|----------|
| Search response | `topicId` (hash) | Details, Q&A, PDF endpoints |
| Search response | `cycleName`, `releaseNumber`, `component` | Instruction download URL construction |
| Search response | `noOfPublishedQuestions` | Skip Q&A call when count is 0 |
| Search response | `baaInstructions` array | Determine which instruction types are available |
| Details response | `description`, `objective`, phases | Enriched topic output, scoring |
| Q&A response | question/answer entries | Enriched topic output, agent analysis |
| Instruction PDFs | Extracted text | Enriched topic output, agent analysis |
| Combined output | Complete JSON | `FinderService`, cache, scoring, agent stdout |
