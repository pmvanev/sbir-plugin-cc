# Definition of Ready Validation -- Rigor Profile

Feature: rigor-profile
Date: 2026-03-23
Phase: 3 -- Requirements Crafting

---

## RP-001: View and Compare Rigor Profiles

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "She finds it impossible to make an informed quality/cost tradeoff because the plugin treats every proposal identically" -- domain language, specific pain point |
| User/persona identified | PASS | Dr. Elena Vasquez, PI at Meridian Defense, 12 employees, 2-3 simultaneous proposals, lost Phase II on Technical Merit |
| 3+ domain examples | PASS | 3 examples: Elena compares profiles for must-win; Elena drills into thorough detail; Marcus views profiles without active proposal |
| UAT scenarios (3-7) | PASS | 3 scenarios: summary comparison, detail view, profiles without active proposal |
| AC derived from UAT | PASS | 5 AC items derived from the 3 scenarios (table display, detail per role, active indicator, cost ranges, role names) |
| Right-sized | PASS | 1-2 days effort, 3 scenarios, single demonstrable feature (read-only display command) |
| Technical notes | PASS | Profile definitions in config/rigor-profiles.json (read-only), no write operations, depends on schema definition |
| Dependencies tracked | PASS | Depends on rigor-profiles.json schema definition (new artifact, defined as part of this feature) |

### DoR Status: PASSED

---

## RP-002: Select Rigor Profile for a Proposal

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "She lost her last Phase II proposal because the debrief cited 'insufficient detail in TRL advancement methodology'" -- real loss, real debrief feedback, domain language |
| User/persona identified | PASS | Dr. Elena Vasquez, PI, lost Phase II, suspects stronger model would help; Marcus Chen, cost-conscious screener |
| 3+ domain examples | PASS | 4 examples: Elena upgrades to thorough; Marcus downgrades to lean; Elena tries invalid name; Elena sets same profile |
| UAT scenarios (3-7) | PASS | 5 scenarios: set with diff, set lean, invalid name, no active proposal, same profile no-op |
| AC derived from UAT | PASS | 7 AC items covering all scenario outcomes (update, diff, preserved artifacts, history, errors, no-op) |
| Right-sized | PASS | 2-3 days effort, 5 scenarios, single demonstrable feature (write profile + display diff) |
| Technical notes | PASS | Atomic write protocol (.tmp/.bak/rename), append-only history, depends on RP-001 and active-proposal resolution |
| Dependencies tracked | PASS | RP-001 (profile definitions), active-proposal resolution (multi-proposal workspace, pre-existing and complete) |

### DoR Status: PASSED

---

## RP-003: Contextual Rigor Suggestion at Proposal Creation

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "He spent $4,200 in API costs last quarter... His CEO asked 'is this sustainable?'" -- real dollar figure, real stakeholder pressure, domain language |
| User/persona identified | PASS | Marcus Chen, Proposal Manager at NovaTech Solutions, 5-6 topics per solicitation, CEO watches costs monthly |
| 3+ domain examples | PASS | 3 examples: high-value gets thorough suggestion; moderate gets lean suggestion; mid-range gets no suggestion |
| UAT scenarios (3-7) | PASS | 4 scenarios: thorough suggestion, lean suggestion, no suggestion, default always standard |
| AC derived from UAT | PASS | 6 AC items covering default, file creation, suggestion thresholds (thorough/lean/none), non-blocking |
| Right-sized | PASS | 1-2 days effort, 4 scenarios, single demonstrable feature (suggestion logic in /proposal new output) |
| Technical notes | PASS | Reads fit_score/contract_value/phase from proposal-state.json, thresholds hardcoded for MVP |
| Dependencies tracked | PASS | /proposal new command (pre-existing, complete), proposal-state.json schema (pre-existing) |

### DoR Status: PASSED

---

## RP-004: Agent Model Resolution from Rigor Profile

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "If agents silently ignore the rigor setting and use their hardcoded defaults, the entire feature is a placebo dial" -- highest opportunity score (16.5), foundational requirement |
| User/persona identified | PASS | Dr. Elena Vasquez, expects thorough rigor to use strongest models; Marcus Chen, expects lean to be cheap; Phil Santos, pre-existing proposal without rigor file |
| 3+ domain examples | PASS | 3 examples: writer uses strongest at thorough; all agents basic at lean; fallback to standard when file missing |
| UAT scenarios (3-7) | PASS | 5 scenarios + 1 @property: writer resolution, reviewer passes, lean reduction, critique cap, missing file fallback, enforcement consistency |
| AC derived from UAT | PASS | 6 AC items covering all 18 agents, resolution chain, reviewer passes, critique cap, fallback, wave output |
| Right-sized | PASS | 2-3 days effort, 6 scenarios, demonstrable by running a wave and seeing model tier in output. Note: the 18 agent frontmatter updates are repetitive but mechanical -- the core logic is the resolution chain. |
| Technical notes | PASS | All 18 agent markdown files need frontmatter update, agent role-to-name mapping required, rigor-profiles.json must define all roles |
| Dependencies tracked | PASS | RP-001 (profile definitions), rigor-profile.json schema (defined in this feature) |

### DoR Status: PASSED

---

## RP-005: Rigor Display in Wave Execution

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "Without visible evidence, rigor feels like a placebo dial" -- addresses primary anxiety from Four Forces |
| User/persona identified | PASS | Dr. Elena Vasquez, running waves after setting thorough; Marcus Chen, running lean screening |
| 3+ domain examples | PASS | 3 examples: Elena sees thorough in Wave 1; Marcus sees lean in Wave 0; Phil sees standard baseline |
| UAT scenarios (3-7) | PASS | 3 scenarios: wave header shows rigor, per-step model tier, lean visibly lighter |
| AC derived from UAT | PASS | 4 AC items covering header, step display, tier names (not model names), review pass count |
| Right-sized | PASS | 1 day effort, 3 scenarios, display-only change to wave execution output |
| Technical notes | PASS | Display-only, no new state written, wave execution code reads rigor profile for display |
| Dependencies tracked | PASS | RP-004 (agent model resolution provides the data to display) |

### DoR Status: PASSED

---

## RP-006: Rigor in Proposal Status and Portfolio View (Phase 2)

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "She cannot see the rigor allocation across her portfolio... When her VP asks 'how are we allocating effort?'" -- portfolio visibility gap, real stakeholder question |
| User/persona identified | PASS | Dr. Elena Vasquez, 3 simultaneous proposals at different priority levels; Phil Santos, single proposal |
| 3+ domain examples | PASS | 3 examples: Elena sees rigor across portfolio; rigor follows switch; single proposal shows rigor in header |
| UAT scenarios (3-7) | PASS | 3 scenarios: portfolio view, switch loads target rigor, single proposal |
| AC derived from UAT | PASS | 5 AC items covering active line, other proposals, fit/cost/rigor together, switch, no bleed |
| Right-sized | PASS | 1-2 days effort, 3 scenarios, additive display change to existing /proposal status |
| Technical notes | PASS | Reads rigor-profile.json from each proposal namespace, switch follows existing per-proposal pattern |
| Dependencies tracked | PASS | RP-002 (rigor stored per-proposal), multi-proposal workspace (pre-existing, complete) |

### DoR Status: PASSED

---

## RP-007: Adjust Rigor Mid-Proposal (Phase 2)

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "After Wave 2 research, the topic turns out to be a stronger fit... She wants to upgrade without re-running Waves 0-2" -- real scenario, real cost concern ($20+, 45 min) |
| User/persona identified | PASS | Dr. Elena Vasquez, re-prioritizing DA244-003 based on new research; Phil Santos, multiple changes tracked |
| 3+ domain examples | PASS | 3 examples: Elena upgrades lean to standard at Wave 3; history recorded for debrief; Phil makes multiple changes |
| UAT scenarios (3-7) | PASS | 3 scenarios: mid-proposal upgrade preserves artifacts, history records wave, re-processing guidance |
| AC derived from UAT | PASS | 6 AC items covering any-wave change, preserved artifacts, old/new wave display, history entry, re-processing guidance |
| Right-sized | PASS | 1-2 days effort, 3 scenarios, builds on RP-002 set command with forward-application messaging |
| Technical notes | PASS | Uses current_wave from proposal-state.json, /proposal iterate is existing functionality |
| Dependencies tracked | PASS | RP-002 (profile set command), proposal-state.json current_wave field (pre-existing) |

### DoR Status: PASSED

---

## RP-008: Rigor Summary in Proposal Debrief (Phase 2)

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "She wants to know if the investment paid off... she needs to correlate rigor settings with reviewer scores" -- post-submission feedback loop, real evaluation concern |
| User/persona identified | PASS | Dr. Elena Vasquez, submitted thorough proposal awaiting results; Marcus Chen, lean screening completed |
| 3+ domain examples | PASS | 3 examples: consistent thorough debrief; mid-proposal change debrief; lean-only screening debrief |
| UAT scenarios (3-7) | PASS | 3 scenarios: consistent profile, mid-proposal change, lean-only |
| AC derived from UAT | PASS | 5 AC items covering summary section, review cycles, critique loops, profile changes, "used throughout" |
| Right-sized | PASS | 1-2 days effort, 3 scenarios, additive section to existing /proposal debrief output |
| Technical notes | PASS | Reads rigor-profile.json and proposal-state.json, review/critique counts must be accumulated during execution |
| Dependencies tracked | PASS | RP-004 (agent resolution tracking), /proposal debrief command (pre-existing). Note: review/critique count accumulation is a prerequisite that RP-004 enables. |

### DoR Status: PASSED

---

## Summary

| Story | DoR Status | Effort Estimate | Scope |
|-------|-----------|-----------------|-------|
| RP-001 | PASSED | 1-2 days | MVP |
| RP-002 | PASSED | 2-3 days | MVP |
| RP-003 | PASSED | 1-2 days | MVP |
| RP-004 | PASSED | 2-3 days | MVP |
| RP-005 | PASSED | 1 day | MVP |
| RP-006 | PASSED | 1-2 days | Phase 2 |
| RP-007 | PASSED | 1-2 days | Phase 2 |
| RP-008 | PASSED | 1-2 days | Phase 2 |

**All 8 stories pass DoR. Ready for handoff to DESIGN wave.**

### MVP Total: 7-11 days (5 stories)

### Phase 2 Total: 3-6 days (3 stories)

### Delivery Order (recommended)

1. **RP-001** (View profiles) -- prerequisite for all others, defines the profile schema
2. **RP-004** (Agent resolution) -- foundational technical requirement, highest opportunity score
3. **RP-002** (Set profile) -- core user interaction, depends on RP-001
4. **RP-003** (Suggestion at creation) -- discoverability, depends on RP-001 schema
5. **RP-005** (Wave display) -- evidence of rigor, depends on RP-004
6. **RP-006** (Status/portfolio) -- Phase 2, depends on RP-002
7. **RP-007** (Mid-proposal adjust) -- Phase 2, depends on RP-002
8. **RP-008** (Debrief summary) -- Phase 2, depends on RP-004

### Deferred Stories (not written -- Jobs 3 and 5)

- Per-section rigor override (Job 5, outcome #20, score 9.5 -- Overserved)
- Quick vs. deep review toggle during drafting (Job 3 -- medium priority, strong habit friction)
- Custom profile creation (Job 6 variant -- niche demand, FR-09 in profiles.json is sufficient)
