---
name: visual-asset-generator
description: Domain knowledge for SBIR proposal visual asset generation -- domain model, generation lifecycle, review checkpoint, cross-reference validation, method selection, and agency format requirements
---

# Visual Asset Generator

## Domain Model

PES enforces the visual asset lifecycle through value objects and services in `scripts/pes/`.

### Value Objects (`domain/visual_asset.py`)

| Object | Role | Key Fields |
|--------|------|------------|
| `FigurePlaceholder` | A figure slot from the proposal outline (frozen) | `figure_number`, `section_id`, `description`, `figure_type`, `generation_method` |
| `FigureInventory` | Collection of all placeholders for a proposal | `placeholders: list[FigurePlaceholder]`, `.count` property |
| `GeneratedFigure` | A produced figure artifact (frozen) | `figure_number`, `section_id`, `file_path`, `format` |
| `CrossReferenceEntry` | Single text-to-figure reference (frozen) | `section_id`, `referenced_figure`, `exists` |
| `CrossReferenceLog` | Validates figure-to-text consistency | `entries`, `.orphaned_references`, `.all_valid` |
| `ExternalBrief` | Brief for figures that cannot be auto-generated (frozen) | `figure_number`, `section_id`, `content_description`, `dimensions`, `resolution` |

All frozen value objects are immutable after creation. FigureInventory and CrossReferenceLog are mutable aggregates.

### Service (`domain/visual_asset_service.py`)

`VisualAssetService` orchestrates the generation lifecycle through three driven ports:

| Port | Protocol | Purpose |
|------|----------|---------|
| `FigureGenerator` | `generate_svg(placeholder) -> str` | Produces SVG content from a placeholder |
| `FigurePersistence` | `write_figure`, `write_external_brief`, `write_cross_reference_log`, `replace_figure` | Persists all figure artifacts |
| `PdcChecker` | `all_sections_pdc_green() -> bool`, `get_red_pdc_items() -> list` | PDC gate enforcement for Wave 5 entry |

Service methods:
- `generate_figure(placeholder)` -- routes by `generation_method`: "external" creates an ExternalBrief, all others delegate to FigureGenerator for SVG
- `validate_cross_references(generated_figures, text_references)` -- builds CrossReferenceLog, flags orphaned references, persists via port
- `check_pdc_gate()` -- raises `PdcGateBlockedError` if any section has RED Tier 1+2 PDC items
- `replace_figure(figure_number, new_path)` -- swaps a generated figure with a manually provided file

### Persistence (`ports/visual_asset_port.py`, `adapters/file_visual_asset_adapter.py`)

`VisualAssetPort` (abstract): `write_inventory`, `read_inventory`, `write_cross_reference_log`, `read_cross_reference_log`

`FileVisualAssetAdapter` implements both `VisualAssetPort` and `FigurePersistence`:
- Inventory: `{artifacts_dir}/figure-inventory.json`
- Cross-reference log: `{artifacts_dir}/cross-reference-log.json`
- Generated figures: `{artifacts_dir}/figures/figure-{N}.svg`
- External briefs: `{artifacts_dir}/figures/figure-{N}-brief.json`

## Generation Lifecycle

### Step 1: PDC Gate Check
Wave 5 entry requires all sections to have Tier 1+2 PDCs GREEN. `VisualAssetService.check_pdc_gate()` enforces this. If RED items exist, generation is blocked until resolved.

### Step 2: Build Figure Inventory
Read figure plan from `./artifacts/wave-3-outline/figure-plan.md`. Create `FigurePlaceholder` for each planned figure. Write inventory via `VisualAssetPort.write_inventory()`.

### Step 3: Generate Each Figure
For each placeholder, `VisualAssetService.generate_figure()` returns a `FigureGenerationResult` with:
- `figure_number`, `section_id`, `file_path`, `format`
- `review_status`: starts as "pending"
- `review_options`: `["approve", "revise", "replace"]`

Routing logic:
- `generation_method == "external"` -> ExternalBrief (dimensions: "6.5in x 4.5in", resolution: "300 DPI")
- All other methods -> SVG via FigureGenerator, written to `figures/figure-{N}.svg`

### Step 4: Human Review Checkpoint
Each figure pauses for human review. Three outcomes:
- **approve**: Figure accepted as-is
- **revise**: Regenerate with feedback incorporated
- **replace**: User provides manual file, service calls `replace_figure()`

### Step 5: Cross-Reference Validation
After all figures are generated/approved, validate every text reference resolves:
- Build list of `text_references` (each with `section_id` and `referenced_figure`)
- `validate_cross_references()` creates `CrossReferenceLog`
- `log.orphaned_references` lists references to non-existent figures
- `log.all_valid` must be `True` before proceeding to assembly

## Figure Types and When to Use Each

| Type | When | Characteristics |
|------|------|-----------------|
| System diagram | Overall system architecture, subsystem relationships | Boxes, arrows, labels. Clear hierarchy. |
| Block diagram | Functional decomposition, data flow between components | Input/output blocks, signal flow paths |
| Timeline / Gantt | Project phases, milestones, deliverable schedule | Horizontal bars, milestone markers, phase labels |
| Chart (bar/line/pie) | Quantitative data -- performance metrics, market sizing, budget | Axes labeled with units, data sourced from research or budget |
| Concept image | Abstract concepts, operational scenarios, deployment environments | Descriptive, may reference external generation tools |
| Process flow | Step-by-step procedures, decision logic, test protocols | Flowchart nodes, decision diamonds, swim lanes |
| Comparison table (visual) | Side-by-side comparison of approaches, technologies, competitors | Structured grid with visual indicators |

## Generation Methods

### SVG (Inline Generation)
Best for: precise technical diagrams, system architectures, block diagrams.
Constraints: Keep SVG under 200 lines. Use viewBox for scaling. Avoid embedded raster images.

### Mermaid
Best for: flowcharts, sequence diagrams, Gantt charts, class diagrams.
Detection: Check `mmdc` availability before attempting render.

```bash
which mmdc 2>/dev/null && echo "mermaid-available" || echo "mermaid-unavailable"
```

### Graphviz (DOT)
Best for: complex directed graphs, dependency trees, network topology.
Detection: Check `dot` availability before attempting render.

```bash
which dot 2>/dev/null && echo "graphviz-available" || echo "graphviz-unavailable"
```

### Chart Generation
Best for: quantitative data visualization.
Approach: Python matplotlib/seaborn if available, otherwise SVG chart markup directly.

### Nano Banana (Google Gemini Image Generation)
Best for: concept figures, technical illustrations, operational scenarios, polished infographics.

**Select over SVG/Mermaid when:**
- Figure needs realistic or semi-realistic rendering
- Abstract concept that boxes-and-arrows cannot convey
- Evaluator benefits from polished, professional illustration
- Complex scenes with multiple interacting elements

**Prompt engineering for SBIR figures:**
- Lead with figure type: "Technical diagram showing...", "Concept illustration of..."
- Specify style: "Clean, professional, suitable for a government proposal. White background."
- Include all labeled elements explicitly
- Specify aspect ratio (typically 16:9 full-width, 4:3 column-width)
- Avoid: photorealistic people, logos, trademarked imagery, text-heavy layouts

```bash
scripts/nano-banana-generate.sh \
  --prompt "{detailed prompt}" \
  --output ./artifacts/wave-5-visuals/{figure-name}.png \
  --aspect-ratio 16:9 \
  --size 2K
```

Detection:
```bash
test -n "$GEMINI_API_KEY" && echo "nano-banana-available" || echo "nano-banana-unavailable"
```

Fallback: If `GEMINI_API_KEY` is not set, write an external brief for manual generation.

### Corpus Reuse
Best for: figures that already exist in a past winning proposal at adequate resolution and are relevant to the current topic.

**When to use**: A figure matching the needed type and content exists in the image corpus (discovered via `corpus images search`). The image has HIGH quality (>= 300 DPI), no compliance flags, and relevant content that needs only caption adaptation rather than full regeneration.

**How it works**: The corpus librarian's `corpus images use` command places the image file in `./artifacts/wave-5-visuals/` and creates a `FigurePlaceholder` with `generation_method: "corpus-reuse"`. During Wave 5 generation, the formatter skips generation for corpus-reuse figures and presents them for human review instead.

**Review process**:
- **approve**: Use as-is with the adapted caption. Status -> "approved". Proceeds to Wave 6 insertion.
- **revise**: Edit the caption text or adjust figure placement. Re-present after changes.
- **replace**: Abandon corpus reuse for this figure. User selects a standard generation method (SVG, Mermaid, Graphviz, chart, Nano Banana, external). The figure re-enters the normal generation flow. The method change is logged.

**Source attribution**: Every corpus-reused figure records in the figure log: source proposal ID, original figure number, agency, outcome, and the adapted caption alongside the original. This audit trail supports compliance review and intellectual property tracking.

**Limitations**: Cannot modify embedded text within raster images. If the image contains proposal-specific text rendered as pixels, the user must edit the image externally or choose "replace" to generate a new figure.

### TikZ/PGF (LaTeX Native)
Best for: diagram-type figures in LaTeX proposals where typographic consistency matters. Produces vector-sharp diagrams that compile natively with the document, matching its fonts and scaling.

**When to offer TikZ:**
- Proposal format is LaTeX (not DOCX)
- A LaTeX compiler is detected (pdflatex, xelatex, or lualatex)
- Figure type is a diagram: system-diagram, block-diagram, process-flow, comparison, or timeline

**When NOT to offer TikZ:**
- Proposal format is DOCX (TikZ requires LaTeX compilation)
- No LaTeX compiler detected (mark as "unavailable" with install help reference)
- Figure type is concept image (TikZ cannot render realistic/semi-realistic illustrations)
- Figure type is chart with complex data (matplotlib or SVG is more efficient)

**Compatible figure types:**

| Figure Type | TikZ Suitability | Notes |
|-------------|------------------|-------|
| System diagram | HIGH | Nodes, edges, labels -- TikZ excels |
| Block diagram | HIGH | Rectangular nodes with arrow connections |
| Process flow | HIGH | Flowchart nodes, decision diamonds, swim lanes |
| Comparison table | MEDIUM | Grid layout with TikZ matrix or tabular |
| Timeline / Gantt | MEDIUM | Horizontal bars and milestone markers |
| Chart (bar/line/pie) | LOW | Use pgfplots if available; matplotlib preferred |
| Concept image | NOT SUITABLE | TikZ cannot produce realistic illustrations |

**Compilation steps:**

1. Generate TikZ code as a standalone `.tex` file with `\documentclass{standalone}` and required packages (`tikz`, `pgfplots`, etc.)
2. Compile with the detected LaTeX compiler:
   ```bash
   pdflatex -interaction=nonstopmode -halt-on-error figure-{N}.tex
   ```
3. Check exit code: 0 = success, non-zero = compilation failure
4. On success: PDF preview at `wave-5-visuals/figure-{N}.pdf`, source at `wave-5-visuals/figure-{N}.tex`
5. Present PDF preview to user in the standard critique flow (same 5 categories)

**Compilation failure fallback:**

If TikZ compilation fails:
1. Display the compiler error message with the line number
2. Show the problematic TikZ source line in context
3. Offer three options:
   - **Edit TikZ source** -- user or agent fixes the syntax error, recompile
   - **Switch to SVG** -- generate an SVG version of the same diagram (automatic fallback)
   - **Defer to external** -- write external brief with the diagram specification
4. Do NOT write a broken figure file to artifacts
5. Log the compilation failure and chosen fallback in the figure log

**Detection:**
```bash
which pdflatex 2>/dev/null || which xelatex 2>/dev/null || which lualatex 2>/dev/null
```
If none found: TikZ listed as "unavailable (no LaTeX compiler detected). See /proposal setup for installation help."

**TikZ code guidelines:**
- Use `standalone` document class for isolated compilation
- Include `\usepackage{tikz}` and relevant TikZ libraries (`arrows.meta`, `positioning`, `shapes.geometric`, `fit`, `calc`)
- Use the style profile palette for node colors: `\definecolor{primary}{HTML}{RRGGBB}`
- Keep code under 150 lines for maintainability
- Use relative positioning (`right=of`, `below=of`) not absolute coordinates
- Add comments for each major section of the diagram

### External Tool (Manual Fallback)
Best for: figures no available tool can generate.
Approach: Write detailed specification brief. Track as "pending-external" in figure log. The domain model's `ExternalBrief` captures `content_description`, `dimensions`, and `resolution`.

## Method Selection Guide

| Figure Need | First Choice | Fallback |
|------------|-------------|----------|
| Figure exists in corpus at HIGH quality | Corpus Reuse | Generate with standard method |
| System architecture, block diagrams (LaTeX) | TikZ | Mermaid or SVG |
| System architecture, block diagrams (DOCX) | Mermaid or SVG | SVG inline |
| Flowcharts, sequence diagrams (LaTeX) | TikZ or Mermaid | SVG inline |
| Flowcharts, sequence diagrams (DOCX) | Mermaid | SVG inline |
| Dependency graphs, network topology | Graphviz | SVG inline |
| Data charts (bar, line, pie) | Python matplotlib | SVG inline |
| Concept figures, technical illustrations | Nano Banana | External brief |
| Deployment scenarios, operational environments | Nano Banana | External brief |
| Hardware/system visualizations | Nano Banana | External brief |
| Complex infographics | Nano Banana | External brief |
| Comparison tables (visual) | SVG | TikZ (LaTeX) or Mermaid |

## Figure Specification Format

Each figure gets a specification before generation:

```markdown
## Figure {N}: {Title}

- **Type**: {system-diagram | block-diagram | timeline | chart | concept | process-flow | comparison}
- **Method**: {svg | mermaid | graphviz | chart | nano-banana | tikz | external}
- **Purpose**: {What this figure communicates to the evaluator}
- **Content**: {Specific elements to include}
- **Cross-references**: {Section(s) that cite this figure}
- **Compliance items**: {Matrix item IDs this figure supports}
- **Caption**: {Draft caption text}
```

## Engineered Prompt Templates

### Prompt Structure

Every Nano Banana prompt is constructed from five mandatory sections. The formatter agent assembles these from the figure specification, style profile, and figure plan metadata.

```
COMPOSITION: {composition directive based on figure type}
STYLE: {tone and palette from style profile}
LABELS: {component list extracted from figure description and section content}
AVOID: {figure-type avoids + style profile avoids}
RESOLUTION: {size and aspect ratio}
```

### Section Definitions

**COMPOSITION** -- Describes the visual layout, perspective, and spatial organization. Derived from the figure type. Includes arrangement of elements, visual hierarchy, and perspective (isometric, top-down, left-to-right flow, etc.).

**STYLE** -- Visual tone and color scheme. Injected from the approved style profile (see Style Profile Injection below). Includes palette colors, illustration tone, background color, and line style.

**LABELS** -- Explicit list of every component, subsystem, or data element that must appear as a labeled element in the figure. Extracted from the figure description, the section content it cross-references, and compliance items it supports.

**AVOID** -- Explicit negative directives. Combines figure-type-specific avoids with style profile avoids. Prevents common AI generation failures (photorealistic people, unlabeled components, decorative clutter, text-heavy layouts).

**RESOLUTION** -- Output dimensions and quality. Specifies pixel density ("2K"), aspect ratio (from figure spec or default), and any agency-specific resolution requirements.

### Per-Figure-Type Prompt Patterns

#### System Diagram

```
COMPOSITION: Technical illustration showing system architecture. Exploded isometric
view or layered block layout. Clear subsystem boundaries with labeled interfaces.
Hierarchical arrangement: top-level system at top, subsystems below, external
interfaces at edges.
STYLE: {style_profile.tone} illustration. {palette.primary} and {palette.secondary}
color scheme. White background. Clean outlines. Labels in {palette.primary} with
high contrast.
LABELS: {all subsystem names}, {interface names}, {data flow labels}, {external
system connections}.
AVOID: Photorealistic rendering, unlabeled components, decorative elements,
3D perspective distortion, {style_profile.avoid}.
RESOLUTION: 2K, {aspect_ratio from figure spec, default 16:9}.
```

#### Concept Image

```
COMPOSITION: Professional technical illustration depicting {concept description}.
Scene composition showing operational context with clearly distinguishable elements.
Focal point on the primary innovation or system under discussion.
STYLE: {style_profile.tone} illustration. {palette.primary} and {palette.secondary}
color scheme. {palette.accent} for callout arrows and emphasis markers.
Clean, professional, suitable for a government proposal.
LABELS: {key concept elements}, {operational environment features}, {annotated
callouts for critical components}.
AVOID: Photorealistic people, logos, trademarked imagery, science fiction aesthetic,
cartoon/sketch style, {style_profile.avoid}.
RESOLUTION: 2K, {aspect_ratio from figure spec, default 16:9}.
```

#### Block Diagram

```
COMPOSITION: Functional block diagram showing data/signal flow between components.
Left-to-right or top-to-bottom flow direction. Input sources on left/top, output
sinks on right/bottom. Clear signal path lines with arrowheads.
STYLE: {style_profile.tone} illustration. {palette.primary} blocks with
{palette.secondary} borders. White background. {palette.accent} for signal flow
arrows. Consistent block sizing.
LABELS: {input sources}, {processing blocks}, {output sinks}, {signal types with
units where applicable}.
AVOID: Overlapping blocks, unlabeled signal paths, excessive detail inside blocks,
rounded organic shapes for technical systems, {style_profile.avoid}.
RESOLUTION: 2K, {aspect_ratio from figure spec, default 16:9}.
```

#### Timeline / Gantt

```
COMPOSITION: Horizontal timeline showing project phases and milestones. Time axis
at top or bottom with labeled intervals. Phase bars with clear start/end boundaries.
Milestone markers at key deliverables.
STYLE: {style_profile.tone} layout. {palette.primary} for phase bars.
{palette.accent} for milestone markers. {palette.secondary} for grid lines.
White background. Clean typography.
LABELS: {phase names}, {milestone labels with dates}, {deliverable names},
{time period labels}.
AVOID: Overlapping bars, unlabeled milestones, excessive decoration, 3D bar effects,
{style_profile.avoid}.
RESOLUTION: 2K, {aspect_ratio from figure spec, default 16:9}.
```

#### Chart (Bar/Line/Pie)

```
COMPOSITION: Data visualization with clearly labeled axes. Title at top. Legend
positioned to avoid obscuring data. Data points/bars/slices with direct labels
where possible. Source citation below chart.
STYLE: {style_profile.tone} chart. {palette.primary} for primary data series.
{palette.accent} for secondary series. {palette.secondary} for axes and gridlines.
White background. No gradient fills.
LABELS: {axis labels with units}, {data series names}, {data point annotations
where significant}, {source citation}.
AVOID: 3D chart effects, gradient fills, unlabeled axes, missing units,
decorative chartjunk, {style_profile.avoid}.
RESOLUTION: 2K, {aspect_ratio from figure spec, default 4:3}.
```

#### Process Flow

```
COMPOSITION: Flowchart with clear start/end nodes. Decision diamonds with
yes/no labels. Process rectangles with action descriptions. Swim lanes if
multiple actors involved. Top-to-bottom or left-to-right flow.
STYLE: {style_profile.tone} diagram. {palette.primary} for process nodes.
{palette.accent} for decision diamonds. {palette.highlight} for start/end nodes.
{palette.secondary} for flow arrows. White background.
LABELS: {process step names}, {decision conditions}, {branch labels (yes/no/
condition)}, {actor names for swim lanes}.
AVOID: Ambiguous flow directions, unlabeled decisions, excessive node count
(max 15-20 nodes), crossing flow lines, {style_profile.avoid}.
RESOLUTION: 2K, {aspect_ratio from figure spec, default 3:4 portrait}.
```

#### Comparison Table (Visual)

```
COMPOSITION: Structured grid with row headers on left, column headers on top.
Visual indicators (checkmarks, color coding, rating bars) for comparison values.
Clear cell boundaries. Summary row at bottom if applicable.
STYLE: {style_profile.tone} table. {palette.primary} for header row/column.
{palette.secondary} for cell borders. {palette.highlight} for positive indicators.
{palette.accent} for caution/warning indicators. White background.
LABELS: {row category names}, {column option names}, {cell values or indicators},
{summary labels}.
AVOID: Dense text in cells (use icons/indicators), inconsistent cell sizing,
missing legend for visual indicators, {style_profile.avoid}.
RESOLUTION: 2K, {aspect_ratio from figure spec, default 4:3}.
```

### Style Profile Injection

The style profile (from `visual-style-intelligence` skill, persisted at `{artifact_base}/wave-5-visuals/style-profile.yaml`) is injected into prompts at these points:

| Prompt Section | Injected Values | Source Field |
|---------------|-----------------|--------------|
| STYLE | `{tone} illustration` | `style_profile.tone` |
| STYLE | `{primary} and {secondary} color scheme` | `style_profile.palette.primary`, `.secondary` |
| STYLE | `{accent} for callout arrows` | `style_profile.palette.accent` (if defined) |
| STYLE | `{highlight} for secondary groupings` | `style_profile.palette.highlight` (if defined) |
| AVOID | Appended to figure-type avoids | `style_profile.avoid` (joined by ", ") |

If no style profile exists (user skipped style analysis), fall back to the default palette defined in the "Color Palette for Consistent Styling" section of this skill.

### Figure Plan Metadata Injection

The figure plan (`./artifacts/wave-3-outline/figure-plan.md`) and section content provide metadata injected into the prompt:

| Metadata | Injection Point | How Used |
|----------|----------------|----------|
| `figure_type` | Selects the per-figure-type template | Determines COMPOSITION pattern |
| `description` | COMPOSITION, LABELS | Seeded into composition narrative; key terms extracted for labels |
| `section_id` | LABELS, COMPOSITION | Section content read to extract domain terms, subsystem names, technical details |
| `compliance_items` | LABELS | Compliance matrix items (e.g., R-7) looked up; relevant requirements added as labeled elements |
| `cross_references` | COMPOSITION | Referenced sections provide context for what the figure must communicate |
| `caption` | COMPOSITION | Draft caption informs the focal point and narrative intent |

#### Metadata Injection Example

Given figure plan entry:
```markdown
## Figure 3: System Architecture
- **Type**: system-diagram
- **Purpose**: Show compact DE weapon system architecture for naval integration
- **Cross-references**: Section 3.1
- **Compliance items**: R-3, R-7
- **Caption**: Figure 3. Compact DE weapon system architecture showing subsystem integration
```

And section 3.1 content mentions: "Power Conditioning Unit, Beam Director Assembly, Target Acquisition Sensor, Thermal Management System, C2 Interface, Ship Power Bus 450V DC."

The assembled prompt becomes:
```
COMPOSITION: Technical illustration showing system architecture. Exploded isometric
view showing compact DE weapon system architecture for naval integration. Clear
subsystem boundaries with labeled interfaces. Hierarchical arrangement: top-level
system at top, subsystems below, external interfaces at edges.
STYLE: technical-authoritative illustration. #003366 and #6B7B8D color scheme.
White background. Clean outlines. Labels in #003366 with high contrast.
Use #FF6B35 for callout arrows and emphasis markers.
Use #2B7A8C for secondary groupings or status indicators.
LABELS: Power Conditioning Unit, Beam Director Assembly, Target Acquisition Sensor,
Thermal Management System, C2 Interface, Ship Power Bus 450V DC, subsystem
interfaces, data flow paths.
AVOID: Photorealistic rendering, unlabeled components, decorative elements,
3D perspective distortion, cartoon/sketch style, excessive gradients,
land-centric imagery in maritime context.
RESOLUTION: 2K, 16:9.
```

## Critique Categories and Refinement Patterns

### Five Critique Categories

Every generated figure is reviewed using five structured categories. Each category is rated 1-5, where 1 = poor and 5 = excellent. Categories rated below 3 are flagged for refinement.

| # | Category | Description | What to Evaluate |
|---|----------|-------------|------------------|
| 1 | **Composition** | Spatial layout, visual hierarchy, element arrangement | Are elements logically arranged? Is the visual flow clear? Is the perspective appropriate for the figure type? |
| 2 | **Labels** | Text clarity, label placement, readability | Are all components labeled? Are labels readable (size, contrast)? Do labels overlap or obscure content? |
| 3 | **Accuracy** | Technical correctness, completeness of required elements | Are all required subsystems/components present? Are connections/flows correct? Does the figure match the section content? |
| 4 | **Style Match** | Consistency with approved style profile | Does the palette match the style profile? Is the tone appropriate for the agency? Does it feel professional and domain-appropriate? |
| 5 | **Scale / Proportion** | Element sizing, relative proportions, whitespace balance | Are elements proportionally sized? Is whitespace balanced? Are important elements visually prominent? |

### Rating Scale

| Rating | Meaning | Action |
|--------|---------|--------|
| 5 | Excellent -- no changes needed | Preserve in refinement |
| 4 | Good -- minor issues acceptable | Preserve in refinement |
| 3 | Adequate -- at threshold, acceptable | No refinement (boundary) |
| 2 | Below standard -- specific issues identified | Flag for refinement |
| 1 | Poor -- significant rework needed | Flag for refinement |

### Per-Category Prompt Adjustment Patterns

When a category is flagged (rated below 3), the system prepares prompt additions and removals specific to that category. The user reviews adjustments before regeneration.

#### Composition (flagged)

**Additions:**
- "Clear visual hierarchy with primary element centered or at focal point"
- "Logical left-to-right / top-to-bottom flow with no ambiguous spatial relationships"
- "Balanced whitespace, no crowded regions"
- Specific layout directive based on user notes (e.g., "isometric view" or "layered horizontal layout")

**Removals:**
- Remove any conflicting layout directive from the original prompt
- Remove perspective instructions that produced the poor composition

#### Labels (flagged)

**Additions:**
- "Large clear labels, minimum 12pt equivalent, high-contrast label backgrounds"
- "No overlapping labels -- offset with leader lines if necessary"
- "Every component, interface, and data flow labeled"
- Specific label instructions from user notes (e.g., "power bus as bold line with voltage annotation")

**Removals:**
- Remove any small-font or compact-label instructions
- Remove "minimal labeling" or "clean/uncluttered" directives that caused under-labeling

#### Accuracy (flagged)

**Additions:**
- "Include all of the following components: {missing components from user notes}"
- "Correct the following: {specific inaccuracies from user notes}"
- Re-inject section content terms that were omitted in the original generation

**Removals:**
- Remove elements the user identified as incorrect or extraneous
- Remove generic placeholders that were rendered instead of specific technical content

#### Style Match (flagged)

**Additions:**
- "Use exactly these colors: {palette.primary}, {palette.secondary}, {palette.accent}"
- "Match tone: {style_profile.tone}"
- Specific style directives from user notes (e.g., "more authoritative, less casual")

**Removals:**
- Remove any color specifications that deviate from the approved palette
- Remove tone descriptors that conflict with the style profile

#### Scale / Proportion (flagged)

**Additions:**
- "Primary system/component visually largest, supporting elements proportionally smaller"
- "Balanced element sizing -- no single element dominating disproportionately"
- Specific sizing directives from user notes (e.g., "power bus connection more prominent")

**Removals:**
- Remove fixed-size instructions that caused proportion issues
- Remove "equal sizing" directives if hierarchy is needed

### Refinement Preservation Rules

During prompt refinement, sections associated with well-rated categories (rated 3 or higher) are preserved unchanged. This prevents regression in areas the user already approved.

| User Rating | Prompt Action |
|-------------|---------------|
| 4-5 (Good/Excellent) | **Lock** -- do not modify this section's prompt text |
| 3 (Adequate) | **Preserve** -- do not modify unless user explicitly requests |
| 1-2 (Below standard) | **Refine** -- apply per-category adjustments |

The refinement prompt is constructed by:
1. Copying the previous prompt verbatim
2. Applying additions for flagged categories (appended to relevant section)
3. Applying removals for flagged categories (specific string removal)
4. Leaving locked sections untouched
5. Showing the diff to the user before regeneration

### Maximum Iterations and Escape Paths

The refinement loop runs a maximum of **3 iterations** per figure. After the 3rd iteration:

| Escape Path | When to Offer | What Happens |
|-------------|---------------|--------------|
| **Approve current** | Always | Accept the current result despite remaining issues |
| **Switch to TikZ** | Labels persistently failing (Nano Banana text rendering limitation) | Generate TikZ code for precise label control; enters TikZ compilation flow |
| **Switch to SVG** | Composition/scale persistently failing | Generate SVG for pixel-precise layout control |
| **Defer to external** | All categories persistently failing | Write external brief with the engineered prompt for manual generation |
| **Write external brief** | User wants to use a different tool entirely | Save the refined prompt text for use outside the plugin |

The iteration count and per-category ratings for each iteration are recorded in the figure log for the Wave 5 quality summary.

## Agency Format Requirements

| Requirement | Typical Constraint | Check Method |
|------------|-------------------|--------------|
| Resolution | 300 DPI minimum for raster | Check image metadata or ensure vector format |
| Color mode | Grayscale for some agencies; color for others | Read solicitation FORMAT requirements |
| File size | Individual figure caps (often 2-5 MB) | Check file size after generation |
| Format | PDF, PNG, or EPS depending on agency | Match solicitation spec |
| Labeling | Figure number, title, source citation required | Verify caption and numbering |
| Accessibility | Alt text or descriptions for 508 compliance | Generate alt text for each figure |

## Figure Numbering Convention

Figures numbered sequentially per volume:
- Technical Volume: Figure 1, Figure 2, ...
- Cost Volume: Figure C-1, Figure C-2, ...
- Management Volume: Figure M-1, Figure M-2, ...

Cross-references in text use "Figure N" (capitalized). Every figure cited in text must exist. Every figure must be cited at least once. The `CrossReferenceLog.all_valid` property enforces this invariant.

## Figure Log Format

```markdown
# Figure Log

| # | Title | Type | Method | Status | File | Compliance Items |
|---|-------|------|--------|--------|------|-----------------|
| 1 | System Architecture | system-diagram | svg | approved | system-arch.svg | R-3, R-7 |
| 2 | Project Timeline | timeline | mermaid | pending-review | timeline.mmd | R-12 |
| 3 | Deployment Scenario | concept | nano-banana | approved | deployment-scenario.png | R-10 |
| 4 | Market Size | chart | external | pending-external | -- | R-15 |
| 5 | System Architecture | system-diagram | corpus-reuse | pending-manual-review | system-arch-reuse.png | R-3 |
```

Statuses: `draft` | `pending-review` | `pending-manual-review` | `revision-N` | `approved` | `pending-external` | `external-received`

These map to the `FigureGenerationResult.review_status` field in the domain model.

## Color Palette for Consistent Styling

Use a restrained, professional palette across all generated figures:

- Primary: #2563EB (blue) -- main elements, headings
- Secondary: #059669 (green) -- positive indicators, completed items
- Accent: #D97706 (amber) -- warnings, attention items
- Neutral: #4B5563 (gray) -- borders, secondary text
- Background: #FFFFFF (white) -- clean background for print
- Text: #1F2937 (dark gray) -- readable on white background

Override palette only if agency solicitation specifies branding requirements.
