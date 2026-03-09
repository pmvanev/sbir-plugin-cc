---
name: compliance-domain
description: SBIR/STTR compliance domain knowledge -- requirement types, extraction patterns, section mappings, matrix format, and coverage lifecycle
---

# Compliance Domain Knowledge

## Requirement Types

| Type | Source | Detection |
|------|--------|-----------|
| SHALL | Explicit shall-statements in solicitation | "shall", "must", "is required to" |
| FORMAT | Page limits, fonts, margins, submission format | "must use", "shall not exceed", "font", "page limit", "format", "margin", "spacing" |
| IMPLICIT | Evaluation criteria implying requirements | "evaluation criteria", "will be evaluated", "assessed based on", "expected to demonstrate" |
| MANUAL | User-added requirements not found by extraction | Added via `compliance add` command |

## Extraction Priority

Process solicitation text in this order:
1. SHALL statements first (strongest contractual language)
2. FORMAT requirements (compliance gatekeepers -- non-compliance is disqualifying)
3. IMPLICIT requirements from evaluation criteria (often missed, high value)
4. Flag any requirement with ambiguous scope or conflicting language

## Section Mapping

Map extracted requirements to proposal sections using keyword detection:

| Keyword in Requirement | Proposal Section |
|----------------------|-----------------|
| technical, risk, prototype | Technical Volume |
| cost, budget | Cost Volume |
| management, schedule, personnel | Management Volume |
| Explicit "Section N" reference | Section N |
| No keyword match | null (flag for user assignment) |

Unmapped requirements are opportunities -- they need human judgment on placement.

## Coverage Statuses

| Status | Meaning | When to Set |
|--------|---------|-------------|
| NOT_STARTED | No proposal content addresses this requirement | Initial state after extraction |
| PARTIAL | Some content exists but does not fully satisfy | Draft exists but incomplete |
| COVERED | Requirement fully addressed in proposal section | Section review confirms coverage |
| WAIVED | Requirement intentionally not addressed | User explicitly waives with rationale |

## Matrix File Format

The compliance matrix is a markdown file at `.sbir/compliance-matrix.md` with this structure:

```markdown
# Compliance Matrix

**Total items:** {count}
**Coverage:** {covered}/{total} covered | {partial} partial | {not_started} not started

## Warnings

- {warning text}

## Requirements

| ID | Type | Requirement | Section | Status | Ambiguity |
|---:|------|-------------|---------|--------|-----------|
| 1 | shall | The contractor shall... | Technical Volume | not_started | |
| 2 | format | Proposals shall not exceed... | All Sections | not_started | |
| 3 | implicit | Will be evaluated on... | Technical Volume | not_started | Implicit from evaluation criteria -- verify weighting and scope |
```

## Ambiguity Patterns

Flag these as ambiguities when detected:
- Contradictory requirements (two shall-statements that conflict)
- Vague quantifiers ("adequate", "sufficient", "appropriate" without metrics)
- Implicit requirements from evaluation criteria (always flag: "Implicit from evaluation criteria -- verify weighting and scope")
- Cross-references to other documents not provided ("as specified in Attachment J")
- Requirements with multiple interpretations

## Low Extraction Warning

When fewer than 5 requirements are extracted, emit a warning. This typically means:
- Solicitation text is incomplete or truncated
- Requirements are embedded in attachments not yet ingested
- Non-standard solicitation format requires manual review

## Compliance Check Output

The check command produces a coverage summary:

```
{total} items | {covered} covered | {partial} partial | {missing} missing | {waived} waived
```

When no matrix exists, guide the user to generate one first. When the matrix cannot be parsed, suggest verifying the markdown table format.

## Architecture Integration

- `ComplianceService.generate_matrix(text)` -- extracts requirements, builds matrix
- `ComplianceService.add_item(matrix, text)` -- adds manual requirement
- `ComplianceCheckService.check(matrix)` -- returns coverage breakdown
- `TextComplianceAdapter` -- regex-based extraction from solicitation text
- `MarkdownComplianceAdapter` -- reads/writes matrix as markdown file
- Matrix file path: `.sbir/compliance-matrix.md`
