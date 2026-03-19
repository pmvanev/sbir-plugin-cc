Feature: Partnership-Aware AI Suggestions
  As an SBIR proposal writer with partner profiles on file,
  I want existing proposal agents to factor in partner capabilities,
  so that scoring, approaches, strategy, and drafting reflect the combined team.

  Background:
    Given Phil Santos has a company profile with capabilities "directed energy, RF engineering, machine learning"
    And a partner profile exists for "CU Boulder" with capabilities "autonomous navigation, underwater acoustics, sensor fusion"
    And CU Boulder has key personnel "Dr. Sarah Kim, Co-PI, autonomous navigation, underwater acoustics"

  # Partnership-Aware Topic Scoring

  Scenario: STTR topic scoring shows company-only and partnership columns
    Given STTR topic N244-012 "Autonomous UUV Navigation" requires "autonomous navigation, underwater sensing, real-time processing"
    When Phil runs "/solicitation-find" with partnership scoring enabled
    Then the tool displays a "You Only" scoring column
    And the tool displays a "+ CU Boulder" scoring column
    And the tool displays a "Delta" column showing score differences
    And the STTR dimension shows 0.50 (solo) vs 1.00 (partnership)

  Scenario: Partnership elevates topic from EVALUATE to GO
    Given STTR topic N244-012 scores 0.56 composite for Phil's company alone (EVALUATE)
    And the combined score with CU Boulder is 0.82 (GO)
    When Phil views the scoring results
    Then the tool displays "Partnership elevated this topic from EVALUATE to GO"
    And the tool lists which partner capabilities drove the elevation

  Scenario: Partnership scoring shows minimal impact when partner does not fit
    Given SBIR topic AF243-001 requires "directed energy, power systems, thermal management"
    And CU Boulder's capabilities do not overlap with topic requirements
    When Phil runs "/solicitation-find" with partnership scoring enabled
    Then the Delta column shows less than +0.05 for all dimensions
    And the tool notes "Partnership has minimal impact on this topic"
    And the tool suggests the topic may be better pursued solo

  Scenario: No partner profile prompts setup for STTR topics
    Given no partner profiles exist
    And Phil is scoring STTR topic N244-012
    When the tool encounters the STTR dimension
    Then the tool displays "STTR topic -- no partner profiles found"
    And the tool displays STTR score as 0.0
    And the tool suggests "/proposal partner-setup" to create a partner profile

  # Partnership-Aware Approach Generation

  Scenario: Approach generation leverages combined capabilities
    Given Phil has selected topic N244-012 and partner CU Boulder
    When Phil runs "/proposal-shape"
    Then the tool generates approaches that reference CU Boulder's capabilities
    And at least one approach includes a work split with CU Boulder
    And the recommended approach explains which partner capabilities it leverages
    And work split percentages are shown for each approach

  Scenario: Approach flags when partner capabilities are not leveraged
    Given Phil has selected a cybersecurity topic and partner CU Boulder
    When Phil runs "/proposal-shape"
    Then the tool generates approaches based on Phil's capabilities
    And the tool flags that none of the approaches strongly leverage CU Boulder
    And the tool suggests considering a different partner or the SBIR track

  Scenario: STTR approach enforces minimum partner work percentage
    Given Phil is working on an STTR Phase I proposal with CU Boulder
    When the tool generates approach work splits
    Then every STTR-eligible approach allocates at least 30% of work to CU Boulder
    And approaches below the 30% threshold are flagged as STTR non-compliant

  # Partnership-Aware Strategy Brief

  Scenario: Strategy brief auto-generates teaming section from partner profile
    Given Phil has selected approach "Acoustic-Inertial Fusion" for topic N244-012
    And CU Boulder is the designated partner
    When Phil runs "/proposal-wave-strategy"
    Then the strategy brief includes a teaming section
    And the teaming section names "Dr. Sarah Kim" as Co-PI
    And the teaming section lists CU Boulder facilities
    And the teaming section shows a capability complementarity matrix
    And the work split matches the approach brief percentages

  Scenario: Teaming section cites partner profile as data source
    Given the strategist agent generates a teaming section
    When Phil reviews the strategy brief
    Then the teaming section includes a source attribution to the partner profile file
    And all personnel names in the teaming section match the partner profile exactly
    And all facility claims trace to the partner profile facilities field

  # Partnership-Aware Drafting

  Scenario: Proposal draft references partner capabilities with real names
    Given a strategy brief exists with teaming section for CU Boulder
    When Phil runs "/proposal-draft" for the Technical Approach section
    Then the draft text references CU Boulder by name
    And the draft text names Dr. Sarah Kim and her expertise
    And the draft text mentions specific CU Boulder facilities
    And the draft text describes the work split consistent with the strategy brief

  Scenario: Draft with no partner profile produces standard (non-partnered) content
    Given no partner profile is associated with the current proposal
    When Phil runs "/proposal-draft" for the Technical Approach section
    Then the draft does not reference any partner institution
    And the draft does not include a teaming narrative
    And this is identical to the current non-partnership behavior

  # Cross-Agent Consistency

  @property
  Scenario: Partner data consistency across all consuming agents
    Given a partner profile exists and is associated with a proposal
    Then the partner name is identical in scoring, approach brief, strategy brief, and draft
    And partner personnel names are identical across strategy brief and draft
    And work split percentages are identical across approach brief, strategy brief, and draft
    And capability claims trace to partner profile keywords in every agent output
