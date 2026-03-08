# Definition of Ready Validation -- Phase C1 User Stories

## US-001: Proposal Status and Reorientation

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "disorienting to return after days away"; domain language used |
| User/persona identified | PASS | Phil Santos, 2-3 proposals/year, multi-session over weeks |
| 3+ domain examples | PASS | 3 examples: happy path (mid-Wave 1), edge case (deadline pressure), error (no proposal) |
| UAT scenarios (3-7) | PASS | 4 scenarios in Given/When/Then |
| AC derived from UAT | PASS | 5 AC items derived from scenarios |
| Right-sized | PASS | 4 scenarios, 1-2 days estimated |
| Technical notes | PASS | State reading, deadline computation, PES thresholds noted |
| Dependencies tracked | PASS | Depends on US-007 (state schema) |

### DoR Status: PASSED

---

## US-002: Start New Proposal from Solicitation

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "time-consuming to manually parse"; "decides in his head" |
| User/persona identified | PASS | Phil Santos, found new solicitation, wants data-driven Go/No-Go |
| 3+ domain examples | PASS | 3 examples with real topic IDs and data (AF243-001, N244-012) |
| UAT scenarios (3-7) | PASS | 6 scenarios covering URL, file, empty corpus, parse error, Go, No-Go |
| AC derived from UAT | PASS | 8 AC items cover all scenario outcomes |
| Right-sized | PASS | 6 scenarios, 2-3 days estimated |
| Technical notes | PASS | Parse strategies, corpus search, company-profile.json noted |
| Dependencies tracked | PASS | Depends on US-003 (corpus), US-007 (state) |

### DoR Status: PASSED

---

## US-003: Directory-Based Corpus Ingestion

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "unacceptable to spend hours organizing and ingesting one at a time" |
| User/persona identified | PASS | Phil Santos, has directories of past work, wants batch ingestion |
| 3+ domain examples | PASS | 3 examples: happy path (7 docs), edge (mixed files), edge (re-ingest) + 1 error (empty dir) |
| UAT scenarios (3-7) | PASS | 4 scenarios |
| AC derived from UAT | PASS | 6 AC items |
| Right-sized | PASS | 4 scenarios, 1-2 days estimated |
| Technical notes | PASS | Supported formats, deduplication, storage path noted |
| Dependencies tracked | PASS | Depends on ADR-005 (corpus storage architecture) |

### DoR Status: PASSED

---

## US-004: Automated Compliance Matrix from Solicitation

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "requirements get missed"; "penalty is disqualification" |
| User/persona identified | PASS | Phil Santos, parsing new solicitation, needs every requirement surfaced |
| 3+ domain examples | PASS | 3 examples: 47 items extracted, manually add missed, low extraction warning |
| UAT scenarios (3-7) | PASS | 4 scenarios |
| AC derived from UAT | PASS | 8 AC items including ambiguity flagging and manual edit |
| Right-sized | PASS | 4 scenarios, 2-3 days estimated |
| Technical notes | PASS | Markdown format, status values, waiver policy, living document noted |
| Dependencies tracked | PASS | Depends on US-002 (solicitation parsing), US-007 (state) |

### DoR Status: PASSED

---

## US-005: TPOC Question Generation and Answer Ingestion

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "one chance to talk to TPOC"; "writes questions from intuition"; "insights live in handwritten notes" |
| User/persona identified | PASS | Phil Santos, preparing for TPOC call, needs strategic questions |
| 3+ domain examples | PASS | 3 examples: full flow (generate + ingest), call never happens, partial notes |
| UAT scenarios (3-7) | PASS | 4 scenarios |
| AC derived from UAT | PASS | 8 AC items covering generation, ingestion, delta, and pending state |
| Right-sized | PASS | 4 scenarios, 2-3 days estimated |
| Technical notes | PASS | Async event handling, write-once immutability, delta propagation noted |
| Dependencies tracked | PASS | Depends on US-004 (compliance matrix), US-007 (state) |

### DoR Status: PASSED

---

## US-006: PES Foundation

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "risky to rely solely on discipline and memory"; "current tools lack structural guardrails" |
| User/persona identified | PASS | Phil Santos, multi-session over weeks, needs structural guarantees |
| 3+ domain examples | PASS | 3 examples: orphaned draft detection, wave ordering, extensibility |
| UAT scenarios (3-7) | PASS | 5 scenarios |
| AC derived from UAT | PASS | 7 AC items including extensibility requirement |
| Right-sized | PASS | 5 scenarios, 2-3 days estimated |
| Technical notes | PASS | Command-layer enforcement, pes-config.json, escape hatch, audit log, extensibility design noted |
| Dependencies tracked | PASS | Depends on US-007 (state) |

### DoR Status: PASSED

---

## US-007: Proposal State Schema and Persistence

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "unacceptable to lose work"; "no tolerance for corruption" |
| User/persona identified | PASS | Phil Santos, multi-session, needs reliable state |
| 3+ domain examples | PASS | 3 examples: state persists, no state file, corrupted state |
| UAT scenarios (3-7) | PASS | 4 scenarios |
| AC derived from UAT | PASS | 6 AC items |
| Right-sized | PASS | 4 scenarios, 1-2 days estimated |
| Technical notes | PASS | Schema versioning, atomic writes, backup strategy noted |
| Dependencies tracked | PASS | No dependencies (foundation) |

### DoR Status: PASSED

---

## US-008: Simplified Compliance Check Command

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "frustrating to open the matrix file, count statuses manually" |
| User/persona identified | PASS | Phil Santos, mid-proposal, wants quick health check |
| 3+ domain examples | PASS | 3 examples: mid-wave check, fresh matrix, no matrix |
| UAT scenarios (3-7) | PASS | 3 scenarios |
| AC derived from UAT | PASS | 4 AC items including extensibility for Phase C2 |
| Right-sized | PASS | 3 scenarios, 1 day estimated |
| Technical notes | PASS | Reads Markdown, phase extensibility noted |
| Dependencies tracked | PASS | Depends on US-004 (compliance matrix) |

### DoR Status: PASSED

---

---

## US-009: Strategy Brief and Wave 1 Checkpoint

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "risky to start writing without a clear, documented strategy"; "mid-course corrections" |
| User/persona identified | PASS | Phil Santos, completing Wave 1, needs documented strategy |
| 3+ domain examples | PASS | 3 examples: full context brief, without TPOC, revision cycle |
| UAT scenarios (3-7) | PASS | 4 scenarios |
| AC derived from UAT | PASS | 6 AC items covering synthesis, TPOC absence, checkpoint, and revision |
| Right-sized | PASS | 4 scenarios, 2-3 days estimated |
| Technical notes | PASS | ADR analogy, reference policy, PES gate noted |
| Dependencies tracked | PASS | Depends on US-004, US-005, US-007 |

### DoR Status: PASSED

---

## Summary

| Story | DoR Status | Scenarios | Est. Days |
|-------|-----------|-----------|-----------|
| US-001 | PASSED | 4 | 1-2 |
| US-002 | PASSED | 6 | 2-3 |
| US-003 | PASSED | 5 | 1-2 |
| US-004 | PASSED | 4 | 2-3 |
| US-005 | PASSED | 4 | 2-3 |
| US-006 | PASSED | 5 | 2-3 |
| US-007 | PASSED | 4 | 1-2 |
| US-008 | PASSED | 3 | 1 |
| US-009 | PASSED | 4 | 2-3 |

All 9 stories pass DoR. Total estimated effort: 14-22 days.
Total scenarios: 39.
