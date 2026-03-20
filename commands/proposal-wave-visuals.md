---
description: "Initialize Wave 5 visual assets with figure specifications, style analysis, and tool detection"
argument-hint: "- No arguments required"
---

# /proposal wave visuals

Initialize Wave 5 (Visual Assets). Reads the figure plan from the outline, analyzes agency style conventions, checks tool availability, writes figure specifications, and presents a human checkpoint for approval.

## Usage

```
/proposal wave visuals
```

## Prerequisites

- Wave 3 outline completed with figure plan at `./artifacts/wave-3-outline/figure-plan.md`
- Compliance matrix generated (`.sbir/compliance-matrix.md`)

## Flow

1. **Read figure plan** -- Load planned figures from `./artifacts/wave-3-outline/figure-plan.md`
2. **Read compliance matrix** -- Identify FORMAT items and cross-reference targets from `.sbir/compliance-matrix.md`
3. **Check tool availability** -- Detect which generation tools are present:
   - Mermaid CLI (`mmdc`)
   - Graphviz (`dot`)
   - Python matplotlib (`python3`)
   - LaTeX compilers (`pdflatex`, `xelatex`, `lualatex`)
   - Nano Banana (`GEMINI_API_KEY` env var)
4. **Style analysis** -- Match solicitation context (agency, domain, topic area) against the agency-domain style database:
   - Recommend a style profile with palette hex codes, tone, detail level, and avoid list
   - Present recommendation with rationale for human review
   - User can **approve**, **adjust** (modify palette colors, tone, detail level, avoid items), or **skip**
   - If no Nano Banana figures are planned, style analysis is optional -- inform user and offer to proceed without
   - If the agency is not in the style database, recommend the generic professional style
   - Persist approved profile to `./artifacts/wave-5-visuals/style-profile.yaml`
5. **Write figure specifications** -- For each planned figure, produce a specification containing:
   - Figure type (architecture, timeline, data chart, concept illustration)
   - Generation method (matched to available tools)
   - Caption text
   - Cross-references to outline sections and compliance matrix items
6. **Persist specifications** -- Write to `./artifacts/wave-5-visuals/figure-specs.md`
7. **Human checkpoint** -- Present planned figures, style profile, and selected methods for review:
   - **approve** -- Accept figure plan and proceed to generation
   - **revise** -- Adjust specifications based on feedback
   - **skip** -- Record skip and proceed (with PES audit)

## Context Files

- `./artifacts/wave-3-outline/figure-plan.md` -- Source figure plan from writer
- `.sbir/compliance-matrix.md` -- FORMAT items and cross-reference targets
- `skills/formatter/visual-asset-generator.md` -- Loaded by agent for figure type selection and generation methodology
- `skills/formatter/visual-style-intelligence.md` -- Loaded by agent for agency style database, style profiles, and prompt integration

## Agent Invocation

@sbir-formatter

Dispatch to sbir-formatter agent (Phase 1: FIGURE PLAN). The agent loads both the `visual-asset-generator` and `visual-style-intelligence` skills for figure type selection, generation method routing, style analysis, and specification format.

## Examples

With all tools available and DoD solicitation:
```
4 figures planned | mmdc available | dot available | python3 available | GEMINI_API_KEY set
Style analysis: DoD / directed-energy -> "Professional Technical" profile
  Palette: #003366, #336699, #66CCFF, #F5F5F5 | Tone: formal-authoritative
  User: approve
-> Style profile written to ./artifacts/wave-5-visuals/style-profile.yaml
-> 4 specifications written to ./artifacts/wave-5-visuals/figure-specs.md
-> Methods: 2 Mermaid, 1 matplotlib, 1 Nano Banana
-> Awaiting approval
```

No Nano Banana figures planned:
```
3 figures planned | mmdc available | no GEMINI_API_KEY
All figures are diagram/chart type -- no Nano Banana figures planned.
Style analysis is optional. Proceed without style profile? [yes/no]
-> 3 specifications written (2 Mermaid, 1 inline SVG)
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

This command invokes `VisualAssetService.prepare_figure_plan()` (driving port) after checking PES PDC gate via `VisualAssetService.check_pdc_gate()`. The formatter agent reads the figure plan, performs style analysis against the agency-domain style database, detects available tools, and writes figure specifications following the visual-asset-generator and visual-style-intelligence skill methodologies.
