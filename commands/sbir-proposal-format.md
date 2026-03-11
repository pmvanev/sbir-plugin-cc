# /proposal format

Format the drafted proposal to solicitation specifications and assemble submission-ready volumes.

## Usage

```
/proposal format                # Run full formatting and assembly pipeline
/proposal format approve        # Approve formatted document and unlock Wave 7
/proposal format revise         # Revise with feedback
```

## Prerequisites

- Wave 5 complete (all figures approved or deferred to external briefs)
- Wave 4 complete (all sections drafted)
- Compliance matrix generated with FORMAT items populated

## Flow

1. **Read compliance matrix FORMAT items** -- Extract font, margins, headers/footers, page numbering, and file naming requirements
2. **Load agency format template** -- Select template from `templates/format-rules/` based on agency (DoD, NASA, NSF, DOE) and solicitation type
3. **Apply formatting** -- Font family and size, margins, line spacing, headers/footers, page numbering, section heading styles
4. **Insert finalized figures** -- Place approved figures at positions specified in the outline; verify every cross-reference resolves
5. **Format references** -- Apply consistent citation style throughout
6. **Run jargon audit** -- Flag undefined acronyms across the assembled document
7. **Verify page counts** -- Check each volume against solicitation page limits
8. **Assemble volumes** -- Build required file structure per agency into `./artifacts/wave-6-formatted/`
9. **Run compliance final check** -- Verify every compliance matrix item is covered or waived
10. **Present checkpoint** -- Human review of formatted document: approve | revise

## Agent

Dispatches to `sbir-formatter` (Wave 6: Phase 3 FORMAT and Phase 4 ASSEMBLE).

The agent loads these skills during execution:
- `skills/formatter/visual-asset-generator.md` -- figure positioning and cross-reference verification
- `skills/compliance-sheriff/compliance-domain.md` -- FORMAT requirement extraction and final compliance check

## Context Files

- `.sbir/compliance-matrix.md` -- FORMAT items and full compliance status
- `./artifacts/wave-3-outline/figure-plan.md` -- figure positions and cross-references
- `./artifacts/wave-5-visuals/figure-log.md` -- approved figures and external briefs
- `./artifacts/wave-4-draft/` -- drafted proposal sections
- `templates/format-rules/{agency}.json` -- agency-specific formatting rules

## Output

Formatted and assembled package:
```
artifacts/wave-6-formatted/
  volume-1-technical.md
  volume-2-cost.md
  volume-3-company.md
  assembly-report.md
```

Assembly report includes: formatting rules applied, figures inserted, jargon audit results, page counts per volume, compliance final check summary.

## Examples

Within page limits:
```
Formatting complete -- 3 volumes assembled
Technical: 23/25 pages (2 pages margin)
Cost: 8/10 pages (2 pages margin)
Compliance: 47/47 covered | 2 waived | 0 missing
```

Over page limit:
```
Technical volume: 27/25 pages -- OVER LIMIT by 2 pages
Largest sections: Technical Approach (8 pages), Risk Mitigation (6 pages)
Recommend: condense largest sections, resize figures, or cut content
```

Missing compliance items:
```
Compliance final check: 44/47 covered | 2 waived | 1 missing
Missing: R-12 "Phase III commercialization plan"
Provide content for missing items or waive with justification before proceeding.
```

## Implementation

This command dispatches to the `sbir-formatter` agent which orchestrates:
- `FormattingService.load_format_template()` -- loads agency-specific rules from `templates/format-rules/`
- `FormattingService.insert_figures()` -- inserts approved figures at outline-specified positions
- `FormattingService.run_jargon_audit()` -- flags undefined acronyms with locations
- `FormattingService.report_page_count()` -- verifies page counts against solicitation limits
- `AssemblyService.run_final_compliance_check()` -- validates all matrix items before assembly
- `AssemblyService.assemble_volumes()` -- builds volume file structure per agency template

The checkpoint decision is recorded in proposal state. Approval unlocks Wave 7 (review).
