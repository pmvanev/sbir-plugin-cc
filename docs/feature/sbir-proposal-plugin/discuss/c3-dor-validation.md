# Definition of Ready Validation -- Phase C3 User Stories

## US-010: Visual Asset Generation from Outline Placeholders

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "tedious to create each figure manually"; "30-60 minutes per figure"; "cross-references break" |
| User/persona identified | PASS | Phil Santos, all sections approved, entering Wave 5 |
| 3+ domain examples | PASS | 3 examples: Mermaid diagram generation, external brief for photo, cross-reference mismatch |
| UAT scenarios (3-7) | PASS | 5 scenarios in Given/When/Then |
| AC derived from UAT | PASS | 7 AC items derived from scenarios |
| Right-sized | PASS | 5 scenarios, 2-3 days estimated |
| Technical notes | PASS | Generation methods (Mermaid, SVG, Graphviz, Gemini API), external brief fallback, cross-reference tracking |
| Dependencies tracked | PASS | Depends on approved outline (Wave 3), approved sections (Wave 4), PES PDC gate |

### DoR Status: PASSED

---

## US-011: Document Formatting and Volume Assembly

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "dreads the formatting phase"; "2-3 hours of mechanical work"; "returned for wrong font size" |
| User/persona identified | PASS | Phil Santos, all figures approved, entering Wave 6 |
| 3+ domain examples | PASS | 3 examples: happy path formatting (AF243-001), page count exceeded, compliance missing item |
| UAT scenarios (3-7) | PASS | 7 scenarios covering formatting, figures, jargon, pages, compliance, assembly |
| AC derived from UAT | PASS | 9 AC items cover all scenario outcomes |
| Right-sized | PASS | 7 scenarios, 2-3 days estimated |
| Technical notes | PASS | Template-based approach, output medium selection, compliance matrix as living document |
| Dependencies tracked | PASS | Depends on US-010 (figures), US-004 (compliance matrix), outline (Wave 3) |

### DoR Status: PASSED

---

## US-012: Final Review with Simulated Government Evaluator

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "sole writer"; "no one to do a proper red team review"; AF241-087 debrief quote |
| User/persona identified | PASS | Phil Santos, assembled proposal ready, entering Wave 7 |
| 3+ domain examples | PASS | 3 examples: full review with findings (AF243-001), no past debriefs, two iteration cycles |
| UAT scenarios (3-7) | PASS | 6 scenarios covering simulation, red team, debrief check, no debriefs, iteration, sign-off |
| AC derived from UAT | PASS | 8 AC items derived from scenarios |
| Right-sized | PASS | 6 scenarios, 2-3 days estimated |
| Technical notes | PASS | DoD evaluation criteria, severity tags, corpus debrief queries, PES sign-off gate |
| Dependencies tracked | PASS | Depends on US-011 (assembled volumes), US-004 (compliance matrix), US-015 (corpus debriefs) |

### DoR Status: PASSED

---

## US-013: Submission Preparation and Portal-Specific Packaging

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "discovered 2 hours before deadline"; "forgot Firm Certification"; specific portal pain (DSIP, Grants.gov) |
| User/persona identified | PASS | Phil Santos, signed-off proposal, entering Wave 8 |
| 3+ domain examples | PASS | 3 examples: DSIP submission (AF243-001), missing attachment, portal naming change |
| UAT scenarios (3-7) | PASS | 6 scenarios covering portal ID, verification, missing files, confirmation, archive, PES block |
| AC derived from UAT | PASS | 9 AC items cover all scenarios |
| Right-sized | PASS | 6 scenarios, 2-3 days estimated |
| Technical notes | PASS | Portal mapping, manual submission step, confirmation entry, immutable archive, PES immutability |
| Dependencies tracked | PASS | Depends on US-011 (assembled volumes), US-012 (sign-off), PES US-014 |

### DoR Status: PASSED

---

## US-014: PES Enforcement for C3 Invariants

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "starting to format before sections are approved"; "submitting without review"; "modifying submitted proposal" |
| User/persona identified | PASS | Phil Santos, working through Waves 5-9, needs structural guarantees |
| 3+ domain examples | PASS | 3 examples: PDC gate, deadline blocking, submitted proposal edit blocked |
| UAT scenarios (3-7) | PASS | 5 scenarios covering PDC gate, deadline blocking, immutability, corpus integrity, audit log |
| AC derived from UAT | PASS | 7 AC items including configurable rules and backward compatibility |
| Right-sized | PASS | 5 scenarios, 2-3 days estimated |
| Technical notes | PASS | Extends US-006, pes-config.json, file-system enforcement, write hooks |
| Dependencies tracked | PASS | Depends on US-006 (PES Foundation), US-007 (state schema) |

### DoR Status: PASSED

---

## US-015: Debrief Ingestion and Critique-to-Section Mapping

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "20 minutes to figure out which section"; "debriefs are skimmed once and filed away"; "40% get no feedback" |
| User/persona identified | PASS | Phil Santos, received proposal outcome, wants structured institutional learning |
| 3+ domain examples | PASS | 3 examples: full debrief ingestion (AF243-001 loss), no debrief received, awarded outcome |
| UAT scenarios (3-7) | PASS | 6 scenarios covering ingestion, pattern analysis, no debrief, award, unstructured debrief, lessons learned |
| AC derived from UAT | PASS | 10 AC items including append-only tags, unstructured handling, and near-zero effort |
| Right-sized | PASS | 5 scenarios, 2-3 days estimated |
| Technical notes | PASS | Best-effort parsing, section numbering, confidence levels, append-only enforcement |
| Dependencies tracked | PASS | Depends on US-013 (submission archive), US-003 (corpus), US-014 (PES integrity) |

### DoR Status: PASSED

---

## US-016: Debrief Request Letter Draft

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | "administrative friction"; "sometimes skips the request"; "one more chore after disappointing result" |
| User/persona identified | PASS | Phil Santos, proposal not selected, wants ready-to-send letter |
| 3+ domain examples | PASS | 3 examples: DoD letter (AF243-001), NASA-specific procedure, skip request |
| UAT scenarios (3-7) | PASS | 3 scenarios covering DoD, NASA, and skip |
| AC derived from UAT | PASS | 5 AC items |
| Right-sized | PASS | 3 scenarios, 1 day estimated |
| Technical notes | PASS | Templates per agency, FAR 15.505, low-effort feature |
| Dependencies tracked | PASS | Depends on US-013 (confirmation record), proposal-state.json outcome |

### DoR Status: PASSED

---

## Summary

| Story | DoR Status | Scenarios | Est. Days |
|-------|-----------|-----------|-----------|
| US-010 | PASSED | 5 | 2-3 |
| US-011 | PASSED | 7 | 2-3 |
| US-012 | PASSED | 6 | 2-3 |
| US-013 | PASSED | 6 | 2-3 |
| US-014 | PASSED | 5 | 2-3 |
| US-015 | PASSED | 6 | 2-3 |
| US-016 | PASSED | 3 | 1 |

All 7 stories pass DoR. Total estimated effort: 13-21 days.
Total scenarios: 38.
