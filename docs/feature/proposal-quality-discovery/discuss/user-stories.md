<!-- markdownlint-disable MD024 -->

# User Stories: Proposal Quality Discovery

Scope: Cross-cutting feature extending setup wizard, corpus librarian, writer, strategist, and reviewer agents with quality discovery intelligence.
All stories trace to JTBD analysis jobs JS-1 through JS-4.

---

## US-QD-001: Past Proposal Quality Rating

### Problem

Dr. Elena Vasquez is a PI who has submitted 12 SBIR proposals over 8 years. She finds it frustrating that the system tracks win/loss outcomes but never asks about writing quality -- a barely-won proposal with weak writing is treated the same as a strong win where evaluators praised the prose. Today she mentally categorizes her past proposals as "good writing" or "bad writing" but this knowledge lives in her head and is lost when she's not the PI on the next proposal.

### Who

- Principal Investigator | Has 5+ past proposals with known outcomes | Wants quality intelligence to transfer across proposal cycles

### Solution

A guided flow within quality discovery that walks through each past_performance entry in the company profile, asking the user to rate writing quality (weak/adequate/strong), describe what made it strong or weak, and capture any evaluator praise or criticism about writing specifically.

### Domain Examples

#### 1: Happy Path -- Elena rates a strong winning proposal

Dr. Elena Vasquez reviews past proposal AF243-001 (Air Force, Directed Energy, WIN). She rates writing quality as "strong" and enters: "Led with quantitative results in every section. Short paragraphs. Used evaluator language from the solicitation throughout." She adds evaluator praise: "Clearly organized approach with measurable milestones." The system stores this as a winning pattern with source attribution.

#### 2: Edge Case -- Elena skips a proposal she barely remembers

Elena encounters N244-012 (Navy, Autonomous UUV, LOSS) from 3 years ago. She doesn't remember the writing quality well enough to rate it. She selects "skip" and the system excludes it from quality analysis, proceeding to the next proposal without penalty.

#### 3: Error/Boundary -- New company with zero past proposals

Marcus Chen has just set up Pacific Systems Engineering's profile with no past_performance entries. When quality discovery starts, the system detects zero proposals and skips the past proposal review step entirely, offering to proceed directly to the writing style interview. No error, no empty list display.

### UAT Scenarios (BDD)

#### Scenario: Rate a winning proposal's writing quality

Given Elena Vasquez has a company profile with past_performance entry AF243-001 (Air Force, Directed Energy, WIN)
When she starts quality discovery
And she rates AF243-001 writing quality as "strong"
And she enters winning practice "Led with quantitative results in every section"
And she enters evaluator praise "Clearly organized approach with measurable milestones"
Then the quality rating "strong" is recorded for AF243-001
And the winning practice is stored in practices-to-replicate
And the evaluator praise is stored as a positive writing quality entry

#### Scenario: Skip a proposal the user cannot recall

Given Elena Vasquez has 5 past_performance entries in her profile
When she selects "skip" for proposal N244-012
Then N244-012 is excluded from quality analysis
And the system proceeds to the next proposal without error

#### Scenario: No past proposals available

Given Marcus Chen has a company profile with zero past_performance entries
When he starts quality discovery
Then the system skips the past proposal review step
And displays "No past proposals found in your company profile"
And offers to proceed to writing style preferences

#### Scenario: Rate a losing proposal with writing weakness noted

Given Elena Vasquez has past_performance entry AF243-002 (Air Force, RF Countermeasures, LOSS)
When she rates AF243-002 writing quality as "weak"
And she enters writing weakness "Technical approach section was too dense, no subheadings"
Then the quality rating "weak" is recorded for AF243-002
And the writing weakness is stored in practices-to-avoid

#### Scenario: Finish reviewing early before all proposals rated

Given Elena Vasquez has 5 past proposals and has rated 3 of them
When she selects "finish early"
Then artifact assembly uses ratings from the 3 reviewed proposals
And the 2 unreviewed proposals are excluded from analysis

### Acceptance Criteria

- [ ] System reads past_performance entries from company-profile.json and presents each for quality rating
- [ ] User can rate each proposal as weak, adequate, or strong
- [ ] User can enter freeform text for winning practices and evaluator praise/criticism
- [ ] User can skip individual proposals or finish early
- [ ] System handles zero past proposals gracefully (skip step, offer alternative)
- [ ] Quality ratings are additive -- they do not modify the company profile

### Technical Notes

- Reads past_performance from ~/.sbir/company-profile.json (read-only -- does not modify profile)
- Quality ratings stored in ~/.sbir/winning-patterns.json (separate artifact)
- Must handle case where past_performance has entries without topic_id (legacy profiles)
- Depends on: company-profile-schema.json past_performance structure

---

## US-QD-002: Writing Style Preferences Interview

### Problem

Marcus Chen is a BD lead who manages 3-4 active proposals simultaneously across different PIs. He finds it inconsistent that proposals by different PIs sound completely different -- one uses formal academic tone, another is conversational. Today he gives each PI verbal instructions ("data first, claims second") but these instructions are never captured in the system. The writing_style field exists in proposal-state.json but nothing ever populates it.

### Who

- BD Lead | Manages multiple PIs writing proposals | Wants consistent company voice across all proposals

### Solution

A guided interview within quality discovery that captures preferences for tone, detail level, evidence citation style, paragraph organization, and explicit practices to replicate/avoid. Produces a quality-preferences.json artifact at ~/.sbir/ that downstream agents (writer, reviewer) consume.

### Domain Examples

#### 1: Happy Path -- Marcus captures Pacific Systems Engineering's voice

Marcus Chen selects "direct and data-driven" tone, "deep technical detail" level, "inline quantitative" evidence style, and "short paragraphs, many subheadings" organization. He enters two practices to replicate: "Always lead with the result, then cite the evidence" and "Use evaluator language from solicitation." He enters two practices to avoid: "Our team has extensive experience without specifics" and "Passive voice chains." The system creates quality-preferences.json at ~/.sbir/.

#### 2: Edge Case -- Marcus wants a custom tone description

Marcus finds none of the predefined tone options fit. He selects "Let me describe it" and enters: "Technical but accessible -- assume the evaluator is smart but not in our specific subfield." The system stores this as a custom tone description alongside the standard fields.

#### 3: Error/Boundary -- Marcus reviews and edits before saving

Marcus completes the interview but realizes he selected the wrong evidence style. He chooses "review summary" to see all answers, then "edit answers" to change evidence style from "inline quantitative" to "table-heavy with metrics comparisons." The updated preference is saved.

### UAT Scenarios (BDD)

#### Scenario: Complete full writing style interview

Given Marcus Chen is running quality discovery for Pacific Systems Engineering
When he selects tone "direct and data-driven"
And he selects detail level "deep technical detail"
And he selects evidence style "inline quantitative"
And he selects organization "short paragraphs, many subheadings"
And he enters practice to replicate "Always lead with the result, then cite the evidence"
And he enters practice to avoid "Our team has extensive experience without specifics"
And he confirms the style preferences
Then quality-preferences.json is created at ~/.sbir/
And the tone field is "direct_data_driven"
And practices_to_replicate contains 1 item
And practices_to_avoid contains 1 item

#### Scenario: Custom tone description

Given Marcus Chen selects tone option "Let me describe it"
When he enters "Technical but accessible -- assume the evaluator is smart but not in our specific subfield"
Then the tone field is "custom" with the description text stored

#### Scenario: Review and edit preferences before saving

Given Marcus Chen has completed the style interview
When he selects "review summary"
Then all preferences are displayed
When he selects "edit answers" and changes evidence style to "table-heavy"
And he confirms
Then quality-preferences.json reflects the updated evidence_style

#### Scenario: Interview completable in under 10 minutes

Given Marcus Chen starts the writing style interview
When he selects predefined options for all 4 dimensions
And he enters 2 practices to replicate and 2 practices to avoid
Then the total interaction takes fewer than 15 prompts

### Acceptance Criteria

- [ ] Interview captures tone, detail_level, evidence_style, and organization preferences
- [ ] User can enter freeform practices to replicate and practices to avoid (arrays)
- [ ] Predefined options available for each dimension with a custom/freeform fallback
- [ ] User can review and edit answers before saving
- [ ] Artifact is created at ~/.sbir/quality-preferences.json with schema_version and updated_at
- [ ] Interview is completable in under 10 minutes for typical user

### Technical Notes

- quality-preferences.json lives at ~/.sbir/ (company-level, persists across proposals)
- Tone selection should inform the writing_style field in proposal-state.json when a new proposal starts
- Must support incremental update (add practices without losing existing ones)
- quality-preferences.json represents company consensus, not individual PI preferences. Concurrent updates use last-writer-wins with .bak backup, consistent with existing PES atomic write pattern. Merge strategy for multi-user teams is a DESIGN wave concern.
- Depends on: nothing (standalone artifact, new file)

---

## US-QD-003: Evaluator Writing Quality Feedback Extraction

### Problem

Dr. Sarah Kim is a research director who reviews all proposals before submission and has the most debrief reading experience on the team. She finds it impossible to distinguish between evaluator comments about writing quality ("difficult to follow") and comments about technical content ("lacked specific market data") in the current system. Today, the debrief analyst dumps everything into a single weakness profile, so writing quality lessons get lost among content feedback.

### Who

- Research Director | Reviews debriefs and proposals | Wants to separate writing quality signal from content signal

### Solution

A feedback extraction step within quality discovery that accepts evaluator comments, auto-categorizes each as meta-writing (organization, clarity, tone, persuasiveness) or content, presents the categorization for user confirmation, and stores meta-writing feedback in a separate writing-quality-profile.json while routing content feedback to the existing weakness profile.

### Domain Examples

#### 1: Happy Path -- Sarah separates writing from content feedback

Dr. Sarah Kim enters "Technical approach was difficult to follow" from AF243-002 debrief. The system auto-detects this as writing quality (organization/clarity). She then enters "Commercialization plan lacked specific market data." The system detects this as content feedback and routes it to the weakness profile. She confirms both categorizations.

#### 2: Edge Case -- Sarah overrides auto-categorization

Sarah enters "Risk table was hard to parse." The system categorizes it as content (risk section). Sarah overrides to writing quality (organization/clarity) because the evaluator was commenting on table formatting, not risk content. The system accepts the override.

#### 3: Error/Boundary -- No debrief feedback available

Elena Vasquez has no debriefs and cannot recall evaluator comments. She selects "No / Skip" and the system proceeds without creating a writing-quality-profile.json, noting that feedback can be added later.

### UAT Scenarios (BDD)

#### Scenario: Auto-categorize meta-writing vs content feedback

Given Dr. Sarah Kim enters evaluator comment "Technical approach was difficult to follow"
And she attributes it to proposal AF243-002 (Air Force, LOSS)
When the system categorizes the feedback
Then "difficult to follow" is categorized as writing quality under "organization_clarity"
And the entry is stored in writing-quality-profile.json

#### Scenario: Route content feedback to existing weakness profile

Given Dr. Sarah Kim enters evaluator comment "Commercialization plan lacked specific market data"
And she attributes it to proposal AF243-002 (Air Force, LOSS)
When the system categorizes the feedback
Then "lacked specific market data" is categorized as content feedback
And the content feedback is routed to the existing weakness profile

#### Scenario: User overrides auto-categorization

Given Dr. Sarah Kim enters "Risk table was hard to parse"
And the system categorizes it as content
When she overrides the category to writing quality "organization_clarity"
Then the entry is stored in writing-quality-profile.json under "organization_clarity"

#### Scenario: Detect cross-proposal writing patterns

Given writing-quality-profile.json has negative "organization_clarity" from AF243-002
And positive "organization_clarity" from AF243-001
When the system analyzes patterns
Then it identifies "organization_clarity" as a discriminator for Air Force proposals

#### Scenario: Skip feedback when none available

Given Elena Vasquez selects "No / Skip" for evaluator feedback
Then no writing-quality-profile.json is created
And the system proceeds to artifact assembly

### Acceptance Criteria

- [ ] System auto-categorizes evaluator comments as meta-writing or content feedback
- [ ] User can confirm or override auto-categorization for each comment
- [ ] Meta-writing feedback stored in ~/.sbir/writing-quality-profile.json
- [ ] Content feedback routed to existing weakness profile (no duplication)
- [ ] Each entry links to proposal topic_id, agency, and outcome
- [ ] System detects patterns across multiple proposals for the same agency

### Technical Notes

- Auto-categorization uses keyword matching: "difficult to follow," "hard to read," "well-organized," "clear" -> writing quality; "lacked data," "insufficient detail," "TRL gap" -> content
- writing-quality-profile.json lives at ~/.sbir/ (company-level)
- Content feedback integration must follow existing weakness_profile schema (category, pattern, frequency, agencies)
- Depends on: win-loss-analyzer weakness profile schema

---

## US-QD-004: Quality Artifact Assembly and Persistence

### Problem

Dr. Elena Vasquez is a PI who completes the quality discovery Q&A and wants to see tangible proof that her knowledge was captured. She finds it unsatisfying when systems collect data and then it "disappears" into a black box. Today, the only quality-related artifact is the weakness profile buried in proposal state, and it only tracks negatives.

### Who

- PI or BD Lead | Has just completed quality discovery steps | Wants confirmation that knowledge was captured and will be used

### Solution

After the user completes whichever quality discovery steps they chose, the system assembles up to three JSON artifacts at ~/.sbir/, displays a clear summary of what was captured, reports confidence levels, and shows which downstream agents will consume each artifact.

### Domain Examples

#### 1: Happy Path -- Elena completes full discovery, three artifacts created

Elena completes all three steps (past proposal review for 5 proposals, style interview, 4 evaluator feedback comments). Assembly creates quality-preferences.json, winning-patterns.json, and writing-quality-profile.json. Summary shows: preferences captured with 6 dimensions, 3 winning patterns at medium confidence, 2 writing quality entries across Air Force proposals.

#### 2: Edge Case -- Marcus completes only style interview

Marcus skips past proposal review and evaluator feedback. Assembly creates only quality-preferences.json. Summary shows 1 of 3 artifacts created, with notes about running the other steps later.

#### 3: Error/Boundary -- Elena updates existing artifacts

Elena runs quality discovery again after a proposal cycle. Existing quality-preferences.json has 3 practices-to-replicate. She adds 2 more. Assembly merges: 5 total practices. No data loss from prior session. updated_at timestamp refreshed.

### UAT Scenarios (BDD)

#### Scenario: Full discovery produces three artifacts

Given Elena Vasquez has completed past proposal review for 5 proposals
And she has completed the writing style interview
And she has entered 4 evaluator feedback comments
When artifact assembly runs
Then quality-preferences.json exists at ~/.sbir/ with schema_version "1.0.0" and updated_at
And winning-patterns.json exists at ~/.sbir/ with schema_version "1.0.0" and updated_at
And writing-quality-profile.json exists at ~/.sbir/ with schema_version "1.0.0" and updated_at
And a summary displays all three artifacts with key counts

#### Scenario: Partial discovery creates only available artifacts

Given Marcus Chen skipped past proposal review and evaluator feedback
And he completed the writing style interview
When artifact assembly runs
Then quality-preferences.json exists at ~/.sbir/
And winning-patterns.json does not exist
And writing-quality-profile.json does not exist
And summary notes which artifacts were skipped

#### Scenario: Update existing artifacts without data loss

Given quality-preferences.json exists with 3 practices_to_replicate
When Elena runs quality discovery and adds 2 new practices
And she confirms the update
Then quality-preferences.json contains 5 practices_to_replicate
And the updated_at timestamp is refreshed
And existing practices are preserved

#### Scenario: Confidence level computed from corpus size

Given winning-patterns.json is generated from 3 winning proposals
When confidence is calculated
Then confidence_level is "low" (fewer than 10 wins)
And the summary displays "Confidence: low (3 wins analyzed)"

#### Scenario: Atomic write prevents corruption

Given Elena is completing artifact assembly
When a write error occurs during quality-preferences.json save
Then no partial file is written
And any existing quality-preferences.json is unchanged
And an error message explains what happened and how to retry

### Acceptance Criteria

- [ ] Up to three artifacts created at ~/.sbir/ depending on which steps were completed
- [ ] Each artifact has schema_version and updated_at fields
- [ ] Summary displayed showing what was captured, confidence levels, and consumer agents
- [ ] Incremental updates merge with existing data (no data loss)
- [ ] Atomic writes (write to .tmp, rename to target)
- [ ] Confidence levels: low (<10 wins), medium (10-19 wins), high (>=20 wins)

### Technical Notes

- Artifacts live at ~/.sbir/ (company-level, not per-proposal)
- Atomic write pattern: write to .tmp, backup to .bak, rename .tmp to target (matches existing PES pattern)
- Confidence thresholds align with win-loss-analyzer.md thresholds
- Artifact sizes are bounded by the number of past proposals (typically 3-5/year for SBIR teams) and evaluator feedback entries (1-3 per debrief). Even at 50+ proposals, artifacts remain under 50KB. No size-limiting mechanism needed initially.
- Depends on: Steps 1-3 completion (or partial completion)

---

## US-QD-005: Strategist Reads Winning Patterns

### Problem

Dr. Elena Vasquez is a PI generating a strategy brief for a new Air Force proposal. She finds it frustrating that the strategist builds competitive positioning from the compliance matrix and company profile but ignores what actually worked in her past wins. Today, winning discriminators are captured in Wave 9 debrief analysis but never fed forward to Wave 1 strategy generation.

### Who

- PI | Starting a new proposal for an agency with prior submissions | Wants strategy informed by actual win data

### Solution

The strategist agent, during Wave 1 strategy brief generation, reads winning-patterns.json if it exists and integrates applicable patterns into the competitive positioning section of the strategy brief, with source attribution and confidence levels.

### Domain Examples

#### 1: Happy Path -- Elena's Air Force winning patterns inform new Air Force strategy

winning-patterns.json has 3 patterns from Air Force wins: "lead with quantitative results," "explicit TRL entry/exit criteria," and "use evaluator language from solicitation." The strategist references all three in the competitive positioning section with source proposal citations and low confidence (3 wins).

#### 2: Edge Case -- No matching patterns for new agency

Elena is writing her first DARPA proposal. winning-patterns.json has patterns only from Air Force and Navy. The strategist notes "No agency-specific winning patterns for DARPA" and proceeds with standard competitive positioning.

#### 3: Error/Boundary -- No quality artifacts exist

Marcus Chen has not run quality discovery. No winning-patterns.json exists. The strategist generates the strategy brief without quality intelligence and includes a note: "Quality playbook: not available. Run /sbir:proposal quality discover."

### UAT Scenarios (BDD)

#### Scenario: Strategist references winning patterns in strategy brief

Given winning-patterns.json exists with Air Force patterns "lead with quantitative results" and "explicit TRL entry/exit criteria"
And Elena is generating a strategy brief for Air Force topic AF244-015
When the strategist loads quality intelligence
Then the competitive positioning section references both patterns
And each pattern cites its source proposal and confidence level

#### Scenario: No matching patterns for target agency

Given winning-patterns.json has patterns only from Air Force
And the current proposal is for DARPA
When the strategist loads quality intelligence
Then the strategy brief notes "No agency-specific winning patterns for DARPA"
And standard competitive positioning is generated

#### Scenario: Missing quality artifacts handled gracefully

Given no winning-patterns.json exists at ~/.sbir/
When the strategist generates a strategy brief
Then the brief is generated without quality intelligence
And a note appears suggesting quality discovery

### Acceptance Criteria

- [ ] Strategist loads winning-patterns.json if it exists during Wave 1
- [ ] Applicable patterns filtered by agency match
- [ ] Patterns cited with source proposal and confidence level
- [ ] Missing file is non-fatal (graceful degradation)
- [ ] No matching patterns produces informational note, not error

### Technical Notes

- Read-only access to ~/.sbir/winning-patterns.json
- Agency matching: exact match on agency field from winning pattern vs. current topic agency
- Pattern applicability: all patterns from matching agency + patterns flagged as "universal"
- Depends on: US-QD-004 (artifact assembly), sbir-strategist existing workflow

---

## US-QD-006: Writer Applies Quality Intelligence During Drafting

### Problem

Dr. Elena Vasquez is a PI drafting the technical approach section for a new Air Force proposal. She finds it frustrating that the writer agent uses generic Strunk & White style guidance when her company has specific writing patterns that won past proposals and specific weaknesses that evaluators flagged. Today, the writer loads elements-of-style.md as a skill but has no access to company-specific quality intelligence.

### Who

- PI | Drafting proposal sections in Waves 3-4 | Wants drafts that reflect company's proven writing approach

### Solution

The writer agent, during Waves 3-4, loads all three quality artifacts if they exist: quality-preferences.json (for style guidance), winning-patterns.json (for pattern replication), and writing-quality-profile.json (for quality alerts when drafting sections for agencies with known writing feedback).

### Domain Examples

#### 1: Happy Path -- Elena drafts with quality intelligence loaded

quality-preferences.json says "direct and data-driven" tone, "short paragraphs." winning-patterns.json has "lead with quantitative results." writing-quality-profile.json has a negative "organization_clarity" entry for Air Force. The writer drafts the technical approach with short paragraphs, inline quantitative evidence, leading with results, and displays a quality alert: "Past Air Force evaluators noted 'difficult to follow' -- ensure clear subheading structure."

#### 2: Edge Case -- Only quality preferences exist (no patterns or feedback)

Marcus Chen ran only the style interview. The writer loads quality-preferences.json and applies tone and organization preferences. No winning patterns or quality alerts are available. Writer proceeds with preferences + default elements-of-style.

#### 3: Error/Boundary -- No quality artifacts exist

No quality artifacts at ~/.sbir/. writing_style in proposal-state.json is null. Writer uses standard prose conventions without loading elements-of-style (null means no style skill). Drafting proceeds normally with generic quality.

### UAT Scenarios (BDD)

#### Scenario: Writer applies all three quality artifacts

Given quality-preferences.json specifies "direct_data_driven" tone and "short_paragraphs" organization
And winning-patterns.json includes "lead with quantitative results"
And writing-quality-profile.json has negative "organization_clarity" for Air Force
And the current proposal is for Air Force
When the writer drafts the technical approach section
Then paragraphs are limited to 3-4 sentences with frequent subheadings
And claims include inline quantitative evidence
And a quality alert is displayed about past Air Force organization feedback

#### Scenario: Writer loads partial quality artifacts

Given quality-preferences.json exists with style preferences
And no winning-patterns.json exists
And no writing-quality-profile.json exists
When the writer drafts a section
Then style preferences are applied
And no winning pattern guidance appears
And no quality alerts appear

#### Scenario: Writer falls back gracefully when no artifacts exist

Given no quality artifacts exist at ~/.sbir/
When the writer drafts a section
Then standard prose conventions are used
And no quality-related messages appear

#### Scenario: Quality alert for specific agency/section combination

Given writing-quality-profile.json has "organization_clarity" negative for Air Force
And the current proposal is for Air Force
When the writer begins drafting the technical approach section
Then a quality alert references the specific past evaluator comment
And suggests structural improvements based on the feedback

### Acceptance Criteria

- [ ] Writer loads quality-preferences.json, winning-patterns.json, and writing-quality-profile.json if they exist
- [ ] Style preferences influence tone, detail level, evidence citation, and paragraph structure
- [ ] Winning patterns are applied as drafting guidance (not rigid templates)
- [ ] Quality alerts surface for matching agency and section combinations
- [ ] Missing artifacts produce no error (graceful degradation to defaults)
- [ ] Quality intelligence supplements, not replaces, existing elements-of-style skill

### Technical Notes

- quality-preferences.json loaded during Phase 3 (DRAFT) alongside writing_style skill
- Quality alerts match on agency field AND can be section-specific (technical approach, SOW, etc.)
- Winning patterns are guidance ("evaluators praised X"), not rigid rules
- Depends on: US-QD-004 (artifact assembly), sbir-writer existing workflow

---

## US-QD-007: Reviewer Checks Quality Profile During Review

### Problem

Dr. Sarah Kim is a research director reviewing the technical approach section for a new Air Force proposal. She finds it frustrating that the reviewer checks against the generic weakness profile (technical content issues) but misses writing quality patterns she has seen in past debriefs. Today, the reviewer loads win-loss-analyzer for content weaknesses but has no awareness of writing quality feedback.

### Who

- Research Director (or any proposal reviewer) | Reviewing draft sections in Waves 4 or 7 | Wants review calibrated to known writing quality issues

### Solution

The reviewer agent, during Waves 4 and 7, loads writing-quality-profile.json alongside the existing weakness profile and quality-preferences.json for style compliance. Quality profile matches produce tagged findings ("[QUALITY PROFILE MATCH]") with elevated severity and references to past evaluator comments.

### Domain Examples

#### 1: Happy Path -- Reviewer flags organization issue matching past Air Force feedback

writing-quality-profile.json has "organization_clarity" negative for Air Force from AF243-002 ("Technical approach was difficult to follow"). The reviewer reviews a new Air Force technical approach section with 3 consecutive paragraphs exceeding 6 sentences. The reviewer flags it as "[QUALITY PROFILE MATCH]" with high severity, citing the past evaluator comment.

#### 2: Edge Case -- Reviewer checks style compliance against quality preferences

quality-preferences.json says practices_to_avoid includes "Our team has extensive experience without specifics." The reviewer finds "Our team brings extensive experience to this effort" in a draft. It flags a style compliance finding.

#### 3: Error/Boundary -- No quality artifacts exist

No quality artifacts at ~/.sbir/. The reviewer operates with standard evaluation criteria only. No quality profile match findings are produced. Review quality is baseline, not degraded.

### UAT Scenarios (BDD)

#### Scenario: Reviewer flags quality profile match

Given writing-quality-profile.json has negative "organization_clarity" for Air Force
And the current proposal is for Air Force
When the reviewer reviews the technical approach section
And the section contains paragraphs exceeding 6 sentences
Then a finding is produced with tag "[QUALITY PROFILE MATCH]"
And the finding references "Technical approach was difficult to follow" (AF243-002)
And severity is "high"

#### Scenario: Reviewer checks practices-to-avoid compliance

Given quality-preferences.json has practices_to_avoid "Our team has extensive experience without specifics"
When the reviewer finds "Our team brings extensive experience to this effort" in a draft section
Then a style compliance finding is produced
And the suggestion references the quality preference

#### Scenario: Reviewer operates normally without quality artifacts

Given no quality artifacts exist at ~/.sbir/
When the reviewer reviews a section
Then standard evaluation criteria are applied
And no quality-related findings are produced
And review proceeds normally

### Acceptance Criteria

- [ ] Reviewer loads writing-quality-profile.json and quality-preferences.json during Waves 4 and 7
- [ ] Quality profile matches produce "[QUALITY PROFILE MATCH]" tagged findings
- [ ] Quality profile matches have elevated severity (high or critical)
- [ ] Style compliance checks reference specific practices_to_avoid entries
- [ ] Missing artifacts are non-fatal (reviewer uses standard criteria only)
- [ ] Quality findings are additional -- they do not replace existing review findings

### Technical Notes

- writing-quality-profile.json loaded alongside win-loss-analyzer weakness profile in Phase 2 (SECTION REVIEW)
- quality-preferences.json loaded in Phase 1 (ORIENT) alongside writing_style skill
- Pattern matching: agency match + category match + section match (if section-specific)
- Depends on: US-QD-004 (artifact assembly), sbir-reviewer existing workflow

---

## US-QD-008: Incremental Quality Learning After Proposal Cycle

### Problem

Dr. Elena Vasquez has just completed a proposal cycle and received debrief feedback through the debrief analyst (Wave 9). She finds it frustrating that the lessons learned are captured in per-proposal artifacts but never flow back into the company-level quality playbook. Today, she would need to manually re-run quality discovery and re-enter everything the debrief analyst already processed.

### Who

- PI or BD Lead | After completing Wave 9 debrief processing | Wants quality artifacts to compound automatically with each cycle

### Solution

A quality update command (/sbir:proposal quality update) that reads the latest debrief analysis, extracts any new writing quality feedback, updates winning-patterns.json with new win data, recalculates confidence levels, and flags stale patterns over 2 years old.

### Domain Examples

#### 1: Happy Path -- Elena updates after a winning proposal cycle

Elena's proposal AF244-015 won. The debrief praised "clear milestone structure" and "quantitative TRL evidence." She runs quality update. The system adds AF244-015 to the win corpus, extracts the praise as new winning patterns, increments confidence from "low" (3 wins) to "low" (4 wins), and stores the evaluator praise in writing-quality-profile.json as positive entries.

#### 2: Edge Case -- Stale patterns flagged during update

winning-patterns.json has a pattern from a 2023 Navy proposal. Today is March 2026. Quality update flags it as stale (over 2 years old) and asks Elena: keep, review individually, or drop stale patterns.

#### 3: Error/Boundary -- Quality update with no prior artifacts

Marcus Chen runs quality update but has never run quality discovery. No artifacts exist. The system suggests running full discovery first: "No quality artifacts found. Run /sbir:proposal quality discover first."

### UAT Scenarios (BDD)

#### Scenario: Update winning patterns after new win

Given Elena's proposal AF244-015 has outcome WIN
And the debrief contains praise "clear milestone structure"
When she runs "/sbir:proposal quality update"
Then winning-patterns.json adds AF244-015 to the win corpus
And "clear milestone structure" is added as a winning pattern
And confidence_level is recalculated

#### Scenario: Flag stale patterns during update

Given winning-patterns.json has a pattern from Navy proposal dated 2023-06-15
And today is 2026-03-17
When Elena runs quality update
Then the pattern is flagged as stale (over 2 years old)
And she is offered options: keep, review individually, drop stale

#### Scenario: Update with no prior artifacts

Given no quality artifacts exist at ~/.sbir/
When Marcus runs "/sbir:proposal quality update"
Then the system displays "No quality artifacts found"
And suggests "/sbir:proposal quality discover"

#### Scenario: Extract meta-writing feedback from Wave 9 debrief

Given the debrief analyst processed AF244-015 with evaluator comment "sections were well-organized"
When Elena runs quality update
Then "well-organized" is auto-categorized as writing quality (organization_clarity, positive)
And writing-quality-profile.json is updated with the new entry

#### Scenario: Recalculate confidence after corpus grows

Given winning-patterns.json currently has confidence_level "low" (7 wins)
And 3 new wins are added during update
When confidence is recalculated
Then confidence_level is "medium" (10 wins)

### Acceptance Criteria

- [ ] Quality update reads latest debrief analysis artifacts
- [ ] New writing quality feedback extracted and categorized (meta-writing vs content)
- [ ] Winning patterns updated with new win data
- [ ] Confidence levels recalculated from updated corpus size
- [ ] Patterns over 2 years old flagged as stale with user action options
- [ ] Update preserves existing data (additive, not destructive)
- [ ] Missing prior artifacts produces clear message directing to full discovery

### Technical Notes

- Reads debrief artifacts from ./artifacts/wave-9-debrief/ (per-proposal)
- Updates company-level artifacts at ~/.sbir/
- Staleness threshold: 2 years (configurable)
- Must handle case where debrief has no writing quality comments (no-op for writing-quality-profile)
- Depends on: US-QD-004 (existing artifacts), sbir-debrief-analyst Wave 9 outputs
