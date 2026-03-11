# /proposal draft figure [name]

Generate a specific figure by name from the figure specification, with human review loop.

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
3. **Check tool availability** -- Verify the generation method tools are available (Mermaid CLI, Graphviz, Python, Nano Banana)
4. **Generate draft** -- Dispatch to `sbir-formatter` agent to generate using the specified method
5. **Present for review** -- Human checkpoint with four options:
   - **approve** -- Update figure log, move figure to `./artifacts/wave-5-visuals/` as approved
   - **revise** -- Accept feedback notes, regenerate incorporating changes, re-present
   - **regenerate** -- Switch to a different generation method, produce new draft, re-present
   - **defer** -- Write external brief to `./artifacts/wave-5-visuals/external-briefs/{name}-brief.md`

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `[name]` | Yes | Figure name from figure plan (matches `figure-specs.md` entry) |

## Examples

Generate a specific figure:
```
/proposal draft figure "system-architecture"
```

After generation, reviewer sees:
```
Figure: system-architecture (Figure 3)
Method: Mermaid (flowchart TB)
Section: 3.1 Technical Approach
File: ./artifacts/wave-5-visuals/system-architecture.svg

[approve] [revise] [regenerate] [defer]
```

Revise with feedback:
```
> revise: Add cloud infrastructure layer between API gateway and database
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
- `generate_figure(placeholder)` -- Routes by `generation_method` (Mermaid -> SVG, external -> brief)
- `replace_figure(figure_number, new_path)` -- Replaces a figure with a manually created file

Domain models (`visual_asset.py`):
- `FigurePlaceholder` -- Figure slot with `figure_number`, `section_id`, `description`, `figure_type`, `generation_method`
- `GeneratedFigure` -- Produced figure artifact with `figure_number`, `section_id`, `file_path`, `format`
- `ExternalBrief` -- Brief for non-generatable figures with `content_description`, `dimensions`, `resolution`

The formatter agent loads `skills/formatter/visual-asset-generator.md` for generation methodology.
