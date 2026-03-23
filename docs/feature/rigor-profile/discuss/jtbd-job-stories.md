# JTBD Job Stories -- Rigor Profile

Feature: rigor-profile
Date: 2026-03-23
Phase: 1 -- Deep Discovery (JTBD Analysis)

---

## Job Classification

**Job Type**: Build Something New (Greenfield) -- cross-cutting infrastructure feature
**ODI Phase**: Discovery -- we know the problem space but not the exact shape of the solution
**Research Depth**: Comprehensive

The rigor profile is a quality/cost dial that cuts across all 10 waves and 18 agents. It does not add a new wave or user-facing proposal artifact -- it changes HOW existing waves execute. This makes it infrastructure with user-facing configuration.

---

## Job 1: Right-Size Quality to Proposal Stakes

### Job Story

**When** I am working on an SBIR proposal where the topic is a strong fit and the contract ceiling is $1.7M (Phase II),
**I want to** dial up the thoroughness of every agent in the pipeline,
**so I can** maximize my evaluation score on a must-win opportunity without worrying that the AI cut corners.

### Functional Job

Increase review depth, iteration cycles, and model capability for high-stakes proposals to produce the strongest possible submission.

### Emotional Job

Feel confident that the tool is giving its absolute best effort on this proposal -- the same intensity I would bring myself if I had unlimited time.

### Social Job

Submit a proposal that my TPOC and program manager would recognize as polished and thorough, not as obviously AI-generated boilerplate.

### Three Dimensions -- Concrete Examples

- **Functional**: Dr. Elena Vasquez at Meridian Defense is responding to AF243-001 ("Compact Directed Energy for Maritime UAS Defense"), a $1.7M Phase II. She wants double-pass writer-reviewer iteration, full figure critique loops, and the strongest available model on the strategist and writer agents. Her last proposal lost on Technical Merit, and the debrief cited "insufficient detail in TRL advancement methodology."
- **Emotional**: Elena wants to feel that when she hits `/proposal submit`, she has extracted every ounce of quality the tool can provide. She does NOT want to wonder "would it have been better if I'd used a stronger model?"
- **Social**: Elena's company has 12 employees. Winning this contract funds 3 positions for 2 years. Her board will see the proposal. It must not read like a first draft.

---

## Job 2: Control API Costs During Exploratory Work

### Job Story

**When** I am evaluating 4-5 SBIR topics in Wave 0 to decide which ones to pursue,
**I want to** use cheaper, faster models for the initial scouting and shaping,
**so I can** screen topics without burning $30-50 in API costs per topic before I even know if they are worth pursuing.

### Functional Job

Reduce per-run token costs during early-stage exploration where output quality thresholds are lower and volume is higher.

### Emotional Job

Feel smart about resource allocation -- not wasteful. The anxiety of watching API costs climb during exploration is real when you are a small business funding this out of overhead.

### Social Job

Be seen (by co-founders, by the accountant) as someone who manages tooling costs responsibly, not someone who throws money at AI without thinking about ROI.

### Three Dimensions -- Concrete Examples

- **Functional**: Marcus Chen at NovaTech Solutions is screening 6 Navy topics from the latest SBIR solicitation. He wants Wave 0 (topic scout + solution shaper) to run on a fast, inexpensive model. He does not need Opus-tier analysis to decide "is this topic a 3/5 or a 5/5 fit?" He needs to spend $2-3 per topic, not $15-20.
- **Emotional**: Marcus closed Q4 with $4,200 in Claude API costs across 8 proposals. His CEO asked "is this sustainable?" Marcus wants to show that exploration is cheap and that heavy spend is reserved for proposals that actually get submitted.
- **Social**: Marcus reports API costs monthly. He needs a credible answer to "why did we spend X this month?" -- and "I ran everything at maximum quality including topics we rejected" is not a credible answer.

---

## Job 3: Accelerate Iteration Cycles During Drafting

### Job Story

**When** I am in Wave 4 drafting and I want rapid feedback on a section I just restructured,
**I want to** get a quick, lightweight review pass in 30 seconds instead of waiting 3 minutes for a thorough review,
**so I can** iterate on structure and flow quickly before committing to a deep quality review.

### Functional Job

Reduce latency in the writer-reviewer feedback loop during active drafting sessions where speed matters more than completeness.

### Emotional Job

Stay in creative flow. A 3-minute wait between iterations breaks concentration and creates friction that makes me want to skip the review entirely.

### Social Job

Not relevant for this job -- this is a solo workflow moment.

### Three Dimensions -- Concrete Examples

- **Functional**: Phil Santos at Apex Engineering is drafting Section 3 (Technical Approach) for topic N244-012. He has restructured the TRL advancement methodology after reviewer feedback. He wants to quickly check if the new structure addresses the finding before investing in a full deep review. A lightweight pass that checks structure, compliance coverage, and flow -- skipping detailed evaluator scoring -- would take 30 seconds vs. 3 minutes.
- **Emotional**: Phil has 6 sections to draft today. If each one requires 2 full review cycles at 3 minutes each, that is 36 minutes of waiting. He would rather do a quick structural check on each, then batch the deep reviews at the end. Waiting kills his momentum.
- **Functional (variant)**: Phil is experimenting with two different structures for the management plan. He wants to review both quickly and pick the stronger one before investing deep review effort in the winner.

---

## Job 4: Manage Multiple Proposals at Different Priority Levels

### Job Story

**When** I am running 3 proposals simultaneously with different deadlines and win probabilities,
**I want to** assign different quality levels per proposal,
**so I can** invest maximum effort in my must-win (85% fit score, $1.7M) while keeping costs reasonable on my long-shot (60% fit, $250K Phase I).

### Functional Job

Configure quality/cost tradeoffs per proposal in a multi-proposal workspace, with each proposal retaining its rigor setting across sessions.

### Emotional Job

Feel organized and strategic about resource allocation across proposals -- not guilty about under-investing in the long-shot and not anxious about over-spending on it either.

### Social Job

Demonstrate to the team that proposal prioritization is deliberate and data-driven, not ad hoc. "We allocated Thorough to AF243-001 and Lean to N244-012 because of fit scores and contract value."

### Three Dimensions -- Concrete Examples

- **Functional**: Dr. Elena Vasquez has three active proposals in her workspace: AF243-001 (must-win, 85% fit, Phase II $1.7M), N244-012 (moderate, 72% fit, Phase I $250K), and DA244-003 (exploratory, 58% fit, Phase I $250K). She wants AF243-001 at "thorough" (best model, double review, full critique loops), N244-012 at "standard" (balanced model, single review, critique loops enabled), and DA244-003 at "lean" (fast model, minimal review, critique loops skipped).
- **Emotional**: Elena checks her proposal dashboard and sees the rigor level next to each proposal. It confirms that her resource allocation matches her strategic priorities. No second-guessing.
- **Social**: When her VP asks "how are we allocating effort across the three open proposals?", Elena can show the rigor assignments alongside fit scores and contract values. It tells a coherent story.

---

## Job 5: Recover Quality When a Section Fails Review

### Job Story

**When** a specific section has failed its second review cycle and the reviewer recommends escalation,
**I want to** temporarily increase the rigor for just that section's next revision,
**so I can** bring maximum model capability to bear on the problem area without re-running the entire wave at high cost.

### Functional Job

Override the proposal-level rigor setting for a targeted re-run of a specific section or figure, then revert to the baseline setting.

### Emotional Job

Feel empowered to address quality problems surgically. The current all-or-nothing approach (escalate to human) feels like giving up.

### Social Job

Demonstrate that the tool helped solve the quality problem, rather than having to explain "the AI couldn't handle this section, I had to rewrite it manually."

### Three Dimensions -- Concrete Examples

- **Functional**: Phil Santos is on proposal N244-012 at "standard" rigor. The reviewer flagged Section 3.2 (TRL Advancement Methodology) as deficient after 2 cycles -- the entry/exit criteria lack specificity. Phil wants to re-run the writer on just Section 3.2 with "thorough" rigor (stronger model, more detailed instructions), get it reviewed, and then continue the rest of the proposal at "standard."
- **Emotional**: Phil does not want to re-run the entire Wave 4 at "thorough" -- that would cost $40+ and take an hour. He wants a scalpel, not a sledgehammer.
- **Functional (variant)**: In Wave 5, Figure 3 (system architecture diagram) keeps failing the composition critique after 3 iterations. Phil wants to try one more iteration at the highest model tier before deferring to external.

---

## Job 6: Understand What Rigor Actually Changes

### Job Story

**When** I am choosing a rigor level for the first time,
**I want to** see exactly what each level does to my proposal process -- which models, how many review passes, which loops are enabled,
**so I can** make an informed tradeoff between quality and cost without guessing.

### Functional Job

View a transparent comparison of what each rigor level configures: models per agent role, review depth, iteration caps, critique loop settings, and compliance checking depth.

### Emotional Job

Feel informed and in control. Opacity about what "thorough" means would make me distrust the entire feature. I need to see the knobs, not just the label.

### Social Job

Be able to explain to colleagues or a co-founder what "standard" vs. "thorough" means in concrete terms, not marketing language.

### Three Dimensions -- Concrete Examples

- **Functional**: Marcus Chen is about to start his first proposal with the rigor feature. He runs `/proposal rigor` and sees a comparison table: Lean uses Haiku for scouting/Sonnet for writing, 1 review pass, critique loops skipped. Standard uses Sonnet across the board, 2 review passes, critique loops enabled with 2 max iterations. Thorough uses Opus for writing/reviewing, 2 review passes, critique loops enabled with 3 max iterations. He picks Standard and knows exactly what he is getting.
- **Emotional**: Marcus reads the comparison and thinks "okay, this makes sense -- I understand the tradeoff." He does NOT think "what is the difference between Standard and Thorough, really?"
- **Functional (variant)**: Elena wants to create a custom profile that uses Opus for the strategist and writer but Sonnet for everything else. She sees that "custom" lets her set model per agent role, and the interface shows which agents belong to which role.

---

## Universal Job Map -- Rigor Profile

Walking the 8-step job map across the rigor profile lifecycle:

| Step | What Happens | Key Needs |
|------|-------------|-----------|
| 1. Define | User decides what quality level is appropriate for this proposal | Understand what each level does, see cost implications |
| 2. Locate | Find the rigor command, see available profiles | Discoverable command, clear profile names |
| 3. Prepare | Select or customize a profile | Simple selection for common cases, customization for advanced users |
| 4. Confirm | Verify the profile before applying | Preview what will change, see affected agents/waves |
| 5. Execute | Profile applies to all subsequent agent invocations | Seamless integration -- agents use configured model/settings without user action |
| 6. Monitor | See rigor level in status displays, cost tracking | Rigor level visible in `/proposal status`, cumulative cost awareness |
| 7. Modify | Change rigor mid-proposal, override per-section | Smooth transitions, no lost work, targeted overrides |
| 8. Conclude | Assess quality/cost outcome after submission | Debrief includes rigor settings used, cost summary |

---

## Job Relationships

```
Job 6 (Understand)
    |
    v
Job 2 (Control Costs) ---+---> Job 4 (Multi-Proposal)
                          |
Job 1 (Right-Size)  -----+
                          |
Job 3 (Fast Iteration) --+---> Job 5 (Recover Quality)
```

Jobs 1 and 2 are the primary demand-generating jobs (must-win quality vs. cost control). Job 4 is the multiplier (multiple proposals amplify both). Job 3 and 5 are workflow refinements that emerge during active use. Job 6 is the prerequisite for adoption of all others.
