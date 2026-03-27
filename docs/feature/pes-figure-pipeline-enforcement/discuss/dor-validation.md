# Definition of Ready Validation

## Story: US-FPIPE-01 (Figure Pipeline Gate Evaluator)

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Real incident: SF25D-T1201 session, formatter hand-coded inline SVGs bypassing pipeline. Domain language used throughout. |
| User/persona identified | PASS | Dr. Rafael Moreno (defense tech PI, SF25D-T1201) and Phil (plugin maintainer). Specific characteristics documented. |
| 3+ domain examples | PASS | 4 examples with real topic IDs (SF25D-T1201, af263-042), real personas, specific file paths, multi-proposal and legacy layouts. |
| UAT scenarios (3-7) | PASS | 5 scenarios in Given/When/Then with concrete data. |
| AC derived from UAT | PASS | 8 acceptance criteria, each traceable to one or more scenarios. |
| Right-sized | PASS | 1 evaluator class, 1 rule in config, estimated 1-2 days. 5 scenarios. |
| Technical notes | PASS | Evaluator pattern, rule_type, config location, file_path interface consideration, dependency on hook adapter. |
| Dependencies tracked | PASS | Dependency on hook adapter passing file_path; dependency on US-FPIPE-03 for engine registration. |

### DoR Status: PASSED

---

## Story: US-FPIPE-02 (Style Profile Gate Evaluator)

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Real incident: SF25D-T1201 session, style analysis skipped entirely. Domain language used. |
| User/persona identified | PASS | Dr. Rafael Moreno, Dr. Elena Vasquez (af263-042), Dr. James Park (navy-fy26-001). Three distinct personas showing different paths. |
| 3+ domain examples | PASS | 4 examples: blocked without profile, allowed with profile, allowed with skip marker, writing style-profile.yaml itself. Real topic IDs and personas. |
| UAT scenarios (3-7) | PASS | 5 scenarios in Given/When/Then with concrete data. |
| AC derived from UAT | PASS | 7 acceptance criteria, each traceable to scenarios. |
| Right-sized | PASS | 1 evaluator class, 1 rule in config, estimated 1-2 days. 5 scenarios. |
| Technical notes | PASS | Evaluator pattern, rule_type, state field access, file_path consideration, dependency on US-FPIPE-01. |
| Dependencies tracked | PASS | Dependency on US-FPIPE-01 (pipeline gate must also pass); dependency on US-FPIPE-03 for registration. |

### DoR Status: PASSED

---

## Story: US-FPIPE-03 (Evaluator Integration with Engine and Config)

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Silent enforcement absence when evaluators not registered. Phil (maintainer) needs correct wiring. |
| User/persona identified | PASS | Phil (plugin maintainer) with specific context (hexagonal architecture, existing patterns). |
| 3+ domain examples | PASS | 3 examples: engine dispatch, config structure, silent degradation for unregistered types. |
| UAT scenarios (3-7) | PASS | 3 scenarios verifying engine dispatch and config presence. |
| AC derived from UAT | PASS | 6 acceptance criteria covering registration, config, interface pattern, and domain purity. |
| Right-sized | PASS | Wiring changes only (engine dict + config JSON), estimated half day. 3 scenarios. |
| Technical notes | PASS | Specific code locations (engine.py lines 38-44, pes-config.json), interface extension design decision flagged for DESIGN wave. |
| Dependencies tracked | PASS | Depends on US-FPIPE-01 and US-FPIPE-02 (the evaluators to register). |

### DoR Status: PASSED
