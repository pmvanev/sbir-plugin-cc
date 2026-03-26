# JTBD Analysis: Company Profile Enrichment

## Workflow Classification

**Job Type**: Improve Existing System (Brownfield)
**Rationale**: The company profile builder already exists (US-CPB-001 through US-CPB-005). This feature extends the existing onboarding flow by adding automated data retrieval from three federal APIs. The user's need (populate profile fields) is understood; the improvement is eliminating manual data entry by pulling from authoritative sources.

**Workflow**: research -> baseline -> roadmap -> split -> execute -> review

Research is complete (see `docs/research/company-profile-enrichment-apis.md`). This DISCUSS wave defines the requirements before DESIGN.

---

## Primary Persona

### Persona: Rafael Medina (extends existing)

**Who**: Small business technical founder at Radiant Defense Systems (23 employees) who pursues SBIR/STTR grants 3-5 times per year. Already the primary persona from the company-profile-builder feature.

**New Context for Enrichment**:
- Rafael has a SAM.gov account with an active entity registration (required for SBIR awards)
- He knows his UEI (DKJF84NXLE73) but cannot remember his exact CAGE code, NAICS codes, or which socioeconomic certifications his SAM.gov profile lists
- He has won 2 prior SBIR awards but is unsure whether his SBIR.gov listing is current
- He uses a free personal SAM.gov API key (obtained during entity registration)

**Pain Points**:
- "I have all this data in SAM.gov already but I'm retyping it into the profile builder. Why can't it just pull from my registration?" -> Job Step: Locate
- "I always forget whether we're listed as HUBZone or just applied. I end up guessing during profile setup and then the fit scoring is wrong." -> Job Step: Confirm
- "I had no idea we had 3 awards on SBIR.gov -- I only remembered 2. The third was from a subcontract our partner led." -> Job Step: Locate
- "Every year our SAM.gov registration renews and I forget to check whether the profile still matches." -> Job Step: Monitor

**Success Metrics**:
- Profile enrichment from UEI to confirmed data in under 3 minutes
- Zero manual entry for fields available from federal APIs
- User sees exactly what was pulled and from where (transparency)
- User confirms every enriched field before it enters the profile (no silent writes)

### Job Step Table

| Job Step | Goal | Desired Outcome |
|----------|------|-----------------|
| Define | Understand what enrichment can provide and what input is needed | Minimize time to understand what the system can auto-populate |
| Locate | Retrieve company data from SAM.gov, SBIR.gov, and USASpending | Minimize manual data entry by pulling from authoritative sources |
| Prepare | Organize API responses into profile schema fields | Minimize effort to map API data to profile structure |
| Confirm | Review enriched data, correct discrepancies, approve fields | Minimize likelihood of incorrect API data entering the profile |
| Execute | Merge confirmed enrichment data into the profile draft | Minimize time from "data reviewed" to "profile populated" |
| Monitor | Verify enrichment sources responded and data is current | Minimize likelihood of stale or missing API data going unnoticed |
| Modify | Handle API failures, partial data, user corrections | Minimize effort to recover from enrichment errors |
| Conclude | Confirm enriched profile is ready for fit scoring | Minimize doubt about data accuracy and completeness |

---

## Job Stories

### Job 4: Automated Profile Enrichment from Federal APIs

**When** I am creating or updating my company profile and the builder asks for SAM.gov details, certifications, and past performance,
**I want to** provide just my UEI and have the system pull the rest from federal databases,
**so I can** get an accurate, complete profile without retyping data that already exists in government systems.

#### Functional Job
Retrieve company registration data, certification flags, NAICS codes, SBIR award history, and federal award totals from SAM.gov, SBIR.gov, and USASpending.gov using the company's UEI.

#### Emotional Job
Feel that the system is working WITH government data I already provided, not asking me to duplicate it. Feel confident the data is authoritative because it came from the source of record.

#### Social Job
Present the company accurately using official government data rather than self-reported data that might contain errors or omissions.

#### Forces Analysis

**Demand-Generating**:
- **Push**: Rafael is in the middle of the profile interview (US-CPB-001). The builder asks for his CAGE code, NAICS codes, socioeconomic certifications, and past performance. He has to minimize the builder, open SAM.gov in a browser, log in, navigate to his entity page, and copy values one by one. For past performance, he opens SBIR.gov and searches for his company. This takes 15-20 minutes of tab-switching and copy-pasting, and he still misses his third SBIR award because it was under a slightly different company name.
- **Pull**: Type UEI once, watch the system pull legal name, CAGE, NAICS, certifications, 3 SBIR awards, and federal spending history in seconds. Review a summary, confirm, done. The data is authoritative -- it came from the same databases the government uses to verify eligibility.

**Demand-Reducing**:
- **Anxiety**: "What if the API pulls stale data? My SAM.gov registration just renewed and some fields might not be updated yet." / "What if it overwrites something I already entered correctly?" / "I don't want to store my SAM.gov API key somewhere insecure."
- **Habit**: "I've already typed this stuff before. It only took 10 minutes. Why set up an API key for a one-time thing?"

**Assessment**:
- Switch likelihood: HIGH -- the push is strong (15-20 min of copy-pasting from multiple government sites) and the pull is concrete (one input, multiple fields populated from authoritative sources).
- Key blocker: Anxiety about data accuracy and API key security. Must show source attribution for every field and store API key securely.
- Key enabler: The data comes from the same government databases that verify SBIR eligibility -- users already trust these sources.
- Design implication: Enrichment proposes, user confirms. Every field shows its source. API key stored in a separate, restricted-permission file.

---

### Job 5: Enrichment During Profile Update

**When** my SAM.gov registration renews or I win a new SBIR award,
**I want to** re-run enrichment against the APIs to detect what changed,
**so I can** update my profile with fresh data instead of guessing what is different.

#### Functional Job
Compare current profile data against fresh API responses and surface differences for user review.

#### Emotional Job
Feel that keeping the profile current is effortless, not a chore I keep deferring.

#### Social Job
Ensure fit scoring reflects the company's current status, not a stale snapshot from months ago.

#### Forces Analysis

**Demand-Generating**:
- **Push**: Rafael's SAM.gov registration renewed 2 months ago with updated NAICS codes (he added 541715 for R&D in physical sciences). His profile still has the old NAICS list. He won a Phase I from Navy last quarter but his profile shows only Air Force and DARPA. The topic scout is not matching him to Navy-relevant topics.
- **Pull**: Run enrichment during profile update, see a diff of what changed, confirm the updates. Two minutes instead of manually checking three government websites.

**Demand-Reducing**:
- **Anxiety**: "Will it overwrite changes I made manually that aren't in the APIs?" (e.g., capabilities keywords the user added beyond what SAM.gov lists)
- **Habit**: "I'll update it when I need to submit a proposal" -- deferred maintenance.

**Assessment**:
- Switch likelihood: MEDIUM-HIGH -- pull is strong for users who update profiles, but habit of deferral is real.
- Key blocker: Must not overwrite user-entered data that is not represented in APIs. Enrichment augments, never replaces.
- Design implication: Show a diff between current profile and API data. User selects which changes to accept. Manual entries preserved unless user explicitly replaces them.

---

### Job 6: SAM.gov API Key Setup

**When** I want to use profile enrichment but need a SAM.gov API key first,
**I want to** be guided through obtaining and storing the key with minimal friction,
**so I can** start enrichment without a research detour into SAM.gov's developer portal.

#### Functional Job
Obtain a free personal API key from SAM.gov and store it securely for the plugin to use.

#### Emotional Job
Feel that this one-time setup step is quick and well-explained, not a bureaucratic obstacle.

#### Social Job
N/A (private setup step).

#### Forces Analysis

**Demand-Generating**:
- **Push**: Rafael tries to enrich his profile but the system says "SAM.gov API key required." He does not know where to get one or how to store it.
- **Pull**: Clear instructions with the direct URL, a validation test, and secure storage -- done in 2 minutes.

**Demand-Reducing**:
- **Anxiety**: "Is this really free? Will I get rate-limited? Is it safe to give the plugin my API key?"
- **Habit**: "I'll just type the data manually instead of setting up an API key."

**Assessment**:
- Switch likelihood: HIGH if the setup is under 2 minutes with clear instructions. LOW if it feels bureaucratic.
- Key blocker: Perceived friction of obtaining the key.
- Design implication: Provide the exact URL. Validate the key with a test call. Store in `~/.sbir/api-keys.json` with restricted permissions. Never pass via command-line flags.

---

## Opportunity Scoring

| # | Outcome Statement | Imp. (%) | Sat. (%) | Score | Priority |
|---|-------------------|----------|----------|-------|----------|
| 1 | Minimize the time to populate profile fields available in federal APIs | 95 | 15 | 17.6 | Extremely Underserved |
| 2 | Minimize the likelihood of entering incorrect certification or registration data | 90 | 20 | 16.2 | Extremely Underserved |
| 3 | Minimize the effort to discover all SBIR awards (including ones the user forgot) | 80 | 10 | 14.8 | Underserved |
| 4 | Minimize the likelihood of enriched data silently overwriting correct user entries | 85 | 5 | 16.0 | Extremely Underserved |
| 5 | Minimize the time to set up SAM.gov API key for enrichment | 70 | 5 | 13.3 | Underserved |
| 6 | Minimize the time to detect profile staleness after SAM.gov renewal or new award | 75 | 10 | 14.0 | Underserved |
| 7 | Minimize the likelihood of proceeding with enrichment when an API is unavailable | 65 | 20 | 10.9 | Appropriately Served |

### Scoring Method
- Importance: estimated % of target users rating 4+ on 5-point scale (team estimate based on persona analysis)
- Satisfaction: estimated % satisfied with current approach (manual entry during profile interview)
- Score: Importance + max(0, Importance - Satisfaction)
- Data quality: team estimates (pre-build feature)

### Top Opportunities (Score >= 12)
1. Auto-populate from APIs (17.6) -- primary story: three-API enrichment cascade
2. Data accuracy from authoritative sources (16.2) -- cross-cutting: source attribution on every field
3. No silent overwrite of user data (16.0) -- cross-cutting: propose-and-confirm pattern
4. Discover forgotten SBIR awards (14.8) -- secondary: SBIR.gov award history retrieval
5. Detect profile staleness (14.0) -- tertiary: re-enrichment during update
6. API key setup friction (13.3) -- enabler: guided key setup with validation

### Appropriately Served Areas (Score 10-12)
1. Handle API unavailability (10.9) -- graceful degradation, existing error handling patterns

---

## Job-to-Story Mapping (Preview)

| Job Story | Primary User Stories |
|-----------|---------------------|
| Job 4: Automated Profile Enrichment | US-CPE-001 (Three-API Enrichment), US-CPE-002 (Enrichment Review and Confirm) |
| Job 5: Enrichment During Profile Update | US-CPE-003 (Re-Enrichment on Update) |
| Job 6: SAM.gov API Key Setup | US-CPE-004 (API Key Setup and Validation) |

All jobs share: source attribution, propose-and-confirm pattern, graceful API failure handling.
