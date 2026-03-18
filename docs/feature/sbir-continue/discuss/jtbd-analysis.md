# JTBD Analysis: sbir-continue

## Job Classification

**Job Type**: Brownfield (Improve Existing System)
**Entry Point**: discuss (discovery needed -- cross-cutting command spanning entire lifecycle)
**Rationale**: The SBIR proposal plugin exists with 10 waves, existing state management, and established commands. `/sbir:continue` adds a cross-cutting navigation capability. Discovery is needed because the command must handle every possible lifecycle state and the emotional experience of "returning" varies dramatically by context.

---

## Job Stories

### JS-01: Resume After Session Break

**When** I return to Claude Code after being away from my SBIR proposal for hours or days,
**I want to** immediately understand where I left off and what to do next,
**so I can** resume productive work within seconds instead of spending minutes re-orienting myself.

#### Functional Job
Detect current proposal lifecycle position and present the correct next action with one command.

#### Emotional Job
Feel confident and grounded upon return -- not lost, not anxious about forgotten context, not overwhelmed by choices.

#### Social Job
Demonstrate to myself (and any collaborators reviewing progress) that the proposal effort is organized and under control.

#### Forces Analysis
- **Push**: Currently, returning users must remember what wave they were in, which command to run next, and what artifacts exist. `/proposal status` reports state but does not resume -- it shows a dashboard, not a call to action.
- **Pull**: A single command that reads state, determines the right next step, and either starts it or tells the user exactly what to type. Zero cognitive load on return.
- **Anxiety**: "Will it skip something I need?" or "Will it push me forward when I want to review what I did last time?"
- **Habit**: Users currently rely on `/proposal status` plus manual memory of which command to run. Some may prefer the explicit control of choosing their own command.

---

### JS-02: First-Time User Without Setup

**When** I type `/sbir:continue` in a project that has no SBIR configuration at all,
**I want to** be guided to the right starting point,
**so I can** begin the proposal process without having to know which setup command exists.

#### Functional Job
Detect missing prerequisites (no profile, no proposal state) and route to `/sbir:setup`.

#### Emotional Job
Feel welcomed rather than blocked -- the system meets me where I am instead of throwing an error.

#### Social Job
Not feel foolish for typing the wrong command or not knowing the setup sequence.

#### Forces Analysis
- **Push**: Error messages like "No active proposal found. Start with /proposal new" require the user to already know the command vocabulary. First-time users do not have this vocabulary.
- **Pull**: A command that always works, regardless of where you are in the lifecycle -- the universal entry point.
- **Anxiety**: "Am I going to get a cryptic error because I have not set something up yet?"
- **Habit**: New users have no habit yet -- this is their first interaction. The command should create a positive first impression.

---

### JS-03: Resume Incomplete Setup

**When** I started the setup wizard but did not finish (profile exists but no corpus, or profile is incomplete),
**I want to** pick up where I left off in setup,
**so I can** complete configuration without repeating steps I already finished.

#### Functional Job
Detect partial setup state (profile present/absent, corpus populated/empty, API key configured/missing) and resume the setup wizard from the incomplete step.

#### Emotional Job
Feel that my prior effort was not wasted -- the system remembers what I already did.

#### Social Job
Not feel like the system is punishing me for having left setup early.

#### Forces Analysis
- **Push**: Currently, re-running `/sbir:setup` re-checks everything from scratch. While it is idempotent (detects existing config), it still walks through all steps. The user must press (k) keep for things already done.
- **Pull**: Jump directly to the first incomplete setup step with a brief summary of what is already configured.
- **Anxiety**: "Will it overwrite my profile or corpus if I run setup again?"
- **Habit**: Users may re-run `/sbir:setup` manually, expecting it to know where they left off. The setup wizard already handles this reasonably but requires explicit navigation through each step.

---

### JS-04: Resume Mid-Wave Work

**When** I am partway through a wave (e.g., compliance matrix generated but TPOC questions not yet created, or two of three sections drafted),
**I want to** see what I have completed in the current wave and what remains,
**so I can** pick up the next incomplete task without guessing.

#### Functional Job
Read wave-specific state (compliance matrix status, TPOC status, strategy brief status, draft statuses per volume, review findings) and identify the next incomplete task within the current wave.

#### Emotional Job
Feel in control of progress -- see the finish line for this wave and know exactly how far I am.

#### Social Job
Maintain momentum on the proposal without having to consult external notes or checklists.

#### Forces Analysis
- **Push**: `/proposal status` shows wave-level progress but does not drill into within-wave task completion. A user in Wave 4 with two of three volumes drafted has to remember which volume is next.
- **Pull**: Within-wave task awareness that says "Technical volume: approved. Management volume: in review. Cost volume: not started. Run `/sbir:proposal draft cost` to continue."
- **Anxiety**: "What if it skips the TPOC call I have not had yet?" (async events complicate linear progress)
- **Habit**: Users currently check `/proposal status` then mentally map to the next command. This works but requires domain knowledge of the wave structure.

---

### JS-05: Transition Between Waves

**When** I have completed all tasks and passed the exit gate for the current wave,
**I want to** be guided to start the next wave,
**so I can** maintain momentum without having to look up what the next wave involves.

#### Functional Job
Detect that the current wave is completed (exit gate approved), identify the next wave, and present what it involves with the command to start it.

#### Emotional Job
Feel a sense of accomplishment for completing a wave and excitement about the next phase -- a natural transition point that celebrates progress.

#### Social Job
Track my velocity across waves to demonstrate proposal progress to stakeholders or collaborators.

#### Forces Analysis
- **Push**: After approving a wave checkpoint, the system currently returns to the generic status view. The user must know that Wave 2 follows Wave 1 and which command initiates it.
- **Pull**: A celebratory transition moment -- "Wave 1 complete! You have a strategy brief, compliance matrix, and TPOC data. Wave 2 (Research) is next. Run `/sbir:proposal wave research` or type `/sbir:continue` to begin."
- **Anxiety**: "Did I really finish everything in this wave? Is it safe to move on?"
- **Habit**: Users currently use `/proposal wave <name>` to manually transition. This requires knowing wave names and order.

---

### JS-06: Post-Submission and Completion

**When** my proposal has been submitted (Wave 8 confirmed) or the debrief is complete (Wave 9 done),
**I want to** know what to do next,
**so I can** either begin post-submission activities or start a new proposal cycle.

#### Functional Job
Detect post-submission or completed state and guide to debrief ingestion (Wave 9) or suggest starting a new proposal.

#### Emotional Job
Feel closure on the completed proposal and openness to the next opportunity -- not abandoned by the tool after submission.

#### Social Job
Demonstrate a complete proposal lifecycle, including lessons learned (debrief), to improve future proposals.

#### Forces Analysis
- **Push**: After submission, the tool has no natural next step. The user is left wondering "now what?" The debrief capability exists but is not proactively surfaced.
- **Pull**: Guide the user through the complete lifecycle including post-submission, then suggest starting fresh when truly done.
- **Anxiety**: "Is there anything I forgot before submission?" (answered by Wave 7-8, but worth reassuring)
- **Habit**: Users may forget about debrief entirely and just start a new proposal. The tool should gently remind them that debriefs improve future proposals.

---

## Opportunity Scoring

| # | Outcome Statement | Imp. (%) | Sat. (%) | Score | Priority |
|---|-------------------|----------|----------|-------|----------|
| 1 | Minimize the time to identify the correct next action upon returning to a proposal | 95 | 30 | 16.0 | Extremely Underserved |
| 2 | Minimize the likelihood of running the wrong command for the current lifecycle state | 90 | 40 | 14.0 | Underserved |
| 3 | Minimize the time to resume productive work after a session break | 90 | 35 | 14.5 | Underserved |
| 4 | Minimize the likelihood of a first-time user encountering a dead-end error | 85 | 50 | 12.0 | Appropriately Served |
| 5 | Minimize the time to complete setup after a partial interruption | 75 | 45 | 10.5 | Appropriately Served |
| 6 | Minimize the likelihood of skipping an incomplete task within a wave | 80 | 25 | 13.5 | Underserved |
| 7 | Maximize the likelihood that wave transitions feel like progress milestones | 70 | 20 | 12.0 | Appropriately Served |
| 8 | Minimize the likelihood of forgetting post-submission activities (debrief) | 65 | 15 | 11.5 | Appropriately Served |

### Scoring Method
- Importance: estimated % of users rating 4+ on 5-point scale (team estimate based on persona analysis of Phil Santos)
- Satisfaction: estimated % of users rating 4+ with current `/proposal status` approach
- Score: Importance + max(0, Importance - Satisfaction)
- Priority: Extremely Underserved (15+), Underserved (12-15), Appropriately Served (10-12), Overserved (<10)

### Data Quality Notes
- Source: team estimates based on persona (Phil Santos) and existing command usage patterns
- Sample size: 1 primary persona
- Confidence: Medium (team estimate, single persona)

### Top Opportunities (Score >= 12)
1. Next-action identification upon return -- Score: 16.0 -- JS-01, JS-04
2. Resuming productive work -- Score: 14.5 -- JS-01, JS-04, JS-05
3. Avoiding wrong command -- Score: 14.0 -- JS-01, JS-02, JS-04
4. Detecting incomplete within-wave tasks -- Score: 13.5 -- JS-04
5. First-time user routing -- Score: 12.0 -- JS-02
6. Wave transition celebration -- Score: 12.0 -- JS-05

---

## Job Map (8-Step Universal)

### 1. Define: Determine what state the proposal is in
- User needs to know: Is there a proposal? Is setup complete? What wave? What tasks within the wave?
- Outcome: "Minimize the time to determine current lifecycle position"

### 2. Locate: Find the state information
- User needs: `.sbir/proposal-state.json`, `~/.sbir/company-profile.json`, `.sbir/corpus/` directory
- Outcome: "Minimize the likelihood of missing a relevant state signal"

### 3. Prepare: No preparation needed (read-only command)
- The command itself requires no setup -- it reads existing state
- Outcome: "Minimize the time between typing the command and seeing results"

### 4. Confirm: Validate that the detected state is accurate
- User needs to trust the assessment: "Am I really in Wave 4? Did I really finish the compliance matrix?"
- Outcome: "Minimize the likelihood of an incorrect state assessment"

### 5. Execute: Present the next action and optionally begin it
- Core action: display context-aware guidance with the exact command to run
- Outcome: "Minimize the number of steps between continue and productive work"

### 6. Monitor: Track whether the suggested action is correct
- User verifies the suggestion makes sense: "Yes, I should draft the cost volume next"
- Outcome: "Minimize the likelihood of following an incorrect suggestion"

### 7. Modify: Handle cases where the suggestion is wrong
- User disagrees: "No, I want to review the technical volume again before moving on"
- Outcome: "Minimize the effort to override the suggested next action"

### 8. Conclude: Begin the suggested work or acknowledge the state
- User either runs the suggested command or navigates manually
- Outcome: "Minimize the friction between receiving guidance and acting on it"
