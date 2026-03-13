# Journey: Solicitation Finder -- Visual Map

## Journey Overview

```
[Trigger]          [Step 1]         [Step 2]          [Step 3]         [Step 4]          [Step 5]
New SBIR    -->  Invoke finder  --> Topics fetched --> Topics scored --> Review results --> Select topic
cycle opens      with filters       & pre-filtered     & ranked          & drill down       & begin proposal

Feels:           Feels:           Feels:            Feels:           Feels:             Feels:
Overwhelmed      Hopeful          Relieved          Impressed        Empowered          Momentum
(300+ topics)    (help is here)   (heavy lifting    (clear ranking   (informed           (decision flows
                                   done for me)      with reasons)    decision)           into action)
```

## Emotional Arc: Confidence Building

```
Confidence
    ^
    |                                                          * Step 5: Select
    |                                                     *         & proceed
    |                                               * Step 4: Review
    |                                          *         ranked results
    |                                 * Step 3: Scoring
    |                            *         complete
    |                   * Step 2: Topics
    |              *         fetched
    |     * Step 1: Command
    |*         invoked
    +-------------------------------------------------> Time
  Overwhelmed  Hopeful   Relieved  Impressed  Empowered  Momentum
```

---

## Step 1: Invoke Finder

**Command**: `/sbir:solicitation find`

**Emotional state**: Overwhelmed -> Hopeful

Phil opens his terminal knowing a new solicitation cycle has 347 topics. Instead of opening a browser, he types a single command.

```
+-- Step 1: Invoke Finder --------------------------------------------+
|                                                                      |
|  $ /sbir:solicitation find                                           |
|                                                                      |
|  Solicitation Finder                                                 |
|  Company: Radiant Defense Systems, LLC                               |
|  Profile: ~/.sbir/company-profile.json (loaded, 12 capabilities)     |
|                                                                      |
|  Fetching open topics from DoD SBIR/STTR...                          |
|  [============================] 347 topics retrieved                 |
|                                                                      |
+----------------------------------------------------------------------+
```

With filters:

```
+-- Step 1: Invoke Finder (filtered) ---------------------------------+
|                                                                      |
|  $ /sbir:solicitation find --agency "Air Force" --phase I            |
|                                                                      |
|  Solicitation Finder                                                 |
|  Company: Radiant Defense Systems, LLC                               |
|  Profile: ~/.sbir/company-profile.json (loaded, 12 capabilities)     |
|  Filters: agency=Air Force, phase=I                                  |
|                                                                      |
|  Fetching open topics from DoD SBIR/STTR...                          |
|  [============================] 89 topics retrieved (filtered)       |
|                                                                      |
+----------------------------------------------------------------------+
```

### Error: No company profile

```
+-- Step 1: Error -- No Profile ---------------------------------------+
|                                                                      |
|  $ /sbir:solicitation find                                           |
|                                                                      |
|  Error: No company profile found at ~/.sbir/company-profile.json     |
|                                                                      |
|  The solicitation finder matches topics against your company's       |
|  capabilities, certifications, and past performance. A profile       |
|  is required for accurate scoring.                                   |
|                                                                      |
|  Try:                                                                |
|    1. Create your profile:  /sbir:proposal profile setup             |
|    2. Or provide a file:    /sbir:solicitation find --file baa.pdf   |
|       (scoring will run without profile, accuracy degraded)          |
|                                                                      |
+----------------------------------------------------------------------+
```

### Error: API unavailable, automatic fallback

```
+-- Step 1: API Fallback ---------------------------------------------+
|                                                                      |
|  $ /sbir:solicitation find                                           |
|                                                                      |
|  Solicitation Finder                                                 |
|  Company: Radiant Defense Systems, LLC                               |
|                                                                      |
|  Fetching open topics from DoD SBIR/STTR...                          |
|  Warning: DSIP API unavailable (connection timeout)                  |
|                                                                      |
|  Provide a BAA PDF to continue:                                      |
|    /sbir:solicitation find --file ./solicitations/baa-2026-3.pdf     |
|                                                                      |
|  Download the BAA from:                                              |
|    https://www.dodsbirsttr.mil/topics-app/                           |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Step 2: Topics Fetched and Pre-Filtered

**Emotional state**: Hopeful -> Relieved

The heavy lifting of browsing 347 topics is replaced by a progress indicator showing keyword pre-filtering.

```
+-- Step 2: Pre-Filter ------------------------------------------------+
|                                                                      |
|  Pre-filtering 347 topics against company capabilities...            |
|  [====================] 347/347                                      |
|                                                                      |
|  Keyword match: 42 candidate topics (305 eliminated)                 |
|  Downloading topic details for candidates...                         |
|  [====================] 42/42 topic PDFs retrieved                   |
|                                                                      |
|  Scoring 42 candidates against company profile...                    |
|  [=========           ] 18/42  Scoring topic A263-105...             |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Step 3: Topics Scored and Ranked

**Emotional state**: Relieved -> Impressed

Scoring complete. The ranked table appears, showing clear recommendations.

```
+-- Step 3: Scored Results --------------------------------------------+
|                                                                      |
|  === Solicitation Finder Results ===                                 |
|  Company: Radiant Defense Systems, LLC                               |
|  Source: DoD SBIR 2026.3 (347 topics parsed, 42 candidates scored)   |
|  Date: 2026-03-15                                                    |
|                                                                      |
|  Rank | Topic ID    | Agency    | Title                    | Score  |
|  -----|-------------|-----------|--------------------------|--------|
|    1  | AF263-042   | Air Force | Compact DE for C-UAS     | 0.82   |
|    2  | N263-018    | Navy      | Shipboard RF Power Mgmt  | 0.71   |
|    3  | A263-105    | Army      | Thermal Mgmt Mobile DE   | 0.65   |
|    4  | HR001126-01 | DARPA     | Next-Gen Power Electrncs | 0.52   |
|    5  | N263-044    | Navy      | Undersea Sensor Networks | 0.34   |
|                                                                      |
|  Rank | Rec      | Deadline   | Flags                              |
|  -----|----------|------------|------------------------------------|
|    1  | GO       | 2026-05-15 |                                    |
|    2  | GO       | 2026-05-15 |                                    |
|    3  | GO       | 2026-05-15 |                                    |
|    4  | EVALUATE | 2026-04-30 | Low past performance               |
|    5  | EVALUATE | 2026-05-15 | Low SME match                      |
|                                                                      |
|  --- Disqualified (3 topics) ---                                     |
|    -  | AF263-099   | Air Force | Classified Avionics Test | NO-GO  |
|       | Reason: Requires TS clearance (profile: Secret)               |
|    -  | A263-200    | Army      | Biodefense Rapid Diag    | NO-GO  |
|       | Reason: No SME match (0.08 composite)                         |
|    -  | N263-S05    | Navy      | AI for Sonar (STTR)      | NO-GO  |
|       | Reason: No research institution partner                       |
|                                                                      |
|  Results saved to .sbir/finder-results.json                          |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Step 4: Review and Drill Down

**Emotional state**: Impressed -> Empowered

Phil drills into a specific topic to see the full scoring breakdown before making a decision.

```
+-- Step 4: Topic Detail ---------------------------------------------+
|                                                                      |
|  details AF263-042                                                   |
|                                                                      |
|  === AF263-042: Compact Directed Energy for C-UAS ===                |
|  Agency: Air Force | Phase: I | Deadline: 2026-05-15 (61 days)      |
|  Program: SBIR | Solicitation: DOD_SBIR_2026_P1_C3                   |
|                                                                      |
|  Scoring Breakdown:                                                  |
|    Subject Matter Expertise:  0.95  (core competency match)          |
|    Past Performance:          0.80  (AF Phase I win, DE domain)      |
|    Certifications:            1.00  (SAM active, Secret clearance)   |
|    Phase Eligibility:         1.00  (Phase I, 15 employees)          |
|    STTR Institution:          1.00  (SBIR -- not required)           |
|    ------------------------------------------------                  |
|    Composite Score:           0.82  --> Recommendation: GO           |
|                                                                      |
|  Rationale:                                                          |
|    Core competency in directed energy aligns with topic focus on     |
|    compact DE systems for counter-UAS. Prior Air Force Phase I win   |
|    in related DE domain. All certifications and eligibility met.     |
|                                                                      |
|  Key Personnel Match:                                                |
|    Dr. Elena Vasquez -- directed energy systems, laser physics       |
|    Marcus Chen -- RF power systems, thermal management               |
|                                                                      |
|  Actions:                                                            |
|    pursue AF263-042    Start proposal for this topic                 |
|    back                Return to results list                        |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Step 5: Select Topic and Begin Proposal

**Emotional state**: Empowered -> Momentum

Phil selects a topic. The system confirms and transitions to the proposal workflow.

```
+-- Step 5: Topic Selection ------------------------------------------+
|                                                                      |
|  pursue AF263-042                                                    |
|                                                                      |
|  Selected: AF263-042 -- Compact Directed Energy for C-UAS            |
|  Agency: Air Force | Phase I | Deadline: 2026-05-15 (61 days)       |
|  Composite Score: 0.82 | Recommendation: GO                         |
|                                                                      |
|  Proceed to create proposal? (y/n): y                                |
|                                                                      |
|  Starting /sbir:proposal new with topic AF263-042...                 |
|  Topic data pre-loaded from finder results.                          |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Error Paths

### No matching topics found

```
+-- Error: No Matches ------------------------------------------------+
|                                                                      |
|  === Solicitation Finder Results ===                                 |
|  Company: Radiant Defense Systems, LLC                               |
|  Source: DoD SBIR 2026.3 (347 topics parsed, 0 candidates scored)    |
|                                                                      |
|  No topics matched your company profile.                             |
|                                                                      |
|  This may indicate:                                                  |
|    1. Company capabilities are too narrow for this cycle             |
|       Review profile: /sbir:proposal profile show                    |
|    2. Filters are too restrictive                                    |
|       Try broader search: /sbir:solicitation find (no filters)       |
|    3. This cycle does not align with your domain                     |
|       Check next cycle: typically 3-4 months                         |
|                                                                      |
+----------------------------------------------------------------------+
```

### Expired topics in results

```
+-- Warning: Expired Topics ------------------------------------------+
|                                                                      |
|  Warning: 2 topics in results have passed their deadline.            |
|  These are shown for reference but cannot be pursued.                |
|                                                                      |
|    AF263-042  | Deadline: 2026-03-01 (EXPIRED 14 days ago)           |
|    N263-018   | Deadline: 2026-03-10 (EXPIRED 5 days ago)            |
|                                                                      |
+----------------------------------------------------------------------+
```

### API rate limiting

```
+-- Warning: Rate Limited --------------------------------------------+
|                                                                      |
|  Warning: DSIP API rate limit reached after 200 topics.              |
|  Partial results available (200 of 347 topics fetched).              |
|                                                                      |
|  Options:                                                            |
|    1. Score partial results now (200 topics)                         |
|    2. Wait and retry in 5 minutes                                    |
|    3. Provide BAA PDF: /sbir:solicitation find --file baa.pdf        |
|                                                                      |
+----------------------------------------------------------------------+
```
