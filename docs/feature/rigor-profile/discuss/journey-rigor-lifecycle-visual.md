# Journey: Rigor Profile Lifecycle -- Visual Map

Feature: rigor-profile
Date: 2026-03-23
Phase: 2 -- Journey Visualization

---

## Journey Overview

This journey maps the full lifecycle of a rigor profile: from first encounter during
proposal creation, through wave execution where rigor shapes agent behavior, to
mid-proposal adjustment and multi-proposal differentiation.

**Persona**: Dr. Elena Vasquez, Principal Investigator at Meridian Defense (12 employees).
Runs 2-3 simultaneous SBIR proposals per quarter. Lost a Phase II last cycle on
Technical Merit. Needs to invest quality where it counts.

**Secondary Persona**: Marcus Chen, Proposal Manager at NovaTech Solutions. Screens
5-6 topics per solicitation. CEO watches API costs monthly. Needs exploration to be
cheap and submission-quality to be high.

---

## Emotional Arc

```
Confidence
  ^
  |                                                          ****
  |                                                     ****
  |                                               *****
  |                                          ****
  |                                     ****         "I see rigor shaping
  |                                ****               every wave. This is
  |                           ****                    working."
  |                      ****
  |                  ***
  |             ***       "I understand the
  |         ***            tradeoffs. I picked
  |     ***                the right level."
  |  **
  | *   "What does 'thorough'
  |      actually mean?"
  +-----------------------------------------------------------> Time
  Step 1       Step 2       Step 3       Step 4       Step 5
  Discover     Select       Execute      Adjust       Review
```

**Arc pattern**: Confidence Building
- **Start**: Uncertain -- "How do I choose the right level? What am I actually paying for?"
- **Middle**: Engaged -- "I can see the profile controlling agent behavior. My must-win gets Opus."
- **End**: Confident -- "My rigor allocation matches my strategic priorities across all proposals."

---

## Step 1: Discover Rigor Profiles (Job 6 -- Understand What Rigor Changes)

**Trigger**: Elena runs `/proposal new` for topic AF243-001. After Go/No-Go, the
system mentions rigor profiles for the first time.

**Emotional state**: Curious but cautious. She does not want another configuration
step delaying real work.

```
+-- /proposal new AF243-001 ------------------------------------------+
|                                                                      |
|  Proposal created: AF243-001 (Compact Directed Energy)               |
|  Phase II | $1.7M ceiling | Deadline: 2026-05-15                     |
|  Fit score: 85/100                                                   |
|  Format: LaTeX                                                       |
|  Decision: GO                                                        |
|                                                                      |
|  Rigor Profile: standard (default)                                   |
|                                                                      |
|  Tip: This proposal has a high fit score and Phase II value.         |
|  Consider /proposal rigor set thorough for maximum quality.          |
|  Run /proposal rigor show to compare profiles.                       |
|                                                                      |
+----------------------------------------------------------------------+
```

**Key design decisions**:
- Rigor defaults to "standard" -- no mandatory decision at proposal creation
- Contextual suggestion based on fit score (85) and contract value ($1.7M Phase II)
- Progressive disclosure: hint exists, detail available on demand
- No blocking prompt -- the user can ignore and proceed

**Integration checkpoint**: `${fit_score}` and `${contract_value}` from proposal-state.json
drive the suggestion logic.

---

## Step 2: Understand and Select a Profile (Job 6 + Job 1 + Job 2)

**Trigger**: Elena runs `/proposal rigor show` to understand her options.

**Emotional state**: Evaluating. She wants clarity, not a wall of configuration.

```
+-- /proposal rigor show ----------------------------------------------+
|                                                                      |
|  Rigor Profiles                                                      |
|  Active: standard                   Proposal: AF243-001              |
|                                                                      |
|  Profile     Quality   Cost/Wave   Review   Critique   Best For      |
|  ---------   -------   ---------   ------   --------   -----------   |
|  lean        Basic     $2-5        1 pass   Skipped    Screening     |
|  standard    Balanced  $8-15       2 pass   2 iter     Most work     |
|  thorough    Deep      $20-35      2 pass   3 iter     Must-win      |
|  exhaustive  Maximum   $40-60      3 pass   4 iter     Critical bid  |
|                                                                      |
|  Run /proposal rigor show <profile> for full detail.                 |
|                                                                      |
+----------------------------------------------------------------------+
```

**Detail view** (on demand -- `/proposal rigor show thorough`):

```
+-- /proposal rigor show thorough -------------------------------------+
|                                                                      |
|  Profile: thorough                                                   |
|                                                                      |
|  Agent Role        Model Tier    Notes                               |
|  ---------------   -----------   --------------------------------    |
|  Strategist        Strongest     Deep strategic analysis             |
|  Writer            Strongest     Maximum prose quality               |
|  Reviewer          Strongest     Thorough evaluation scoring         |
|  Researcher        Standard      Research quality stable at this     |
|  Topic Scout       Standard      Screening accuracy sufficient       |
|  Formatter         Standard      Formatting is deterministic         |
|  Compliance        Strongest     Catch every compliance gap          |
|  Visual Assets     Strongest     Full critique-refine loops          |
|                                                                      |
|  Review depth:     2 passes (structural + evaluator scoring)         |
|  Critique loops:   Enabled, max 3 iterations                         |
|  Iteration cap:    3 writer-reviewer cycles per section              |
|                                                                      |
|  Estimated cost:   $20-35 per wave (varies by section count)         |
|                                                                      |
+----------------------------------------------------------------------+
```

**Emotional state exit**: Informed. Elena sees exactly what "thorough" means -- strongest
model on strategist/writer/reviewer/compliance, 2 review passes, 3 critique iterations.
She knows what she is paying for.

**She selects**:

```
+-- /proposal rigor set thorough --------------------------------------+
|                                                                      |
|  Rigor updated: standard -> thorough                                 |
|  Proposal: AF243-001 (Compact Directed Energy)                       |
|                                                                      |
|  Changes:                                                            |
|    Writer model:     standard -> strongest                           |
|    Reviewer model:   standard -> strongest                           |
|    Strategist model: standard -> strongest                           |
|    Compliance model: standard -> strongest                           |
|    Visual assets:    standard -> strongest                           |
|    Review passes:    2 -> 2 (unchanged)                              |
|    Critique loops:   2 iter -> 3 iter                                |
|                                                                      |
|  All subsequent waves will use thorough settings.                    |
|  Existing artifacts are preserved -- no re-run required.             |
|                                                                      |
+----------------------------------------------------------------------+
```

**Key design decisions**:
- Two-level disclosure: summary table first, per-profile detail on demand
- Cost ranges, not exact prices (model pricing changes; ranges stay valid longer)
- "Agent role" not "agent name" -- users think in roles, not internal agent identifiers
- Diff display when changing: shows exactly what shifts, reducing anxiety
- Explicit reassurance: existing artifacts preserved

**Integration checkpoint**: `${active_profile}` written to rigor-profile.json.
`${previous_profile}` shown in diff for user confidence.

---

## Step 3: Execute Waves with Rigor Applied (Job 1 -- Right-Size Quality)

**Trigger**: Elena starts Wave 1 (Strategy). The active profile silently controls
agent behavior.

**Emotional state**: Hopeful, watching for evidence that "thorough" actually makes
a difference.

```
+-- /proposal strategy (Wave 1 at thorough) --------------------------+
|                                                                      |
|  Wave 1: Requirements & Strategy                                     |
|  Rigor: thorough                                                     |
|                                                                      |
|  [1/3] Topic analysis...                                             |
|         Model: strongest | Depth: comprehensive                     |
|  [2/3] Strategy brief...                                             |
|         Model: strongest | Reviewing: 2 passes                      |
|  [3/3] Compliance pre-check...                                       |
|         Model: strongest | Checking: all criteria                    |
|                                                                      |
|  Strategy brief saved to artifacts/af243-001/wave-1-strategy/        |
|                                                                      |
+----------------------------------------------------------------------+
```

**Key design decisions**:
- Rigor level shown in wave header -- constant visual confirmation
- Per-step model tier and depth shown inline -- evidence that rigor is active
- Not showing model names (Opus/Sonnet) -- model tiers abstract over pricing changes
- Progress indicator uses step counting for predictability

**Emotional state exit**: Reassured. Elena can SEE that "thorough" changed the
execution. The strategist used the strongest model. Reviews ran 2 passes. This is
not a placebo dial.

---

## Step 4: Status Display with Rigor Context (Job 4 -- Multi-Proposal)

**Trigger**: Elena runs `/proposal status` to check her portfolio.

**Emotional state**: Managing. She has 3 proposals and needs to see the big picture.

```
+-- /proposal status --------------------------------------------------+
|                                                                      |
|  Active: AF243-001 (Compact Directed Energy)                         |
|  Phase II | $1.7M | Fit: 85 | Rigor: thorough                       |
|  Wave 3: Discrimination & Outline                                    |
|  27 days to deadline                                                 |
|  Next: /proposal wave outline                                        |
|                                                                      |
|  Other proposals:                                                    |
|  ---------------------------------------------------------------     |
|  N244-012  AUV Navigation      Phase I  $250K  Fit: 72  standard     |
|  DA244-003 Sensor Fusion        Phase I  $250K  Fit: 58  lean        |
|                                                                      |
+----------------------------------------------------------------------+
```

**Key design decisions**:
- Rigor level shown inline with each proposal -- portfolio-level visibility
- Active proposal gets full detail; others get one-line summary
- Rigor, fit score, and contract value together tell the resource allocation story
- Elena can confirm: must-win = thorough, moderate = standard, exploratory = lean

**Integration checkpoint**: `${rigor_level}` per proposal read from each proposal's
rigor-profile.json. Dashboard aggregates across `.sbir/proposals/*/`.

---

## Step 5: Adjust Rigor Mid-Proposal (Job 4 + Job 2)

**Trigger**: After Wave 2 research, DA244-003 turns out to be a stronger fit than
expected. Elena wants to upgrade it from lean to standard.

**Emotional state**: Decisive. New information warrants a priority change.

```
+-- /proposal switch da244-003 ----------------------------------------+
|                                                                      |
|  Switched to: DA244-003 (Sensor Fusion)                              |
|  Rigor: lean                                                         |
|  Wave 2: Research & Evidence                                         |
|                                                                      |
+----------------------------------------------------------------------+

+-- /proposal rigor set standard --------------------------------------+
|                                                                      |
|  Rigor updated: lean -> standard                                     |
|  Proposal: DA244-003 (Sensor Fusion)                                 |
|                                                                      |
|  Changes:                                                            |
|    Writer model:     basic -> standard                               |
|    Reviewer model:   basic -> standard                               |
|    Review passes:    1 -> 2                                          |
|    Critique loops:   Skipped -> 2 iter                               |
|                                                                      |
|  Waves 0-2 retain their existing artifacts (produced at lean).       |
|  Wave 3+ will use standard settings.                                 |
|                                                                      |
|  Note: Earlier waves were produced at lean rigor.                    |
|  Run /proposal iterate <section> to re-process specific sections     |
|  at the new rigor level if needed.                                   |
|                                                                      |
+----------------------------------------------------------------------+
```

**Key design decisions**:
- Rigor change is metadata-only -- no automatic re-run of completed waves
- Explicit statement about what was produced at the old level
- Actionable guidance: `/proposal iterate` to selectively re-process if desired
- No guilt, no pressure -- informational, not judgmental
- Change applies forward (Wave 3+), preserving completed work

**Emotional state exit**: Confident and organized. Elena adjusted her portfolio
allocation based on new information. The tool supported the change without friction.

---

## Step 6: Cost-Conscious Exploration (Job 2 -- Control Costs)

**Trigger**: Marcus Chen is screening 6 Navy topics. He creates each at lean rigor.

**Emotional state**: Efficient. He wants speed and low cost for go/no-go decisions.

```
+-- /proposal new N244-015 -------------------------------------------+
|                                                                      |
|  Proposal created: N244-015 (Undersea Acoustic Sensing)              |
|  Phase I | $250K | Deadline: 2026-06-01                              |
|  Fit score: 64/100                                                   |
|  Format: DOCX                                                        |
|  Decision: GO                                                        |
|                                                                      |
|  Rigor Profile: standard (default)                                   |
|                                                                      |
|  Tip: For exploratory screening, /proposal rigor set lean            |
|  reduces cost to $2-5/wave while maintaining go/no-go accuracy.      |
|                                                                      |
+----------------------------------------------------------------------+

+-- /proposal rigor set lean ------------------------------------------+
|                                                                      |
|  Rigor updated: standard -> lean                                     |
|  Proposal: N244-015 (Undersea Acoustic Sensing)                      |
|                                                                      |
|  Lean profile optimizes for speed and cost:                          |
|    All agents:       basic model tier                                |
|    Review passes:    1 (structural only)                             |
|    Critique loops:   Skipped                                         |
|    Estimated cost:   $2-5 per wave                                   |
|                                                                      |
+----------------------------------------------------------------------+
```

**Key design decisions**:
- Contextual tip adapts to proposal metadata (moderate fit + Phase I = lean suggestion)
- Lean mode description emphasizes what IS provided, not what is missing
- Cost estimate prominent -- this is the primary value proposition for Marcus

---

## Step 7: Debrief with Rigor Context (Job 1 -- Right-Size Quality)

**Trigger**: After submission, Elena runs `/proposal debrief` for AF243-001.

**Emotional state**: Reflective. She wants to know if the investment paid off.

```
+-- /proposal debrief (Wave 9) ----------------------------------------+
|                                                                      |
|  Proposal: AF243-001 (Compact Directed Energy)                       |
|  Rigor: thorough (used throughout)                                   |
|                                                                      |
|  Rigor Summary:                                                      |
|    Profile:          thorough                                        |
|    Waves completed:  10/10                                           |
|    Review cycles:    24 total (avg 2.4/section)                      |
|    Critique loops:   8 figures, 3 iterations avg                     |
|    Profile changes:  None (thorough from start)                      |
|                                                                      |
|  This information is recorded for future rigor decisions.            |
|  If you receive evaluation feedback, re-run debrief to correlate     |
|  rigor settings with reviewer scores.                                |
|                                                                      |
+----------------------------------------------------------------------+
```

**Key design decisions**:
- Rigor summary in debrief creates a feedback loop: investment -> outcome
- Review cycle counts make the "thoroughness" concrete and auditable
- Profile change history tracked (if Elena had changed mid-proposal, shown here)
- Forward-looking: debrief data informs future rigor choices (Job 6 long-term)

**Emotional state exit**: Satisfied. Elena knows exactly what level of effort the
tool applied. When evaluation results come back, she can correlate rigor with scores.

---

## Journey Flow Diagram

```
                    /proposal new
                         |
                    [1] DISCOVER
                    Rigor hint shown
                    Default: standard
                         |
            +-----------+------------+
            |                        |
     Accept default          /proposal rigor show
     (most users)                    |
            |               [2] UNDERSTAND
            |               Compare profiles
            |               See detail on demand
            |                        |
            |               /proposal rigor set <profile>
            |               Diff shown, artifacts preserved
            |                        |
            +-----------+------------+
                        |
                   [3] EXECUTE
                   Waves run with rigor applied
                   Model tier + depth shown per step
                        |
                   [4] MONITOR
                   /proposal status shows rigor
                   Portfolio view with rigor per proposal
                        |
              +---------+---------+
              |                   |
        Continue as-is    [5] ADJUST
              |           /proposal rigor set <new>
              |           Forward-only, artifacts preserved
              |           Re-process hint for earlier sections
              |                   |
              +---------+---------+
                        |
                   [6] EXPLORE (lean path)
                   Cheap screening for go/no-go
                   Upgrade on commit
                        |
                   [7] DEBRIEF
                   Rigor summary in debrief
                   Feedback loop for future choices
```

---

## Error Paths

### E1: Unknown profile name

```
$ /proposal rigor set ultra

Error: Unknown rigor profile "ultra".

Available profiles: lean, standard, thorough, exhaustive

Run /proposal rigor show to compare profiles.
```

### E2: No active proposal

```
$ /proposal rigor set thorough

Error: No active proposal.

Start a proposal with /proposal new <solicitation-file>
or switch to an existing one with /proposal switch <topic-id>.
```

### E3: Profile already active

```
$ /proposal rigor set thorough

Rigor is already set to "thorough" for AF243-001.
No changes made.
```

---

## JTBD Traceability

| Step | Primary Job | Supporting Jobs | Top Opportunity Outcomes |
|------|------------|-----------------|-------------------------|
| 1. Discover | J6 (Understand) | J1, J2 | #6 (not knowing feature exists), #8 (minimize decisions) |
| 2. Select | J6, J1, J2 | -- | #1 (time to determine tradeoff), #4 (understand config), #7 (time to select) |
| 3. Execute | J1 (Right-Size) | J2 | #12 (agent respects rigor), #13 (apply across agents) |
| 4. Monitor | J4 (Multi-Proposal) | J6 | #15 (see current level), #16 (track active level) |
| 5. Adjust | J4, J2 | J1 | #18 (change mid-proposal), #19 (no lost work) |
| 6. Explore | J2 (Control Costs) | J6 | #2 (over-investing), #7 (time to select) |
| 7. Debrief | J1 | J6 | #22 (debrief informs future), #21 (review settings used) |
