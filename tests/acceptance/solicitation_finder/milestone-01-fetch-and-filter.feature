Feature: Topic Fetching and Keyword Pre-Filter
  As a solo SBIR proposal writer
  I want to fetch open topics and filter them against my company capabilities
  So that I only review topics relevant to my expertise

  Background:
    Given the solicitation finder system is available

  # --- US-SF-001: Fetch Open Topics ---

  # Happy path: fetch all open topics
  Scenario: Fetch all open topics from the solicitation source
    Given Phil has a company profile for "Radiant Defense Systems, LLC"
    And the topic source has 347 open topics for the current cycle
    When Phil searches for matching solicitation topics
    Then the tool retrieves 347 topics
    And the tool displays "Radiant Defense Systems, LLC" as the active company
    And the tool displays a progress indicator during fetching

  # Happy path: fetch with agency and phase filters
  Scenario: Fetch topics filtered by agency and phase
    Given Phil has a company profile for "Radiant Defense Systems, LLC"
    And the topic source has 89 open Air Force Phase I topics
    When Phil searches for Air Force Phase I topics
    Then the tool retrieves 89 topics
    And the active filters show agency "Air Force" and phase "I"

  # Error: topic source unavailable triggers fallback guidance
  Scenario: Unavailable topic source suggests alternative
    Given Phil has a company profile
    And the topic source is unreachable
    When Phil searches for matching solicitation topics
    Then the tool displays "topic source unavailable"
    And the tool suggests providing a solicitation document as a file
    And the tool displays the download location for solicitation documents

  # Error: fallback to solicitation document file
  Scenario: Topics extracted from solicitation document when source unavailable
    Given Phil has a company profile
    And the topic source is unreachable
    And Phil has a solicitation document containing 47 topics
    When Phil searches for topics using the solicitation document
    Then 47 topics are extracted from the document
    And the tool displays "Source: solicitation document (47 topics extracted)"

  # Error: topic source rate-limits after partial retrieval
  Scenario: Partial results offered when source limits further requests
    Given Phil has a company profile
    And the topic source returns 200 topics then limits further requests
    When Phil searches for matching solicitation topics
    Then the tool displays "source rate limit reached after 200 topics"
    And the tool offers to score partial results or retry later

  # --- US-SF-001 + US-SF-002: Keyword Pre-Filter ---

  # Happy path: pre-filter reduces candidate set
  Scenario: Keyword pre-filter eliminates irrelevant topics
    Given the topic source returned 347 open topics
    And the company profile has capabilities "directed energy", "RF power systems", "thermal management"
    When the keyword pre-filter runs
    Then 42 candidate topics are identified
    And 305 topics are eliminated
    And the tool displays "Keyword match: 42 candidate topics (305 eliminated)"

  # Edge: pre-filter is case-insensitive
  Scenario: Pre-filter matches regardless of letter case
    Given the topic source returned a topic titled "DIRECTED ENERGY Systems for Defense"
    And the company profile has capability "directed energy"
    When the keyword pre-filter runs
    Then the topic is included as a candidate

  # Error: zero candidates after pre-filter
  Scenario: No matching topics found after pre-filter
    Given the topic source returned 347 open topics
    And the company profile has capabilities "underwater basket weaving"
    When the keyword pre-filter runs
    Then zero candidates are identified
    And the tool displays "No topics matched your company profile"
    And the tool suggests reviewing the profile or broadening filters

  # Edge: pre-filter with empty capabilities returns all topics with warning
  Scenario: Empty capabilities list passes all topics with warning
    Given the topic source returned 50 open topics
    And the company profile has no capability keywords
    When the keyword pre-filter runs
    Then all 50 topics pass the pre-filter
    And the tool warns "No capability keywords in profile -- all topics passed"

  # --- US-SF-005: No Company Profile ---

  # Error: no profile exists
  Scenario: Missing company profile shows clear guidance
    Given no company profile exists
    When Phil searches for matching solicitation topics
    Then the tool displays "No company profile found"
    And the tool explains that the profile enables matching, eligibility, and personnel alignment
    And the tool suggests creating a profile first

  # Edge: no profile with document file enables degraded mode
  Scenario: Solicitation document processed without profile in degraded mode
    Given no company profile exists
    And Phil has a solicitation document containing 47 topics
    When Phil searches for topics using the solicitation document
    Then the tool warns "No company profile: scoring accuracy severely degraded"
    And 47 topics are listed without five-dimension scoring

  # Edge: incomplete profile with missing sections
  Scenario: Incomplete profile triggers per-section warnings
    Given the company profile has company name and capabilities only
    And the profile has no certifications, past performance, or key personnel
    When Phil searches for matching solicitation topics
    Then the tool warns about each missing profile section
    And scoring proceeds with defaults for missing dimensions
    And recommendations cap at EVALUATE for dimensions with missing data
