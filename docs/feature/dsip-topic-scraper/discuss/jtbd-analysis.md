# JTBD Analysis: DSIP Topic Scraper

## Job Classification

**Job Type**: Brownfield improvement (Job 2) -- integrating DSIP scraping into an existing solicitation discovery workflow.

**Workflow**: `[research] -> discuss -> design -> distill -> baseline -> roadmap -> split -> execute -> review`

Discovery is needed because the scraper introduces new data sources, a new execution model (headless browser), and new integration points with the existing topic-scout agent.

---

## Job Story 1: Comprehensive Topic Discovery

**When** I am starting a new proposal cycle and need to find all open SBIR/STTR topics from DoD agencies,
**I want to** automatically retrieve every current topic from the DSIP portal with its full metadata,
**so I can** evaluate all available opportunities without manually browsing an Angular web app that is difficult to search.

### Functional Job
Retrieve all open and pre-release DoD SBIR/STTR topics with structured metadata (ID, title, agency, phase, dates, status).

### Emotional Job
Feel confident that I have not missed any relevant topic because the portal's clunky pagination or JavaScript rendering hid it from me.

### Social Job
Be seen as thorough and systematic in opportunity identification -- no one on the team questions whether we missed a good topic.

### Forces Analysis
- **Push**: The DSIP portal is an Angular SPA that is slow to browse, requires clicking through paginated tables, and does not export data. Manually reviewing 100+ topics takes hours.
- **Pull**: A single command that fetches all topics with metadata and outputs structured JSON that can be scored automatically.
- **Anxiety**: What if the scraper breaks when DSIP changes their UI? What if we miss topics because the API changes its response format?
- **Habit**: Currently, Phil browses the portal manually or relies on email alerts from SBIR.gov which often arrive late.

### Assessment
- Switch likelihood: HIGH -- the manual process is painful and error-prone
- Key blocker: Reliability anxiety (will the scraper keep working?)
- Key enabler: Strong push from manual browsing frustration
- Design implication: Scraper must fail gracefully with clear error messages about what went wrong and what data was still captured.

---

## Job Story 2: Topic Detail Enrichment

**When** I have identified a list of potentially relevant topics from DSIP and need to evaluate them more deeply,
**I want to** automatically retrieve the full description, submission instructions, component-specific instructions, and Q&A for each topic,
**so I can** make informed go/no-go decisions without clicking into each individual topic page.

### Functional Job
Enrich topic metadata with detailed content: full description text, phase expectations, submission instructions, component instructions, and all Q&A threads.

### Emotional Job
Feel prepared and well-informed when making the go/no-go decision -- every piece of available information is at my fingertips.

### Social Job
Present a thorough, data-backed assessment to teammates or management when recommending which topics to pursue.

### Forces Analysis
- **Push**: Clicking into each topic on DSIP to read the description, then checking Q&A, then checking instructions is tedious. For 20+ potentially relevant topics, this is hours of clicking.
- **Pull**: All topic details in one JSON file, ready for the fit-scoring pipeline and agent consumption.
- **Anxiety**: Will the scraper correctly capture long descriptions with special characters, tables, and formatting? Will Q&A data be complete?
- **Habit**: Currently reads each topic page individually, copies key paragraphs into notes.

### Assessment
- Switch likelihood: HIGH
- Key blocker: Data completeness anxiety
- Key enabler: Time savings on per-topic investigation
- Design implication: Output must include completeness indicators (description captured: yes/no, Q&A count matches expected).

---

## Job Story 3: Seamless Pipeline Integration

**When** the DSIP scraper has captured topic data and I want to score topics against my company profile,
**I want to** have the scraped data flow directly into the existing `/solicitation find` scoring pipeline,
**so I can** go from "fetch topics" to "ranked recommendations" in one continuous workflow.

### Functional Job
Produce output in a format that the topic-scout agent and fit-scoring service can consume directly, with no manual data transformation.

### Emotional Job
Feel that the tooling is cohesive and well-integrated -- not a collection of disconnected scripts that require manual glue.

### Social Job
Demonstrate a professional, automated proposal discovery pipeline rather than ad hoc scripts.

### Forces Analysis
- **Push**: The prototype scraper outputs raw JSON that requires manual loading and interpretation. No connection to scoring.
- **Pull**: End-to-end automated pipeline: scrape -> filter -> score -> rank -> present.
- **Anxiety**: Will the scraper output format match what the scoring service expects? What if field names or data shapes change?
- **Habit**: Currently, solicitation-find works from BAA PDF files or manual input, not from scraped API data.

### Assessment
- Switch likelihood: HIGH (foundational improvement to existing workflow)
- Key blocker: Format compatibility anxiety
- Key enabler: Existing scoring pipeline already accepts structured TopicInfo
- Design implication: Scraper output must conform to the TopicInfo schema or include a clear adapter layer.

---

## 8-Step Job Map: Discover DSIP Topics

| Step | Description | User Need | Risk |
|------|-------------|-----------|------|
| 1. Define | Decide to search for DSIP topics for current solicitation cycle | Know which cycle/status to search (Open, Pre-Release) | Wrong filter produces stale results |
| 2. Locate | Connect to DSIP portal or API endpoint | Reliable access to DSIP data source | Portal down, API endpoint changed |
| 3. Prepare | Configure search parameters (agency, status, solicitation ID) | Set filters before executing | Misconfigured filters miss relevant topics |
| 4. Confirm | Verify scraper has access and can reach the portal | Connection validated before long-running scrape | Silent failure wastes time |
| 5. Execute | Run the scraper to fetch all matching topics | Complete data capture with progress indication | Timeout, partial capture, malformed data |
| 6. Monitor | Track scraping progress (topics found, pages processed) | Know how far along the scrape is and whether it is working | No feedback during 2-5 minute scrape |
| 7. Modify | Handle errors, retry failed topics, adjust filters | Recover from partial failures without full restart | Retry logic absent, forcing full re-scrape |
| 8. Conclude | Save results, verify completeness, hand off to scoring | Confidence that capture is complete and data is usable | Missing topics not detected, corrupt output |

---

## Outcome Statements

1. Minimize the time it takes to discover all open DoD SBIR/STTR topics (currently hours of manual browsing)
2. Minimize the likelihood of missing a relevant topic due to portal pagination or rendering issues
3. Minimize the time between topic data capture and fit-score ranking
4. Maximize the completeness of per-topic detail (description, instructions, Q&A)
5. Minimize the effort required to recover from a partial scrape failure
6. Maximize confidence that the scraped data accurately represents what is on the DSIP portal
