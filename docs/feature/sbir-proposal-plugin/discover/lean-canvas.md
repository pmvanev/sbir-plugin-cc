# Lean Canvas -- SBIR Proposal Writing Plugin

## Canvas

### 1. Problem

Top 3 validated problems (customer words):

1. **"Searching through documents"** -- Engineers spend hours finding relevant past performance, evidence, and boilerplate across scattered files. No semantic search; no organized retrieval.

2. **"Meeting requirements for content, format, length"** -- Manual compliance tracking with checklists is inadequate. Requirements get missed. Disqualification is the penalty.

3. **"AI writes garbage sometimes"** -- Current AI tools produce untrustworthy output with "hallucinatory technical promises." No guardrails, no enforcement, no confidence signals.

### 2. Customer Segments

**Primary:** Small business engineers (5-500 employees) who write SBIR/STTR proposals as part of their job. They are technical professionals doing double duty as proposal writers. They are comfortable with CLI tools and code. They submit 3-8 proposals per year across DoD, NASA, NSF, DOE, and other agencies.

**Segmented by JTBD, not demographics:**
- Job: "Write a winning SBIR proposal faster with less effort"
- Context: Time-pressured, compliance-heavy, competitive, recurring

**Not the target:** Large defense contractors (have dedicated proposal teams). Contracts/BD professionals who prefer GUI tools. Companies that outsource all proposal writing.

### 3. Unique Value Proposition

The only SBIR proposal tool that lives in your engineering environment, learns from every proposal cycle, and enforces compliance as a structural guarantee -- not a checklist.

**High-concept pitch:** "PES for proposals -- what TDD enforcement is to code quality, compliance enforcement is to proposal quality."

### 4. Solution

**Phase C1 (MVP):**
- Corpus librarian: semantic search across past proposals, debriefs, TPOC logs, boilerplate
- Compliance matrix: automated extraction of "shall" statements from solicitations with live tracking
- PES enforcement: structural compliance gates from day one
- Topic intelligence: solicitation scanning and fit scoring (Wave 0)

**Phase C2:**
- Guardrailed AI drafting: section-by-section with confidence flagging and claim verification
- Human checkpoints between waves
- Multi-agent iteration (writer + reviewer + compliance) with PES enforcement
- TPOC question generation and research synthesis

**Phase C3:**
- Visual asset generation
- Document formatting and assembly
- Submission packaging
- Post-submission learning and win/loss analysis

### 5. Channels

1. **Claude Code plugin marketplace** -- direct distribution to existing Claude Code users
2. **SBIR/STTR community** -- SBTC conferences, agency outreach events, SBIR.gov forums
3. **Word of mouth** -- tight-knit small business SBIR community; proposal writers talk to each other
4. **Content marketing** -- SBIR proposal writing best practices content targeting engineers

### 6. Revenue Streams

- **Plugin license:** Per-company annual subscription ($1,500-$3,000/year)
- **Claude API usage:** Pass-through or bundled
- **Benchmark:** Companies currently pay $5-10K per proposal to firms. Annual tool subscription at $2K covers unlimited proposals -- clear value proposition

### 7. Cost Structure

- Development: Claude Code plugin engineering (primary cost)
- Claude API costs per usage (variable, passed to user or absorbed)
- Support and documentation
- No infrastructure hosting -- runs locally on user machines
- No web UI to maintain

### 8. Key Metrics

| Metric | Type | Measurement |
|---|---|---|
| Proposals completed using tool | Adoption | Count per quarter |
| Time saved per proposal | Value delivered | Before/after comparison |
| Compliance items auto-caught | Feature value | Items found by tool vs. manual review |
| Corpus size growth | Engagement | Documents ingested per quarter |
| Win rate delta | Lagging outcome | Compare win rate pre/post adoption |
| H3 validation | Critical early signal | Would users adopt without drafting features? |

### 9. Unfair Advantage

1. **Compounding institutional corpus** -- gets materially better with every proposal cycle. Company-specific knowledge that no SaaS competitor can replicate.
2. **PES enforcement pattern** -- architectural commitment to structural guarantees. Hard to bolt on after the fact.
3. **First mover in quadrant** -- no existing tool combines SBIR-specific depth + CLI-native + institutional memory + enforcement layer.
4. **Builder is user** -- dogfooding from day one eliminates build-wrong risk for Phase C1.
5. **Local-first, company-controlled data** -- no sensitive proposal content leaves the company's machines. Government contractors care about this.

## 4 Big Risks

| Risk | Status | Evidence | Mitigation |
|---|---|---|---|
| **Value** | GREEN | 9 sources confirm pain. $5-10K current spend. Built internal tooling. 100% problem confirmation. | Option C ships proven-value features first |
| **Usability** | YELLOW | Engineers comfortable with CLI. But 10-wave complexity untested. "Micromanagement" concern addressed by PES but unproven. | Test H1-H3 on next real proposal cycle (dogfooding) |
| **Feasibility** | YELLOW | Claude Code plugin arch proven (nWave). PES novel but DES precedent. Corpus search well-understood. Formatting genuinely hard. | Phase C1 technically feasible. Defer formatting to C3 or template-based approach |
| **Viability** | YELLOW | ~5,000 companies submit SBIR annually. $2K/year pricing vs $5-10K/proposal firms. Low infrastructure cost. | Niche market; even 200 customers = $400K ARR. Growth via agency expansion and proposal type expansion |

## Market Size

| Metric | Estimate |
|---|---|
| Annual SBIR/STTR proposals submitted | ~25,000-30,000 |
| Unique submitting companies | ~5,000-6,000 |
| Addressable (tech-savvy, CLI-comfortable) | ~2,000-3,000 |
| Conservative penetration (200 customers) | $400K ARR |
| Moderate penetration (500 customers) | $1M ARR |

## Go/No-Go Decision

### Decision: GO -- with conditions

### Rationale

1. Validated pain (9 sources, 100% confirmation, $5-10K current spend)
2. No direct competitor in the SBIR-specific + CLI-native + corpus + enforcement quadrant
3. Builder is user -- dogfooding eliminates Phase C1 build-wrong risk
4. Architecture validated by user preference for wave-based structure with enforcement
5. Option C de-risks by shipping proven AI capabilities first

### Conditions

1. **Test H3 early:** If corpus search + compliance alone do not drive adoption, accelerate Phase C2 drafting features
2. **Validate H4 before full Wave 3-4:** Prototype one section with confidence flagging before building all agents
3. **Be explicit about formatting boundary:** Orphans/widows/margins may require template approach, not LLM
4. **Track market size:** Measure actual SBIR submission volumes during Wave 0 development

### Spec Implications

The existing 76KB specification (sbir-proposal-plugin.md) remains architecturally valid. Key adjustments from discovery:

1. **Build order changes:** Waves 0-1 + corpus + PES first (Phase C1), then Waves 2-4 (Phase C2), then Waves 5-9 (Phase C3)
2. **PES ships from day one:** Not a later addition. Enforcement is the trust mechanism users need.
3. **Drafting agents need confidence flagging:** H4 hypothesis must be tested. "AI proposes, human validates each claim" pattern.
4. **Formatting may need template approach:** LLM-driven formatting for orphans/widows is acknowledged as hard. Consider LaTeX/Word templates instead.
5. **"Tailor-made not general purpose" is a feature:** The plugin architecture validates this preference. Do not pivot to SaaS.
