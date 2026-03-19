Feature: Partnership-Aware Approaches and Strategy (US-PM-004, US-PM-003)
  As an SBIR proposal writer generating approaches and strategy for a partnered proposal
  I want approaches and strategy to reflect the combined team capabilities
  So that the proposal demonstrates credible partnership with concrete work splits

  # --- US-PM-004: Partnership-Aware Approach Generation ---

  @skip
  Scenario: Approach generation uses combined capability set
    Given Phil has a company profile with capabilities "directed energy, RF engineering, machine learning"
    And Phil has a partner profile for "CU Boulder" with capabilities "autonomous navigation, underwater acoustics, sensor fusion"
    And Phil is generating approaches for STTR topic "N244-012" requiring "autonomous navigation, underwater sensing"
    When approach options are generated with partnership context
    Then at least one approach references CU Boulder capabilities
    And the approach includes a work split between Phil's company and CU Boulder

  @skip
  Scenario: Each approach shows explicit work split percentages
    Given Phil is generating approaches for an STTR topic with CU Boulder as partner
    When approach options are generated with partnership context
    Then every approach includes a company percentage and a partner percentage
    And the two percentages sum to 100

  @skip
  Scenario: STTR approach enforces 30 percent minimum partner allocation
    Given Phil is generating approaches for an STTR Phase I topic with CU Boulder
    When approach work splits are validated
    Then every approach allocates at least 30 percent to CU Boulder
    And approaches below 30 percent are flagged as STTR non-compliant

  @skip
  Scenario: Weak partnership utilization flagged when capabilities do not match
    Given Phil has a partner profile for "CU Boulder" with capabilities "autonomous navigation, underwater acoustics"
    And Phil is generating approaches for a cybersecurity topic
    When approach options are generated with partnership context
    Then the tool flags that approaches do not strongly leverage CU Boulder
    And the tool suggests considering a different partner or the SBIR track

  @skip
  Scenario: Non-partnered proposal generates approaches without partner references
    Given Phil has no designated partner for the current proposal
    When approach options are generated
    Then no approach references any partner institution
    And approach generation matches current non-partnership behavior

  # --- US-PM-003: Partnership-Aware Strategy Brief ---

  @skip
  Scenario: Teaming section auto-generated from partner profile
    Given Phil has selected approach "Acoustic-Inertial Fusion" for topic "N244-012"
    And CU Boulder is the designated partner with Co-PI "Dr. Sarah Kim"
    And CU Boulder has facilities "underwater acoustics lab, GPU compute cluster"
    And the approach brief allocates 40 percent to CU Boulder
    When the strategy brief is generated with partnership context
    Then the teaming section names "Dr. Sarah Kim" as Co-PI
    And the teaming section lists "underwater acoustics lab" as a facility
    And the teaming section shows capability complementarity between both entities
    And the work split percentage matches the approach brief at 40 percent

  @skip
  Scenario: Teaming section cites partner profile as data source
    Given a teaming section has been generated using CU Boulder data
    When the teaming section attribution is checked
    Then the source cites the partner profile file
    And all personnel names match the partner profile exactly

  @skip
  Scenario: Missing partner data flagged but does not block strategy generation
    Given the partner profile for "CU Boulder" has no facilities listed
    When the strategy brief teaming section is generated
    Then the facilities subsection notes that facilities are not provided in the partner profile
    And the rest of the teaming section generates normally
    And the strategy brief is not blocked

  @skip
  Scenario: Non-partnered proposal has standard teaming section
    Given no partner is designated for SBIR topic "AF243-001"
    When the strategy brief is generated
    Then the teaming section uses standard non-partnered language
    And no partner-specific content appears in the teaming section

  # --- Boundary: Consistency ---

  @property @skip
  Scenario: Work split percentages are consistent across approach and strategy
    Given any approach with a partner work split
    When the strategy brief references the approach work split
    Then the strategy brief percentage matches the approach brief percentage exactly
