Feature: DSIP API Complete
  As the sbir-topic-scout agent
  I need complete topic intelligence from the DSIP API
  So I can make accurate GO/EVALUATE/NO-GO recommendations
  Without Dr. Sarah Chen having to manually browse dodsbirsttr.mil

  Background:
    Given the DSIP API is accessible at dodsbirsttr.mil
    And the User-Agent header is set to "Mozilla/5.0"

  # --- Step 1: Search with Correct Format ---

  Scenario: Search returns only matching topics using JSON searchParam format
    Given the current SBIR solicitation cycle has 24 open and pre-release topics
    When the adapter searches with status filter "Open"
    Then the search request uses the JSON searchParam format with topicReleaseStatus [592]
    And the response contains exactly the matching topics (not all 32,638 historical topics)
    And each topic has a hash ID in the topicId field (e.g., "7051b2da4a1e4c52bd0e7daf80d514f7_86352")
    And each topic includes cycleName, releaseNumber, and component fields

  Scenario: Search uses "size" parameter instead of "numPerPage"
    When the adapter builds the search request
    Then the pagination parameter is "size" (not "numPerPage")
    And page numbering is 0-indexed

  Scenario: Search maps status filter to correct status IDs
    When the adapter searches with status filter "Open"
    Then the searchParam JSON contains topicReleaseStatus [592]
    When the adapter searches with status filter "Pre-Release"
    Then the searchParam JSON contains topicReleaseStatus [591]

  Scenario: Search normalizes response with new fields
    Given the DSIP API returns a topic with topicId "7051b2da4a1e4c52bd0e7daf80d514f7_86352"
    And the topic has cycleName "DOD_SBIR_2025_P1_C4" and releaseNumber 12 and component "ARMY"
    And the topic has noOfPublishedQuestions 7
    When the adapter normalizes the response
    Then the normalized topic includes cycle_name "DOD_SBIR_2025_P1_C4"
    And the normalized topic includes release_number 12
    And the normalized topic includes published_qa_count 7

  # --- Step 2: Topic Details via API ---

  Scenario: Enrichment fetches structured details instead of PDF-only
    Given topic "7051b2da4a1e4c52bd0e7daf80d514f7_86352" exists for topic code A254-049
    When the enrichment adapter fetches details for this topic
    Then it calls GET /topics/api/public/topics/7051b2da4a1e4c52bd0e7daf80d514f7_86352/details
    And the enriched topic contains a description field with HTML content
    And the enriched topic contains an objective field
    And the enriched topic contains phase1_description, phase2_description fields
    And the enriched topic contains keywords as a parsed list
    And the enriched topic contains technology_areas as an array
    And the enriched topic contains focus_areas as an array
    And the enriched topic contains itar as a boolean
    And the enriched topic contains cmmc_level

  Scenario: Details endpoint returns richer data than PDF extraction
    Given topic A254-049 description via PDF extraction is "The Test and Evaluation community..."
    And topic A254-049 description via details API is "<p>The Test and Evaluation community...</p>"
    When the enrichment adapter fetches details
    Then the description preserves HTML structure
    And technology areas "Information Systems" and "Materials" are available as structured data
    And focus areas "Advanced Computing and Software" and "Microelectronics" are available

  # --- Step 3: Topic Q&A ---

  Scenario: Enrichment fetches Q&A for topics with published questions
    Given topic A254-049 has noOfPublishedQuestions 7
    When the enrichment adapter fetches Q&A for this topic
    Then it calls GET /topics/api/public/topics/7051b2da4a1e4c52bd0e7daf80d514f7_86352/questions
    And the enriched topic contains 7 qa_entries
    And each qa_entry has question_no, question (text), answer (text), and status

  Scenario: Q&A answer JSON is correctly double-parsed
    Given the Q&A response has an answer field containing '{"content": "<p>The parameters listed...</p>"}'
    When the enrichment adapter parses the Q&A
    Then the answer text is "The parameters listed..." (HTML extracted from nested JSON)

  Scenario: Topics with zero published questions skip Q&A fetch
    Given topic CBD254-005 has noOfPublishedQuestions 0
    When the enrichment adapter enriches this topic
    Then no Q&A endpoint call is made for this topic
    And the enriched topic has qa_entries as an empty array
    And no error is recorded

  # --- Step 4: Instruction Documents ---

  Scenario: Enrichment downloads solicitation instructions (BAA preface)
    Given topic A254-049 has cycleName "DOD_SBIR_2025_P1_C4" and releaseNumber 12
    When the enrichment adapter fetches solicitation instructions
    Then it calls GET /submissions/api/public/download/solicitationDocuments
      with solicitation "DOD_SBIR_2025_P1_C4" and release "12" and documentType "RELEASE_PREFACE"
    And the enriched topic contains solicitation_instructions extracted from the PDF

  Scenario: Enrichment downloads component instructions
    Given topic A254-049 has cycleName "DOD_SBIR_2025_P1_C4" and releaseNumber 12 and component "ARMY"
    When the enrichment adapter fetches component instructions
    Then it calls GET /submissions/api/public/download/solicitationDocuments
      with solicitation "DOD_SBIR_2025_P1_C4" and documentType "INSTRUCTIONS" and component "ARMY" and release "12"
    And the enriched topic contains component_instructions extracted from the PDF

  Scenario: Missing instruction PDF does not fail the batch
    Given topic CBD254-005 component "CBD" has no published component instructions
    When the enrichment adapter tries to download component instructions
    And the endpoint returns 404
    Then the enriched topic has component_instructions as null
    And an informational message is logged
    And other topics in the batch are unaffected

  # --- Step 5: Combine and Output ---

  Scenario: Complete enrichment produces all 4 data types
    Given topic A254-049 has been enriched with details, Q&A, and instructions
    When the FinderService combines search metadata with enrichment
    Then the enriched topic output contains description (from details API)
    And the output contains objective, phase descriptions, keywords, technology_areas
    And the output contains qa_entries with 7 entries
    And the output contains solicitation_instructions (from BAA preface PDF)
    And the output contains component_instructions (from ARMY annex PDF)
    And the enrichment_status is "complete"

  Scenario: Completeness metrics report all 4 data types
    Given a batch of 3 topics has been enriched
    And 3 have descriptions, 2 have Q&A, 3 have solicitation instructions, 2 have component instructions
    When the completeness metrics are calculated
    Then the metrics show descriptions: 3, qa: 2, solicitation_instructions: 3, component_instructions: 2, total: 3

  # --- Error Isolation ---

  Scenario: Details endpoint failure does not block Q&A or instructions
    Given the details endpoint returns 500 for topic A254-049
    When the enrichment adapter enriches this topic
    Then the description field is empty
    And Q&A entries are still fetched successfully
    And instruction documents are still fetched successfully
    And the enrichment_status is "partial"
    And the error is recorded in the errors list

  Scenario: Q&A endpoint failure does not block other data types
    Given the Q&A endpoint returns 500 for topic A254-049
    When the enrichment adapter enriches this topic
    Then the description is fetched from the details endpoint
    And instruction documents are still fetched
    And qa_entries is an empty array
    And the enrichment_status is "partial"

  # --- CLI and Agent Interface ---

  Scenario: CLI detail command uses hash ID
    Given Dr. Sarah Chen asks the agent to investigate topic A254-049
    And the agent knows the hash ID "7051b2da4a1e4c52bd0e7daf80d514f7_86352"
    When the agent runs "python scripts/dsip_cli.py detail --topic-id 7051b2da4a1e4c52bd0e7daf80d514f7_86352"
    Then the output JSON contains all 4 data types for this topic

  Scenario: Agent receives enough data for confident recommendation
    Given the sbir-topic-scout agent runs "python scripts/dsip_cli.py enrich --status Open"
    When the CLI returns enriched topics
    Then each topic with published questions includes Q&A entries
    And each topic includes solicitation and component instructions when available
    And the agent can assess government intent from Q&A before recommending GO/EVALUATE/NO-GO

  @property
  Scenario: Per-endpoint failure isolation preserves batch integrity
    Given a batch of N topics is being enriched
    Then a failure on any single endpoint for any single topic
      does not prevent enrichment of other endpoints for that topic
      and does not prevent enrichment of other topics in the batch
