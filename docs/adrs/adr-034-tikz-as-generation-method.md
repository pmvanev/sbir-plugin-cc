# ADR-034: TikZ as a Generation Method with Compilation Verification

## Status

Accepted

## Context

LaTeX proposals embed figures as raster PNGs or external SVGs that don't match the document's typography. TikZ/PGF produces native vector graphics compiled by the same LaTeX engine, matching fonts and scaling infinitely. The question is how to integrate TikZ into the existing generation pipeline.

## Decision

Add "tikz" as a `generation_method` value in `FigurePlaceholder`. The formatter agent generates TikZ code via LLM reasoning, compiles it via the detected LaTeX compiler (subprocess), verifies 0 errors, and saves both `.tex` source and `.pdf` preview.

TikZ is offered only when all conditions are met:
1. Proposal output format is "latex"
2. A LaTeX compiler is detected (pdflatex, xelatex, or lualatex)
3. Figure type is diagram-compatible (system-diagram, block-diagram, process-flow, comparison)

On compilation failure: show error with line number, offer edit/SVG-fallback/defer.

## Alternatives Considered

### Alternative 1: TikZ generation as a separate external tool script
- **What**: A shell script `scripts/tikz-generate.sh` that wraps TikZ compilation, similar to `nano-banana-generate.sh`.
- **Expected impact**: Consistent with Nano Banana integration pattern.
- **Why rejected**: TikZ code generation is fundamentally different from API calls. The agent generates the TikZ code itself (via LLM). The only external tool needed is the compiler. A thin shell script adds indirection without value. The agent can invoke the compiler directly via Bash tool.

### Alternative 2: Convert all diagrams to TikZ (not just offer as option)
- **What**: Default to TikZ for all diagram-type figures in LaTeX proposals.
- **Expected impact**: Maximum visual consistency in LaTeX documents.
- **Why rejected**: TikZ compilation failures are harder to debug than SVG/Mermaid issues. Risk of blocking Wave 5 progress. Users should choose TikZ when the visual quality benefit justifies the compilation risk. Keep it as an option alongside existing methods.

### Alternative 3: PGFPlots only (subset of TikZ)
- **What**: Limit to PGFPlots for data charts only, not full TikZ for diagrams.
- **Expected impact**: Lower compilation failure risk (PGFPlots is well-constrained).
- **Why rejected**: The primary value of TikZ is for technical diagrams (block diagrams, architectures) where the font/scaling mismatch is most visible. PGFPlots alone addresses only data charts, which are a minority of proposal figures.

## Consequences

- **Positive**: LaTeX proposals get native vector figures matching document typography.
- **Positive**: Both .tex source and .pdf preview saved -- user can manually edit TikZ if needed.
- **Positive**: Same critique loop applies (via PDF preview) -- consistent workflow.
- **Negative**: TikZ compilation may fail. Mitigated by: error display with line numbers, SVG fallback, and offering TikZ only for compatible figure types.
- **Negative**: Adds complexity to `VisualAssetService` routing. Minimal: one new method paralleling existing patterns.
