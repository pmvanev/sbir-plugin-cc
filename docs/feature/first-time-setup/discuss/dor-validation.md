# Definition of Ready Validation: First-Time Setup

## Story: US-FTS-001 (Prerequisites Check)

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | "Finds it frustrating to discover missing dependencies mid-setup" -- domain language, specific pain |
| User/persona identified | PASS | Dr. Elena Vasquez, PI at 25-person defense tech startup, first plugin session |
| 3+ domain examples | PASS | 3 examples: all pass (Elena), Python 3.10 (version too old), Git not in PATH (Windows-specific) |
| UAT scenarios (3-7) | PASS | 4 scenarios: all pass, version too old, git missing, multiple missing |
| AC derived from UAT | PASS | 6 AC items map to scenarios (prereq check, version display, fix instructions, halt behavior, no files, time estimate) |
| Right-sized | PASS | 4 scenarios, 1 day effort, single demo-able feature |
| Technical notes | PASS | Python/Git version check commands, Windows compatibility note, auth check TBD |
| Dependencies tracked | PASS | No dependencies (first step) |

### DoR Status: PASSED

---

## Story: US-FTS-002 (Guided Profile Creation)

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | "Finds it daunting to run a separate command with no context about why each field matters" |
| User/persona identified | PASS | Dr. Elena Vasquez (new profile), Marcus Chen (existing), Sarah Kim (cancel) -- three distinct personas |
| 3+ domain examples | PASS | 3 examples with real data: Elena creates via "both" mode (CAGE 7XY3Z, Meridian Photonics), Marcus keeps existing (Pacific Systems Engineering), Sarah cancels |
| UAT scenarios (3-7) | PASS | 5 scenarios: new profile, keep existing, update existing, cancel mid-setup, fresh with backup |
| AC derived from UAT | PASS | 7 AC items cover all scenario outcomes |
| Right-sized | PASS | 5 scenarios, 2 days effort -- delegates heavy lifting to existing profile builder agent |
| Technical notes | PASS | Delegates to sbir-profile-builder, uses JsonProfileAdapter, global path, resume after completion |
| Dependencies tracked | PASS | Depends on US-FTS-001 (documented) |

### DoR Status: PASSED

---

## Story: US-FTS-003 (Guided Corpus Setup)

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | "Has past proposals scattered across directories... finds it confusing to figure out which files the plugin can use" |
| User/persona identified | PASS | Dr. Elena Vasquez (ingests documents), Marcus Chen (skips), Sarah Kim (bad path) |
| 3+ domain examples | PASS | 3 examples with real paths and file counts: Elena ingests 2 dirs (12 docs + 2 skipped), Marcus skips, Sarah typos path |
| UAT scenarios (3-7) | PASS | 5 scenarios: multiple dirs, skip, invalid path, empty dir, re-ingestion |
| AC derived from UAT | PASS | 7 AC items map to all scenario outcomes |
| Right-sized | PASS | 5 scenarios, 1-2 days -- delegates to existing corpus ingestion |
| Technical notes | PASS | Delegates to corpus add logic, comma-separated paths, SHA-256 dedup, project-local .sbir/corpus/ |
| Dependencies tracked | PASS | Depends on US-FTS-002 (documented) |

### DoR Status: PASSED

---

## Story: US-FTS-004 (Validation Summary and Next Steps)

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | "Has no way to know if everything is actually configured correctly... finds it unsettling to proceed without confirmation" |
| User/persona identified | PASS | Dr. Elena Vasquez (full setup), Elena (SAM warning), Marcus Chen (re-run) |
| 3+ domain examples | PASS | 3 examples: all green (14 docs, Meridian Photonics), SAM.gov inactive warning, Marcus re-runs existing |
| UAT scenarios (3-7) | PASS | 5 scenarios: all pass, SAM warning, empty corpus, re-run detection, next steps |
| AC derived from UAT | PASS | 8 AC items cover validation re-check, indicators, warnings, status, next steps, re-run |
| Right-sized | PASS | 5 scenarios, 1-2 days effort |
| Technical notes | PASS | JsonProfileAdapter, corpus index, env var check, status computation logic |
| Dependencies tracked | PASS | Depends on US-FTS-001, 002, 003 (documented) |

### DoR Status: PASSED

---

## Story: US-FTS-005 (API Key Configuration Guidance)

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | "Does not know what the Gemini API key is for or whether she needs it right now" |
| User/persona identified | PASS | Dr. Elena Vasquez (skip, instructions), Marcus Chen (already has key) |
| 3+ domain examples | PASS | 3 examples: Elena skips, Marcus has key, Elena reads instructions |
| UAT scenarios (3-7) | PASS | 3 scenarios -- at lower bound but appropriate for single-step optional config |
| AC derived from UAT | PASS | 6 AC items cover detection, explanation, skip, instructions, auto-continue |
| Right-sized | PASS | 3 scenarios, 1 day effort -- smallest story in the set |
| Technical notes | PASS | Env var check, no validation, ai.google.dev reference, shell-specific syntax note |
| Dependencies tracked | PASS | Depends on US-FTS-003 (documented) |

### DoR Status: PASSED

---

## Overall DoR Summary

| Story | Status | Issues |
|-------|--------|--------|
| US-FTS-001 | PASSED | None |
| US-FTS-002 | PASSED | None |
| US-FTS-003 | PASSED | None |
| US-FTS-004 | PASSED | None |
| US-FTS-005 | PASSED | None |

All 5 stories pass the 8-item DoR hard gate. Ready for DESIGN wave handoff.

---

## Anti-Pattern Scan

| Anti-Pattern | Check | Result |
|---|---|---|
| Implement-X | Stories start from user pain? | PASS -- all stories start with persona + situation + pain |
| Generic data | Real names and data throughout? | PASS -- Dr. Elena Vasquez, Marcus Chen, Sarah Kim, Meridian Photonics, Pacific Systems Engineering, CAGE 7XY3Z |
| Technical AC | AC describes observable outcomes? | PASS -- no technology prescriptions in AC (auth check mechanism explicitly deferred to DESIGN) |
| Oversized story | All stories 3-7 scenarios, 1-3 days? | PASS -- range is 3-5 scenarios, 1-2 days each |
| Abstract requirements | All stories have 3+ concrete examples? | PASS -- every story has 3 examples with real data |
