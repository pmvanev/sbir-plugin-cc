# Journey: Writing Style Gate Enforcement

## Journey Flow

```
[Writer dispatched to Wave 4]
    |
    v
[Writer enters Phase 3: DRAFT]
    |
    +-- Is this first section draft? --NO--> [Style already confirmed, proceed]
    |
    YES
    |
    v
[Style Checkpoint: Present writing style options]
    |
    +-- quality-preferences.json at ~/.sbir/?
    |       |
    |       YES --> "Your quality profile suggests: tone={direct},
    |       |        evidence_style={inline}. Apply these? Or choose
    |       |        another style?"
    |       |
    |       NO --> "No quality profile found. Choose a writing style:
    |                Strunk & White | Academic | Conversational |
    |                Agency default | Skip style selection"
    |
    v
[User chooses: apply profile | adjust | choose new | skip]
    |
    +-- User chooses style --> writing_style set in proposal state
    |                          quality artifacts loaded
    |
    +-- User skips ----------> writing_style_selection_skipped = true
    |                          in proposal state
    v
[Writer attempts Write to wave-4-drafting/sections/]
    |
    +-- quality-preferences.json exists at ~/.sbir/
    |   OR writing_style_selection_skipped in state?
    |       |
    |       NO --> [PES BLOCKS]
    |              "Cannot write draft sections before style selection.
    |               Run quality discovery or skip style selection."
    |              Agent redirected to style checkpoint
    |       |
    |       YES -> [PES ALLOWS]
    |              Section drafting proceeds with style applied
    v
[Section drafted with intentional style]
```

## Emotional Arc

```
Start: Guided               Middle: Empowered            End: Confident
(style options presented)    (user makes choice)          (every section consistent)

Dr. Moreno:                  Dr. Moreno:                  Dr. Moreno:
"The system is asking me     "I chose Strunk & White      "Every section reads the way
 about writing style before   with my winning patterns.    I intended. Concise,
 drafting anything."          This is exactly what I       data-driven, consistent."
                              wanted last time."

Dr. Okafor:                  Dr. Okafor:                  Dr. Okafor:
"It's asking about style.    "I'll go with Standard       "The proposal reads
 I haven't thought about      for now -- I can always      professionally even though
 this before."                 refine later."               I'm new to this."

Phil:                        Phil:                        Phil:
"The checkpoint fires        "The PES gate also           "No more generic prose.
 before any drafting."        catches any bypass.          Both layers hold."
                              Belt and suspenders."
```

## Step-by-Step Detail

### Step 1: Writer Agent Dispatched to Wave 4

The orchestrator dispatches sbir-writer for Wave 4 drafting work. PES SubagentStart hook verifies the agent is authorized for Wave 4 (existing behavior).

```
+-- Wave 4: Proposal Drafting ------------------------------------+
|                                                                  |
| sbir-writer dispatched                                           |
| State: current_wave = 4                                          |
| Artifacts dir: artifacts/{topic-id}/wave-4-drafting/             |
|                                                                  |
+------------------------------------------------------------------+
```

**Emotional state**: Neutral. The user is ready to draft sections.

### Step 2: Style Checkpoint at Wave 4 Entry (Writer Agent)

Before drafting any section, the writer agent checks if writing style has been confirmed for this proposal. This is a mandatory checkpoint in the agent's Phase 3 workflow.

The agent reads:
- `~/.sbir/quality-preferences.json` (global quality profile, if exists)
- `~/.sbir/winning-patterns.json` (winning proposal patterns, if exists)
- `~/.sbir/writing-quality-profile.json` (evaluator feedback, if exists)
- `.sbir/proposals/{topic-id}/state.json` field `writing_style` (per-proposal choice)

If `writing_style` is already set in proposal state (from a previous Wave 4 session), the checkpoint is satisfied and drafting proceeds.

If not set, the agent presents a guided style discussion:

```
+-- Writing Style Selection --------------------------------------+
|                                                                  |
| Before drafting, let's confirm your writing style for this       |
| proposal.                                                        |
|                                                                  |
| Your quality profile (from quality discovery):                   |
|   Tone: direct                                                   |
|   Detail level: high                                             |
|   Evidence style: inline citations                               |
|   Practices to replicate: "Start with impact statement"          |
|                                                                  |
| Agency match (Air Force):                                        |
|   Winning patterns: 3 found, confidence: medium                  |
|   Quality alerts: "Technical approach clarity" (past feedback)   |
|                                                                  |
| Available writing styles:                                        |
|   1. Elements of Style (Strunk & White) -- concise, direct       |
|   2. Academic -- formal, detailed, citation-heavy                |
|   3. Conversational -- accessible, narrative-driven              |
|   4. Agency default -- style calibrated to Air Force norms       |
|   5. Custom -- define your own rules                             |
|   6. Skip style selection -- use standard prose defaults         |
|                                                                  |
| Your quality profile suggests: Elements of Style + winning       |
| patterns from Air Force proposals.                               |
|                                                                  |
| Choose [1-6] or describe your preference:                        |
|                                                                  |
+------------------------------------------------------------------+
```

If no quality profile exists (first-time user like Dr. Okafor):

```
+-- Writing Style Selection --------------------------------------+
|                                                                  |
| Before drafting, let's confirm your writing style for this       |
| proposal.                                                        |
|                                                                  |
| No quality profile found. You can create one anytime with:       |
|   /proposal quality discover                                     |
|                                                                  |
| Available writing styles:                                        |
|   1. Elements of Style (Strunk & White) -- concise, direct       |
|   2. Academic -- formal, detailed, citation-heavy                |
|   3. Conversational -- accessible, narrative-driven              |
|   4. Standard -- balanced professional prose (recommended)       |
|   5. Skip style selection -- use defaults, no skill loaded       |
|                                                                  |
| Choose [1-5] or describe your preference:                        |
|                                                                  |
+------------------------------------------------------------------+
```

**Emotional state**: Guided. The user sees their options with context-aware recommendations.

### Step 3: User Makes Style Choice

The user selects a style. The writer records the choice in per-proposal state:

- `writing_style`: the chosen style identifier (e.g., "elements", "academic", "standard")
- If user chose "skip": `writing_style_selection_skipped: true`

```
+-- Style Confirmed ----------------------------------------------+
|                                                                  |
| Writing style for SF25D-T1201: Elements of Style                 |
|   + Winning patterns from Air Force proposals applied            |
|   + Quality alerts active for this agency                        |
|                                                                  |
| Proceeding to draft first section...                             |
|                                                                  |
+------------------------------------------------------------------+
```

**Emotional state**: Empowered. The user made a deliberate choice about their proposal's voice.

### Step 4: Writer Attempts Write to wave-4-drafting/ (PES Gate)

The writer agent drafts a section and attempts to Write to `artifacts/{topic-id}/wave-4-drafting/sections/technical-approach.md`. PES PreToolUse hook fires. The WritingStyleGateEvaluator checks:

- Is the tool Write or Edit?
- Is the target path in wave-4-drafting/?
- Does quality-preferences.json exist at ~/.sbir/ OR does per-proposal state contain writing_style_selection_skipped: true?

If neither condition is met: BLOCK.

```
+-- PES: Writing Style Gate -- BLOCKED ---------------------------+
|                                                                  |
| BLOCKED: Cannot write draft sections to wave-4-drafting/ before  |
| writing style selection.                                         |
|                                                                  |
| Required (one of):                                               |
|  - ~/.sbir/quality-preferences.json (run /proposal quality       |
|    discover)                                                     |
|  - writing_style_selection_skipped in proposal state             |
|    (choose "skip" at the style checkpoint)                       |
|                                                                  |
| Complete the writing style selection before drafting.             |
|                                                                  |
+------------------------------------------------------------------+
```

**Emotional state**: Redirective. The agent receives clear guidance. This is the belt-and-suspenders layer -- the writer agent's style checkpoint (Step 2) should catch this first, but if bypassed, PES enforces.

### Step 5: Section Drafting Proceeds (Both Layers Satisfied)

With style confirmed (writer checkpoint) and quality-preferences.json present or skip marker set (PES gate), drafting proceeds normally. The writer loads the chosen style skill, applies quality preferences, surfaces agency-specific winning patterns and quality alerts.

```
+-- PES: Writing Style Gate -- ALLOWED ---------------------------+
|                                                                  |
| quality-preferences.json: EXISTS (or skip recorded)              |
|                                                                  |
| Section drafting proceeds with style applied.                    |
|                                                                  |
+------------------------------------------------------------------+
```

**Emotional state**: Confident. Every section is drafted with intentional style.

## Integration Points

| From | To | Artifact | Validation |
|------|----|----------|------------|
| Quality discovery | Writing style gate | quality-preferences.json at ~/.sbir/ | PES evaluator checks file existence |
| Style checkpoint | Per-proposal state | writing_style field | Writer records user choice |
| Style checkpoint | Per-proposal state | writing_style_selection_skipped | Writer records explicit skip |
| PES config | Engine evaluator dispatch | rule_type "writing_style_gate" | New type registered in engine |
| Hook adapter | PreToolUse handler | file_path + ~/.sbir/ artifact check | Path extraction + global artifact resolution |
| Writer agent | Style skills | writing_style value | Writer loads named style skill file |
