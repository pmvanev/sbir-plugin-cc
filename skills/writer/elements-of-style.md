---
name: elements-of-style
description: Writing style skill based on Strunk & White's Elements of Style, adapted for SBIR/STTR proposal prose -- active voice, brevity, positive form, parallel construction, with SBIR-specific exceptions documented
---

# Elements of Style -- SBIR Adaptation

This skill is loaded when `writing_style: "elements"` is set in `.sbir/proposal-state.json`. It applies Strunk & White principles to proposal drafting and review, with documented exceptions where SBIR conventions override general prose guidance.

## Core Rules

### 1. Omit Needless Words

Vigorous writing is concise. Every word should tell.

| Instead of | Write |
|-----------|-------|
| "in order to" | "to" |
| "due to the fact that" | "because" |
| "at this point in time" | "now" |
| "is capable of" | "can" |
| "for the purpose of" | "to" |
| "in the event that" | "if" |
| "a large number of" | "many" |
| "has the ability to" | "can" |
| "it is important to note that" | (delete entirely -- just state the point) |
| "the proposed approach will leverage" | "this approach uses" |

**SBIR application**: Evaluators review 15-30 proposals per cycle. Every unnecessary word competes with your technical content for their attention. A 10-page limit with concise prose carries more information than 10 pages of padding.

### 2. Use the Active Voice

The active voice is usually more direct and vigorous than the passive.

| Passive (avoid) | Active (prefer) |
|----------------|-----------------|
| "The signal was processed by the FPGA" | "The FPGA processes the signal" |
| "Tests will be conducted to validate" | "We will test to validate" |
| "It was determined that the approach" | "We determined that the approach" |
| "Data was collected from three sources" | "We collected data from three sources" |

**SBIR exception -- SOW sections**: Statement of Work uses contractual voice by convention: "The contractor shall deliver..." This is active voice with a specific subject (the contractor), not passive. Do not rewrite SOW language to use "we."

**SBIR exception -- evaluation criteria paraphrasing**: When restating solicitation criteria, match the solicitation's voice to signal compliance. If the solicitation says "approaches shall be evaluated," keep that phrasing in the compliance traceability matrix.

### 3. Put Statements in Positive Form

Make definite assertions. Avoid tame, colorless, hesitating, noncommittal language.

| Negative (avoid) | Positive (prefer) |
|-----------------|-------------------|
| "did not succeed" | "failed" |
| "not inexpensive" | "costly" |
| "not unlike" | "similar to" |
| "does not have" | "lacks" |
| "not impossible" | "feasible" |

**SBIR application**: Evaluators notice hedging. "The approach is not without risk" signals uncertainty. "The approach carries two identified risks, both with mitigations" signals competence. State what IS, not what ISN'T.

**Confidence calibration**: Distinguish between honest uncertainty (appropriate) and hedging (weak). "We expect TRL 5 by Month 9" is confident with an implicit uncertainty. "We do not anticipate that it would be impossible to potentially achieve TRL 5" is hedging.

### 4. Use Parallel Construction

Express coordinate ideas in similar form.

| Non-parallel (avoid) | Parallel (prefer) |
|---------------------|-------------------|
| "The system detects threats, tracking of targets, and will classify objects" | "The system detects threats, tracks targets, and classifies objects" |
| "The PI has experience in radar design, has published on signal processing, and machine learning" | "The PI has experience in radar design, signal processing, and machine learning" |

**SBIR application**: Parallel construction matters in:
- Milestone deliverables (each milestone follows the same structure)
- Key personnel qualifications (each bio follows the same pattern)
- Risk tables (each risk row uses the same format)
- Evaluation criteria responses (each criterion addressed with the same depth)

### 5. Keep Related Words Together

The subject of a sentence and its principal verb should not be separated by a phrase or clause that can be transferred to the beginning.

| Separated (avoid) | Together (prefer) |
|-------------------|-------------------|
| "The algorithm, which was developed over three years of DARPA-funded research and refined during two Air Force Phase I awards, reduces latency by 40%." | "Developed over three years of DARPA-funded research and refined during two Phase I awards, the algorithm reduces latency by 40%." |

**SBIR application**: Evaluators skim. If the key claim ("reduces latency by 40%") is buried after a long parenthetical, the evaluator may miss it. Lead with the result, then cite the evidence.

### 6. Use Definite, Specific, Concrete Language

Prefer the specific to the general, the definite to the vague, the concrete to the abstract.

| Vague (avoid) | Specific (prefer) |
|--------------|-------------------|
| "extensive experience" | "12 years designing fiber laser systems" |
| "significant improvement" | "40% reduction in processing latency" |
| "state-of-the-art" | "exceeds current SOTA by 2.3 dB SNR (ref: Smith 2025)" |
| "our team is well-qualified" | "Dr. Chen led AF241-087 Phase I, achieving TRL 4" |
| "large market opportunity" | "$340M addressable market (MarketsandMarkets 2025)" |

**SBIR application**: This is the single most important Strunk & White principle for SBIR proposals. Evaluators discount vague claims. Every assertion earns credibility when backed by specific data from the company profile, past performance, or published research.

## Section-Specific Guidance

### Technical Approach
- Lead each subsection with the claim, then the evidence. Not the other way around.
- Use present tense for established facts, future tense for proposed work.
- One idea per paragraph. Long paragraphs signal muddled thinking.

### Key Personnel
- Name, then qualification, then relevance. Not: "The team includes highly qualified individuals who bring a wealth of experience to this effort."
- Quantify: years, publications, awards, specific contracts.

### Past Performance
- Result first, then context. "Achieved TRL 5 prototype (AF241-087, $150K Phase I, 2025)" not "Under contract AF241-087, which was a Phase I SBIR awarded by the Air Force in 2025 for $150K, we achieved a TRL 5 prototype."

### Commercialization
- Name the customer or market segment. "Autonomous vehicle OEMs (Waymo, Cruise, Aurora)" not "various commercial entities."
- Name the dollar amount. "$340M addressable market" not "significant market opportunity."

### Risk
- State the risk, not the absence of risk. "Schedule risk: FPGA integration may require 2 additional weeks if custom IP cores fail timing closure" not "We do not anticipate major schedule impacts."

## What This Style Does NOT Override

These SBIR conventions take precedence over Elements of Style guidance:

1. **Acronym definitions**: SBIR requires defining acronyms on first use even when the full form is wordy. Do not omit the definition for brevity.
2. **SOW contractual voice**: "The contractor shall..." is the correct register for SOW sections. Do not rewrite to informal active voice.
3. **Compliance traceability language**: When paraphrasing solicitation requirements, match the solicitation's terminology exactly, even if wordy. This signals compliance to evaluators.
4. **Section headers mandated by solicitation**: Use the solicitation's exact section titles, even if they violate style rules.
5. **Agency-specific jargon**: If the solicitation uses specific terms (e.g., "warfighter," "CONOPS," "system-of-systems"), use them. This is the evaluator's language.

## Reviewer Application

When this style is active, the reviewer checks for:
- Passive voice (flag chains of 2+ consecutive passive sentences, not isolated instances)
- Vague claims without quantification (flag with suggestion to add specific data)
- Wordy constructions from the "Instead of / Write" table above
- Non-parallel construction in lists, milestones, and risk tables
- Key claims buried in subordinate clauses

Severity for style findings:
- **Major**: Vague claim where specific data exists in company profile but was not cited
- **Minor**: Wordiness, passive voice, non-parallel construction
- Style findings never override compliance, technical accuracy, or SOW convention findings
