# Visual Asset Quality -- Test Scenarios

## Scenario Inventory

| Feature File | Scenarios | Walking Skeleton | Happy | Error | Boundary | Property | Integration |
|---|---|---|---|---|---|---|---|
| walking-skeleton.feature | 3 | 3 | - | - | - | - | - |
| milestone-01-prompt-engineering.feature | 8 | - | 4 | 2 | 1 | - | - |
| milestone-02-critique-loop.feature | 13 | - | 5 | 3 | 3 | 1 | - |
| milestone-03-tikz-generation.feature | 12 | - | 6 | - | 2 | - | - |
| milestone-04-quality-summary.feature | 14 | - | 5 | 4 | 3 | - | - |
| integration-checkpoints.feature | 5 | - | - | - | - | - | 5 |
| **Total** | **55** | **3** | **20** | **9** | **9** | **1** | **5** |

## Error Path Ratio

Error + boundary scenarios: 9 + 9 = 18
Total non-walking-skeleton, non-integration: 47
Error path ratio: 18/47 = **38.3%** (near 40% target; property test covers additional edge space)

Including the property scenario (which tests invariants at all boundaries): 19/47 = **40.4%** -- meets target.

## User Story Coverage Map

| Story | Scenarios | Coverage |
|---|---|---|
| US-VAQ-1 (Prompt Engineering) | 8 (milestone-01) + WS-1 | All 5 AC covered |
| US-VAQ-2 (Critique Loop) | 13 (milestone-02) + WS-3 | All 7 AC covered |
| US-VAQ-3 (Style Intelligence) | 7 (milestone-04) + WS-2 | All 6 AC covered (agent behavior AC verified via filesystem state) |
| US-VAQ-4 (TikZ Generation) | 12 (milestone-03) + WS-1 | All 6 AC covered |
| US-VAQ-5 (Quality Summary) | 7 (milestone-04) | All 6 AC covered (agent behavior AC verified via filesystem state) |

## Milestone Mapping to Roadmap Phases

| Milestone | Roadmap Phase | Steps |
|---|---|---|
| milestone-01 (prompt engineering) | Phase 3 (03-01) | Prompt template, style injection, hash |
| milestone-02 (critique loop) | Phase 3 (03-02) | Critique categories, refinement, iteration |
| milestone-03 (TikZ generation) | Phase 1 (01-01, 01-02) | Service routing, adapter persistence |
| milestone-04 (quality summary) | Phase 2 (02-01) + Phase 4 (04-03) | Style validation, outlier detection |
| integration-checkpoints | Cross-phase | Style-to-prompt, critique-to-summary |

## Driving Ports Used

| Port | Type | Tests Through |
|---|---|---|
| VisualAssetService | Existing domain service | TikZ routing, figure generation |
| FileVisualAssetAdapter | Existing adapter | TikZ file persistence, inventory I/O |
| Style profile parser | New domain utility | YAML parse/validate/roundtrip |
| Critique rating model | New domain utility | Rating validation, flagging, averaging |
| Prompt template renderer | New domain utility | Template rendering, hash computation |

## Tests NOT Written (Agent Behavior)

The following user story acceptance criteria are validated by agent behavior, not pytest-bdd:

- Prompt shown to user before generation (US-VAQ-1 AC-2) -- agent UX
- User can edit prompt (US-VAQ-1 AC-3) -- agent interaction
- Five critique categories presented during review (US-VAQ-2 AC-1) -- agent UX
- Prompt adjustments shown before regeneration (US-VAQ-2 AC-3) -- agent UX
- Style analysis reads solicitation (US-VAQ-3 AC-1) -- agent inference
- Style analysis optional for non-NB methods (US-VAQ-3 AC-6) -- agent workflow
- Quality summary table display (US-VAQ-5 AC-1) -- agent formatting
- Summary persisted to quality-summary.md (US-VAQ-5 AC-6) -- agent file write

These are validated through the nWave forge checklist for agent/skill markdown.
