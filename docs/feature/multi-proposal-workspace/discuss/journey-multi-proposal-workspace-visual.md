# Journey: Multi-Proposal Workspace -- Visual

## Journey Flow

```
[Trigger: Phil wants      [Step 1: Start       [Step 2: Orient     [Step 3: Switch
 to start 2nd proposal     2nd Proposal]         Across All]         Context]
 in same workspace]             |                     |                  |
                                v                     v                  v
Feels: Cautious          Feels: Reassured      Feels: Oriented     Feels: Confident
 "Will this break        "Both proposals       "I see both          "I know which
  my first one?"          coexist safely"       at a glance"         one I'm on"

                         [Step 4: Work in      [Step 5: Complete    [Step 6: Return
                          Active Context]       a Proposal]          for Debrief]
                               |                     |                  |
                               v                     v                  v
                         Feels: Focused         Feels: Satisfied    Feels: Nostalgic
                          "Commands just         "It's out of         "I can pull up
                           work for this          my active view       everything from
                           proposal"              but not gone"        6 months ago"
```

## Emotional Arc

```
Confidence
    ^
    |                                              *** (Step 5: complete)
    |                                    ****  ***
    |                          **** **** (Step 4: focused work)
    |               **** **** (Step 3: context switch)
    |          ****  (Step 2: orient)
    |     ****  (Step 1: create 2nd)
    | ***  (Trigger: cautious)
    +--------------------------------------------------------> Time
```

Arc pattern: **Confidence Building** -- starts cautious, builds through progressive reassurance.

---

## Step 1: Start Second Proposal

### Context
Phil has an active proposal for AF263-042 in Wave 3 (outlining). He downloads a new solicitation for N244-012 and wants to start evaluating it.

### Command
```
/sbir:proposal new ./solicitations/N244-012.pdf
```

### TUI Mockup

```
+-- /sbir:proposal new -- Multi-Proposal Workspace ----------------------+
|                                                                         |
|  Existing proposals detected in this workspace:                         |
|    1. AF263-042 "Compact Directed Energy"  [Wave 3 -- Outline]          |
|                                                                         |
|  Creating new proposal from N244-012.pdf...                             |
|                                                                         |
|  Topic:     N244-012                                                    |
|  Title:     Autonomous Underwater Vehicle Navigation                    |
|  Agency:    Navy                                                        |
|  Phase:     I                                                           |
|  Deadline:  2026-05-30 (72 days)                                        |
|                                                                         |
|  Proposal namespace: n244-012                                           |
|  State:     .sbir/proposals/n244-012/proposal-state.json                |
|  Artifacts: artifacts/n244-012/                                         |
|                                                                         |
|  Shared resources available:                                            |
|    [ok] Corpus (47 documents)                                           |
|    [ok] Company profile (Santos Engineering LLC)                        |
|    [ok] Partners: CU Boulder, NDSU, SWRI                               |
|                                                                         |
|  Active proposal switched to: n244-012                                  |
|                                                                         |
|  Fit Scoring:                                                           |
|    Subject matter:   72% (partial overlap with AUV past work)           |
|    Past performance: 85% (Navy Phase I experience)                      |
|    Certifications:   100% (SAM.gov, small business)                     |
|                                                                         |
|  Go/No-Go Decision:                                                     |
|    (g) Go   -- proceed with proposal                                    |
|    (n) No-Go -- archive and return to af263-042                         |
|    (d) Defer -- save for later evaluation                               |
|                                                                         |
+-------------------------------------------------------------------------+
```

### Shared Artifacts
- `${existing_proposals}` -- source: `.sbir/proposals/*/proposal-state.json`
- `${topic_id}` -- source: solicitation parsing, stored in per-proposal state
- `${corpus_count}` -- source: `.sbir/corpus/` file count
- `${company_name}` -- source: `~/.sbir/company-profile.json`
- `${partner_list}` -- source: `~/.sbir/partners/*.json`

### Emotional State
- Entry: Cautious -- "Will this mess up my AF263-042 work?"
- Exit: Reassured -- "Both proposals have separate namespaces. Shared resources carry over."

### Integration Checkpoint
After proposal creation, verify:
- AF263-042 state file is untouched at `.sbir/proposals/af263-042/proposal-state.json`
- N244-012 state file exists at `.sbir/proposals/n244-012/proposal-state.json`
- Active proposal pointer updated to `n244-012`
- Shared corpus accessible from new proposal context

---

## Step 2: Orient Across All Proposals

### Context
Phil returns after a weekend. He has two active proposals and wants to know where he stands.

### Command
```
/sbir:continue
```

### TUI Mockup

```
+-- SBIR Proposal Workspace -- Santos Engineering LLC --------------------+
|                                                                         |
|  Active Proposals:                                                      |
|  +---------+--------------------------+--------+------------+---------+ |
|  | Topic   | Title                    | Wave   | Deadline   | Status  | |
|  +---------+--------------------------+--------+------------+---------+ |
|  | N244-012| AUV Navigation           | Wave 0 | 2026-05-30 | [!!] Go | |
|  |         |                          |        | (72 days)  | pending | |
|  +---------+--------------------------+--------+------------+---------+ |
|  | AF263-  | Compact Directed Energy   | Wave 3 | 2026-04-15 | [..] In | |
|  | 042     |                          |        | (27 days)  | outline | |
|  +---------+--------------------------+--------+------------+---------+ |
|                                                                         |
|  Completed Proposals:                                                   |
|    (none)                                                               |
|                                                                         |
|  Currently active: N244-012 (set during last session)                   |
|                                                                         |
|  Suggested actions:                                                     |
|    AF263-042 has a closer deadline (27 days).                           |
|    Consider: /sbir:proposal switch af263-042                            |
|                                                                         |
+-------------------------------------------------------------------------+
```

### Shared Artifacts
- `${proposal_list}` -- source: `.sbir/proposals/*/proposal-state.json` (all proposals)
- `${active_proposal}` -- source: `.sbir/active-proposal` file
- `${company_name}` -- source: `~/.sbir/company-profile.json`

### Emotional State
- Entry: Disoriented -- "Where was I? What needs attention?"
- Exit: Oriented -- "AF263-042 has the closer deadline. I should switch to that."

### Integration Checkpoint
Dashboard must:
- Sort proposals by deadline proximity (closest first in suggested actions)
- Show active proposal indicator
- Display accurate wave status for each proposal independently
- Not modify any state (read-only operation)

---

## Step 3: Switch Active Proposal Context

### Context
Phil sees that AF263-042 has a closer deadline and wants to switch to it.

### Command
```
/sbir:proposal switch af263-042
```

### TUI Mockup

```
+-- Context Switch -------------------------------------------------------+
|                                                                         |
|  Switched from: N244-012 (AUV Navigation)                              |
|  Switched to:   AF263-042 (Compact Directed Energy)                    |
|                                                                         |
|  AF263-042 Status:                                                      |
|    Wave 3: Discrimination & Outline                                     |
|    Deadline: 2026-04-15 (27 days)                                       |
|                                                                         |
|    [ok] Compliance matrix (52 items)                                    |
|    [ok] Strategy brief (approved)                                       |
|    [..] Outline (in progress -- 3/7 sections drafted)                   |
|                                                                         |
|  Next action:                                                           |
|    /sbir:proposal wave outline                                          |
|    Continue the proposal outline.                                       |
|                                                                         |
+-------------------------------------------------------------------------+
```

### Shared Artifacts
- `${active_proposal}` -- source: `.sbir/active-proposal` (updated by switch)
- `${proposal_status}` -- source: `.sbir/proposals/af263-042/proposal-state.json`

### Emotional State
- Entry: Decisive -- "I need to work on the one with the closer deadline"
- Exit: Confident -- "I can see exactly where AF263-042 stands. The active indicator is clear."

### Integration Checkpoint
After switch:
- `.sbir/active-proposal` contains `af263-042`
- All subsequent commands read from `.sbir/proposals/af263-042/`
- PES enforcement scoped to AF263-042 wave state
- Artifacts written to `artifacts/af263-042/`

---

## Step 4: Work in Active Context

### Context
Phil works on AF263-042 normally. All commands operate on the active proposal.

### Command
```
/sbir:proposal wave outline
```

### TUI Mockup

```
+-- Wave 3: Discrimination & Outline -- AF263-042 -----------------------+
|                                                                         |
|  Active proposal: AF263-042 (Compact Directed Energy)                   |
|  Deadline: 2026-04-15 (27 days)                                        |
|                                                                         |
|  [Standard outline workflow -- unchanged from current behavior]         |
|  [Only difference: proposal ID shown in header for orientation]         |
|                                                                         |
+-------------------------------------------------------------------------+
```

### Design Note
The active-proposal indicator in the header is the only visible change during normal workflow. All existing wave commands work identically -- they just read/write to the namespaced path instead of the root path.

### Emotional State
- Entry: Focused -- "I know which proposal I'm working on"
- Exit: Productive -- "The workflow feels exactly the same as before"

### Integration Checkpoint
- All state reads go to `.sbir/proposals/af263-042/`
- All artifact writes go to `artifacts/af263-042/wave-3-outline/`
- PES enforcement reads from the active proposal's state
- Status command shows AF263-042 context

---

## Step 5: Complete a Proposal

### Context
Phil submits AF263-042 (Wave 8 complete). He wants it out of his active view.

### Command
```
/sbir:proposal status
```

### TUI Mockup

```
+-- SBIR Proposal Workspace -- Santos Engineering LLC --------------------+
|                                                                         |
|  Active Proposals:                                                      |
|  +---------+--------------------------+--------+------------+---------+ |
|  | Topic   | Title                    | Wave   | Deadline   | Status  | |
|  +---------+--------------------------+--------+------------+---------+ |
|  | N244-012| AUV Navigation           | Wave 1 | 2026-05-30 | [..] In | |
|  |         |                          |        | (45 days)  | strategy| |
|  +---------+--------------------------+--------+------------+---------+ |
|                                                                         |
|  Completed Proposals:                                                   |
|  +---------+--------------------------+--------+------------+---------+ |
|  | AF263-  | Compact Directed Energy   | Wave 8 | 2026-04-15 | [ok]    | |
|  | 042     |                          |        | (submitted)| Submitted|
|  +---------+--------------------------+--------+------------+---------+ |
|                                                                         |
|  Currently active: N244-012                                             |
|  (Active proposal auto-switched after AF263-042 submission)             |
|                                                                         |
+-------------------------------------------------------------------------+
```

### Emotional State
- Entry: Satisfied -- "I submitted that one"
- Exit: Focused -- "One down, one to go. N244-012 is now my focus."

### Integration Checkpoint
- Completed proposals moved to "Completed" section in dashboard
- Active proposal auto-switches to the remaining active proposal
- Completed proposal artifacts remain at `artifacts/af263-042/` (not moved or hidden)
- Wave 9 (debrief) still accessible for completed proposals

---

## Step 6: Return for Debrief

### Context
Six months later, Phil gets evaluator feedback for AF263-042. He wants to ingest the debrief.

### Command
```
/sbir:proposal switch af263-042
/sbir:proposal debrief ingest ./feedback/af263-042-eval.pdf
```

### TUI Mockup

```
+-- Context Switch -------------------------------------------------------+
|                                                                         |
|  Switched to: AF263-042 (Compact Directed Energy)                      |
|  Status: Submitted (Wave 8 complete, awaiting debrief)                 |
|                                                                         |
|  This proposal was submitted on 2026-04-14.                            |
|  Wave 9 (Post-Submission) is available for debrief ingestion.          |
|                                                                         |
+-------------------------------------------------------------------------+
```

### Emotional State
- Entry: Nostalgic/curious -- "I wonder how we did"
- Exit: Informed -- "Debrief captured, lessons learned for next cycle"

### Integration Checkpoint
- Completed proposals accept context switch for Wave 9 operations
- Debrief artifacts written to `artifacts/af263-042/wave-9-debrief/`
- Lessons learned accessible from corpus for future proposals

---

## Proposed File Layout

```
my-proposals/
  .sbir/
    active-proposal              <-- contains "af263-042" (plain text)
    corpus/                      <-- SHARED across all proposals
      past-proposals/
      debriefs/
    proposals/
      af263-042/                 <-- per-proposal namespace
        proposal-state.json
        compliance-matrix.json
        tpoc-answers.json
      n244-012/
        proposal-state.json
        compliance-matrix.json
        tpoc-answers.json
  artifacts/
    af263-042/                   <-- per-proposal artifacts
      wave-0-intelligence/
      wave-1-strategy/
      ...wave-9-debrief/
    n244-012/
      wave-0-intelligence/
      ...
  ~/.sbir/                       <-- GLOBAL (unchanged)
    company-profile.json
    partners/
      cu-boulder.json
      ndsu.json
      swri.json
```

---

## Error Paths

### Error: Command Issued with No Active Proposal Set

```
WHAT:  No active proposal selected.
WHY:   This workspace has 2 proposals but none is set as active.
       This can happen after migration from a single-proposal layout.
DO:    Run /sbir:proposal switch <topic-id> to select a proposal.
       Available: af263-042, n244-012
```

### Error: Proposal Namespace Collision

```
WHAT:  A proposal with topic ID "af263-042" already exists in this workspace.
WHY:   The solicitation topic ID matches an existing proposal.
DO:    Use --name <custom-name> to create a differently-named proposal:
       /sbir:proposal new ./solicitation.pdf --name af263-042-v2
```

### Error: Legacy Layout Detected

```
WHAT:  Single-proposal layout detected (.sbir/proposal-state.json at root).
WHY:   This workspace was created before multi-proposal support.
       Your existing proposal will continue to work as-is.
DO:    To enable multi-proposal support, run:
       /sbir:proposal migrate
       This will move your existing proposal into a namespace.
       Or continue using single-proposal mode -- it still works.
```
