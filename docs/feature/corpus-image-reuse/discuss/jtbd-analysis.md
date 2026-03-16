# JTBD Analysis: Corpus Image Reuse

## Job Classification

**Job Type**: Brownfield (Job 2) -- extends existing corpus librarian, writer, and formatter agents with image awareness.

**ODI Phase**: Discovery required. The problem domain (image extraction, indexing, retrieval, adaptation) is understood from user context, but the interaction model, quality thresholds, and compliance boundaries need discovery before execution.

**Workflow**: `[research] -> discuss -> design -> distill -> baseline -> roadmap -> split -> execute -> review`

---

## Personas

### Primary: Dr. Elena Vasquez

**Who**: Principal Investigator at a 25-person defense tech startup. Writes 2-3 SBIR proposals per year.

**Demographics**:
- Technical proficiency: High (PhD, writes code, designs system architectures)
- Proposal frequency: 2-3 per year, each taking 4-6 weeks
- Environment: CLI-native, comfortable with terminal workflows
- Primary motivation: Leverage past winning work to maximize hit rate

**Jobs-to-be-Done**:

| Job Step | Goal | Desired Outcome |
|----------|------|-----------------|
| Recall | Remember which past proposals had useful diagrams | Minimize time to locate a known visual asset |
| Retrieve | Pull the right figure from past work | Minimize likelihood of recreating an existing asset |
| Assess | Determine if a past figure is reusable in current context | Minimize time to evaluate figure fitness |
| Adapt | Update captions, labels, and context for new solicitation | Minimize risk of submitting mismatched content |
| Insert | Place adapted figure into the new proposal with proper formatting | Minimize manual effort to integrate a reused figure |

**Pain Points**:
- "I know I had a great TRL roadmap in that Navy proposal from 2024, but I cannot find it" -- maps to: Recall
- "I end up recreating system architecture diagrams that are 80% identical to ones I already have" -- maps to: Retrieve
- "When I copy a figure from an old proposal, I forget to update the system name in the labels" -- maps to: Adapt

**Success Metrics**:
- Figure reuse identified and suggested in < 30 seconds during drafting
- Zero stale labels or captions in reused figures (all flagged for review)
- 50%+ reduction in time spent on figure creation for proposals to the same agency

### Secondary: Marcus Chen

**Who**: Business Development lead at a 120-person firm with 40+ past proposals. Manages the firm's institutional memory.

**Demographics**:
- Technical proficiency: Medium (business-oriented, not a developer)
- Proposal frequency: Oversees 8-12 proposals per year across PIs
- Environment: Delegates CLI work to proposal managers, reviews output
- Primary motivation: Build a reusable visual asset library that compounds across proposal cycles

**Jobs-to-be-Done**:

| Job Step | Goal | Desired Outcome |
|----------|------|-----------------|
| Catalog | Build a searchable library of all visual assets across 40+ proposals | Minimize time to create a comprehensive image inventory |
| Classify | Organize figures by type, agency, outcome, and domain | Minimize likelihood of miscategorized assets |
| Share | Make the library available to all PIs on the team | Minimize effort to distribute institutional visual knowledge |
| Track | Know which figures came from winning vs losing proposals | Minimize risk of reusing figures from losing proposals |

**Pain Points**:
- "We have 40+ proposals and no one knows what figures exist across them" -- maps to: Catalog
- "Different PIs recreate the same org chart for the same agency every quarter" -- maps to: Share
- "I want to prioritize figures from proposals we won, but I cannot filter by outcome" -- maps to: Track

**Success Metrics**:
- Full image catalog extracted from 40+ proposals in < 1 hour total (batch)
- Zero manual cataloging steps -- classification is automatic from metadata
- Outcome filtering available on every image search query

### Tertiary: Sarah Kim

**Who**: Consultant helping clients build SBIR capability. Onboards client organizations.

**Demographics**:
- Technical proficiency: High (former PI, now consulting)
- Engagement: One-time setup per client, then handoff
- Environment: Works in client's project directories
- Primary motivation: Fast client onboarding with maximum institutional knowledge extraction

**Jobs-to-be-Done**:

| Job Step | Goal | Desired Outcome |
|----------|------|-----------------|
| Onboard | Extract all reusable assets (text + images) from client's past proposals in one pass | Minimize time to build a client's asset library from scratch |
| Audit | Identify proprietary/sensitive images that should not be reused | Minimize risk of compliance violations from image reuse |

**Pain Points**:
- "When I onboard a new client, I spend days manually cataloging their past work. Images are the worst -- I have to open every PDF" -- maps to: Onboard
- "Some client proposals contain government-furnished images with restricted reuse rights" -- maps to: Audit

**Success Metrics**:
- Client onboarding extracts text and images in a single `corpus add` pass
- All extracted images have source attribution automatically recorded

---

## Job Stories

### JS-1: Recall and Retrieve Past Visual Assets

**When** I am drafting a proposal section that needs a system architecture diagram and I know I created a similar one for a past Air Force proposal,
**I want to** search my corpus for matching figures from past work,
**so I can** reuse a proven visual asset instead of recreating one from scratch.

**Functional Job**: Find and retrieve a specific figure from past proposals by type, agency, and domain match.
**Emotional Job**: Feel resourceful and efficient -- "I have a library, not just a pile of old PDFs."
**Social Job**: Demonstrate to the team that institutional knowledge compounds across proposals.

### JS-2: Assess Figure Fitness for New Context

**When** the system surfaces a candidate figure from a past proposal,
**I want to** quickly evaluate whether it fits the current solicitation's requirements,
**so I can** decide to reuse, adapt, or skip it without wasting time on an unfit asset.

**Functional Job**: Compare a candidate figure's metadata (agency, domain, outcome, age) against the current proposal context.
**Emotional Job**: Feel confident in the decision -- not anxious about whether a reused figure will hurt the proposal.
**Social Job**: Avoid the embarrassment of submitting a figure with wrong labels or outdated information.

### JS-3: Adapt and Insert a Reused Figure

**When** I have selected a figure from the corpus to reuse in my current proposal,
**I want to** update its caption, labels, and surrounding text to match the new solicitation,
**so I can** integrate it seamlessly without any trace of the original proposal context.

**Functional Job**: Modify textual elements (caption, cross-references, figure number) while preserving the image itself.
**Emotional Job**: Feel in control of the adaptation -- nothing slips through.
**Social Job**: Present a polished proposal where reused figures look purpose-built.

### JS-4: Build a Visual Asset Library at Scale

**When** I have 40+ past proposals and want to build a searchable visual asset library,
**I want to** extract and catalog all embedded images in a single batch operation,
**so I can** make the full library available to all PIs without manual cataloging.

**Functional Job**: Batch extract images from all corpus documents with automatic metadata tagging.
**Emotional Job**: Feel organized and empowered -- "We finally know what we have."
**Social Job**: Be the person who brought institutional knowledge management to the team.

### JS-5: Ensure Compliance When Reusing Images

**When** I am considering reusing a figure from a past proposal,
**I want to** see its provenance (source proposal, agency, outcome, any reuse restrictions),
**so I can** avoid compliance violations from reusing government-furnished or restricted images.

**Functional Job**: Track attribution and reuse permissions for every extracted image.
**Emotional Job**: Feel safe -- no anxiety about accidentally violating IP or reuse rules.
**Social Job**: Demonstrate due diligence to the contracting officer and team.

---

## Four Forces Analysis

### Demand-Generating

**Push (frustration with current situation)**:
- Dr. Vasquez spends 4-6 hours per proposal recreating figures that are 80% identical to past work
- Marcus Chen's team of 6 PIs duplicates the same org chart and facilities diagram every quarter
- Sarah Kim spends 2 full days per client onboarding manually cataloging visual assets from past proposals
- The current system ingests text only -- users know their images exist but have zero access to them through the tool

**Pull (attraction of new solution)**:
- One command (`corpus add`) extracts both text AND images from past proposals
- "Show me system architecture diagrams from proposals we won at DARPA" returns actionable results
- Reused figures maintain visual consistency across proposals to the same agency
- The visual asset library grows automatically with every ingested proposal

### Demand-Reducing

**Anxiety (fears about new approach)**:
- "What if the extracted image quality is too low for a proposal?" (PDF rasterization degrades images)
- "What if the system suggests an image with wrong labels and I do not catch it?" (stale content)
- "What if I accidentally reuse a government-furnished image without permission?" (compliance)
- "What if the metadata extraction gets the figure type or context wrong?" (misclassification)

**Habit (inertia of current approach)**:
- PIs already have personal folders of "good figures" they manually curate
- Copy-paste from past proposals in Word/PDF is a known workflow, even if slow
- The current Mermaid/Graphviz/Gemini generation pipeline works for new figures
- Some PIs prefer to always generate fresh figures for each proposal

### Assessment

- **Switch likelihood**: High -- Push is strong (measurable time waste) and Pull is concrete (searchable library)
- **Key blocker**: Anxiety about image quality and stale content. If low-quality or outdated images are surfaced without warning, trust erodes fast
- **Key enabler**: Push from time waste. 4-6 hours per proposal on figure recreation is a clear, quantifiable pain
- **Design implication**: Quality assessment and freshness signals are not nice-to-haves -- they are trust-building essentials. Every surfaced image must show quality indicators and staleness warnings

---

## Opportunity Scoring

### Outcome Statements

| # | Outcome Statement | Imp. (%) | Sat. (%) | Score | Priority |
|---|-------------------|----------|----------|-------|----------|
| 1 | Minimize the time to locate a relevant figure from past proposals | 95 | 10 | 18.0 | Extremely Underserved |
| 2 | Minimize the likelihood of recreating a figure that already exists in the corpus | 90 | 15 | 16.5 | Extremely Underserved |
| 3 | Minimize the time to assess whether a past figure fits the current proposal context | 85 | 10 | 16.0 | Extremely Underserved |
| 4 | Minimize the likelihood of submitting a reused figure with stale or incorrect labels | 90 | 20 | 16.0 | Extremely Underserved |
| 5 | Minimize the time to catalog all visual assets from a batch of past proposals | 80 | 5 | 15.5 | Extremely Underserved |
| 6 | Minimize the likelihood of reusing a government-furnished image without attribution | 85 | 15 | 15.5 | Extremely Underserved |
| 7 | Minimize the time to adapt a reused figure's caption and cross-references | 75 | 20 | 13.0 | Underserved |
| 8 | Minimize the likelihood of inserting a low-resolution image into a submission | 70 | 30 | 11.0 | Appropriately Served |
| 9 | Maximize the likelihood that figure search results include outcome (win/loss) data | 65 | 10 | 12.0 | Underserved |

### Scoring Method

- Importance: estimated % of target personas rating outcome 4+ on 5-point scale (team estimate based on persona analysis)
- Satisfaction: estimated % satisfaction with current approach (near-zero for most -- current system has no image capability)
- Score: Importance + max(0, Importance - Satisfaction)
- Data quality: Team estimate. Confidence: Medium (based on persona research, no direct survey)

### Top Opportunities (Score >= 12)

1. **Minimize the time to locate a relevant figure** (18.0) -- Maps to JS-1, drives image search capability
2. **Minimize the likelihood of recreating an existing figure** (16.5) -- Maps to JS-1/JS-4, drives extraction and indexing
3. **Minimize the time to assess figure fitness** (16.0) -- Maps to JS-2, drives rich metadata display
4. **Minimize the likelihood of stale labels** (16.0) -- Maps to JS-3, drives adaptation warnings
5. **Minimize the time to catalog visual assets at scale** (15.5) -- Maps to JS-4, drives batch extraction
6. **Minimize the likelihood of compliance violations** (15.5) -- Maps to JS-5, drives attribution tracking

### Overserved Areas

None identified -- current system has zero image capability, so all outcomes are underserved.

---

## Job-to-Story Mapping

| Job Story | User Stories (forward reference) | Priority |
|-----------|--------------------------------|----------|
| JS-1: Recall and Retrieve | US-CIR-001 (Image Extraction), US-CIR-002 (Image Search) | Must Have |
| JS-2: Assess Figure Fitness | US-CIR-003 (Image Assessment) | Must Have |
| JS-3: Adapt and Insert | US-CIR-004 (Image Adaptation) | Should Have |
| JS-4: Build Library at Scale | US-CIR-001 (Image Extraction -- batch mode) | Must Have |
| JS-5: Compliance Tracking | US-CIR-005 (Attribution Tracking) | Must Have |
