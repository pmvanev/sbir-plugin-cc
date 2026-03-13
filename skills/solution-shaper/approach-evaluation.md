---
name: approach-evaluation
description: Domain knowledge for approach-level scoring against SBIR/STTR solicitations -- scoring dimension rubrics with configurable weights, approach generation patterns (forward/reverse/prior-art), commercialization quick-assessment framework, and approach-brief.md artifact schema
---

# Approach Evaluation

## Scoring Dimensions

Five dimensions evaluate each candidate approach against the company's specific capabilities and the solicitation's requirements. Each dimension scores 0.00 to 1.00. The composite is a weighted sum.

### 1. Personnel Alignment (default weight: 0.25)

Maps required expertise for the approach to company profile `key_personnel[].expertise`.

| Score Range | Criteria |
|------------|---------|
| 0.80-1.00 | Named PI/Co-PI with direct expertise. Multiple team members cover approach needs. Published work or patents in the area. |
| 0.50-0.70 | Adjacent expertise -- team has related experience, credible pivot with ramp-up. One named person with partial coverage. |
| 0.20-0.40 | Tangential skills only. Significant expertise gap requiring new hire or teaming partner. |
| 0.00-0.10 | No relevant personnel. Approach requires capabilities the team does not have. |

Scoring guidance:
- Reference specific personnel by name and expertise keywords
- Count the number of key personnel whose expertise overlaps the approach's required capabilities
- Weight PI/Co-PI alignment higher than supporting staff
- Account for teaming partners listed in company profile

### 2. Past Performance (default weight: 0.20)

Maps approach domain to company profile `past_performance[]` entries.

| Score Range | Criteria |
|------------|---------|
| 0.80-1.00 | Direct domain match with successful outcome. Same agency AND same technical domain. Multiple relevant contracts. |
| 0.50-0.70 | Related domain -- same technical area but different agency, or same agency but adjacent domain. One relevant contract. |
| 0.20-0.40 | Tangential past work. One loosely related effort. |
| 0.00-0.10 | No relevant past performance for this approach domain. |

Scoring guidance:
- Reference specific contract IDs or project names from past_performance entries
- Weight agency match alongside domain match (same agency = reviewer familiarity)
- Recency matters -- past performance within 3 years weighted higher
- Outcome matters -- successful completions > ongoing > incomplete

### 3. Technical Readiness (default weight: 0.20)

Estimates the Technology Readiness Level (TRL) starting point for this approach given the company's current IP, prototypes, and lab work.

| Score Range | Criteria |
|------------|---------|
| 0.80-1.00 | TRL 4-5 start. Company has working prototypes, bench demos, or validated models for core elements. Minimal gap to solicitation target. |
| 0.50-0.70 | TRL 2-3 start. Concept validated in lab. Key components demonstrated individually but not integrated. Moderate gap. |
| 0.20-0.40 | TRL 1-2 start. Concept stage only. Significant development needed within Phase I timeline. |
| 0.00-0.10 | Below TRL 1 for this approach. Fundamental research needed before feasibility. |

Scoring guidance:
- Phase I solicitations expect TRL advancement from ~2-3 to ~4-5
- A higher TRL start reduces schedule risk and strengthens feasibility claims
- Account for company IP, existing codebases, simulation tools, and test equipment
- If the solicitation specifies a target TRL, score against the gap

### 4. Solicitation Fit (default weight: 0.20)

How directly the approach addresses the stated objectives and evaluation criteria.

| Score Range | Criteria |
|------------|---------|
| 0.80-1.00 | Directly addresses all stated objectives. Strong alignment with evaluation criteria weighting. No scope stretching needed. |
| 0.50-0.70 | Addresses most objectives directly. Some scope interpretation required. Good but not perfect fit. |
| 0.20-0.40 | Addresses some objectives. Requires framing or stretch to cover full scope. Risk of "nice but not what we asked for." |
| 0.00-0.10 | Tangential to solicitation objectives. Would require significant scope reframing. |

Scoring guidance:
- Map each solicitation objective to the approach's technical elements -- count coverage
- Weight by evaluation criteria percentages (e.g., technical merit 40% matters more than cost 20%)
- Penalize approaches that address objectives partially or require "creative interpretation"
- Bonus for approaches that address unstated but implied needs (shows domain understanding)

### 5. Commercialization Potential (default weight: 0.15)

Quick Phase III pathway assessment. Full market analysis happens in Wave 2 -- this is a screening-level assessment.

| Score Range | Criteria |
|------------|---------|
| 0.80-1.00 | Dual-use with large addressable market. Clear commercial applications beyond defense. Multiple transition pathways. |
| 0.50-0.70 | Government transition to identified programs of record. Strong Phase III pathway through SBIR agency channels. |
| 0.30-0.50 | Narrow military niche. Single transition pathway. Market exists but is small. |
| 0.00-0.20 | Unclear transition pathway. No obvious Phase III customer. Technology is interesting but market is undefined. |

Scoring guidance:
- Identify the primary commercialization pathway: government transition, commercial market, or dual-use
- Name specific programs of record, commercial sectors, or customer categories
- Consider the approach's IP landscape -- freedom to operate, licensing potential
- Dual-use approaches (defense + commercial) score highest due to multiple revenue paths

## Composite Score Calculation

```
composite = (personnel * 0.25) + (past_perf * 0.20) + (tech_readiness * 0.20) + (solicitation_fit * 0.20) + (commercialization * 0.15)
```

Composite range: 0.00 to 1.00.

## Weight Configurability

Defaults above suit most SBIR Phase I solicitations. Adjust when:

| Condition | Adjustment |
|-----------|-----------|
| Solicitation weights commercialization > 25% | Increase commercialization weight, decrease personnel |
| Topic requires niche expertise with few qualified bidders | Increase personnel alignment weight |
| Phase II follow-on (requires Phase I past performance) | Increase past performance weight |
| Solicitation emphasizes prototype demonstration | Increase technical readiness weight |
| Agency is known for "safe" selections | Increase past performance and solicitation fit weights |

Document any weight adjustments and rationale in the approach brief.

## Approach Generation Patterns

### Forward Mapping (Solicitation Needs → Approaches)

Start from the solicitation's stated problem and work forward to solutions:

1. Decompose the solicitation into discrete technical challenges
2. For each challenge, identify known solution categories from the domain
3. Combine solutions across challenges into complete approaches
4. Filter for approaches that are feasible within Phase I scope

Best for: well-defined solicitation objectives with established solution domains.

### Reverse Mapping (Company Strengths → Approaches)

Start from the company's capabilities and work toward the solicitation:

1. Inventory key personnel expertise, IP, prototypes, and test equipment
2. Identify which company strengths map to solicitation needs
3. Construct approaches that maximize leverage of existing capabilities
4. Validate that each approach actually addresses solicitation objectives (not just "what we can do")

Best for: solicitations adjacent to (not squarely in) company expertise. Surfaces non-obvious fits.

### Prior Art Awareness (Domain Knowledge → Approaches)

Draw on the broader technical landscape:

1. Consider established approaches to this class of problem (published literature, prior SBIR awards in the domain)
2. Identify emerging technologies that could apply (recent breakthroughs, adjacent fields)
3. Look for non-obvious combinations (e.g., applying ML to a traditionally physics-based problem)
4. Note approaches competitors are likely to propose (helps with discrimination)

Best for: crowded solicitation topics where differentiation matters.

## Commercialization Quick-Assessment Framework

Screening-level assessment for each approach. Wave 2 does the deep dive.

### Pathway Types

| Pathway | Description | Strength Signal |
|---------|-------------|----------------|
| **Government transition** | Technology transitions to a DoD program of record (POR) via Phase III contract | Named POR, agency roadmap alignment, prior transition from this program |
| **Commercial market** | Technology has direct commercial applications beyond defense | Identifiable customer segment, existing market, revenue model |
| **Dual-use** | Both government and commercial pathways viable | Multiple customer types, adaptable architecture, broad IP value |

### Dual-Use Assessment Criteria

An approach qualifies as dual-use when:
- Core technology has civilian applications (not just "could be used commercially someday")
- Architecture separates defense-specific components from general-purpose components
- IP strategy supports both government rights and commercial licensing
- At least one non-defense customer segment can be named specifically

### Market Relevance Levels

| Level | Criteria |
|-------|---------|
| **High** | Addressable market > $100M. Multiple identified customers. Active commercial interest in the problem domain. |
| **Medium** | Addressable market $10M-$100M. Niche but real customer base. Some commercial activity in adjacent areas. |
| **Low** | Addressable market < $10M or undefined. Highly specialized. No obvious commercial interest. |

## Approach Brief Schema

The approach brief is written to `./artifacts/wave-0-intelligence/approach-brief.md` and consumed by Wave 1+ agents.

```markdown
# Approach Brief: {Topic ID} -- {Topic Title}

## Solicitation Summary
- Agency: {agency name}
- Problem: {1-2 sentence problem statement from solicitation}
- Key objectives: {bulleted list of objectives from solicitation}
- Evaluation criteria: {criteria with weights, e.g., "Technical Merit (40%), ..." }

## Selected Approach
- Name: {descriptive name, 3-5 words}
- Description: {2-3 sentences explaining the technical concept}
- Key technical elements: {bulleted list of core technologies/methods}
- Why this approach: {rationale referencing scoring dimensions and specific company data}

## Approach Scoring Matrix
| Dimension | {Approach A} | {Approach B} | {Approach C} | ... |
|-----------|-------------|-------------|-------------|-----|
| Personnel alignment (0.25) | {score} | {score} | {score} | |
| Past performance (0.20) | {score} | {score} | {score} | |
| Technical readiness (0.20) | {score} | {score} | {score} | |
| Solicitation fit (0.20) | {score} | {score} | {score} | |
| Commercialization (0.15) | {score} | {score} | {score} | |
| **Composite** | **{score}** | **{score}** | **{score}** | |

## Runner-Up
- Name: {approach name}
- Why not selected: {brief rationale citing scoring differences}
- When to reconsider: {specific conditions under which this approach becomes preferred}

## Discrimination Angles
- {discriminator 1}: {how the selected approach differentiates from likely competitor approaches}
- {discriminator 2}: {unique company capability or past performance that competitors lack}
- {discriminator 3}: {technical differentiation from the "obvious" approach}

## Risks and Open Questions
- {risk/question 1}: Validate in {Wave 1|Wave 2} -- {brief description}
- {risk/question 2}: Validate in {Wave 1|Wave 2} -- {brief description}

## Phase III Quick Assessment
- Primary pathway: {government transition | commercial | dual-use}
- Target programs: {specific programs of record, commercial sectors, or customer categories}
- Estimated market relevance: {high | medium | low} -- {1 sentence rationale}

## Revision History
(Populated only on revision. Append-only.)
- {ISO date}: Original selection -- {approach name} (composite: {score})
- {ISO date}: Revised -- {approach name} ({revision rationale})
```

### Schema Rules

- All sections are required on initial generation (revision history may be empty)
- Scoring matrix must include ALL candidate approaches, not just the selected one
- Dimension weights shown in parentheses in the matrix for downstream reference
- Runner-up section required even if gap is large (documents the decision trail)
- Discrimination angles must be approach-specific, not generic company strengths
- Risks assigned to specific waves so downstream agents know to validate them
