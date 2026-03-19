# JTBD Analysis: Partnership Management

## Discovery Source

Grounded in validated discovery artifacts:
- `docs/feature/partnership-management/discover/problem-validation.md` (10-question deep interview, 2 rounds)
- `docs/feature/partnership-management/discover/opportunity-tree.md` (5 opportunities scored)
- `docs/feature/partnership-management/discover/lean-canvas.md` (risk assessment)

## Job Classification

**Primary job type**: Brownfield improvement (Job 2 from ODI framework).
The SBIR plugin exists with established agents. Partnership management extends existing agents and adds new ones. The user understands the problem domain and can articulate what "done" looks like (Q10 commitment signal).

**Workflow sequence**: `[research] -> discuss -> design -> distill -> baseline -> roadmap -> split -> execute -> review`

Discovery phases (discuss) are warranted because this is a new capability area with cross-cutting integration points across 6 existing agents, even though the system is understood.

---

## Job Stories

### JS-1: Repeat Partner Proposal Content

**When** I am starting a partnered proposal with CU Boulder (a university I have worked with on 3 prior proposals),
**I want to** have the plugin generate partnership-aware suggestions using what it already knows about both entities,
**so I can** produce a stronger teaming section, work-split, and complementarity narrative without manually re-explaining the partnership to every agent.

#### Functional Job
Generate proposal content (teaming plan, work-split, capability complementarity) that reflects both the company profile and the partner profile.

#### Emotional Job
Feel confident that the plugin "understands" the partnership -- that suggestions reflect the actual combined strengths rather than generic teaming boilerplate.

#### Social Job
Present a proposal that demonstrates deep, credible partnership to the evaluator -- not a superficial letter-of-support arrangement.

#### Forces Analysis
- **Push**: Currently every agent (strategist, writer, solution shaper) produces teaming content that is generic because partner capabilities are opaque -- just a name in a flat `string[]`. Phil manually injects partner specifics into every section.
- **Pull**: Rich partner profiles enable AI-assisted suggestions "on the two entities in isolation and as a partnered pair" (Q10). The plugin could generate work-splits, capability matrices, and complementarity narratives automatically.
- **Anxiety**: Will the partner profile be too burdensome to create? Will the suggestions actually be good enough to use, or will they need so much editing that it is faster to write from scratch?
- **Habit**: Phil currently writes teaming sections manually by pulling from memory and past proposals. This works adequately for repeat partners (Q9: no re-collection needed).

#### Assessment
- Switch likelihood: **High** -- Push + Pull clearly exceed Anxiety + Habit. The user explicitly committed (Q10: "worth it").
- Key blocker: Suggestion quality -- if AI suggestions require heavy editing, the habit of manual writing wins.
- Key enabler: Partner profile parity with company profile -- same depth, same schema pattern.
- Design implication: Partner profile must be as rich as company profile. Suggestions must demonstrate they USE the partner data (traceability).

---

### JS-2: New Partner Onboarding with Early Screening

**When** I am evaluating a potential new research institution partner (like SWRI, currently in-flight) for an upcoming STTR proposal,
**I want to** quickly assess their commitment, bandwidth, and capability fit before investing weeks in meetings and facility tours,
**so I can** avoid the catastrophic waste of effort that happened when a partner backed out after extensive engagement (Q8 failure case).

#### Functional Job
Evaluate a new partner's fit and commitment level using structured criteria before heavy investment.

#### Emotional Job
Feel protected against wasted effort. Know early whether this partnership has legs, rather than discovering problems after weeks of meetings.

#### Social Job
Demonstrate to the partner (and internally) that the partnership evaluation is structured and professional -- not ad hoc.

#### Forces Analysis
- **Push**: A research institution backed out after multiple meetings and a facility tour (Q8). The current process has no structured screening -- commitment/fit discovered too late.
- **Pull**: A readiness checklist and fit scoring would surface red flags (bandwidth, timeline, eligibility) before the user invests 14 calendar days in information exchange.
- **Anxiety**: What if the screening is too aggressive and scares away a viable partner? What if the checklist is too rigid for the messy reality of academic partnerships?
- **Habit**: Phil currently evaluates partners informally through conversations. The informal approach feels natural and relationship-preserving.

#### Assessment
- Switch likelihood: **Medium-High** -- Strong push (failure case) and clear pull, but anxiety about over-formalizing is real.
- Key blocker: Screening must feel like due diligence, not an interrogation.
- Key enabler: The Q8 failure case -- concrete, emotionally charged evidence that the current approach fails.
- Design implication: Screening should be lightweight and conversational, not a gating checklist. Frame as "readiness assessment" not "partner qualification."

---

### JS-3: Partner-Aware Topic Scoring

**When** I am scanning SBIR/STTR solicitations with `/solicitation-find` and I have partner profiles on file,
**I want to** see how a topic scores for the partnership (not just for my company alone),
**so I can** identify topics where the combined team has a strong fit even if my company alone would score lower.

#### Functional Job
Score solicitation topics against the combined capability set of company + partner(s).

#### Emotional Job
Feel that no good-fit topics slip through the cracks because the scoring only considers half the team.

#### Social Job
N/A -- scoring is an internal decision tool.

#### Forces Analysis
- **Push**: Current topic scoring has a binary STTR dimension (has partner or not, 0.10 weight). It does not factor partner capabilities into SME or past performance dimensions. A strong partner could elevate a marginal topic to a go.
- **Pull**: Combined scoring would surface partnership-specific opportunities. STTR topics that look marginal for the company alone might be strong for the pair.
- **Anxiety**: Will combined scoring conflate the company's actual capabilities with the partner's? Could it make a weak company position look artificially strong?
- **Habit**: Phil currently mentally adjusts scores knowing "CU Boulder covers the RF side." This mental adjustment works but is informal and not captured.

#### Assessment
- Switch likelihood: **Medium** -- Moderate push (it works informally), strong pull for STTR topics specifically.
- Key blocker: Scoring transparency -- the user must see separate and combined scores, not just a blended number.
- Key enabler: Partner profiles already containing capabilities keywords (same schema as company profile).
- Design implication: Show company-only score AND partnership score side by side. Never hide the components.

---

### JS-4: Partner Coordination Acceleration

**When** I am in the 14-day information exchange cycle with a partner, gathering SOW details, budget breakdowns, and technical scope,
**I want to** have pre-structured templates generated from the topic requirements and partner profile,
**so I can** reduce the back-and-forth exchanges and compress the coordination timeline.

#### Functional Job
Generate structured coordination artifacts (SOW template, budget template, technical scope outline) pre-populated from topic requirements and partner data.

#### Emotional Job
Feel that the plugin is actively reducing the "waiting" burden (Q4: hardest part) rather than just storing information passively.

#### Social Job
Present professional, structured requests to the partner that make coordination easier on their end too.

#### Forces Analysis
- **Push**: 14 calendar days, 2-3 exchanges per partner coordination cycle (Q6). Waiting on SOW/budget info is the hardest part (Q4).
- **Pull**: Pre-structured templates reduce ambiguity in what is needed, enabling the partner to respond more completely in fewer exchanges.
- **Anxiety**: Will templates feel too rigid? Academic partners operate differently from defense contractors -- one-size-fits-all templates might not fit.
- **Habit**: Currently Phil just asks partners directly (Q5: "we tended just to ask them"). This is simple and flexible.

#### Assessment
- Switch likelihood: **Medium** -- The pain is real and quantified, but the current workaround is simple enough.
- Key blocker: Template flexibility -- must be starting points, not rigid forms.
- Key enabler: Templates generated from actual topic requirements (not generic) would be immediately useful.
- Design implication: Frame as "starting point" not "form to fill out." Templates should be editable markdown, not rigid schemas.

---

## Opportunity-to-Job Mapping

| Opportunity (from OST) | Score | Primary Job Story | Secondary |
|------------------------|-------|-------------------|-----------|
| O1: AI-assisted partner-proposal suggestions | 15 | JS-1 (Repeat Partner Content) | JS-3 (Partner-Aware Scoring) |
| O2: Partner coordination acceleration | 14 | JS-4 (Coordination Acceleration) | -- |
| O3: New partner commitment screening | 13 | JS-2 (New Partner Onboarding) | -- |
| O4: Partner profile repository (enabler) | 9 | JS-1 (prerequisite) | JS-2, JS-3 |
| O5: Partner discovery/matching | 8 | -- (deferred) | -- |

## Outcome Statements (Scored)

Derived from job map steps and interview evidence. Scores use single-user estimates (noted as such).

| # | Outcome Statement | Imp. | Sat. | Score | Job |
|---|-------------------|------|------|-------|-----|
| 1 | Minimize the time to produce partnership-aware proposal sections | 9 | 3 | 15 | JS-1 |
| 2 | Minimize the likelihood of a partner backing out after heavy investment | 8 | 2 | 14 | JS-2 |
| 3 | Minimize the elapsed time for partner information exchange | 9 | 4 | 14 | JS-4 |
| 4 | Maximize the likelihood that topic scoring reflects combined team fit | 7 | 3 | 11 | JS-3 |
| 5 | Minimize the time to create a partner profile for AI consumption | 7 | 3 | 11 | JS-1/JS-2 |
| 6 | Minimize the likelihood of missing partner-fit topics during scanning | 6 | 3 | 9 | JS-3 |
| 7 | Minimize the number of exchanges needed to align SOW/budget with partner | 8 | 5 | 11 | JS-4 |

### Data Quality Notes
- Source: single user (plugin author) deep interview, 2 rounds
- Confidence: Medium (single source, but high evidence density with past behavior data)
- All scores should be treated as directional rankings, not absolute

## Priority Ranking

| Priority | Job Story | Rationale |
|----------|-----------|-----------|
| 1 | JS-1: Repeat Partner Content | Highest opportunity score (15). Strongest commitment signal (Q10). Enables the core value proposition shift: from storage to AI suggestions. |
| 2 | JS-2: New Partner Onboarding | Second-highest score (14). Addresses catastrophic failure case (Q8). Low frequency (new partners rare) but high impact. |
| 3 | JS-3: Partner-Aware Scoring | Moderate score (11). Natural extension of existing fit scoring. Lower urgency -- mental adjustment works today. |
| 4 | JS-4: Coordination Acceleration | Good score (14) but highest habit resistance. Simple workaround exists ("just ask"). Templates are a nice-to-have. |

**Note**: O4 (Partner Profile Repository) is not a job -- it is an enabler. It must exist for JS-1, JS-2, and JS-3 to function. It appears as a prerequisite story, not a standalone priority.

## Four Forces Summary (Feature-Level)

### Demand-Generating
- **Push**: Partner capabilities are opaque to the plugin (every agent produces generic teaming content). New partner onboarding can fail catastrophically (Q8). 14-day coordination cycles (Q6).
- **Pull**: "Make suggestions based on the two entities in isolation and as a partnered pair" (Q10). Combined scoring surfaces hidden opportunities. Structured screening prevents wasted effort.

### Demand-Reducing
- **Anxiety**: Partner profile creation burden. Will AI suggestions actually be usable? Will screening scare off partners?
- **Habit**: Manual teaming sections work for repeat partners (Q9). "We just ask them" (Q5). Mental score adjustment works informally.

### Assessment
- Switch likelihood: **High** overall -- user explicitly committed (Q10: "worth it")
- Key blocker: Partner profile must not feel like busywork -- must demonstrably produce better suggestions
- Key enabler: Mirroring company profile pattern (familiar UX, proven architecture)
- Design implication: Build partner profile builder first (familiar pattern), then demonstrate AI suggestion value immediately
