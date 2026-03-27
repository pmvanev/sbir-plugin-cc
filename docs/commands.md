# Command Reference

| Command | Wave | Purpose |
|---------|------|---------|
| `/sbir:setup` | Pre | Guided first-time setup (profile, corpus, API key, validation) |
| `/sbir:proposal-profile-setup` | Pre | Create company profile (standalone) |
| `/sbir:proposal-profile-update` | Pre | Update company profile |
| `/sbir:proposal-partner-setup` | Pre | Create or update a research institution partner profile |
| `/sbir:proposal-partner-set <slug>` | 0+ | Designate a partner for the active proposal |
| `/sbir:proposal-partner-screen <name>` | Pre | Screen a potential partner for readiness (5 signals) |
| `/sbir:proposal-quality-discover` | Pre | Build writing quality intelligence from past proposals |
| `/sbir:proposal-quality-update` | Pre | Update quality artifacts from new debrief data |
| `/sbir:proposal-quality-status` | Pre | Show quality intelligence status |
| `/sbir:solicitation-find` | 0 | Search and rank open topics by fit |
| `/sbir:proposal-new <topic-or-file>` | 0 | Start proposal with Go/No-Go checkpoint |
| `/sbir:proposal-shape` | 0 | Generate candidate technical approaches |
| `/sbir:continue` | Any | Detect where you left off and suggest next action |
| `/sbir:proposal-status` | Any | Show current wave, progress, next actions |
| `/sbir:proposal-check` | 1+ | View compliance matrix coverage |
| `/sbir:proposal-compliance-add` | 1+ | Add missed compliance item |
| `/sbir:proposal-tpoc-questions` | 1 | Generate TPOC call questions |
| `/sbir:proposal-tpoc-ingest <file>` | 1 | Parse TPOC call notes |
| `/sbir:proposal-wave-strategy` | 1 | Generate and approve strategy brief |
| `/sbir:proposal-draft <section>` | 4 | Draft a proposal section |
| `/sbir:proposal-iterate <section>` | 4 | Submit section for reviewer iteration |
| `/sbir:proposal-wave-visuals` | 5 | Initialize figure generation |
| `/sbir:proposal-draft-figure <name>` | 5 | Generate a specific figure |
| `/sbir:proposal-format` | 6 | Format and assemble volumes |
| `/sbir:proposal-wave-final-review` | 7 | Red team review and evaluator simulation |
| `/sbir:proposal-submit-prep` | 8 | Prepare submission package |
| `/sbir:proposal-submit` | 8 | Confirm submission, lock archive |
| `/sbir:proposal-debrief <action>` | 9 | Outcome, debrief request, ingest, lessons |
| `/sbir:proposal-config-format <fmt>` | Any | Switch output format between `latex` and `docx` (warns about rework at Wave 3+) |
| `/sbir:proposal-rigor [show\|set] <profile>` | Any | View or change the rigor profile (lean / standard / thorough / exhaustive) |
| `/sbir:proposal-switch <topic-id>` | Any | Switch active proposal context in a multi-proposal workspace |
| `/sbir:proposal-developer-feedback` | Any | Submit bug reports, feature suggestions, or quality ratings with automatic context snapshot |
