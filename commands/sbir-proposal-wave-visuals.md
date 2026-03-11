# /proposal wave visuals

Initialize Wave 5 (Visual Assets). Reads the figure plan from the outline, checks tool availability, writes figure specifications, and presents a human checkpoint for approval.

## Usage

```
/proposal wave visuals
```

## Prerequisites

- Wave 3 outline completed with figure plan at `./artifacts/wave-3-outline/figure-plan.md`
- Compliance matrix generated (`.sbir/compliance-matrix.md`)

## Flow

1. **Read figure plan** -- Load planned figures from `./artifacts/wave-3-outline/figure-plan.md`
2. **Check tool availability** -- Detect which generation tools are present:
   - Mermaid CLI (`mmdc`)
   - Graphviz (`dot`)
   - Python matplotlib (`python3`)
   - Nano Banana (`GEMINI_API_KEY` env var)
3. **Write figure specifications** -- For each planned figure, produce a specification containing:
   - Figure type (architecture, timeline, data chart, concept illustration)
   - Generation method (matched to available tools)
   - Caption text
   - Cross-references to outline sections and compliance matrix items
4. **Persist specifications** -- Write to `./artifacts/wave-5-visuals/figure-specs.md`
5. **Human checkpoint** -- Present planned figures and selected methods for review:
   - **approve** -- Accept figure plan and proceed to generation
   - **revise** -- Adjust specifications based on feedback
   - **skip** -- Record skip and proceed (with PES audit)

## Context Files

- `./artifacts/wave-3-outline/figure-plan.md` -- Source figure plan from writer
- `.sbir/compliance-matrix.md` -- FORMAT items and cross-reference targets
- `skills/formatter/visual-asset-generator.md` -- Loaded by agent for methodology

## Agent

Dispatches to **sbir-formatter** agent (Phase 1: FIGURE PLAN).

The agent loads the `visual-asset-generator` skill for figure type selection, generation method routing, and specification format.

## Examples

With all tools available:
```
4 figures planned | mmdc available | dot available | python3 available | GEMINI_API_KEY set
-> 4 specifications written to ./artifacts/wave-5-visuals/figure-specs.md
-> Methods: 2 Mermaid, 1 matplotlib, 1 Nano Banana
-> Awaiting approval
```

No external tools:
```
3 figures planned | no tools detected
-> 3 specifications written (all fallback to inline SVG or external brief)
-> Awaiting approval
```

Figure plan missing:
```
Figure plan not found at ./artifacts/wave-3-outline/figure-plan.md
Run /proposal wave outline to generate the outline with figure plan first.
```

## Implementation

This command invokes `VisualAssetService.prepare_figure_plan()` (driving port) after checking PES PDC gate via `VisualAssetService.check_pdc_gate()`. The formatter agent reads the figure plan, detects available tools, and writes figure specifications following the visual-asset-generator skill methodology.
