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

### External Tool (Manual Fallback)
Best for: figures no available tool can generate.
Approach: Write detailed specification brief. Track as "pending-external" in figure log. The domain model's `ExternalBrief` captures `content_description`, `dimensions`, and `resolution`.

## Method Selection Guide

| Figure Need | First Choice | Fallback |
|------------|-------------|----------|
| System architecture, block diagrams | Mermaid or SVG | SVG inline |
| Flowcharts, sequence diagrams | Mermaid | SVG inline |
| Dependency graphs, network topology | Graphviz | SVG inline |
| Data charts (bar, line, pie) | Python matplotlib | SVG inline |
| Concept figures, technical illustrations | Nano Banana | External brief |
| Deployment scenarios, operational environments | Nano Banana | External brief |
| Hardware/system visualizations | Nano Banana | External brief |
| Complex infographics | Nano Banana | External brief |
| Comparison tables (visual) | SVG | Mermaid |

## Figure Specification Format

Each figure gets a specification before generation:

```markdown
## Figure {N}: {Title}

- **Type**: {system-diagram | block-diagram | timeline | chart | concept | process-flow | comparison}
- **Method**: {svg | mermaid | graphviz | chart | nano-banana | external}
- **Purpose**: {What this figure communicates to the evaluator}
- **Content**: {Specific elements to include}
- **Cross-references**: {Section(s) that cite this figure}
- **Compliance items**: {Matrix item IDs this figure supports}
- **Caption**: {Draft caption text}
```

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
```

Statuses: `draft` | `pending-review` | `revision-N` | `approved` | `pending-external` | `external-received`

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
