# Definition of Ready Validation

## Story: US-OGATE-01 (Outline Gate Evaluator)

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Real incident: SF25D-T1201 session, writer agent fabricated section structure without referencing the approved outline. Domain language used throughout (page budgets, compliance mapping, discrimination table). |
| User/persona identified | PASS | Dr. Rafael Moreno (defense tech PI, SF25D-T1201), Dr. Elena Vasquez (af263-042), Dr. James Park (navy-fy26-001), Phil (plugin maintainer). Specific characteristics documented. |
| 3+ domain examples | PASS | 4 examples with real topic IDs (SF25D-T1201, af263-042, navy-fy26-001), real personas, specific file paths, multi-proposal and legacy layouts, cross-directory resolution. |
| UAT scenarios (3-7) | PASS | 5 scenarios in Given/When/Then with concrete data. Covers block, allow, edit, non-interference, and cross-directory resolution. |
| AC derived from UAT | PASS | 8 acceptance criteria, each traceable to one or more scenarios. |
| Right-sized | PASS | 1 evaluator class, 1 rule in config, estimated 1-2 days. 5 scenarios. Simpler than figure pipeline gate (no skip marker, no prerequisite creation exception). |
| Technical notes | PASS | Evaluator pattern, rule_type, config location, cross-directory adapter concern, file_path interface consideration. |
| Dependencies tracked | PASS | Dependency on hook adapter passing file_path (same as figure pipeline gate); dependency on US-OGATE-02 for engine registration and adapter extension. |

### DoR Status: PASSED

---

## Story: US-OGATE-02 (Evaluator Integration with Engine and Config)

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Silent enforcement absence when evaluator not registered. Phil (maintainer) needs correct wiring. Cross-directory resolution is new adapter pattern. |
| User/persona identified | PASS | Phil (plugin maintainer) with specific context (hexagonal architecture, 8 existing evaluators, cross-directory as new pattern). |
| 3+ domain examples | PASS | 4 examples: engine dispatch, config structure, multi-proposal adapter resolution, legacy adapter resolution. Real topic IDs (af263-042). |
| UAT scenarios (3-7) | PASS | 4 scenarios verifying engine dispatch, config presence, and cross-directory resolution for both workspace layouts. |
| AC derived from UAT | PASS | 6 acceptance criteria covering registration, config, interface pattern, domain purity, and adapter cross-directory resolution. |
| Right-sized | PASS | Wiring changes (engine dict + config JSON + adapter extension), estimated 1 day. 4 scenarios. |
| Technical notes | PASS | Specific code locations (engine.py, pes-config.json), interface consideration, cross-directory as adapter concern, first cross-directory check in PES. |
| Dependencies tracked | PASS | Depends on US-OGATE-01 (the evaluator to register). |

### DoR Status: PASSED
