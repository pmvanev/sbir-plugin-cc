# Definition of Ready Validation: dsip-api-complete

## Story: US-DSIP-01 -- Correct Search Query Format

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Agent receives 32,638 unfiltered topics with numeric IDs; domain language used throughout |
| User/persona identified | PASS | sbir-topic-scout agent calling dsip_cli.py via Bash |
| 3+ domain examples | PASS | 4 examples: happy path, pre-release, no filter, zero results |
| UAT scenarios (3-7) | PASS | 5 scenarios covering format, hash IDs, status mapping, default, metadata |
| AC derived from UAT | PASS | 6 criteria each traced to scenarios |
| Right-sized | PASS | 1-2 days; 5 scenarios; single adapter file change |
| Technical notes | PASS | searchParam encoding, User-Agent, field mapping documented |
| Dependencies tracked | PASS | No dependencies (first in sequence) |

### DoR Status: PASSED

---

## Story: US-DSIP-02 -- Structured Topic Details via API

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | PDF extraction is lossy, misses structured fields needed for scoring |
| User/persona identified | PASS | sbir-topic-scout agent needing technology_areas and ITAR for scoring |
| 3+ domain examples | PASS | 3 examples: happy path with A254-049, ITAR topic, 500 error |
| UAT scenarios (3-7) | PASS | 3 scenarios: structured details, richer than PDF, failure isolation |
| AC derived from UAT | PASS | 5 criteria traced to scenarios |
| Right-sized | PASS | 1-2 days; 3 scenarios; enrichment adapter change |
| Technical notes | PASS | HTML preservation, keyword parsing, referenceDocuments noted |
| Dependencies tracked | PASS | Depends on US-DSIP-01 (hash IDs) -- documented |

### DoR Status: PASSED

---

## Story: US-DSIP-03 -- Topic Q&A Retrieval

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Zero Q&A visibility; A254-049 has 7 entries with radar specs invisible to agent |
| User/persona identified | PASS | sbir-topic-scout agent + Dr. Sarah Chen (indirect) |
| 3+ domain examples | PASS | 3 examples: 7-entry happy path, zero-question skip, malformed JSON fallback |
| UAT scenarios (3-7) | PASS | 5 scenarios: fetch, double-parse, skip, malformed fallback, failure isolation |
| AC derived from UAT | PASS | 6 criteria traced to scenarios |
| Right-sized | PASS | 1-2 days; 5 scenarios; new endpoint + parsing logic |
| Technical notes | PASS | Nested JSON format, oembed edge case, timestamp normalization documented |
| Dependencies tracked | PASS | Depends on US-DSIP-01, US-DSIP-02 -- documented |

### DoR Status: PASSED

---

## Story: US-DSIP-04 -- Solicitation and Component Instruction Documents

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | No access to BAA preface or component annex; cannot assess submission requirements |
| User/persona identified | PASS | sbir-topic-scout agent + Dr. Sarah Chen needing page limits and eval criteria |
| 3+ domain examples | PASS | 3 examples: ARMY happy path, missing component, shared cache |
| UAT scenarios (3-7) | PASS | 5 scenarios: BAA preface, component, missing, cache, failure |
| AC derived from UAT | PASS | 6 criteria traced to scenarios |
| Right-sized | PASS | 2-3 days; 5 scenarios; new endpoints + PDF extraction + caching |
| Technical notes | PASS | URL construction, PDF sizes, rate limiting, baaInstructions hint documented |
| Dependencies tracked | PASS | Depends on US-DSIP-01 (search metadata) -- documented |

### DoR Status: PASSED

---

## Story: US-DSIP-05 -- CLI and Agent Skill Update

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Skill documents old behavior; CLI output missing new fields; agent cannot learn new capabilities |
| User/persona identified | PASS | sbir-topic-scout agent learning from skill; future developers maintaining CLI |
| 3+ domain examples | PASS | 3 examples: agent reads skill, detail with hash ID, completeness metrics |
| UAT scenarios (3-7) | PASS | 3 scenarios: new fields, detail command, skill documentation |
| AC derived from UAT | PASS | 4 criteria traced to scenarios |
| Right-sized | PASS | 1 day; 3 scenarios; documentation and output format update |
| Technical notes | PASS | File paths, no new flags, dependency chain documented |
| Dependencies tracked | PASS | Depends on US-DSIP-01 through US-DSIP-04 -- documented |

### DoR Status: PASSED

---

## Summary

| Story | DoR Status | Effort Estimate | Scenario Count |
|-------|-----------|----------------|----------------|
| US-DSIP-01 | PASSED | 1-2 days | 5 |
| US-DSIP-02 | PASSED | 1-2 days | 3 |
| US-DSIP-03 | PASSED | 1-2 days | 5 |
| US-DSIP-04 | PASSED | 2-3 days | 5 |
| US-DSIP-05 | PASSED | 1 day | 3 |

Total: 5 stories, 21 UAT scenarios, 6-10 days estimated effort.

Delivery order: US-DSIP-01 -> US-DSIP-02 -> US-DSIP-03 -> US-DSIP-04 -> US-DSIP-05

US-DSIP-02, US-DSIP-03, and US-DSIP-04 can be parallelized after US-DSIP-01 is complete (all depend on hash IDs from search). US-DSIP-05 is last (documentation update after all behavior changes).
