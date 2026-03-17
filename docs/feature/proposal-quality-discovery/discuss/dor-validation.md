# Definition of Ready Validation: Proposal Quality Discovery

## US-QD-001: Past Proposal Quality Rating

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | "Elena finds it frustrating that the system tracks win/loss outcomes but never asks about writing quality" -- specific pain, domain language |
| User/persona identified | PASS | "Dr. Elena Vasquez, PI, 12 proposals over 8 years, 5 wins" -- specific characteristics |
| 3+ domain examples | PASS | 3 examples: happy path (rate strong win), edge case (skip forgotten proposal), error (zero past proposals) |
| UAT scenarios (3-7) | PASS | 5 scenarios with concrete Given/When/Then using real data (AF243-001, N244-012) |
| AC derived from UAT | PASS | 6 AC items map to scenarios (quality rating, freeform text, skip, zero proposals, additive) |
| Right-sized | PASS | Estimated 2 days, 5 scenarios, single demo-able flow |
| Technical notes | PASS | Read-only access to company-profile.json, winning-patterns.json storage, legacy profile handling |
| Dependencies tracked | PASS | Depends on company-profile-schema.json past_performance structure (exists) |

### DoR Status: PASSED

---

## US-QD-002: Writing Style Preferences Interview

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | "Marcus finds it inconsistent that proposals by different PIs sound completely different" -- specific pain |
| User/persona identified | PASS | "Marcus Chen, BD lead, manages 3-4 proposals across PIs" -- specific role and context |
| 3+ domain examples | PASS | 3 examples: full interview, custom tone, review-and-edit |
| UAT scenarios (3-7) | PASS | 4 scenarios with real data (Pacific Systems Engineering, tone options, evidence styles) |
| AC derived from UAT | PASS | 6 AC items covering all dimensions, review flow, time constraint |
| Right-sized | PASS | Estimated 1-2 days, 4 scenarios, single interview flow |
| Technical notes | PASS | ~/.sbir/ location, writing_style field population, incremental update support |
| Dependencies tracked | PASS | Standalone artifact, no external dependencies |

### DoR Status: PASSED

---

## US-QD-003: Evaluator Writing Quality Feedback Extraction

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | "Sarah finds it impossible to distinguish between comments about writing quality and content" -- specific differentiation pain |
| User/persona identified | PASS | "Dr. Sarah Kim, research director, most debrief reading experience" -- specific expertise |
| 3+ domain examples | PASS | 3 examples: separate writing/content, override categorization, no feedback available |
| UAT scenarios (3-7) | PASS | 5 scenarios covering auto-categorization, routing, override, pattern detection, skip |
| AC derived from UAT | PASS | 6 AC items mapping to each scenario dimension |
| Right-sized | PASS | Estimated 2-3 days, 5 scenarios, single extraction flow |
| Technical notes | PASS | Keyword matching for auto-categorization, integration with weakness profile schema |
| Dependencies tracked | PASS | Depends on win-loss-analyzer weakness profile schema (exists) |

### DoR Status: PASSED

---

## US-QD-004: Quality Artifact Assembly and Persistence

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | "Elena finds it unsatisfying when systems collect data and then it disappears into a black box" -- specific transparency pain |
| User/persona identified | PASS | "PI or BD Lead who has just completed quality discovery steps" -- clear role and context |
| 3+ domain examples | PASS | 3 examples: full assembly, partial (style only), incremental update |
| UAT scenarios (3-7) | PASS | 5 scenarios covering full/partial creation, merge, confidence, atomic write |
| AC derived from UAT | PASS | 6 AC items covering artifact creation, schema fields, merge, atomic writes, confidence |
| Right-sized | PASS | Estimated 1-2 days, 5 scenarios, single assembly step |
| Technical notes | PASS | ~/.sbir/ location, atomic write pattern, confidence thresholds |
| Dependencies tracked | PASS | Depends on Steps 1-3 (US-QD-001 through 003) |

### DoR Status: PASSED

---

## US-QD-005: Strategist Reads Winning Patterns

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | "Elena finds it frustrating that strategist ignores what worked in past wins" -- forward-feeding pain |
| User/persona identified | PASS | "PI starting a new proposal for an agency with prior submissions" |
| 3+ domain examples | PASS | 3 examples: matching patterns, no agency match, no artifacts |
| UAT scenarios (3-7) | PASS | 3 scenarios -- note: at lower bound of 3-7 range but each is focused |
| AC derived from UAT | PASS | 5 AC items covering load, filter, citation, graceful degradation |
| Right-sized | PASS | Estimated 1 day, 3 scenarios, single read integration |
| Technical notes | PASS | Read-only access, agency matching, universal pattern flag |
| Dependencies tracked | PASS | Depends on US-QD-004, sbir-strategist existing workflow (both exist/planned) |

### DoR Status: PASSED

---

## US-QD-006: Writer Applies Quality Intelligence During Drafting

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | "Elena finds it frustrating that writer uses generic Strunk & White when company has specific winning patterns" |
| User/persona identified | PASS | "PI drafting proposal sections in Waves 3-4" |
| 3+ domain examples | PASS | 3 examples: all three artifacts, partial artifacts, no artifacts |
| UAT scenarios (3-7) | PASS | 4 scenarios covering full integration, partial, fallback, quality alert |
| AC derived from UAT | PASS | 6 AC items covering all artifact types, style influence, alerts, graceful degradation |
| Right-sized | PASS | Estimated 2 days, 4 scenarios, writer skill extension |
| Technical notes | PASS | Loading phase, agency+section matching, guidance vs rules distinction |
| Dependencies tracked | PASS | Depends on US-QD-004, sbir-writer existing workflow |

### DoR Status: PASSED

---

## US-QD-007: Reviewer Checks Quality Profile During Review

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | "Sarah finds it frustrating that reviewer misses writing quality patterns from past debriefs" |
| User/persona identified | PASS | "Research Director reviewing draft sections in Waves 4 or 7" |
| 3+ domain examples | PASS | 3 examples: quality profile match, style compliance, no artifacts |
| UAT scenarios (3-7) | PASS | 3 scenarios -- at lower bound but focused and complete |
| AC derived from UAT | PASS | 6 AC items covering loading, tagging, severity, style checks, graceful degradation |
| Right-sized | PASS | Estimated 1-2 days, 3 scenarios, reviewer skill extension |
| Technical notes | PASS | Loading phase, pattern matching criteria, additive findings |
| Dependencies tracked | PASS | Depends on US-QD-004, sbir-reviewer existing workflow |

### DoR Status: PASSED

---

## US-QD-008: Incremental Quality Learning After Proposal Cycle

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | "Elena finds it frustrating that lessons learned never flow back into company-level quality playbook" |
| User/persona identified | PASS | "PI or BD Lead after completing Wave 9 debrief processing" |
| 3+ domain examples | PASS | 3 examples: update after win, stale patterns, no prior artifacts |
| UAT scenarios (3-7) | PASS | 5 scenarios covering update, staleness, no artifacts, meta-writing extraction, confidence recalculation |
| AC derived from UAT | PASS | 7 AC items covering all scenario dimensions |
| Right-sized | PASS | Estimated 2 days, 5 scenarios, update flow |
| Technical notes | PASS | Reads wave-9-debrief artifacts, staleness threshold, additive updates |
| Dependencies tracked | PASS | Depends on US-QD-004, sbir-debrief-analyst Wave 9 outputs |

### DoR Status: PASSED

---

## Summary

| Story | DoR Status | Scenarios | Est. Days |
|-------|-----------|-----------|-----------|
| US-QD-001 | PASSED | 5 | 2 |
| US-QD-002 | PASSED | 4 | 1-2 |
| US-QD-003 | PASSED | 5 | 2-3 |
| US-QD-004 | PASSED | 5 | 1-2 |
| US-QD-005 | PASSED | 3 | 1 |
| US-QD-006 | PASSED | 4 | 2 |
| US-QD-007 | PASSED | 3 | 1-2 |
| US-QD-008 | PASSED | 5 | 2 |
| **Total** | **8/8 PASSED** | **34** | **12-16** |

All 8 stories pass the Definition of Ready hard gate. The handoff package is ready for peer review.

## MoSCoW Classification

| Priority | Stories | Rationale |
|----------|---------|-----------|
| Must Have | US-QD-001, US-QD-002, US-QD-004 | Core discovery flow: capture quality knowledge and persist artifacts. Without these, no downstream value. |
| Should Have | US-QD-005, US-QD-006, US-QD-007 | Downstream consumption: artifacts are useless without agents reading them. High value, but could ship discovery first and consumption second. |
| Should Have | US-QD-003 | Evaluator feedback extraction adds depth but requires debrief history. Can be added after initial flow works. |
| Could Have | US-QD-008 | Incremental learning compounds value over time. Important but can be manual initially (re-run discover). |

## Recommended Implementation Order

1. US-QD-002 (style interview) -- smallest, standalone, fills the writing_style gap immediately
2. US-QD-001 (past proposal review) -- adds winning patterns from existing profile data
3. US-QD-004 (artifact assembly) -- persists outputs from 1 and 2
4. US-QD-006 (writer consumption) -- first downstream integration, highest daily impact
5. US-QD-007 (reviewer consumption) -- second downstream integration
6. US-QD-005 (strategist consumption) -- third downstream integration
7. US-QD-003 (feedback extraction) -- adds evaluator feedback dimension
8. US-QD-008 (incremental learning) -- closes the feedback loop
