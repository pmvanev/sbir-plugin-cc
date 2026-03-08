# Journey: SBIR Proposal Lifecycle -- Visual Map

## Persona

Phil Santos -- small business engineer, 2-3 proposals/year, 10-15 hours each, CLI-native.

## Emotional Arc

```
Confidence
    ^
    |                                                          *** Confident
    |                                              ***  Relief (submitted)
    |                                   *** Focused
    |                        *** Engaged (drafting flow)
    |             *** Oriented
    |   *** Grounded (I know what they want)
    | * Curious (new solicitation)
    +-----------------------------------------------------------> Time
   Step 0    1       2       3       4      5-6     7      8-9
   Entry  Strategy Research Outline Draft  Format  Review  Submit
```

Start: Curious but uncertain ("Is this worth pursuing?")
Middle: Grounded and engaged ("I know what they want; I am building it")
End: Confident and relieved ("It is complete, compliant, and submitted")

Peak tension: Wave 4 (Drafting) -- most hours, most cognitive load, highest stakes for narrative quality.

---

## Full Lifecycle Flow

```
 ============================================================================
  PHASE C1 (MVP) -- Walking Skeleton
 ============================================================================

 STEP 0: Entry & Reorientation
 ──────────────────────────────
 Trigger: New solicitation found OR returning to existing proposal
 Commands: /proposal new  |  /proposal status

 Two entry paths:
   Path A (New):     /proposal new  -->  guided setup wizard
   Path B (Resume):  /proposal status  -->  see where you left off

 +-- /proposal status -----------------------------------------------+
 |                                                                    |
 |  PROPOSAL STATUS -- AF243-001                                      |
 |  "Compact Directed Energy for Maritime UAS Defense"                |
 |  Wave 1: Requirements & Strategy | 18 days to deadline             |
 |                                                                    |
 |  Progress:                                                         |
 |    Wave 0  Intelligence & Fit     [completed] Go: approved         |
 |    Wave 1  Requirements & Strategy [active]                        |
 |      > Compliance matrix generated (47 items)                      |
 |      > TPOC questions generated (23 questions) -- PENDING CALL     |
 |      > Strategy brief: not started                                 |
 |    Wave 2  Research               [not started]                    |
 |    ...                                                             |
 |                                                                    |
 |  Next action: Have TPOC call, then /proposal tpoc ingest           |
 |  Or: /proposal wave strategy to continue strategy work             |
 |                                                                    |
 +--------------------------------------------------------------------+

 Emotion: Curious -> Oriented
 "I know exactly where I am and what to do next."

 ──────────────────────────────────────────────────────────────────────

 STEP 1: Intelligence & Fit (Wave 0)
 ────────────────────────────────────
 Jobs: J1 (Find relevant past work)
 Commands: /proposal new  |  /proposal corpus add <directory>

 +-- /proposal new ---------------------------------------------------+
 |                                                                    |
 |  NEW PROPOSAL PROJECT                                              |
 |                                                                    |
 |  Solicitation URL or file path:                                    |
 |  > https://www.sbir.gov/node/12345                                 |
 |                                                                    |
 |  Parsing solicitation...                                           |
 |    Topic: AF243-001                                                |
 |    Agency: Air Force                                               |
 |    Phase: I                                                        |
 |    Deadline: 2026-04-15 (38 days)                                  |
 |    Title: "Compact Directed Energy for Maritime UAS Defense"       |
 |                                                                    |
 |  Checking corpus for relevant past work...                         |
 |    Found 2 related proposals:                                      |
 |      1. AF241-087 (2024) -- Directed Energy Countermeasures        |
 |         Relevance: 0.87 | Outcome: Not selected                   |
 |      2. N222-038 (2023) -- Maritime Sensor Integration             |
 |         Relevance: 0.62 | Outcome: Awarded                        |
 |                                                                    |
 |  Scoring company fit...                                            |
 |    Subject matter match:    HIGH (2 prior proposals)               |
 |    Past performance:        MEDIUM (1 award, different agency)     |
 |    Certifications:          OK (SAM.gov active)                    |
 |    Phase I eligibility:     OK (no prior award on this topic)      |
 |                                                                    |
 |  ┌─────────────────────────────────────────────────────────┐       |
 |  │ RECOMMENDATION: GO                                      │       |
 |  │ Strong technical fit. Prior directed energy work.       │       |
 |  │ Note: AF241-087 was not selected -- review debrief.     │       |
 |  └─────────────────────────────────────────────────────────┘       |
 |                                                                    |
 |  CHECKPOINT: Go/No-Go Decision                                    |
 |    (g) go     -- proceed to requirements & strategy                |
 |    (n) no-go  -- archive and exit                                  |
 |    (d) defer  -- save for later review                             |
 |  >                                                                 |
 +--------------------------------------------------------------------+

 Emotion: Curious -> Grounded
 "I have data to support this decision, not just gut feel."

 Shared Artifacts Created:
   ${topic_id}           = "AF243-001"           <- proposal-state.json
   ${agency}             = "Air Force"            <- proposal-state.json
   ${deadline}           = "2026-04-15"           <- proposal-state.json
   ${go_no_go}           = "go"                   <- proposal-state.json
   ${corpus_matches}     = [AF241-087, N222-038]  <- proposal-state.json

 ──────────────────────────────────────────────────────────────────────

 STEP 2: Requirements & Strategy (Wave 1)
 ─────────────────────────────────────────
 Jobs: J2 (Track compliance), J4 (Understand real need)
 Commands: /proposal wave strategy
           /proposal compliance check
           /proposal tpoc questions
           /proposal tpoc ingest

 Sub-step 2a: Compliance Matrix Generation

 +-- /proposal wave strategy -----------------------------------------+
 |                                                                    |
 |  WAVE 1: REQUIREMENTS & STRATEGY                                   |
 |  Topic: AF243-001 | 36 days to deadline                            |
 |                                                                    |
 |  Parsing solicitation for requirements...                          |
 |                                                                    |
 |  COMPLIANCE MATRIX (47 items extracted)                             |
 |  ┌────┬──────────────────────────────────────┬──────────┬────────┐ |
 |  │ #  │ Requirement                          │ Section  │ Status │ |
 |  ├────┼──────────────────────────────────────┼──────────┼────────┤ |
 |  │  1 │ Technical approach shall describe    │ Sec 3    │ --     │ |
 |  │    │ feasibility of proposed concept      │          │        │ |
 |  │  2 │ Proposal shall not exceed 20 pages   │ All      │ --     │ |
 |  │  3 │ Font shall be Times New Roman 12pt   │ Format   │ --     │ |
 |  │  4 │ Phase I shall demonstrate prototype  │ Sec 3    │ --     │ |
 |  │  5 │ SOW shall include milestones with    │ SOW      │ --     │ |
 |  │    │ specific deliverables                │          │        │ |
 |  │ ...│ (42 more items)                      │          │        │ |
 |  └────┴──────────────────────────────────────┴──────────┴────────┘ |
 |                                                                    |
 |  3 ambiguities flagged:                                            |
 |    ! #12: "relevant environment" -- define what qualifies          |
 |    ! #27: "appropriate integration" -- scope unclear               |
 |    ! #41: "sufficient detail" -- subjective threshold              |
 |                                                                    |
 |  Matrix written to: ./artifacts/wave-1-strategy/compliance-matrix.md|
 |  Edit manually or run /proposal compliance check to refresh.       |
 |                                                                    |
 +--------------------------------------------------------------------+

 Emotion: Uncertain -> Grounded
 "I can see every requirement. Nothing is hidden."

 Sub-step 2b: TPOC Question Generation

 +-- /proposal tpoc questions ----------------------------------------+
 |                                                                    |
 |  TPOC QUESTION LIST (23 questions generated)                        |
 |                                                                    |
 |  Priority A -- Ask First:                                          |
 |    1. [scope-clarification] Does "compact" imply a specific        |
 |       SWaP-C envelope, or is this open to the proposer?            |
 |    2. [approach-validation] We plan a solid-state laser approach.   |
 |       Is the program open to non-laser DE alternatives?            |
 |    3. [incumbent-landscape] Have prior Phase I awards on this      |
 |       topic progressed to Phase II?                                |
 |                                                                    |
 |  Priority B -- If Time Permits:                                    |
 |    4. [transition-pathway] Is there a program of record for        |
 |       maritime UAS defense DE systems?                              |
 |    5. [budget-signal] Is the $250K Phase I budget firm or          |
 |       flexible for larger demonstrations?                          |
 |    ...                                                             |
 |                                                                    |
 |  Questions written to:                                             |
 |    ./artifacts/wave-1-strategy/tpoc-questions.md                   |
 |                                                                    |
 |  Edit before your call. After the call:                            |
 |    /proposal tpoc ingest                                           |
 |                                                                    |
 +--------------------------------------------------------------------+

 Note: TPOC call is an ASYNC external event.
 State: tpoc_questions = "generated" | tpoc_call = "pending"
 The tool shows this pending state on every /proposal status until resolved.
 "Questions generated but call never happened" is a valid terminal state.

 Sub-step 2c: TPOC Answer Ingestion (days later)

 +-- /proposal tpoc ingest -------------------------------------------+
 |                                                                    |
 |  TPOC ANSWER INGESTION                                              |
 |                                                                    |
 |  Enter answers inline or provide a file path:                      |
 |  > ./notes/tpoc-call-2026-03-15.txt                                |
 |                                                                    |
 |  Parsing answers...                                                |
 |  Matched 18/23 questions to answers.                               |
 |  5 questions unanswered (marked as such).                          |
 |                                                                    |
 |  SOLICITATION DELTA ANALYSIS                                        |
 |  ┌──────────────────────────────────────────────────────────────┐  |
 |  │ TPOC said "compact" means < 50 lbs total system weight.     │  |
 |  │   -> Compliance item #12 clarified: "relevant environment"  │  |
 |  │      = shipboard maritime, salt spray, vibration             │  |
 |  │                                                              │  |
 |  │ TPOC confirmed no prior Phase II on this topic.             │  |
 |  │   -> Competitive landscape: open field                       │  |
 |  │                                                              │  |
 |  │ TPOC indicated strong interest in Phase III transition       │  |
 |  │ to PMS 501 (Surface Ship Weapons).                          │  |
 |  │   -> Update commercialization strategy                       │  |
 |  └──────────────────────────────────────────────────────────────┘  |
 |                                                                    |
 |  Compliance matrix updated with TPOC clarifications.               |
 |  Delta written to:                                                 |
 |    ./artifacts/wave-1-strategy/solicitation-delta.md                |
 |                                                                    |
 +--------------------------------------------------------------------+

 Emotion: Grounded -> Confident
 "Now I know what they REALLY want, not just what the solicitation says."

 Sub-step 2d: Strategy Alignment Checkpoint

 +-- CHECKPOINT: Strategy Alignment -----------------------------------+
 |                                                                    |
 |  STRATEGY BRIEF SUMMARY                                             |
 |  ┌──────────────────────────────────────────────────────────────┐  |
 |  │ Technical approach: Solid-state laser, < 50 lbs (TPOC)      │  |
 |  │ TRL entry: 3 (lab demo) -> Target: 5 (relevant environment) │  |
 |  │ Teaming: Solo (no STTR RI needed for Phase I)               │  |
 |  │ Phase III: PMS 501 Surface Ship Weapons (TPOC confirmed)    │  |
 |  │ Budget: $250K standard Phase I                               │  |
 |  │ Compliance: 47 items, 3 clarified via TPOC                  │  |
 |  │ Key risk: No prior Phase II on topic = unproven transition   │  |
 |  └──────────────────────────────────────────────────────────────┘  |
 |                                                                    |
 |  Review: ./artifacts/wave-1-strategy/strategy-brief.md             |
 |                                                                    |
 |    (a) approve -- proceed to research                              |
 |    (r) revise  -- provide feedback                                 |
 |    (s) skip    -- defer and continue                               |
 |  >                                                                 |
 +--------------------------------------------------------------------+

 ============================================================================
  END PHASE C1 (MVP) -- Walking Skeleton
  Below: Phase C2 and C3 journeys (deferred implementation)
 ============================================================================


 STEP 3: Research (Wave 2) [Phase C2]
 ─────────────────────────────────────
 Jobs: J8 (Commercializability argument)
 Commands: /proposal wave research

 - Technical landscape: state of art, prior art, patent scan
 - Market research: TAM/SAM/SOM, commercialization pathway
 - Prior award analysis from USASpending.gov and SBIR.gov
 - TRL assessment with evidence

 +-- CHECKPOINT: Research Review ------------------------------------+
 |  Technical landscape, market research, TRL assessment presented.   |
 |  Human validates direction before outline work begins.             |
 +--------------------------------------------------------------------+

 Emotion: Engaged -> Informed
 "I have the evidence base to write from."


 STEP 4: Discrimination & Outline (Wave 3) [Phase C2]
 ─────────────────────────────────────────────────────
 Jobs: J5 (Competitive advantage)
 Commands: /proposal wave outline
           /proposal iterate discrimination

 - Build discrimination table: company vs. competitors vs. prior art
 - Draft proposal outline with page budgets and thesis statements
 - Generate PDCs (/proposal:distill) before drafting

 +-- CHECKPOINT: Discrimination Table + Outline Approval ------------+
 |  Discrimination table reviewed. Outline with page budgets          |
 |  and section thesis statements approved.                           |
 +--------------------------------------------------------------------+

 Emotion: Informed -> Focused
 "I know exactly what argument I am making in every section."


 STEP 5: Drafting (Wave 4) [Phase C2]
 ─────────────────────────────────────
 Jobs: J3 (Trustworthy technical narrative)
 Commands: /proposal draft <section>
           /proposal:check <section>
           /proposal iterate <section>

 The PDC-driven loop:
   /proposal:distill [section]  ->  PDCs generated, human approves
   /proposal:draft [section]    ->  Agent drafts against PDCs
   /proposal:check [section]    ->  Tier 1+2 PDCs evaluated -> RED items listed
   /proposal iterate [section]  ->  Agent targets red items
   ... repeat until GREEN ...
   /proposal review [section]   ->  Human reviews + Tier 3 persona output

 +-- /proposal:check section-3 --------------------------------------+
 |                                                                    |
 |  PDC CHECK: Section 3 -- Technical Approach                         |
 |                                                                    |
 |  Tier 1 (Mechanical):                                              |
 |    [PASS] Page count: 14/15                                        |
 |    [PASS] TRL stated: "TRL 3 -> TRL 5"                            |
 |    [FAIL] Acronym "SWaP-C" used without definition                |
 |    [PASS] All figures referenced exist                             |
 |                                                                    |
 |  Tier 2 (Rubric):                                                  |
 |    [PASS] Responds to topic objective statement                    |
 |    [PASS] Novelty differentiated from 2 prior approaches           |
 |    [FAIL] Phase II pathway uses generic language                   |
 |    [PASS] TPOC requirement (< 50 lbs) addressed                   |
 |                                                                    |
 |  Summary: 10/12 GREEN | 2 RED                                      |
 |  Run /proposal iterate section-3 to target red items.              |
 |                                                                    |
 +--------------------------------------------------------------------+

 +-- Confidence Flagging (during draft) ------------------------------+
 |                                                                    |
 |  "The proposed solid-state laser achieves beam quality of          |
 |   M-squared < 1.5 at the target range."                            |
 |                                                                    |
 |  [CONFIDENCE: LOW] This claim is not supported by any document     |
 |  in the corpus. Source needed or claim should be qualified.         |
 |                                                                    |
 +--------------------------------------------------------------------+

 Emotion: Focused -> Engaged (flow state during iterate loop)
 Peak tension here -- most cognitive effort, but PDC framework provides structure.


 STEP 6: Visual Assets + Formatting (Waves 5-6) [Phase C3]
 ──────────────────────────────────────────────────────────
 Jobs: J6 (Format and assemble)
 Commands: /proposal wave visuals
           /proposal format

 - Generate figures (SVG, Mermaid, external tools)
 - Apply document formatting per solicitation
 - Assemble all volumes into required file structure
 - Final compliance matrix check

 Emotion: Engaged -> Relieved
 "Formatting is handled. I am not counting orphans."


 STEP 7: Final Review (Wave 7) [Phase C3]
 ─────────────────────────────────────────
 Commands: /proposal wave final-review

 - Reviewer persona simulation (government technical evaluator)
 - Red team review (strongest objections)
 - Final compliance check
 - Human sign-off

 Emotion: Cautious -> Confident
 "A simulated reviewer found no fatal flaws."


 STEP 8: Submission (Wave 8) [Phase C3]
 ──────────────────────────────────────
 Commands: /proposal submit prep
           /proposal submit

 - Portal-specific packaging
 - Submission confirmation and archiving
 - Immutable snapshot

 Emotion: Anxious -> Relieved
 "It is submitted. I have a confirmation and an archive."


 STEP 9: Post-Submission & Learning (Wave 9) [Phase C3]
 ───────────────────────────────────────────────────────
 Jobs: J7 (Learn from win/loss patterns)
 Commands: /proposal debrief ingest <path>

 - Debrief ingestion and parsing
 - Win/loss pattern update
 - Corpus enrichment

 Emotion: Reflective -> Hopeful
 "Every proposal makes the next one better."

---

## Error Paths

### E1: Solicitation Parse Failure
Trigger: URL is invalid, solicitation format is unexpected, or content is behind a login wall.
Recovery: "Could not parse solicitation at this URL. Try downloading the PDF and providing a local file path: /proposal new --file ./solicitation.pdf"

### E2: Corpus Is Empty
Trigger: First-time use, no documents ingested yet.
Recovery: Tool proceeds without corpus matches. "No corpus documents found. Add past proposals with: /proposal corpus add <directory>. The tool works without a corpus but improves with one."

### E3: TPOC Call Never Happens
Trigger: Questions generated but tpoc_call remains "pending" for weeks.
Recovery: Status shows "TPOC questions pending -- no call recorded." User can: (a) ingest answers when ready, (b) mark as "no call" and proceed with solicitation text only, (c) leave pending indefinitely.

### E4: Compliance Item Missed by Parser
Trigger: User finds a requirement the parser did not extract.
Recovery: Manual addition to compliance matrix. "Add requirement: /proposal compliance add 'Section 3 shall include risk mitigation table'" -- matrix is always human-editable.

### E5: Deadline Pressure
Trigger: Critical days threshold reached.
Recovery: PES surfaces warning on every status check. At critical threshold, non-essential waves can be skipped with documented waiver.

### E6: Session Crash / State Corruption
Trigger: Claude Code session ends unexpectedly.
Recovery: PES session startup runs integrity check on proposal-state.json. Orphaned drafts reconciled. "State recovered from last saved checkpoint."
