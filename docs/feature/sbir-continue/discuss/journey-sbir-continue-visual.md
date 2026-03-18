# Journey Visual: sbir-continue

## Journey Overview

```
/sbir:continue
      |
      v
+-- DETECT STATE --+
|                   |
| Read:             |
|   profile?        |
|   proposal-state? |
|   corpus?         |
|   wave status?    |
+-------------------+
      |
      +----------+----------+-----------+-----------+-----------+
      |          |          |           |           |           |
      v          v          v           v           v           v
  [NO SETUP] [PARTIAL  [NO         [MID-WAVE] [BETWEEN   [POST-
              SETUP]    PROPOSAL]              WAVES]     SUBMIT]
      |          |          |           |           |           |
      v          v          v           v           v           v
  Route to   Resume     Route to    Show        Celebrate  Guide to
  /sbir:     setup at   /sbir:      within-     + start    debrief
  setup      first gap  proposal    wave tasks  next wave  or new
                        new         remaining              proposal
      |          |          |           |           |           |
      v          v          v           v           v           v
  Feels:     Feels:     Feels:      Feels:      Feels:     Feels:
  Welcomed   Remembered Guided      In control  Accomplished  Closure
```

## Emotional Arc

```
Confidence
    ^
    |                                              *  (Accomplished)
    |                                           *
    |                                  *  *  *     (In control)
    |                        *  *  *
    |               *  *  *                         (Oriented)
    |         *  *
    |    *                                          (Welcomed/Guided)
    | *                                             (Uncertain)
    +-------------------------------------------------> Journey
      Type      Read     Understand   Act on
      command   output   position     suggestion
```

**Start**: Uncertain -- "Where was I? What should I do?"
**Middle**: Oriented and informed -- "I see where I am and what is next."
**End**: Confident and moving -- "I know what to do and I am doing it."

---

## Step 1: No Setup (First-Time User)

Phil Santos installs the SBIR plugin and types `/sbir:continue` before any setup.

```
+-- /sbir:continue ------------------------------------------+
|                                                             |
|  SBIR Proposal Plugin                                       |
|  =====================                                      |
|                                                             |
|  No configuration detected. Let's get you set up.           |
|                                                             |
|  The setup wizard will:                                     |
|    - Check prerequisites (Python, Git)                      |
|    - Create your company profile                            |
|    - Optionally ingest past proposals                       |
|    - Configure API keys                                     |
|                                                             |
|  Estimated time: 10-15 minutes                              |
|                                                             |
|  Run:  /sbir:setup                                          |
|                                                             |
+-------------------------------------------------------------+
```

**Emotional state**: Uncertain -> Welcomed
**Shared artifacts**: None yet
**Error paths**: None -- always produces output

---

## Step 2: Partial Setup (Returning After Incomplete Setup)

Phil ran `/sbir:setup` last week, created a profile, but quit before adding corpus.

```
+-- /sbir:continue ------------------------------------------+
|                                                             |
|  SBIR Proposal Plugin                                       |
|  =====================                                      |
|                                                             |
|  Setup Status:                                              |
|    [ok] Prerequisites (Python 3.12.4, Git 2.44.0)           |
|    [ok] Company profile (Pacific Systems Engineering)       |
|    [--] Corpus (no documents indexed)                       |
|    [--] GEMINI_API_KEY (not configured)                     |
|                                                             |
|  Setup is usable but incomplete.                            |
|                                                             |
|  Options:                                                   |
|    (c) continue setup   -- resume from corpus step          |
|    (s) skip to proposal -- start a proposal now             |
|    (q) quit                                                 |
|                                                             |
+-------------------------------------------------------------+
```

**Emotional state**: Uncertain -> Remembered ("it knows what I did")
**Shared artifacts**: `~/.sbir/company-profile.json` (profile data), `.sbir/corpus/` (empty)
**Error paths**: Corrupt profile -> route to setup with explanation

---

## Step 3: No Proposal (Setup Complete, No Active Proposal)

Phil has a complete setup but has not started a proposal.

```
+-- /sbir:continue ------------------------------------------+
|                                                             |
|  SBIR Proposal Plugin                                       |
|  =====================                                      |
|                                                             |
|  Profile: Pacific Systems Engineering                       |
|  Corpus:  12 documents indexed                              |
|                                                             |
|  No active proposal found.                                  |
|                                                             |
|  Ready to start:                                            |
|    /sbir:solicitation find              -- discover topics  |
|    /sbir:proposal new <solicitation>    -- start a proposal |
|                                                             |
+-------------------------------------------------------------+
```

**Emotional state**: Oriented -> Guided
**Shared artifacts**: `~/.sbir/company-profile.json`, `.sbir/corpus/`
**Error paths**: None -- clean state

---

## Step 4: Mid-Wave (Partway Through a Wave)

Phil is in Wave 1. Compliance matrix is generated, TPOC questions are pending, strategy brief not started.

```
+-- /sbir:continue ------------------------------------------+
|                                                             |
|  SBIR Proposal: AF243-001                                   |
|  Compact Directed Energy for Maritime UAS Defense           |
|  =====================================================      |
|  Wave 1: Requirements & Strategy                            |
|  Deadline: 2026-04-15 (28 days)                             |
|                                                             |
|  Wave 1 Progress:                                           |
|    [ok] Compliance matrix (24 items extracted)              |
|    [..] TPOC questions generated -- PENDING CALL            |
|    [  ] Strategy brief                                      |
|                                                             |
|  TPOC call is optional. You can proceed without it.         |
|                                                             |
|  Suggested next action:                                     |
|    /sbir:proposal wave strategy                             |
|    Generate strategy brief (TPOC data will be marked        |
|    as pending if call has not happened)                      |
|                                                             |
+-------------------------------------------------------------+
```

**Emotional state**: Uncertain -> In control
**Shared artifacts**: `.sbir/proposal-state.json` (wave status, TPOC status, compliance count), `./artifacts/wave-1-strategy/compliance-matrix.md`
**Error paths**: Corrupted state -> PES session checker handles; continue reports gracefully

---

## Step 5: Between Waves (Gate Approved, Next Wave Not Started)

Phil approved the Wave 1 strategy alignment checkpoint. Wave 2 has not started.

```
+-- /sbir:continue ------------------------------------------+
|                                                             |
|  SBIR Proposal: AF243-001                                   |
|  Compact Directed Energy for Maritime UAS Defense           |
|  =====================================================      |
|  Deadline: 2026-04-15 (25 days)                             |
|                                                             |
|  Wave Progress:                                             |
|    [x] Wave 0 -- Intelligence & Fit                         |
|    [x] Wave 1 -- Requirements & Strategy                    |
|    [ ] Wave 2 -- Research                      <-- YOU ARE  |
|    [ ] Wave 3 -- Discrimination & Outline          HERE     |
|    ...                                                      |
|                                                             |
|  Wave 1 completed. Strategy brief approved.                 |
|                                                             |
|  Next: Wave 2 -- Research                                   |
|    Deep dive into technical landscape, prior art,           |
|    and competitive analysis.                                |
|                                                             |
|  Suggested next action:                                     |
|    /sbir:proposal wave research                             |
|                                                             |
+-------------------------------------------------------------+
```

**Emotional state**: Accomplished -> Excited about next phase
**Shared artifacts**: `.sbir/proposal-state.json` (current_wave, waves.1.status=completed, waves.2.status=not_started)
**Error paths**: Wave completed but gate not approved (PES inconsistency) -> surface warning

---

## Step 6: Wave 4 Mid-Draft (Multiple Volumes)

Phil is in Wave 4. Technical volume approved, management volume in review, cost volume not started.

```
+-- /sbir:continue ------------------------------------------+
|                                                             |
|  SBIR Proposal: AF243-001                                   |
|  Compact Directed Energy for Maritime UAS Defense           |
|  =====================================================      |
|  Wave 4: Drafting                                           |
|  Deadline: 2026-04-15 (18 days)      Format: docx          |
|                                                             |
|  Volume Progress:                                           |
|    [ok] Technical volume (approved)                         |
|    [..] Management volume (in review -- 2 open items)       |
|    [  ] Cost volume (not started)                           |
|                                                             |
|  Suggested next action:                                     |
|    /sbir:proposal iterate management                        |
|    Address 2 open review items on management volume         |
|                                                             |
|  After management review:                                   |
|    /sbir:proposal draft cost                                |
|                                                             |
+-------------------------------------------------------------+
```

**Emotional state**: Focused -> In control (clear path to wave completion)
**Shared artifacts**: `.sbir/proposal-state.json` (volumes.technical.status, volumes.management.status, volumes.cost.status, open_review_items)

---

## Step 7: Post-Submission (Wave 8 Complete)

Phil confirmed submission. Wave 9 (debrief) not started.

```
+-- /sbir:continue ------------------------------------------+
|                                                             |
|  SBIR Proposal: AF243-001                                   |
|  Compact Directed Energy for Maritime UAS Defense           |
|  =====================================================      |
|                                                             |
|  Proposal submitted.                                        |
|                                                             |
|  Wave Progress:                                             |
|    [x] Wave 0-8 -- Complete                                 |
|    [ ] Wave 9 -- Post-Submission Debrief                    |
|                                                             |
|  When you receive evaluator feedback:                       |
|    /sbir:proposal debrief ingest <feedback-file>            |
|    Captures lessons learned and improves future proposals.  |
|                                                             |
|  Or start a new proposal:                                   |
|    /sbir:proposal new <solicitation>                        |
|                                                             |
+-------------------------------------------------------------+
```

**Emotional state**: Accomplished -> Closure with forward path
**Shared artifacts**: `.sbir/proposal-state.json` (waves.8.status=completed)

---

## Step 8: Fully Complete (Wave 9 Done)

Phil completed the debrief. Entire lifecycle is finished.

```
+-- /sbir:continue ------------------------------------------+
|                                                             |
|  SBIR Proposal: AF243-001                                   |
|  Compact Directed Energy for Maritime UAS Defense           |
|  =====================================================      |
|                                                             |
|  Proposal lifecycle complete.                               |
|  All 10 waves finished. Debrief archived.                   |
|                                                             |
|  Start a new proposal:                                      |
|    /sbir:solicitation find              -- discover topics  |
|    /sbir:proposal new <solicitation>    -- start fresh      |
|                                                             |
+-------------------------------------------------------------+
```

**Emotional state**: Satisfied -> Ready for next cycle
**Shared artifacts**: `.sbir/proposal-state.json` (all waves completed)

---

## Integration Checkpoints

| Checkpoint | Validates | Failure Behavior |
|------------|-----------|-----------------|
| Profile existence | `~/.sbir/company-profile.json` readable | Route to setup |
| Proposal state existence | `.sbir/proposal-state.json` readable | Route to proposal new or setup |
| State schema validity | JSON parses, schema_version compatible | PES session checker handles; continue reports error with what/why/do |
| Wave status consistency | current_wave matches waves.{N}.status | Surface warning, suggest `/proposal status` for details |
| Deadline proximity | topic.deadline vs current date | Surface warning at 7-day and 3-day thresholds |
| Async event status | tpoc.status, approach_selection.status | Note pending items but do not block suggestions |
