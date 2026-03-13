# Handoff to DESIGN Wave -- Solution Shaper

## Handoff Summary

| Field | Value |
|-------|-------|
| Feature | solution-shaper |
| Date | 2026-03-13 |
| From | product-owner (DISCUSS wave) |
| To | solution-architect (DESIGN wave) |
| Stories | US-SS-001 (Approach Generation, Scoring, Selection), US-SS-002 (Approach Revision) |
| Total Scenarios | 9 |
| Estimated Effort | 3-5 days |

---

## Handoff Package Contents

| Artifact | Path | Description |
|----------|------|-------------|
| JTBD Job Stories | `docs/feature/solution-shaper/discuss/jtbd-job-stories.md` | 6 job stories with 3 dimensions each, 8-step job map |
| Four Forces Analysis | `docs/feature/solution-shaper/discuss/jtbd-four-forces.md` | Push/Pull/Anxiety/Habit with force balance assessment |
| Opportunity Scores | `docs/feature/solution-shaper/discuss/jtbd-opportunity-scores.md` | 8 outcomes scored and prioritized (MoSCoW) |
| Journey Visual | `docs/feature/solution-shaper/discuss/journey-approach-selection-visual.md` | 5-step journey with ASCII mockups, emotional arc, error paths |
| Shared Artifacts Registry | `docs/feature/solution-shaper/discuss/shared-artifacts-registry.md` | 9 tracked artifacts, 5 integration checkpoints, flow diagram |
| User Stories | `docs/feature/solution-shaper/discuss/user-stories.md` | 2 stories with 9 BDD scenarios, dependency map, sizing |
| Requirements | `docs/feature/solution-shaper/discuss/requirements.md` | 7 FRs, 4 NFRs, business rules, glossary, risk assessment, traceability |
| Discovery Artifacts | `docs/feature/solution-shaper/discover/` | Problem validation, opportunity tree, solution testing, lean canvas |

---

## Definition of Ready Validation

### US-SS-001: Approach Generation, Scoring, and Selection

| DoR Item | Status | Evidence |
|----------|--------|----------|
| 1. Problem statement clear, domain language | PASS | "After making a Go decision on a solicitation topic, he jumps directly to strategy without systematically evaluating what technical approach to propose." Uses SBIR domain terms throughout. |
| 2. User/persona identified with specific characteristics | PASS | Phil Santos, defense tech engineer, 3-5 proposals/year, technical founder, pursues adjacent topics for growth. |
| 3. 3+ domain examples with real data | PASS | 3 examples: AF243-001 fiber laser (happy), N244-012 quantum override (edge), AF243-099 low scores (error). Real topic IDs, personnel (Dr. Sarah Chen), contract IDs (AF241-087). |
| 4. UAT scenarios in Given/When/Then (3-7) | PASS | 6 scenarios covering happy path, approval, override, low scores, missing profile, narrow spread. |
| 5. AC derived from UAT | PASS | 11 acceptance criteria, each traceable to one or more scenarios. |
| 6. Right-sized (1-3 days, 3-7 scenarios) | PASS | 6 scenarios, 2-3 days estimated. Single demonstrable outcome: approach selected with brief produced. |
| 7. Technical notes identify constraints | PASS | Implementation type (markdown agent + skill + command), data dependencies (proposal-state.json, company-profile.json), PES integration (Wave 1 gating). |
| 8. Dependencies resolved or tracked | PASS | Depends on US-002 (complete), company-profile-builder (complete). No unresolved dependencies. |

### DoR Status: PASSED

---

### US-SS-002: Approach Revision After New Information

| DoR Item | Status | Evidence |
|----------|--------|----------|
| 1. Problem statement clear, domain language | PASS | "Learns new information after selecting an approach -- a TPOC call reveals different priorities, Wave 2 research surfaces a competing approach." Domain-specific triggers. |
| 2. User/persona identified with specific characteristics | PASS | Same persona (Phil Santos), mid-proposal context with new information. |
| 3. 3+ domain examples with real data | PASS | 3 examples: TPOC revision for AF243-001, teaming partner for N244-012 (NavTech Corp), no-prior-selection error. |
| 4. UAT scenarios in Given/When/Then (3-7) | PASS | 3 scenarios covering TPOC revision, teaming partner, and error path. |
| 5. AC derived from UAT | PASS | 5 acceptance criteria derived from the 3 scenarios. |
| 6. Right-sized (1-3 days, 3-7 scenarios) | PASS | 3 scenarios, 1-2 days estimated. Single outcome: approach revised with history preserved. |
| 7. Technical notes identify constraints | PASS | --revise flag, append-only revision history, re-reads updated inputs. |
| 8. Dependencies resolved or tracked | PASS | Depends on US-SS-001 (in same feature scope). |

### DoR Status: PASSED

---

## Peer Review

### Review Iteration 1

```yaml
review_id: "req_rev_20260313_solution_shaper"
reviewer: "product-owner (review mode)"
artifact: "docs/feature/solution-shaper/discuss/user-stories.md"
iteration: 1

strengths:
  - "Strong problem statement grounded in codebase structural analysis (5 evidence points)"
  - "Real domain data throughout: AF243-001, Dr. Sarah Chen, AF241-087, VanEvery Technologies"
  - "Emotional arc is coherent: determined → curious → excited → analytical → confident → decisive"
  - "Shared artifact registry has complete traceability with integration checkpoints"
  - "Error paths are well-defined with actionable recovery in all cases"

issues_identified:
  confirmation_bias:
    - issue: "No scenario tests what happens when the LLM generates fewer than 3 approaches"
      severity: "medium"
      location: "US-SS-001"
      recommendation: "Add a note in FR-2 that fewer than 3 approaches is acceptable for narrow topics, with user notification"

  completeness_gaps:
    - issue: "No explicit scenario for the 'explore' checkpoint option"
      severity: "low"
      location: "US-SS-001 Scenarios"
      recommendation: "The explore option is documented in FR-5 and the journey visual. Adding a full scenario would push to 7 scenarios. Acceptable to defer to implementation."

  clarity_issues: []

  testability_concerns: []

  priority_validation:
    q1_largest_bottleneck: "YES — approach selection is the highest-uncertainty pre-proposal decision"
    q2_simple_alternatives: "ADEQUATE — current workaround (mental evaluation) documented; solution designed to be fast enough to justify over intuition"
    q3_constraint_prioritization: "CORRECT — Must Have items (O2, O3, O5) are the core value; Should/Could items are enhancements"
    q4_data_justified: "JUSTIFIED — 5 codebase evidence points, explicit user request, opportunity scoring with documented methodology"
    verdict: "PASS"

approval_status: "approved"
critical_issues_count: 0
high_issues_count: 0
```

### Remediation Applied

- Medium issue (fewer than 3 approaches): Added note in FR-2 that 3-5 is the target range; fewer is acceptable for narrow topics with user notification. No new scenario needed as this is a documentation clarification, not a behavioral change.

- Low issue (explore option): Acknowledged. The explore option is documented in FR-5 and the journey visual Step 5 mockup. Adding a dedicated scenario is deferred to implementation when the explore behavior can be specified in detail.

### Review Status: APPROVED (Iteration 1)

---

## Design Decisions for Solution Architect

The following decisions are left to the DESIGN wave (solution-architect):

1. **Exact command name and routing**: `/sbir:proposal shape` is the working name. The solution architect determines the final command name and whether the orchestrator auto-dispatches after Go or the user invokes manually.

2. **Wave placement**: The solution-shaper sits between Wave 0 and Wave 1. Whether this is "Wave 0.5", extends Wave 0 output, or is a separate named wave is a design decision.

3. **Artifact location**: `./artifacts/wave-0-intelligence/approach-brief.md` is proposed. The solution architect may choose a different directory structure.

4. **Skill file structure**: One skill (`approach-evaluation.md`) is proposed. The solution architect may split into approach-generation and approach-scoring if the skill exceeds recommended size.

5. **PES integration**: The approach selection checkpoint should integrate with PES wave ordering. Whether this requires new PES rules or extends existing wave-ordering logic is a design decision.

6. **Strategist integration**: How the strategist agent reads the approach brief (additional context file vs. state reference) is a design decision.

---

## Acceptance Designer Notes

For handoff to acceptance-designer (DISTILL wave):

- Journey schema: `docs/feature/solution-shaper/discuss/journey-approach-selection-visual.md`
- Gherkin scenarios: Embedded in `docs/feature/solution-shaper/discuss/user-stories.md` (UAT Scenarios sections)
- Integration checkpoints: `docs/feature/solution-shaper/discuss/shared-artifacts-registry.md` (5 checkpoints defined)
- Shared artifacts: 9 artifacts tracked with sources, consumers, and validation rules
