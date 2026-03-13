# Lean Canvas: Solicitation Finder

## 1. Problem (Phase 1 Validated)

| # | Problem | Evidence |
|---|---------|----------|
| P1 | Small businesses spend 2-6 hours per solicitation cycle manually browsing 300-500 SBIR topics | Domain knowledge + competitive landscape confirms universal pain |
| P2 | Keyword-based searching misses relevant topics that use different terminology | Semantic gap between company capabilities language and solicitation language |
| P3 | Hidden eligibility requirements (clearance, STTR, prior Phase I) discovered late waste hours of evaluation effort | Company profile data exists but is not checked against topics until manual review |

**Existing alternatives**: Manual browsing on dodsbirsttr.mil, SBIR.gov keyword search, commercial tools (GovWin $2K/yr, HigherGov $200-800/yr), consultants ($500-1500/cycle), general AI tools (ChatGPT/Perplexity with copy-paste)

## 2. Customer Segments (by JTBD)

| Segment | Job | Frequency | Urgency |
|---------|-----|-----------|---------|
| **Primary**: Solo / small-team SBIR proposal writers (1-25 employees) | Find best-fit topics from 300-500 candidates per cycle | 3x/year (DoD cycles) + continuous (other agencies) | High -- deadline pressure |
| **Secondary**: SBIR consultants who screen topics for multiple clients | Batch-evaluate topics against multiple company profiles | Weekly during open periods | Medium -- professional efficiency |

Primary segment first. The plugin is designed for Phil/Rafael -- technical founders at small businesses.

## 3. Unique Value Proposition

**One-sentence**: Turn a 4-hour manual topic search into a 10-minute scored shortlist matched against your actual company capabilities, certifications, and past performance.

**Key differentiator from commercial tools**: Runs locally within the CLI workflow the user already uses for proposal writing. No separate SaaS subscription. Scoring uses the same five-dimension model that later informs the Go/No-Go decision -- consistent methodology from topic discovery through proposal completion.

**Key differentiator from manual search**: Semantic matching (not just keywords), automatic eligibility screening (clearance, STTR, Phase II prerequisites), and quantitative scoring with per-dimension breakdown.

## 4. Solution (Phase 3 Validated)

| Feature | Addresses | Priority |
|---------|-----------|----------|
| **Batch topic extraction** from BAA PDFs and topic files | P1 -- eliminates manual browsing | Must-have (MVP) |
| **Two-pass matching** (keyword pre-filter + LLM semantic scoring) | P2 -- catches terminology mismatches | Must-have (MVP) |
| **Five-dimension fit scoring** with automatic eligibility screening | P3 -- surfaces disqualifiers immediately | Must-have (MVP) |
| **Ranked shortlist** with Go/Evaluate/No-Go recommendations | P1 -- delivers actionable output | Must-have (MVP) |
| **Topic selection flow** feeding into `/sbir:proposal new` | Workflow integration | Must-have (MVP) |
| Multi-source monitoring (NASA, DoE) | Coverage expansion | Deferred to v2 |
| Automated data fetching from Topics App API | Convenience | Deferred (if API becomes available) |

## 5. Channels (Path to Users)

| Channel | Mechanism | Status |
|---------|-----------|--------|
| **Plugin ecosystem** | Part of sbir-plugin-cc -- installed via `claude plugin install` | Existing -- same distribution as all plugin features |
| **CLI discoverability** | `/sbir:solicitation find` command -- users encounter it in command list | Built into plugin |
| **Workflow integration** | Topic scout suggests running finder when user has no topic selected | Natural prompt from existing agent |

No new channels needed. The solicitation finder is a feature within the existing plugin. Users who have the plugin discover it through the command interface and through agent prompts.

## 6. Revenue Streams

Not applicable -- the SBIR plugin is an open-source tool, not a commercial product. Value is measured in:

| Metric | Target |
|--------|--------|
| Time saved per cycle | 2-5 hours (from 4-6 hours manual to 10-30 minutes automated) |
| Topic coverage | >90% of relevant topics surfaced (vs ~60-70% from manual browse) |
| False negative rate | <10% (missed good-fit topics) |
| Decision confidence | Quantitative scores replace gut feel |

## 7. Cost Structure

| Cost | Type | Estimate |
|------|------|----------|
| Development effort | One-time | 2-3 weeks (extends existing agent + adds command + tests) |
| LLM token usage per run | Per-use | ~100-200K tokens per batch scoring session (included in Claude Code subscription) |
| Maintenance | Ongoing | Low -- BAA format changes rarely; LLM handles format variation |
| Data source monitoring | Ongoing | Low -- dodsbirsttr.mil structure changes infrequently |

## 8. Key Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Topics parsed per run | 50-500 | Count from batch processing |
| Scoring precision | >80% | True positives / all recommended topics |
| Scoring recall | >70% | True positives / all actually-relevant topics |
| Time to ranked shortlist | <10 minutes | End-to-end from command invocation to results display |
| User proceeds to proposal | >50% of runs | At least one topic selected for Go/No-Go evaluation |

## 9. Unfair Advantage

1. **Integrated scoring methodology**: The same five-dimension fit scoring model is used from topic discovery through Go/No-Go through proposal strategy. No other tool provides this continuity.
2. **Company profile leverage**: The detailed company profile (capabilities, certifications, key personnel expertise, past performance, research partners) is already built and validated. Competitors require users to re-enter company data in their system.
3. **LLM semantic understanding**: Claude reads and understands solicitation text -- not just keyword matching. This handles the terminology mismatch problem that keyword-based tools struggle with.
4. **Local operation**: No data leaves the user's machine. Solicitation text and company profile are processed locally. For defense-adjacent small businesses, this matters.

## 4 Big Risks Assessment

### Value Risk: Will users want this?

| Signal | Assessment |
|--------|-----------|
| Problem validated | Strong -- 6/6 confirmation signals |
| Competitive market exists | $200-2000/year tools validate demand |
| Adjacent feature validation | Topic scout scoring is already used and valued |
| Unique angle | Integrated scoring + local operation + CLI workflow |

**Risk level**: LOW. The problem is validated, the market exists, and this solution has clear differentiation.

### Usability Risk: Can users use this?

| Signal | Assessment |
|--------|-----------|
| CLI command pattern | Consistent with existing plugin commands |
| Input model | Same as existing `/sbir:proposal new` -- provide a file |
| Output model | Tabular ranked list is familiar |
| Workflow integration | Feeds directly into existing Go/No-Go flow |

**Risk level**: LOW. The interaction pattern mirrors existing plugin commands. No new UI paradigm.

### Feasibility Risk: Can we build this?

| Signal | Assessment |
|--------|-----------|
| Data access | Assisted download (user provides file) -- no scraping dependency |
| Parsing | Claude reads PDFs/text -- proven capability |
| Scoring model | Five-dimension model already implemented |
| Batch processing | Token budget feasible for 50-100 topics |
| Agent extension | Extends existing sbir-topic-scout -- not a new agent |

**Risk level**: LOW. All major components exist or are straightforward extensions of existing capabilities.

### Viability Risk: Does the business model work?

| Signal | Assessment |
|--------|-----------|
| Development cost | 2-3 weeks -- reasonable for the value delivered |
| Ongoing cost | LLM tokens only -- included in Claude Code subscription |
| Maintenance burden | Low -- LLM handles format variation, no brittle parsers |
| Strategic fit | Core to the SBIR proposal lifecycle -- the most natural next feature |

**Risk level**: LOW. This is the highest-value next feature for the plugin with minimal ongoing cost.

## Gate G4 Evaluation

| Criteria | Target | Actual | Status |
|----------|--------|--------|--------|
| Lean Canvas complete | All 9 sections | All 9 sections filled with validated evidence | PASS |
| Value risk | Green/Yellow | GREEN -- validated problem with competitive market proof | PASS |
| Usability risk | Green/Yellow | GREEN -- mirrors existing command patterns | PASS |
| Feasibility risk | Green/Yellow | GREEN -- extends existing components | PASS |
| Viability risk | Green/Yellow | GREEN -- low cost, high strategic fit | PASS |
| Channel validated | 1+ viable | Plugin ecosystem (existing) | PASS |

### G4 Decision: GO -- Proceed to handoff

All four gates passed. All four big risks are green. The solicitation finder is a validated, feasible, high-value feature that extends the existing plugin architecture with minimal risk.

## Go/No-Go Summary

**Decision: GO**

**Rationale**: The solicitation finder addresses the most painful upstream bottleneck in the SBIR proposal lifecycle -- finding relevant topics. The solution leverages existing infrastructure (company profile, fit scoring model, topic scout agent), requires no external API dependencies (assisted download model), and integrates naturally into the existing CLI workflow. All four big risks are low. Development effort is estimated at 2-3 weeks.

**Key design decisions to carry forward**:
1. Assisted download model -- user provides topic data (BAA PDF, topic files), plugin processes it. No automated scraping.
2. Two-pass matching -- keyword pre-filter + LLM semantic scoring. Manages token budget while maintaining accuracy.
3. Extend sbir-topic-scout agent (not a new agent) -- follows ADR-005.
4. Finder results saved to `.sbir/finder-results.json` for reference and re-use.
5. Topic selection feeds directly into `/sbir:proposal new` flow.
