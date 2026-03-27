# Outline Gate Enforcement -- Test Scenarios

## Scenario Inventory

| # | Feature File | Scenario | Category | Tag |
|---|---|---|---|---|
| 1 | walking-skeleton.feature | Writer is blocked from drafting a section when no approved outline exists | Walking skeleton | @walking_skeleton |
| 2 | outline_gate.feature | Block draft section write when proposal-outline.md does not exist | Error path | @skip |
| 3 | outline_gate.feature | Block Edit to existing draft when proposal-outline.md does not exist | Error path | @skip |
| 4 | outline_gate.feature | Allow draft section write when proposal-outline.md exists | Happy path | @skip |
| 5 | outline_gate.feature | Allow writing any file type to wave-4-drafting when outline exists | Happy path | @skip |
| 6 | integration_checkpoints.feature | Gate works with multi-proposal workspace path layout | Error/integration | @skip |
| 7 | integration_checkpoints.feature | Gate works with legacy single-proposal path layout | Error/integration | @skip |
| 8 | integration_checkpoints.feature | Cross-directory resolution derives wave-3-outline from wave-4-drafting | Happy/integration | @skip |
| 9 | integration_checkpoints.feature | Gate does not affect writes outside wave-4-drafting | Non-interference | @skip |
| 10 | integration_checkpoints.feature | Gate does not affect Read operations on wave-4-drafting | Non-interference | @skip |
| 11 | integration_checkpoints.feature | Gate does not affect wave-5 writes when outline is missing | Non-interference | @skip |
| 12 | integration_checkpoints.feature | Blocked draft write is recorded in audit log | Audit/error | @skip |
| 13 | integration_checkpoints.feature | Allowed draft write after outline exists is recorded in audit log | Audit/happy | @skip |

## Coverage Analysis

### Error Path Ratio

- Block scenarios: 5 (#1, #2, #3, #6, #7) + audit block (#12) = 6
- Allow scenarios: 5 (#4, #5, #8, #9, #10) + audit allow (#13) + non-interference (#11) = 7
- Error path ratio: 6/13 = 46% (exceeds 40% threshold)

### Acceptance Criteria Coverage

| AC (US-OGATE-01) | Scenarios |
|---|---|
| Writes to wave-4-drafting/ blocked when outline missing | #1, #2, #6, #7 |
| Both Write and Edit subject to gate | #2 (Write), #3 (Edit) |
| Multi-proposal path layout | #6, #8 |
| Legacy single-proposal path layout | #7 |
| Writes outside wave-4-drafting/ not affected | #9, #11 |
| Block message includes guidance | #2 (message checks) |
| Block message includes path | #2 (wave-3-outline check) |
| Blocked and allowed decisions in audit log | #12, #13 |

| AC (US-OGATE-02) | Scenarios |
|---|---|
| Evaluator registered with key outline_gate | All scenarios exercise engine dispatch |
| Config contains drafting-requires-outline rule | All scenarios load config with this rule |
| Evaluator follows existing interface pattern | Walking skeleton proves E2E path |
| Evaluator is pure domain (no infra imports) | Architecture constraint, not scenario |
| Adapter derives wave-3-outline from wave-4-drafting | #8 |
| Adapter handles both layouts | #6 (multi), #7 (legacy) |

### Simplifications vs. Previous Gates

| Feature | Figure Pipeline | Writing Style | Outline Gate |
|---|---|---|---|
| Skip marker | No | Yes | No |
| Prerequisite creation exception | Yes (figure-specs.md) | No | No |
| Global artifacts | No | Yes | No |
| Cross-directory check | No | No | Yes (new) |
| tool_context field | artifacts_present | global_artifacts_present | outline_artifacts_present |

## Implementation Sequence

Enable one scenario at a time, implement, commit:

1. Walking skeleton (#1) -- first, no @skip
2. Block Write (#2) -- focused block with message assertions
3. Block Edit (#3) -- confirms Edit is also gated
4. Allow Write (#4) -- confirms outline presence unblocks
5. Allow any file (#5) -- confirms any wave-4-drafting file allowed
6. Multi-proposal block (#6) -- path resolution
7. Legacy block (#7) -- path resolution
8. Cross-directory allow (#8) -- confirms sibling resolution
9. Non-interference writes (#9) -- outside wave-4-drafting
10. Non-interference Read (#10) -- Read operations
11. Non-interference wave-5 (#11) -- other waves
12. Audit block (#12) -- audit trail for blocks
13. Audit allow (#13) -- audit trail for allows
