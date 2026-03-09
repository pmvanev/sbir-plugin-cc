---
name: discrimination-table
description: Domain knowledge for building and iterating the discrimination table -- the three-dimension competitive positioning framework that forms the narrative spine of every SBIR/STTR proposal.
---

# Discrimination Table

## Purpose

The discrimination table is the "why us / why this approach" argument distilled into a structured comparison. It is built in Wave 3 and referenced by every section drafted in Wave 4. Reviewers score proposals on differentiation -- the discrimination table ensures every draft paragraph reinforces at least one discriminator.

## Three Dimensions

### Dimension 1: Company vs. Competitors

Compare the proposing company against likely competitors on the evaluation criteria.

| Factor | Our Company | Likely Competitor A | Likely Competitor B |
|--------|-------------|--------------------|--------------------|
| Past performance | {specific awards, outcomes} | {known competitor history} | {known competitor history} |
| Certifications | {relevant certs, clearances} | {estimated} | {estimated} |
| Facilities | {specific capabilities} | {estimated} | {estimated} |
| Key relationships | {agency relationships, partners} | {estimated} | {estimated} |

**Sources**: Company profile (`~/.sbir/company-profile.json`), corpus past performance records, USASpending/SBIR.gov prior award data from Wave 2 research.

**Competitor identification**: Use prior award data for the same agency/topic area. If no prior awardees are known, identify competitors by capability category and note the analysis as estimated.

### Dimension 2: Technical Approach vs. Prior Art

Compare the proposed technical approach against known prior art and previously attempted solutions.

| Factor | Our Approach | Prior Art / Failed Approaches |
|--------|-------------|-------------------------------|
| Innovation | {what is novel} | {what has been tried} |
| Performance | {expected metrics} | {known limitations} |
| Feasibility | {TRL evidence, preliminary data} | {where prior attempts failed} |
| Cost/schedule | {resource efficiency} | {known cost/schedule issues} |

**Sources**: Wave 2 technical landscape research, TPOC insights about failed prior approaches, solicitation description of problem space.

**TPOC integration**: TPOC calls frequently reveal why prior approaches failed. These insights are high-value discriminators. Frame each technical discriminator as addressing a known gap or failure point.

### Dimension 3: Team Discriminators

Compare team qualifications against solicitation requirements and likely competitor teams.

| Factor | Our Team | Requirement | Discriminator |
|--------|----------|-------------|---------------|
| PI/PD qualifications | {specific credentials, publications} | {from solicitation} | {why this person is uniquely qualified} |
| Key personnel | {relevant experience per person} | {from solicitation} | {specific past work on related problems} |
| Facilities | {specific equipment, labs, clearances} | {from solicitation} | {capability competitors lack} |
| Past performance | {specific contract outcomes} | {from evaluation criteria} | {quantitative results} |

**Sources**: Company profile key personnel section, past performance write-ups from corpus, solicitation evaluation criteria.

## Construction Process

1. **Gather inputs**: Read strategy brief (competitive positioning section), compliance matrix (evaluation criteria), company profile, TPOC Q&A, Wave 2 research artifacts
2. **Identify evaluation criteria**: Extract how reviewers will score -- this determines which discriminators matter
3. **Map strengths to criteria**: For each evaluation criterion, identify which company strength addresses it
4. **Identify gaps**: Where company has no clear discriminator, flag as a weakness to mitigate in the narrative
5. **Incorporate TPOC insights**: If TPOC revealed failed approaches, agency preferences, or scoring priorities, use these to sharpen discriminator framing
6. **Draft the three tables**: Company vs. competitors, approach vs. prior art, team discriminators
7. **Cross-reference compliance matrix**: Every discriminator should map to at least one compliance item

## Quality Criteria

A complete discrimination table:
- Covers all three dimensions with specific, evidence-backed entries
- Maps every major evaluation criterion to at least one discriminator
- Uses quantitative evidence where possible ("3 prior awards" not "extensive experience")
- Identifies at least one gap or weakness with a mitigation strategy
- Integrates TPOC insights when available (or notes their absence)
- Is structured for direct use by the writer agent when drafting sections

## Iteration Patterns

### Common Feedback and Response

| Feedback | Action |
|----------|--------|
| "Competitor analysis too speculative" | Replace estimates with prior award data or note "insufficient data -- recommend /proposal wave research for competitor analysis" |
| "Discriminators too generic" | Replace general claims with specific evidence from company profile or corpus |
| "Missing a key differentiator" | Add the discriminator to the appropriate dimension, cite source |
| "Technical approach comparison weak" | Pull additional prior art from Wave 2 research, TPOC insights, or corpus |
| "Team section focuses on credentials, not relevance" | Reframe each person's entry around how their specific experience applies to this topic |

### When TPOC Data Is Unavailable

- Build discrimination table from solicitation text, company profile, and corpus alone
- Note "TPOC insights: not available" in each dimension where TPOC data would strengthen the analysis
- Flag specific discriminators that are weaker without TPOC validation
- The table is still complete and actionable -- TPOC data sharpens but does not enable

## Output Format

Write to `./artifacts/wave-3-outline/discrimination-table.md` with:
- Header: topic ID, agency, date, TPOC availability status
- Three dimension tables as shown above
- Gap analysis section listing identified weaknesses with mitigation plans
- Compliance matrix cross-reference: which compliance items each discriminator addresses
- Version number for iteration tracking (v1, v2, etc.)

## Relationship to Downstream Sections

| Wave 4 Section | Discrimination Table Usage |
|----------------|---------------------------|
| Technical approach | Dimension 2 drives the "why this approach" narrative |
| Key personnel | Dimension 3 provides tailored bio framing |
| Past performance | Dimensions 1 and 3 provide specific contract outcomes to cite |
| Facilities | Dimension 3 maps facility capabilities to requirements |
| Management plan | Dimensions 1 and 3 inform team structure rationale |
| Commercialization | Dimension 1 organizational discriminators support transition credibility |
| SOW | Dimension 2 technical approach translates to milestone structure |
