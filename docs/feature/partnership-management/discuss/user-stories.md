<!-- markdownlint-disable MD024 -->

# User Stories: Partnership Management

All stories trace to JTBD analysis in `jtbd-analysis.md` and journey artifacts.
Stories are sized for agent/skill markdown implementation via /nw:forge.

---

## US-PM-001: Partner Profile Builder Agent

### Problem

Phil Santos is an engineer who works with research institution partners (CU Boulder, NDSU, SWRI) on STTR proposals. He finds that every proposal agent (strategist, writer, solution shaper) produces generic teaming content because partner capabilities are stored as a flat `string[]` with only names -- no capabilities, personnel, facilities, or past collaborations. Today he manually injects partner specifics into every section of every partnered proposal.

### Who

- SBIR proposal writer | Has existing research institution partnerships | Wants AI-assisted suggestions that reflect the actual combined team strengths

### Solution

A partner profile builder agent (mirroring the existing company profile builder) that captures structured partner data through conversational interview with web research pre-population, validates against a partner profile schema, and saves to `~/.sbir/partners/{slug}.json`.

### Domain Examples

#### 1: Happy Path -- Phil adds SWRI as a new partner

Phil Santos runs `/proposal partner-setup`, selects "new", and enters "Southwest Research Institute". The agent searches the web, finds SWRI's 200+ SBIR awards, research areas (intelligent systems, autonomy), and key personnel (Dr. Rebecca Chen). Phil confirms the research findings, refines capabilities to "intelligent systems, autonomy, sensor fusion, applied ML", adds Dr. Rebecca Chen as Co-PI with expertise keywords, and lists SWRI's 6-DOF motion sim lab and RF anechoic chamber. The preview shows the SWRI profile alongside a combined capability analysis with Phil's company. Phil saves. The profile is written to `~/.sbir/partners/swri.json`.

#### 2: Edge Case -- Phil updates CU Boulder's profile after a new hire

Phil runs `/proposal partner-setup`, sees CU Boulder listed, selects "update". The agent loads the existing profile. Phil adds a new key personnel entry: "Dr. James Rivera, Senior Researcher, underwater robotics, acoustic sensing". The agent merges the addition, re-validates, and saves. The existing profile is backed up to `.bak` before overwrite.

#### 3: Error Path -- Phil cancels mid-interview for NDSU

Phil starts a partner setup for NDSU but realizes he needs to check some details with the NDSU contact first. He says "cancel". The agent confirms: "Partner profile creation cancelled. No files written or modified." No partial file exists.

### UAT Scenarios (BDD)

#### Scenario: Create new partner profile via interview with web research

Given Phil Santos has a company profile at ~/.sbir/company-profile.json
And no partner profile exists for "SWRI"
When Phil runs "/proposal partner-setup" and creates a profile for SWRI
And the agent pre-populates from web research (200+ SBIR awards, intelligent systems research area)
And Phil provides capabilities "intelligent systems, autonomy, sensor fusion, applied ML"
And Phil adds Dr. Rebecca Chen as Co-PI with expertise "autonomous navigation, sensor fusion"
And Phil adds facilities "6-DOF motion sim lab, RF anechoic chamber"
Then the preview shows the SWRI profile with all provided data
And the preview shows a combined capability analysis with Phil's company
And the profile saves to ~/.sbir/partners/swri.json
And the profile passes schema validation

#### Scenario: Update existing partner profile preserves data

Given a partner profile exists for "CU Boulder" with 2 key personnel entries
When Phil selects "update" and adds a third key personnel entry
Then the existing 2 key personnel entries are preserved
And the new entry is added
And the old profile is backed up to .bak before overwrite

#### Scenario: Preview shows combined capability analysis

Given Phil has completed interview sections for SWRI with capabilities "intelligent systems, autonomy, sensor fusion, applied ML"
And Phil's company has capabilities "directed energy, RF engineering, machine learning"
When the tool displays the preview
Then the combined analysis shows overlap as "machine learning / applied ML"
And the combined analysis shows unique to Phil as "directed energy, RF engineering"
And the combined analysis shows unique to SWRI as "autonomy, sensor fusion, intelligent systems"

#### Scenario: Cancel at any point writes no files

Given Phil is in the middle of partner interview for NDSU
When Phil says "cancel"
Then the tool confirms no files were written or modified
And no partner profile file exists for NDSU

#### Scenario: Validation failure blocks save with actionable error

Given Phil attempts to save a partner profile with empty capabilities
When the tool validates the profile
Then the tool reports "capabilities: must have at least 1 keyword"
And the tool returns to preview for correction
And no file is written

### Acceptance Criteria

- [ ] Partner profile interview covers 6 sections: basics, capabilities, key personnel, facilities, past collaborations, STTR eligibility
- [ ] Web research pre-populates draft data for known institutions
- [ ] Preview shows combined capability analysis (company + partner)
- [ ] Schema validation runs before every save; invalid profiles are never written
- [ ] Cancel at any point writes no files (hard invariant)
- [ ] Overwrite protection: existing profiles trigger backup/update/cancel options

### Technical Notes

- New agent: `agents/sbir-partner-builder.md` (modeled on sbir-profile-builder)
- New skill: `skills/partner-builder/partner-domain.md` (field-by-field interview guidance)
- Partner profiles stored at `~/.sbir/partners/{slug}.json` (one file per partner)
- Partner profile schema extends company profile pattern: capabilities[], key_personnel[], plus facilities[], past_collaborations[], sttr_eligibility
- Depends on: company profile existing for combined analysis (soft dependency -- setup works without it but skips combined preview)

---

## US-PM-002: Partnership-Aware Topic Scoring

### Problem

Phil Santos is an engineer who scans SBIR/STTR solicitations with `/solicitation-find`. Currently, the STTR scoring dimension is binary (0.50 if partners listed, 1.0 if established partner) and partner capabilities are invisible to the SME dimension. This means STTR topics where the combined team is strong but Phil's company alone is marginal appear as "EVALUATE" when they should be "GO". Phil mentally adjusts scores knowing "CU Boulder covers the RF side" -- but this informal adjustment is not captured and not shareable.

### Who

- SBIR proposal writer | Has partner profiles on file | Scanning solicitations for best-fit topics including STTR

### Solution

Enhance topic-scout agent to load partner profiles and compute side-by-side scoring: company-only vs. company+partner. Display both columns with a delta, highlighting topics elevated by the partnership.

### Domain Examples

#### 1: Happy Path -- Partnership elevates STTR topic from EVALUATE to GO

Phil Santos has CU Boulder on file with capabilities "autonomous navigation, underwater acoustics, sensor fusion". He runs `/solicitation-find` against STTR topic N244-012 "Autonomous UUV Navigation". Company-only scores 0.56 (EVALUATE). Partnership score with CU Boulder is 0.82 (GO). The delta column shows +0.26, with the SME dimension gaining +0.33 from CU Boulder's acoustics expertise. Phil would have passed on this topic without the partnership view.

#### 2: Edge Case -- Partnership has minimal impact on SBIR topic

Phil scans SBIR topic AF243-001 "Compact Directed Energy". This is Phil's core competency. CU Boulder's capabilities (navigation, acoustics) do not match. Partnership scoring shows +0.02 delta. The tool notes: "Partnership has minimal impact on this topic. Consider pursuing solo."

#### 3: Error Path -- No partner profile exists for STTR topic

Phil scores STTR topic N244-012 but has no partner profiles on file. STTR dimension scores 0.0. The tool prompts: "STTR topic -- no partner profiles found. STTR score: 0.0. Run /proposal partner-setup to create a partner profile."

### UAT Scenarios (BDD)

#### Scenario: Display company-only and partnership scoring columns

Given Phil has a partner profile for CU Boulder
And STTR topic N244-012 requires "autonomous navigation, underwater sensing"
When Phil runs "/solicitation-find"
Then the scoring display shows a "You Only" column and a "+ CU Boulder" column and a "Delta" column
And the STTR dimension shows 0.50 (solo) vs 1.00 (partnership)

#### Scenario: Partnership elevates recommendation from EVALUATE to GO

Given topic N244-012 scores 0.56 composite for Phil alone (EVALUATE)
And the combined score with CU Boulder is 0.82 (GO)
When Phil views the scoring results
Then the tool displays "Partnership elevated this topic from EVALUATE to GO"
And the tool lists the capabilities that drove the elevation

#### Scenario: Minimal partnership impact noted for non-matching topic

Given SBIR topic AF243-001 requires "directed energy, power systems, thermal management"
And CU Boulder's capabilities do not overlap
When Phil views partnership scoring
Then the Delta column shows less than +0.05 total
And the tool notes "Partnership has minimal impact on this topic"

#### Scenario: Missing partner profile shows STTR warning

Given no partner profiles exist
And Phil scores an STTR topic
When the tool computes the STTR dimension
Then the STTR score is 0.0
And the tool suggests "/proposal partner-setup"

### Acceptance Criteria

- [ ] Topic scoring shows both solo and partnership columns when partner profiles exist
- [ ] Delta column highlights score differences per dimension
- [ ] Partnership SME score uses union of company + partner capability keywords
- [ ] Partnership STTR score reflects partner institution type validation
- [ ] Recommendation elevation (e.g., EVALUATE to GO) is explicitly noted
- [ ] Graceful fallback: no partner profiles = current behavior (solo scoring only)

### Technical Notes

- Modifies: `agents/sbir-topic-scout.md` and `skills/topic-scout/fit-scoring-methodology.md`
- Partner profiles read from `~/.sbir/partners/*.json` via filesystem glob
- Combined SME: union of `capabilities` + `key_personnel.expertise` from both profiles
- Combined STTR: validates partner `type` matches STTR-qualifying institution types
- Depends on: US-PM-001 (partner profiles must exist for this to activate)

---

## US-PM-003: Partnership-Aware Strategy Brief (Teaming Section)

### Problem

Phil Santos is an engineer who generates strategy briefs with `/proposal-wave-strategy`. The strategist currently produces a generic teaming section that says "will partner with a research institution" without naming personnel, facilities, or capability complementarity. Phil manually rewrites the teaming section every time, pulling partner details from memory and past proposals. This is the most tedious section to write because it requires precise attribution (naming Co-PI, listing specific facilities, quantifying work split).

### Who

- SBIR proposal writer | Has a partner profile on file | Generating strategy brief for a partnered proposal

### Solution

Enhance the strategist agent to read the designated partner profile and auto-generate the teaming section with partnership structure, capability complementarity matrix, work split with named personnel, and facility listing.

### Domain Examples

#### 1: Happy Path -- Auto-generated teaming section with CU Boulder

Phil Santos is generating a strategy brief for STTR topic N244-012 with CU Boulder as partner. The strategist reads the CU Boulder profile and generates: "Acme Defense (prime) + CU Boulder (university). CU Boulder performs 35% of Phase I work. Capability complementarity: CU Boulder covers autonomous navigation and underwater acoustics; Acme covers RF engineering and system integration. Co-PI: Dr. Sarah Kim (autonomous nav, underwater acoustics). CU Boulder facilities: underwater acoustics lab, GPU compute cluster."

#### 2: Edge Case -- Strategy brief without partner (SBIR topic)

Phil generates a strategy brief for SBIR topic AF243-001 without a partner. The strategist produces a standard teaming section: "No research institution partner required for SBIR Phase I. Subcontracting to be determined during Phase I execution."

#### 3: Error Path -- Partner profile missing a field used in teaming

Phil generates a strategy brief for a partner whose profile has no facilities listed. The strategist generates the teaming section but notes: "Facilities: [not provided in partner profile -- update via /proposal partner-setup]". The brief is not blocked; the gap is flagged.

### UAT Scenarios (BDD)

#### Scenario: Teaming section auto-generated from partner profile

Given Phil has selected approach "Acoustic-Inertial Fusion" for topic N244-012
And CU Boulder is the designated partner with Co-PI "Dr. Sarah Kim"
And CU Boulder has facilities "underwater acoustics lab, GPU compute cluster"
When Phil runs "/proposal-wave-strategy"
Then the strategy brief teaming section names "Dr. Sarah Kim" as Co-PI
And the teaming section lists CU Boulder facilities
And the teaming section shows a capability complementarity matrix
And the work split percentage matches the approach brief

#### Scenario: Teaming section cites partner profile as source

Given the strategist generates a teaming section using CU Boulder data
When Phil reviews the strategy brief
Then the teaming section includes "[Source: cu-boulder.json + company-profile.json]"
And all personnel names match the partner profile exactly

#### Scenario: Missing partner data flagged but not blocking

Given the partner profile for CU Boulder has no facilities listed
When the strategist generates the teaming section
Then the facilities subsection notes "[not provided in partner profile]"
And the rest of the teaming section generates normally

#### Scenario: Non-partnered proposal has standard teaming section

Given no partner is designated for SBIR topic AF243-001
When Phil runs "/proposal-wave-strategy"
Then the teaming section uses standard non-partnered language
And no partner-specific content appears

### Acceptance Criteria

- [ ] Teaming section auto-generated from partner profile when partner designated
- [ ] Personnel names match partner profile exactly (no paraphrasing)
- [ ] Capability complementarity matrix shows both entities side by side
- [ ] Work split percentages consistent with approach brief
- [ ] Source attribution cites partner profile file
- [ ] Missing partner fields flagged, not blocking
- [ ] Non-partnered proposals retain current behavior

### Technical Notes

- Modifies: `agents/sbir-strategist.md` and `skills/strategist/sbir-strategy-knowledge.md`
- Strategist must read `~/.sbir/partners/{slug}.json` when partner designated in proposal state
- Teaming section becomes a new dimension (7th) in the strategy brief alongside technical_approach, trl, teaming, phase_iii, budget, risks
- Depends on: US-PM-001 (partner profiles), proposal state tracking which partner is designated

---

## US-PM-004: Partnership-Aware Approach Generation

### Problem

Phil Santos is an engineer who uses `/proposal-shape` to generate candidate technical approaches. Currently the solution shaper only considers Phil's company capabilities when scoring approaches. For partnered proposals, approaches that leverage the combined team's strengths (e.g., CU Boulder's acoustics expertise + Phil's RF engineering) are not surfaced. Phil manually identifies these combinations, losing the structured scoring benefit.

### Who

- SBIR proposal writer | Has a partner profile on file | Selecting a technical approach for a partnered proposal

### Solution

Enhance the solution shaper agent to load the designated partner profile, generate approaches that leverage combined capabilities, include work split recommendations per approach, and flag approaches that do not leverage the partner.

### Domain Examples

#### 1: Happy Path -- Approach leverages CU Boulder's acoustics expertise

Phil is selecting an approach for STTR topic N244-012 with CU Boulder. The solution shaper generates "Acoustic-Inertial Fusion" which scores 8.2/10 by leveraging CU Boulder's acoustic signal processing (Dr. Sarah Kim) + Phil's RF engineering. Work split: CU Boulder leads acoustic algorithms (40%), Phil leads system integration (60%). The approach names CU Boulder's underwater acoustics lab for testing.

#### 2: Edge Case -- No approach strongly leverages the partner

Phil is selecting an approach for a cybersecurity topic with CU Boulder (acoustics/navigation expertise). The solution shaper generates 3 approaches based on Phil's capabilities. All approaches show weak partnership utilization. The tool flags: "None of the generated approaches strongly leverage CU Boulder. Consider pursuing this topic solo or with a cybersecurity-focused partner."

#### 3: Error Path -- STTR approach below 30% partner allocation

The solution shaper generates an approach where the partner's role is only 20% of the effort. The tool flags: "This approach allocates 20% to CU Boulder. STTR requires research institution to perform >= 30% of Phase I work. Adjust the work split or choose a different approach."

### UAT Scenarios (BDD)

#### Scenario: Approaches reference partner capabilities and name personnel

Given Phil has selected topic N244-012 and partner CU Boulder
When Phil runs "/proposal-shape"
Then at least one approach references CU Boulder's capabilities by keyword
And the recommended approach includes a work split with CU Boulder
And the recommended approach names specific CU Boulder facilities

#### Scenario: Weak partnership utilization flagged

Given Phil has selected a cybersecurity topic with partner CU Boulder
When Phil runs "/proposal-shape"
Then the tool notes that generated approaches do not strongly leverage CU Boulder
And the tool suggests considering a different partner or the SBIR track

#### Scenario: STTR minimum partner percentage enforced

Given Phil is working on an STTR proposal with CU Boulder
When the tool generates approach work splits
Then every approach allocates at least 30% to CU Boulder
And approaches that cannot reach 30% are flagged as STTR non-compliant

### Acceptance Criteria

- [ ] Approach generation uses combined capability set (company + partner)
- [ ] Each approach shows work split percentages
- [ ] Approaches reference specific partner capabilities, personnel, and facilities
- [ ] Weak partnership utilization explicitly flagged
- [ ] STTR 30% minimum enforced on work splits
- [ ] Non-partnered proposals retain current behavior

### Technical Notes

- Modifies: `agents/sbir-solution-shaper.md` and `skills/solution-shaper/approach-evaluation.md`
- Solution shaper must read partner profile alongside company profile
- Work split percentages stored in approach-brief.md and consumed downstream by strategist and writer
- Depends on: US-PM-001 (partner profiles), proposal state tracking designated partner

---

## US-PM-005: New Partner Readiness Screening

### Problem

Phil Santos is an engineer who has been burned by a partner backing out after weeks of meetings and a facility tour (Q8 failure case). Currently there is no structured way to assess a potential new partner's commitment, bandwidth, and fit before investing significant coordination time. Phil discovers problems too late -- after 14 calendar days (Q6) of information exchange.

### Who

- SBIR proposal writer | Evaluating a new potential research institution partner | Wants to detect red flags before heavy investment

### Solution

A lightweight screening command (`/proposal partner-screen`) that asks structured questions about the potential partner's readiness and produces a risk-assessed recommendation (proceed, caution, do not proceed) with concrete next steps.

### Domain Examples

#### 1: Happy Path -- SWRI screens as "Proceed with Caution"

Phil Santos is evaluating SWRI for STTR topic N244-012. He runs `/proposal partner-screen`. The tool asks about timeline commitment ("they said probably"), bandwidth ("not sure"), SBIR experience ("200+ awards"), POC assignment ("Dr. Rebecca Chen"), and scope agreement ("high level"). Result: PROCEED WITH CAUTION. Risks: soft timeline, unknown bandwidth. Suggested next steps: get explicit commitment, ask about competing proposals, draft preliminary work split.

#### 2: Edge Case -- All signals positive

Phil screens a new partner who has confirmed timeline, assigned a POC with direct email, has 50+ SBIR awards, and agreed on detailed scope. Result: PROCEED. All signals positive. Tool suggests moving directly to `/proposal partner-setup`.

#### 3: Error Path -- Critical red flags detected

Phil screens a potential partner who has no timeline commitment, no named POC ("someone in the proposals office"), and no prior SBIR experience. Result: DO NOT PROCEED. Three critical red flags. Tool references the Q8 risk pattern and suggests alternative partners.

### UAT Scenarios (BDD)

#### Scenario: Screening produces risk-assessed recommendation

Given Phil is evaluating SWRI for topic N244-012
And SWRI has strong SBIR experience and a named POC
And SWRI has a soft timeline commitment and unknown bandwidth
When Phil completes the screening questions
Then the recommendation is "PROCEED WITH CAUTION"
And the tool lists specific strengths and specific risks
And the tool suggests concrete next steps to resolve risks

#### Scenario: Clear proceed with all positive signals

Given all readiness signals are positive for a potential partner
When the screening completes
Then the recommendation is "PROCEED"
And the tool suggests proceeding directly to /proposal partner-setup

#### Scenario: Critical red flags produce do-not-proceed

Given a potential partner has no timeline commitment, no named POC, and no SBIR experience
When the screening completes
Then the recommendation is "DO NOT PROCEED"
And the tool lists critical red flags
And the tool references the historical pattern of partner dropout

#### Scenario: Capability fit included when topic provided

Given Phil provides topic N244-012 during screening
And SWRI capabilities overlap with topic requirements
When the screening includes capability assessment
Then the tool shows topic requirements alongside SWRI and Phil's capabilities
And the tool rates fit as HIGH/MEDIUM/LOW

#### Scenario: Save screening for later review

Given Phil has completed screening for SWRI
When Phil selects "save"
Then the screening results are saved to .sbir/partner-screenings/swri.json
And Phil can retrieve them later

### Acceptance Criteria

- [ ] Screening asks about 5 readiness signals: timeline, bandwidth, SBIR experience, POC assignment, scope agreement
- [ ] Each signal rated as OK, CAUTION, or UNKNOWN
- [ ] Recommendation is one of: PROCEED, PROCEED WITH CAUTION, DO NOT PROCEED
- [ ] Concrete next steps provided for CAUTION recommendations
- [ ] Optional capability fit assessment when topic provided
- [ ] Screening results saveable for later reference
- [ ] Screening transitions to /proposal partner-setup when user proceeds

### Technical Notes

- New command: `commands/proposal-partner-screen.md` (dispatches to sbir-partner-builder agent in screening mode, or a dedicated screening skill)
- Screening is conversational (not a form) -- the agent asks questions one at a time
- Results stored at `.sbir/partner-screenings/{slug}.json` (project-level, not global)
- Depends on: nothing (screening is standalone; does not require existing partner profiles)
- Screening findings carry forward to partner-setup if user proceeds

---

## US-PM-006: Partner Designation in Proposal State

### Problem

Phil Santos starts a new partnered proposal with `/proposal new`. Currently, proposal state tracks the topic but not which partner is designated. Every downstream agent must be told separately about the partner. When Phil switches between proposals, the partner context is lost and must be re-established.

### Who

- SBIR proposal writer | Starting or resuming a partnered proposal | Needs all agents to know which partner is designated

### Solution

Extend proposal state to track the designated partner. The partner is selected during `/proposal new` (for STTR topics) or can be associated later. All downstream agents read the designated partner from proposal state rather than requiring separate configuration.

### Domain Examples

#### 1: Happy Path -- Phil starts STTR proposal and designates CU Boulder

Phil runs `/proposal new` for STTR topic N244-012. The tool detects it is STTR and asks "Which partner for this proposal?" showing available partner profiles. Phil selects CU Boulder. The proposal state records `partner: "cu-boulder"`. All subsequent commands (`/proposal-shape`, `/proposal-wave-strategy`, `/proposal-draft`) automatically use the CU Boulder profile.

#### 2: Edge Case -- Phil starts STTR proposal with no partner profiles

Phil runs `/proposal new` for an STTR topic but has no partner profiles. The tool warns: "STTR topics require a research institution partner. No partner profiles found. Would you like to (s) set up a partner profile now, or (k) skip and add one later?"

#### 3: Error Path -- Phil changes partner mid-proposal

Phil designated CU Boulder but needs to switch to NDSU. He runs `/proposal partner-set NDSU`. The tool warns: "Changing partner mid-proposal. The approach brief and strategy brief reference CU Boulder. Regenerating these artifacts is recommended." Phil confirms. The partner designation updates.

### UAT Scenarios (BDD)

#### Scenario: STTR topic prompts partner selection during proposal new

Given partner profiles exist for CU Boulder and NDSU
And Phil runs "/proposal new" for STTR topic N244-012
When the tool detects the topic is STTR
Then the tool asks which partner to designate
And the tool shows available partner profiles
And Phil selects CU Boulder
And the proposal state records partner as "cu-boulder"

#### Scenario: All downstream agents use designated partner automatically

Given Phil has an active proposal with CU Boulder designated
When Phil runs "/proposal-shape"
Then the solution shaper reads the CU Boulder profile automatically
And Phil does not need to specify the partner again

#### Scenario: No partner profiles triggers setup prompt for STTR

Given no partner profiles exist
And Phil starts an STTR proposal
When the tool detects no partners available
Then the tool suggests /proposal partner-setup
And Phil can set up a partner or skip

#### Scenario: Partner change mid-proposal warns about stale artifacts

Given Phil has an active proposal with CU Boulder designated
And approach-brief.md references CU Boulder
When Phil changes the designated partner to NDSU
Then the tool warns that approach brief and strategy brief reference CU Boulder
And the tool suggests regenerating those artifacts

### Acceptance Criteria

- [ ] Proposal state includes designated partner slug (or null for non-partnered)
- [ ] STTR topics prompt partner selection during /proposal new
- [ ] All consuming agents (topic-scout, solution-shaper, strategist, writer) read partner from proposal state
- [ ] No partner profiles triggers helpful prompt, not error
- [ ] Partner change warns about stale artifacts

### Technical Notes

- Modifies: `skills/common/proposal-state-schema.md` (add `partner` field)
- Modifies: `commands/proposal-new.md` (add partner selection for STTR)
- New command: `commands/proposal-partner-set.md` (change designated partner)
- All consuming agents must check `proposal-state.json` for `partner` field
- Depends on: US-PM-001 (partner profiles must exist to be selectable)

---

## US-PM-007: Partnership Content in Proposal Drafting

### Problem

Phil Santos is an engineer drafting proposal sections with `/proposal-draft`. Currently, the writer agent produces sections without partner-specific content -- no named Co-PI, no partner facilities, no capability complementarity narrative. Phil manually inserts all partnership language, which is error-prone (inconsistent names, forgotten facilities) and time-consuming (every section needs partner context).

### Who

- SBIR proposal writer | Drafting sections for a partnered proposal | Needs draft text to reflect the actual partnership

### Solution

Enhance the writer agent to read the designated partner profile and strategy brief teaming section, incorporating partner names, capabilities, facilities, and work split into proposal draft sections where relevant.

### Domain Examples

#### 1: Happy Path -- Technical Approach section references CU Boulder

Phil is drafting the Technical Approach for STTR topic N244-012 with CU Boulder. The writer produces: "CU Boulder brings extensive experience in autonomous navigation and underwater acoustics through their underwater acoustics laboratory. Dr. Sarah Kim (Co-PI) will lead the acoustic algorithm development, leveraging her expertise in sensor fusion and signal processing." This text traces directly to the CU Boulder partner profile.

#### 2: Edge Case -- Non-partnered proposal drafts normally

Phil is drafting an SBIR proposal with no designated partner. The writer produces standard content without any partner references -- identical to current behavior.

#### 3: Error Path -- Partner profile has sparse data

Phil is drafting with a partner whose profile has no facilities and only one key personnel entry. The writer uses what is available (names the one person, references their expertise) but does not fabricate facilities or capabilities not in the profile.

### UAT Scenarios (BDD)

#### Scenario: Draft references partner by name with real personnel and facilities

Given a strategy brief exists with teaming section for CU Boulder
And CU Boulder's profile includes Dr. Sarah Kim and underwater acoustics lab
When Phil runs "/proposal-draft" for the Technical Approach section
Then the draft text names CU Boulder
And the draft text names Dr. Sarah Kim and her expertise
And the draft text mentions the underwater acoustics laboratory
And the draft text describes the work split consistent with the strategy brief

#### Scenario: Non-partnered proposal produces standard content

Given no partner is designated for the current proposal
When Phil runs "/proposal-draft"
Then the draft does not reference any partner institution
And behavior is identical to current non-partnership drafting

#### Scenario: Sparse partner data used without fabrication

Given the partner profile has only 1 key personnel and no facilities
When Phil runs "/proposal-draft"
Then the draft names the 1 available person with their expertise
And the draft does not fabricate facilities or additional personnel
And the draft notes where additional partner detail would strengthen the narrative

### Acceptance Criteria

- [ ] Draft sections reference partner name, personnel, facilities, and capabilities
- [ ] All partner references trace to partner profile data (no fabrication)
- [ ] Personnel names in draft match partner profile exactly
- [ ] Work split in draft matches strategy brief
- [ ] Non-partnered proposals retain current behavior
- [ ] Sparse partner data used as-is without fabrication

### Technical Notes

- Modifies: `agents/sbir-writer.md`
- Writer must read designated partner profile from proposal state
- Writer must read strategy brief teaming section as input
- Partnership content appears in Technical Approach, Management Plan, and relevant sections
- Depends on: US-PM-001 (partner profiles), US-PM-003 (strategy brief teaming section), US-PM-006 (partner designation)

---

## Story Dependency Map

```
US-PM-001 (Partner Profile Builder) -----> prerequisite for all others
     |
     +---> US-PM-006 (Partner Designation) ---> US-PM-002 (Scoring)
     |                                     ---> US-PM-004 (Approaches)
     |                                     ---> US-PM-003 (Strategy)
     |                                     ---> US-PM-007 (Drafting)
     |
     +---> US-PM-005 (Screening) -----> feeds into US-PM-001

US-PM-003 (Strategy) ---> US-PM-007 (Drafting) reads teaming section
US-PM-004 (Approaches) --> US-PM-003 (Strategy) reads work split
```

## Implementation Order (Recommended)

| Order | Story | Rationale |
|-------|-------|-----------|
| 1 | US-PM-001 | Foundation: all other stories depend on partner profiles |
| 2 | US-PM-006 | Wiring: enables all agents to know which partner is active |
| 3 | US-PM-002 | First visible value: partnership scoring during topic scanning |
| 4 | US-PM-004 | Pre-strategy: approach generation uses partner capabilities |
| 5 | US-PM-003 | Strategy: teaming section auto-generation |
| 6 | US-PM-007 | Drafting: partnership content in proposal text |
| 7 | US-PM-005 | Screening: standalone, lower priority, can be added anytime |

## MoSCoW Classification

| Must Have | Should Have | Could Have | Won't Have |
|-----------|------------|------------|------------|
| US-PM-001 (Profile Builder) | US-PM-002 (Scoring) | US-PM-005 (Screening) | O5: Partner Discovery/Matching (deferred) |
| US-PM-006 (Designation) | US-PM-004 (Approaches) | | O2: SOW/Budget Templates (deferred) |
| US-PM-003 (Strategy) | US-PM-007 (Drafting) | | |
