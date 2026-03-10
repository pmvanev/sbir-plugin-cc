# C3 Component Boundaries -- New Domain Services, Ports, and Adapters

Extends the existing ports-and-adapters pattern established in C1/C2. All new services follow the same conventions: domain logic as pure Python, ports as abstract interfaces, adapters for infrastructure.

---

## New Domain Services

### VisualAssetService (Wave 5)

| Aspect | Detail |
|--------|--------|
| **Responsibility** | Inventory figure placeholders from outline, classify each by type/method, manage generation lifecycle, validate cross-references |
| **Driven ports** | VisualAssetPort (generate figures) |
| **Consumes** | ProposalOutline (from Wave 3), SectionDraft (from Wave 4), PES PDC gate result |
| **Produces** | FigureInventory, GeneratedFigure, CrossReferenceLog |
| **State fields** | `visuals.figure_count`, `visuals.generated_count`, `visuals.cross_refs_valid` |

### FormattingService (Wave 6)

| Aspect | Detail |
|--------|--------|
| **Responsibility** | Apply solicitation format rules via templates, insert figures at correct positions, format references, run jargon audit, verify page count |
| **Driven ports** | FormatTemplatePort (read templates), DocumentAssemblyPort (produce formatted output) |
| **Consumes** | FigureInventory, GeneratedFigures (Wave 5), compliance matrix (Wave 1), solicitation metadata |
| **Produces** | FormattedDocument, JargonAudit, PageCountReport |
| **State fields** | `formatting.output_medium`, `formatting.page_count`, `formatting.page_limit`, `formatting.jargon_issues` |

### AssemblyService (Wave 6)

| Aspect | Detail |
|--------|--------|
| **Responsibility** | Assemble formatted sections into volumes per solicitation structure, run final compliance check, validate all cross-references resolve |
| **Driven ports** | DocumentAssemblyPort (assemble volumes) |
| **Consumes** | FormattedDocument, compliance matrix, solicitation volume structure |
| **Produces** | AssembledVolumes, ComplianceFinalCheck |
| **State fields** | `assembly.volume_count`, `assembly.volumes[].page_count`, `assembly.compliance_check_status` |

### FinalReviewService (Wave 7)

| Aspect | Detail |
|--------|--------|
| **Responsibility** | Orchestrate reviewer persona simulation, red team review, debrief cross-check, iteration loop (max 2), sign-off gate |
| **Driven ports** | None (LLM-driven via agents; domain service tracks iteration state and sign-off) |
| **Consumes** | AssembledVolumes (Wave 6), compliance matrix, corpus debrief annotations |
| **Produces** | ReviewerScorecard, RedTeamFindings, DebriefCrossCheck, SignOffRecord |
| **State fields** | `final_review.review_round`, `final_review.sign_off_at`, `final_review.high_findings_count`, `final_review.signed_off_by` |

### SubmissionService (Wave 8)

| Aspect | Detail |
|--------|--------|
| **Responsibility** | Identify portal from agency, apply portal packaging rules, verify file completeness/naming/sizes, capture confirmation, create immutable archive |
| **Driven ports** | PortalRulesPort (read portal rules) |
| **Consumes** | AssembledVolumes (Wave 6), SignOffRecord (Wave 7), solicitation metadata |
| **Produces** | SubmissionPackage, PreSubmissionChecklist, ConfirmationRecord, ImmutableArchive |
| **State fields** | `submission.portal`, `submission.confirmation_number`, `submission.submitted_at`, `submission.archive_path`, `submission.immutable` |

### DebriefService (Wave 9)

| Aspect | Detail |
|--------|--------|
| **Responsibility** | Parse debrief feedback (structured or freeform), map critiques to proposal sections, flag known weaknesses from corpus |
| **Driven ports** | DebriefParserPort (parse debrief files) |
| **Consumes** | Submitted proposal outline (for section mapping), corpus annotations (for known weakness matching) |
| **Produces** | StructuredDebrief, CritiqueSectionMap |
| **State fields** | `learning.debrief_ingested`, `learning.critique_count`, `learning.known_weaknesses_flagged` |

### OutcomeService (Wave 9)

| Aspect | Detail |
|--------|--------|
| **Responsibility** | Record win/loss outcome, generate debrief request letter draft, update pattern analysis, archive winning proposals |
| **Driven ports** | None (writes to state and artifacts via existing ports) |
| **Consumes** | Confirmation record (Wave 8), agency metadata (for debrief letter template) |
| **Produces** | OutcomeRecord, DebriefRequestDraft, PatternAnalysis, LessonsLearned |
| **State fields** | `learning.outcome`, `learning.outcome_recorded_at`, `learning.debrief_requested`, `learning.pattern_analysis_updated` |

---

## New Ports (Driven)

### VisualAssetPort

| Aspect | Detail |
|--------|--------|
| **Purpose** | Generate visual assets from structured descriptions |
| **Methods** | `generate(description, method, output_path)`, `validate_cross_references(figures, text_references)` |
| **Adapter** | `FileVisualAssetAdapter` -- writes Mermaid/Graphviz/SVG to disk, delegates image generation to Gemini API wrapper |

### FormatTemplatePort

| Aspect | Detail |
|--------|--------|
| **Purpose** | Load agency-specific formatting rules |
| **Methods** | `load_template(agency, solicitation_type)` |
| **Adapter** | `JsonFormatTemplateAdapter` -- reads from `templates/format-rules/` |

### DocumentAssemblyPort

| Aspect | Detail |
|--------|--------|
| **Purpose** | Produce formatted documents in selected output medium |
| **Methods** | `format_document(content, template, figures, output_medium)`, `assemble_volumes(sections, structure)` |
| **Adapter** | `PythonDocxAdapter` (Word), `LatexAdapter` (LaTeX/PDF) -- see ADR-008 |

### PortalRulesPort

| Aspect | Detail |
|--------|--------|
| **Purpose** | Load portal-specific packaging rules |
| **Methods** | `load_rules(portal_name)`, `list_portals()` |
| **Adapter** | `JsonPortalRulesAdapter` -- reads from `templates/portal-rules/` |

### DebriefParserPort

| Aspect | Detail |
|--------|--------|
| **Purpose** | Parse debrief documents into structured feedback |
| **Methods** | `parse(file_path)` |
| **Adapter** | `TextDebriefParserAdapter` -- extracts text from PDF/text/markdown, delegates structured parsing to LLM via agent |

---

## New PES Rule Evaluators

### PDCGateEvaluator

| Aspect | Detail |
|--------|--------|
| **Rule type** | `pdc_gate` |
| **Triggers** | Wave 5 commands when any section has RED Tier 1 or Tier 2 PDC items |
| **State read** | Reads PDC evaluation results from `./pdcs/*.pdc` or state PDC summary |
| **Integration** | Registered in EnforcementEngine._rule_triggers() as new dispatch case |

### DeadlineBlockingEvaluator

| Aspect | Detail |
|--------|--------|
| **Rule type** | `deadline_blocking` |
| **Triggers** | Non-essential wave commands when `days_to_deadline < critical_days` |
| **State read** | `topic.deadline`, current date, `enforcement.deadlines.critical_days` |
| **Integration** | Runs on every PreToolUse check, independent of wave ordering |

### SubmissionImmutabilityEvaluator

| Aspect | Detail |
|--------|--------|
| **Rule type** | `submission_immutability` |
| **Triggers** | Any write operation to proposal artifact directories when `submission.immutable == true` |
| **State read** | `submission.immutable`, tool name (to detect write operations) |
| **Integration** | Highest priority rule -- evaluated before wave ordering |

### CorpusIntegrityEvaluator

| Aspect | Detail |
|--------|--------|
| **Rule type** | `corpus_integrity` |
| **Triggers** | Attempts to modify win/loss tags or source documents in corpus |
| **State read** | `learning.outcome` (checks for existing value before allowing overwrite) |
| **Integration** | Evaluated on state write operations targeting outcome fields |

---

## File Layout Extension

```
scripts/pes/
    domain/
        visual_asset.py             # FigureInventory, GeneratedFigure, CrossReferenceLog models
        visual_asset_service.py     # VisualAssetService
        formatting.py               # FormattedDocument, JargonAudit, PageCountReport models
        formatting_service.py       # FormattingService
        assembly.py                 # AssembledVolumes, ComplianceFinalCheck models
        assembly_service.py         # AssemblyService
        final_review.py             # ReviewerScorecard (C3), RedTeamFinding, SignOffRecord models
        final_review_service.py     # FinalReviewService
        submission.py               # SubmissionPackage, ConfirmationRecord, ImmutableArchive models
        submission_service.py       # SubmissionService
        debrief.py                  # StructuredDebrief, CritiqueSectionMap models
        debrief_service.py          # DebriefService
        outcome.py                  # OutcomeRecord, PatternAnalysis, LessonsLearned models
        outcome_service.py          # OutcomeService
        pdc_gate.py                 # PDCGateEvaluator
        deadline_blocking.py        # DeadlineBlockingEvaluator
        submission_immutability.py  # SubmissionImmutabilityEvaluator
        corpus_integrity.py         # CorpusIntegrityEvaluator
    ports/
        visual_asset_port.py        # VisualAssetPort interface
        format_template_port.py     # FormatTemplatePort interface
        document_assembly_port.py   # DocumentAssemblyPort interface
        portal_rules_port.py        # PortalRulesPort interface
        debrief_parser_port.py      # DebriefParserPort interface
    adapters/
        file_visual_asset_adapter.py
        json_format_template_adapter.py
        python_docx_adapter.py
        latex_adapter.py
        json_portal_rules_adapter.py
        text_debrief_parser_adapter.py

templates/
    format-rules/
        dod-phase-i.json            # DoD Phase I formatting rules
        nasa-phase-i.json           # NASA formatting rules
        nsf.json                    # NSF formatting rules
        doe.json                    # DOE formatting rules
    portal-rules/
        dsip.json                   # DSIP packaging rules
        grants-gov.json             # Grants.gov packaging rules
        nspires.json                # NSPIRES packaging rules
    debrief-request/
        dod-far-15-505.md           # DoD debrief request template
        nasa-debrief.md             # NASA debrief request template
```

---

## Dependency Direction (Ports-and-Adapters Compliance)

```
Adapters (infrastructure) --> Ports (interfaces) <-- Domain Services (business logic)
                                                      |
                                                      v
                                               Domain Models (value objects)
```

All new C3 components follow the same inward dependency direction as C1/C2:
- Domain models: zero imports from ports, adapters, or infrastructure
- Domain services: import domain models and port interfaces only
- Ports: abstract interfaces, no concrete dependencies
- Adapters: import ports and infrastructure libraries (python-docx, etc.)
