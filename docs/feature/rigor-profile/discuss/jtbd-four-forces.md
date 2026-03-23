# JTBD Four Forces Analysis -- Rigor Profile

Feature: rigor-profile
Date: 2026-03-23
Phase: 1 -- Deep Discovery (JTBD Analysis)

---

## Forces Analysis: Job 1 -- Right-Size Quality to Proposal Stakes

### Demand-Generating

- **Push**: All 18 agents use `model: inherit`, meaning a $250K Phase I long-shot gets the same model as a $1.7M Phase II must-win. Dr. Elena Vasquez at Meridian Defense lost a proposal where the debrief cited "insufficient detail in TRL advancement methodology" -- she suspects a more capable model would have produced deeper technical content. She has no way to tell the tool "this one matters more."
- **Pull**: A rigor dial that lets Elena select "thorough" for her must-win proposal and know that the writer, reviewer, and strategist agents will use the strongest available model, run double review passes, and execute full critique loops. The tool matches her investment to the opportunity.

### Demand-Reducing

- **Anxiety**: "Will changing the model actually produce better proposals, or am I just spending more for the same output?" Elena has no evidence that Opus writes better SBIR sections than Sonnet. Without visible quality differences, the feature feels like a placebo dial. Also: "What if I pick the wrong level and miss quality I could have had?"
- **Habit**: Elena currently runs everything at one quality level and it "works." She has a workflow. Adding a decision point before every proposal creates cognitive load she does not have time for during deadline pressure.

### Assessment

- **Switch likelihood**: High -- the push is strong (real proposal losses, real money at stake) and the pull is concrete (per-proposal quality control).
- **Key blocker**: Anxiety that quality differences are not visible. The feature must show tangible output differences, not just model names.
- **Key enabler**: The push of losing proposals where quality could have been higher.
- **Design implication**: Profiles must be quick to select (reduce habit friction) and the differences between levels must be observable in output, not just configuration (reduce anxiety).

---

## Forces Analysis: Job 2 -- Control API Costs During Exploratory Work

### Demand-Generating

- **Push**: Marcus Chen at NovaTech spent $4,200 in Claude API costs in Q4 across 8 proposals. His CEO asked "is this sustainable?" Much of that spend was on Wave 0 exploration for topics that were ultimately rejected. Running Opus-tier analysis on 6 topics just to filter them down to 2 is wasteful. At $15-20 per topic for Wave 0, screening 6 costs $90-120 when a $2-3 fast model run would have produced the same go/no-go decision.
- **Pull**: A "lean" profile that routes Wave 0 agents to fast, cheap models. Marcus screens 6 topics for $12-18 instead of $90-120. He reserves budget for the 2 topics that make it to drafting. Monthly API reports show deliberate cost allocation, not uniform burn.

### Demand-Reducing

- **Anxiety**: "What if the cheap model misses a great topic or misjudges fit?" If lean screening produces a false negative -- rating a strong topic as weak -- the cost savings are worthless because Marcus loses a winnable opportunity. The scouting agents need to be good enough to not produce dangerous errors.
- **Habit**: Marcus currently does not think about model selection at all. The tool "just works." Adding a cost-optimization step to the beginning of every exploration session is friction he might skip, falling back to "just run it."

### Assessment

- **Switch likelihood**: High -- the financial push is concrete and recurring (monthly API bills). Small businesses feel this acutely.
- **Key blocker**: Anxiety about false negatives in topic screening. Lean mode must still be "good enough" for go/no-go decisions.
- **Key enabler**: Visible cost tracking. If Marcus can see "this exploration session cost $3.20" after a lean run vs. "$18.40" after a standard run, the value is self-evident.
- **Design implication**: Lean profiles must not degrade critical decision quality. Degradation should affect polish and depth, not directional accuracy. Cost visibility per session or per wave would directly address the push.

---

## Forces Analysis: Job 3 -- Accelerate Iteration Cycles During Drafting

### Demand-Generating

- **Push**: Phil Santos at Apex Engineering finds that the 3-minute wait between writer-reviewer iterations in Wave 4 breaks his creative flow. He is drafting 6 sections in a session. At 2 full review cycles per section, that is 36 minutes of pure waiting. He starts multitasking during waits, loses context, and makes worse editing decisions. Sometimes he skips the review entirely to maintain momentum.
- **Pull**: A lightweight "quick review" mode where the reviewer checks structure, compliance coverage, and flow in 30 seconds instead of running the full evaluator simulation. Phil iterates rapidly on structure, then triggers a deep review when the section is ready. Fast feedback, then thorough feedback.

### Demand-Reducing

- **Anxiety**: "If I use quick review, will I miss something critical that a full review would have caught? Am I building a false sense of security?" Phil worries that lightweight review creates a habit of shipping under-reviewed sections.
- **Habit**: Phil has internalized "2 review cycles per section, then human checkpoint." It is a rhythm. Introducing a variable review depth per iteration disrupts the rhythm and adds a decision: "should this iteration be quick or deep?"

### Assessment

- **Switch likelihood**: Medium -- the push is real (flow disruption) but the habit is strong (established review rhythm). The pull is attractive but the anxiety is non-trivial.
- **Key blocker**: Fear that lightweight review creates false confidence. Design must make it clear that quick review is structural, not a substitute for deep review.
- **Key enabler**: Time pressure. During deadline crunch (4 days remaining), the push overwhelms the habit, and fast iteration becomes essential.
- **Design implication**: Quick and deep review should be complementary, not alternatives. The workflow should encourage "quick iterations during drafting, deep review when ready" as the natural path, not "choose one."

---

## Forces Analysis: Job 4 -- Manage Multiple Proposals at Different Priority Levels

### Demand-Generating

- **Push**: Dr. Elena Vasquez runs 3 proposals simultaneously. They all use the same quality level despite very different stakes: must-win Phase II ($1.7M, 85% fit), moderate Phase I ($250K, 72% fit), and exploratory Phase I ($250K, 58% fit). She is either over-investing in the long-shot or under-investing in the must-win. The multi-proposal workspace (already shipped) namespaces state per proposal but has no quality differentiation.
- **Pull**: Per-proposal rigor settings that persist across sessions. Elena sets AF243-001 to "thorough," N244-012 to "standard," and DA244-003 to "lean." When she switches proposals with `/proposal switch`, the rigor level switches with it. The dashboard shows rigor level alongside fit score and deadline. Resource allocation matches strategic priority.

### Demand-Reducing

- **Anxiety**: "What if I misjudge priority and under-invest in a proposal that turns out to be winnable?" The fit score is an estimate. A 58% fit topic could turn out to be a strong match after deeper research. Locking in a rigor level early might create a self-fulfilling prophecy where lean execution confirms the low-priority assumption.
- **Habit**: Elena currently treats all proposals the same. Her workflow is consistent: same commands, same review depth, same expectations. Per-proposal configuration adds management overhead to an already complex multi-proposal workflow.

### Assessment

- **Switch likelihood**: High -- the multi-proposal workspace already exists and already namespaces per proposal. Adding rigor as another per-proposal setting is a natural extension. The push (misallocated resources across proposals) is strong for anyone running 2+ proposals.
- **Key blocker**: Anxiety about mis-prioritization. Must be easy to change rigor level mid-proposal when priorities shift.
- **Key enabler**: Integration with existing multi-proposal workspace. If rigor is visible on the dashboard and switches with `/proposal switch`, adoption friction is minimal.
- **Design implication**: Rigor must be mutable, not locked. Changing rigor mid-proposal must be as easy as setting it initially. The dashboard should show rigor alongside other per-proposal metadata.

---

## Forces Analysis: Job 5 -- Recover Quality When a Section Fails Review

### Demand-Generating

- **Push**: Phil Santos hits the 2-cycle review cap on Section 3.2. The reviewer recommends escalation to human. Phil knows the section needs better content, not human rewriting. The current escape path is "stop and fix it yourself" -- which defeats the purpose of using the tool. Re-running the entire Wave 4 at a higher rigor level would cost $40+ and take an hour, most of it redundant for sections that already passed review.
- **Pull**: A targeted override: "re-run just this section at thorough rigor." Phil applies surgical quality to the problem area, gets a fresh review, and continues at the baseline rigor for everything else. The tool helps solve quality problems instead of punting them to the human.

### Demand-Reducing

- **Anxiety**: "If I override rigor per-section, will the resulting proposal be inconsistent? Will the thorough-model section read differently from the standard-model sections?" Stylistic inconsistency across sections could be worse than uniform mediocrity.
- **Habit**: The current escalation path (human fixes it) is well-understood. Phil knows how to rewrite a section manually. Using a targeted rigor override is a new workflow he has to learn and trust.

### Assessment

- **Switch likelihood**: Medium -- the push is strong in the moment (frustration with the escalation dead-end) but the frequency is low (most sections pass review). This is a power-user feature.
- **Key blocker**: Stylistic inconsistency anxiety. If the override produces noticeably different prose quality, the cure is worse than the disease.
- **Key enabler**: The pain of hitting escalation on a must-win proposal with deadline pressure. In that moment, Phil will try anything the tool offers.
- **Design implication**: This is a Phase 2 or Phase 3 feature, not MVP. The core profiles (Job 1, 2, 4) must ship first. If this ships, it needs a consistency check after the override.

---

## Forces Analysis: Job 6 -- Understand What Rigor Actually Changes

### Demand-Generating

- **Push**: Marcus Chen tries to pick a rigor level but the labels are opaque. "Standard" vs. "Thorough" -- what does that actually mean? He does not know which agents use which models, or what "double review pass" entails. Without transparency, rigor selection feels like guessing. He either picks the most expensive option "to be safe" (defeating the cost-control purpose) or picks the cheapest "because why pay more for something I don't understand" (defeating the quality purpose).
- **Pull**: A clear comparison table showing, for each profile: model per agent role, review passes, iteration caps, critique loop settings, and indicative cost ranges. Marcus reads it once and makes an informed choice. When he picks "standard," he knows exactly what he is getting and what he is giving up relative to "thorough."

### Demand-Reducing

- **Anxiety**: "The comparison table is so detailed it is overwhelming. I don't know what 'Opus on the strategist vs. Sonnet on the strategist' means in practice. I just want to know: will my proposal be good enough?" Too much transparency can be as paralyzing as too little.
- **Habit**: Marcus has never thought about model selection before. The concept of "rigor profiles" is new. The path of least resistance is to ignore the feature and keep using `inherit` (which becomes the implicit default).

### Assessment

- **Switch likelihood**: Medium-High -- the push is strong (opacity creates poor decisions) but the habit of not-thinking-about-it is also strong. This job is the prerequisite for all others -- if users don't understand profiles, they won't use them.
- **Key blocker**: Information overload. The explanation must be layered: simple summary for quick decisions, detail available on demand.
- **Key enabler**: Sensible defaults. If "standard" is the right choice for 70% of proposals, and the tool suggests it by default, most users never need to go deeper.
- **Design implication**: Progressive disclosure. The command shows profile names with one-line descriptions first. Detail (model per agent, iteration caps) available on request. Sensible default pre-selected based on proposal metadata (fit score, contract value).

---

## Cross-Job Force Summary

| Job | Push Strength | Pull Strength | Anxiety | Habit | Net | Priority |
|-----|--------------|---------------|---------|-------|-----|----------|
| J1: Right-Size Quality | Strong (lost proposals) | Strong (per-proposal control) | Medium (placebo fear) | Medium (one-level workflow) | Strong positive | High |
| J2: Control Costs | Strong (real $ pain) | Strong (visible savings) | Medium (false negatives) | Medium (no-think default) | Strong positive | High |
| J3: Fast Iteration | Medium (flow disruption) | Medium (30s vs 3min) | Medium (false confidence) | Strong (review rhythm) | Moderate positive | Medium |
| J4: Multi-Proposal | Strong (misallocation) | Strong (workspace integration) | Medium (mis-prioritization) | Medium (uniform treatment) | Strong positive | High |
| J5: Recover Quality | Strong in moment | Medium (surgical fix) | Medium (inconsistency) | Medium (manual fallback) | Moderate positive | Low (power user) |
| J6: Understand Rigor | Strong (opacity) | Strong (informed choice) | Medium (overload) | Strong (ignore feature) | Moderate positive | High (prerequisite) |

### Priority Ordering by Force Balance

1. **Job 6** (Understand) -- prerequisite for all others. Without it, nothing switches.
2. **Job 1** (Right-Size Quality) + **Job 2** (Control Costs) -- the twin demand generators. Ship together as the core feature.
3. **Job 4** (Multi-Proposal) -- natural extension, integrates with existing workspace.
4. **Job 3** (Fast Iteration) -- workflow refinement, lower urgency.
5. **Job 5** (Recover Quality) -- power-user edge case, defer to later phase.
