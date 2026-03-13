Feature: Solicitation Finder
  As Phil Santos, a solo SBIR proposal writer at Radiant Defense Systems,
  I want to find the best-fit SBIR/STTR topics from each solicitation cycle
  so I can focus my limited proposal-writing time on topics with the highest win probability.

  Background:
    Given Phil Santos has a company profile at ~/.sbir/company-profile.json
    And the company profile has company_name "Radiant Defense Systems, LLC"
    And the company profile has capabilities including "directed energy", "RF power systems", "thermal management"
    And the company profile has SAM.gov registration active with CAGE code "7X9K2"
    And the company profile has security_clearance "secret"
    And the company profile has employee_count 15
    And the company profile has key_personnel including Dr. Elena Vasquez (directed energy, laser physics) and Marcus Chen (RF power, thermal management)

  # --- Step 1: Invoke Finder ---

  Scenario: Fetch open topics from DSIP API with default settings
    Given the DSIP API has 347 open topics for solicitation cycle DOD_SBIR_2026_P1_C3
    When Phil runs "/sbir:solicitation find"
    Then the tool displays "Radiant Defense Systems, LLC" as the company name
    And the tool displays "347 topics retrieved"
    And the tool begins pre-filtering against company capabilities

  Scenario: Fetch open topics with agency and phase filters
    Given the DSIP API has 89 open Air Force Phase I topics
    When Phil runs "/sbir:solicitation find --agency 'Air Force' --phase I"
    Then the tool displays "89 topics retrieved (filtered)"
    And the tool displays "agency=Air Force, phase=I" as active filters

  Scenario: Fetch topics for a specific solicitation cycle
    Given the DSIP API has topics for solicitation DOD_SBIR_2026_P1_C3
    When Phil runs "/sbir:solicitation find --solicitation DOD_SBIR_2026_P1_C3"
    Then only topics from that solicitation cycle are retrieved

  # --- Step 1: Error Paths ---

  Scenario: No company profile exists
    Given no company profile exists at ~/.sbir/company-profile.json
    When Phil runs "/sbir:solicitation find"
    Then the tool displays an error "No company profile found"
    And the tool suggests "/sbir:proposal profile setup" to create one
    And the tool suggests "--file" option for degraded-accuracy scoring without profile

  Scenario: DSIP API unavailable triggers fallback guidance
    Given the DSIP API is unreachable (connection timeout)
    When Phil runs "/sbir:solicitation find"
    Then the tool displays a warning "DSIP API unavailable"
    And the tool suggests providing a BAA PDF with --file flag
    And the tool displays the download URL for dodsbirsttr.mil/topics-app/

  Scenario: Fall back to BAA PDF when API unavailable
    Given the DSIP API is unreachable
    And Phil has downloaded baa-2026-3.pdf containing 47 topics
    When Phil runs "/sbir:solicitation find --file ./solicitations/baa-2026-3.pdf"
    Then the tool extracts 47 topics from the PDF
    And the tool proceeds with pre-filtering and scoring
    And the tool displays "Source: BAA PDF (47 topics extracted)"

  Scenario: API rate limiting with partial results
    Given the DSIP API returns 200 topics then rate-limits further requests
    When Phil runs "/sbir:solicitation find"
    Then the tool displays "DSIP API rate limit reached after 200 topics"
    And the tool offers to score partial results (200 topics)
    And the tool offers to retry in 5 minutes
    And the tool offers the --file fallback option

  # --- Step 2: Pre-Filter and Score ---

  Scenario: Keyword pre-filter reduces candidate set
    Given the DSIP API returned 347 open topics
    And the company profile has capabilities "directed energy", "RF power systems", "thermal management"
    When the keyword pre-filter runs
    Then 42 candidate topics are identified as keyword matches
    And 305 topics are eliminated
    And the tool displays progress "Keyword match: 42 candidate topics (305 eliminated)"

  Scenario: Score candidates with five-dimension fit model
    Given 42 candidate topics have been identified by keyword pre-filter
    And topic details (PDFs) have been retrieved for all 42 candidates
    When the LLM scores each candidate against the company profile
    Then each candidate receives scores for all five dimensions (SME, PP, Cert, Elig, STTR)
    And each candidate receives a composite score
    And each candidate receives a recommendation (GO, EVALUATE, or NO-GO)
    And progress is displayed during scoring ("Scoring topic 18 of 42...")

  Scenario: Pre-filter produces zero candidates
    Given the DSIP API returned 347 open topics
    And no topics contain keywords matching company capabilities
    When the keyword pre-filter runs
    Then zero candidate topics are identified
    And the tool displays "No topics matched your company profile"
    And the tool suggests reviewing the company profile
    And the tool suggests running without filters

  # --- Step 3: Review Results ---

  Scenario: Display ranked results with GO recommendations
    Given scoring has completed for 42 candidate topics
    And 3 topics scored above 0.60 with no zero-score dimensions
    When the results are displayed
    Then the 3 topics are listed in descending composite score order
    And each row shows topic ID, agency, title, composite score, recommendation, and deadline
    And the top-scoring topic AF263-042 shows "GO" recommendation with score 0.82

  Scenario: Display disqualified topics with reasons
    Given scoring has completed
    And topic AF263-099 requires TS clearance but company profile has Secret
    And topic N263-S05 is STTR but company has no research institution partner
    And topic A263-200 has composite score 0.08
    When the results are displayed
    Then AF263-099 shows "NO-GO" with reason "Requires TS clearance (profile: Secret)"
    And N263-S05 shows "NO-GO" with reason "No research institution partner"
    And A263-200 shows "NO-GO" with reason "No SME match (0.08 composite)"
    And disqualified topics are listed in a separate section below scored results

  Scenario: Results include deadline warnings
    Given scoring has completed
    And topic HR001126-01 has a deadline in 5 days
    And topic AF263-042 has a deadline in 61 days
    When the results are displayed
    Then HR001126-01 shows an "URGENT" flag
    And AF263-042 shows the deadline without a flag

  Scenario: Results persisted to finder-results.json
    Given scoring has completed with 5 GO topics and 3 NO-GO topics
    When the results are displayed
    Then the tool saves results to .sbir/finder-results.json
    And the saved file includes finder_run_id, run_date, source, and all scored topics
    And each scored topic includes topic_id, composite_score, dimension scores, and recommendation

  Scenario: Flag expired topics in results
    Given scoring has completed
    And topic AF263-042 has a deadline of 2026-03-01 which has passed
    When the results are displayed
    Then AF263-042 shows "EXPIRED" instead of days remaining
    And the tool warns "2 topics in results have passed their deadline"

  # --- Step 4: Drill Down ---

  Scenario: View detailed scoring breakdown for a topic
    Given finder results include topic AF263-042 with composite score 0.82
    And AF263-042 scored SME=0.95, PP=0.80, Cert=1.00, Elig=1.00, STTR=1.00
    When Phil types "details AF263-042"
    Then the tool displays the five-dimension scoring breakdown with rationale per dimension
    And the tool displays the overall recommendation rationale
    And the tool displays matching key personnel (Dr. Elena Vasquez, Marcus Chen)
    And the tool shows "61 days" remaining to the deadline
    And the tool offers "pursue AF263-042" and "back" as next actions

  Scenario: Request details for a disqualified topic
    Given finder results include topic AF263-099 with NO-GO recommendation
    And AF263-099 was disqualified for requiring TS clearance
    When Phil types "details AF263-099"
    Then the tool displays the disqualification reason prominently
    And the tool shows which profile field triggered the disqualification
    And the tool does not offer "pursue" as an action

  # --- Step 5: Select and Transition ---

  Scenario: Select topic and transition to proposal creation
    Given Phil is viewing finder results
    And topic AF263-042 has recommendation GO with score 0.82
    When Phil types "pursue AF263-042"
    Then the tool displays a confirmation summary (topic ID, title, agency, phase, deadline, score)
    And the tool prompts "Proceed to create proposal? (y/n)"

  Scenario: Confirm topic selection starts proposal workflow
    Given Phil has typed "pursue AF263-042"
    And the confirmation summary is displayed
    When Phil confirms with "y"
    Then the tool transitions to /sbir:proposal new
    And topic AF263-042 data is pre-loaded as TopicInfo (topic_id, agency, phase, deadline, title)
    And Phil does not need to re-enter any topic metadata

  Scenario: Cancel topic selection returns to results
    Given Phil has typed "pursue AF263-042"
    And the confirmation summary is displayed
    When Phil declines with "n"
    Then the tool returns to the results list
    And no proposal is created

  # --- Edge Cases ---

  Scenario: Company profile has incomplete data
    Given the company profile exists but has no past_performance entries
    And the company profile has no research_institution_partners
    When Phil runs "/sbir:solicitation find"
    Then the tool warns "Profile incomplete: past_performance empty (scoring accuracy degraded)"
    And past_performance dimension scores 0.0 for all topics
    And recommendations cap at EVALUATE (not NO-GO from data absence alone)

  Scenario: Re-run finder with different filters
    Given Phil previously ran the finder and .sbir/finder-results.json exists
    When Phil runs "/sbir:solicitation find --agency Navy"
    Then the tool fetches and scores Navy topics
    And the previous finder-results.json is overwritten with new results
    And the new results header shows "agency=Navy" filter
