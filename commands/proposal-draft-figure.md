---
description: "Generate a specific figure by name from the figure specification with prompt preview and structured critique"
argument-hint: "<figure-name> - Name of the figure from the figure plan"
---

# /proposal draft figure [name]

Generate a specific figure by name from the figure specification. Includes prompt preview for AI-generated figures and a structured critique loop with per-category quality ratings.

## Usage

```
/proposal draft figure "system-architecture"
/proposal draft figure "project-timeline"
```

## Prerequisites

- `/proposal wave visuals` completed (figure specs exist at `./artifacts/wave-5-visuals/figure-specs.md`)
- Figure name must match an entry in the figure specifications

## Flow

1. **Read specifications** -- Load figure specs from `./artifacts/wave-5-visuals/figure-specs.md`
2. **Look up figure** -- Find the figure matching `[name]` argument. Error if not found.
3. **Check tool availability** -- Verify the generation method tools are available (Mermaid CLI, Graphviz, Python, LaTeX compilers, Nano Banana)
4. **Prompt preview** (Nano Banana figures only) -- Construct an engineered prompt using the five-section template (COMPOSITION, STYLE, LABELS, AVOID, RESOLUTION):
   - Inject metadata from the figure specification and style profile values
   - Display the full prompt text to the user
   - User chooses: **generate** (proceed) | **edit prompt** (modify text) | **switch method** | **skip figure**
   - Generation does not begin until the user confirms
   - If `GEMINI_API_KEY` is not set, display the engineered prompt for external use and offer: switch to SVG or write external brief
5. **TikZ routing** (LaTeX proposals with diagram-type figures) -- If proposal format is LaTeX and a compiler is detected and figure type is diagram-compatible, offer TikZ alongside other methods:
   - On success: save `.tex` source and `.pdf` preview
   - On compilation failure: display error with line context, offer edit/SVG fallback/defer
6. **Generate draft** -- Dispatch to `sbir-formatter` agent to generate using the confirmed method
7. **Structured critique** -- Present the figure with five quality categories, each rated 1-5:
   - **Composition** (spatial layout, visual hierarchy, element arrangement)
   - **Labels** (text clarity, label placement, readability)
   - **Accuracy** (technical correctness, completeness of required elements)
   - **Style match** (consistency with approved style profile)
   - **Scale / Proportion** (element sizing, relative proportions, whitespace balance)
   - Includes free-text notes field
   - If all categories rate 3 or above: prominently offer **approve as-is**
   - Other options: **regenerate** (different method) | **defer to external**
8. **Refinement loop** (categories rated below 3) -- Per-category prompt adjustments:
   - Preserve prompt sections for well-rated categories (4-5: locked, 3: preserved)
   - Show prompt diff (additions/removals) to user before regeneration
   - Maximum **3 refinement iterations** per figure
   - After 3rd iteration: offer approve current, switch to TikZ, switch to SVG, defer, or write external brief
   - Record per-iteration category ratings in figure log

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `[name]` | Yes | Figure name from figure plan (matches `figure-specs.md` entry) |

## Context Files

- `./artifacts/wave-5-visuals/figure-specs.md` -- Figure specifications from `/proposal wave visuals`
- `./artifacts/wave-5-visuals/style-profile.yaml` -- Approved style profile (palette, tone, avoid list)
- `skills/formatter/visual-asset-generator.md` -- Loaded by agent for generation methodology and prompt templates
- `skills/formatter/visual-style-intelligence.md` -- Loaded by agent for style profile integration and prompt styling

## Examples

Generate a Nano Banana figure with prompt preview:
```
/proposal draft figure "deployment-scenario"

Prompt preview:
  COMPOSITION: Technical illustration of compact directed energy system on naval vessel...
  STYLE: Professional, formal-authoritative tone. Palette: #003366, #336699, #66CCFF...
  LABELS: Component labels for phased array, beam path, operator console...
  AVOID: Cartoon style, bright neon colors, cluttered backgrounds...
  RESOLUTION: 16:9, 2K

[generate] [edit prompt] [switch method] [skip figure]
> generate

Generating via Nano Banana...

Critique:
  Composition: 4/5 | Labels: 2/5 | Accuracy: 4/5 | Style match: 5/5 | Scale: 3/5
  Notes: Label text too small, overlapping near console area

Labels rated below 3 -- preparing refinement:
  LABELS section: +increase font size to 14pt +reposition console labels above components
  Other sections: locked (rated 4+)

[regenerate with adjustments] [edit adjustments] [approve current] [defer]
```

Generate a Mermaid figure (no prompt preview needed):
```
/proposal draft figure "system-architecture"

Figure: system-architecture (Figure 3)
Method: Mermaid (flowchart TB)
Section: 3.1 Technical Approach
File: ./artifacts/wave-5-visuals/system-architecture.svg

Critique:
  Composition: 4/5 | Labels: 4/5 | Accuracy: 5/5 | Style match: 3/5 | Scale: 4/5
  All categories 3+ -- approve recommended

[approve as-is] [regenerate] [defer]
```

TikZ figure in LaTeX proposal:
```
/proposal draft figure "block-diagram"

LaTeX compiler detected: pdflatex
Figure type: block-diagram (TikZ-compatible)
Method options: [TikZ] [Mermaid] [SVG] [Nano Banana]
> TikZ

Compiling TikZ source... success
Preview: ./artifacts/wave-5-visuals/block-diagram.pdf
Source: ./artifacts/wave-5-visuals/block-diagram.tex

Critique:
  Composition: 5/5 | Labels: 5/5 | Accuracy: 4/5 | Style match: 4/5 | Scale: 5/5
[approve as-is] [regenerate] [defer]
```

Figure not found:
```
Figure "deployment-view" not found in figure-specs.md
Available figures: system-architecture, project-timeline, data-flow, trl-progression
```

Specs not yet generated:
```
Figure specifications not found at ./artifacts/wave-5-visuals/figure-specs.md
Run /proposal wave visuals first to generate figure specifications.
```

## Implementation

This command dispatches to the `sbir-formatter` agent (Wave 5 figure generation).

Domain service: `VisualAssetService` (driving port)
- `generate_figure(placeholder)` -- Routes by `generation_method` (Mermaid -> SVG, TikZ -> PDF, Nano Banana -> PNG, external -> brief)
- `replace_figure(figure_number, new_path)` -- Replaces a figure with a manually created file

Domain models (`visual_asset.py`):
- `FigurePlaceholder` -- Figure slot with `figure_number`, `section_id`, `description`, `figure_type`, `generation_method`
- `GeneratedFigure` -- Produced figure artifact with `figure_number`, `section_id`, `file_path`, `format`
- `ExternalBrief` -- Brief for non-generatable figures with `content_description`, `dimensions`, `resolution`

The formatter agent loads `skills/formatter/visual-asset-generator.md` for generation methodology and prompt templates, and `skills/formatter/visual-style-intelligence.md` for style profile integration.

## Agent Invocation

@sbir-formatter

Generate the named figure using the confirmed method from figure specs. Present prompt preview for Nano Banana figures. Apply structured critique with per-category ratings and refinement loop.
