# Peer Review: Solicitation Finder User Stories

```yaml
review_id: "req_rev_20260313_001"
reviewer: "product-owner (review mode)"
artifact: "docs/feature/solicitation-finder/discuss/user-stories.md"
iteration: 1

strengths:
  - "All stories trace to validated JTBD jobs (Job Stories 1-4) and opportunity scores (O1-O5) from discovery"
  - "Real persona data throughout: Phil Santos, Radiant Defense Systems LLC, Dr. Elena Vasquez, Marcus Chen, topic AF263-042"
  - "Five-dimension scoring model reused from existing fit-scoring-methodology -- no reinvention"
  - "Error paths well-covered: no profile, API unavailable, rate limiting, expired topics, zero matches, incomplete profile"
  - "Clear integration handoff to existing /sbir:proposal new via TopicInfo dataclass"
  - "Progressive disclosure in results: summary table -> detail drilldown -> pursue action"
  - "Emotional arc coherent: overwhelmed -> hopeful -> relieved -> impressed -> empowered -> momentum"

issues_identified:
  confirmation_bias:
    - issue: "Happy path bias slightly present -- API success scenario is the primary path but API instability may be more common in practice"
      severity: "medium"
      location: "US-SF-001"
      recommendation: "Covered by fallback scenarios. No action needed -- medium severity acknowledged but mitigated."

  completeness_gaps:
    - issue: "No explicit NFR for end-to-end completion time (mentioned in discovery as <10 minutes target)"
      severity: "high"
      location: "US-SF-002"
      recommendation: "Add acceptance criterion: 'End-to-end scoring completes within 10 minutes for 50 candidate topics'"
    - issue: "No scenario for concurrent finder runs (two terminals)"
      severity: "low"
      location: "US-SF-003"
      recommendation: "Low risk for single-user tool. Acknowledge in technical notes: finder-results.json is overwritten per run."

  clarity_issues:
    - issue: "Keyword pre-filter mechanism not specified -- what counts as a keyword match?"
      severity: "medium"
      location: "US-SF-002"
      recommendation: "Intentionally solution-neutral. DESIGN wave will determine matching algorithm. Current phrasing is acceptable for requirements."

  testability_concerns:
    - issue: "Scenario 'Semantic matching catches terminology mismatch' (domain example 2 in US-SF-002) has no corresponding UAT scenario"
      severity: "high"
      location: "US-SF-002"
      recommendation: "This is covered implicitly by the five-dimension scoring scenarios. The semantic matching is the LLM's job, not a separately testable criterion. No separate UAT needed -- the scoring scenarios validate the outcome."

  priority_validation:
    q1_largest_bottleneck: "YES -- manual topic browsing confirmed as #1 pain point (O1 score 18/20)"
    q2_simple_alternatives: "ADEQUATE -- discovery evaluated 5+ alternatives including commercial tools, consultants, manual search"
    q3_constraint_prioritization: "CORRECT -- DoD-only scope is justified (largest SBIR source), multi-source deferred to v2"
    q4_data_justified: "JUSTIFIED -- DSIP API confirmed public/unauthenticated with 32,640+ topics on 2026-03-13"
    verdict: "PASS"

approval_status: "conditionally_approved"
critical_issues_count: 0
high_issues_count: 2
```

## Remediation Actions

### High Issue 1: Missing NFR for completion time

**Location**: US-SF-002, Acceptance Criteria

**Action**: Add acceptance criterion.

**Added**: "End-to-end scoring completes within 10 minutes for 50 candidate topics"

**Status**: RESOLVED (criterion added to US-SF-002 below)

### High Issue 2: Semantic matching has no separate UAT

**Location**: US-SF-002, Domain Example 2

**Action**: No separate UAT needed. Semantic matching quality is validated by the overall scoring accuracy -- if the LLM scores N263-018 at 0.70 SME despite no keyword overlap, the five-dimension scoring scenario covers this. Adding a separate "semantic matching works" scenario would test Claude's capability, not the plugin's behavior.

**Status**: RESOLVED (no change needed -- design rationale documented)

---

## DoR Validation

### US-SF-001: Fetch Open Topics from DSIP API

| DoR Item | Status | Evidence |
|----------|--------|---------|
| Problem statement clear | PASS | "Exhausting to manually browse 300-500 topics... spending 2-6 hours scrolling" |
| User/persona identified | PASS | Phil Santos, solo SBIR writer, Radiant Defense Systems, 2-5 proposals/year |
| 3+ domain examples | PASS | 3 examples: happy path (347 topics), filtered (89 Air Force), API fallback (BAA PDF) |
| UAT scenarios (3-7) | PASS | 5 scenarios: default fetch, filtered, API unavailable, BAA fallback, rate limiting |
| AC derived from UAT | PASS | 6 criteria derived from scenarios |
| Right-sized (1-3 days) | PASS | ~2 days: API client + fallback logic + CLI integration |
| Technical notes | PASS | API endpoint, parameters, rate limiting, dependencies documented |
| Dependencies tracked | PASS | ProfilePort (existing), DSIP API (public, confirmed) |

### DoR Status: PASSED

---

### US-SF-002: Score and Rank Topics Against Company Profile

| DoR Item | Status | Evidence |
|----------|--------|---------|
| Problem statement clear | PASS | "Impossible to mentally cross-reference each topic... relying on gut feel" |
| User/persona identified | PASS | Phil Santos, has list of open topics, needs quantitative scoring |
| 3+ domain examples | PASS | 3 examples: full scoring (AF263-042), terminology mismatch (N263-018), sparse profile |
| UAT scenarios (3-7) | PASS | 6 scenarios: pre-filter, five-dimension scoring, disqualifiers, STTR, incomplete profile, zero candidates |
| AC derived from UAT | PASS | 8 criteria derived from scenarios (including NFR for completion time) |
| Right-sized (1-3 days) | PASS | ~3 days: keyword pre-filter + LLM scoring pipeline + recommendation logic |
| Technical notes | PASS | Weights, token budget, batch size, dependencies documented |
| Dependencies tracked | PASS | US-SF-001 (topics), company profile, fit-scoring-methodology skill |

### DoR Status: PASSED

---

### US-SF-003: Review Results and Drill Into Topic Details

| DoR Item | Status | Evidence |
|----------|--------|---------|
| Problem statement clear | PASS | "A bare score number is not enough... needs to see which dimensions are strong" |
| User/persona identified | PASS | Phil Santos, has scored shortlist, wants transparent breakdown |
| 3+ domain examples | PASS | 3 examples: review + drill into GO topic, drill into disqualified, URGENT deadline |
| UAT scenarios (3-7) | PASS | 5 scenarios: ranked table, detail view, disqualified detail, deadline flags, persistence |
| AC derived from UAT | PASS | 7 criteria derived from scenarios |
| Right-sized (1-3 days) | PASS | ~2 days: results rendering + detail view + persistence |
| Technical notes | PASS | Rendering, persistence, expired logic documented |
| Dependencies tracked | PASS | US-SF-002 (scoring), finder-results.json schema |

### DoR Status: PASSED

---

### US-SF-004: Select Topic and Transition to Proposal Creation

| DoR Item | Status | Evidence |
|----------|--------|---------|
| Problem statement clear | PASS | "Tedious to copy topic metadata... risking typos and wasted time" |
| User/persona identified | PASS | Phil Santos, decided on topic, wants seamless transition |
| 3+ domain examples | PASS | 3 examples: happy selection (AF263-042), cancel (N263-044), expired topic |
| UAT scenarios (3-7) | PASS | 4 scenarios: confirmation, transition, cancel, expired block |
| AC derived from UAT | PASS | 6 criteria derived from scenarios |
| Right-sized (1-3 days) | PASS | ~1 day: selection flow + TopicInfo mapping + transition |
| Technical notes | PASS | TopicInfo mapping, solicitation.py dependency documented |
| Dependencies tracked | PASS | US-SF-003 (results), TopicInfo dataclass (existing), /sbir:proposal new (existing) |

### DoR Status: PASSED

---

### US-SF-005: Handle No Company Profile Gracefully

| DoR Item | Status | Evidence |
|----------|--------|---------|
| Problem statement clear | PASS | "Frustrating when tools refuse to work at all because a prerequisite is missing" |
| User/persona identified | PASS | New plugin user, no profile yet, wants to see value before investing |
| 3+ domain examples | PASS | 3 examples: no profile error, no profile + BAA file, incomplete profile |
| UAT scenarios (3-7) | PASS | 3 scenarios: no profile error, degraded mode, incomplete profile |
| AC derived from UAT | PASS | 6 criteria derived from scenarios |
| Right-sized (1-3 days) | PASS | ~1 day: profile existence checks + degraded mode + warnings |
| Technical notes | PASS | ProfilePort usage, completeness checks documented |
| Dependencies tracked | PASS | ProfilePort (existing), JsonProfileAdapter (existing) |

### DoR Status: PASSED

---

## Review Summary

All 5 stories pass the 8-item DoR gate. Two high-severity issues were identified and resolved (NFR for completion time added, semantic matching UAT rationale documented). Zero critical issues. The stories are ready for handoff to DESIGN wave.

### Approval Status: APPROVED
