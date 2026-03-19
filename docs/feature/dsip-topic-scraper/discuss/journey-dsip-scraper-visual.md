# Journey: DSIP Topic Scraping and Scoring Pipeline

## Journey Flow

```
[Trigger]         [Step 1]           [Step 2]           [Step 3]           [Step 4]           [Goal]
 User runs        Connect &          Fetch topic         Enrich with        Integrate &        Scored topics
 /solicitation    validate           metadata via        descriptions,      score against      with GO/
 find             DSIP access        API endpoint        instructions,      company profile    EVALUATE/
                                                         Q&A                                   NO-GO
 Feels:           Feels:             Feels:              Feels:             Feels:             Feels:
 Curious,         Reassured          Engaged,            Thorough,          Anticipating       Confident,
 hopeful          (or warned)        watching            informed           results            informed
                                     progress
```

## Emotional Arc

- **Start**: Curious and hopeful -- "Let me see what is out there this cycle"
- **Middle**: Engaged and watchful during scraping, building to thorough and informed as detail enrichment completes
- **End**: Confident and empowered -- "I have everything I need to make decisions"
- **Pattern**: Confidence Building (anxious/uncertain -> focused/engaged -> confident/satisfied)

---

## Step 1: Validate DSIP Access

**Command**: Internal step within `/solicitation find` pipeline
**Duration**: 2-5 seconds

```
+-- Step 1: Validate DSIP Access -----------------------------------+
|                                                                    |
|  $ /solicitation find --agency "Air Force" --phase I               |
|                                                                    |
|  [info] Loading company profile from ~/.sbir/company-profile.json  |
|  [info] Connecting to DSIP portal...                               |
|  [ok]   DSIP API endpoint reachable                                |
|  [info] Searching: status=Open, component=USAF, phase=I            |
|                                                                    |
+--------------------------------------------------------------------+
```

**Emotional state**: Entry: curious, hopeful | Exit: reassured

**Error variant**:
```
+-- Step 1: Validate DSIP Access (FAILURE) -------------------------+
|                                                                    |
|  [info] Connecting to DSIP portal...                               |
|  [warn] DSIP API endpoint unreachable (timeout after 30s)          |
|                                                                    |
|  WHAT:  Cannot connect to DSIP topic search API                    |
|  WHY:   The portal may be down or your network blocks it           |
|  DO:    Try --file ./baa.pdf to search from a downloaded BAA       |
|         or retry later with /solicitation find                     |
|                                                                    |
+--------------------------------------------------------------------+
```

---

## Step 2: Fetch Topic Metadata via API

**Command**: Internal pipeline step (API call with pagination)
**Duration**: 5-30 seconds depending on result count

```
+-- Step 2: Fetch Topic Metadata ------------------------------------+
|                                                                     |
|  [info] Fetching topics from DSIP API (page 1)...                   |
|  [info] Found 247 total topics matching criteria                    |
|  [info] Fetching page 1/3 (100 topics)...  done                    |
|  [info] Fetching page 2/3 (100 topics)...  done                    |
|  [info] Fetching page 3/3 (47 topics)...   done                    |
|                                                                     |
|  Summary: 247 topics fetched                                        |
|    Open: 183  |  Pre-Release: 64                                    |
|    Air Force: 42  |  Navy: 38  |  Army: 31  |  DARPA: 19           |
|    CBD: 12  |  DHA: 15  |  MDA: 11  |  SOCOM: 14  |  Other: 65    |
|                                                                     |
+---------------------------------------------------------------------+
```

**Emotional state**: Entry: anticipating | Exit: engaged, seeing data arrive

**Error variant (partial fetch)**:
```
+-- Step 2: Fetch Topic Metadata (PARTIAL) --------------------------+
|                                                                     |
|  [info] Fetching page 1/3 (100 topics)...  done                    |
|  [info] Fetching page 2/3 (100 topics)...  done                    |
|  [warn] Fetching page 3/3 failed (HTTP 503)                        |
|                                                                     |
|  [warn] Partial results: 200 of ~247 topics fetched                |
|  [info] Proceeding with available data. Missing ~47 topics.         |
|  [info] Retry later to capture remaining topics.                    |
|                                                                     |
+---------------------------------------------------------------------+
```

---

## Step 3: Enrich Topics with Descriptions, Instructions, and Q&A

**Command**: Internal pipeline step (per-topic detail fetching)
**Duration**: 30 seconds to 5 minutes depending on topic count after pre-filter

```
+-- Step 3: Enrich Topic Details ------------------------------------+
|                                                                     |
|  [info] Pre-filtering by company capabilities...                    |
|  [info] 42 topics match capability keywords (of 247 total)         |
|                                                                     |
|  Enriching topic details:                                           |
|    [  1/42] AF263-042  Compact Directed Energy for C-UAS     [ok]   |
|    [  2/42] AF263-078  Edge AI for ISR Data Fusion           [ok]   |
|    [  3/42] N261-034   Autonomous UUV Navigation             [ok]   |
|    ...                                                              |
|    [ 40/42] DARPA-PA-26-01  Resilient Mesh Networks          [ok]   |
|    [ 41/42] MDA263-009  Hypersonic Tracking Algorithms       [warn] |
|             Description: captured | Q&A: 0 (none posted)           |
|    [ 42/42] CBD263-003  CBRN Sensor Miniaturization          [ok]   |
|                                                                     |
|  Enrichment complete: 42 topics                                     |
|    Descriptions: 42/42  |  Instructions: 38/42  |  Q&A: 29/42     |
|                                                                     |
+---------------------------------------------------------------------+
```

**Emotional state**: Entry: watchful, patient | Exit: thorough, informed

---

## Step 4: Score and Rank Topics

**Command**: Continues within `/solicitation find` -- hands off to existing fit-scoring pipeline
**Duration**: 5-15 seconds

```
+-- Step 4: Score & Rank Topics -------------------------------------+
|                                                                     |
|  [info] Scoring 42 topics against company profile...                |
|                                                                     |
|  Rank | Topic ID     | Agency    | Title                    | Score | Rec       | Deadline   |
|  -----+--------------+-----------+--------------------------+-------+-----------+------------|
|     1 | AF263-042    | Air Force | Compact Directed Energy  | 0.84  | GO        | 2026-05-15 |
|     2 | N261-034     | Navy      | Autonomous UUV Nav       | 0.71  | GO        | 2026-05-15 |
|     3 | AF263-078    | Air Force | Edge AI for ISR Fusion   | 0.62  | GO        | 2026-05-15 |
|     4 | DARPA-PA-26  | DARPA     | Resilient Mesh Networks  | 0.55  | EVALUATE  | 2026-06-01 |
|     5 | CBD263-003   | CBD       | CBRN Sensor Miniatur.    | 0.48  | EVALUATE  | 2026-05-15 |
|  ...                                                                |
|                                                                     |
|  Disqualified:                                                      |
|  MDA263-009  | MDA  | Hypersonic Tracking | Requires TS (profile: Secret) |
|                                                                     |
|  Results saved to .sbir/finder-results.json                         |
|  Type "pursue <topic-id>" to start a proposal for a topic.         |
|                                                                     |
+---------------------------------------------------------------------+
```

**Emotional state**: Entry: anticipating | Exit: confident, empowered

---

## Data Flow Diagram

```
                    DSIP Portal
                    (dodsbirsttr.mil)
                         |
                    [DSIP Search API]
                    /topics/api/public/
                    topics/search
                         |
                         v
              +---------------------+
              | DSIP Scraper Port   |
              | (Python/Playwright) |
              +---------------------+
                         |
                         v
              +---------------------+
              | Raw Topic JSON      |
              | (API response)      |
              +---------------------+
                         |
                    [Parse & Normalize]
                         |
                         v
              +---------------------+
              | TopicInfo[]         |
              | (domain objects)    |
              +---------------------+
                         |
              +----------+----------+
              |                     |
              v                     v
   +------------------+   +------------------+
   | .sbir/           |   | Topic Scout      |
   | dsip_topics.json |   | Agent            |
   | (cache)          |   | (fit scoring)    |
   +------------------+   +------------------+
                                   |
                                   v
                          +------------------+
                          | .sbir/           |
                          | finder-results   |
                          | .json            |
                          +------------------+
```
