# Skills Reference

Skills are domain-knowledge files loaded on demand by agents. They are not invoked directly — agents pull them in when needed.

| Skill | Agent | What it provides |
|-------|-------|-----------------|
| `proposal-state-schema` | common | Schema reference for `proposal-state.json` — shared by all agents that read or write proposal state |
| `compliance-domain` | compliance-sheriff | Requirement types, extraction patterns, section mappings, compliance matrix format, and wave-specific behavior |
| `continue-detection` | continue | State detection priority, wave-to-command mapping, display patterns, and error handling |
| `multi-proposal-dashboard` | continue | Enumeration patterns, display templates, corruption handling, and deadline sorting for the multi-proposal dashboard |
| `corpus-domain-knowledge` | corpus-librarian | Document types, metadata schema, ingestion workflow, and search strategies for corpus management |
| `corpus-image-reuse` | corpus-librarian | Image search strategies, fitness assessment, caption adaptation heuristics, and compliance flagging |
| `proposal-archive-reader` | corpus-librarian | Archive directory layout, immutability constraints, portal-specific packaging, and corpus ingestion strategies |
| `win-loss-analyzer` | corpus-librarian | Pattern extraction from outcome-tagged proposals, weakness profiling, and agency-specific debrief handling |
| `debrief-domain-knowledge` | debrief-analyst | Loss categorization, debrief request letter format, lessons-learned generation, and feedback distribution |
| `visual-asset-generator` | formatter | Generation lifecycle, review checkpoint, cross-reference validation, method selection, and agency format requirements |
| `visual-style-intelligence` | formatter | Agency style database, style profile schema, and recommendation workflow for visual assets |
| `proposal-state-patterns` | orchestrator | State persistence patterns, atomic writes, status rendering, and session continuity |
| `rigor-resolution` | orchestrator | Rigor profile resolution chain, agent-role mapping, and rendering logic |
| `wave-agent-mapping` | orchestrator | Wave definitions, agent routing table, and checkpoint gates |
| `partner-domain` | partner-builder | Partner profile interview guidance, schema reference, STTR eligibility rules, and combined capability analysis |
| `profile-domain` | profile-builder | Company profile field-by-field fit scoring explanations, schema reference, validation rules, and interview guidance |
| `quality-discovery-domain` | quality-discoverer | Feedback taxonomy, auto-categorization keywords, confidence thresholds, and artifact schemas |
| `market-researcher` | researcher | TAM/SAM/SOM sizing methodology, competitor landscape analysis, and commercialization pathway mapping |
| `reviewer-persona-simulator` | reviewer | Government evaluator scoring rubrics, persona construction, red team review, and iteration loop with sign-off gate |
| `setup-domain` | setup-wizard | Prerequisites check commands, validation rules, TUI display patterns, and next-steps guidance |
| `approach-evaluation` | solution-shaper | Approach scoring rubrics, generation patterns (forward/reverse/prior-art), and commercialization quick-assessment |
| `budget-scaffolder` | strategist | Cost modeling by labor category, indirect rates, materials, and phase — scaffolds realistic SBIR budgets |
| `sbir-strategy-knowledge` | strategist | Teaming patterns, Phase III pathways, risk frameworks, competitive positioning, and required brief sections |
| `trl-assessor` | strategist | TRL evidence mapping, gap feasibility analysis, and red flag detection |
| `portal-packaging-rules` | submission-agent | Portal-specific packaging requirements for DSIP, Grants.gov, NSPIRES — file naming, size limits, upload procedures |
| `dsip-cli-usage` | topic-scout | How to call the DSIP topic CLI for fetching, enriching, scoring, and inspecting topics |
| `dsip-enrichment` | topic-scout | DSIP topic detail structure, Q&A format interpretation, and enrichment data for semantic scoring |
| `finder-batch-scoring` | topic-scout | Batch scoring workflow — five-dimension scoring of candidate topics with ranked results and disqualifiers |
| `fit-scoring-methodology` | topic-scout | Five-dimension fit scoring rubrics, composite scoring algorithm, and recommendation thresholds |
| `solicitation-intelligence` | topic-scout | Solicitation sources, document format parsing, and metadata extraction into TopicInfo schema |
| `tpoc-domain` | tpoc-analyst | TPOC question generation taxonomy, conversational sequencing strategy, and delta analysis methodology |
| `discrimination-table` | writer | Three-dimension competitive positioning framework that forms the narrative spine of the proposal |
| `elements-of-style` | writer | Strunk & White writing style adapted for SBIR prose — active voice, brevity, positive form, parallel construction |
