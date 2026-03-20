# Visual Asset Quality -- Architecture Design

## System Context

Brownfield enhancement to the existing SBIR proposal plugin's Wave 5 visual asset pipeline. Four capabilities added: engineered prompt generation, structured critique-and-refine loop, domain-aware style intelligence, and TikZ generation for LaTeX proposals.

**Architectural approach**: Extend existing ports-and-adapters OOP (Python PES) and markdown agent/skill system. No new agents, no new commands. Enhancements delivered through skill expansion, agent behavior updates, and minimal domain model extension.

---

## C4 System Context (Level 1)

```mermaid
C4Context
    title System Context -- Visual Asset Quality Enhancement

    Person(phil, "Phil Van Every", "Solo SBIR proposal writer. Generates 4-8 figures per proposal.")

    System(plugin, "SBIR Proposal Plugin", "Claude Code plugin. Formatter agent generates visual assets in Wave 5. PES enforces lifecycle rules.")

    System_Ext(claude_code, "Claude Code", "CLI runtime. Loads agents, commands, hooks. Provides LLM reasoning and tool use.")
    System_Ext(gemini, "Google Gemini API", "Nano Banana image generation. Receives engineered prompts, returns PNG images.")
    System_Ext(latex_compiler, "LaTeX Compiler", "pdflatex/xelatex/lualatex. Compiles TikZ code to PDF. Already detected by setup wizard.")
    System_Ext(filesystem, "Local File System", "Solicitation files, proposal state, artifacts, style profiles, figure logs.")

    Rel(phil, plugin, "Invokes via slash commands", "/proposal wave visuals, /proposal draft figure")
    Rel(plugin, claude_code, "Runs within", "Plugin protocol")
    Rel(plugin, gemini, "Sends engineered prompts to", "REST API, GEMINI_API_KEY")
    Rel(plugin, latex_compiler, "Compiles TikZ code via", "Subprocess invocation")
    Rel(plugin, filesystem, "Reads solicitation, writes style profiles, figure logs, quality summaries")
```

---

## C4 Container (Level 2)

```mermaid
C4Container
    title Container Diagram -- Visual Asset Quality

    Person(phil, "Phil Van Every")

    System_Boundary(plugin, "SBIR Proposal Plugin") {
        Container(commands, "Slash Commands", "Markdown", "/proposal wave visuals (enhanced), /proposal draft figure (enhanced)")
        Container(formatter_agent, "sbir-formatter Agent", "Markdown", "Orchestrates figure generation with engineered prompts, critique loop, style analysis, TikZ routing")
        Container(vag_skill, "visual-asset-generator Skill", "Markdown", "ENHANCED: Prompt engineering templates, critique categories, refinement patterns, TikZ generation guidance")
        Container(style_skill, "visual-style-intelligence Skill", "Markdown", "NEW: Domain-style database, agency palette recommendations, style profile schema")
        Container(pes_domain, "PES Domain Model", "Python 3.12", "FigurePlaceholder with 'tikz' method, FigureGenerationResult routing")
        Container(pes_service, "VisualAssetService", "Python 3.12", "Generation routing extended for TikZ method")
        Container(state, "Proposal State", "JSON/YAML on disk", "style-profile.yaml, figure-log.md with ratings and prompt hashes")
        Container(artifacts, "Wave 5 Artifacts", "Files on disk", "Figures (PNG/SVG/PDF/TEX), quality-summary.md, external briefs")
    }

    System_Ext(claude_code, "Claude Code Runtime")
    System_Ext(gemini, "Gemini API")
    System_Ext(latex, "LaTeX Compiler")

    Rel(phil, commands, "Invokes")
    Rel(commands, formatter_agent, "Dispatches to", "@sbir-formatter")
    Rel(formatter_agent, vag_skill, "Loads prompt templates and critique patterns from")
    Rel(formatter_agent, style_skill, "Loads style database and palette recommendations from")
    Rel(formatter_agent, state, "Reads/writes style profiles, figure logs, ratings")
    Rel(formatter_agent, artifacts, "Writes figures, quality summaries")
    Rel(formatter_agent, gemini, "Sends engineered prompts to")
    Rel(formatter_agent, latex, "Compiles TikZ code via subprocess")
    Rel(claude_code, pes_domain, "Invokes via hooks for validation")
    Rel(pes_service, pes_domain, "Uses domain models")
```

---

## Delivery Surface Map

| Component | Surface | Delivery Method | Rationale |
|-----------|---------|-----------------|-----------|
| visual-asset-generator skill (enhanced) | Markdown | `skill/edit` | Prompt templates, critique categories, refinement patterns are domain knowledge |
| visual-style-intelligence skill (new) | Markdown | `forge/skill` | Style database, agency palettes, recommendation logic are domain knowledge |
| sbir-formatter agent (enhanced) | Markdown | `agent/edit` | Critique loop, style analysis step, TikZ routing are agent behavior |
| /proposal wave visuals command (enhanced) | Markdown | `command/edit` | Style analysis step added to existing command flow |
| /proposal draft figure command (enhanced) | Markdown | `command/edit` | Prompt preview and critique loop added to existing command flow |
| FigurePlaceholder domain model | Python | `code/tdd` | Add "tikz" as valid generation_method |
| VisualAssetService routing | Python | `code/tdd` | Route "tikz" method through generation pipeline |
| FigureGenerationResult extension | Python | `code/tdd` | Add prompt_hash, iteration_count fields |

---

## Component Architecture

### 1. Engineered Prompt Generation (US-VAQ-1)

**Delivery surface**: Markdown (skill + agent behavior)

The visual-asset-generator skill gains a prompt engineering section with:
- Structured prompt template: COMPOSITION, STYLE, LABELS, AVOID, RESOLUTION sections
- Per-figure-type prompt patterns (system-diagram, concept, block-diagram, etc.)
- Style profile injection point (palette, tone from style-profile.yaml)
- Figure plan metadata injection (section content, compliance items)

The formatter agent's Phase 2 (GENERATE FIGURES) gains a prompt preview step before generation. The agent constructs the prompt using skill templates, displays it, and offers: generate, edit prompt, switch method, skip.

### 2. Structured Critique and Refinement Loop (US-VAQ-2)

**Delivery surface**: Markdown (skill + agent behavior)

The visual-asset-generator skill gains:
- Five critique categories: composition, labels, accuracy, style match, scale/proportion
- Category descriptions and rating scale (1-5)
- Per-category prompt adjustment patterns (what to add/remove for each low-rated category)
- Refinement preservation rules (high-rated sections unchanged)

The formatter agent's review checkpoint is replaced with structured critique:
- Present 5 categories with descriptions
- Categories rated below 3 flagged for refinement
- System prepares prompt adjustments, shows to user, regenerates
- Maximum 3 refinement rounds, then escape paths
- Ratings recorded in figure log

### 3. Domain-Aware Visual Style Intelligence (US-VAQ-3)

**Delivery surface**: Markdown (new skill + agent behavior)

New skill `skills/formatter/visual-style-intelligence.md` contains:
- Agency-domain style database (Navy/maritime, Air Force/aerospace, Army/ground, DARPA/advanced, generic fallback)
- Per-domain entries: palette (hex), tone, detail level, avoid list
- Style profile YAML schema
- Recommendation logic guidance (read solicitation -> identify agency/domain -> recommend profile)

The formatter agent's Phase 1 (FIGURE PLAN) gains a style analysis step at the start of Wave 5:
- Read solicitation context (agency, domain, topic)
- Recommend style profile using style-intelligence skill
- Present for review, allow adjustments
- Persist to `{artifact_base}/wave-5-visuals/style-profile.yaml`
- Style profile injected into all subsequent Nano Banana prompts

### 4. TikZ Generation for LaTeX (US-VAQ-4)

**Delivery surface**: Mixed (Python domain model + Markdown agent behavior)

**Python changes** (PES domain):
- `FigurePlaceholder.generation_method` accepts "tikz" as valid value
- `VisualAssetService.generate_figure()` routes "tikz" to a new internal method
- New `_generate_tikz()` method on service returns `FigureGenerationResult` with format "tikz"

**Markdown changes** (agent/skill):
- visual-asset-generator skill gains TikZ generation section: when to offer, compilation verification, fallback guidance
- Formatter agent routes TikZ figures through: generate code -> compile via subprocess -> verify 0 errors -> save .tex + .pdf -> present for critique
- TikZ offered only when: proposal format is LaTeX AND compiler detected AND figure type is diagram-compatible

### 5. Quality Summary and Style Consistency (US-VAQ-5)

**Delivery surface**: Markdown (agent behavior)

The formatter agent's Wave 5 conclusion gains:
- Quality summary aggregation: per-figure ratings table, average quality, iteration counts
- Style consistency check: compare prompt hex codes against style-profile.yaml
- Quality outlier detection: any category 2+ points below proposal average flagged
- Persist summary to `{artifact_base}/wave-5-visuals/quality-summary.md`

---

## Integration Patterns

### Shared Artifacts (Data Flow)

```
solicitation-parsed.md -> [Style Analysis] -> style-profile.yaml
                                                    |
figure-plan.md -----> [Prompt Engineering] <--------+
                             |
                      engineered prompt (in-memory)
                             |
                      [Generate] -> figure file + figure-log.md entry
                             |
                      [Critique] -> ratings (in-memory) -> figure-log.md
                             |
                      [Refine] -> adjusted prompt -> [Generate] (loop)
                             |
                      [Approve] -> figure-log.md (final ratings, prompt hash)
                             |
                      [Conclude] -> quality-summary.md
```

### Integration Points with Existing System

| Integration | Direction | Contract |
|------------|-----------|----------|
| Solicitation context | Read | `{state_dir}/solicitation-parsed.md` -- agency, domain, topic |
| Figure plan | Read | `{artifact_base}/wave-3-outline/figure-plan.md` -- figure specs |
| Compliance matrix | Read | `{state_dir}/compliance-matrix.md` -- FORMAT items |
| Format config | Read | `proposal-state.json` field `output_format` -- "latex" or "docx" |
| LaTeX compiler detection | Read | Setup wizard detection result (check `which pdflatex`) |
| Nano Banana script | Invoke | `scripts/nano-banana-generate.sh` -- unchanged interface |
| Figure log | Write | `{artifact_base}/wave-5-visuals/figure-log.md` -- extended with ratings, prompt hash |
| Cross-reference log | Write | Existing `VisualAssetService.validate_cross_references()` -- unchanged |

---

## Quality Attribute Strategies

| Attribute | Strategy |
|-----------|----------|
| **Maintainability** | Domain knowledge in skills (easy to edit markdown), not code. Prompt templates updated without Python changes. |
| **Testability** | Python domain model changes tested via TDD. Agent/skill behavior validated via forge checklist. |
| **Time-to-market** | Minimal Python changes (add "tikz" to routing). Bulk of work is skill/agent markdown. |
| **Reliability** | TikZ compilation verified before presenting. Critique loop capped at 3 iterations. Fallback paths at every decision point. |

---

## Rejected Simple Alternatives

### Alternative 1: Prompt improvement in skill only (no structured critique)
- **What**: Update visual-asset-generator skill with better prompt templates. No critique categories, no refinement loop.
- **Expected impact**: ~40% of problem solved (better first-generation quality, but no iteration capability)
- **Why insufficient**: User stories US-VAQ-2 explicitly requires structured critique. The JTBD analysis shows iteration efficiency (16.0 score) is second-highest priority. Prompt-only improvement leaves the "take it or leave it" problem unsolved.

### Alternative 2: Style as prompt prefix only (no persisted profile)
- **What**: Add domain-aware style keywords to prompts without a persisted style profile YAML.
- **Expected impact**: ~60% of style problem solved (better per-figure style, but no cross-figure consistency)
- **Why insufficient**: US-VAQ-5 quality summary requires comparing figures against an approved profile. Without persistence, no consistency check is possible. Also, user cannot review/adjust style once and have it apply to all figures.
