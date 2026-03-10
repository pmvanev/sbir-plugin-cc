# C3 Walking Skeleton Strategy -- SBIR Proposal Plugin

## Walking Skeletons (3)

Each skeleton traces a thin vertical slice delivering observable user value.
Stakeholder can confirm: "yes, that is what users need."

### Skeleton 6: Engineer produces figures, formats document, and assembles volumes

**User goal:** Go from approved sections to a submission-ready formatted document with figures.

**Journey:** Generate figure inventory -> Generate and approve figures -> Validate cross-references -> Format proposal with solicitation rules -> Run jargon audit -> Assemble volumes -> Human checkpoint for assembled package.

**Observable outcome:** Phil sees figures classified by type and method. After generation and approval, Phil sees a cross-reference log. After formatting, Phil sees page count within limits and any undefined acronyms flagged. After assembly, Phil reviews Technical, Cost, and Company Info volumes at a human checkpoint.

**Layers exercised (as consequence of journey):**
- VisualAssetService (figure inventory, generation, cross-reference validation)
- FormattingService (template formatting, jargon audit, page count)
- AssemblyService (volume assembly, compliance final check)
- State persistence (visuals, formatting, assembly status)
- PES PDC gate (Wave 5 entry requires GREEN PDCs)

**Litmus test:**
1. Title describes user goal? Yes -- "produces figures, formats document, and assembles volumes"
2. Then steps describe user observations? Yes -- "sees figures classified", "sees formatting applied", "reviews assembled package"
3. Non-technical stakeholder can confirm? Yes -- this is the production workflow from approved content to submission-ready package

### Skeleton 7: Engineer reviews proposal, submits, and captures lessons learned

**User goal:** Complete the final mile from assembled proposal to submitted, archived, and learning captured.

**Journey:** Request final review -> See evaluation scores and red team objections -> Address HIGH issues and sign off -> Prepare submission package -> See files correctly named and sized -> Confirm submission and enter confirmation number -> Immutable archive created -> Record outcome and ingest debrief -> See critiques mapped and pattern analysis.

**Observable outcome:** Phil sees evaluation scores with rationales and red team objections. After sign-off, Wave 8 is unlocked. Phil sees files named for portal. After confirmation, artifacts are read-only. After outcome recording, Phil sees critiques mapped to sections and pattern analysis across the corpus.

**Layers exercised (as consequence of journey):**
- FinalReviewService (reviewer simulation, red team, sign-off)
- SubmissionService (portal identification, packaging, verification, confirmation, archive)
- DebriefService (debrief parsing, critique mapping)
- OutcomeService (outcome recording, pattern analysis)
- PES (sign-off gate, submission immutability)

**Litmus test:**
1. Title describes user goal? Yes -- "reviews, submits, and captures lessons learned"
2. Then steps describe user observations? Yes -- "sees evaluation scores", "sees files correctly named", "sees critiques mapped"
3. Non-technical stakeholder can confirm? Yes -- this is the review-submit-learn lifecycle

### Skeleton 8: Enforcement system prevents production and submission violations

**User goal:** Trust that production integrity is maintained by guardrails.

**Journey:** Attempt Wave 5 with RED PDC items -> PES blocks -> User sees specific section and PDC items -> Guidance to resolve.

**Observable outcome:** Phil sees a block message explaining what RED items remain and guidance to resolve them before proceeding.

**Layers exercised (as consequence of journey):**
- PES PDCGateEvaluator (checks section PDC status)
- EnforcementEngine (evaluates and blocks)
- State reader (checks PDC files)
- Audit logger (records block decision)

**Litmus test:**
1. Title describes user goal? Yes -- "prevents production and submission violations"
2. Then steps describe user observations? Yes -- "blocks the action", "sees specific section and PDC items"
3. Non-technical stakeholder can confirm? Yes -- this is the guardrail preventing premature production work

## C3 Focused Scenarios (43)

Focused scenarios test specific business rules at driving port boundaries for Waves 5-9.

Distribution:
- PES C3 Enforcement (US-014): 8 focused scenarios (including 1 property)
- Visual Assets (US-010): 5 focused scenarios
- Formatting & Assembly (US-011): 8 focused scenarios
- Final Review (US-012): 7 focused scenarios
- Submission (US-013): 6 focused scenarios
- Debrief Ingestion (US-015): 6 focused scenarios (including 1 property)
- Debrief Request Letter (US-016): 3 focused scenarios

Total C3: 3 walking skeletons + 43 focused scenarios = 46 scenarios.

## Combined C1 + C2 + C3 Ratio Assessment

- Walking skeletons: 8 (3 C1 + 2 C2 + 3 C3)
- Focused scenarios: 148 across ~22 domain areas
- Error/edge path ratio: 87/156 = 56% -- exceeds 40% target
- Property scenarios: 10 (7 C1/C2 + 3 C3)
