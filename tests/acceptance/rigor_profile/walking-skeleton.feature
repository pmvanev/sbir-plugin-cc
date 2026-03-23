Feature: Rigor Profile Walking Skeleton
  As an SBIR proposal author managing proposals of varying strategic value
  I want to set a quality/cost dial per proposal
  So that must-win proposals get maximum effort while exploratory screenings stay cheap

  # Walking Skeleton 1: Author selects a rigor profile and it persists
  # Validates: profile validation -> state write -> state read
  # Driving port: RigorService (application service)
  @walking_skeleton
  Scenario: Elena sets thorough rigor for her must-win proposal
    Given Elena has an active proposal "AF243-001" at "standard" rigor
    When Elena sets the rigor to "thorough"
    Then the active rigor profile is "thorough"
    And the change from "standard" to "thorough" is recorded in history

  # Walking Skeleton 2: Missing rigor config defaults to standard
  # Validates: fallback resolution -> default profile behavior
  # Driving port: RigorService (application service)
  @walking_skeleton
  Scenario: Phil opens a pre-rigor proposal and it works with standard defaults
    Given Phil has a proposal "DA244-007" with no rigor configuration
    When Phil reads the active rigor profile
    Then the rigor profile resolves to "standard"
    And no error is reported

  # Walking Skeleton 3: Model tier resolves from rigor profile for an agent role
  # Validates: profile read -> definition lookup -> tier resolution
  # Driving port: RigorService (resolution chain)
  @walking_skeleton
  Scenario: The writer agent resolves its model tier from the active rigor profile
    Given Elena has an active proposal "AF243-001" at "thorough" rigor
    When the model tier is resolved for the "writer" role
    Then the resolved model tier is "strongest"
