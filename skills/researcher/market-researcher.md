---
name: market-researcher
description: TAM/SAM/SOM sizing methodology, competitor landscape analysis, commercialization pathway mapping, and customer discovery for SBIR/STTR proposals.
---

# Market Research Methodology for SBIR/STTR

## TAM / SAM / SOM Sizing

### Bottom-Up Approach (Preferred)

Top-down sizing ("the global defense market is $800B, we target 0.01%") is unconvincing to evaluators. Use bottom-up data points:

**TAM (Total Addressable Market):**
- Identify all programs, contracts, and budget lines that could use the technology
- Sources: DoD budget justification documents (PB docs), agency RDT&E budget exhibits, USASpending.gov contract data
- Include: DoD programs + allied nation equivalents + commercial applications if dual-use
- Express as annual contract value, not unit counts alone

**SAM (Serviceable Available Market):**
- Narrow TAM to segments the company can realistically serve
- Filters: geography (domestic vs. export), clearance requirements, contract vehicle access (GSA schedule, IDIQ membership), technology readiness
- For SBIR Phase I: SAM is typically the sponsoring agency's budget for this technology area

**SOM (Serviceable Obtainable Market):**
- Narrow SAM to realistic capture in 3-5 years post-Phase III
- Factors: competitive landscape, incumbent advantage, transition timeline, production capacity
- For SBIR: SOM is typically 1-3 specific contract opportunities or programs of record
- Name the specific programs, not percentages

### Data Sources for Market Sizing

| Source | What It Provides | URL |
|--------|-----------------|-----|
| USASpending.gov | Federal contract awards, amounts, recipients | usaspending.gov |
| FPDS | Federal procurement data, contract actions | fpds.gov |
| DoD Budget Justification | RDT&E spending by program element | comptroller.defense.gov |
| SBIR.gov | Prior SBIR/STTR awards, topics, amounts | sbir.gov |
| SAM.gov | Active solicitations, contract vehicles | sam.gov |
| Agency PEO briefings | Program roadmaps, transition targets | Varies by agency |

### Sizing Red Flags

- TAM stated without identifiable programs or budget lines
- SAM/SOM derived as percentages of TAM rather than named opportunities
- Market size claims from analyst reports without government budget validation
- No distinction between R&D market (SBIR) and production market (Phase III)
- Commercial market claims without regulatory pathway assessment

## Competitor Landscape Analysis

### Identify Competitors From

1. **Prior SBIR awards**: Same topic area, same agency, past 5 years
2. **USASpending.gov**: Companies receiving contracts in the technology domain
3. **Patent holders**: Companies with relevant IP (from patent landscape)
4. **Conference proceedings**: Authors and affiliations in relevant technical conferences
5. **Industry associations**: Member directories in the technology domain

### Competitor Assessment Framework

For each identified competitor, assess:

| Dimension | Question |
|-----------|----------|
| Technical approach | What approach do they use? How does it differ? |
| Maturity | What TRL have they demonstrated? Evidence? |
| Prior awards | How many SBIR/STTR awards on this topic? Phase I only or Phase II/III? |
| Incumbent advantage | Do they have existing relationships with the sponsoring agency? |
| Weaknesses | Where does their approach fall short vs. solicitation requirements? |
| IP position | Do they hold blocking patents? Are they freedom-to-operate risks? |

### Positioning Against Competitors

Frame discriminators relative to competitors, not in a vacuum:
- "Our approach achieves X where CompetitorCo's demonstrated Y" (cite evidence)
- Avoid: "We are the best" without comparative basis
- Identify Blue Ocean opportunities where no competitor operates

## Commercialization Pathway

### DoD Transition Pathway

1. **Identify the Program of Record (POR)**: Which acquisition program would integrate this technology? Name the PEO, PM, and program.
2. **Map the budget line**: Which PE (Program Element) and project number fund this area?
3. **Identify the transition mechanism**: Direct Phase III contract, IDIQ task order, OTA follow-on, or integration into existing program?
4. **Assess transition readiness**: Does the POR have a technology insertion point? What TRL does the PM require for integration?
5. **Timeline**: From Phase II completion to transition -- typically 1-3 years. Map key milestones.

### Commercial Pathway

1. **Identify commercial customers**: Who buys this outside DoD?
2. **Regulatory requirements**: FDA, FCC, FAA, export controls (ITAR/EAR)?
3. **Certification timeline**: How long from prototype to certified product?
4. **Revenue model**: Product sale, SaaS, licensing, integration services?
5. **Market entry strategy**: Direct sales, channel partners, OEM integration?

### Dual-Use Assessment

When technology has both DoD and commercial applications:
- Quantify both markets separately
- Identify which market provides faster revenue
- Assess whether DoD IP restrictions (DFARS 252.227-7014) limit commercial exploitation
- Note SBIR data rights provisions (5-year protection period)

## Customer Discovery Beyond TPOC

### Additional Stakeholders to Identify

| Stakeholder | How to Find | Why They Matter |
|-------------|------------|-----------------|
| Program Manager (PM) | Agency org charts, conference speakers | Controls acquisition budget and transition decisions |
| Requirements Owner | Solicitation POC, JCIDS documents | Defines what "success" looks like operationally |
| End User (Operator) | CONOPS documents, field exercises | Validates operational relevance |
| Other agencies | Cross-agency SBIR topics on same area | Parallel funding opportunities |
| Allied nations | FMS cases, NATO STANAG refs | Export market sizing |
| Integrators | Prime contractor tech scouts | Phase III integration partners |

### Discovery Sources

- SBIR.gov topic search for same keywords across all agencies
- Conference proceedings (NDIA, SPIE, IEEE) for author affiliations
- LinkedIn for people in relevant program offices
- SAM.gov for upcoming solicitations in the domain

## Regulatory and Certification Landscape

Assess regulatory factors that affect time-to-market and cost:

| Factor | Impact | Where to Check |
|--------|--------|---------------|
| ITAR/EAR classification | Limits export, increases compliance cost | USML categories, CCL |
| CUI/NIST 800-171 | Data handling requirements | Solicitation security section |
| Safety certification | Adds 6-24 months to timeline | Domain-specific (DO-178C for avionics, MIL-STD-882 for safety) |
| Spectrum allocation | Required for RF/wireless technologies | FCC, NTIA |
| Environmental compliance | Required for field-deployed systems | EPA, state regs |

Flag any regulatory factor that adds more than 6 months or $100K to the commercialization timeline. These are material risks for Phase III transition.
