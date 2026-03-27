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
4. **Style analysis (guided discussion)** -- Match solicitation context (agency, domain, topic area) against the agency-domain style database:
   - Build a recommended style profile with palette hex codes, tone, detail level, and avoid list
   - **Present recommendation to the user and ask them to choose**: approve, adjust, or skip
   - Do not auto-approve or proceed without user input -- this is an interactive checkpoint
   - If user adjusts: present revised profile and confirm again
   - If no Nano Banana figures are planned, inform user that style analysis is optional and ask whether to proceed without
   - If the agency is not in the style database, recommend the generic professional style and inform user
   - Persist approved profile to `./artifacts/wave-5-visuals/style-profile.yaml`
5. **Method selection (guided discussion)** -- For each planned figure, walk through generation options with the user:
   - Present the recommended method based on figure type and available tools
   - Show alternative methods that are available and what each is best at
   - Specifically ask about **Nano Banana** (AI image generation) for concept figures and illustrations
   - Let the user select the method for each figure -- do not auto-assign without asking
6. **Write figure specifications** -- For each planned figure, produce a specification containing:
   - Figure type (architecture, timeline, data chart, concept illustration)
   - Generation method (user-selected from step 5)
   - Caption text
   - Cross-references to outline sections and compliance matrix items
7. **Persist specifications** -- Write to `./artifacts/wave-5-visuals/figure-specs.md`
8. **Human checkpoint** -- Present complete figure plan with style profile and methods for explicit approval:
   - **approve** -- Accept figure plan and proceed to generation
   - **revise** -- User provides feedback, loop back to adjust specific figures or methods
   - **skip** -- Record skip and proceed (with PES audit)
   - Do not proceed to figure generation until user explicitly approves

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
