# JTBD Analysis: Proposal Quality Discovery

## Job Classification

**Type**: Brownfield (extends existing agents with new cross-cutting Q&A flow)
**Workflow**: discuss -> design -> distill -> baseline -> roadmap -> split -> execute -> review

## Job Stories

### JS-1: Replicate Winning Approaches

**When** I am starting a new SBIR proposal and my company has submitted proposals before (some won, some lost),
**I want to** capture what made our winning proposals strong and what made our losing proposals weak,
**so I can** ensure the new proposal replicates our proven winning patterns and avoids our known failure modes.

#### Functional Job
Extract structured quality intelligence from past proposal outcomes and evaluator feedback to inform future proposal writing.

#### Emotional Job
Feel confident that institutional knowledge is preserved and applied -- not relying on memory or tribal knowledge that degrades over time.

#### Social Job
Be seen as someone who learns from every submission cycle, demonstrating systematic improvement to teammates and leadership.

#### Forces Analysis
- **Push**: Dr. Elena Vasquez lost two Air Force proposals with similar evaluator critiques ("vague TRL methodology") -- she realized the same mistakes keep recurring because lessons live in people's heads, not in the system. The debrief analyst (Wave 9) captures weaknesses but nothing feeds them forward proactively to the writer during the next proposal.
- **Pull**: A system that automatically surfaces "your Air Force proposals that won all had explicit TRL entry/exit criteria" and "evaluators praised your use of quantitative metrics in past performance" when drafting a new Air Force proposal.
- **Anxiety**: "What if the system overfits to past patterns and produces cookie-cutter proposals that lack the originality evaluators reward?"
- **Habit**: Currently, Elena re-reads her best past proposals manually before starting a new one, and Marcus Chen (her BD lead) keeps a mental list of "what evaluators like."

#### Assessment
- Switch likelihood: HIGH (strong push from recurring losses + strong pull from automated pattern replication)
- Key blocker: Anxiety about losing originality
- Design implication: System must present patterns as guidance, not templates -- "evaluators praised X" not "always write X"

---

### JS-2: Capture Writing Quality Preferences

**When** I am setting up the proposal system for the first time (or updating after a proposal cycle),
**I want to** articulate my preferences for writing style, tone, organization, and quality standards,
**so I can** get proposals that sound like my company wrote them, not like a generic AI produced them.

#### Functional Job
Record writing style preferences (tone, level of detail, organization patterns, terminology conventions) in a structured artifact that the writer agent consumes.

#### Emotional Job
Feel ownership over the proposal voice -- the system amplifies my style rather than replacing it.

#### Social Job
Present proposals that reflect the company's professional identity consistently, so evaluators associate a quality standard with the company name.

#### Forces Analysis
- **Push**: Marcus Chen noticed that the `writing_style` field exists in proposal-state.json but nothing ever asks him to set it. The writer agent uses `elements-of-style` by default but his company prefers a more direct, data-heavy style that doesn't match Strunk & White for every context. Past proposals written by different PIs sound completely different from each other.
- **Pull**: A guided interview that captures "we prefer quantitative over qualitative claims," "keep paragraphs under 4 sentences," "always lead with the result, then cite the evidence" -- producing a personalized writing guide the writer agent loads alongside elements-of-style.
- **Anxiety**: "What if the interview takes too long and I don't remember all my preferences upfront?"
- **Habit**: Currently, Marcus gives verbal instructions to each PI before they start writing: "remember, data first, claims second."

#### Assessment
- Switch likelihood: HIGH (low effort, high value, directly addresses existing gap)
- Key blocker: Interview fatigue -- must be short and progressively refinable
- Design implication: Interview should be completable in 5-10 minutes, with ability to update after each proposal cycle

---

### JS-3: Extract Meta-Writing Feedback from Evaluator Comments

**When** I receive a debrief (or recall evaluator feedback from past submissions),
**I want to** separate comments about writing quality (clarity, organization, tone, persuasiveness) from comments about technical content,
**so I can** build a "writing quality profile" that tells me how evaluators perceive my company's prose, not just our technical ideas.

#### Functional Job
Parse evaluator feedback for meta-writing signals -- comments about readability, organization, persuasiveness, specificity -- distinct from technical merit comments.

#### Emotional Job
Feel empowered by understanding that proposal quality has two dimensions (what you say AND how you say it) and both are within my control.

#### Social Job
Demonstrate to evaluators through improved writing that we take their feedback seriously and improve systematically.

#### Forces Analysis
- **Push**: Dr. Sarah Kim received debrief feedback saying "the technical approach section was difficult to follow" and "the commercialization plan lacked specific market data." The first comment is about writing quality (organization/clarity); the second is about content. Currently, the debrief analyst treats both the same -- maps them to sections and adds them to the weakness profile. There is no way to distinguish "we need to write better" from "we need to research better."
- **Pull**: A writing quality profile that says: "Air Force evaluators have twice noted your proposals are hard to follow in technical approach sections -- consider shorter paragraphs and more subheadings" as distinct from "evaluators want more quantitative TRL evidence."
- **Anxiety**: "What if we don't have enough debriefs to build a meaningful writing quality profile?"
- **Habit**: Currently, debrief feedback is processed as a single stream -- no categorization between writing quality and content quality.

#### Assessment
- Switch likelihood: MEDIUM (requires debrief history to be useful -- new companies start cold)
- Key blocker: Requires minimum debrief corpus to generate actionable patterns
- Design implication: Graceful degradation when debrief corpus is thin; explicit confidence levels

---

### JS-4: Maintain Consistent Quality Standards Across Proposal Cycles

**When** I have completed several proposal cycles and accumulated quality intelligence (winning patterns, writing preferences, evaluator meta-feedback),
**I want to** ensure this intelligence automatically informs every new proposal without manual re-entry,
**so I can** build compounding quality improvement across cycles rather than starting from scratch each time.

#### Functional Job
Persist quality discovery artifacts at the company level (~/.sbir/) so they survive across proposals and compound with each cycle.

#### Emotional Job
Feel that the system gets smarter with every proposal -- each submission makes the next one better.

#### Social Job
Build a reputation for consistently high-quality proposals that stand out from competitors who don't learn from feedback.

#### Forces Analysis
- **Push**: After 5 proposals, Elena has accumulated knowledge about what works and what doesn't, but it lives in scattered artifacts across proposal directories. The debrief analyst updates the weakness profile per-proposal, but there is no company-level "quality playbook" that aggregates lessons across all proposals.
- **Pull**: A living quality playbook at ~/.sbir/ that every new proposal reads automatically -- winning patterns from all prior wins, writing preferences that evolve, evaluator feedback trends that sharpen with each cycle.
- **Anxiety**: "What if old patterns become stale as agency preferences shift?"
- **Habit**: Currently, institutional knowledge transfers via the weakness profile (negative patterns only) and verbal team discussions.

#### Assessment
- Switch likelihood: HIGH (compounds existing system investment)
- Key blocker: Staleness anxiety -- must support pattern deprecation/update
- Design implication: Artifacts must support versioning, timestamps, and explicit "review this pattern" triggers

---

## Opportunity Scoring

| # | Outcome Statement | Imp. | Sat. | Score | Priority |
|---|-------------------|------|------|-------|----------|
| 1 | Minimize the likelihood of repeating known proposal weaknesses | 95% | 30% | 16.0 | Extremely Underserved |
| 2 | Minimize the time to capture writing quality preferences | 85% | 10% | 14.5 | Extremely Underserved |
| 3 | Maximize the likelihood that winning patterns are replicated | 90% | 20% | 15.0 | Extremely Underserved |
| 4 | Minimize the likelihood of losing company-specific voice in proposals | 80% | 15% | 13.5 | Underserved |
| 5 | Minimize the time to distinguish writing feedback from content feedback | 70% | 5% | 11.9 | Appropriately Served |
| 6 | Maximize the likelihood that quality intelligence compounds across cycles | 90% | 25% | 13.5 | Underserved |

### Scoring Method
- Importance: estimated from feature description emphasis and system gap severity
- Satisfaction: estimated from current system capability analysis
- Score: Importance + max(0, Importance - Satisfaction)
- Data quality: team estimate based on codebase audit (not user interviews)

### Top Opportunities (Score >= 12)
1. Minimize repeating known weaknesses -- Score: 16.0 -- JS-1 (replicate winning approaches)
2. Maximize winning pattern replication -- Score: 15.0 -- JS-1
3. Minimize time to capture writing preferences -- Score: 14.5 -- JS-2
4. Minimize loss of company voice -- Score: 13.5 -- JS-2, JS-4
5. Maximize quality compounding across cycles -- Score: 13.5 -- JS-4

## Personas

### Dr. Elena Vasquez -- Principal Investigator
- 8 years SBIR experience, 12 proposals submitted, 5 wins
- Writes technical approach and SOW sections herself
- Keeps mental notes about "what worked" from past proposals
- Frustrated that lessons from debriefs don't automatically inform next proposal
- Trigger: starting a new proposal after receiving a loss debrief

### Marcus Chen -- Business Development Lead
- Manages 3-4 active proposals simultaneously across PIs
- Cares about consistency: all proposals should "sound like Pacific Systems Engineering"
- Keeps verbal checklist of writing quality standards he shares with each PI
- Frustrated that writing_style field exists but nothing populates it
- Trigger: onboarding a new PI who doesn't know the company's proposal voice

### Dr. Sarah Kim -- Research Director (Secondary Persona)
- Reviews all proposals before submission
- Focuses on evaluator perception: "how will this read to a tired reviewer on proposal #20?"
- Has most debrief reading experience, notices meta-writing patterns others miss
- Frustrated that writing quality feedback gets mixed in with content feedback
- Trigger: reviewing a draft and wishing the writer had known about past evaluator comments on readability

## Domain Language Glossary

| Term | Definition |
|------|-----------|
| Quality discovery | Guided Q&A process capturing what makes proposals win/lose from a writing quality perspective |
| Winning patterns | Specific writing practices, structures, and approaches found in proposals that received high evaluator scores |
| Writing quality profile | Structured artifact capturing how evaluators perceive a company's prose quality (distinct from technical merit) |
| Quality preferences | User-articulated standards for tone, style, organization, and level of detail in proposal writing |
| Meta-writing feedback | Evaluator comments about how something is written (clarity, organization, persuasiveness) vs. what is written (technical content) |
| Quality playbook | Company-level aggregate of winning patterns, writing preferences, and evaluator feedback trends |
