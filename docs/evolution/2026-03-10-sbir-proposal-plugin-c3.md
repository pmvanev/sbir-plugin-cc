# Evolution: SBIR Proposal Plugin -- Phase C3

**Date**: 2026-03-10
**Feature**: sbir-proposal-plugin
**Phase**: C3 (Waves 5-9: Visual Assets, Formatting & Assembly, Final Review, Submission, Post-Submission Learning)
**Status**: COMPLETE

## Summary

Phase C3 extended the Proposal Enforcement System (PES) Python domain layer to cover Waves 5 through 9 of the SBIR proposal lifecycle. This adds visual asset generation and review, template-based document formatting and volume assembly, simulated government evaluator final review with red team and debrief cross-check, portal-specific submission packaging with immutable archiving, and post-submission learning (debrief ingestion, win/loss pattern analysis, debrief request letter generation). All domain logic follows ports-and-adapters architecture with pure Python domain objects.

With C3 complete, the feature is spec-complete for Waves 0-9 -- the full SBIR proposal lifecycle from solicitation intake through post-submission learning.

## Scope

### Phase 01: PES C3 Enforcement -- US-014 (1 step)

| Step | Description | Result |
|------|-------------|--------|
| 01-01 | PES C3 rule evaluators and state schema v2.0.0 extension | PASS |

### Phase 02: Visual Assets -- US-010 (2 steps)

| Step | Description | Result |
|------|-------------|--------|
| 02-01 | Visual asset domain models and port | PASS |
| 02-02 | Visual asset generation and review lifecycle | PASS |

### Phase 03: Formatting & Assembly -- US-011 (3 steps)

| Step | Description | Result |
|------|-------------|--------|
| 03-01 | Format template port and agency templates | PASS |
| 03-02 | Document formatting, figure insertion, and jargon audit | PASS |
| 03-03 | Volume assembly and compliance final check | PASS |

### Phase 04: Final Review -- US-012 (2 steps)

| Step | Description | Result |
|------|-------------|--------|
| 04-01 | Final review domain models and service | PASS |
| 04-02 | Review sign-off and Wave 8 gate | PASS |

### Phase 05: Submission -- US-013 (3 steps)

| Step | Description | Result |
|------|-------------|--------|
| 05-01 | Portal rules port and submission packaging | PASS |
| 05-02 | Submission confirmation, immutable archive, and read-only enforcement | PASS |
| 05-03 | Status service extension for C3 waves | PASS |

### Phase 06: Debrief Request Letter -- US-016 (2 steps)

| Step | Description | Result |
|------|-------------|--------|
| 06-01 | Outcome recording and debrief request letter generation | PASS |
| 06-02 | Awarded proposal archiving with outcome tags | PASS |

### Phase 07: Debrief Ingestion & Learning -- US-015 (2 steps)

| Step | Description | Result |
|------|-------------|--------|
| 07-01 | Debrief parsing and critique-to-section mapping | PASS |
| 07-02 | Win/loss pattern analysis, corpus update, and lessons learned | PASS |

## Execution Statistics

- **Phases**: 7
- **Steps**: 15/15 COMMIT/PASS
- **User stories**: 7 (US-010 through US-016)
- **Tests**: 359 (baseline was 242 from C2, net gain of 117)
- **Refactoring**: L1-L4 applied across steps, plus post-review D1-D3 remediation
- **Adversarial review**: 1 defect found (D1 -- domain I/O violation), remediated in refactoring commit
- **Mutation testing**: SKIPPED -- mutmut does not support Windows/MINGW64 natively
- **DES integrity**: PASSED -- all 15 steps have complete execution traces in execution-log.json

## Execution Timeline

- **Start**: 2026-03-10T22:32:39Z (step 01-01 PREPARE)
- **End**: 2026-03-11T01:00:00Z (step 07-02 COMMIT)
- **Duration**: approximately 147 minutes

## Review Finding and Remediation

The adversarial review identified one defect cluster (D1-D3) related to domain layer purity:

| Finding | Severity | Description | Remediation |
|---------|----------|-------------|-------------|
| D1 | HIGH | Domain services (OutcomeService, DebriefService, SubmissionService) contained direct file I/O via pathlib/json/shutil | Extracted into 3 new driven ports: ArtifactWriterPort, TemplateLoaderPort, ArchiveCreatorPort with filesystem adapters |
| D2 | MEDIUM | CorpusEntry.path used pathlib.Path (infrastructure type in domain model) | Changed to str for domain model purity |
| D3 | MEDIUM | Unit tests used tmp_path (filesystem coupling) instead of in-memory fakes | Replaced with FakeArtifactWriter, FakeArchiveCreator, FakeTemplateLoader |

Remediation commit: `969e0a1 refactor(sbir-proposal-plugin): extract domain I/O into ports per review D1-D3`
All 359 tests remained green after remediation.

## Architectural Decisions (C3)

| ADR | Title | Status |
|-----|-------|--------|
| ADR-008 | Document formatting engine selection (python-docx + WeasyPrint) | Accepted |
| ADR-009 | Submission portal packaging as data-driven adapters | Accepted |
| ADR-010 | Debrief parsing strategy -- best-effort with freeform fallback | Accepted |
| ADR-011 | Visual asset generation -- local-first with API fallback | Accepted |
| ADR-012 | State schema evolution for C3 | Accepted |

## Domain Services Added

| Module | Purpose |
|--------|---------|
| `scripts/pes/domain/visual_asset.py` | FigurePlaceholder, FigureInventory, GeneratedFigure, CrossReferenceLog value objects |
| `scripts/pes/domain/visual_asset_service.py` | Figure inventory, generation lifecycle, review checkpoint, cross-reference validation |
| `scripts/pes/domain/formatting.py` | FormatTemplate, JargonAuditEntry, PageCountResult domain models |
| `scripts/pes/domain/formatting_service.py` | Template-based formatting, figure insertion, jargon audit, page count verification |
| `scripts/pes/domain/assembly.py` | AssembledVolume, ComplianceFinalCheck domain models |
| `scripts/pes/domain/assembly_service.py` | Volume assembly, compliance matrix final check, human checkpoint |
| `scripts/pes/domain/final_review.py` | ReviewerScorecard, RedTeamFinding, DebriefCrossCheckEntry, SignOffRecord models |
| `scripts/pes/domain/final_review_service.py` | Reviewer simulation, red team, debrief cross-check, iteration loop (max 2), sign-off gate |
| `scripts/pes/domain/submission.py` | SubmissionPackage, PortalRule, PreSubmissionCheck, ConfirmationRecord models |
| `scripts/pes/domain/submission_service.py` | Portal identification, packaging, pre-submission verification, confirmation capture, archive |
| `scripts/pes/domain/outcome.py` | OutcomeRecord, DebriefRequestLetter, WinLossPattern, LessonsLearned models |
| `scripts/pes/domain/outcome_service.py` | Outcome recording, debrief request letter generation, awarded archiving, pattern analysis |
| `scripts/pes/domain/debrief.py` | StructuredDebrief, CritiqueSectionMap, ParsedCritique models |
| `scripts/pes/domain/debrief_service.py` | Debrief parsing, critique-to-section mapping, weakness flagging |
| `scripts/pes/domain/pdc_gate.py` | PDC gate evaluator -- blocks Wave 5 when sections have RED Tier 1/2 PDC items |
| `scripts/pes/domain/deadline_blocking.py` | Deadline blocking evaluator -- warns at critical threshold, blocks non-essential waves |
| `scripts/pes/domain/submission_immutability.py` | Submission immutability evaluator -- blocks writes to submitted artifacts |
| `scripts/pes/domain/corpus_integrity.py` | Corpus integrity evaluator -- enforces append-only on win/loss tags |

## Ports Added

| Module | Purpose |
|--------|---------|
| `scripts/pes/ports/visual_asset_port.py` | Driven port: figure generation (Mermaid/Graphviz/SVG/API) |
| `scripts/pes/ports/format_template_port.py` | Driven port: agency format template loading |
| `scripts/pes/ports/document_assembly_port.py` | Driven port: document assembly (Word/LaTeX/PDF) |
| `scripts/pes/ports/portal_rules_port.py` | Driven port: portal packaging rules |
| `scripts/pes/ports/debrief_parser_port.py` | Driven port: debrief file parsing (PDF/text) |
| `scripts/pes/ports/artifact_writer_port.py` | Driven port: artifact file writing (post-review D1 extraction) |
| `scripts/pes/ports/template_loader_port.py` | Driven port: template file loading (post-review D1 extraction) |
| `scripts/pes/ports/archive_port.py` | Driven port: archive creation (post-review D1 extraction) |

## Adapters Added

| Module | Purpose |
|--------|---------|
| `scripts/pes/adapters/file_visual_asset_adapter.py` | Filesystem adapter for figure generation output |
| `scripts/pes/adapters/json_format_template_adapter.py` | JSON adapter for agency format templates |
| `scripts/pes/adapters/python_docx_adapter.py` | python-docx adapter for Word document assembly |
| `scripts/pes/adapters/json_portal_rules_adapter.py` | JSON adapter for portal packaging rules |
| `scripts/pes/adapters/text_debrief_parser_adapter.py` | Text adapter for debrief parsing |
| `scripts/pes/adapters/filesystem_artifact_writer_adapter.py` | Filesystem adapter for artifact writes (post-review D1) |
| `scripts/pes/adapters/filesystem_template_loader_adapter.py` | Filesystem adapter for template loading (post-review D1) |
| `scripts/pes/adapters/filesystem_archive_adapter.py` | Filesystem adapter for archive creation (post-review D1) |

## Modified Modules

| Module | Change |
|--------|--------|
| `scripts/pes/domain/engine.py` | Dispatch for 4 new rule types: pdc_gate, deadline_blocking, submission_immutability, corpus_integrity |
| `scripts/pes/domain/state.py` | Schema v2.0.0 with visuals, formatting, review, submission, learning fields |
| `scripts/pes/domain/wave_rules.py` | Wave 5-8 prerequisites (PDC gate, sign-off, figure approval) |
| `scripts/pes/domain/status_service.py` | C3 wave progress, deadline warnings, submission status reporting |
| `scripts/pes/domain/corpus.py` | CorpusEntry.path changed from Path to str (D2 remediation) |

## Data Templates Added

| File | Purpose |
|------|---------|
| `templates/format-rules/dod-phase-i.json` | DoD Phase I formatting rules |
| `templates/format-rules/nasa-phase-i.json` | NASA Phase I formatting rules |
| `templates/format-rules/nsf.json` | NSF formatting rules |
| `templates/format-rules/doe.json` | DOE formatting rules |
| `templates/portal-rules/dsip.json` | DSIP portal packaging rules |
| `templates/portal-rules/grants-gov.json` | Grants.gov portal packaging rules |
| `templates/portal-rules/nspires.json` | NSPIRES portal packaging rules |
| `templates/debrief-request/dod-far-15-505.md` | DoD FAR 15.505 debrief request letter template |
| `templates/debrief-request/nasa-debrief.md` | NASA debrief request letter template |

## Quality Gates

| Gate | Status | Evidence |
|------|--------|----------|
| TDD discipline | PASSED | All 15 steps followed PREPARE > RED > GREEN > COMMIT cycle |
| Unit tests | PASSED | 359 tests passing |
| Acceptance tests | PASSED | 46 C3 scenarios across 8 feature files |
| Adversarial review | APPROVED | D1-D3 findings remediated, all tests green |
| Mutation testing | SKIPPED | Platform limitation (Windows/MINGW64) |
| DES integrity | PASSED | 15/15 steps with complete execution traces |

## Decisions

- **PES gates first**: C3 PES evaluators (PDC gate, deadline blocking, submission immutability, corpus integrity) built before wave services, establishing enforcement layer for all subsequent waves.
- **Data-driven templates**: Agency format rules, portal packaging rules, and debrief request letter templates are JSON/Markdown data files, not code. New agencies or portal changes require no code modifications.
- **Best-effort debrief parsing**: Structured extraction attempted first; unstructured debriefs preserved as freeform text rather than discarded. Confidence levels noted with small corpus sizes.
- **Domain I/O extraction**: Post-review refactoring extracted all file I/O from domain services into driven ports (ArtifactWriter, TemplateLoader, ArchiveCreator), restoring ports-and-adapters purity across all C3 services.
- **Mutation testing deferral**: mutmut skipped due to MINGW64 incompatibility. To be addressed when CI pipeline (GitHub Actions, Linux runner) is operational.

## Cumulative Test Growth

| Phase | Tests | Net Gain |
|-------|-------|----------|
| C1 | 126 | 126 (baseline) |
| C2 | 242 | +116 |
| C3 | 359 | +117 |

## What Comes Next

- **Mutation testing**: Execute via GitHub Actions CI on Linux runner to close the gap from C2/C3
- **Integration testing**: End-to-end scenarios validating cross-wave state transitions across all 10 waves
- **Agent and command markdown**: Implement the 7 C3 slash commands and agent definitions that invoke these domain services
- **Skills authoring**: Create the 4 new C3 skills (visual-asset-generator, reviewer-persona-simulator, win-loss-analyzer, proposal-archive-reader)
