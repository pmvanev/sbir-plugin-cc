Feature: Proposal Quality Discovery
  As a PI or BD lead who has submitted SBIR proposals before,
  I want to capture what made our proposals win or lose from a writing quality perspective,
  so that future proposals replicate our winning patterns and avoid our known weaknesses.

  Background:
    Given the SBIR proposal plugin is installed and configured
    And a company profile exists at ~/.sbir/company-profile.json

  # --- Step 1: Past Proposal Quality Review ---

  Scenario: Rate writing quality of past winning proposal
    Given Elena Vasquez has a company profile with past_performance entry:
      | topic_id  | agency    | topic_area           | outcome |
      | AF243-001 | Air Force | Directed Energy      | WIN     |
    When she starts quality discovery
    And she rates AF243-001 writing quality as "strong"
    And she enters winning practice: "Led with quantitative results in every section"
    And she enters evaluator praise: "Clearly organized approach with measurable milestones"
    Then the quality rating is recorded for AF243-001
    And the winning practice is stored in the practices-to-replicate list
    And the evaluator praise is stored as a positive writing quality entry

  Scenario: Rate writing quality of past losing proposal
    Given Elena Vasquez has a company profile with past_performance entry:
      | topic_id  | agency    | topic_area           | outcome |
      | AF243-002 | Air Force | RF Countermeasures   | LOSS    |
    When she starts quality discovery
    And she rates AF243-002 writing quality as "weak"
    And she enters writing weakness: "Technical approach section was too dense, no subheadings"
    Then the quality rating is recorded for AF243-002
    And the writing weakness is stored in the practices-to-avoid list

  Scenario: Skip proposal quality rating when user cannot recall
    Given Elena Vasquez has a company profile with 5 past_performance entries
    When she starts quality discovery
    And she selects "skip" for proposal N244-012
    Then N244-012 is excluded from quality analysis
    And the system proceeds to the next proposal

  Scenario: No past proposals in company profile
    Given Marcus Chen has a company profile with zero past_performance entries
    When he starts quality discovery
    Then the system displays "No past proposals found in your company profile"
    And offers to skip directly to writing style preferences
    And does not show the past proposal review step

  # --- Step 2: Writing Style Interview ---

  Scenario: Complete writing style preferences interview
    Given Marcus Chen is running quality discovery for Pacific Systems Engineering
    When he selects tone "direct and data-driven"
    And he selects detail level "deep technical detail"
    And he selects evidence style "inline quantitative"
    And he selects organization "short paragraphs, many subheadings"
    And he enters practice to replicate: "Always lead with the result, then cite the evidence"
    And he enters practice to replicate: "Use evaluator language from solicitation"
    And he enters practice to avoid: "Our team has extensive experience without specifics"
    And he enters practice to avoid: "Passive voice chains"
    And he confirms the style preferences
    Then quality-preferences.json is created at ~/.sbir/
    And the tone field is "direct_data_driven"
    And the detail_level field is "deep_technical"
    And the evidence_style field is "inline_quantitative"
    And the organization field is "short_paragraphs"
    And practices_to_replicate contains 2 items
    And practices_to_avoid contains 2 items

  Scenario: Describe custom tone instead of selecting predefined option
    Given Marcus Chen selects tone option "Let me describe it"
    When he enters "Technical but accessible -- assume the evaluator is smart but not in our specific subfield"
    Then the custom tone description is stored in quality-preferences.json
    And the tone field is "custom" with the description text

  Scenario: Review and edit style preferences before saving
    Given Marcus Chen has completed the style interview
    When he selects "review summary"
    Then all preferences are displayed in a summary view
    When he selects "edit answers"
    And he changes tone from "direct and data-driven" to "formal and authoritative"
    And he confirms
    Then quality-preferences.json reflects the updated tone

  # --- Step 3: Evaluator Feedback Extraction ---

  Scenario: Separate meta-writing feedback from content feedback
    Given Dr. Sarah Kim enters evaluator comment "Technical approach was difficult to follow"
    And she attributes it to proposal AF243-002 with outcome LOSS
    And she enters evaluator comment "Commercialization plan lacked specific market data"
    And she attributes it to proposal AF243-002 with outcome LOSS
    When the system categorizes the feedback
    Then "difficult to follow" is categorized as writing quality under "organization_clarity"
    And "lacked specific market data" is categorized as content feedback
    And the writing quality entry is stored in writing-quality-profile.json
    And the content feedback is routed to the existing weakness profile

  Scenario: Capture positive writing quality feedback from winning proposal
    Given Dr. Sarah Kim enters evaluator comment "Well-organized approach with clear milestones"
    And she attributes it to proposal AF243-001 with outcome WIN
    When the system categorizes the feedback
    Then the comment is categorized as positive writing quality under "organization_clarity"
    And it is stored in writing-quality-profile.json with sentiment "positive"

  Scenario: Detect writing quality patterns across proposals
    Given writing-quality-profile.json has entries:
      | comment                                    | proposal  | agency    | category             | sentiment |
      | Technical approach was difficult to follow  | AF243-002 | Air Force | organization_clarity | negative  |
      | Well-organized approach with clear milestones| AF243-001 | Air Force | organization_clarity | positive  |
    When the system analyzes patterns
    Then it identifies "organization_clarity" as a discriminator for Air Force proposals
    And it notes the contrast: wins had clear structure, losses did not

  Scenario: Skip evaluator feedback when none available
    Given Elena Vasquez selects "No / Skip" for evaluator feedback
    Then no writing-quality-profile.json is created
    And the system proceeds to artifact assembly
    And a message notes "Add evaluator feedback later with /sbir:proposal quality update"

  # --- Step 4: Artifact Assembly ---

  Scenario: Create all three quality artifacts after full discovery
    Given Elena Vasquez has completed past proposal review for 5 proposals
    And she has completed the writing style interview
    And she has entered 4 evaluator feedback comments
    When artifact assembly runs
    Then quality-preferences.json exists at ~/.sbir/ with schema_version and updated_at
    And winning-patterns.json exists at ~/.sbir/ with schema_version and updated_at
    And writing-quality-profile.json exists at ~/.sbir/ with schema_version and updated_at
    And a summary displays all three artifacts with key metrics

  Scenario: Create partial artifacts when steps were skipped
    Given Marcus Chen skipped past proposal review
    And he completed the writing style interview
    And he skipped evaluator feedback
    When artifact assembly runs
    Then quality-preferences.json exists at ~/.sbir/
    And winning-patterns.json is not created (no data)
    And writing-quality-profile.json is not created (no data)
    And the summary shows which artifacts were created and which were skipped

  Scenario: Update existing artifacts without data loss
    Given quality-preferences.json already exists at ~/.sbir/ with 3 practices to replicate
    When Elena Vasquez runs quality discovery again
    And she adds 2 new practices to replicate
    And she confirms the update
    Then quality-preferences.json contains 5 practices to replicate (3 original + 2 new)
    And the updated_at timestamp is refreshed

  Scenario: Artifact assembly with confidence levels
    Given winning-patterns.json is generated from 3 winning proposals
    When the system assigns confidence level
    Then confidence_level is "low" because fewer than 10 wins are analyzed
    And the summary displays "Confidence: low (3 wins analyzed)"

  # --- Step 5: Strategist Consumption ---

  Scenario: Strategist integrates winning patterns into strategy brief
    Given winning-patterns.json exists with patterns:
      | pattern                                        | source_proposals | agency    |
      | Lead with quantitative results                 | AF243-001        | Air Force |
      | Explicit TRL entry/exit criteria               | AF243-001, N244-008 | Air Force, Navy |
    And Elena is generating a strategy brief for a new Air Force proposal
    When the strategist loads quality intelligence
    Then the strategy brief competitive positioning section references:
      | pattern                        | source             | confidence |
      | Lead with quantitative results | AF243-001 (WIN)    | low        |
      | Explicit TRL entry/exit criteria | AF243-001 (WIN) | low        |

  Scenario: Strategist gracefully handles missing quality artifacts
    Given no quality artifacts exist at ~/.sbir/
    When the strategist generates a strategy brief
    Then the strategy brief is generated without quality intelligence
    And a note appears: "Quality playbook: not available. Run /sbir:proposal quality discover"

  # --- Step 6: Writer Consumption ---

  Scenario: Writer applies quality preferences during section drafting
    Given quality-preferences.json specifies:
      | field          | value                |
      | tone           | direct_data_driven   |
      | detail_level   | deep_technical       |
      | evidence_style | inline_quantitative  |
      | organization   | short_paragraphs     |
    And winning-patterns.json includes "lead with quantitative results"
    When the writer drafts the technical approach section
    Then paragraphs are limited to 3-4 sentences
    And each claim includes inline quantitative evidence
    And the draft tone is direct and data-driven

  Scenario: Writer surfaces writing quality alerts for matching agency
    Given writing-quality-profile.json has a negative "organization_clarity" entry for Air Force
    And the current proposal is for Air Force topic AF244-015
    When the writer begins drafting the technical approach section
    Then a quality alert is displayed:
      """
      Past Air Force evaluators noted "difficult to follow" in technical approach sections.
      Ensure clear subheading structure.
      """

  Scenario: Writer falls back to defaults when no quality artifacts exist
    Given no quality artifacts exist at ~/.sbir/
    And writing_style in proposal-state.json is null
    When the writer drafts a section
    Then the writer uses standard prose conventions
    And elements-of-style is not loaded (no writing_style set)

  # --- Step 7: Reviewer Consumption ---

  Scenario: Reviewer flags quality profile match in section review
    Given writing-quality-profile.json has entry:
      | category             | agency    | comment                                    |
      | organization_clarity | Air Force | Technical approach was difficult to follow  |
    And the current proposal is for Air Force
    When the reviewer reviews the technical approach section
    And the section contains paragraphs exceeding 6 sentences
    Then the reviewer produces a finding with tag "[QUALITY PROFILE MATCH]"
    And the finding references the past evaluator comment
    And severity is "high" because it matches a known quality weakness

  Scenario: Reviewer checks style compliance against quality preferences
    Given quality-preferences.json specifies practices_to_avoid:
      | practice                                          |
      | "Our team has extensive experience" without specifics |
    When the reviewer reviews a section containing "Our team brings extensive experience to this effort"
    Then the reviewer flags a style compliance finding
    And the suggestion references the quality preference that prohibits vague experience claims

  Scenario: Reviewer operates normally when no quality artifacts exist
    Given no quality artifacts exist at ~/.sbir/
    When the reviewer reviews a section
    Then the reviewer uses standard evaluation criteria only
    And no quality profile match findings are produced
    And review quality is not degraded

  # --- Incremental Learning (Post-Cycle Update) ---

  Scenario: Update quality artifacts after Wave 9 debrief
    Given Elena has completed a proposal cycle for AF244-015
    And the debrief analyst has processed the debrief with evaluator feedback
    And the debrief included writing quality comment "clear and well-organized"
    When Elena runs "/sbir:proposal quality update"
    Then the system presents the new debrief feedback for categorization
    And writing-quality-profile.json is updated with the new positive entry
    And winning-patterns.json is updated if the proposal won
    And confidence levels are recalculated with the larger corpus

  Scenario: Flag stale winning patterns during update
    Given winning-patterns.json has a pattern from a Navy proposal dated 2023-06-15
    And today is 2026-03-17
    When Elena runs quality update
    Then the system flags the pattern as stale (over 2 years old)
    And offers options: keep, review individually, or drop stale patterns

  # --- Cancel and Error Handling ---

  Scenario: Cancel quality discovery mid-flow
    Given Elena has completed Step 1 (past proposal review)
    And she is in the middle of Step 2 (writing style interview)
    When she cancels the discovery
    Then no quality artifacts are written or modified
    And a message confirms "Quality discovery cancelled. No files were written or modified."

  Scenario: Resume quality discovery after partial completion
    Given Elena previously completed Steps 1-2 and artifacts were saved
    When she runs "/sbir:proposal quality update"
    Then the system detects existing artifacts
    And offers to update specific sections rather than redo everything
