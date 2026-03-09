---
name: sbir-strategy-knowledge
description: Core domain knowledge for SBIR/STTR strategy brief generation -- teaming patterns, Phase III pathways, risk frameworks, competitive positioning, TPOC integration, and required brief sections.
---

# SBIR Strategy Domain Knowledge

## Teaming Strategy Patterns

### When Teaming Is Required
- STTR: research institution partnership is mandatory (minimum 30% in Phase I, 40% in Phase II)
- Capability gaps in solicitation requirements not covered by prime
- Past performance requirements the prime cannot meet alone

### Teaming Models
- **Subcontractor**: Task-based, prime retains IP and control
- **Research partner (STTR)**: Joint research, shared IP per agreement
- **Consultant**: Advisory role, limited scope, lower overhead
- **Teaming agreement**: Pre-award arrangement, may convert to sub

### Assessment Checklist
Identify capability gaps from compliance matrix | Match gaps to potential partners | Verify partner size status (affects SBC size calculation) | Check organizational conflict of interest | Confirm partner availability and commitment timeline

## Phase III Transition Pathways

Phase III = commercialization. Two main pathways:

### Government Transition
- Program of record (POR) insertion -- align technology to existing acquisition program
- New requirement -- technology creates capability the agency needs
- Follow-on contract -- direct sole-source from sponsoring agency
- Cross-agency adoption -- other DoD/civilian agencies adopt

### Commercial Transition
- Dual-use technology with commercial market
- Licensing to commercial partner
- Spin-off company formation
- Direct sales to commercial customers

### Strengthening Phase III Narrative
- Name specific programs of record or acquisition milestones
- Cite letters of support or memoranda of understanding
- Reference TAM/SAM/SOM with sources
- Show customer discovery evidence (beyond TPOC)
- Connect to agency strategic plans or technology roadmaps

## Risk Assessment Framework

### Risk Categories for SBIR
1. **Technical**: Can the technology achieve claimed performance?
2. **Schedule**: Can milestones be met within period of performance?
3. **Cost**: Is the budget realistic for proposed scope?
4. **Commercialization**: Is the Phase III pathway credible?
5. **Team**: Does the team have required expertise and availability?

### Risk Matrix Format
| Risk | Likelihood (L/M/H) | Impact (L/M/H) | Mitigation |
|------|--------------------:|----------------:|------------|
| {risk description} | {L/M/H} | {L/M/H} | {mitigation strategy} |

### Common SBIR Risks to Assess
- Key personnel availability conflicts
- Technology performance shortfall at target TRL
- Subcontractor/partner non-performance
- Prototype materials lead time exceeding schedule
- IP/data rights conflicts with teaming partners
- Regulatory or certification delays

## Competitive Positioning

### Discriminator Categories
- **Technical**: Novel approach, unique algorithms, proprietary methods
- **Team**: Key personnel expertise, relevant past performance
- **Organizational**: Facilities, certifications, existing relationships
- **Commercial**: Existing customers, market traction, transition readiness

### Assessment Method
1. Identify evaluation criteria from solicitation
2. Map company strengths to each criterion
3. Identify likely competitors (prior awardees on similar topics)
4. Articulate "why us" for each discriminator
5. Flag weaknesses that need mitigation in proposal narrative

## Required Strategy Brief Sections

Map to domain model `REQUIRED_SECTION_KEYS`:

| Key | Section | Content Focus |
|-----|---------|---------------|
| `technical_approach` | Technical Approach | Innovation summary, approach rationale, connection to solicitation needs |
| `trl` | Technology Readiness Level | Current TRL with evidence, target TRL, gap analysis |
| `teaming` | Teaming Strategy | Capability gaps, partner identification, team structure |
| `phase_iii` | Phase III Pathway | Transition strategy, market analysis, customer evidence |
| `budget` | Budget Strategy | Cost allocation, rate structure, subcontract rationale |
| `risks` | Risk Assessment | Risk matrix with mitigations across all categories |

## TPOC Integration

When TPOC answers are available:
- Adjust TRL assessment based on agency expectations revealed in conversation
- Refine teaming needs based on agency preferences for specific capabilities
- Sharpen Phase III narrative based on agency transition priorities
- Align budget emphasis with TPOC-indicated priorities

When TPOC answers are unavailable:
- Note absence explicitly in brief ("TPOC insights: not available")
- Base all assessments on solicitation text alone
- Flag items where TPOC clarification would materially change strategy
- Recommend specific follow-up questions for user to pursue
