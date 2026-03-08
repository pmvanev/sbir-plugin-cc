# Walking Skeleton Strategy -- SBIR Proposal Plugin

## Walking Skeletons (3)

Each skeleton traces a thin vertical slice delivering observable user value.
Stakeholder can confirm: "yes, that is what users need."

### Skeleton 1: Engineer starts a new proposal and decides to proceed

**User goal:** Evaluate a solicitation and make a data-driven Go/No-Go decision.

**Journey:** Ingest corpus -> Parse solicitation -> Search for related work -> Score fit -> Present recommendation -> Record Go decision -> Unlock Wave 1.

**Observable outcome:** Phil sees topic metadata, related past work with scores, a recommendation, and after approving Go, Wave 1 is unlocked.

**Layers exercised (as consequence of journey):**
- Corpus ingestion (state tracking of ingested files)
- Solicitation metadata extraction (via agent/LLM -- mocked in acceptance tests)
- State persistence (proposal-state.json created and updated)
- PES wave transition (Go unlocks Wave 1)

**Litmus test:**
1. Title describes user goal? Yes -- "starts a new proposal and decides to proceed"
2. Then steps describe user observations? Yes -- "sees topic", "sees related work", "sees recommendation"
3. Non-technical stakeholder can confirm? Yes -- this is the core proposal evaluation workflow

### Skeleton 2: Engineer returns after days away and regains context

**User goal:** Understand current proposal state in seconds, not minutes.

**Journey:** Read state -> Compute deadline -> Identify pending events -> Suggest next action.

**Observable outcome:** Phil sees wave progress, compliance matrix status, TPOC pending status, deadline countdown, and a suggested next action.

**Layers exercised (as consequence of journey):**
- State read (proposal-state.json)
- Deadline computation (display-time calculation)
- Status formatting (wave progress, TPOC status)

**Litmus test:**
1. Title describes user goal? Yes -- "returns and regains context"
2. Then steps describe user observations? Yes -- "sees current wave", "sees deadline", "sees suggested next action"
3. Non-technical stakeholder can confirm? Yes -- this is the daily re-entry experience

### Skeleton 3: Enforcement system prevents skipping required steps

**User goal:** Trust that process integrity is maintained automatically.

**Journey:** Attempt Wave 1 without Go decision -> PES blocks -> User sees explanation and guidance.

**Observable outcome:** Phil sees a block message explaining what is required and how to proceed.

**Layers exercised (as consequence of journey):**
- PES hook adapter (receives event)
- Enforcement engine (evaluates wave ordering rule)
- State reader (checks go_no_go value)
- Audit logger (records block decision)

**Litmus test:**
1. Title describes user goal? Yes -- "prevents skipping required steps"
2. Then steps describe user observations? Yes -- "blocks the action", "sees Wave 1 requires Go decision"
3. Non-technical stakeholder can confirm? Yes -- this is the guardrail that prevents mistakes

## Focused Scenarios (52)

Focused scenarios test specific business rules at driving port boundaries.
They use test doubles for external dependencies (Claude Code LLM) but real
PES and state management code.

Distribution by story:
- US-007 (State): 5 focused scenarios
- US-006 (PES): 9 focused scenarios (including 2 property-tagged)
- US-003 (Corpus): 6 focused scenarios
- US-002 (New Proposal): 7 focused scenarios
- US-001 (Status): 5 focused scenarios
- US-004 (Compliance Matrix): 6 focused scenarios
- US-005 (TPOC): 6 focused scenarios
- US-009 (Strategy Brief): 6 focused scenarios
- US-008 (Compliance Check): 4 focused scenarios

Total: 3 walking skeletons + 52 focused scenarios = 55 scenarios.

## Ratio Assessment

- Walking skeletons: 3 (target 2-5) -- meets target
- Focused scenarios: 52 (target 15-20 per feature) -- 52 across 9 stories averages ~6 per story, appropriate for this scope
- Error/edge path ratio: 31/55 = 56% -- exceeds 40% target
