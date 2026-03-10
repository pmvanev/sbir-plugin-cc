# Acceptance Test Scenarios -- SBIR Proposal Plugin (Phase C3)

## Scenario Inventory

| Feature File | Story | Walking Skeleton | Happy Path | Edge Case | Error Path | Total |
|-------------|-------|-----------------|------------|-----------|------------|-------|
| walking_skeleton_c3.feature | All | 3 | 0 | 0 | 0 | 3 |
| pes_enforcement_c3.feature | US-014 | 0 | 2 | 1 | 5 | 8* |
| visual_assets.feature | US-010 | 0 | 2 | 2 | 1 | 5* |
| formatting_assembly.feature | US-011 | 0 | 3 | 1 | 4 | 8 |
| final_review.feature | US-012 | 0 | 3 | 2 | 2 | 7 |
| submission.feature | US-013 | 0 | 3 | 0 | 3 | 6* |
| debrief_ingestion.feature | US-015 | 0 | 2 | 3 | 1 | 6* |
| debrief_request.feature | US-016 | 0 | 2 | 1 | 0 | 3 |
| **Total** | | **3** | **17** | **10** | **16** | **46** |

*Includes property-tagged scenarios counted in their category.

## Error Path Ratio

- Error + Edge scenarios: 26 / 46 = **57%** (exceeds 40% target)
- Property-tagged scenarios: 3 (C3 config extensibility, append-only tags, win/loss immutability)

## Story-to-Scenario Traceability

### US-014: PES Enforcement for C3 Invariants (11 scenarios: 8 focused + 3 in walking skeleton)

| AC | Scenario | Feature File |
|----|----------|-------------|
| PDC gate blocks Wave 5 with RED items | PDC gate blocks Wave 5 when a section has RED Tier 2 PDC items | pes_enforcement_c3 |
| PDC gate allows when GREEN | PDC gate allows Wave 5 when all sections have GREEN PDCs | pes_enforcement_c3 |
| Deadline blocking at critical threshold | Deadline blocking surfaces critical warning | pes_enforcement_c3 |
| No warning above threshold | Deadline blocking does not trigger above critical threshold | pes_enforcement_c3 |
| Submission immutability blocks writes | Submission immutability prevents edits to submitted artifacts | pes_enforcement_c3 |
| Submission immutability allows reads | Submission immutability allows reads of submitted artifacts | pes_enforcement_c3 |
| Corpus integrity blocks tag modification | Corpus integrity blocks modification of win/loss tags | pes_enforcement_c3 |
| Corpus integrity allows new tags | Corpus integrity allows appending new outcome tags | pes_enforcement_c3 |
| Audit log records C3 actions | PES audit log records all C3 enforcement actions | pes_enforcement_c3 |
| All rules configurable | All C3 enforcement rules are configurable | pes_enforcement_c3 |
| C1 invariants continue | All C3 enforcement rules are configurable (includes C1 check) | pes_enforcement_c3 |

### US-010: Visual Asset Generation (6 scenarios: 5 focused + 1 in skeleton)

| AC | Scenario | Feature File |
|----|----------|-------------|
| Inventories figure placeholders | Generate figure inventory from approved outline | visual_assets |
| Classified by type and method | Generate figure inventory from approved outline | visual_assets |
| Figures generated per method | Generate Mermaid diagram and present for review | visual_assets |
| External brief for non-generatable | Create external brief for non-generatable figure | visual_assets |
| Cross-reference catches orphans | Cross-reference validation catches orphaned reference | visual_assets |
| Cross-reference passes when valid | Cross-reference validation passes with consistent references | visual_assets |
| PES blocks with RED PDCs | PES blocks Wave 5 when sections have RED PDCs | visual_assets |

### US-011: Document Formatting and Assembly (8 scenarios)

| AC | Scenario | Feature File |
|----|----------|-------------|
| Format rules applied via templates | Apply solicitation formatting rules | formatting_assembly |
| Output medium selectable | Apply solicitation formatting rules | formatting_assembly |
| Figures inserted at correct positions | Insert figures and format references | formatting_assembly |
| References formatted consistently | Insert figures and format references | formatting_assembly |
| Jargon audit flags undefined | Jargon audit flags undefined acronyms | formatting_assembly |
| Page count within limits | Page count within solicitation limits | formatting_assembly |
| Page count over with guidance | Page count over limit with guidance | formatting_assembly |
| Compliance final check runs | Compliance matrix final check during formatting | formatting_assembly |
| Missing items flagged | Compliance matrix check flags missing items | formatting_assembly |
| Volumes assembled | Assemble volumes and present for review | formatting_assembly |
| Human checkpoint at assembly | Assemble volumes and present for review | formatting_assembly |

### US-012: Final Review (7 scenarios)

| AC | Scenario | Feature File |
|----|----------|-------------|
| Reviewer persona simulation | Reviewer persona simulation scores proposal | final_review |
| Red team identifies objections | Red team review identifies strongest objections | final_review |
| Debrief cross-check flags weaknesses | Debrief-informed review flags known weaknesses | final_review |
| Handles no debriefs gracefully | No past debriefs available | final_review |
| Issue resolution loop (max 2) | Issue resolution and re-review | final_review |
| Forced sign-off after 2 iterations | Forced sign-off after 2 review iterations | final_review |
| Human sign-off gates Wave 8 | Human sign-off unlocks Wave 8 | final_review |

### US-013: Submission Preparation (7 scenarios: 6 focused + 1 in skeleton)

| AC | Scenario | Feature File |
|----|----------|-------------|
| Portal identified from agency | Identify submission portal and apply packaging rules | submission |
| Portal-specific packaging applied | Identify submission portal and apply packaging rules | submission |
| All files verified present | Pre-submission verification passes | submission |
| Missing files block submission | Missing attachment blocks submission | submission |
| Explicit human confirmation | Human confirms submission at point of no return | submission |
| Confirmation number recorded | Manual submission with confirmation entry | submission |
| Immutable archive created | Manual submission with confirmation entry | submission |
| PES read-only enforcement | PES blocks modification after submission | submission |
| PES blocks without sign-off | PES blocks Wave 8 without Wave 7 sign-off | submission |

### US-015: Debrief Ingestion (7 scenarios: 6 focused + 1 in skeleton)

| AC | Scenario | Feature File |
|----|----------|-------------|
| Debrief parsed from file | Ingest debrief and map critiques to sections | debrief_ingestion |
| Critiques mapped to sections | Ingest debrief and map critiques to sections | debrief_ingestion |
| Known weaknesses flagged | Ingest debrief and map critiques to sections | debrief_ingestion |
| Pattern analysis updates | Win/loss pattern analysis updates across corpus | debrief_ingestion |
| No debrief is valid state | Record outcome without debrief | debrief_ingestion |
| Awarded proposals archived | Record awarded outcome and archive winner | debrief_ingestion |
| Unstructured debriefs preserved | Ingest unstructured debrief with minimal content | debrief_ingestion |
| Win/loss tags append-only | Win/loss tags are append-only regardless of outcome changes | debrief_ingestion |
| Lessons learned checkpoint | Lessons learned human checkpoint | debrief_ingestion |

### US-016: Debrief Request Letter (3 scenarios)

| AC | Scenario | Feature File |
|----|----------|-------------|
| Letter references topic and regulations | Generate debrief request letter for DoD submission | debrief_request |
| Agency-specific procedures | Generate debrief request for NASA submission | debrief_request |
| Skipping is valid option | Skip debrief request | debrief_request |

## Implementation Sequence

Build order follows DISCUSS/DESIGN recommendation:

1. **US-014** (PES C3 Invariants) -- enforcement layer for all C3 waves
   - First enabled: Walking Skeleton 8 (PES enforcement prevents production violations)
   - Then: PDC gate blocks/allows Wave 5 (2 scenarios)
   - Then: Deadline blocking (2 scenarios)
   - Then: Submission immutability (2 scenarios)
   - Then: Corpus integrity (2 scenarios)
   - Then: Audit log, configuration (2 scenarios)

2. **US-010** (Visual Assets) -- Wave 5
   - Figure inventory, generation, external brief, cross-reference validation
   - PES gate integration scenario

3. **US-011** (Formatting & Assembly) -- Wave 6
   - Formatting rules, figure insertion, jargon audit
   - Page count, compliance check
   - Volume assembly with human checkpoint

4. **US-012** (Final Review) -- Wave 7
   - Reviewer simulation, red team, debrief cross-check
   - Issue resolution iteration
   - Sign-off gate

5. **US-013** (Submission) -- Wave 8
   - Portal identification, packaging, verification
   - Human confirmation, confirmation entry, archive
   - PES enforcement integration

6. **US-016** (Debrief Request Letter) -- small, low dependency
   - DoD letter, NASA letter, skip option

7. **US-015** (Debrief Ingestion) -- Wave 9
   - Debrief parsing, critique mapping
   - Pattern analysis, outcome recording
   - Lessons learned checkpoint
