# Definition of Ready Validation: PES Enforcement Wiring

## Story: US-PEW-001 (PDC Gate Enforcement)

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | Phil wastes drafting effort when RED PDC items exist; domain language used (PDC, Tier 1/2, RED/GREEN) |
| User/persona identified | PASS | Phil Santos, small business engineer, entering Wave 5 drafting phase |
| 3+ domain examples | PASS | 5 examples: RED Tier 1 blocks, all GREEN allows, RED Tier 2 blocks, non-Wave-5 unaffected, empty pdc_status |
| UAT scenarios (3-7) | PASS | 5 scenarios with Given/When/Then, real data (AF243-001, TRL justification) |
| AC derived from UAT | PASS | 5 AC items mapped from scenarios |
| Right-sized | PASS | 1 day effort (config rule addition + end-to-end verification), 5 scenarios |
| Technical notes | PASS | Identifies evaluator file, engine dispatch, state field dependency, tool_name matching |
| Dependencies tracked | PASS | PdcGateEvaluator (exists), engine dispatch (exists), pdc_status schema (v2.0.0) |

### DoR Status: PASSED

---

## Story: US-PEW-002 (Deadline Blocking Enforcement)

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | Phil loses track of deadlines working on non-essential waves; domain language (deadline, critical threshold, non-essential waves) |
| User/persona identified | PASS | Phil Santos, working on non-essential waves near submission deadline |
| 3+ domain examples | PASS | 4 examples: blocked near deadline, essential wave allowed, allowed outside threshold, no deadline |
| UAT scenarios (3-7) | PASS | 5 scenarios including invalid date edge case |
| AC derived from UAT | PASS | 5 AC items mapped from scenarios |
| Right-sized | PASS | 1 day effort, 5 scenarios |
| Technical notes | PASS | Identifies date.today() usage, dual check (current_wave + tool_name), non_essential_waves product decision |
| Dependencies tracked | PASS | DeadlineBlockingEvaluator (exists), engine dispatch (exists), topic.deadline (populated by /proposal new), deadlines.critical_days (exists in config) |

### DoR Status: PASSED

---

## Story: US-PEW-003 (Submission Immutability Enforcement)

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | Phil risks modifying submitted proposal artifacts; domain language (submission, immutable, read-only) |
| User/persona identified | PASS | Phil Santos, returning to project after submission |
| 3+ domain examples | PASS | 3 examples: blocked after submit, allowed while drafting, no submission field |
| UAT scenarios (3-7) | PASS | 5 scenarios including submitted-but-not-immutable and fallback message |
| AC derived from UAT | PASS | 5 AC items mapped from scenarios |
| Right-sized | PASS | 1 day effort, 5 scenarios |
| Technical notes | PASS | Identifies tool-name-agnostic blocking, submission state field dependency |
| Dependencies tracked | PASS | SubmissionImmutabilityEvaluator (exists), engine dispatch (exists), submission field (tracked -- populated by submission agent, not yet implemented) |

### DoR Status: PASSED

---

## Story: US-PEW-004 (Corpus Integrity Enforcement)

| DoR Item | Status | Evidence/Issue |
|----------|--------|----------------|
| Problem statement clear | PASS | Phil needs immutable outcome tags for corpus learning integrity; domain language (win/loss, outcome tags, append-only) |
| User/persona identified | PASS | Phil Santos, recording or reviewing proposal outcomes |
| 3+ domain examples | PASS | 4 examples: modification blocked, first assignment allowed, non-outcome tools unaffected, same-value allowed |
| UAT scenarios (3-7) | PASS | 5 scenarios including missing learning field edge case |
| AC derived from UAT | PASS | 6 AC items mapped from scenarios |
| Right-sized | PASS | 1 day effort, 5 scenarios |
| Technical notes | PASS | Identifies tool_name matching, outcome vs requested_outcome_change comparison, no build_block_message (falls through to rule.message) |
| Dependencies tracked | PASS | CorpusIntegrityEvaluator (exists), engine dispatch (exists), learning/requested_outcome_change fields (populated by debrief analyst), engine._build_message fallthrough behavior documented |

### DoR Status: PASSED

---

## Summary

| Story | DoR Status | Scenarios | Est. Effort |
|-------|-----------|-----------|-------------|
| US-PEW-001 PDC Gate | PASSED | 5 | 1 day |
| US-PEW-002 Deadline Blocking | PASSED | 5 | 1 day |
| US-PEW-003 Submission Immutability | PASSED | 5 | 1 day |
| US-PEW-004 Corpus Integrity | PASSED | 5 | 1 day |
| **Total** | **ALL PASSED** | **20** | **~2-3 days** |

All 4 stories pass the 8-item DoR hard gate and are ready for handoff to the DESIGN wave.
