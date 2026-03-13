# Opportunity Solution Tree: Solicitation Finder

## Desired Outcome

Minimize the time from "new solicitation cycle opened" to "priority-ranked shortlist of best-fit topics ready for Go/No-Go evaluation."

## Job Map

| Job Step | Goal | Current Pain |
|----------|------|-------------|
| Define | Determine which solicitation sources to monitor | Manually remembers to check dodsbirsttr.mil; forgets other sources |
| Locate | Find all open topics across relevant sources | 300-500 topics per DoD cycle alone; manual browsing |
| Prepare | Filter and pre-screen topics for relevance | Reads titles and descriptions one by one; 2-6 hours per cycle |
| Confirm | Verify match against company capabilities, certs, clearance | Mental cross-reference against memory; misses hidden requirements |
| Execute | Score and rank topics by fit | No scoring system; gut feel + ad hoc notes |
| Monitor | Track topic status and deadlines | Spreadsheet or memory; deadlines slip |
| Modify | Adjust priorities as new information arrives | Re-scan entire list; no incremental update |
| Conclude | Select topics for proposal pursuit | Decision often made under time pressure with incomplete analysis |

## Opportunity Scoring

Scoring method: Importance + Max(0, Importance - Satisfaction). Each on 1-10 scale. Max score = 20.
Importance and satisfaction estimated from domain analysis, competitive landscape, and user behavior patterns.

| # | Opportunity (Outcome Statement) | Imp | Sat | Score | Priority |
|---|--------------------------------|-----|-----|-------|----------|
| O1 | Minimize time to identify all relevant open topics from DoD SBIR/STTR | 10 | 2 | 18 | Extremely Underserved |
| O2 | Minimize likelihood of missing a high-fit topic due to terminology mismatch | 9 | 1 | 17 | Extremely Underserved |
| O3 | Minimize effort to verify eligibility requirements (clearance, STTR, Phase II prior work) | 8 | 2 | 14 | Extremely Underserved |
| O4 | Minimize time from topic identification to scored Go/No-Go recommendation | 9 | 3 | 15 | Extremely Underserved |
| O5 | Minimize likelihood of pursuing a topic with hidden disqualifiers | 8 | 3 | 13 | Underserved |
| O6 | Minimize effort to track deadlines across multiple open topics | 6 | 4 | 8 | Moderately Underserved |
| O7 | Minimize effort to monitor additional sources beyond DoD (NASA, DoE, NIH) | 5 | 2 | 8 | Moderately Underserved |
| O8 | Minimize effort to share topic shortlist with teaming partners | 4 | 5 | 4 | Overserved |

## Top 3 Opportunities (Score > 8)

### O1: Automated Topic Discovery (Score: 18)

**Why it matters**: The core bottleneck. 300-500 topics per cycle, each requiring manual reading. Automation reduces hours to minutes.

**Solution Ideas**:
- A. Fetch topic data from DoD SBIR/STTR Topics App and match against company profile capabilities
- B. Download and parse the full BAA PDF, extract all topics, batch-score against profile
- C. Use SBIR.gov open data / API to retrieve structured topic metadata

### O2: Semantic Matching Beyond Keywords (Score: 17)

**Why it matters**: Keyword matching alone misses topics that use different terminology for the same technical area. "Directed energy" vs "high-energy laser" vs "DEW" vs "counter-UAS energy weapon."

**Solution Ideas**:
- A. LLM-based semantic matching: use Claude to assess capability-to-topic alignment beyond keyword overlap
- B. Domain-specific synonym expansion: build a mapping of SBIR technical area terminology
- C. Two-pass matching: fast keyword filter, then LLM semantic analysis on candidates

### O3: Automatic Eligibility Screening (Score: 14)

**Why it matters**: Hidden requirements (clearance, STTR institution, prior Phase I) waste time when discovered late. Automated screening surfaces disqualifiers immediately.

**Solution Ideas**:
- A. Extract requirement indicators from topic text (clearance level, STTR flag, Phase II prerequisites) and compare against company profile
- B. Use the existing five-dimension fit scoring model (already implemented in sbir-topic-scout) on each discovered topic
- C. Flag-only mode: do not score, just surface likely disqualifiers for quick human triage

## Opportunity Solution Tree (Visual)

```
Desired Outcome: Minimize time from "cycle opens" to "ranked shortlist"
  |
  +-- O1: Automated Topic Discovery (18)
  |     +-- [A] Fetch from DoD Topics App + profile matching  <-- SELECTED
  |     +-- [B] Parse full BAA PDF, batch-score
  |     +-- [C] SBIR.gov open data / API
  |
  +-- O2: Semantic Matching Beyond Keywords (17)
  |     +-- [A] LLM semantic matching (Claude)  <-- SELECTED
  |     +-- [B] Domain synonym expansion
  |     +-- [C] Two-pass: keyword filter + LLM analysis  <-- SELECTED
  |
  +-- O3: Automatic Eligibility Screening (14)
  |     +-- [A] Extract requirements + compare to profile  <-- SELECTED
  |     +-- [B] Reuse five-dimension fit scoring model
  |     +-- [C] Flag-only mode for quick triage
  |
  +-- O4: Fast Go/No-Go Scoring (15)
  |     +-- [A] Batch apply fit scoring to all matched topics
  |     +-- [B] Single ranked output with per-topic recommendation
  |
  +-- O5: Disqualifier Detection (13)
  |     +-- [A] Hard-stop rules: no SAM.gov, wrong clearance, no STTR partner
  |     +-- [B] "Cannot pursue" vs "needs attention" classification
  |
  +-- O6: Deadline Tracking (8)
  |     +-- [A] Sort by deadline, flag critical/warning
  |
  +-- O7: Multi-Source Monitoring (8)
  |     +-- [A] NASA NSPIRES integration
  |     +-- [B] Grants.gov integration
  |
  +-- O8: Sharing (4) -- DEPRIORITIZED
```

## Selected Solution Approach

Combining the selected ideas from O1-O5:

1. **Data retrieval**: Fetch topic data from the DoD SBIR/STTR Topics App (primary source). The Topics App at dodsbirsttr.mil/topics-app/ provides a searchable interface. Investigation needed: whether structured data (API/JSON) is available, or if HTML scraping/manual download is required.

2. **Two-pass matching**: First pass uses keyword matching (company capabilities vs topic keywords/title/description) to reduce 300-500 topics to 20-50 candidates. Second pass uses LLM semantic analysis for nuanced alignment scoring.

3. **Profile-based eligibility screening**: Extract clearance requirements, STTR flags, Phase II prerequisites from topic text. Compare against company profile certifications, research institution partners, and past performance.

4. **Batch fit scoring**: Apply the existing five-dimension scoring model (from fit-scoring-methodology) to each candidate topic. Produce a composite score and recommendation (go/evaluate/no-go) per topic.

5. **Ranked output**: Present topics sorted by composite score (descending), then deadline (ascending). Include per-dimension breakdown, rationale, and disqualifier flags.

## Data Source Investigation

### DoD SBIR/STTR Topics App (dodsbirsttr.mil/topics-app/)

**What we know**:
- Public web application listing all DoD SBIR/STTR topics
- Searchable by keyword, agency, phase, status
- Each topic has: ID, title, description, agency, phase, keywords, technology areas, deadline
- Used by the entire DoD SBIR community

**What we need to determine**:
- Is there a public API? (Technical feasibility risk -- A1)
- Can topics be downloaded in structured format (CSV, JSON)?
- Is scraping permissible and practical?
- Rate limiting or access restrictions?

**Fallback approaches**:
- Manual download: User downloads topic list or individual topic pages, plugin processes them locally
- Hybrid: Plugin assists with search queries, user copies results, plugin scores them
- BAA PDF parsing: Download the full BAA document, extract topics from it

### Other Sources (Deferred to v2)
- SBIR.gov: aggregator, may have API access
- NASA NSPIRES: separate interface, different format
- Grants.gov: very broad, SBIR is a subset

## Gate G2 Evaluation

| Criteria | Target | Actual | Status |
|----------|--------|--------|--------|
| Opportunities identified | 5+ distinct | 8 | PASS |
| Top scores | >8 / max 20 | O1=18, O2=17, O4=15, O3=14, O5=13 | PASS |
| Job step coverage | 80%+ | 7/8 steps addressed (Modify partially via re-running) | PASS |
| Strategic alignment | Confirmed | Directly extends existing topic-scout + company-profile capabilities | PASS |

### G2 Decision: PROCEED to Phase 3 (Solution Testing)

Top opportunities are all extremely or significantly underserved. The solution approach leverages existing infrastructure (fit scoring model, company profile) and addresses the core bottleneck (manual topic browsing). The primary technical risk (A1: data access) needs spike validation.
