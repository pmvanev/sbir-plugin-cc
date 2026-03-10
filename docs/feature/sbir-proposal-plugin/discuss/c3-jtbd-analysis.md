# JTBD Analysis -- Phase C3: Proposal Production & Learning

Phase C3 covers Waves 5-9: visual assets, formatting and assembly, final review, submission, and post-submission learning. This analysis deepens the existing J6 and J7 job stories from the C1/C2 JTBD analysis, discovers new jobs specific to C3 scope, and maps all jobs to waves.

## Persona: Phil Santos (Continued)

Same persona as C1/C2 analysis. Relevant C3-specific context:

- By the time Phil reaches Wave 5, he has invested 8-12 hours in Waves 0-4. Sunk cost pressure is real.
- Formatting is the task Phil resents most -- it adds no intellectual value but carries disqualification risk.
- Phil submits to DSIP (DoD), Grants.gov (multi-agency), and occasionally NSPIRES (NASA). Each portal has different packaging rules.
- Phil receives debrief feedback on roughly 60% of submissions. The other 40% get no feedback at all.
- At 2-3 proposals per year, Phil has accumulated 6-8 proposals over 3 years. Pattern detection is just becoming possible.

---

## Job Stories

### J6: Format and Assemble Without Manual Labor (Deepened)

**When** I have a final draft with all sections approved and figures ready,
**I want to** automate document formatting (margins, headers, figure placement, cross-references, page counts) and assembly into submission-ready volumes,
**so I can** stop spending 2-3 hours on mechanical formatting work that adds no intellectual value but carries disqualification risk if done wrong.

| Dimension | Description |
|-----------|-------------|
| Functional | Produce formatted, submission-compliant document package from approved draft content and figures |
| Emotional | Feel relieved that formatting is handled correctly, not anxious about orphaned lines, wrong fonts, or misplaced figures |
| Social | Submit a polished document that looks as professional as a proposal firm's output |

**Forces**:

- **Push**: "Formatting is purely manual" -- orphans, widows, margins, cross-references, page counts. Phil spent 3 hours reformatting AF241-087 after a last-minute section edit shifted every page. One proposal was returned for wrong font size in headers.
- **Pull**: Template-based automated formatting that applies solicitation-specific rules in one command. Output in Google Docs, Word, or LaTeX depending on the solicitation. Compliance matrix final check catches formatting violations before submission.
- **Anxiety**: Will automated formatting introduce errors Phil does not notice? What if the tool cannot handle agency-specific quirks (e.g., NSF requires specific header formatting that differs from DoD)? Will Phil lose control over the final look?
- **Habit**: Manual formatting in Word or Google Docs. "At least I control the output." Phil has Word templates from past proposals that he reuses and tweaks.

**Design Implication**: Template-based approach is more feasible than LLM formatting for precise layout control. The tool should generate content into a template, not try to control orphans and widows via LLM. Phil needs to preview and make manual adjustments before submission. This is an assist, not full automation.

**Feasibility Assessment**: Acknowledged in C1 discovery as hard. The tool should handle what it can (section assembly, cross-references, page counting, format rule verification) and provide a clear handoff for what requires manual intervention (orphan/widow control, final figure placement tweaks). Overpromising formatting automation and underdelivering would be worse than scoping it honestly.

---

### J7: Learn from Win/Loss Patterns (Deepened)

**When** I receive a debrief letter (or get no feedback at all) after a proposal decision,
**I want to** systematically capture what worked and what did not, map critiques to specific proposal sections, and see patterns across my submission history,
**so I can** improve my win rate over time instead of repeating the same mistakes and relying on fading memory.

| Dimension | Description |
|-----------|-------------|
| Functional | Parse debrief feedback; map critiques to proposal sections; track win/loss patterns across multiple proposals; update company capability profile |
| Emotional | Feel that every proposal makes the next one better -- that institutional learning is happening, not just repetition |
| Social | Demonstrate to leadership and teaming partners that the company has a disciplined approach to improving win rates |

**Forces**:

- **Push**: "Vague or no feedback" makes improvement hard. Phil's debrief for AF241-087 said "technical approach lacked sufficient detail on transition pathway" -- useful, but it took him 20 minutes to figure out which section that mapped to. His debrief for N222-038 (which he won) had high marks on "prior relevant work" -- but he cannot systematically compare what made one win and the other lose.
- **Pull**: Structured debrief parsing that maps each critique to a section. Win/loss pattern analysis across the corpus: "Your section 3 scores average 7.2/10 when you include prototype data, 5.1/10 when you do not." Automatic update to known weakness profile that the reviewer agent consults in future proposals.
- **Anxiety**: Small corpus (6-8 proposals over 3 years) makes pattern detection unreliable. "Am I seeing a real pattern or just noise?" Will ingesting a debrief take more time than the insight is worth?
- **Habit**: Informal mental notes. "I'll remember for next time." Phil keeps a mental model of what works but has never written it down systematically. After each debrief, he skims it and moves on.

**Design Implication**: At 2-3 proposals/year, meaningful pattern detection requires 3-5 years of data. The immediate value is structured capture (debrief -> section mapping) and corpus enrichment (win/loss tags, critique annotations). Pattern analysis becomes increasingly valuable over time but must not be the primary selling point for adoption. Near-zero ingestion effort is critical -- if parsing a debrief takes more than 5 minutes of Phil's time, it will not happen.

---

### J9: Produce Visual Assets That Strengthen the Narrative (New)

**When** I have approved draft sections that reference figure placeholders (system diagrams, data flow charts, concept illustrations, timelines),
**I want to** generate professional-quality diagrams and figures that are cross-referenced in the text and meet agency format requirements,
**so I can** submit a proposal with visuals that strengthen the technical argument instead of looking like afterthoughts.

| Dimension | Description |
|-----------|-------------|
| Functional | Generate SVG/Mermaid/Graphviz diagrams, concept illustrations, data charts from draft content; ensure captions and cross-references are consistent |
| Emotional | Feel that figures add value to the proposal rather than being obligatory filler |
| Social | Present visuals that look professional -- not hand-drawn boxes or clip art |

**Forces**:

- **Push**: "Creating images and diagrams" was noted as medium-intensity pain in problem validation (all sources). Phil currently uses draw.io or PowerPoint to create figures manually, spending 30-60 minutes per figure. Cross-references between text and figures break when sections are reordered.
- **Pull**: Automated diagram generation from structured draft content. System architecture diagrams from Mermaid definitions embedded in the outline. Concept figures via image generation API. Cross-reference log that stays consistent even when sections move.
- **Anxiety**: Will generated diagrams look generic or "AI-generated"? Will they meet agency resolution and format requirements (some agencies require 300 DPI minimum)? Will Phil have enough control to customize diagrams?
- **Habit**: Manual figure creation in draw.io or PowerPoint. "At least I can make it look exactly how I want."

**Design Implication**: Diagrams that can be described structurally (system architecture, timelines, data flows) are good candidates for automated generation via Mermaid/Graphviz/SVG. Concept illustrations and technical photos are harder -- the Gemini image API is available but quality must be validated. Every figure needs a human review checkpoint. The tool should generate a draft figure, present it for review, and allow iteration or manual replacement.

---

### J10: Survive Submission Without Errors (New)

**When** I have a reviewed, formatted proposal ready to submit,
**I want to** package it correctly for the specific submission portal (DSIP, Grants.gov, NSPIRES), verify all file naming and size requirements, submit on time, and create an immutable archive of exactly what was submitted,
**so I can** avoid the nightmare scenario of a rejected submission due to a file naming error or missed attachment after weeks of work.

| Dimension | Description |
|-----------|-------------|
| Functional | Identify correct portal; apply portal-specific packaging rules; verify file naming, sizes, and formats; submit; capture confirmation; create immutable archive |
| Emotional | Feel certain that the submission is correct and complete -- no "did I remember to attach the budget?" anxiety at 11pm before the deadline |
| Social | Be the person who never misses a submission deadline or gets rejected on a technicality |

**Forces**:

- **Push**: Phil once discovered 2 hours before deadline that DSIP required a specific file naming convention he had not followed. Repackaging under time pressure was stressful. Another time, he forgot to attach the required Firm Certification form to a Grants.gov submission and had to scramble for a late correction.
- **Pull**: Portal-aware packaging that knows DSIP wants `TopicNumber_CompanyName_Volume1.pdf` and Grants.gov wants specific form attachments. Pre-submission checklist that verifies every required file exists, is named correctly, and is within size limits. Confirmation capture and immutable archive.
- **Anxiety**: Will the tool correctly identify portal requirements that change between solicitation cycles? What if the tool submits incorrectly and there is no time to fix it?
- **Habit**: Manual packaging and submission. Phil has a personal checklist he runs through. "I always triple-check before clicking submit."

**Design Implication**: The tool should prepare the package and present it for verification but should NOT auto-submit without explicit human confirmation. Submission is a point of no return. The immutable archive is critical for compliance and audit purposes -- PES enforces read-only status on submitted packages.

---

### J11: Catch Fatal Flaws Before Submission (New)

**When** I have a formatted, assembled proposal that I believe is ready to submit,
**I want to** run it through a simulated government technical evaluator review and a red team critique,
**so I can** catch fatal flaws, weak arguments, and compliance gaps while there is still time to fix them.

| Dimension | Description |
|-----------|-------------|
| Functional | Simulate reviewer persona scoring against evaluation criteria; red team the strongest objections; verify compliance matrix completion; check for missing attachments and certifications |
| Emotional | Feel cautious but ultimately confident -- "a simulated reviewer found no fatal flaws" is powerful reassurance before clicking submit |
| Social | Demonstrate that the proposal was rigorously reviewed, not just proofread |

**Forces**:

- **Push**: Phil's AF241-087 debrief critique said "transition pathway lacked specificity" -- something a simulated reviewer could have caught. He has no one to do a proper red team review; he is the sole writer.
- **Pull**: Multi-persona simulation (technical evaluator + cost evaluator + program manager). Red team that identifies the 3 strongest objections a skeptical reviewer would raise. Debrief-informed review that checks against known weaknesses from past proposals in the corpus.
- **Anxiety**: Will the simulated reviewer catch things the real reviewer would catch? Or will it give false confidence? Is simulated review a substitute for or supplement to Phil's own review?
- **Habit**: Phil reads the proposal once or twice himself. "I am the only reviewer I have."

**Design Implication**: Simulated review is a supplement, not a replacement. The tool surfaces potential issues; Phil decides which to address. The iteration loop (find issues -> fix -> re-review) must converge -- a maximum of 2-3 review cycles before diminishing returns. The tool should flag when an issue was also raised in a past debrief (corpus-informed).

---

## Opportunity Scoring -- C3 Jobs

Formula: Score = Importance + Max(0, Importance - Satisfaction)

Ratings based on C1/C2 discovery evidence plus C3-specific analysis of Phil's workflow in Waves 5-9.

**Data Quality Note**: Ratings refined from C1 JTBD analysis with deeper analysis of formatting/submission/learning workflows. Confidence is Medium -- single-user context with strong behavioral signals from past proposal experience.

| # | Job | Imp | Sat | Score | Wave | Priority |
|---|-----|-----|-----|-------|------|----------|
| J10 | Survive submission without errors | 9 | 3 | 15 | 8 | Extremely Underserved |
| J11 | Catch fatal flaws before submission | 8 | 2 | 14 | 7 | Underserved |
| J6 | Format and assemble without manual labor | 7 | 2 | 12 | 5-6 | Underserved |
| J9 | Produce visual assets that strengthen narrative | 7 | 3 | 11 | 5 | Appropriately Served |
| J7 | Learn from win/loss patterns | 7 | 2 | 12 | 9 | Underserved |

### Scoring Rationale

**J10 (Score 15)**: Highest importance in C3. Submission failure after weeks of work is catastrophic -- it wastes 10-15 hours of effort entirely. Current satisfaction is low because Phil relies on manual checklists and anxiety. Portal-specific packaging rules change between solicitation cycles and are poorly documented.

**J11 (Score 14)**: Phil is the sole reviewer. No red team, no fresh eyes. Every debrief critique that could have been caught before submission represents preventable waste. The corpus of past debriefs makes this increasingly powerful over time.

**J6 (Score 12)**: Real pain but feasibility is genuinely uncertain. Template-based approach is viable for structure; precise layout control (orphans, widows) remains hard. Honest scoping is critical -- overpromise here and trust collapses.

**J9 (Score 11)**: Moderate pain. Phil creates figures manually but it works. Automated generation would save 30-60 minutes per figure (3-5 figures per proposal = 1.5-5 hours saved). But quality concerns about generated figures are real.

**J7 (Score 12)**: High long-term value but extremely slow payoff. Near-zero ingestion effort is the only path to adoption. Immediate value is structured capture; pattern analysis is future value.

---

## Job Map (8-Step Universal) -- C3 Waves

| Step | C3 Activity | Primary Job(s) | Wave |
|------|------------|-----------------|------|
| 1. Define | Determine what figures are needed from outline placeholders | J9 | 5 |
| 2. Locate | Gather figure references, format templates, portal requirements | J6, J9, J10 | 5-6 |
| 3. Prepare | Generate figures; apply formatting templates; build submission package | J6, J9, J10 | 5-6, 8 |
| 4. Confirm | Verify compliance matrix completion; verify figure cross-references; verify file naming | J6, J10, J11 | 6, 8 |
| 5. Execute | Run final review simulation; address issues; submit | J10, J11 | 7-8 |
| 6. Monitor | Track submission confirmation; track award notification timeline | J10, J7 | 8-9 |
| 7. Modify | Address review findings; repackage if portal rejects; ingest debrief | J11, J10, J7 | 7-9 |
| 8. Conclude | Archive submitted proposal; update win/loss analysis; feed lessons learned | J7, J10 | 8-9 |

### Key Insight: Steps 4-8 Are Where C3 Delivers Most Value

Steps 1-3 (Define, Locate, Prepare) in C3 are largely mechanical -- template application, figure generation, package assembly. The real value is in Steps 4-8: verification that catches errors before they become rejections (J10, J11), and learning loops that compound over proposal cycles (J7).

---

## C3 Phase Strategy

### Must Have (Ship or C3 has no value)

- **J10**: Submission packaging and archival (Wave 8) -- without correct submission, all prior work is wasted
- **J6**: Document assembly and compliance verification (Wave 6 core) -- submission requires assembled documents
- **J11**: Final review simulation (Wave 7) -- last chance to catch fatal flaws

### Should Have (Significant value, workaround exists)

- **J9**: Visual asset generation (Wave 5) -- saves hours but Phil can create figures manually
- **J7**: Debrief ingestion and structured capture (Wave 9 core) -- immediate value even without pattern analysis

### Could Have (Nice-to-have, long-term payoff)

- **J7**: Win/loss pattern analysis (Wave 9 advanced) -- requires 3-5 years of data to be reliable

---

## PES Additions for C3

C3 introduces four new PES invariant classes (extending the C1 foundation from US-006):

1. **PDC Gate (Wave 4 -> Wave 5)**: All sections must have Tier 1+2 PDCs GREEN and at least one human review before visual assets can begin. Prevents "polishing content that is not yet approved."

2. **Deadline Blocking (Any Wave)**: When days_to_deadline drops below critical threshold, PES blocks non-essential waves (e.g., visual asset generation) and surfaces "submit what you have" guidance. Phil should not spend time on figures when the deadline is tomorrow.

3. **Submission Immutability (Wave 8)**: Once submitted, the proposal package and all its artifacts are marked read-only. PES blocks any modification to submitted files. Archive is immutable.

4. **Corpus Integrity (Wave 9)**: Win/loss tags are append-only. Debrief annotations layer on top of source documents without modifying them. Submitted proposals in the corpus cannot be edited.

---

## Cross-References

- C1/C2 JTBD analysis: `docs/feature/sbir-proposal-plugin/discuss/jtbd-analysis.md` (J1-J5, J8)
- Discovery evidence: `docs/feature/sbir-proposal-plugin/discover/problem-validation.md`
- Opportunity tree: `docs/feature/sbir-proposal-plugin/discover/opportunity-tree.md` (O6, O7)
- Specification: `sbir-proposal-plugin.md` (Waves 5-9, lines 316-455)
