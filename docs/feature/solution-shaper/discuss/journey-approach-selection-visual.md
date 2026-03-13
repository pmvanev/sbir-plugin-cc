# Journey: Approach Selection -- Visual

## Journey Overview

```
Trigger: Phil made a GO decision on a solicitation topic (Wave 0 complete)

[GO Decision]  →  [Deep Read]  →  [Generate]  →  [Score]  →  [Converge]  →  [Checkpoint]  →  [Wave 1]
  Wave 0 done     Solicitation     Candidate       Approach      Recommend       Human          Strategy
                  analysis         approaches      matrix        + brief         approval       begins

Emotional Arc:
  Determined  →   Curious     →   Excited    →   Analytical  →  Confident   →  Decisive    →  Ready
  "Let's do       "What does      "I didn't       "The data      "This is      "Approved,     "Strategy
   this"          it really        think of        is clear"     the right      let's go"      has a
                  need?"           that one"                      approach"                     foundation"
```

---

## Step 1: Solicitation Deep Read

**Command**: Automatic (first phase of `/sbir:proposal shape`)
**Emotional State**: Curious → Informed

```
+-- Step 1: Solicitation Deep Read -------------------------------------------+
|                                                                              |
|  SOLUTION SHAPER — AF243-001                                                 |
|  Compact Directed Energy for Maritime UAS Defense                            |
|                                                                              |
|  Analyzing solicitation...                                                   |
|                                                                              |
|  Agency:      Air Force (AFRL/RD)                                            |
|  Phase:       I                                                              |
|  Deadline:    2026-04-15 (33 days remaining)                                 |
|                                                                              |
|  Problem Statement:                                                          |
|    Develop a compact, shipboard-deployable directed energy system            |
|    capable of neutralizing Group 1-3 UAS at ranges up to 1 km               |
|    in maritime environments with salt spray and vibration.                    |
|                                                                              |
|  Key Objectives:                                                             |
|    1. Demonstrate beam quality in maritime atmospheric conditions             |
|    2. Achieve system weight < 200 lbs for deck-mount installation            |
|    3. Engage multiple UAS targets in sequence (< 5 sec retarget)             |
|    4. Operate from standard shipboard 440V 3-phase power                     |
|                                                                              |
|  Evaluation Criteria:                                                        |
|    - Technical merit and innovation (40%)                                    |
|    - Team qualifications and past performance (30%)                          |
|    - Commercialization potential (20%)                                        |
|    - Cost realism (10%)                                                      |
|                                                                              |
|  Constraints:                                                                |
|    - ITAR restricted                                                         |
|    - Must address TRL 3→5 progression in Phase I                             |
|    - Size: 15-page technical volume                                          |
|                                                                              |
|  3 ambiguities flagged for TPOC questions                                    |
|                                                                              |
+------------------------------------------------------------------------------+
```

**Shared Artifacts Produced**:
- `${topic_id}` — AF243-001
- `${topic_title}` — Compact Directed Energy for Maritime UAS Defense
- `${agency}` — Air Force (AFRL/RD)
- `${deadline}` — 2026-04-15
- `${eval_criteria}` — Technical merit 40%, Team 30%, Commercialization 20%, Cost 10%

---

## Step 2: Approach Generation

**Command**: Automatic (second phase of `/sbir:proposal shape`)
**Emotional State**: Informed → Excited (option space revealed)

```
+-- Step 2: Candidate Approaches ---------------------------------------------+
|                                                                              |
|  Generated 4 candidate approaches for AF243-001                              |
|                                                                              |
|  A. High-Power Fiber Laser Array                                             |
|     Coherent beam combining of multiple fiber laser modules for              |
|     scalable power. Leverages commercial telecom fiber technology.           |
|     Key elements: spectral beam combining, adaptive optics,                  |
|     ruggedized fiber modules                                                 |
|                                                                              |
|  B. Diode-Pumped Solid-State Laser (DPSSL)                                  |
|     Slab or thin-disk gain medium with direct diode pumping.                 |
|     Proven military heritage from prior Navy programs.                       |
|     Key elements: Nd:YAG slab, active cooling, beam director                |
|                                                                              |
|  C. Hybrid RF-Optical Defeat System                                          |
|     Combined RF jammer for navigation denial plus lower-power               |
|     laser for sensor dazzle/damage. Layered defense approach.               |
|     Key elements: phased array RF, compact laser, sensor fusion             |
|                                                                              |
|  D. Direct Semiconductor Laser with Beam Shaping                             |
|     High-power laser diode stacks with novel beam shaping optics.           |
|     Lowest SWaP, highest wall-plug efficiency. Emerging approach.           |
|     Key elements: GaN diode stacks, diffractive optics, thermal             |
|     management                                                               |
|                                                                              |
|  Press Enter to continue to scoring, or type an approach to                  |
|  add/modify candidates...                                                    |
|                                                                              |
+------------------------------------------------------------------------------+
```

**Shared Artifacts Produced**:
- `${candidate_approaches}` — List of 4 named approaches with descriptions
- `${approach_count}` — 4

---

## Step 3: Approach Scoring

**Command**: Automatic (third phase of `/sbir:proposal shape`)
**Emotional State**: Excited → Analytical (data-driven evaluation)

```
+-- Step 3: Approach Scoring Matrix -------------------------------------------+
|                                                                              |
|  Scoring AF243-001 approaches against VanEvery Technologies profile          |
|                                                                              |
|  Dimension (Weight)      | Fiber  | DPSSL  | Hybrid | Diode  |              |
|  ========================|========|========|========|========|              |
|  Personnel align. (0.25) |  0.85  |  0.60  |  0.70  |  0.45  |              |
|  Past performance (0.20) |  0.80  |  0.50  |  0.65  |  0.30  |              |
|  Technical ready. (0.20) |  0.70  |  0.75  |  0.55  |  0.40  |              |
|  Solicitation fit (0.20) |  0.80  |  0.85  |  0.70  |  0.65  |              |
|  Commercializn.  (0.15)  |  0.75  |  0.60  |  0.80  |  0.70  |              |
|  ========================|========|========|========|========|              |
|  COMPOSITE               |  0.79  |  0.66  |  0.68  |  0.49  |              |
|                           | ^^^^   |        |        |        |              |
|                           | TOP    |  #3    |  #2    |  #4    |              |
|                                                                              |
|  Score spread: 30 percentage points (0.49 to 0.79)                           |
|  Meaningful differentiation: YES                                             |
|                                                                              |
|  Key differentiators for top approach (Fiber Laser Array):                   |
|    - Dr. Sarah Chen: 12 years fiber laser beam combining (personnel)         |
|    - AF241-087 Phase I: fiber laser target tracking (past performance)       |
|    - Existing lab prototype at TRL 3 (technical readiness)                   |
|                                                                              |
+------------------------------------------------------------------------------+
```

**Shared Artifacts Produced**:
- `${scoring_matrix}` — Full approach x dimension scoring grid
- `${top_approach}` — High-Power Fiber Laser Array
- `${top_score}` — 0.79
- `${runner_up}` — Hybrid RF-Optical Defeat System
- `${score_spread}` — 30 percentage points

---

## Step 4: Convergence and Recommendation

**Command**: Automatic (fourth phase of `/sbir:proposal shape`)
**Emotional State**: Analytical → Confident (clear recommendation)

```
+-- Step 4: Approach Recommendation -------------------------------------------+
|                                                                              |
|  RECOMMENDED: High-Power Fiber Laser Array                                   |
|  Composite Score: 0.79 / 1.00                                               |
|                                                                              |
|  Why this approach:                                                          |
|    - Strongest personnel alignment: Dr. Sarah Chen (PI) has 12 years        |
|      in fiber laser beam combining with 8 publications                       |
|    - Direct past performance: AF241-087 Phase I demonstrated fiber          |
|      laser target tracking in field conditions                               |
|    - Leverages existing TRL 3 lab prototype for rapid TRL advancement       |
|    - Commercial fiber laser components reduce supply chain risk              |
|                                                                              |
|  Runner-up: Hybrid RF-Optical Defeat System (0.68)                           |
|    - Stronger commercialization (dual-use RF/optical)                        |
|    - Weaker past performance (no prior RF-optical integration work)          |
|    - Reconsider if: TPOC signals preference for layered defense              |
|                                                                              |
|  Discrimination Angles:                                                      |
|    1. Only team with demonstrated fiber beam combining in field conditions   |
|    2. TRL 3 prototype reduces Phase I technical risk vs. paper studies       |
|    3. Commercial fiber components = lower cost and faster Phase III          |
|                                                                              |
|  Risks and Open Questions:                                                   |
|    - Maritime salt spray effect on fiber optics — validate in Wave 2         |
|    - Thermal management at sustained fire rates — validate in Wave 2         |
|    - Weight target (< 200 lbs) achievability — engineering analysis needed   |
|                                                                              |
|  Phase III Quick Assessment:                                                 |
|    - Primary pathway: Dual-use (Navy shipboard + commercial maritime)        |
|    - Target programs: PMS 501 (Surface Ship Weapons), NAVSEA                 |
|    - Market relevance: HIGH (C-UAS is $5B+ growing market)                   |
|                                                                              |
+------------------------------------------------------------------------------+
```

**Shared Artifacts Produced**:
- `${selected_approach}` — High-Power Fiber Laser Array
- `${selection_rationale}` — Personnel + past performance + TRL advantage
- `${discrimination_angles}` — 3 angles for Wave 3
- `${risks}` — 3 risks for Wave 1-2 validation
- `${phase3_pathway}` — Dual-use, PMS 501, HIGH market relevance

---

## Step 5: Human Checkpoint

**Command**: Interactive checkpoint at end of `/sbir:proposal shape`
**Emotional State**: Confident → Decisive

```
+-- Step 5: Approach Selection Checkpoint -------------------------------------+
|                                                                              |
|  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                         |
|  CHECKPOINT: Approach Selection                                              |
|  Solution Shaper — AF243-001                                                 |
|  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                         |
|                                                                              |
|  Recommended: High-Power Fiber Laser Array (0.79)                            |
|  Runner-up:   Hybrid RF-Optical Defeat System (0.68)                         |
|                                                                              |
|  Approach brief written to:                                                  |
|    ./artifacts/wave-0-intelligence/approach-brief.md                         |
|                                                                              |
|  Options:                                                                    |
|    (a) approve  — proceed to Wave 1 with this approach                       |
|    (r) revise   — adjust approach or scoring, regenerate brief               |
|    (e) explore  — dig deeper on a specific approach                          |
|    (x) restart  — regenerate candidate approaches                            |
|    (q) quit     — save state and exit                                        |
|                                                                              |
|  >                                                                           |
|                                                                              |
+------------------------------------------------------------------------------+
```

**Shared Artifacts Produced**:
- `${checkpoint_decision}` — approve / revise / explore / restart / quit
- `${approach_brief_path}` — ./artifacts/wave-0-intelligence/approach-brief.md

---

## Error Paths

### E1: Solicitation is Vague or Underspecified

```
+-- Warning: Ambiguous Solicitation ------------------------------------------+
|                                                                              |
|  The solicitation for N244-012 uses vague language in key areas:             |
|    - "Relevant environment" — not defined (lab? field? maritime?)            |
|    - "Appropriate integration" — scope unclear                               |
|    - "Novel approach" — no baseline for comparison                           |
|                                                                              |
|  Impact: Candidate approaches may not align with TPOC's actual intent.      |
|                                                                              |
|  Recommendation: Generate TPOC questions targeting these ambiguities         |
|  before finalizing approach selection. Use /sbir:proposal tpoc questions     |
|  after this step.                                                            |
|                                                                              |
+------------------------------------------------------------------------------+
```

### E2: Company Has Low Capability Match for All Approaches

```
+-- Warning: Low Company Fit -------------------------------------------------+
|                                                                              |
|  All 4 candidate approaches scored below 0.40 composite for AF243-099.      |
|                                                                              |
|  Highest: Approach B (0.38) — insufficient past performance and             |
|  no key personnel with direct domain expertise.                              |
|                                                                              |
|  Recommendation: Reconsider the Go decision for this topic.                  |
|  Run /sbir:proposal status to review Go/No-Go rationale.                     |
|                                                                              |
+------------------------------------------------------------------------------+
```

### E3: All Approaches Score Similarly

```
+-- Note: Multiple Viable Approaches -----------------------------------------+
|                                                                              |
|  Score spread is narrow: 0.62 to 0.68 (6 percentage points).                |
|  No clear winner by composite score alone.                                   |
|                                                                              |
|  Tiebreaker considerations:                                                  |
|    1. Which approach has the strongest single discriminator?                  |
|    2. Which has the lowest technical risk for Phase I?                        |
|    3. Which produces the most compelling proposal narrative?                  |
|                                                                              |
|  Consider using (e) explore to compare the top 2 approaches in depth.        |
|                                                                              |
+------------------------------------------------------------------------------+
```

### E4: No Company Profile Found

```
+-- Error: Company Profile Missing --------------------------------------------+
|                                                                              |
|  Could not load company profile from ~/.sbir/company-profile.json            |
|                                                                              |
|  The solution shaper requires a company profile to score approaches          |
|  against your specific capabilities.                                         |
|                                                                              |
|  Create one with: /sbir:company-profile setup                                |
|                                                                              |
+------------------------------------------------------------------------------+
```

---

## Emotional Arc Summary

| Step | Entry Emotion | Exit Emotion | Design Driver |
|------|---------------|--------------|---------------|
| 1. Deep Read | Determined | Curious/Informed | Show the solicitation is understood at depth, not just summarized |
| 2. Generation | Curious | Excited | Surface at least 1 approach Phil did not consider independently |
| 3. Scoring | Excited | Analytical | Concrete numbers, company-specific evidence, real personnel names |
| 4. Convergence | Analytical | Confident | Clear recommendation with documented rationale |
| 5. Checkpoint | Confident | Decisive | Control over the decision with revise/explore/restart options |
| Errors | Varies | Guided | Every error suggests a concrete next action |

**Arc Pattern**: Confidence Building -- anxious/uncertain at start, progressively more confident through evidence, decisive at checkpoint.
