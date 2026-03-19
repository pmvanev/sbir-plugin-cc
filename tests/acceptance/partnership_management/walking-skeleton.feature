Feature: Partnership Management Walking Skeletons
  As an SBIR proposal writer with research institution partners
  I want partner capabilities reflected across scoring, strategy, and drafting
  So that partnered proposals leverage the combined team strengths automatically

  # Walking Skeleton 1: Partner profile validates and persists
  # Validates: partner data -> schema validation -> write to partners dir -> read back
  @walking_skeleton
  Scenario: Proposal writer creates a validated partner profile and retrieves it
    Given Phil has no partner profiles on file
    And Phil has prepared a complete partner profile for "CU Boulder" as a university
    And the profile includes capabilities "autonomous navigation, underwater acoustics, sensor fusion"
    And the profile includes key personnel "Dr. Sarah Kim" as Co-PI with expertise "autonomous navigation, underwater acoustics"
    And the profile includes facility "underwater acoustics lab"
    When Phil submits the partner profile for validation and saving
    Then the partner profile passes validation with no errors
    And the partner profile is saved to the partners directory as "cu-boulder.json"
    And when Phil retrieves the partner profile the partner name is "CU Boulder"
    And the retrieved profile contains 3 capabilities

  # Walking Skeleton 2: Partnership elevates topic scoring
  # Validates: company profile + partner profile -> combined scoring -> recommendation change
  # Note: STTR topic without a research institution partner produces NO-GO (disqualifier).
  # Adding CU Boulder as partner removes the disqualifier and elevates the score.
  @walking_skeleton
  Scenario: Partnership scoring elevates an STTR topic from NO-GO to GO
    Given Phil has a company profile with capabilities "directed energy, RF engineering, machine learning"
    And Phil has a partner profile for "CU Boulder" with capabilities "autonomous navigation, underwater acoustics, sensor fusion"
    And CU Boulder is a qualifying research institution of type "university"
    And STTR topic "N244-012" requires expertise in "autonomous navigation underwater acoustics"
    When the topic is scored for Phil's company alone
    Then the solo recommendation is NO-GO
    When the topic is scored with CU Boulder as partner
    Then the partnership recommendation is GO
    And the partnership score is higher than the solo score

  # Walking Skeleton 3: Partner designation flows to strategy brief
  # Validates: partner designation in state -> strategy reads partner -> teaming section generated
  @walking_skeleton @skip
  Scenario: Designated partner data appears in strategy brief teaming section
    Given Phil has a partner profile for "CU Boulder" with Co-PI "Dr. Sarah Kim"
    And CU Boulder has facilities "underwater acoustics lab, GPU compute cluster"
    And Phil has designated CU Boulder as the partner for the current proposal
    When the strategy brief teaming section is generated
    Then the teaming section names "Dr. Sarah Kim" as Co-PI
    And the teaming section lists "underwater acoustics lab" as a facility
    And the teaming section shows a capability complementarity analysis
