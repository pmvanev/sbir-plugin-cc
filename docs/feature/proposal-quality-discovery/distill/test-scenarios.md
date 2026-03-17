# Test Scenarios: Proposal Quality Discovery

## Story-to-Scenario Coverage Map

| Story | Testable Aspect | Scenarios | Feature File |
|---|---|---|---|
| US-QD-001 | Proposal rating schema (quality_rating enum, winning_practices array) | 5 | artifact_schema_validation |
| US-QD-002 | Quality preferences schema (tone, detail, evidence, organization enums, practices arrays) | 10 | artifact_schema_validation |
| US-QD-003 | Writing quality profile schema (category taxonomy, sentiment, section) | 6 | artifact_schema_validation |
| US-QD-004 | Artifact assembly, persistence, merge, confidence levels | 13 + 8 | artifact_persistence, confidence_calculation |
| US-QD-005 | Strategist agency filtering, universal patterns, graceful degradation | 4 | downstream_consumption |
| US-QD-006 | Writer quality alerts matching agency/section, graceful degradation | 4 | downstream_consumption |
| US-QD-007 | Reviewer practices-to-avoid matching, graceful degradation | 2 | downstream_consumption |
| US-QD-008 | Incremental update (merge preserving originals, confidence recalculation) | 4 | artifact_persistence, confidence_calculation |

## Stories NOT Directly Testable in Python

US-QD-001 through US-QD-003 Q&A flow (guided interview, skip/finish-early, user interaction) -- these are agent conversation patterns validated by forge checklist, not pytest.

US-QD-005 through US-QD-007 actual agent behavior during proposal processing -- these are agent markdown behaviors. The tests validate the data access patterns (loading, filtering, matching) that the agents will use.

## Error Path Inventory (23 scenarios, 43% of total)

### Schema Validation Errors (9)
- Invalid tone value rejected
- Missing tone field rejected
- Custom tone without description rejected
- Invalid detail level rejected
- Invalid quality rating rejected
- Invalid outcome (not WIN/LOSS) rejected
- Empty topic ID rejected
- Invalid category (not in taxonomy) rejected
- Invalid sentiment (not positive/negative) rejected

### Persistence Errors (7)
- Missing directory created on save
- Missing quality preferences file reports absence
- Missing winning patterns file reports absence
- Missing writing quality profile reports absence
- Roundtrip preservation (3 property scenarios)

### Confidence Errors (2)
- Zero wins yields low confidence
- Negative win count validation fails

### Downstream Consumption Errors (5)
- Missing quality preferences handled gracefully
- Missing winning patterns handled gracefully
- Missing writing quality profile handled gracefully
- No matching patterns for agency (empty result, no error)
- Malformed artifact produces warning not crash

## Implementation Sequence

All 53 scenarios are currently enabled (none marked skip). For one-at-a-time TDD in the DELIVER wave, the crafter should:

1. Start with the 3 schema validation walking skeletons
2. Progress through schema validation error paths
3. Move to confidence calculation
4. Implement persistence scenarios
5. Finish with downstream consumption patterns

Each scenario should pass before enabling the next during inner-loop TDD.
