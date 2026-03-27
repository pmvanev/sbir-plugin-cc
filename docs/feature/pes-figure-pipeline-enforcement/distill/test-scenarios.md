# PES Figure Pipeline Enforcement -- Test Scenario Mapping

## Scenario Inventory

| # | Feature File | Scenario | Story | Category | Tag |
|---|---|---|---|---|---|
| 1 | walking-skeleton.feature | Formatter blocked from generating figure when no specification plan exists | US-FPIPE-01 | Walking skeleton | @walking_skeleton |
| 2 | figure_pipeline_gate.feature | Block figure file write when figure-specs.md does not exist | US-FPIPE-01 | Error path | @skip |
| 3 | figure_pipeline_gate.feature | Block Edit to existing figure when figure-specs.md does not exist | US-FPIPE-01 | Error path | @skip |
| 4 | figure_pipeline_gate.feature | Allow writing figure-specs.md itself (prerequisite creation) | US-FPIPE-01 | Happy path | @skip |
| 5 | figure_pipeline_gate.feature | Allow figure file write when specs and style exist | US-FPIPE-01 | Happy path | @skip |
| 6 | figure_pipeline_gate.feature | Allow writing figure-log.md when specs and style exist | US-FPIPE-01 | Happy path | @skip |
| 7 | figure_pipeline_gate.feature | Allow writing external brief when specs and style exist | US-FPIPE-01 | Happy path | @skip |
| 8 | style_profile_gate.feature | Block figure generation when style missing and no skip | US-FPIPE-02 | Error path | @skip |
| 9 | style_profile_gate.feature | Allow figure generation when style-profile.yaml exists | US-FPIPE-02 | Happy path | @skip |
| 10 | style_profile_gate.feature | Allow figure generation when user explicitly skipped style | US-FPIPE-02 | Happy path | @skip |
| 11 | style_profile_gate.feature | Allow writing style-profile.yaml itself | US-FPIPE-02 | Happy path | @skip |
| 12 | integration_checkpoints.feature | Gate works with multi-proposal workspace path layout | US-FPIPE-01, US-FPIPE-03 | Edge case | @skip |
| 13 | integration_checkpoints.feature | Gate works with legacy single-proposal path layout | US-FPIPE-01, US-FPIPE-03 | Edge case | @skip |
| 14 | integration_checkpoints.feature | Gate does not affect writes outside visual assets | US-FPIPE-01 | Non-interference | @skip |
| 15 | integration_checkpoints.feature | Gate does not affect Read operations | US-FPIPE-01 | Non-interference | @skip |
| 16 | integration_checkpoints.feature | Blocked figure write recorded in audit log | US-FPIPE-03 | Audit trail | @skip |
| 17 | integration_checkpoints.feature | Allowed figure write after gates pass recorded in audit | US-FPIPE-03 | Audit trail | @skip |

## Coverage Summary

| Category | Count | Percentage |
|---|---|---|
| Walking skeleton | 1 | 6% |
| Happy path | 7 | 41% |
| Error path | 3 | 18% |
| Edge case (path resolution) | 2 | 12% |
| Non-interference | 2 | 12% |
| Audit trail | 2 | 12% |
| **Total** | **17** | **100%** |

Error + edge + non-interference = 7 scenarios = **41%** (exceeds 40% target).

## Story Coverage Matrix

| Story | Acceptance Criteria | Scenarios Covering |
|---|---|---|
| US-FPIPE-01 | Writes blocked when specs absent | #1, #2, #3 |
| US-FPIPE-01 | Writing figure-specs.md allowed | #4 |
| US-FPIPE-01 | Both Write and Edit subject to gate | #2, #3 |
| US-FPIPE-01 | Multi-proposal path layout | #12 |
| US-FPIPE-01 | Legacy single-proposal path layout | #13 |
| US-FPIPE-01 | Writes outside wave-5-visuals not affected | #14 |
| US-FPIPE-01 | Block message includes guidance | #1, #2 |
| US-FPIPE-01 | Decisions recorded in audit log | #16, #17 |
| US-FPIPE-02 | Blocked when no style and no skip | #8 |
| US-FPIPE-02 | Allowed with style-profile.yaml | #9 |
| US-FPIPE-02 | Writing figure-specs.md not affected | #4 (gate allows) |
| US-FPIPE-02 | Skip marker is valid alternative | #10 |
| US-FPIPE-02 | Writing style-profile.yaml allowed | #11 |
| US-FPIPE-02 | Block message includes guidance | #8 |
| US-FPIPE-02 | Decisions recorded in audit log | #16, #17 |
| US-FPIPE-03 | Both evaluators registered | #1 (walking skeleton proves dispatch) |
| US-FPIPE-03 | Rules in pes-config.json | conftest.py fixture |
| US-FPIPE-03 | Existing interface pattern | All scenarios use evaluate() |

## Implementation Sequence

Enable one scenario at a time, implement, pass, commit:

1. Walking skeleton (no @skip tag) -- proves end-to-end wiring
2. #2 Block figure write -- focused figure pipeline gate blocking
3. #4 Allow writing figure-specs.md -- prerequisite creation path
4. #3 Block Edit -- verifies Edit tool parity with Write
5. #5 Allow figure write with both gates passing -- happy path
6. #8 Block without style profile -- style gate blocking
7. #9 Allow with style profile -- style gate happy path
8. #10 Allow with skip marker -- style gate alternative path
9. #11 Allow writing style-profile.yaml -- style prerequisite creation
10. #6 Allow figure-log.md -- non-figure file in visual assets
11. #7 Allow external brief -- subdirectory write
12. #12 Multi-proposal path -- path resolution
13. #13 Legacy path -- path resolution
14. #14 Non-interference: outside wave-5-visuals
15. #15 Non-interference: Read operation
16. #16 Audit trail: block entry
17. #17 Audit trail: allow entry
