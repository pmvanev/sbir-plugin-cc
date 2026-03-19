# Definition of Ready Validation: Partnership Management

## US-PM-001: Partner Profile Builder Agent

| DoR Item | Status | Evidence |
|----------|--------|---------|
| Problem statement clear | PASS | Domain language: "partner capabilities stored as flat string[]", "manually injects partner specifics into every section". Quantified via Q10 commitment signal. |
| User/persona identified | PASS | Phil Santos, SBIR proposal writer, 2-3 proposals/year, works with CU Boulder/NDSU/SWRI. |
| 3+ domain examples | PASS | 3 examples: SWRI new profile (happy), CU Boulder update (edge), NDSU cancel (error). Real names, real data. |
| UAT scenarios (3-7) | PASS | 5 scenarios covering create, update, preview, cancel, and validation failure. |
| AC derived from UAT | PASS | 6 AC items derived from the 5 scenarios. |
| Right-sized (1-3 days) | PASS | Single agent + skill file. Mirrors existing profile-builder pattern. Estimated 2-3 days. |
| Technical notes | PASS | New agent file, new skill file, storage path, schema extension, soft dependency on company profile. |
| Dependencies tracked | PASS | Company profile (soft dependency). No blocking dependencies. |

### DoR Status: PASSED

---

## US-PM-002: Partnership-Aware Topic Scoring

| DoR Item | Status | Evidence |
|----------|--------|---------|
| Problem statement clear | PASS | "STTR dimension is binary", "partner capabilities invisible to SME dimension", "mentally adjusts scores". |
| User/persona identified | PASS | Phil Santos, scanning solicitations, has partner profiles on file. |
| 3+ domain examples | PASS | 3 examples: STTR elevation (happy), minimal impact (edge), no partner profile (error). Real topic IDs, real scores. |
| UAT scenarios (3-7) | PASS | 4 scenarios covering dual columns, elevation, minimal impact, and missing profile. |
| AC derived from UAT | PASS | 6 AC items derived from scenarios. |
| Right-sized (1-3 days) | PASS | Modifies existing agent + skill. Estimated 1-2 days. |
| Technical notes | PASS | Modifies topic-scout agent and fit-scoring skill. Partner glob pattern. Combined SME computation. |
| Dependencies tracked | PASS | Depends on US-PM-001 (partner profiles must exist). |

### DoR Status: PASSED

---

## US-PM-003: Partnership-Aware Strategy Brief

| DoR Item | Status | Evidence |
|----------|--------|---------|
| Problem statement clear | PASS | "generic teaming section", "manually rewrites every time", "pulling partner details from memory". |
| User/persona identified | PASS | Phil Santos, generating strategy brief for partnered proposal. |
| 3+ domain examples | PASS | 3 examples: CU Boulder auto-generation (happy), SBIR no-partner (edge), missing field (error). |
| UAT scenarios (3-7) | PASS | 4 scenarios covering auto-generation, source citation, missing data, and non-partnered. |
| AC derived from UAT | PASS | 7 AC items derived from scenarios. |
| Right-sized (1-3 days) | PASS | Modifies existing agent + skill. Estimated 1-2 days. |
| Technical notes | PASS | Modifies strategist agent and strategy knowledge skill. Teaming as 7th dimension. |
| Dependencies tracked | PASS | Depends on US-PM-001 (partner profiles) and proposal state partner tracking. |

### DoR Status: PASSED

---

## US-PM-004: Partnership-Aware Approach Generation

| DoR Item | Status | Evidence |
|----------|--------|---------|
| Problem statement clear | PASS | "only considers company capabilities", "approaches that leverage combined strengths not surfaced", "manually identifies combinations". |
| User/persona identified | PASS | Phil Santos, selecting approach for partnered proposal. |
| 3+ domain examples | PASS | 3 examples: CU Boulder acoustics approach (happy), no partner match (edge), STTR 30% violation (error). |
| UAT scenarios (3-7) | PASS | 3 scenarios. Minimum threshold. |
| AC derived from UAT | PASS | 6 AC items. |
| Right-sized (1-3 days) | PASS | Modifies existing agent + skill. Estimated 1-2 days. |
| Technical notes | PASS | Modifies solution-shaper and approach-evaluation skill. Work split stored in approach-brief.md. |
| Dependencies tracked | PASS | Depends on US-PM-001 and proposal state partner tracking. |

### DoR Status: PASSED

---

## US-PM-005: New Partner Readiness Screening

| DoR Item | Status | Evidence |
|----------|--------|---------|
| Problem statement clear | PASS | "burned by partner backing out" (Q8), "no structured way to assess", "discovers problems too late". |
| User/persona identified | PASS | Phil Santos, evaluating new potential partner, wants to detect red flags early. |
| 3+ domain examples | PASS | 3 examples: SWRI caution (happy), all positive (edge), critical red flags (error). Real partner names. |
| UAT scenarios (3-7) | PASS | 5 scenarios covering caution, proceed, do-not-proceed, capability fit, and save. |
| AC derived from UAT | PASS | 7 AC items. |
| Right-sized (1-3 days) | PASS | New command + screening logic within partner-builder agent. Estimated 1-2 days. |
| Technical notes | PASS | New command file. Screening results stored project-level. Conversational format. |
| Dependencies tracked | PASS | No dependencies (standalone). Feeds into US-PM-001 when proceeding. |

### DoR Status: PASSED

---

## US-PM-006: Partner Designation in Proposal State

| DoR Item | Status | Evidence |
|----------|--------|---------|
| Problem statement clear | PASS | "tracks topic but not which partner", "every downstream agent must be told separately", "partner context lost between sessions". |
| User/persona identified | PASS | Phil Santos, starting or resuming partnered proposal. |
| 3+ domain examples | PASS | 3 examples: STTR designation (happy), no profiles (edge), mid-proposal change (error). |
| UAT scenarios (3-7) | PASS | 4 scenarios covering STTR prompt, automatic usage, no-profiles, and partner change. |
| AC derived from UAT | PASS | 5 AC items. |
| Right-sized (1-3 days) | PASS | State schema change + command modifications. Estimated 1 day. |
| Technical notes | PASS | Modifies proposal-state-schema, proposal-new command. New partner-set command. |
| Dependencies tracked | PASS | Depends on US-PM-001 (partner profiles must exist to be selectable). |

### DoR Status: PASSED

---

## US-PM-007: Partnership Content in Proposal Drafting

| DoR Item | Status | Evidence |
|----------|--------|---------|
| Problem statement clear | PASS | "writer produces sections without partner-specific content", "manually inserts all partnership language", "error-prone and time-consuming". |
| User/persona identified | PASS | Phil Santos, drafting sections for partnered proposal. |
| 3+ domain examples | PASS | 3 examples: CU Boulder Technical Approach (happy), non-partnered normal (edge), sparse data (error). |
| UAT scenarios (3-7) | PASS | 3 scenarios. Minimum threshold. |
| AC derived from UAT | PASS | 6 AC items. |
| Right-sized (1-3 days) | PASS | Modifies existing writer agent. Estimated 1-2 days. |
| Technical notes | PASS | Modifies writer agent. Reads partner profile and strategy teaming section. |
| Dependencies tracked | PASS | Depends on US-PM-001, US-PM-003, US-PM-006. |

### DoR Status: PASSED

---

## Summary

| Story | DoR Status | Items Passed | Notes |
|-------|-----------|-------------|-------|
| US-PM-001 | PASSED | 8/8 | Foundation story. Must be implemented first. |
| US-PM-002 | PASSED | 8/8 | First visible value for existing workflow. |
| US-PM-003 | PASSED | 8/8 | High-impact: teaming section is most tedious to write. |
| US-PM-004 | PASSED | 8/8 | Extends approach generation with partner awareness. |
| US-PM-005 | PASSED | 8/8 | Standalone. Addresses Q8 failure case. |
| US-PM-006 | PASSED | 8/8 | Wiring story. Enables cross-agent partner context. |
| US-PM-007 | PASSED | 8/8 | Final integration point in proposal drafting. |

All 7 stories pass the 8-item DoR hard gate.
