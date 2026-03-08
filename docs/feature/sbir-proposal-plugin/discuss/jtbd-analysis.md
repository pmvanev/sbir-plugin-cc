# JTBD Analysis -- SBIR Proposal Writing Plugin

## Persona: Phil Santos

**Who**: Small business engineer who writes SBIR/STTR proposals as part of his job -- technical professional doing double duty as proposal writer.

**Demographics**:

- Technical proficiency: High -- comfortable with CLI tools, writes code, built an internal AI scrubbing tool
- Proposal frequency: 2-3 proposals per year, 10-15 hours each
- Environment: Claude Code CLI, local file system, no web UI
- Primary motivation: Win more proposals with less effort; stop doing mechanical work that adds no intellectual value

**Social Job**: Be seen as a thorough, credible proposal writer who does not miss things.

**Emotional Job**: Feel confident that the proposal addresses the real requirements and that nothing critical was overlooked.

---

## Job Stories

### J1: Find Relevant Past Work

**When** I am starting a new proposal and need to argue company fit based on previous work,
**I want to** quickly find the most relevant past proposals, debriefs, and past performance evidence,
**so I can** build a credible "why us" argument without spending hours searching through scattered files.

| Dimension | Description |
|-----------|-------------|
| Functional | Retrieve relevant past performance documents by topic similarity |
| Emotional | Feel confident I have not missed relevant evidence buried in old files |
| Social | Demonstrate thorough knowledge of company history to evaluators |

**Forces**:

- **Push**: "Searching through documents" -- 9/9 sources confirm; hours of manual file system search
- **Pull**: Semantic search that surfaces relevant evidence in seconds, improves with each proposal cycle
- **Anxiety**: Will ingesting documents take more time than it saves? Corpus grows slowly at 2-3 proposals/year
- **Habit**: Manual search across file system and email; "at least I know where things are"

**Design Implication**: At 2-3 proposals/year, corpus ingestion must be near-zero effort or the payback period is unacceptable. The tool cannot ask for a weekend of document organizing before it becomes useful.

---

### J2: Track Compliance Without Missing Requirements

**When** I am managing a proposal against a solicitation with dozens of "shall" statements,
**I want to** have every requirement automatically extracted, mapped to sections, and tracked as I draft,
**so I can** avoid disqualification from missing a requirement I did not even know existed.

| Dimension | Description |
|-----------|-------------|
| Functional | Extract and track all solicitation requirements against proposal sections |
| Emotional | Feel safe that nothing critical is missing before submission |
| Social | Be the writer who never gets disqualified on a technicality |

**Forces**:

- **Push**: Manual checklists inadequate; items get missed; disqualification is the penalty
- **Pull**: Automated extraction + live tracking + pre-submission compliance gate
- **Anxiety**: Will the parser miss requirements the human would catch? False sense of security
- **Habit**: Manual checklists and careful re-reading of the solicitation

**Design Implication**: The compliance matrix must be editable. Automated extraction is a starting point; the human adds, removes, and annotates. The tool augments judgment, not replaces it.

---

### J3: Draft Trustworthy Technical Narrative

**When** I am writing the core technical approach section and need AI assistance,
**I want to** get a draft that makes claims my company can actually support, with uncertainty flagged,
**so I can** edit toward a finished product instead of rewriting from scratch and worrying about "hallucinatory promises."

| Dimension | Description |
|-----------|-------------|
| Functional | Produce a draft section that is factually grounded in company evidence |
| Emotional | Feel trust in AI output -- "good enough to edit, not garbage to rewrite" |
| Social | Deliver a narrative that no reviewer will call out as AI-generated or unsubstantiated |

**Forces**:

- **Push**: "AI writes garbage sometimes" -- 8/8 writers confirm; "hallucinatory technical promises"
- **Pull**: Confidence-flagged drafts; AI says "I am uncertain about this claim"
- **Anxiety**: Will guardrails make the AI too conservative? Will it still be faster than writing from scratch?
- **Habit**: Writing from scratch or using AI only for boilerplate

**Design Implication**: At 10-15 hours per proposal, the drafting tool must save at least 2-3 hours per proposal to justify the learning curve. If confidence flagging adds review overhead that offsets time savings, adoption fails.

---

### J4: Understand What the Solicitation Really Wants

**When** I am reading a solicitation that uses vague or ambiguous language about the technical challenge,
**I want to** identify the gaps, generate sharp TPOC questions, and synthesize what I learn,
**so I can** write a proposal that addresses the real need, not just the literal text.

| Dimension | Description |
|-----------|-------------|
| Functional | Parse solicitation for ambiguities; generate TPOC questions; capture and propagate answers |
| Emotional | Feel confident I understand the real problem, not just the stated one |
| Social | Ask intelligent questions that signal competence to the TPOC |

**Forces**:

- **Push**: "Technical challenges not well articulated in solicitations"
- **Pull**: Structured gap analysis + prioritized TPOC question list + delta analysis
- **Anxiety**: Will AI-generated questions reveal strategic intent or signal weakness?
- **Habit**: Reading the solicitation multiple times; relying on domain intuition and TPOC calls

**Design Implication**: TPOC questions must be human-curated before the call. The AI generates candidates; the human selects, rewords, and sequences. The tool must never imply "just ask these."

---

### J5: Argue Competitive Advantage

**When** I need to demonstrate why my company and approach are better than alternatives,
**I want to** build a structured discrimination table from company history, research, and TPOC insights,
**so I can** make a compelling "why us" case that goes beyond generic claims.

| Dimension | Description |
|-----------|-------------|
| Functional | Build evidence-backed discrimination table with company vs. competitor vs. prior art |
| Emotional | Feel that the competitive argument is honest and defensible |
| Social | Present a differentiation story that evaluators find credible, not marketing fluff |

**Forces**:

- **Push**: "Arguing company is better than competitors" -- hard without structured evidence
- **Pull**: Discrimination table builder pulling from corpus, research, and TPOC insights
- **Anxiety**: Will the tool surface weaknesses I would rather not confront?
- **Habit**: Writing differentiators from memory and gut feel

---

### J6: Format and Assemble Without Manual Labor

**When** I have a final draft and need to produce a submission-ready document,
**I want to** automate formatting (margins, headers, figure placement, orphans/widows) and assembly,
**so I can** stop spending hours on mechanical formatting work that adds no intellectual value.

| Dimension | Description |
|-----------|-------------|
| Functional | Produce formatted, submission-compliant documents from draft content |
| Emotional | Feel relieved that formatting is handled, not anxious about missed orphans |
| Social | Submit a polished document that looks professional |

**Forces**:

- **Push**: "Formatting is purely manual" -- orphans, widows, margins, cross-references
- **Pull**: Template-based automated formatting
- **Anxiety**: Will automated formatting introduce errors I do not notice?
- **Habit**: Manual formatting in Word; "at least I control the output"

**Design Implication**: Feasibility is uncertain. This may require template-based approach (LaTeX/Word templates) rather than LLM formatting. Acknowledged in discovery as hard.

---

### J7: Learn from Win/Loss Patterns

**When** I receive a debrief (or get no feedback at all) after a proposal decision,
**I want to** systematically capture what worked and what did not and apply it to the next proposal,
**so I can** improve my win rate over time instead of repeating the same mistakes.

| Dimension | Description |
|-----------|-------------|
| Functional | Parse debrief feedback; map critiques to proposal sections; track patterns |
| Emotional | Feel that every proposal makes the next one better, not just a fresh start |
| Social | Demonstrate institutional learning to leadership and teaming partners |

**Forces**:

- **Push**: "Vague or no feedback" makes improvement hard
- **Pull**: Structured debrief parsing; pattern analysis across proposal cycles
- **Anxiety**: Small corpus (2-3/year) makes pattern detection unreliable for years
- **Habit**: Informal mental notes; "I'll remember for next time"

**Design Implication**: At 2-3 proposals/year, meaningful pattern detection takes 3-5 years. This job has real value but extremely slow payoff. Must be low-effort to feed or it will be abandoned.

---

### J8: Argue Commercializability Beyond the Solicitor

**When** I need to write the commercialization section and demonstrate market potential beyond the sponsoring agency,
**I want to** build a credible TAM/SAM/SOM argument and identify non-obvious commercial applications,
**so I can** score well on commercialization criteria without making claims I cannot defend.

| Dimension | Description |
|-----------|-------------|
| Functional | Research market size; identify commercial applications beyond the SBIR sponsor |
| Emotional | Feel that the commercialization argument is honest, not inflated marketing |
| Social | Present market analysis that evaluators (often technical, not business) find credible |

**Forces**:

- **Push**: "Arguing commercializability beyond the solicitor's problem space" -- engineers struggle with market language
- **Pull**: Structured market research synthesis; TAM/SAM/SOM scaffolding with real data
- **Anxiety**: Will AI-generated market claims be verifiable? Will they sound like MBA boilerplate?
- **Habit**: Writing vague commercialization sections; "it's never the section that wins or loses"

**Design Implication**: Engineers writing for technical evaluators. The commercialization section needs to be credible to a PhD reviewer, not a VC. Different tone than typical market analysis.

---

## Opportunity Scoring

Formula: Score = Importance + Max(0, Importance - Satisfaction)

Importance and Satisfaction rated 1-10 based on discovery evidence (9 sources, product owner first-person experience).

**Data Quality Note**: Ratings are based on discovery interview evidence (9 sources) plus product owner direct experience. Confidence is Medium -- single-company sample with strong behavioral signals.

| # | Job | Imp | Sat | Score | Phase | Priority |
|---|-----|-----|-----|-------|-------|----------|
| J3 | Draft trustworthy technical narrative | 9 | 2 | 16 | C2 | Extremely Underserved |
| J1 | Find relevant past work | 9 | 3 | 15 | C1 | Extremely Underserved |
| J2 | Track compliance without missing requirements | 9 | 4 | 14 | C1 | Underserved |
| J4 | Understand what the solicitation really wants | 8 | 3 | 13 | C1 | Underserved |
| J5 | Argue competitive advantage | 8 | 3 | 13 | C2 | Underserved |
| J8 | Argue commercializability beyond the solicitor | 7 | 2 | 12 | C2 | Underserved |
| J6 | Format and assemble without manual labor | 7 | 2 | 12 | C3 | Underserved |
| J7 | Learn from win/loss patterns | 7 | 2 | 12 | C3 | Underserved |

### Scoring Rationale

**J3 (Score 16)**: Highest importance AND lowest satisfaction. Every proposal requires technical narrative. Current AI tools actively harm trust. But deferred to Phase C2 because the trust problem must be solved with guardrails (PES + confidence flagging), not just better prompts.

**J1 (Score 15)**: Named by all 9 sources. User built an internal tool to partially solve this. At 10-15 hours/proposal, even 30 minutes saved per proposal is meaningful. But slow corpus growth (2-3/year) means the compounding value takes years.

**J2 (Score 14)**: Disqualification risk makes this existentially important. Manual checklists are inadequate. Automated extraction is a proven AI capability (lower technical risk than drafting).

**J4 (Score 13)**: Understanding the real need is foundational -- everything downstream depends on it. TPOC question generation is high-leverage because it happens early and shapes the entire proposal direction.

**J5 (Score 13)**: Competitive positioning is hard without structure. Same score as J4 but deferred to C2 because it depends on having drafting capability to use the discrimination table effectively.

**J8 (Score 12)**: Separate job from J5 -- commercializability is about market potential beyond the sponsor, not head-to-head competitive comparison. Engineers find this section especially painful because it requires market language they are not comfortable with.

**J6 (Score 12)**: Real pain, very low satisfaction, but feasibility is genuinely uncertain. Template approach may work; LLM formatting for orphans/widows is hard.

**J7 (Score 12)**: High long-term value but extremely slow payoff at 2-3 proposals/year. Must be near-zero effort to feed.

---

## Job Map (8-Step Universal)

Mapped to the proposal lifecycle with jobs overlaid:

| Step | Proposal Activity | Primary Job(s) | Phase |
|------|------------------|-----------------|-------|
| 1. Define | Identify solicitation; Go/No-Go decision | J1 (corpus for fit) | C1 |
| 2. Locate | Gather past performance, solicitation, TPOC logs | J1 | C1 |
| 3. Prepare | Parse solicitation; build compliance matrix; generate TPOC questions | J2, J4 | C1 |
| 4. Confirm | TPOC call; validate fit and approach; strategy alignment | J4, J5 | C1/C2 |
| 5. Execute | Draft all sections; build discrimination table; research market | J3, J5, J8 | C2 |
| 6. Monitor | Track compliance as sections are drafted; check PDCs | J2 | C1 (ongoing) |
| 7. Modify | Iterate based on review, red team, persona simulation | J3 | C2 |
| 8. Conclude | Format, assemble, submit; debrief and learn | J6, J7 | C3 |

### Key Insight: Steps 1-4 Are Phase C1

The first four steps of the universal job map (Define through Confirm) align precisely with Phase C1. This validates the phasing decision -- the MVP delivers value in the "understanding and preparation" part of the journey, where proven AI capabilities (search, extraction, synthesis) can be applied without the trust problems that plague drafting.

---

## Phase C1 Walking Skeleton Scope

Jobs in the walking skeleton (MVP):

| Job | Walking Skeleton Scope | Full Scope (Later) |
|-----|----------------------|-------------------|
| J1 | Semantic search across ingested corpus; retrieve relevant past work by topic | Agency preference modeling; voice/style extraction |
| J2 | Automated "shall" extraction; compliance matrix with live tracking | Pre-submission compliance gate (PES); cross-reference checking |
| J4 | Solicitation gap analysis; TPOC question generation; answer capture | Delta analysis propagation to all downstream artifacts |

Jobs deferred entirely to later phases: J3, J5, J6, J7, J8.

---

## Critical Design Constraint: The 10-15 Hour Budget

At 10-15 hours per proposal, every feature must pass a time-value test:

- **Ingestion overhead**: If corpus setup takes 2 hours, that is 13-20% of the entire proposal effort. Unacceptable for first use. Must be incremental -- ingest one document at a time, zero upfront cost.
- **Learning curve**: If the tool takes 2 hours to learn, that is the same 13-20% tax. Must be immediately useful on first command.
- **False economy**: If compliance matrix review takes as long as building one manually, the automation added overhead, not removed it.

The tool must save at least 1-2 hours per proposal (10-15% of total effort) to justify any adoption cost. At 2-3 proposals/year, that is 2-6 hours saved annually. The compounding corpus value must be real but cannot be the primary justification for early adoption.
