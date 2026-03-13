# JTBD Analysis: Company Profile Builder

## Workflow Classification

**Job Type**: Build Something New (Greenfield)
**Rationale**: The company profile builder is a new capability that does not exist in the plugin. Users currently create `~/.sbir/company-profile.json` by hand. Discovery is required because the conversational interview pattern, document extraction, and validation workflows need to be defined from scratch.

**Workflow**: research -> discuss -> design -> distill -> baseline -> roadmap -> split -> execute -> review

---

## Primary Persona

### Persona: Rafael Medina

**Who**: Small business technical founder who pursues SBIR/STTR grants 3-5 times per year alongside engineering work.
**Demographics**:
- Technical proficiency: High (software/hardware engineer), low patience for administrative busywork
- Frequency: Sets up company profile once, updates occasionally (new hire, new certification, new past performance)
- Environment: CLI-native, works in terminal, comfortable with JSON but resents hand-crafting it
- Primary motivation: Get through setup fast so he can start evaluating solicitations

**Pain Points**:
- "I installed this plugin and immediately hit a wall -- it wants a company profile JSON and I have no idea what fields it expects" -> Job Step: Define
- "I have a capability statement PDF and a SAM.gov profile but I'm copy-pasting between documents and a JSON file" -> Job Step: Locate
- "I fat-fingered my CAGE code and the fit scoring was wrong for weeks before I noticed" -> Job Step: Confirm
- "Every time we win an award or hire someone, I forget to update the profile and the scoring gets stale" -> Job Step: Modify

**Success Metrics**:
- Profile created from first command to validated JSON in under 10 minutes
- Zero manual JSON editing required
- All schema fields populated or explicitly marked as not applicable
- Validation catches data errors before writing the file

### Job Step Table

| Job Step | Goal | Desired Outcome |
|----------|------|-----------------|
| Define | Understand what company information is needed and why | Minimize time to understand what the profile requires |
| Locate | Gather source documents and data (capability statements, SAM.gov, past proposals) | Minimize effort to identify where company data lives |
| Prepare | Organize gathered information into profile structure | Minimize manual data entry and reformatting |
| Confirm | Validate the profile is complete and accurate before writing | Minimize likelihood of writing incorrect data to the profile |
| Execute | Write the validated profile to ~/.sbir/company-profile.json | Minimize time from "data gathered" to "profile saved" |
| Monitor | Verify the profile works correctly with fit scoring | Minimize uncertainty about whether the profile is usable |
| Modify | Update the profile when company data changes (new hire, new award, new certification) | Minimize effort to keep the profile current |
| Conclude | Confirm the profile is complete and the plugin is ready for solicitation scouting | Minimize doubt about readiness to start evaluating topics |

---

## Job Stories

### Job 1: Initial Profile Creation

**When** I install the SBIR proposal plugin and want to start evaluating solicitations,
**I want to** provide my company information conversationally without hand-crafting JSON,
**so I can** get a validated company profile in place and move on to scoring topics within minutes.

#### Functional Job
Create a complete, schema-valid company profile from conversational input and source documents.

#### Emotional Job
Feel guided and confident during setup rather than overwhelmed by an unfamiliar JSON schema.

#### Social Job
Present the company accurately to the fit scoring engine so recommendations reflect true capabilities (not data entry errors).

#### Forces Analysis

**Demand-Generating**:
- **Push**: Rafael installed the plugin, ran `/sbir:proposal new`, and got a degraded scoring warning: "Company profile not found. Certifications and eligibility score 0.0." He now has to figure out the JSON schema from source code or documentation, hand-craft the file, and hope he got the nesting right. This is a 30-60 minute detour from his actual goal (evaluating a solicitation before the deadline).
- **Pull**: A conversational builder that asks plain-English questions ("What is your CAGE code?"), reads his capability statement PDF, and produces validated JSON would take 10 minutes and eliminate errors.

**Demand-Reducing**:
- **Anxiety**: "What if the builder misinterprets my documents and puts wrong capabilities in the profile?" / "What if it overwrites my existing profile without asking?"
- **Habit**: Rafael has already hand-crafted company-profile.json once for a previous tool. He knows the workaround and it "works" even though it is tedious and error-prone.

**Assessment**:
- Switch likelihood: HIGH -- the push is strong (degraded scoring is immediate and visible) and the pull is concrete (conversational vs. manual JSON).
- Key blocker: Anxiety about accuracy -- Rafael must be able to review and edit the profile before it is written.
- Key enabler: The degraded scoring warning creates an immediate, visible trigger.
- Design implication: The builder MUST show a preview and ask for confirmation before writing. It MUST NOT silently overwrite existing profiles.

---

### Job 2: Profile Update After Company Change

**When** my company wins a new SBIR award, hires a key person, or renews a certification,
**I want to** update just the changed section of my profile without re-entering everything,
**so I can** keep fit scoring accurate without repeating the full setup process.

#### Functional Job
Selectively update specific sections of an existing company profile.

#### Emotional Job
Feel that maintenance is lightweight, not a chore I keep deferring.

#### Social Job
Ensure the team's recent achievements are reflected in scoring so good opportunities are not missed.

#### Forces Analysis

**Demand-Generating**:
- **Push**: Rafael's company won a Phase I award from NASA three months ago but his profile still shows no NASA past performance. The topic scout scored a NASA Phase II topic as "evaluate" instead of "go" because past_performance was 0.0 for NASA. He missed the opportunity window.
- **Pull**: A targeted update command that lets him add one past performance entry or one key personnel record without touching the rest of the profile.

**Demand-Reducing**:
- **Anxiety**: "Will updating one field break the rest of the profile?"
- **Habit**: "I'll update it later" -- deferred maintenance is the natural human pattern.

**Assessment**:
- Switch likelihood: MEDIUM -- the push is real but delayed (missed opportunities are only visible in retrospect).
- Key blocker: Habit of deferral. The system needs to surface staleness.
- Design implication: The update flow should be surgical (target one section) and fast (under 2 minutes).

---

### Job 3: Profile Creation from Existing Documents

**When** I have a company capability statement, SAM.gov profile, and past proposal documents,
**I want to** point the builder at these sources and have it extract the relevant information,
**so I can** avoid re-typing information that already exists in structured or semi-structured form.

#### Functional Job
Extract company profile data from existing documents (PDFs, URLs, text files) and map it to the profile schema.

#### Emotional Job
Feel that the system is working WITH my existing documents, not asking me to duplicate effort.

#### Social Job
Trust that the extraction is accurate enough that I am not embarrassed by incorrect data in fit scoring.

#### Forces Analysis

**Demand-Generating**:
- **Push**: Rafael has a 4-page capability statement PDF that contains his company name, capabilities, certifications, key personnel, and past performance -- all the fields the profile needs. Manually transcribing this into JSON is tedious and error-prone.
- **Pull**: "Read this PDF and draft the profile" would save 20+ minutes and reduce transcription errors.

**Demand-Reducing**:
- **Anxiety**: "Will it hallucinate capabilities I don't have?" / "PDFs are messy -- will it parse correctly?"
- **Habit**: "I already typed most of this into a spreadsheet once."

**Assessment**:
- Switch likelihood: HIGH -- document extraction is the strongest pull for users who already have capability statements.
- Key blocker: Trust in extraction accuracy -- must show what was extracted and allow correction.
- Design implication: Extract-then-confirm pattern. Never write extracted data without human review.

---

## Opportunity Scoring

| # | Outcome Statement | Imp. (%) | Sat. (%) | Score | Priority |
|---|-------------------|----------|----------|-------|----------|
| 1 | Minimize the time to create a complete company profile from scratch | 95 | 10 | 18.1 | Extremely Underserved |
| 2 | Minimize the likelihood of writing incorrect data to the profile | 90 | 25 | 15.5 | Extremely Underserved |
| 3 | Minimize the effort to extract profile data from existing documents | 85 | 5 | 16.0 | Extremely Underserved |
| 4 | Minimize the time to update a single section of an existing profile | 75 | 20 | 13.0 | Underserved |
| 5 | Minimize the likelihood of proceeding with an incomplete profile | 80 | 15 | 14.5 | Underserved |
| 6 | Minimize the time to understand what fields the profile requires | 85 | 30 | 13.2 | Underserved |
| 7 | Minimize the likelihood of the profile becoming stale after company changes | 70 | 10 | 12.6 | Underserved |
| 8 | Minimize the effort to verify the profile works with fit scoring | 65 | 40 | 9.0 | Overserved |

### Scoring Method
- Importance: estimated % of target users rating 4+ on 5-point scale (team estimate based on persona analysis)
- Satisfaction: estimated % satisfied with current approach (manual JSON editing)
- Score: Importance + max(0, Importance - Satisfaction)
- Data quality: team estimates, N/A for user interviews (pre-build feature)

### Top Opportunities (Score >= 12)
1. Initial profile creation time (18.1) -- primary story: guided interview flow
2. Document extraction effort (16.0) -- secondary story: read capability statement / SAM.gov
3. Data accuracy before write (15.5) -- cross-cutting: preview and validation before save
4. Incomplete profile detection (14.5) -- cross-cutting: completeness check with field-level feedback
5. Schema understanding (13.2) -- embedded in interview flow (explain why each field matters)
6. Selective update (13.0) -- tertiary story: update single section
7. Staleness detection (12.6) -- could be deferred to later iteration

### Overserved Areas (Score < 10)
1. Verify profile works with fit scoring (9.0) -- existing topic scout already warns when profile missing; incremental improvement only

---

## Job-to-Story Mapping (Preview)

| Job Story | Primary User Stories |
|-----------|---------------------|
| Job 1: Initial Profile Creation | US-CPB-001 (Guided Interview), US-CPB-002 (Preview and Save) |
| Job 2: Profile Update | US-CPB-004 (Selective Section Update) |
| Job 3: Document Extraction | US-CPB-003 (Document/URL Extraction) |

All jobs share: validation before write, existing profile protection, schema completeness checking.
