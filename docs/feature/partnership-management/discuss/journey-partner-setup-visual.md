# Journey: Partner Profile Setup

## Overview

Build a partner profile through conversational interview (mirroring `/proposal-profile-setup`), making partner capabilities available to all downstream agents.

## Persona

Phil Santos -- engineer, 2-3 SBIR proposals/year, works with CU Boulder, NDSU, SWRI. Primary user and plugin author.

## Emotional Arc

- **Start**: Purposeful but slightly apprehensive ("is this going to be tedious?")
- **Middle**: Engaged as fit scoring connections become clear ("this will actually help")
- **End**: Confident that the partner is now "visible" to the plugin ("now the AI can work with both of us")

---

## Flow Diagram

```
[Trigger]                [Phase 1]              [Phase 2]           [Phase 3]
/proposal partner-setup  MODE SELECT             RESEARCH            GATHER
        |                     |                     |                   |
        v                     v                     v                   v
  "Add a partner"     Detect existing        Web search for        Interview or
  Phil knows which    partners. Show         partner institution.  document mode.
  institution.        options: new/update/   Pre-populate from     Walk sections:
                      list.                  public data.          basics, capabilities,
        |                     |                     |               personnel, facilities,
  Feels: purposeful    Feels: oriented       Feels: impressed     past collabs.
  Sees: prompt         Sees: partner list    ("it found them!")        |
                             |                     |               Feels: engaged
                             v                     v               Sees: fit scoring
                       If new partner:       Carry findings        explanations
                       ask for name +        forward as draft.          |
                       type.                       |                   v
                             |                     |              [Phase 4]
                             +------->-------------+              PREVIEW
                                                                      |
                                                                      v
                                                                 Show complete
                                                                 profile. Edit/
                                                                 save/cancel.
                                                                      |
                                                                 Feels: in control
                                                                 Sees: side-by-side
                                                                 partner + company
                                                                      |
                                                                      v
                                                                 [Phase 5]
                                                                 VALIDATE & SAVE
                                                                      |
                                                                      v
                                                                 Schema validation.
                                                                 Atomic write to
                                                                 ~/.sbir/partners/
                                                                 {slug}.json
                                                                      |
                                                                 Feels: confident
                                                                 Sees: "Partner saved.
                                                                 Available for scoring
                                                                 and suggestions."
```

---

## Step Details

### Step 1: Trigger -- `/proposal partner-setup`

```
+-- Partner Setup -----------------------------------------------+
|                                                                 |
| > /proposal partner-setup                                       |
|                                                                 |
| SBIR Partnership Manager                                        |
| -----------------------------------------------                 |
|                                                                 |
| I'll help you set up a partner profile. This makes your         |
| partner's capabilities visible to all proposal agents --        |
| strategy, scoring, writing, and approach selection.             |
|                                                                 |
| Existing partners on file:                                      |
|   1. CU Boulder (university) -- last updated 2026-01-15        |
|   2. NDSU (university) -- last updated 2025-11-20              |
|                                                                 |
| Options:                                                        |
|   (n) new     -- add a new partner                              |
|   (u) update  -- update an existing partner                     |
|   (l) list    -- view partner details                           |
|   (c) cancel  -- exit                                           |
| -----------------------------------------------                 |
+----------------------------------------------------------------+
```

**Emotional state**: Oriented. User sees what exists and picks a clear next action.
**Shared artifacts**: `~/.sbir/partners/` directory listing.

### Step 2: Research -- Web Search for Partner

```
+-- Partner Research --------------------------------------------+
|                                                                 |
| Partner name: Southwest Research Institute (SWRI)               |
| Partner type: nonprofit_research                                |
|                                                                 |
| Searching...                                                    |
|   [1/3] "SWRI" SBIR STTR awards...                             |
|   [2/3] "SWRI" capabilities research areas...                   |
|   [3/3] "SWRI" key personnel division leadership...             |
|                                                                 |
| -----------------------------------------------                 |
| PARTNER RESEARCH RESULTS                                        |
| -----------------------------------------------                 |
|                                                                 |
| SBIR/STTR History: 200+ awards found (DoD, NASA, DoE)          |
| Research Areas:  intelligent systems, space science, defense    |
|                  technology, automotive engineering, chemistry   |
| Divisions:       Intelligent Systems, Space Science,            |
|                  Defense & Intel Solutions                       |
| Key Personnel:   Dr. Rebecca Chen (Dir, Intelligent Systems)    |
|                  Dr. James Hartwell (VP Research)                |
|                                                                 |
| Confidence: HIGH -- SWRI is well-documented                     |
| -----------------------------------------------                 |
|                                                                 |
| These findings will pre-populate the partner profile.           |
|   (c) continue -- proceed with these findings                   |
|   (d) discard  -- ignore research, start from scratch           |
|   (q) quit                                                      |
+----------------------------------------------------------------+
```

**Emotional state**: Impressed/validated. The plugin is doing useful work (not just asking questions).
**Shared artifacts**: Research findings carried forward as draft data.

### Step 3: Gather -- Partner Interview

```
+-- Partner Interview: SWRI ------------------------------------+
|                                                                 |
| SECTION 1 of 6: Partner Basics                                  |
| -----------------------------------------------                 |
|                                                                 |
| From research: "Southwest Research Institute"                   |
| Type: nonprofit_research                                        |
|                                                                 |
| Is this correct? (y/n/edit)                                     |
|                                                                 |
| SECTION 2 of 6: Capabilities                                    |
| -----------------------------------------------                 |
|                                                                 |
| Capabilities keywords are matched against solicitations         |
| alongside your company's keywords. The COMBINED keyword set     |
| determines partnership fit scoring.                             |
|                                                                 |
| From research:                                                  |
|   intelligent systems, space science, defense technology,       |
|   automotive engineering, chemistry                             |
|                                                                 |
| These look broad. Which are relevant to your partnership?       |
| Add/remove/refine as needed.                                    |
|                                                                 |
| > intelligent systems, autonomy, sensor fusion, applied ML      |
|                                                                 |
| SECTION 3 of 6: Key Personnel (partner-side)                    |
| -----------------------------------------------                 |
|                                                                 |
| Who at SWRI would be Co-PI or key personnel on proposals        |
| with you? For each person: name, role, expertise keywords.      |
|                                                                 |
| From research: Dr. Rebecca Chen, Dr. James Hartwell             |
|                                                                 |
| > Dr. Rebecca Chen, Co-PI, autonomous navigation, sensor fusion |
|                                                                 |
| SECTION 4 of 6: Facilities & Equipment                          |
| -----------------------------------------------                 |
|                                                                 |
| Evaluators value concrete facility descriptions. What           |
| equipment, labs, or testing facilities does SWRI bring?         |
|                                                                 |
| > 6-DOF motion simulation lab, RF anechoic chamber,            |
|   autonomous vehicle test track (200 acres)                     |
|                                                                 |
| SECTION 5 of 6: Past Collaborations                             |
| -----------------------------------------------                 |
|                                                                 |
| Have you worked with SWRI on prior proposals or contracts?      |
| Past collaborations strengthen the teaming narrative.           |
|                                                                 |
| > No prior proposals together. This is a new partnership.       |
|                                                                 |
| SECTION 6 of 6: STTR Eligibility                                |
| -----------------------------------------------                 |
|                                                                 |
| For STTR, the research institution performs >= 30% of Phase I   |
| work. Can SWRI commit to this level of involvement?             |
|                                                                 |
| > Yes, they would lead the simulation and testing tasks.        |
+----------------------------------------------------------------+
```

**Emotional state**: Engaged. Fit scoring explanations make each question feel purposeful.
**Shared artifacts**: Draft partner profile accumulating section by section.

### Step 4: Preview

```
+-- Partner Profile Preview -------------------------------------+
|                                                                 |
| PARTNER PROFILE: SWRI                                           |
| -----------------------------------------------                 |
|                                                                 |
| Name:          Southwest Research Institute                     |
| Type:          nonprofit_research                               |
| Capabilities:  intelligent systems, autonomy, sensor fusion,    |
|                applied ML                                       |
| Key Personnel: Dr. Rebecca Chen (Co-PI) -- autonomous nav,      |
|                sensor fusion                                    |
| Facilities:    6-DOF motion sim lab, RF anechoic chamber,       |
|                autonomous vehicle test track (200 acres)        |
| Past Collabs:  None (new partnership)                           |
| STTR Ready:    Yes (would lead simulation/testing)              |
|                                                                 |
| -----------------------------------------------                 |
| YOUR COMPANY + SWRI COMBINED PROFILE                            |
| -----------------------------------------------                 |
|                                                                 |
| Combined capabilities: directed energy, RF engineering,         |
|   machine learning (yours) + intelligent systems, autonomy,     |
|   sensor fusion, applied ML (SWRI)                              |
|                                                                 |
| Overlap: machine learning / applied ML (complementary)          |
| Unique to you: directed energy, RF engineering                  |
| Unique to SWRI: autonomy, sensor fusion                         |
|                                                                 |
| This combined profile will be used for partnership scoring      |
| and AI-assisted suggestions.                                    |
| -----------------------------------------------                 |
|                                                                 |
|   (s) save    -- validate and save                              |
|   (e) edit    -- modify a section                               |
|   (c) cancel  -- discard without saving                         |
+----------------------------------------------------------------+
```

**Emotional state**: Confident, in control. The combined profile preview shows immediate value.
**Shared artifacts**: Complete partner profile JSON ready for validation.

### Step 5: Validate and Save

```
+-- Partner Saved -----------------------------------------------+
|                                                                 |
| PARTNER PROFILE SAVED                                           |
| -----------------------------------------------                 |
|                                                                 |
| Location: ~/.sbir/partners/swri.json                            |
| Status:   Validated and saved                                   |
|                                                                 |
| SWRI is now available to:                                       |
|   - /solicitation-find  (partnership-aware scoring)             |
|   - /proposal-shape     (partner capability suggestions)        |
|   - /proposal-wave-strategy (teaming section generation)        |
|   - /proposal-draft     (partnership-aware content)             |
|                                                                 |
| Next steps:                                                     |
|   /proposal partner-setup  -- add another partner               |
|   /solicitation-find       -- scan topics with partnership fit   |
|   /proposal new            -- start a partnered proposal        |
+----------------------------------------------------------------+
```

**Emotional state**: Satisfied, anticipatory. The partner is "live" and the user knows exactly where it will be used.

---

## Error Paths

### E1: Web research finds nothing

```
Research for "Acme Research Lab" found no public data.
No problem -- we'll build the profile from scratch.
Proceeding to interview...
```

### E2: Partner profile already exists

```
SWRI profile already exists (last updated 2026-02-10).
  (u) update -- load and modify
  (f) fresh  -- start over (current backed up to .bak)
  (c) cancel
```

### E3: Validation failure

```
VALIDATION ERRORS
-------------------------------------------------
- capabilities: must have at least 1 keyword (currently empty)
- key_personnel: Co-PI missing expertise keywords

Fix these and save again, or cancel.
```

### E4: Cancel mid-interview

```
Partner profile creation cancelled. No files written or modified.
```
