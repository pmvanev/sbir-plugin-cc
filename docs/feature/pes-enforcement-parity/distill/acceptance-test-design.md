# PES Enforcement Parity -- Acceptance Test Design

## Scenario Summary

| Feature File | Walking Skeletons | Happy Path | Error Path | Edge/Boundary | Property | Total |
|---|---|---|---|---|---|---|
| walking-skeleton.feature | 3 | - | - | - | - | 3 |
| session_housekeeping.feature | - | 2 | 3 | 3 | - | 8 |
| post_action_validation.feature | - | 2 | 4 | 1 | - | 7 |
| agent_lifecycle.feature | - | 3 | 4 | 2 | - | 9 |
| active_audit_logging.feature | - | 4 | 3 | - | 2 | 9 |
| **Totals** | **3** | **11** | **14** | **6** | **2** | **36** |

**Error path ratio**: 14/36 = 38.9% (near 40% target; 16/36 = 44.4% if property scenarios counted as error coverage)

## Driving Ports Used

All scenarios invoke through these driving ports only:
- `EnforcementEngine.check_session_start()` -- session startup housekeeping
- `EnforcementEngine.evaluate()` -- pre/post-tool enforcement and agent lifecycle

No internal components (SessionChecker, evaluators, adapters) are imported directly by step definitions.

## Implementation Sequence (One-at-a-Time)

The walking skeleton scenarios run first (no @skip tag). All other scenarios are tagged @skip. Enable one at a time in this order:

### Gap 1: Session Start Housekeeping
1. WS1: Crash signal cleanup (walking-skeleton.feature) -- **currently failing, drives implementation**
2. Stale crash signal removal (session_housekeeping.feature)
3. Audit log retention rotation
4. Audit log file size rotation
5. Multiple crash signals
6. Locked crash signal file
7. Clean workspace (no crash signals)
8. Retention boundary (365 days exact)
9. Retention boundary (366 days)

### Gap 2: Post-Action Validation
10. WS2: Artifact placement confirmation (walking-skeleton.feature)
11. Artifact in correct directory
12. State file verification
13. Artifact in wrong directory
14. Corrupted state file
15. Missing artifact
16. Missing audit directory auto-creation
17. Read-only tool skips validation

### Gap 3: Agent Lifecycle Tracking
18. WS3: Correct agent dispatch (walking-skeleton.feature)
19. Writer allowed for Wave 4
20. Reviewer allowed for Wave 7
21. Agent stop event recorded
22. Researcher blocked from Wave 4
23. Writer blocked from Wave 2
24. Unknown agent blocked
25. No proposal blocks dispatch
26. Multi-wave agent (writer in Wave 3)
27. Compliance sheriff in Wave 6

### Gap 4: Active Audit Logging
28. Allowed action recorded
29. Blocked action with reason recorded
30. Session start recorded
31. Audit entries on disk
32. Audit write failure non-blocking
33. Multiple block reasons
34. Concurrent session audit isolation
35. Property: one entry per decision
36. Property: append-only audit entries

## Mandate Compliance Evidence

### CM-A: Hexagonal Boundary Enforcement
All step definition files import only through driving ports:
- `pep_common_steps.py` -- imports `EnforcementEngine` via conftest fixture (never directly)
- `pep_post_action_steps.py` -- same fixture-based access
- `pep_audit_logging_steps.py` -- same fixture-based access
- Zero imports of `SessionChecker`, `WaveOrderingEvaluator`, `_NullAuditLogger`, or any internal component

### CM-B: Business Language Purity
Gherkin files use only domain terms:
- "proposal", "wave", "drafting", "session", "crash signal", "audit trail"
- "enforcement rules", "artifact", "agent", "dispatch"
- Zero technical terms (no HTTP, JSON, database, API, status codes, file paths in scenario text)

### CM-C: Walking Skeleton + Focused Scenario Counts
- 3 walking skeletons (user value E2E)
- 33 focused scenarios (boundary tests at driving port)
- Ratio: 8.3% walking skeletons, 91.7% focused -- within recommended range

## New Engine Methods Required (Implementation Notes for Software Crafter)

These acceptance tests drive the creation of new capabilities:
1. `EnforcementEngine.check_session_start()` -- extend with crash signal cleanup and audit log rotation
2. New `check_post_action()` method or extend `evaluate()` -- post-tool artifact validation
3. New `check_agent_dispatch()` method or extend hook adapter -- agent-wave authorization
4. Replace `_NullAuditLogger` with `FileAuditLogger` adapter implementing `AuditLogger` port
