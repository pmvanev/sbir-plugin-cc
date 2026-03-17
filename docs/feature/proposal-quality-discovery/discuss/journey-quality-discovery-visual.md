# Journey: Proposal Quality Discovery -- Visual Map

## Journey Overview

```
TRIGGER                    DISCOVERY FLOW                              CONSUMPTION
  |                              |                                        |
  v                              v                                        v
[First setup]    [Step 1]    [Step 2]     [Step 3]     [Step 4]      [Step 5-7]
   or         -> Past      -> Writing  -> Evaluator -> Artifact   -> Downstream
[Post-cycle]     Proposal     Style       Feedback     Assembly      Agent
  update         Review       Interview   Extraction                 Consumption
                   |             |            |            |              |
Feels:          anxious->     engaged->   reflective-> satisfied->  confident
                curious       expressive  analytical   accomplished  (compounding)
```

## Emotional Arc

```
Confidence
    ^
    |                                                    ****  (Step 5-7)
    |                                             ****         confident
    |                                       ****
    |                                 ****                     (Step 4)
    |                           ****                           accomplished
    |                     ****
    |               ****                                       (Step 3)
    |         ****                                             reflective
    |   ****
    |***                                                       (Step 2)
    |*                                                         engaged
    |
    +---------------------------------------------------------> Time
    ^                                                          ^
    |                                                          |
  anxious/uncertain                                     confident/empowered
  "will this be worth                                   "every proposal
   the time?"                                            gets better"
```

## Step 1: Past Proposal Quality Review

**Trigger**: User runs setup for the first time OR updates quality profile after a proposal cycle.

**Context**: Company has past_performance entries in company-profile.json. Some may already have outcome tags. The system needs to ask about writing quality specifically.

```
+-- Quality Discovery: Past Proposal Review ---------------------------------+
|                                                                             |
|  Your profile shows 5 past proposals. Let's review their writing quality.   |
|                                                                             |
|  Proposal 1 of 5: AF243-001 (Air Force, Directed Energy)                   |
|  Outcome: WIN                                                               |
|                                                                             |
|  How strong was this proposal's writing quality?                            |
|    (1) Weak -- won despite writing, not because of it                       |
|    (2) Adequate -- met the bar but nothing stood out                        |
|    (3) Strong -- writing was a clear discriminator                          |
|    (s) Skip -- I don't remember enough to judge                             |
|                                                                             |
|  > 3                                                                        |
|                                                                             |
|  What made the writing strong? (or press Enter to skip)                     |
|  > Led with quantitative results in every section. Short paragraphs.        |
|    Used evaluator language from the solicitation throughout.                 |
|                                                                             |
|  Any specific evaluator praise about writing? (or press Enter to skip)      |
|  > "Clearly organized approach with measurable milestones"                  |
|                                                                             |
|  [1/5 reviewed] Next: N244-012 (Navy, Autonomous UUV)                      |
|  (n) next  (f) finish early  (q) quit                                       |
+-----------------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Anxious/uncertain ("is this worth the time?")
- Exit: Curious/engaged ("I can see patterns already")

**Integration Checkpoint**: Past performance entries from company-profile.json are matched by topic_id. Quality ratings are new data added alongside existing outcome field.

---

## Step 2: Writing Style Interview

**Trigger**: Follows past proposal review OR invoked independently.

```
+-- Quality Discovery: Writing Style Preferences -----------------------------+
|                                                                             |
|  Let's capture how you want proposals to sound.                             |
|  This takes about 5 minutes. Your answers inform every future draft.        |
|                                                                             |
|  TONE                                                                       |
|  How should your proposals read?                                            |
|    (1) Formal and authoritative ("The proposed approach leverages...")       |
|    (2) Direct and data-driven ("This approach reduces latency by 40%")      |
|    (3) Conversational and accessible ("We solve this by...")                |
|    (4) Let me describe it                                                   |
|                                                                             |
|  > 2                                                                        |
|                                                                             |
|  DETAIL LEVEL                                                               |
|  When explaining technical approaches, how deep should the writing go?      |
|    (1) High-level summaries -- evaluators want the big picture              |
|    (2) Moderate detail -- enough to show competence, not overwhelm          |
|    (3) Deep technical detail -- our evaluators are domain experts           |
|                                                                             |
|  > 3                                                                        |
|                                                                             |
|  EVIDENCE STYLE                                                             |
|  How do you prefer to cite evidence?                                        |
|    (1) Inline quantitative ("achieving 95% accuracy, ref: Chen 2025")       |
|    (2) Narrative with supporting data ("Our tests showed promising...")      |
|    (3) Table-heavy with metrics comparisons                                 |
|                                                                             |
|  > 1                                                                        |
|                                                                             |
|  ORGANIZATION                                                               |
|  What paragraph style works for your proposals?                             |
|    (1) Short paragraphs (2-3 sentences), many subheadings                   |
|    (2) Medium paragraphs (4-6 sentences), section-level headings            |
|    (3) Longer flowing paragraphs with fewer breaks                          |
|                                                                             |
|  > 1                                                                        |
|                                                                             |
|  PRACTICES TO REPLICATE                                                     |
|  Any writing practices you always want in your proposals?                   |
|  (Enter each one, blank line when done)                                     |
|  > Always lead with the result, then cite the evidence                      |
|  > Define every acronym even if obvious                                     |
|  > Use evaluator language from solicitation in our response                  |
|  >                                                                          |
|                                                                             |
|  PRACTICES TO AVOID                                                         |
|  Any writing patterns you want to eliminate?                                |
|  (Enter each one, blank line when done)                                     |
|  > "Our team has extensive experience" without specifics                     |
|  > Passive voice chains                                                     |
|  > Starting paragraphs with "It is important to note that"                  |
|  >                                                                          |
|                                                                             |
|  [Style preferences captured]                                               |
|  (r) review summary  (e) edit answers  (c) continue                         |
+-----------------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Engaged ("I have opinions about this")
- Exit: Expressive/satisfied ("the system now knows how I write")

**Integration Checkpoint**: Responses map to structured quality-preferences artifact. Tone selection maps to writing_style field in proposal-state.json.

---

## Step 3: Evaluator Feedback Extraction

**Trigger**: User has debrief documents or can recall evaluator comments about writing quality.

```
+-- Quality Discovery: Evaluator Feedback on Writing Quality -----------------+
|                                                                             |
|  Have you received evaluator feedback that commented on writing quality?     |
|  (Comments about clarity, organization, readability -- not just technical    |
|   content.)                                                                 |
|                                                                             |
|    (y) Yes -- I have debriefs or remember specific comments                 |
|    (n) No / Skip -- I'll add this later                                     |
|                                                                             |
|  > y                                                                        |
|                                                                             |
|  Enter evaluator comments about writing quality.                            |
|  For each, I'll ask which proposal it was about.                            |
|  (blank line when done)                                                     |
|                                                                             |
|  Comment: "Technical approach was difficult to follow"                       |
|  Proposal: AF243-002 (loss)                                                 |
|  Category:                                                                  |
|    [auto-detected: ORGANIZATION/CLARITY]                                    |
|                                                                             |
|  Comment: "Commercialization plan lacked specific market evidence"           |
|  Proposal: AF243-002 (loss)                                                 |
|  Category:                                                                  |
|    [auto-detected: CONTENT -- not meta-writing, tracked separately]         |
|                                                                             |
|  Comment: "Well-organized approach with clear milestones"                    |
|  Proposal: AF243-001 (win)                                                  |
|  Category:                                                                  |
|    [auto-detected: ORGANIZATION/CLARITY -- POSITIVE]                        |
|                                                                             |
|  Comment:                                                                   |
|  >                                                                          |
|                                                                             |
|  Summary of writing quality feedback:                                       |
|    Positive: 1 comment (organization/clarity)                               |
|    Negative: 1 comment (organization/clarity)                               |
|    Content-only: 1 comment (tracked in weakness profile, not here)          |
|                                                                             |
|  Pattern detected: Organization/clarity appears in both wins and losses.    |
|  Your wins had clear structure; your loss did not. This is actionable.      |
|                                                                             |
|  (c) continue  (a) add more comments  (q) quit                             |
+-----------------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Reflective ("I remember that feedback stung")
- Exit: Analytical/empowered ("now I see the pattern")

**Integration Checkpoint**: Auto-categorization separates meta-writing feedback from content feedback. Content feedback routes to existing weakness profile (win-loss-analyzer). Writing quality feedback routes to new writing-quality-profile artifact.

---

## Step 4: Artifact Assembly

**Trigger**: Follows completion of Steps 1-3 (or whichever steps the user completed).

```
+-- Quality Discovery: Artifacts Created -------------------------------------+
|                                                                             |
|  Quality discovery complete. Created 3 artifacts:                           |
|                                                                             |
|  [ok] ~/.sbir/quality-preferences.json                                      |
|       Tone: direct and data-driven                                          |
|       Detail: deep technical                                                |
|       Evidence: inline quantitative                                         |
|       Organization: short paragraphs, many subheadings                      |
|       Practices to replicate: 3 items                                       |
|       Practices to avoid: 3 items                                           |
|                                                                             |
|  [ok] ~/.sbir/winning-patterns.json                                         |
|       Patterns from 3 winning proposals                                     |
|       Top pattern: "quantitative results leading each section"              |
|       Confidence: medium (3 wins analyzed)                                  |
|                                                                             |
|  [ok] ~/.sbir/writing-quality-profile.json                                  |
|       Writing feedback entries: 2                                           |
|       Agencies with feedback: Air Force                                     |
|       Key insight: organization/clarity is a discriminator                  |
|                                                                             |
|  These artifacts will be read by:                                           |
|    - Strategist (Wave 1) -- winning patterns inform strategy brief          |
|    - Writer (Waves 3-4) -- preferences and patterns guide drafting          |
|    - Reviewer (Waves 4,7) -- quality profile informs review criteria        |
|                                                                             |
|  Update anytime with: /sbir:proposal quality update                         |
+-----------------------------------------------------------------------------+
```

**Emotional State**:
- Entry: Anticipation ("what did the system learn?")
- Exit: Accomplished ("my knowledge is now institutional knowledge")

**Integration Checkpoint**: All three artifacts written to ~/.sbir/ (company-level, not per-proposal). File paths registered in shared artifact registry.

---

## Step 5: Strategist Consumption (Downstream)

**When**: Wave 1 strategy brief generation.

```
+-- Strategy Brief: Quality Intelligence Integrated --------------------------+
|                                                                             |
|  [info] Quality playbook loaded from ~/.sbir/                               |
|         Winning patterns: 5 patterns (medium confidence)                    |
|         Writing preferences: direct/data-driven style                       |
|                                                                             |
|  COMPETITIVE POSITIONING (informed by quality intelligence):                |
|  - Prior wins used quantitative TRL evidence (winning pattern #1)           |
|  - Prior evaluators praised clear milestone structures (pattern #3)         |
|  - Recommend: emphasize measurable deliverables over qualitative claims     |
+-----------------------------------------------------------------------------+
```

---

## Step 6: Writer Consumption (Downstream)

**When**: Waves 3-4 drafting.

```
+-- Writer: Quality-Informed Drafting ----------------------------------------+
|                                                                             |
|  [info] Quality preferences loaded:                                         |
|         Style: direct/data-driven | Detail: deep technical                  |
|         Organization: short paragraphs, many subheadings                    |
|                                                                             |
|  [info] Winning patterns loaded (3 applicable):                             |
|         - Lead with quantitative results                                    |
|         - Use evaluator language from solicitation                           |
|         - Explicit TRL entry/exit criteria                                  |
|                                                                             |
|  [warn] Writing quality alert:                                              |
|         Past Air Force evaluators noted "difficult to follow" in            |
|         technical approach sections. Ensure clear subheading structure.      |
|                                                                             |
|  Drafting Technical Approach section...                                     |
+-----------------------------------------------------------------------------+
```

---

## Step 7: Reviewer Consumption (Downstream)

**When**: Waves 4, 7 review.

```
+-- Reviewer: Quality Profile Check ------------------------------------------+
|                                                                             |
|  [info] Writing quality profile loaded:                                     |
|         Known writing weaknesses: organization/clarity (2 occurrences)      |
|                                                                             |
|  Section Review: Technical Approach                                         |
|  ...                                                                        |
|  Finding 3: [QUALITY PROFILE MATCH]                                         |
|    Location: Section 3.1, paragraphs 2-4                                   |
|    Severity: high                                                           |
|    Issue: Three consecutive paragraphs exceed 6 sentences.                  |
|           Quality profile notes past evaluator feedback:                    |
|           "Technical approach was difficult to follow" (AF243-002).         |
|    Suggestion: Break into shorter paragraphs with descriptive subheadings.  |
+-----------------------------------------------------------------------------+
```

---

## Error Paths

### E1: No Past Proposals Available
User has no past_performance entries in company profile.

```
+-- Quality Discovery ---------------------------------------------------------+
|                                                                             |
|  No past proposals found in your company profile.                           |
|                                                                             |
|  You can still capture writing style preferences.                           |
|  Past proposal review and evaluator feedback will be available              |
|  after you add proposals to your profile or corpus.                         |
|                                                                             |
|  (s) Start with style preferences only                                      |
|  (q) Skip quality discovery entirely                                        |
+-----------------------------------------------------------------------------+
```

### E2: User Wants to Skip and Return Later

```
+-- Quality Discovery ---------------------------------------------------------+
|                                                                             |
|  Quality discovery skipped. No artifacts created.                           |
|                                                                             |
|  You can run quality discovery anytime with:                                |
|    /sbir:proposal quality discover                                          |
|                                                                             |
|  Without quality artifacts, the writer will use default style               |
|  (elements-of-style) and the reviewer will use standard criteria only.      |
+-----------------------------------------------------------------------------+
```

### E3: Stale Winning Patterns

```
+-- Quality Discovery: Pattern Freshness Warning -----------------------------+
|                                                                             |
|  [!!] 2 winning patterns are from proposals over 2 years old:              |
|       - "Use CONOPS diagrams in every section" (Navy, 2023)                 |
|       - "Budget tables in landscape format" (DARPA, 2023)                   |
|                                                                             |
|  Agency preferences may have shifted. Review and confirm:                   |
|    (k) Keep all patterns                                                    |
|    (r) Review each stale pattern individually                               |
|    (d) Drop stale patterns                                                  |
+-----------------------------------------------------------------------------+
```

### E4: Cancel During Discovery

```
+-- Quality Discovery: Cancelled ---------------------------------------------+
|                                                                             |
|  Quality discovery cancelled. No files were written or modified.            |
|                                                                             |
|  Resume anytime with: /sbir:proposal quality discover                       |
+-----------------------------------------------------------------------------+
```
