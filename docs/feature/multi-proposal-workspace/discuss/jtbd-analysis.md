# JTBD Analysis: Multi-Proposal Workspace

## Job Classification

**Job Type**: Brownfield improvement (Job 2) -- existing system with established state management needs namespacing for multiple proposals.

**ODI Phase**: Discovery -- the file layout change is fundamental enough that we need to explore alternatives before committing.

**Workflow**: `[research] -> discuss -> design -> distill -> baseline -> roadmap -> split -> execute -> review`

---

## Job Stories

### JS-MPW-01: Manage Multiple Active Proposals

**When** I am responding to 2-3 SBIR solicitations in the same funding cycle and want to keep all my proposal work in one place,
**I want to** start a new proposal without losing or clobbering the state and artifacts of my existing proposals,
**so I can** work on whichever proposal needs attention without context-switching across directories.

#### Functional Job
Maintain isolated state, artifacts, and compliance data for each proposal while sharing corpus, company profile, and partner profiles across all of them.

#### Emotional Job
Feel organized and in control when juggling multiple deadlines -- not anxious about accidentally overwriting work or losing track of where each proposal stands.

#### Social Job
Be seen as a disciplined proposal writer who manages multiple concurrent proposals professionally, not someone scrambling between scattered directories.

#### Forces Analysis
- **Push**: Starting a second proposal in the same directory would clobber `.sbir/proposal-state.json` and overwrite `artifacts/wave-*`. Current workaround is creating separate project directories, which fragments corpus and partner data.
- **Pull**: One workspace where Phil can see all active proposals at a glance, share corpus and profiles, and switch context with a single command.
- **Anxiety**: "Will this break my existing single-proposal setup?" / "Will migration lose my current proposal state?" / "Will the new layout be confusing?"
- **Habit**: One directory per proposal is simple and familiar. Phil has been doing this for years. Separate directories never clobber each other.
- **Assessment**: Switch likelihood HIGH. Push is strong (corpus fragmentation is real pain when writing 2 partnered proposals per year with overlapping past-performance references). Anxiety about backward compatibility is the key design constraint.

---

### JS-MPW-02: Orient Across Multiple Proposals

**When** I return to my proposal workspace after days away and have multiple proposals at different lifecycle stages,
**I want to** see a dashboard of all proposals with their status, deadlines, and next actions,
**so I can** quickly decide which proposal needs my attention first without opening each one individually.

#### Functional Job
Display a summary of all proposals in the workspace: topic ID, title, current wave, deadline, and suggested next action.

#### Emotional Job
Feel oriented and decisive within seconds of returning -- not overwhelmed by having to remember which proposals exist and where each one stands.

#### Social Job
(Not applicable -- solo user context.)

#### Forces Analysis
- **Push**: Currently, Phil has to `cd` into different directories and run `/sbir:continue` in each one. If he forgets a directory, he might miss a deadline.
- **Pull**: A single command shows every proposal's status with deadline proximity sorting.
- **Anxiety**: "What if the dashboard is cluttered with old proposals I finished months ago?"
- **Habit**: Running `/sbir:continue` in one directory is already learned behavior.
- **Assessment**: Switch likelihood HIGH. Directly enables the multi-workspace value proposition.

---

### JS-MPW-03: Switch Active Proposal Context

**When** I am working on one proposal and need to switch to another (because a deadline is closer or a TPOC call just happened for a different topic),
**I want to** switch the plugin's active context to the other proposal,
**so I can** issue commands without prefixing every command with a proposal identifier.

#### Functional Job
Change which proposal's state and artifacts are the active context for subsequent commands. PES enforcement, artifact writes, and status reads all scope to the newly active proposal.

#### Emotional Job
Feel like the context switch is lightweight and safe -- not worried that I accidentally issued a command against the wrong proposal.

#### Social Job
(Not applicable -- solo user context.)

#### Forces Analysis
- **Push**: Without context switching, every command would need a `--proposal af263-042` flag, which is verbose and error-prone.
- **Pull**: A simple `proposal switch af263-042` sets context, and all subsequent commands operate on that proposal.
- **Anxiety**: "What if I forget which proposal is active and write artifacts to the wrong one?"
- **Habit**: Currently there is only one proposal, so context is implicit.
- **Assessment**: Switch likelihood HIGH. The active-context pattern must make the current proposal visible at all times to address anxiety.

---

### JS-MPW-04: Reuse Shared Resources Across Proposals

**When** I am starting a new proposal and have already ingested past proposals, debriefs, and partner profiles for a previous proposal in this workspace,
**I want to** share the corpus, company profile, and partner profiles across all proposals,
**so I can** avoid re-ingesting the same documents and keep a single source of truth for my organizational data.

#### Functional Job
Corpus, company profile, and partner profiles are shared across all proposals in the workspace. Per-proposal state and artifacts remain isolated.

#### Emotional Job
Feel efficient -- not wasteful re-doing work that should carry over between proposals.

#### Social Job
(Not applicable.)

#### Forces Analysis
- **Push**: In the current one-directory-per-proposal setup, Phil re-ingests corpus in every directory. Partner profile changes in one directory do not propagate.
- **Pull**: Ingest once, available everywhere. Update a partner profile once, reflected in all proposals.
- **Anxiety**: "What if a shared corpus change breaks an already-submitted proposal's references?"
- **Habit**: Corpus lives in `.sbir/corpus/` in each project directory.
- **Assessment**: Switch likelihood HIGH. The shared-resource model is a primary motivator.

---

### JS-MPW-05: Handle Completed and Archived Proposals

**When** I have submitted a proposal and started working on the next one,
**I want to** keep the completed proposal's artifacts accessible for debrief and reference without it cluttering my active workspace view,
**so I can** focus on active work while still being able to pull up past proposals when evaluator feedback arrives.

#### Functional Job
Completed proposals remain in the workspace but are visually de-emphasized in the dashboard. They are accessible for debrief (Wave 9) and reference.

#### Emotional Job
Feel uncluttered -- the workspace grows over time but the cognitive load stays manageable.

#### Social Job
(Not applicable.)

#### Forces Analysis
- **Push**: With 2-3 proposals per year across multiple years, a flat list would eventually show 10+ proposals, most completed.
- **Pull**: Active proposals prominent, completed proposals available but secondary.
- **Anxiety**: "What if I need to access a completed proposal's artifacts and they have been moved or hidden?"
- **Habit**: Currently each proposal is a separate directory, so "archiving" means just not `cd`-ing there.
- **Assessment**: Switch likelihood MEDIUM. Important for long-term usability but not blocking first iteration.

---

## Opportunity Scoring

| # | Outcome Statement | Imp. | Sat. | Score | Priority |
|---|-------------------|------|------|-------|----------|
| 1 | Minimize the likelihood of clobbering an existing proposal's state when starting a new one | 95% | 10% | 18.0 | Extremely Underserved |
| 2 | Minimize the time to orient across multiple proposals and decide which needs attention | 90% | 15% | 16.5 | Extremely Underserved |
| 3 | Minimize the time to switch active proposal context | 85% | 20% | 13.8 | Underserved |
| 4 | Minimize the frequency of re-ingesting shared corpus documents | 80% | 30% | 12.0 | Underserved |
| 5 | Minimize the likelihood of issuing a command against the wrong proposal | 85% | 20% | 13.8 | Underserved |
| 6 | Minimize the cognitive load from completed proposals cluttering the workspace | 70% | 40% | 9.1 | Appropriately Served |
| 7 | Maximize the likelihood that existing single-proposal directories continue working | 90% | 50% | 12.6 | Underserved |

### Scoring Method
- Source: single-user analysis (Phil Santos behavioral patterns from problem statement)
- Confidence: Medium (team estimate based on known usage patterns)

### Top Opportunities (Score >= 12)
1. Proposal isolation (18.0) -- JS-MPW-01
2. Multi-proposal orientation (16.5) -- JS-MPW-02
3. Context switching safety (13.8) -- JS-MPW-03
4. Wrong-proposal prevention (13.8) -- JS-MPW-03
5. Backward compatibility (12.6) -- cross-cutting
6. Shared resource reuse (12.0) -- JS-MPW-04

---

## 8-Step Job Map: "Work on Multiple Proposals from One Workspace"

| Step | Activity | Current Pain | Desired Outcome |
|------|----------|-------------|-----------------|
| 1. **Define** | Decide to start a second proposal | "Can I even do this in the same directory?" | Clear mental model of how proposals coexist |
| 2. **Locate** | Find the workspace, identify existing proposals | `cd` between directories, `ls .sbir/` in each | Single dashboard showing all proposals |
| 3. **Prepare** | Create the new proposal namespace | Manually create a new directory, copy corpus | `/proposal new` auto-namespaces, inherits shared resources |
| 4. **Confirm** | Verify the new proposal is isolated | Check that old proposal-state.json is untouched | Status shows both proposals independently |
| 5. **Execute** | Work on whichever proposal needs attention | `cd` to the right directory, run commands | Switch context, run commands against active proposal |
| 6. **Monitor** | Track deadlines and progress across proposals | Open each directory, run status in each | Dashboard with deadline-sorted multi-proposal view |
| 7. **Modify** | Handle exceptions (wrong proposal, accidental clobber) | Manual recovery from corrupted state | Active-proposal indicator prevents mistakes; PES scoping catches errors |
| 8. **Conclude** | Complete or archive a proposal | Leave the directory alone | Mark as completed, de-emphasize in dashboard, accessible for debrief |

### Missing Requirements from Job Map
- Step 1 (Define): Need clear documentation/help text explaining multi-proposal model
- Step 4 (Confirm): Need a verification command or automatic confirmation after `proposal new`
- Step 7 (Modify): Need undo/recovery if commands hit the wrong proposal context
- Step 8 (Conclude): Need explicit archive/complete lifecycle transition

---

## Naming Convention Analysis

### Option A: Topic ID (e.g., `af263-042`)
- Pro: Matches solicitation language; unambiguous within a cycle
- Con: Opaque for user; topic IDs differ by agency format
- Risk: Collision across years if same agency reuses topic numbers

### Option B: User-chosen name (e.g., `directed-energy-2026`)
- Pro: Memorable; user controls namespace
- Con: Requires uniqueness enforcement; user might forget their own naming scheme
- Risk: Typos in switch commands

### Option C: Topic ID with optional alias
- Pro: System uses topic ID as canonical key; user can set a friendly alias
- Con: Two names to track
- Risk: Alias collisions

### Recommendation (for exploration in DESIGN wave)
**Option A (topic ID as default)** with the topic ID extracted from solicitation during `/proposal new`. User can override with `--name` flag. Topic ID is already unique per solicitation cycle and is domain language Phil already uses.

---

## Backward Compatibility Strategy

### Detection
When `/proposal new` or `/sbir:continue` runs, check directory layout:
1. If `.sbir/proposals/` exists -- multi-proposal workspace (new layout)
2. If `.sbir/proposal-state.json` exists at root -- legacy single-proposal layout
3. If neither exists -- fresh workspace

### Legacy Support
Legacy single-proposal directories continue working exactly as today. No forced migration. A future `proposal migrate` command could offer opt-in conversion.

### Migration Path (optional, not required for MVP)
`/proposal migrate` would move `.sbir/proposal-state.json` to `.sbir/proposals/{topic-id}/proposal-state.json` and restructure `artifacts/` accordingly. Reversible with `.bak` files.

---

## Cross-References
- Journey visualization: `journey-multi-proposal-workspace-visual.md`
- Journey schema: `journey-multi-proposal-workspace.yaml`
- Gherkin scenarios: `journey-multi-proposal-workspace.feature`
- User stories: `user-stories.md`
