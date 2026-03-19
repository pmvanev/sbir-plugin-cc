Feature: DSIP Topic Scraper Walking Skeleton
  As a solo SBIR proposal writer
  I want to fetch topics from DSIP, enrich them with detailed descriptions, and score them
  So that I can discover and evaluate DoD opportunities without manually browsing the portal

  # Walking Skeleton 1: Fetch topics from DSIP, pre-filter, enrich, and see enriched candidates
  # Validates: DSIP source -> pre-filter -> enrichment -> candidate list with completeness report
  @walking_skeleton
  Scenario: Proposal writer discovers and enriches DSIP topics for evaluation
    Given Phil has a company profile for "Radiant Defense Systems, LLC" with capabilities "directed energy", "RF power systems", "thermal management"
    And the topic source has 247 open topics for the current solicitation cycle
    And each candidate topic has a downloadable description document
    When Phil searches for matching solicitation topics with enrichment
    Then 42 candidate topics are identified from 247 total
    And each candidate topic includes a description with at least 500 characters
    And the enrichment report shows "Descriptions: 42/42"
    And enriched topics are cached for reuse within 24 hours

  # Walking Skeleton 2: End-to-end scrape, enrich, score, and see ranked results
  # Validates: fetch -> filter -> enrich -> score -> ranked table with recommendations
  @walking_skeleton @skip
  Scenario: Proposal writer sees scored and ranked DSIP topics with enriched descriptions
    Given Phil has a company profile with capabilities, certifications, and past performance
    And 42 candidate topics have been enriched with descriptions and scored
    And topic "AF263-042" scored 0.84 with recommendation GO
    And topic "N263-044" scored 0.62 with recommendation GO
    And topic "AF263-115" scored 0.41 with recommendation EVALUATE
    When Phil views the finder results
    Then the ranked table shows topics sorted by score descending
    And topic "AF263-042" appears first with recommendation GO
    And the completeness metrics show descriptions, instructions, and Q&A counts
    And results are saved for later review

  # Walking Skeleton 3: Use cached DSIP data to avoid re-scraping
  # Validates: cache check -> fresh data reuse -> scoring on cached data
  @walking_skeleton @skip
  Scenario: Proposal writer reuses cached DSIP data without re-scraping
    Given Phil searched for DSIP topics yesterday and results were cached
    And the cached data is less than 24 hours old
    When Phil searches for matching solicitation topics
    Then the tool offers to use the cached data
    And when Phil accepts, scoring runs immediately on cached data
    And no new requests are made to the topic source
