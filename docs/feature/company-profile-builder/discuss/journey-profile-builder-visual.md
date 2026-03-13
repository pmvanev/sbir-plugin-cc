# Journey Visual: Company Profile Builder

## Journey Overview

```
[Trigger]              [Step 1]           [Step 2]            [Step 3]           [Step 4]           [Step 5]
Plugin warns           Start profile      Gather from         Interview for      Preview &          Confirm &
"no profile"           builder            documents           remaining gaps     validate           save
     |                    |                   |                    |                  |                  |
  Feels:               Feels:              Feels:              Feels:             Feels:             Feels:
  Frustrated,          Guided,             Productive,         Engaged,           Confident,         Relieved,
  blocked              hopeful             "it's reading       "almost done"      in control         accomplished
                                           my docs!"
     |                    |                   |                    |                  |                  |
  Artifacts:           Artifacts:          Artifacts:          Artifacts:         Artifacts:         Artifacts:
  (none)               profile_draft{}     extracted_data{}    complete_draft{}   validated_json{}   ~/.sbir/
                                                                                                    company-
                                                                                                    profile.json
```

**Emotional Arc Pattern**: Confidence Building
- Start: Frustrated/blocked (scoring degraded, unfamiliar schema)
- Middle: Productive/engaged (documents extracted, questions are clear)
- End: Confident/relieved (validated profile saved, ready to score topics)

---

## Step 1: Start Profile Builder

**Command**: `/sbir:proposal profile setup`
**Trigger**: User runs command directly, or is prompted after "Company profile not found" warning from topic scout.

```
+-- Profile Setup ---------------------------------------------------+
|                                                                     |
|  Company Profile Builder                                            |
|                                                                     |
|  This will create your company profile at:                          |
|  ~/.sbir/company-profile.json                                       |
|                                                                     |
|  Your profile powers fit scoring -- it tells the topic scout        |
|  about your capabilities, certifications, personnel, and past       |
|  performance so it can match you to the right solicitations.        |
|                                                                     |
|  I can work from:                                                   |
|    1. Your existing documents (capability statement, SAM.gov, etc.) |
|    2. A conversational interview (I'll ask questions)               |
|    3. Both -- documents first, then fill gaps with questions        |
|                                                                     |
|  Which approach works best for you?                                 |
|                                                                     |
+---------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Frustrated (scoring degraded) or curious (first-time setup)
- Exit: Hopeful -- the path forward is clear and feels manageable

**Integration Checkpoint**: Verify `~/.sbir/` directory exists or can be created.

---

## Step 2: Gather from Documents (Optional)

**Command**: Conversational -- user provides file paths or URLs when prompted.

```
+-- Document Extraction ---------------------------------------------+
|                                                                     |
|  Great, let's start with your documents.                            |
|                                                                     |
|  Share any of these and I'll extract what I can:                    |
|  - Capability statement (PDF, Word, or text)                        |
|  - SAM.gov entity page URL                                          |
|  - Past proposal cover pages or summaries                           |
|  - Team bios or org chart                                           |
|                                                                     |
|  (Just paste file paths or URLs -- I'll read them)                  |
|                                                                     |
+---------------------------------------------------------------------+

  User: Here's our cap statement: ./docs/radiant-cap-statement.pdf

+-- Extraction Results ----------------------------------------------+
|                                                                     |
|  From radiant-cap-statement.pdf I found:                            |
|                                                                     |
|  Company name:    Radiant Defense Systems, LLC                      |
|  Capabilities:    directed energy, RF systems, power electronics,   |
|                   thermal management, embedded firmware              |
|  Employee count:  23                                                |
|  Key personnel:                                                     |
|    - Rafael Medina, CEO/Chief Engineer                              |
|      Expertise: directed energy, RF power amplifiers                |
|    - Dr. Lena Park, VP Engineering                                  |
|      Expertise: thermal management, power electronics               |
|  Past performance:                                                  |
|    - Air Force Phase I: "Compact DE for Maritime UAS" (awarded)     |
|    - DARPA: "High-Power RF Source" (completed)                      |
|                                                                     |
|  Not found in document:                                             |
|    - SAM.gov registration details (CAGE code, UEI)                  |
|    - Socioeconomic certifications                                   |
|    - Security clearance level                                       |
|    - ITAR registration status                                       |
|    - Research institution partners                                  |
|                                                                     |
|  I'll ask about the missing fields next.                            |
|                                                                     |
+---------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Hopeful but slightly skeptical ("will it get this right?")
- Exit: Impressed/productive -- "it pulled most of the data from my PDF"

**Integration Checkpoint**: Extracted data stored in working draft. Missing fields tracked for Step 3.

---

## Step 3: Interview for Remaining Gaps

**Command**: Conversational -- agent asks targeted questions for missing fields only.

```
+-- Filling Gaps ----------------------------------------------------+
|                                                                     |
|  A few things I couldn't find in your documents.                    |
|                                                                     |
|  SAM.gov Registration:                                              |
|  Is your SAM.gov registration active?                               |
|                                                                     |
|  User: Yes, CAGE code is 7X2K9, UEI is DKJF84NXLE73               |
|                                                                     |
|  Got it. Socioeconomic certifications -- do you hold any of these?  |
|  - 8(a)                                                             |
|  - HUBZone                                                          |
|  - WOSB (Women-Owned Small Business)                                |
|  - SDVOSB (Service-Disabled Veteran-Owned)                          |
|  - None of the above                                                |
|                                                                     |
|  User: None currently, we're applying for 8(a) but don't have it   |
|                                                                     |
|  Noted -- I'll leave socioeconomic empty for now. You can update    |
|  it later with /sbir:proposal profile update.                       |
|                                                                     |
|  Security clearance -- what's the highest level your facility       |
|  holds?                                                             |
|  - None                                                             |
|  - Confidential                                                     |
|  - Secret                                                           |
|  - Top Secret                                                       |
|                                                                     |
|  User: Secret                                                       |
|                                                                     |
|  ITAR registration -- is your company registered with DDTC?         |
|                                                                     |
|  User: Yes                                                          |
|                                                                     |
|  Research institution partners -- do you have formal partnerships   |
|  with any universities or research labs? This matters for STTR      |
|  topics.                                                            |
|                                                                     |
|  User: We have an MOU with Georgia Tech Research Institute          |
|                                                                     |
+---------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Engaged -- questions are specific, not redundant
- Exit: Almost done -- "just a few more and we're there"

**Integration Checkpoint**: All schema fields now have values or explicit "not applicable" markers.

---

## Step 4: Preview and Validate

**Command**: Agent presents complete profile for review.

```
+-- Profile Preview -------------------------------------------------+
|                                                                     |
|  Here's your complete company profile:                              |
|                                                                     |
|  Company:          Radiant Defense Systems, LLC                     |
|  Employees:        23                                               |
|                                                                     |
|  Capabilities:                                                      |
|    directed energy, RF systems, power electronics,                  |
|    thermal management, embedded firmware                             |
|                                                                     |
|  Certifications:                                                    |
|    SAM.gov:        Active (CAGE: 7X2K9, UEI: DKJF84NXLE73)        |
|    Socioeconomic:  (none)                                           |
|    Clearance:      Secret                                           |
|    ITAR:           Registered                                       |
|                                                                     |
|  Key Personnel:                                                     |
|    1. Rafael Medina -- CEO/Chief Engineer                           |
|       [directed energy, RF power amplifiers]                        |
|    2. Dr. Lena Park -- VP Engineering                               |
|       [thermal management, power electronics]                       |
|                                                                     |
|  Past Performance:                                                  |
|    1. Air Force | Compact DE for Maritime UAS | awarded             |
|    2. DARPA     | High-Power RF Source        | completed            |
|                                                                     |
|  Research Partners:                                                 |
|    1. Georgia Tech Research Institute                               |
|                                                                     |
|  Validation: PASSED (all required fields present)                   |
|                                                                     |
|  Does this look correct? (yes / edit / cancel)                      |
|                                                                     |
+---------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Expectant -- "let me see the result"
- Exit: Confident -- "that's accurate, save it"

**Integration Checkpoint**: Schema validation passes. All required fields present. Data types correct (employee_count is number, arrays are arrays, booleans are booleans).

---

## Step 5: Confirm and Save

**Command**: Agent writes file after user confirms.

```
+-- Profile Saved ---------------------------------------------------+
|                                                                     |
|  Company profile saved to:                                          |
|  ~/.sbir/company-profile.json                                       |
|                                                                     |
|  Your fit scoring is now fully operational.                         |
|  Run /sbir:proposal new to evaluate a solicitation.                 |
|                                                                     |
|  To update your profile later:                                      |
|  /sbir:proposal profile update                                      |
|                                                                     |
+---------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Ready to commit
- Exit: Relieved and accomplished -- setup is done, ready to do real work

**Integration Checkpoint**: File written to `~/.sbir/company-profile.json`. File is valid JSON. Schema matches what `sbir-topic-scout` expects in Phase 3 SCORE.

---

## Error Paths

### Error 1: Document Cannot Be Read

```
+-- Error -----------------------------------------------------------+
|                                                                     |
|  I couldn't read ./docs/cap-statement.docx                          |
|                                                                     |
|  The file format (.docx) isn't supported for direct reading.        |
|                                                                     |
|  Try:                                                               |
|    1. Export to PDF and share the PDF path                          |
|    2. Copy the text content to a .txt file                          |
|    3. Skip document extraction -- I'll ask all questions instead    |
|                                                                     |
+---------------------------------------------------------------------+
```

### Error 2: Existing Profile Would Be Overwritten

```
+-- Warning ---------------------------------------------------------+
|                                                                     |
|  An existing company profile was found at:                          |
|  ~/.sbir/company-profile.json                                       |
|                                                                     |
|  Company: Radiant Defense Systems, LLC                              |
|  Last modified: 2026-01-15                                          |
|                                                                     |
|  Options:                                                           |
|    1. Start fresh (backs up existing to company-profile.json.bak)   |
|    2. Update existing profile (keep current data, fill gaps)        |
|    3. Cancel                                                        |
|                                                                     |
+---------------------------------------------------------------------+
```

### Error 3: Validation Failure

```
+-- Validation Issues -----------------------------------------------+
|                                                                     |
|  2 issues found before saving:                                      |
|                                                                     |
|  [!] CAGE code "7X2K" is 4 characters (expected 5)                  |
|  [!] Employee count 0 seems incorrect -- SBIR requires > 0         |
|                                                                     |
|  Fix these before saving? (yes / save anyway / cancel)              |
|                                                                     |
+---------------------------------------------------------------------+
```

### Error 4: File System Permission Error

```
+-- Error -----------------------------------------------------------+
|                                                                     |
|  Cannot write to ~/.sbir/company-profile.json                       |
|                                                                     |
|  Permission denied on directory: ~/.sbir/                           |
|                                                                     |
|  Try:                                                               |
|    1. Check directory permissions: ls -la ~/.sbir/                  |
|    2. Create the directory: mkdir -p ~/.sbir                        |
|    3. Save to a different location with --output flag               |
|                                                                     |
+---------------------------------------------------------------------+
```
