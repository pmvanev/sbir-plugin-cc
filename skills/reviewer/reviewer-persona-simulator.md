---
name: reviewer-persona-simulator
description: Government technical evaluator simulation methodology -- scoring rubrics, persona construction, red team review, and debrief-informed weakness detection for SBIR/STTR proposals
---

# Reviewer Persona Simulator

## Government Evaluator Scoring Rubrics

SBIR/STTR proposals are evaluated using one of these rubric types (varies by agency):

### Adjectival Rating Scale (DoD standard)
| Rating | Definition |
|--------|-----------|
| Outstanding | Exceeds requirements, innovative, very high probability of success |
| Good | Meets requirements with some strengths, high probability of success |
| Acceptable | Meets minimum requirements, reasonable probability of success |
| Marginal | Does not clearly meet requirements, low probability of success |
| Unacceptable | Fails to meet requirements, proposal should not be funded |

### Acceptable/Unacceptable (NSF, some NIH)
Binary pass/fail per criterion. All criteria must be Acceptable for funding consideration.

### Numeric Scoring (NIH, some civilian)
1-9 scale per criterion, with overall impact score. Typically: 1-3 exceptional, 4-6 good, 7-9 poor.

## Persona Construction

Build the evaluator persona from solicitation evaluation criteria:

1. **Extract criteria**: Read evaluation criteria section verbatim. Note relative weights if stated.
2. **Identify evaluator expertise**: Government evaluators are typically subject matter experts (GS-13 to GS-15 or equivalent) with 10+ years in the field. They review 15-30 proposals per cycle.
3. **Calibrate skepticism**: Evaluators look for:
   - Unsupported claims (assertions without evidence)
   - Overreliance on future work ("we plan to" vs "we have demonstrated")
   - Vague technical approaches lacking methodology specifics
   - Mismatches between claimed capability and cited past performance
   - Budget items not justified by technical approach
4. **Time pressure**: Each proposal gets 2-4 hours of review. Evaluators skim before reading deeply. First impressions matter -- unclear executive summaries lose evaluators early.

## Section-Level Review (Wave 4)

For each section, simulate evaluator scoring:

1. Read the section against its mapped evaluation criteria
2. Score using the rubric type identified from the solicitation
3. For each criterion, produce:
   - **Score/rating**: The adjectival or numeric score
   - **Strengths**: What the evaluator would highlight positively (quote specific language)
   - **Weaknesses**: What the evaluator would flag (quote specific language)
   - **Questions**: What the evaluator would want clarified
4. Check section against known weakness profile from debrief corpus

### Scorecard Format (Section-Level)
```markdown
## Section Review: {section-name}

**Overall Rating**: {rating}

| Criterion | Weight | Rating | Notes |
|-----------|--------|--------|-------|
| {criterion} | {weight} | {rating} | {strength or weakness} |

### Strengths
- {specific strength with quote from proposal}

### Weaknesses
- {specific weakness with quote from proposal}

### Debrief Pattern Match
- {known weakness from corpus that applies, or "No matches"}
```

## Full Proposal Review (Wave 7)

Comprehensive evaluation simulating a full panel review:

1. **Individual scoring**: Score every evaluation criterion across all volumes
2. **Cross-volume consistency**: Check that technical approach, SOW, management plan, and budget tell the same story
3. **Compliance verification**: Confirm all stated requirements are addressed (defer to compliance matrix)
4. **Discriminator assessment**: Evaluate whether the proposal clearly differentiates from likely competitors
5. **Overall impact**: Would this evaluator recommend funding? Why or why not?

### Scorecard Format (Full Proposal)
```markdown
# Reviewer Persona Simulation -- Full Proposal

**Solicitation**: {topic-id} -- {title}
**Rubric**: {adjectival | acceptable/unacceptable | numeric}
**Overall Recommendation**: {Fund | Do Not Fund}

## Criterion Scores

| Criterion | Weight | Rating | Strengths | Weaknesses |
|-----------|--------|--------|-----------|------------|
| {criterion} | {weight} | {rating} | {summary} | {summary} |

## Cross-Volume Consistency
- {consistency finding or issue}

## Top Strengths (Evaluator Would Highlight)
1. {strength}

## Top Weaknesses (Evaluator Would Flag)
1. {weakness}

## Known Debrief Pattern Matches
- {pattern from weakness profile}

## Funding Recommendation Narrative
{2-3 paragraph evaluator narrative explaining the recommendation}
```

## Red Team Review

The red team identifies the strongest objections a skeptical reviewer could raise. This is adversarial by design -- assume the evaluator is looking for reasons to not fund.

Red team methodology:
1. **Technical feasibility attack**: Where is the approach most likely to fail? What assumptions are untested?
2. **Team credibility attack**: Where is past performance weakest relative to claims? Any gaps in key personnel qualifications?
3. **Commercialization skepticism**: Is the Phase III pathway realistic or aspirational? Is the market evidence credible?
4. **Budget scrutiny**: Do labor hours match the proposed scope? Are any line items unjustified?
5. **Competitive positioning**: Could a competitor make a stronger case on any criterion?

Red team output: 3-5 strongest objections, ranked by severity, each with:
- The objection (stated as the skeptical reviewer would phrase it)
- Evidence from the proposal supporting the objection
- Suggested mitigation (what would address this concern)

## Debrief Weakness Checking

Cross-reference proposal sections against the known weakness profile from win-loss analysis:

1. Load weakness profile from corpus (via win-loss-analyzer skill output)
2. For each weakness pattern with frequency >= 2: check whether current proposal exhibits the same pattern
3. Flag matches with: weakness category, historical frequency, agencies that raised it, and the specific proposal text triggering the match
4. Check for agency-specific patterns if the target agency appears in historical data

## Clarity and Jargon Analysis

### Reading Level
- Target: accessible to a GS-13+ technical evaluator who is an expert in the general domain but may not know your specific technology
- Flag: sentences over 40 words | paragraphs over 150 words without a break | passive voice chains (3+ consecutive passive constructions)

### Acronym Audit
- Every acronym defined on first use in each volume
- Maintain acronym inventory across sections
- Flag: undefined acronyms | acronyms defined but never used | inconsistent definitions

### Cross-Reference Check
- Every cited figure exists and has a caption
- Every section cross-reference points to a real section
- Page number references are valid (if present)
- Table references match actual tables

## Actionable Finding Format

Every finding follows this structure:
```
- **Location**: {volume, section, page/paragraph}
- **Severity**: {critical | major | minor}
- **Finding**: {what the issue is}
- **Suggestion**: {specific action to resolve}
```

Severity definitions:
- **Critical**: Would cause Unacceptable/fail rating on a criterion, or compliance disqualification
- **Major**: Would cause Marginal rating or significant point deduction
- **Minor**: Would not affect rating but reduces proposal polish

## Iteration Protocol

Wave 4 (section-level): Review -> findings to writer -> writer revises -> re-review. Maximum 2 review cycles per section. If issues persist after 2 cycles, escalate to human checkpoint.

Wave 7 (full proposal): Full review -> findings to orchestrator -> team addresses -> re-review. Maximum 2 full review cycles. After 2 cycles, present remaining issues at human checkpoint for sign-off decision.
