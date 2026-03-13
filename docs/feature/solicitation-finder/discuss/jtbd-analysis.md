# JTBD Analysis: Solicitation Finder

## Primary Job Statement

Help me find the best-fit SBIR/STTR topics for my company from each solicitation cycle so I can focus my limited proposal-writing time on topics with the highest win probability.

---

## Job Story 1: Cycle-Wide Topic Discovery

**When** a new DoD SBIR/STTR solicitation cycle opens with 300-500 topics,
**I want to** quickly identify which topics match my company's capabilities, certifications, and past performance,
**so I can** narrow the field to a manageable shortlist in minutes instead of hours.

### Functional Job

Reduce 300-500 topics to 5-15 scored candidates ranked by fit.

### Emotional Job

Feel confident that I have not missed any high-fit topics -- relief from the fear of false negatives.

### Social Job

Be seen as strategic about which topics to pursue, not reactive or scattershot.

### Forces Analysis

- **Push**: Spending 2-6 hours per cycle manually scrolling through topics. Missing good-fit topics because of fatigue or unfamiliar terminology. Deadline pressure compresses the discovery window.
- **Pull**: A 10-minute scored shortlist matched against actual company capabilities. Semantic matching that catches terminology mismatches ("directed energy" vs "high-energy laser"). Disqualifiers surfaced immediately instead of after hours of evaluation.
- **Anxiety**: Will the automated matching miss a great-fit topic I would have found manually? Will scoring accuracy be good enough to trust for Go/No-Go decisions? What if the API data is stale or incomplete?
- **Habit**: Manual browsing on dodsbirsttr.mil feels thorough even though it is slow. Relying on gut feel and memory for topic-to-capability matching. Spreadsheet-based tracking across cycles.

### Assessment

- Switch likelihood: HIGH
- Key blocker: Anxiety about false negatives (missed good-fit topics)
- Key enabler: Push of time pressure + Pull of semantic matching quality
- Design implication: Must show what was excluded and why, so user can verify nothing was missed

---

## Job Story 2: Eligibility Pre-Screening

**When** I find a topic that looks like a technical match,
**I want to** immediately know if there are disqualifying eligibility requirements (clearance, STTR institution, Phase II prerequisite),
**so I can** avoid investing hours evaluating a topic I cannot actually pursue.

### Functional Job

Surface hard-stop eligibility disqualifiers before any deep evaluation.

### Emotional Job

Feel protected from wasting time on topics that are structurally impossible to pursue.

### Social Job

Not applicable (private decision).

### Forces Analysis

- **Push**: Discovering after 2 hours of evaluation that a topic requires TS clearance the company does not hold. Realizing mid-proposal that an STTR topic requires a research institution partner.
- **Pull**: Instant disqualifier flags alongside scored results. Clear "cannot pursue" vs "needs attention" classification.
- **Anxiety**: What if the automated screening misses a requirement buried in the topic PDF? What if profile data is incomplete and causes false disqualification?
- **Habit**: Reading the full topic description to manually identify requirements.

### Assessment

- Switch likelihood: HIGH
- Key blocker: Anxiety about false disqualifications from incomplete profile data
- Key enabler: Push of wasted hours on structurally ineligible topics
- Design implication: Show disqualification reason and profile field that triggered it. Allow override if user believes profile is incomplete.

---

## Job Story 3: Topic-to-Proposal Transition

**When** I have reviewed the scored shortlist and decided to pursue a topic,
**I want to** transition directly into the proposal creation workflow with all topic data pre-loaded,
**so I can** start writing immediately without re-entering topic metadata.

### Functional Job

Carry topic data (ID, agency, title, phase, deadline) from finder results into `/sbir:proposal new`.

### Emotional Job

Feel momentum -- the decision to pursue flows seamlessly into action.

### Social Job

Not applicable (private workflow).

### Forces Analysis

- **Push**: Copying topic IDs and metadata from one tool to another. Re-entering data that was already parsed during scoring.
- **Pull**: Select a topic from the shortlist and immediately enter the proposal workflow.
- **Anxiety**: Will the topic data carry over correctly? What if I select the wrong topic by accident?
- **Habit**: Opening a separate browser tab to copy the solicitation details.

### Assessment

- Switch likelihood: HIGH
- Key blocker: Low anxiety -- straightforward data handoff
- Key enabler: Pull of seamless workflow integration
- Design implication: Confirmation step before transitioning. Show topic summary for verification.

---

## Job Story 4: BAA PDF Fallback

**When** the DSIP API is unavailable or I have a BAA PDF from another source (colleague, email, agency site),
**I want to** provide the PDF directly and get the same scored shortlist,
**so I can** still find best-fit topics regardless of API availability.

### Functional Job

Extract topics from a BAA PDF and score them identically to API-sourced topics.

### Emotional Job

Feel resilient -- the tool works regardless of external service availability.

### Social Job

Not applicable.

### Forces Analysis

- **Push**: API downtime or rate limiting blocking the entire workflow. Having a PDF in hand but no way to batch-process it.
- **Pull**: Same scoring quality from any input source. Automatic fallback without manual intervention.
- **Anxiety**: Will PDF parsing capture all topics accurately? Will the quality be as good as API-sourced data?
- **Habit**: Manually reading the BAA PDF and noting topics in a spreadsheet.

### Assessment

- Switch likelihood: HIGH
- Key blocker: Anxiety about PDF parsing accuracy
- Key enabler: Push of API unreliability + Pull of consistent quality
- Design implication: Show how many topics were extracted from the PDF. Let user verify count against expected total.

---

## 8-Step Job Map

| Step | Goal | Current Pain | Finder Solution |
|------|------|-------------|-----------------|
| 1. Define | Decide which solicitation cycle to search | Remembers to check dodsbirsttr.mil; forgets timing | Command accepts `--solicitation` filter or defaults to current open cycle |
| 2. Locate | Access all open topics | Navigate to website, browse paginated results | Python script fetches from DSIP API; falls back to user-provided BAA PDF |
| 3. Prepare | Filter to relevant subset | Manually select agency/phase filters on website | `--agency` and `--phase` flags pre-filter before scoring |
| 4. Confirm | Verify company profile is ready for matching | Mental recall of capabilities, clearances | Reads `~/.sbir/company-profile.json`; warns if missing or incomplete |
| 5. Execute | Score and rank topics by fit | Read each topic, mentally assess fit, gut-feel ranking | Two-pass matching: keyword pre-filter then LLM five-dimension scoring |
| 6. Monitor | Review results and assess quality | No systematic review; relies on feeling "done" | Ranked table with per-dimension breakdown; disqualified topics shown with reasons |
| 7. Modify | Refine search or re-score | Start over from scratch | Re-run with different filters; results saved for comparison |
| 8. Conclude | Select topic(s) for pursuit | Decision under time pressure with incomplete data | Select from shortlist, transition to `/sbir:proposal new` with data pre-loaded |

---

## Opportunity Prioritization (from Discovery)

| Priority | Opportunity | Score | Stories Addressing |
|----------|------------|-------|-------------------|
| 1 | Automated Topic Discovery (O1) | 18 | US-SF-001, US-SF-004 |
| 2 | Semantic Matching Beyond Keywords (O2) | 17 | US-SF-002 |
| 3 | Fast Go/No-Go Scoring (O4) | 15 | US-SF-002 |
| 4 | Automatic Eligibility Screening (O3) | 14 | US-SF-002 |
| 5 | Disqualifier Detection (O5) | 13 | US-SF-002, US-SF-003 |
| 6 | Deadline Tracking (O6) | 8 | US-SF-005 |
