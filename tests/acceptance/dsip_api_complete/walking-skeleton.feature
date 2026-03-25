Feature: DSIP API Fix Walking Skeletons
  As a solo SBIR proposal writer
  I want topic search to return only current-cycle topics with enriched details, Q&A, and instructions
  So that I can make informed go/no-go decisions based on complete topic intelligence

  # Walking Skeleton 1: Search returns filtered topics with hash IDs
  # Validates: corrected search query -> filtered results -> hash IDs -> normalized metadata
  @walking_skeleton
  Scenario: Proposal writer searches for open topics and sees only current-cycle results
    Given Phil has a company profile for "Radiant Defense Systems, LLC" with capabilities "directed energy", "RF power systems", "thermal management"
    And the DSIP portal has 24 topics in the current solicitation cycle
    When Phil searches for open solicitation topics
    Then at most 24 topics are returned
    And each topic has a hash identifier containing an underscore
    And each topic includes the solicitation cycle name, release number, and component
    And each topic includes the count of published Q&A entries

  # Walking Skeleton 2: Full enrichment pipeline with all 4 data types
  # Validates: search -> enrich (details + Q&A + instructions) -> completeness report
  @walking_skeleton @skip
  Scenario: Proposal writer enriches topics and sees descriptions, Q&A, and instruction documents
    Given Phil has a company profile with capabilities "directed energy" and "RF power systems"
    And the DSIP portal has 24 topics in the current solicitation cycle
    And each topic has structured details, Q&A entries, and instruction documents available
    When Phil searches for matching topics with enrichment
    Then each enriched topic includes a description, objective, and keywords
    And topics with published questions include Q&A entries with government responses
    And each enriched topic includes solicitation instructions extracted from the BAA preface
    And the completeness report shows counts for descriptions, Q&A, solicitation instructions, and component instructions
