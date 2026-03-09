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

---

# Phase C2 Walking Skeletons

## Walking Skeletons (2)

C2 adds 2 walking skeletons covering Waves 2-4 (Research, Discrimination/Outline, Drafting). These complement the 3 C1 skeletons for a combined total of 5.

### Skeleton 4: Engineer completes research and builds proposal structure

**User goal:** Build the intelligence foundation and structural skeleton before drafting.

**Journey:** Generate research from strategy brief -> Approve research review -> Generate discrimination table -> Generate proposal outline -> Approve outline -> Wave 4 unlocked.

**Observable outcome:** Phil sees research covering technical landscape, market analysis, and prior awards. After approval, Phil sees discriminators for company, technical approach, and team. Phil sees every compliance item mapped to a section with page budgets. After outline approval, Wave 4 is unlocked.

**Layers exercised (as consequence of journey):**
- ResearchService (research generation and approval)
- DiscriminationService (discrimination table generation)
- OutlineService (outline generation, compliance mapping, page budgets)
- State persistence (research_summary, discrimination_table, outline status)
- PES wave transition (research approval unlocks Wave 3, outline approval unlocks Wave 4)

**Litmus test:**
1. Title describes user goal? Yes -- "completes research and builds proposal structure"
2. Then steps describe user observations? Yes -- "sees research covering...", "sees discriminators...", "sees every compliance item mapped..."
3. Non-technical stakeholder can confirm? Yes -- this is the pre-drafting intelligence and structuring workflow

### Skeleton 5: Engineer drafts a section and iterates through review

**User goal:** Write a proposal section and improve it through structured review feedback.

**Journey:** Request draft of technical approach -> See compliance-traced draft with word count -> Submit for review -> See actionable scorecard -> Iterate -> Revised section preserves approved content and addresses findings.

**Observable outcome:** Phil sees a draft addressing compliance items with word count reported. After review, Phil sees a scorecard with actionable findings. After iteration, the revised section preserves approved content and addresses the findings.

**Layers exercised (as consequence of journey):**
- DraftService (section drafting from outline)
- ReviewService (scorecard generation, finding tracking)
- Compliance verification (draft traces to compliance items)
- Iteration loop (revision preserves approved content)

**Litmus test:**
1. Title describes user goal? Yes -- "drafts a section and iterates through review"
2. Then steps describe user observations? Yes -- "sees a draft addressing compliance items", "sees a scorecard with actionable findings"
3. Non-technical stakeholder can confirm? Yes -- this is the core write-review-revise workflow

## C2 Focused Scenarios (53)

Focused scenarios test specific business rules at driving port boundaries for Waves 2-4.

Distribution:
- Wave Names / State Expansion: 7 focused scenarios
- Wave Ordering (C2): 9 focused scenarios
- Wave 2 Research: 10 focused scenarios (including 1 property)
- Wave 3 Discrimination & Outline: 11 focused scenarios (including 2 property)
- Wave 4 Drafting: 16 focused scenarios (including 2 property)

Total C2: 2 walking skeletons + 53 focused scenarios = 55 scenarios.

## Combined C1 + C2 Ratio Assessment

- Walking skeletons: 5 (target 2-5) -- meets target
- Focused scenarios: 105 across ~15 domain areas
- Error/edge path ratio: 61/110 = 55% -- exceeds 40% target
- Property scenarios: 7 (signaling property-based testing for DELIVER wave)
