# Peer Review -- Phase C3 Requirements Package

## Review Metadata

- Reviewer: product-owner (review mode)
- Artifacts reviewed:
  - `docs/feature/sbir-proposal-plugin/discuss/c3-jtbd-analysis.md`
  - `docs/feature/sbir-proposal-plugin/discuss/c3-journey-proposal-production.yaml`
  - `docs/feature/sbir-proposal-plugin/discuss/c3-journey-proposal-production-visual.md`
  - `docs/feature/sbir-proposal-plugin/discuss/c3-journey-proposal-production.feature`
  - `docs/feature/sbir-proposal-plugin/discuss/c3-shared-artifacts-registry.md`
  - `docs/feature/sbir-proposal-plugin/discuss/c3-user-stories.md`
  - `docs/feature/sbir-proposal-plugin/discuss/c3-dor-validation.md`
- Iteration: 1

---

## Strengths

1. **New jobs discovered, not just deepened**: J9 (visual assets), J10 (submission survival), and J11 (catch fatal flaws) were not in the C1 JTBD analysis. They were extracted from careful reading of the Wave 5-9 specification and validated against problem validation evidence. J10's scoring at 15 (highest in C3) is well justified -- submission failure wastes 10-15 hours of prior work.

2. **Honest feasibility scoping for J6**: The formatting story (US-011) explicitly acknowledges that template-based formatting handles 90% of cases and flags the remaining 10% for manual intervention. This avoids the overpromising trap flagged in C1 discovery. NFR-004 makes this measurable.

3. **Real data throughout**: AF243-001, AF241-087, N222-038, PMS 501, DSIP-2026-AF243-001-7842, FAR 15.505(a)(1), specific reviewer scores (7.8/10, 7.2/10), specific page counts (19/20, 22/20). No generic data detected.

4. **PES invariants well-scoped**: Four new invariant classes (PDC gate, deadline blocking, submission immutability, corpus integrity) extend the C1 foundation without overreach. Each has clear behavioral scenarios.

5. **Emotional arc coherent**: The C3 arc (fatigued but engaged -> cautious -> relieved -> hopeful) is a natural continuation of the C1/C2 arc. The "point of no return" framing for Wave 8 is emotionally honest -- submission anxiety is real.

6. **Debrief ingestion effort constraint explicit**: US-015 specifies "under 5 minutes of Phil's time" and NFR-007 makes this measurable. This directly addresses the J7 design implication about near-zero effort.

7. **Gherkin coverage comprehensive**: 37 scenarios across 5 waves. The C3 feature file includes `@property` scenarios for PES invariants -- ongoing qualities that should hold continuously, not just in one scenario.

---

## Issues Identified

### Confirmation Bias

**Issue 1: Submission is a manual step, but stories imply automation**
Severity: HIGH
Location: US-013, journey step 9
Finding: The specification says submission itself is a manual step ("Phil clicks submit on the portal"), but the journey TUI mockup for `/proposal submit` shows "SUBMITTED at..." as if the tool performed the submission. The story says "Submission itself is a manual step -- tool prepares and verifies, Phil clicks submit on the portal" in technical notes, but the TUI mockup creates an impression of automated submission. The confirmation number is "manually entered by Phil" but this is buried in technical notes, not visible in the scenario flow.
Recommendation: Add a scenario to US-013 that explicitly shows the manual submission step: "Given Phil has confirmed readiness, When Phil submits through the DSIP portal manually, Then Phil enters the confirmation number into the tool." Update the TUI mockup to show a prompt for confirmation number entry rather than implying automatic submission.

**Issue 2: Happy path bias in debrief ingestion**
Severity: MEDIUM
Location: US-015
Finding: All debrief examples assume the debrief is a well-structured document with clear scores and comments. In practice, many debriefs are vague, partially illegible scans, or consist of a single paragraph. The "best-effort parsing" is mentioned in technical notes but no scenario covers the case where parsing produces minimal useful output.
Recommendation: Add a scenario to US-015: "Given a debrief letter is a 1-paragraph summary with no scores, When Phil ingests it, Then the tool preserves the full text as freeform feedback and notes that structured scores could not be extracted."

### Completeness Gaps

**Issue 3: No explicit scenario for the Wave 5 -> Wave 6 gate**
Severity: MEDIUM
Location: US-010, US-011
Finding: The PES gates from Wave 4 -> 5 and Wave 7 -> 8 have explicit scenarios in US-014. But the gate from Wave 5 -> Wave 6 (all figure placeholders addressed) and Wave 6 -> Wave 7 (compliance items covered, figures inserted, page count within limits) do not have explicit PES enforcement scenarios. They are described in integration checkpoints but not tested.
Recommendation: Add scenarios to US-014 for Wave 5->6 and Wave 6->7 gates, or document them as softer checkpoints that are human-enforced rather than PES-enforced. The current integration checkpoints imply PES enforcement but no story requires it.

**Issue 4: No NFR for review iteration convergence**
Severity: MEDIUM
Location: US-012
Finding: US-012 mentions "max 2 iteration cycles" for the review loop, but no AC or NFR specifies what happens if issues are not resolved after 2 iterations. The story says the sign-off is required, but what if Phil cannot resolve a HIGH issue?
Recommendation: Add AC to US-012: "After 2 review iteration cycles, the tool requires sign-off even if unresolved issues remain, with unresolved items documented in the sign-off record."

### Clarity Issues

**Issue 5: Portal configuration source unclear**
Severity: MEDIUM
Location: US-013
Finding: US-013 says "Portal identification rules stored in a configurable mapping (agency -> portal -> rules)" but does not specify where this mapping lives. Is it a skill file? A config file in the plugin? User-editable? Since portal rules change between solicitation cycles, the source and update mechanism matters.
Recommendation: Add to US-013 technical notes: portal mapping stored in a specific location (e.g., `templates/portal-rules/` or `pes-config.json`) and note that it is user-editable to handle rule changes.

### Testability Concerns

No critical testability issues found. All AC are observable and measurable. The `@property` scenarios correctly identify ongoing invariants.

### Priority Validation

- Q1 (Largest bottleneck): YES -- J10 (submission survival) is correctly prioritized highest. Submission failure wastes all prior investment.
- Q2 (Simpler alternatives): ADEQUATE -- Template-based formatting is explicitly chosen over LLM formatting. Manual figure creation is the fallback.
- Q3 (Constraint prioritization): CORRECT -- The 10-15 hour budget constraint flows into C3 design (near-zero debrief effort, template-based formatting, skip-on-deadline for non-essential waves).
- Q4 (Data justified): JUSTIFIED -- Discovery evidence from 9 sources, specific behavioral signals (built internal tool, $5-10K spend, specific debrief quotes).
- Verdict: PASS

---

## Remediation Required

| # | Issue | Severity | Action |
|---|-------|----------|--------|
| 1 | Submission implies automation in mockup | HIGH | Add manual submission scenario to US-013; update TUI to show confirmation entry prompt |
| 2 | Debrief parsing happy path bias | MEDIUM | Add minimal/unstructured debrief scenario to US-015 |
| 3 | Wave 5->6 and 6->7 gates not in PES stories | MEDIUM | Clarify which gates are PES-enforced vs. human-enforced |
| 4 | Review iteration convergence undefined | MEDIUM | Add AC for forced sign-off after 2 iterations |
| 5 | Portal config source unclear | MEDIUM | Add portal mapping location to US-013 technical notes |

---

## Remediation Applied (Iteration 2)

| # | Issue | Remediation |
|---|-------|-------------|
| 1 | Submission implies automation | Added scenario "Manual submission with confirmation entry" to US-013. Updated TUI mockup in journey visual to show confirmation number entry prompt. Added AC: "Confirmation number is manually entered by Phil after portal submission." |
| 2 | Debrief parsing happy path bias | Added scenario "Ingest unstructured debrief with minimal content" to US-015. Added AC: "Unstructured debriefs are preserved as freeform text when structured parsing fails." |
| 3 | Wave 5->6 and 6->7 gates | Clarified in c3-shared-artifacts-registry integration checkpoints: Wave 5->6 and Wave 6->7 are human-enforced checkpoints (approve/revise), not PES-enforced hard gates. Only Wave 4->5 (PDC), Wave 7->8 (sign-off), and submission immutability are PES hard gates. |
| 4 | Review iteration convergence | Added AC to US-012: "After 2 review iterations, sign-off is required even with unresolved issues; unresolved items documented in sign-off record." |
| 5 | Portal config location | Added to US-013 technical notes: "Portal packaging rules stored in templates/portal-rules/ directory, user-editable to handle rule changes between solicitation cycles." |

---

## Approval Status

**APPROVED** -- all issues remediated. 7 stories, 38 scenarios, all DoR items passed.

No critical or high issues remaining after remediation.
