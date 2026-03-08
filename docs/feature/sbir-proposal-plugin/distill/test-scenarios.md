# Acceptance Test Scenarios -- SBIR Proposal Plugin (Phase C1)

## Scenario Inventory

| Feature File | Story | Walking Skeleton | Happy Path | Edge Case | Error Path | Total |
|-------------|-------|-----------------|------------|-----------|------------|-------|
| walking_skeleton.feature | All | 3 | 0 | 0 | 0 | 3 |
| proposal_state.feature | US-007 | 0 | 2 | 0 | 3 | 5 |
| corpus_ingestion.feature | US-003 | 0 | 2 | 1 | 3 | 6 |
| new_proposal.feature | US-002 | 0 | 4 | 1 | 2 | 7 |
| proposal_status.feature | US-001 | 0 | 3 | 1 | 1 | 5 |
| compliance_matrix.feature | US-004 | 0 | 2 | 2 | 2 | 6 |
| tpoc_questions.feature | US-005 | 0 | 2 | 2 | 2 | 6 |
| strategy_brief.feature | US-009 | 0 | 2 | 2 | 2 | 6 |
| pes_enforcement.feature | US-006 | 0 | 2 | 1 | 4 | 7* |
| compliance_check.feature | US-008 | 0 | 2 | 0 | 2 | 4 |
| **Total** | | **3** | **21** | **10** | **21** | **55** |

*US-006 includes 2 property-tagged scenarios counted under edge/error.

## Error Path Ratio

- Error + Edge scenarios: 31 / 55 = **56%** (exceeds 40% target)
- Property-tagged scenarios: 2 (atomic writes, rule extensibility)

## Story-to-Scenario Traceability

### US-001: Proposal Status and Reorientation (5 scenarios)
| AC | Scenario | Feature File |
|----|----------|-------------|
| Status displays wave, progress, deadline | Status shows current wave, progress, and deadline | proposal_status |
| Shows pending async events | Status shows pending async events | proposal_status |
| Suggests concrete next action | Status shows pending async events (includes suggestion) | proposal_status |
| PES deadline warning at threshold | Status shows deadline warning at critical threshold | proposal_status |
| Handles no proposal gracefully | Status with no active proposal | proposal_status |

### US-002: Start New Proposal from Solicitation (7 scenarios)
| AC | Scenario | Feature File |
|----|----------|-------------|
| Parses solicitation metadata | Start new proposal from local PDF file | new_proposal |
| Searches corpus for related work | Corpus search finds related past work | new_proposal |
| Scores fit and presents recommendation | Corpus search finds related past work | new_proposal |
| Go/No-Go human checkpoint | Go decision recorded and unlocks Wave 1 | new_proposal |
| Go records in state, unlocks Wave 1 | Go decision recorded and unlocks Wave 1 | new_proposal |
| No-Go archives proposal | No-Go decision archives the proposal | new_proposal |
| Empty corpus handled | Empty corpus does not block new proposal | new_proposal |
| Unparseable solicitation error | Solicitation file cannot be parsed | new_proposal |

### US-003: Directory-Based Corpus Ingestion (6 scenarios)
| AC | Scenario | Feature File |
|----|----------|-------------|
| Accepts directory, ingests supported types | Ingest a directory of past proposals | corpus_ingestion |
| Reports count and type | Ingest a directory of past proposals | corpus_ingestion |
| Skips unsupported types | Skip unsupported file types | corpus_ingestion |
| Skips unreadable documents | Corrupted or protected document skipped | corpus_ingestion |
| Incremental re-ingestion | Re-ingestion adds only new files | corpus_ingestion |
| Empty directory helpful message | Empty directory handled gracefully | corpus_ingestion |

### US-004: Automated Compliance Matrix (6 scenarios)
| AC | Scenario | Feature File |
|----|----------|-------------|
| Extracts shall statements | Generate compliance matrix | compliance_matrix |
| Extracts format requirements | Generate compliance matrix | compliance_matrix |
| Extracts implicit requirements | Generate compliance matrix | compliance_matrix |
| Maps items to sections | Generate compliance matrix | compliance_matrix |
| Flags ambiguities | Generate compliance matrix | compliance_matrix |
| Matrix is human-editable | Manually add a missed item | compliance_matrix |
| Compliance check displays status | Compliance matrix status shows coverage | compliance_matrix |
| Low extraction count warning | Low extraction count triggers warning | compliance_matrix |

### US-005: TPOC Question Generation and Answer Ingestion (6 scenarios)
| AC | Scenario | Feature File |
|----|----------|-------------|
| Questions from ambiguities/gaps | Generate TPOC questions | tpoc_questions |
| Categorized and prioritized | Generate TPOC questions | tpoc_questions |
| Written to editable file | Generate TPOC questions | tpoc_questions |
| Ingestion matches answers | Ingest TPOC answers from call notes | tpoc_questions |
| Delta analysis generated | Ingest TPOC answers from call notes | tpoc_questions |
| Matrix updated with clarifications | Ingest TPOC answers from call notes | tpoc_questions |
| Call never happened is valid | TPOC call never happens | tpoc_questions |

### US-006: PES Foundation (7 scenarios + 2 property)
| AC | Scenario | Feature File |
|----|----------|-------------|
| Silent integrity check on startup | Session startup with clean state | pes_enforcement |
| Orphaned files detected | Session startup detects orphaned draft | pes_enforcement |
| Clean state produces no output | Session startup with clean state | pes_enforcement |
| Wave ordering enforced | Wave ordering blocks Wave 1 before Go | pes_enforcement |
| Compliance matrix required before drafting | Compliance gate blocks drafting | pes_enforcement |
| Rules configurable in pes-config | Missing configuration handled | pes_enforcement |
| Extensible via configuration | New rules can be added (property) | pes_enforcement |

### US-007: Proposal State Schema and Persistence (5 scenarios)
| AC | Scenario | Feature File |
|----|----------|-------------|
| State created by /proposal new | (covered in new_proposal) | new_proposal |
| State read/written by all commands | State saved after meaningful action | proposal_state |
| State survives restarts | State persists across sessions | proposal_state |
| Missing file helpful message | Missing state file handled | proposal_state |
| Corrupted file detected with recovery | Corrupted state detected and recovered | proposal_state |

### US-008: Simplified Compliance Check (4 scenarios)
| AC | Scenario | Feature File |
|----|----------|-------------|
| Reports coverage by status | Compliance check reports full breakdown | compliance_check |
| Shows waived items | Compliance check reports full breakdown | compliance_check |
| Missing matrix guidance | Compliance check with no matrix | compliance_check |

### US-009: Strategy Brief and Wave 1 Checkpoint (6 scenarios)
| AC | Scenario | Feature File |
|----|----------|-------------|
| Brief synthesizes all sources | Strategy brief from full context | strategy_brief |
| Covers required topics | Strategy brief from full context | strategy_brief |
| Generated without TPOC answers | Strategy brief without TPOC | strategy_brief |
| Human checkpoint approve/revise/skip | Strategy checkpoint approve | strategy_brief |
| Approval unlocks Wave 2 | Strategy checkpoint approve | strategy_brief |
| Revision cycles regenerate | Strategy revision with feedback | strategy_brief |

## Implementation Sequence

One scenario enabled at a time. Recommended order follows story dependencies:

1. `proposal_state.feature` -- "Missing state file handled gracefully" (first enabled)
2. `proposal_state.feature` -- "State saved after every meaningful action"
3. `proposal_state.feature` -- "State persists across sessions"
4. `proposal_state.feature` -- "State file is never partially written" (property)
5. `proposal_state.feature` -- "Corrupted state file detected and recovered"
6. `pes_enforcement.feature` -- "Session startup with clean state is silent"
7. `pes_enforcement.feature` -- "Wave ordering blocks Wave 1 before Go decision"
8. `pes_enforcement.feature` -- "Wave ordering allows Wave 1 after Go decision"
9. `corpus_ingestion.feature` -- "Ingest a directory of past proposals and debriefs"
10. `corpus_ingestion.feature` -- "Re-ingestion adds only new files"
11. `corpus_ingestion.feature` -- "Skip unsupported file types in directory"
12. `corpus_ingestion.feature` -- "Empty directory handled gracefully"
13. `corpus_ingestion.feature` -- "Corrupted or protected document skipped with warning"
14. `corpus_ingestion.feature` -- "Non-existent directory path rejected"
15. `new_proposal.feature` -- "Start new proposal from local PDF file"
16. `new_proposal.feature` -- "Go decision recorded and unlocks Wave 1"
17. `new_proposal.feature` -- "No-Go decision archives the proposal"
18. `new_proposal.feature` -- "Corpus search finds related past work"
19. `new_proposal.feature` -- "Empty corpus does not block new proposal"
20. `new_proposal.feature` -- "Solicitation file cannot be parsed"
21. `new_proposal.feature` -- "Solicitation missing required metadata fields"
22. `proposal_status.feature` -- all scenarios (US-001)
23. `compliance_matrix.feature` -- all scenarios (US-004)
24. `tpoc_questions.feature` -- all scenarios (US-005)
25. `strategy_brief.feature` -- all scenarios (US-009)
26. `pes_enforcement.feature` -- remaining scenarios (US-006)
27. `compliance_check.feature` -- all scenarios (US-008)
28. `walking_skeleton.feature` -- all 3 walking skeletons (integration validation)
