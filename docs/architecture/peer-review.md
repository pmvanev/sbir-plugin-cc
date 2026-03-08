# Architecture Peer Review -- SBIR Proposal Plugin

## Review Metadata

```yaml
review_id: "arch_rev_2026-03-08"
reviewer: "solution-architect (self-review against critique dimensions)"
artifact: "docs/architecture/architecture.md, docs/adrs/*.md"
iteration: 1
```

## Strengths

1. **Architecture matches the problem domain.** This is a local-only CLI plugin with no servers, no database, and no cloud. The architecture does not over-engineer: JSON files for state, markdown for agents, Python only where enforcement requires it (PES hooks). Every technology choice is justified by the problem, not by preference.

2. **PES as hook-based enforcement (ADR-002) is the right call.** The spec explicitly states "guardrails belong at the execution layer." Agent instructions are advisory; hooks are structural. The DES precedent from nWave validates feasibility.

3. **Corpus search via native file reading (ADR-003) is appropriately simple.** At 2-3 proposals/year, a vector database adds dependency cost without benefit. The migration path to ChromaDB is documented for when/if the corpus outgrows native reading.

4. **All 6 ADRs have 2+ alternatives with evidence-based rejection.** No "we chose X because it's best" without rationale.

5. **C4 diagrams are complete: L1 (System Context), L2 (Container), L3 (PES Component).** Every arrow is labeled with a verb. Abstraction levels are not mixed.

6. **Roadmap step ratio is efficient (0.38).** Well under the 2.5 threshold. No over-decomposition detected.

## Issues Identified

```yaml
architectural_bias:
  - issue: "No bias detected. Stack is minimal and problem-driven."
    severity: "none"

decision_quality:
  - issue: "ADR-001 'Plugin architecture follows nWave conventions' could note the risk of Claude Code plugin protocol changes"
    severity: "low"
    location: "ADR-001"
    recommendation: "Add consequence: 'If Claude Code changes its plugin protocol, all file locations may need migration.' Already partially addressed but could be more explicit."

completeness_gaps:
  - issue: "Company profile schema not defined"
    severity: "medium"
    location: "architecture.md, Proposal State Schema section"
    recommendation: "Add company-profile.json schema or note it as a deferred artifact to be defined during implementation of US-002 (fit scoring reads it)."

  - issue: "No explicit error handling pattern documented"
    severity: "medium"
    location: "architecture.md, Integration Patterns section"
    recommendation: "Document the what/why/what-to-do error message pattern from NFR-003. Currently mentioned in Quality Attributes but not as a pattern."

implementation_feasibility:
  - issue: "No feasibility concern. Single engineer (Phil) with Python and CLI expertise. nWave precedent validates plugin architecture."
    severity: "none"

priority_validation:
  q1_largest_bottleneck:
    evidence: "JTBD analysis scores J1 (corpus) at 15 and J2 (compliance) at 14. Phase C1 addresses both."
    assessment: "YES"
  q2_simple_alternatives:
    assessment: "ADEQUATE -- 2 alternatives documented with rejection rationale"
  q3_constraint_prioritization:
    assessment: "CORRECT -- 10-15 hour budget drives all design decisions"
  q4_data_justified:
    assessment: "JUSTIFIED -- 9 sources, $5-10K current spend, 100% problem confirmation"
```

## Remediation

### Issue: Company profile schema not defined (MEDIUM)

The architecture references `~/.sbir/company-profile.json` but does not define its schema. This is needed by US-002 (fit scoring) and US-009 (strategy brief).

**Resolution:** This is a deferred artifact. The company profile schema will be defined during step 02-02 (solicitation parsing and new proposal creation) when fit scoring needs to read it. Added a note to the architecture document.

### Issue: Error handling pattern not documented (MEDIUM)

The NFR-003 (CLI accessibility) mandates the what/why/what-to-do error pattern. This should be documented as an integration pattern.

**Resolution:** Added to architecture document.

## Approval Status

```yaml
approval_status: "approved"
critical_issues_count: 0
high_issues_count: 0
medium_issues_count: 2
low_issues_count: 1
```

All medium issues are documentation gaps that do not affect architectural decisions. No critical or high issues found. Architecture is approved for handoff.
