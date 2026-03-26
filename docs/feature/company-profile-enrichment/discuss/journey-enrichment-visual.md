# Journey Visual: Company Profile Enrichment

## Journey Overview

```
[Trigger]              [Step 1]           [Step 2]           [Step 3]           [Step 4]           [Step 5]
Profile builder        API key            User provides      Three-API          Review enriched    Merge confirmed
asks for SAM.gov       check/setup        UEI                cascade            data with          data into
details                                                      fetch              sources shown      profile draft
     |                    |                   |                   |                  |                  |
  Feels:               Feels:              Feels:              Feels:             Feels:             Feels:
  "Ugh, I have to      Quick setup,        Simple -- just      Impressed,         In control,        Relieved,
  look all this up"    manageable          one identifier      "it found          transparent        "that saved
                                                               everything!"                          me 15 min"
     |                    |                   |                   |                  |                  |
  Artifacts:           Artifacts:          Artifacts:          Artifacts:         Artifacts:         Artifacts:
  (none)               api_keys.json       uei_input           enrichment_        confirmed_         profile_draft{}
                       (if new)            "DKJF84NXLE73"      result{}           enrichment{}       (enriched)
```

**Emotional Arc Pattern**: Problem Relief
- Start: Frustrated ("I have to look this up on three websites")
- Middle: Impressed/productive ("it pulled everything from my UEI")
- End: Relieved/confident ("authoritative data, confirmed by me")

**Relationship to Existing Journey**: This journey inserts between Step 1 (MODE SELECT) and Step 3 (INTERVIEW) of the existing profile builder journey. When the user provides a UEI, enrichment pre-populates fields that the interview would otherwise ask about. The interview then asks only about remaining gaps.

---

## Step 1: API Key Check and Setup

**Trigger**: User is in profile builder flow (new or update) and the system detects enrichment is possible.
**Command**: Integrated into profile builder agent flow.

```
+-- Enrichment Available -------------------------------------------+
|                                                                   |
|  I can pre-populate your profile from federal databases.          |
|                                                                   |
|  With just your UEI (Unique Entity Identifier), I can pull:       |
|    - Legal name, CAGE code, NAICS codes     (from SAM.gov)        |
|    - Certifications (8(a), HUBZone, etc.)   (from SAM.gov)        |
|    - SBIR award history                     (from SBIR.gov)       |
|    - Federal award totals                   (from USASpending)    |
|                                                                   |
|  This typically saves 15-20 minutes of manual entry.              |
|                                                                   |
|  To use SAM.gov, I need your API key.                             |
|  Checking ~/.sbir/api-keys.json...                                |
|                                                                   |
+-------------------------------------------------------------------+
```

### Case A: API Key Found

```
+-- API Key Found --------------------------------------------------+
|                                                                   |
|  SAM.gov API key found in ~/.sbir/api-keys.json                   |
|  Key ending in: ...x7Kf                                           |
|                                                                   |
|  Ready to enrich. What is your UEI?                               |
|                                                                   |
+-------------------------------------------------------------------+
```

### Case B: API Key Not Found

```
+-- SAM.gov API Key Needed -----------------------------------------+
|                                                                   |
|  No SAM.gov API key found.                                        |
|                                                                   |
|  To get one (free, takes ~2 minutes):                             |
|    1. Log in to SAM.gov                                           |
|    2. Go to: https://sam.gov/profile/details                      |
|    3. Under "Public API Key", click "Generate"                    |
|    4. Copy the key and paste it here                              |
|                                                                   |
|  The key gives you 1,000 API requests/day -- more than enough.    |
|                                                                   |
|  Options:                                                         |
|    1. Enter your SAM.gov API key now                              |
|    2. Skip enrichment -- I'll ask all questions manually          |
|                                                                   |
+-------------------------------------------------------------------+
```

### Case B (continued): Key Validation

```
  User: abc123def456ghi789

+-- Validating Key -------------------------------------------------+
|                                                                   |
|  Testing SAM.gov API key...                                       |
|  [################] API responded successfully                    |
|                                                                   |
|  Key saved to ~/.sbir/api-keys.json (permissions: owner-only)     |
|  You won't need to enter this again.                              |
|                                                                   |
|  What is your UEI?                                                |
|                                                                   |
+-------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Mild friction ("another API key setup?")
- Exit: Quick relief ("that was painless") or skip accepted ("I'll do it manually")

**Integration Checkpoint**: API key file exists at `~/.sbir/api-keys.json` with restricted permissions. Key validated with a test call to SAM.gov. SBIR.gov and USASpending.gov require no key.

---

## Step 2: User Provides UEI

**Command**: Conversational -- user enters UEI when prompted.

```
  User: DKJF84NXLE73

+-- UEI Received ---------------------------------------------------+
|                                                                   |
|  UEI: DKJF84NXLE73                                               |
|                                                                   |
|  Fetching from federal databases...                               |
|                                                                   |
|    SAM.gov Entity API         [################] done             |
|    SBIR.gov Awards API        [################] done             |
|    USASpending.gov            [################] done             |
|                                                                   |
+-------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Expectant ("will this actually work?")
- Exit: Impressed/productive ("it's pulling data from three places at once")

**Integration Checkpoint**: UEI validated as 12 alphanumeric characters before API calls. UEI stored for all three API queries.

---

## Step 3: Three-API Enrichment Cascade

**Command**: System calls Python enrichment service via Bash tool.

The enrichment service calls three APIs in sequence:

1. **SAM.gov Entity API** -- `GET /entity-information/v3/entities?ueiSAM={UEI}&api_key={KEY}`
   Returns: legal name, CAGE code, NAICS codes, business type flags, registration status, addresses

2. **SBIR.gov Company API** -- `GET /api/company?keyword={company_name}` (filtered by UEI in response)
   Returns: SBIR award count, ownership flags

3. **USASpending.gov** -- `POST /api/v2/autocomplete/recipient/` then `GET /api/v2/recipient/{id}/?year=all`
   Returns: total federal award history, business type corroboration

```
+-- Enrichment Results ---------------------------------------------+
|                                                                   |
|  Found data from 3 federal sources for UEI DKJF84NXLE73:         |
|                                                                   |
|  From SAM.gov:                                                    |
|    Legal name:       Radiant Defense Systems, LLC                 |
|    CAGE code:        7X2K9                                        |
|    NAICS codes:      334511 (primary), 541715, 334220             |
|    Registration:     Active (expires 2027-01-15)                  |
|    Certifications:   (none currently listed)                      |
|    Address:          123 Innovation Dr, Huntsville, AL 35806      |
|                                                                   |
|  From SBIR.gov:                                                   |
|    SBIR awards:      3 total                                      |
|      1. Air Force | Compact DE for Maritime UAS    | Phase I      |
|      2. DARPA     | High-Power RF Source           | Completed    |
|      3. Navy      | Shipboard Power Conditioning   | Phase I      |
|                                                                   |
|  From USASpending.gov:                                            |
|    Federal awards:   $2.4M total (5 transactions)                 |
|    Business types:   Small Business, For-Profit                   |
|                                                                   |
|  Not found in any API:                                            |
|    - Security clearance level                                     |
|    - ITAR registration status                                     |
|    - Key personnel details                                        |
|    - Capabilities/expertise keywords                              |
|    - Research institution partners                                |
|                                                                   |
+-------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Curious ("what did it find?")
- Exit: Impressed and slightly surprised ("it found a Navy award I forgot about!")

**Integration Checkpoint**: Enrichment result structured as a dict mapping profile schema fields to {value, source, confidence}. Fields not found tracked explicitly for interview fallback.

---

## Step 4: Review Enriched Data with Source Attribution

**Command**: Agent presents enriched data field-by-field for confirmation.

```
+-- Review Enriched Data -------------------------------------------+
|                                                                   |
|  Please confirm or correct each field.                            |
|  Source shown for transparency -- these came from official APIs.   |
|                                                                   |
|  Company name: "Radiant Defense Systems, LLC"                     |
|    Source: SAM.gov                                                 |
|    [confirm] [edit] [skip]                                        |
|                                                                   |
|  CAGE code: "7X2K9"                                               |
|    Source: SAM.gov                                                 |
|    [confirm] [edit] [skip]                                        |
|                                                                   |
|  NAICS codes: 334511 (primary), 541715, 334220                    |
|    Source: SAM.gov                                                 |
|    [confirm] [edit] [skip]                                        |
|                                                                   |
|  SAM.gov registration: Active (expires 2027-01-15)                |
|    Source: SAM.gov                                                 |
|    [confirm] [edit] [skip]                                        |
|                                                                   |
|  Socioeconomic certifications: (none listed)                      |
|    Source: SAM.gov                                                 |
|    Note: If you have certifications pending or recently added,    |
|    you can enter them manually.                                   |
|    [confirm none] [enter manually]                                |
|                                                                   |
|  Past performance (3 found):                                      |
|    1. Air Force | Compact DE for Maritime UAS    | Phase I        |
|    2. DARPA     | High-Power RF Source           | Completed      |
|    3. Navy      | Shipboard Power Conditioning   | Phase I        |
|    Source: SBIR.gov                                                |
|    [confirm all] [edit] [add more] [remove entry]                 |
|                                                                   |
|  Federal award history: $2.4M across 5 transactions               |
|    Source: USASpending.gov                                         |
|    (informational -- not stored in profile, used for context)     |
|                                                                   |
+-------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Reviewing with attention ("let me check these")
- Exit: Confident ("the data looks right, and I can see where it came from")

**Integration Checkpoint**: Each confirmed field marked as accepted. Edited fields retain user's value with source changed to "user (overriding {api_name})". Skipped fields remain empty for interview. Source attribution preserved in profile metadata.

---

## Step 5: Merge into Profile Draft

**Command**: System merges confirmed enrichment data into profile draft.

```
+-- Enrichment Applied ---------------------------------------------+
|                                                                   |
|  Profile draft updated with enriched data:                        |
|                                                                   |
|  Populated from APIs:                                             |
|    company_name            (SAM.gov)                              |
|    certifications.sam_gov  (SAM.gov)                              |
|    certifications.cage     (SAM.gov)                              |
|    naics_codes             (SAM.gov)                              |
|    past_performance (3)    (SBIR.gov)                             |
|                                                                   |
|  Still need (will ask in interview):                              |
|    capabilities                                                   |
|    security_clearance                                             |
|    itar_registered                                                |
|    employee_count                                                 |
|    key_personnel                                                  |
|    research_institution_partners                                  |
|                                                                   |
|  Continuing to interview for remaining fields...                  |
|                                                                   |
+-------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Ready to proceed
- Exit: Relieved ("half the profile is done, and I trust the data")

**Integration Checkpoint**: Profile draft contains mix of enriched (API-sourced) and pending (interview-needed) fields. Draft feeds into existing Step 3 (INTERVIEW) of the profile builder journey, which now asks only about gaps.

---

## Error Paths

### Error 1: SAM.gov API Key Invalid or Expired

```
+-- API Key Error --------------------------------------------------+
|                                                                   |
|  SAM.gov API key validation failed.                               |
|                                                                   |
|  Response: "403 Forbidden - Invalid API key"                      |
|                                                                   |
|  This can happen if:                                              |
|    - The key was mistyped                                         |
|    - The key has expired or been revoked                          |
|                                                                   |
|  Options:                                                         |
|    1. Re-enter your SAM.gov API key                               |
|    2. Generate a new key at https://sam.gov/profile/details       |
|    3. Skip SAM.gov enrichment (SBIR.gov and USASpending           |
|       still work without a key)                                   |
|    4. Skip all enrichment -- I'll ask everything manually         |
|                                                                   |
+-------------------------------------------------------------------+
```

### Error 2: SAM.gov Returns No Entity for UEI

```
+-- Entity Not Found -----------------------------------------------+
|                                                                   |
|  No entity found in SAM.gov for UEI "XYZABC123456"               |
|                                                                   |
|  This can happen if:                                              |
|    - The UEI was mistyped (check for transposed characters)       |
|    - The entity registration is expired or inactive               |
|    - The entity was registered under a different UEI              |
|                                                                   |
|  Options:                                                         |
|    1. Re-enter your UEI                                           |
|    2. Look up your UEI at https://sam.gov/search                  |
|    3. Skip enrichment -- I'll ask everything manually             |
|                                                                   |
+-------------------------------------------------------------------+
```

### Error 3: API Timeout or Unavailability (Partial Enrichment)

```
+-- Partial Enrichment ---------------------------------------------+
|                                                                   |
|  Enrichment completed with partial results:                       |
|                                                                   |
|    SAM.gov Entity API         [################] done             |
|    SBIR.gov Awards API        [XXXX] timed out after 10s          |
|    USASpending.gov            [################] done             |
|                                                                   |
|  SAM.gov and USASpending data is available.                       |
|  SBIR.gov award history could not be retrieved.                   |
|                                                                   |
|  Options:                                                         |
|    1. Continue with partial data (I'll ask about awards manually) |
|    2. Retry SBIR.gov                                              |
|    3. Skip enrichment entirely                                    |
|                                                                   |
+-------------------------------------------------------------------+
```

### Error 4: SBIR.gov Company Name Mismatch

```
+-- Ambiguous Match ------------------------------------------------+
|                                                                   |
|  SBIR.gov returned 3 companies matching "Radiant Defense":        |
|                                                                   |
|    1. Radiant Defense Systems, LLC (Huntsville, AL) -- 3 awards   |
|    2. Radiant Defense Technologies (San Diego, CA) -- 1 award     |
|    3. Radiant Defense Corp (Arlington, VA) -- 7 awards            |
|                                                                   |
|  Which is your company? (1/2/3/none)                              |
|                                                                   |
+-------------------------------------------------------------------+
```

### Error 5: Enrichment Data Conflicts with Existing Profile (Update Flow)

```
+-- Data Differences Found -----------------------------------------+
|                                                                   |
|  Enrichment found differences from your current profile:          |
|                                                                   |
|  CAGE code:                                                       |
|    Current profile: 7X2K9                                         |
|    SAM.gov says:    7X2K9  (match)                                |
|                                                                   |
|  NAICS codes:                                                     |
|    Current profile: 334511, 541715                                |
|    SAM.gov says:    334511, 541715, 334220  (new: 334220)         |
|                                                                   |
|  Past performance:                                                |
|    Current profile: 2 entries                                     |
|    SBIR.gov says:   3 entries (new: Navy Shipboard Power)         |
|                                                                   |
|  For each difference, choose:                                     |
|    [keep current] [accept API] [merge both]                       |
|                                                                   |
+-------------------------------------------------------------------+
```
