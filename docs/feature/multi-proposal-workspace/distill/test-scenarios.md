# Test Scenarios: Multi-Proposal Workspace

## Summary

| Category | Count | Percentage |
|----------|-------|------------|
| Walking Skeletons | 3 | 6% |
| Happy Path | 19 | 39% |
| Error/Boundary | 16 | 33% |
| Edge Case | 5 | 10% |
| Integration Checkpoint | 9 | 18% |
| Property-Shaped | 4 | 8% |
| **Total** | **49** | |

**Error path ratio**: 16 error + 5 edge = 21 of 49 = **43%** (exceeds 40% target)

Note: Some scenarios are counted in multiple categories (e.g., integration + error).

## Feature Files

| File | Scenarios | Stories Covered |
|------|-----------|----------------|
| `walking-skeleton.feature` | 3 | US-MPW-004, US-MPW-005, US-MPW-001 |
| `milestone-01-path-resolution.feature` | 14 | US-MPW-004, US-MPW-005 |
| `milestone-02-namespace-creation.feature` | 14 | US-MPW-001, US-MPW-005 |
| `milestone-03-context-switching.feature` | 6 | US-MPW-003 |
| `milestone-04-lifecycle.feature` | 7 | US-MPW-006 |
| `integration-checkpoints.feature` | 9 | Cross-cutting |

## Story Coverage Matrix

| Story | Scenarios | Coverage |
|-------|-----------|----------|
| US-MPW-004 (Path Resolution) | 14 + 3 WS | All 5 AC covered |
| US-MPW-001 (Create Additional) | 7 + 1 WS | All 6 AC covered |
| US-MPW-005 (Backward Compat) | 7 + 1 WS | All 5 AC covered |
| US-MPW-003 (Switch Context) | 6 | All 5 AC covered |
| US-MPW-002 (Dashboard) | 5 (via integration) | 4 of 6 AC covered (display formatting is agent behavior) |
| US-MPW-006 (Lifecycle) | 7 | All 5 AC covered |

## Driving Ports (CM-A Compliance)

All test step definitions invoke through these driving ports only:
- `pes.adapters.workspace_resolver.resolve_workspace()` -- path resolution
- `pes.adapters.namespace_manager.create_proposal_namespace()` -- namespace creation
- `pes.adapters.proposal_switch.switch_active_proposal()` -- context switching
- `pes.adapters.migration_service.migrate_legacy_workspace()` -- legacy migration
- `pes.adapters.workspace_enumerator.enumerate_proposals()` -- dashboard enumeration
- `pes.adapters.lifecycle_manager.evaluate_auto_switch()` -- lifecycle management
- `pes.adapters.lifecycle_manager.is_proposal_completed()` -- completion check

No internal component imports. No domain entity direct access.

## Business Language Purity (CM-B Compliance)

Gherkin files contain zero technical terms. Verified terms:
- No: database, API, HTTP, JSON, class, method, controller, status code, exception
- Yes: workspace, proposal, namespace, active proposal, state, artifacts, layout

## Walking Skeleton + Focused Scenario Counts (CM-C Compliance)

- Walking skeletons: 3 (user-centric, demo-able)
- Focused scenarios: 46 (boundary tests through driving ports)
- Ratio: 3 WS / 46 focused -- within recommended range

## Property-Shaped Scenarios (@property tag)

4 scenarios tagged `@property` for property-based test implementation:
1. Path resolution consistency across repeated calls
2. Creating any number of proposals never corrupts existing state
3. Migration is reversible
4. (Path resolution) Cross-reference consistency

## Implementation Sequence (One-at-a-Time)

### Phase 1: Path Resolution (Milestone 01)
1. WS-1: Path resolution in multi-proposal workspace
2. Multi-proposal layout detection
3. State directory derivation
4. Artifact directory derivation
5. Audit directory scoping
6. Legacy layout detection
7. Legacy root-level paths
8. Fresh workspace detection
9. Missing active-proposal error
10. Invalid active-proposal error
11. Empty/whitespace active-proposal errors
12. WS-2: Legacy workspace unchanged

### Phase 2: Namespace Creation (Milestone 02)
13. WS-3: Second proposal with isolation
14. State unchanged after creation (checksum)
15. Fresh workspace multi-proposal layout
16. New proposal state content
17. Custom namespace
18. Namespace collision error
19. Custom name collision error

### Phase 3: Legacy Migration (Milestone 02 cont.)
20. Legacy unchanged without migration
21. Migration moves state
22. Migration preserves safety net
23. Migration moves artifacts
24. Migration preserves audit

### Phase 4: Context Switching (Milestone 03)
25. Switch updates pointer
26. Switch to completed proposal
27. Path resolution after switch
28. Idempotent switch
29. Switch to nonexistent error
30. Switch in legacy error

### Phase 5: Lifecycle (Milestone 04)
31. Auto-switch sole remaining
32. All completed
33. Completed accessible for debrief
34. Multiple active remain -- no auto-switch
35. No-go classified as completed
36. Archived classified as completed
37. Auto-switch with zero active

### Phase 6: Integration Checkpoints
38-46. Integration checkpoint scenarios (run after phases 1-5 complete)

### Phase 7: Property-Based
47-49. Property-shaped scenarios (implemented as property-based tests)
