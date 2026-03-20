# Visual Asset Quality -- Component Boundaries

## Delivery Surface Table

| Component | Surface | Method | Files | New/Modify |
|-----------|---------|--------|-------|------------|
| visual-asset-generator skill | Markdown | `skill/edit` | `skills/formatter/visual-asset-generator.md` | Modify |
| visual-style-intelligence skill | Markdown | `forge/skill` | `skills/formatter/visual-style-intelligence.md` | New |
| sbir-formatter agent | Markdown | `agent/edit` | `agents/sbir-formatter.md` | Modify |
| /proposal wave visuals command | Markdown | `command/edit` | `commands/proposal-wave-visuals.md` | Modify |
| /proposal draft figure command | Markdown | `command/edit` | `commands/proposal-draft-figure.md` | Modify |
| FigurePlaceholder + result models | Python | `code/tdd` | `scripts/pes/domain/visual_asset.py` | Modify |
| VisualAssetService TikZ routing | Python | `code/tdd` | `scripts/pes/domain/visual_asset_service.py` | Modify |
| FileVisualAssetAdapter TikZ support | Python | `code/tdd` | `scripts/pes/adapters/file_visual_asset_adapter.py` | Modify |

## Component Boundaries

### 1. visual-asset-generator Skill (Enhanced)

**Responsibility**: Domain knowledge for prompt engineering, critique categories, refinement patterns, TikZ generation guidance.

**Owns**:
- Structured prompt template (COMPOSITION, STYLE, LABELS, AVOID, RESOLUTION sections)
- Per-figure-type prompt patterns
- Five critique categories with descriptions and rating scale
- Per-category prompt adjustment patterns (additions/removals)
- Refinement preservation rules
- TikZ generation guidance (when to offer, compilation verification steps, fallback)
- Method selection guide (updated with TikZ)

**Does NOT own**:
- Style database or palette recommendations (owned by visual-style-intelligence skill)
- Agent workflow logic (owned by sbir-formatter agent)
- Domain model validation (owned by Python PES)

**Boundary contract**: Agent loads this skill and uses its templates/patterns to construct prompts and apply critique adjustments. Skill provides knowledge, agent applies it.

### 2. visual-style-intelligence Skill (New)

**Responsibility**: Domain knowledge for agency/domain visual style recommendations.

**Owns**:
- Agency-domain style database entries (Navy/maritime, Air Force/aerospace, Army/ground, DARPA/advanced)
- Generic fallback style profile
- Per-domain attributes: palette (hex codes), tone, detail level, avoid list
- Style profile YAML schema definition
- Style recommendation guidance (how to read solicitation, identify domain, recommend)

**Does NOT own**:
- Style profile persistence (owned by agent writing to disk)
- Style consistency checking logic (owned by agent at Wave 5 conclusion)
- Prompt construction (owned by visual-asset-generator skill)

**Boundary contract**: Agent loads this skill at the start of Wave 5 to recommend a style profile. Style profile is persisted as YAML and consumed by prompt engineering in the visual-asset-generator skill.

### 3. sbir-formatter Agent (Enhanced)

**Responsibility**: Orchestrates the enhanced Wave 5 visual asset workflow.

**New behavior**:
- Phase 1 (FIGURE PLAN): Add style analysis step -- load style-intelligence skill, read solicitation, recommend style, present for review, persist profile
- Phase 2 (GENERATE FIGURES): Add prompt preview before generation -- construct engineered prompt using skill templates + style profile, display, offer edit/generate/skip
- Phase 2 (GENERATE FIGURES): Replace unstructured review with structured critique -- present 5 categories, collect ratings, flag low-rated, prepare prompt adjustments, refinement loop (max 3), record ratings in figure log
- Phase 2 (GENERATE FIGURES): Add TikZ routing -- when proposal format is LaTeX and compiler detected and figure type is diagram, offer TikZ alongside other methods
- Phase 2 (GENERATE FIGURES): TikZ workflow -- generate code, compile via `pdflatex`, verify 0 errors, save .tex + .pdf, present for critique
- Post-Phase 2: Add quality summary -- aggregate ratings, check style consistency, flag outliers, persist summary

**Does NOT own**:
- Prompt template content (owned by visual-asset-generator skill)
- Style database content (owned by visual-style-intelligence skill)
- Domain model rules (owned by Python PES)
- Wave state transitions (owned by orchestrator)

### 4. PES Domain Model (Python -- Minimal Extension)

**Responsibility**: Domain rules for visual asset lifecycle.

**Changes**:
- `FigurePlaceholder.generation_method`: Accept "tikz" as valid value (no validation change needed -- field is a plain string)
- `FigureGenerationResult`: Add optional `prompt_hash` (str) and `iteration_count` (int) fields for audit
- `VisualAssetService.generate_figure()`: Add "tikz" routing case alongside "corpus-reuse", "external", and default Mermaid
- `VisualAssetService._generate_tikz()`: New method returning FigureGenerationResult with format "tikz"

**Does NOT own**:
- Prompt construction logic (agent/skill responsibility)
- Critique categories or ratings (agent/skill responsibility)
- Style profile content or persistence (agent/skill responsibility)
- TikZ code generation (agent generates via LLM; Python only routes and records result)

**Boundary contract**: Python domain model validates and routes. The agent generates the actual TikZ code (via LLM) and invokes the compiler. Python service records the result with file paths and format metadata.

### 5. Commands (Enhanced)

**`/proposal wave visuals`**: Add documentation of style analysis step. No structural change -- still dispatches to @sbir-formatter.

**`/proposal draft figure`**: Add documentation of prompt preview and critique loop. No structural change -- still dispatches to @sbir-formatter.

Commands are thin dispatchers. All behavior changes are in the agent and skills.
