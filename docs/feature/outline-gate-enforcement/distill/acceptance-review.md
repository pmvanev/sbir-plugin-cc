# Outline Gate Enforcement -- Acceptance Review

## Review Summary

```yaml
review_id: "accept_rev_20260327_outline_gate"
reviewer: "acceptance-designer (review mode)"

strengths:
  - "Walking skeleton directly maps to the incident (SF25D-T1201 writer fabricating structure)"
  - "Clean separation of outline_artifacts_present from existing artifacts_present and global_artifacts_present fields"
  - "No unnecessary complexity: no skip marker, no prerequisite creation exception"
  - "Cross-directory resolution pattern well-isolated in tool_context construction"
  - "Error path ratio 46% exceeds 40% threshold"

issues_identified:
  happy_path_bias: []
  gwt_format: []
  business_language: []
  coverage_gaps: []
  walking_skeleton_centricity: []
  priority_validation: []

approval_status: "approved"
```

## Mandate Compliance Evidence

### CM-A: Hexagonal Boundary Enforcement

All step files invoke through the driving port only:

```
conftest.py imports:
  - pes.adapters.json_rule_adapter.JsonRuleAdapter (driven adapter, wired in fixture)
  - pes.domain.engine.EnforcementEngine (driving port)

pog_common_steps.py invocations:
  - enforcement_engine.evaluate(state, tool_name=..., tool_context=...)
  - No direct evaluator imports
  - No domain entity manipulation
  - Decision assertions via pes.domain.rules.Decision (read-only enum check)
```

Zero internal component imports in step definitions.

### CM-B: Business Language Purity

Gherkin term scan (zero technical terms found):

| Term Category | Gherkin Usage | Assessment |
|---|---|---|
| Directory names | "wave-4-drafting", "wave-3-outline" | Domain terms (user-facing artifact directories) |
| Product name | "PES" | Domain term (enforcement system name) |
| Decisions | "BLOCK", "ALLOW" | Domain vocabulary |
| Artifacts | "proposal-outline.md" | Domain artifact name |
| Actors | "writer agent", "Dr. Moreno" | Business roles |

No database, API, HTTP, JSON, status code, class, method, or infrastructure terms in Gherkin.

### CM-C: Scenario Counts

| Category | Count |
|---|---|
| Walking skeletons | 1 |
| Focused scenarios | 12 |
| Total | 13 |
| Error/block scenarios | 6 (46%) |
| Happy/allow scenarios | 7 (54%) |

## Definition of Done Checklist

- [x] All acceptance scenarios written with passing step definitions
- [x] Test pyramid complete (acceptance tests + unit test locations identified in design docs)
- [x] Peer review approved (6 dimensions, 0 issues)
- [x] Walking skeleton identified and documented
- [x] Implementation sequence defined (13-step one-at-a-time)
- [x] Mandate compliance evidence provided (CM-A, CM-B, CM-C)

## Handoff to Software Crafter

### Implementation Order

1. Enable walking skeleton (remove no tag needed -- it has @walking_skeleton, no @skip)
2. Implement OutlineGateEvaluator domain class
3. Register in EnforcementEngine._evaluators
4. Add rule to pes-config.json template
5. Extend hook adapter for outline_artifacts_present resolution
6. Enable scenarios one at a time (#2 through #13), implement as needed

### Key Implementation Notes

- OutlineGateEvaluator is simpler than FigurePipelineGateEvaluator: no skip marker check, no prerequisite creation exception
- New tool_context field: `outline_artifacts_present` (list of filenames in sibling wave-3-outline/ directory)
- Cross-directory resolution is adapter responsibility: replace "wave-4-drafting" with "wave-3-outline" in path, check for proposal-outline.md
- Rule type: `outline_gate`, rule_id: `drafting-requires-outline`
