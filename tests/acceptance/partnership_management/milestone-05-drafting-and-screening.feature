Feature: Partnership Drafting and Partner Screening (US-PM-007, US-PM-005)
  As an SBIR proposal writer drafting partnered proposals and evaluating new partners
  I want draft sections to reference real partner data and new partners screened for readiness
  So that proposals are credible and partner investments are protected

  # --- US-PM-007: Partnership Content in Drafting ---

  @skip
  Scenario: Draft section references partner by name with real personnel and facilities
    Given a strategy brief exists with teaming section for CU Boulder
    And CU Boulder profile includes "Dr. Sarah Kim" and "underwater acoustics lab"
    When the Technical Approach section is drafted with partnership context
    Then the draft names CU Boulder as the partner institution
    And the draft names "Dr. Sarah Kim" and her expertise
    And the draft mentions the "underwater acoustics lab"
    And the work split in the draft matches the strategy brief

  @skip
  Scenario: Non-partnered proposal produces standard draft content
    Given no partner is designated for the current proposal
    When the Technical Approach section is drafted
    Then the draft does not reference any partner institution
    And the draft does not include any partnership narrative

  @skip
  Scenario: Sparse partner data used without fabrication
    Given the partner profile has only 1 key personnel and no facilities
    When the draft section is generated with partnership context
    Then the draft names the 1 available person with their expertise
    And the draft does not fabricate facilities or additional personnel
    And the draft notes where additional partner detail would strengthen the narrative

  @skip
  Scenario: Personnel names in draft match partner profile exactly
    Given the partner profile lists "Dr. Sarah Kim" with expertise "autonomous navigation, underwater acoustics"
    When the draft section references partner personnel
    Then the name "Dr. Sarah Kim" appears exactly as stored in the partner profile
    And the expertise keywords match the partner profile exactly

  # --- US-PM-005: New Partner Readiness Screening ---

  @skip
  Scenario: Screening with mixed signals produces cautious recommendation
    Given Phil is screening "SWRI" for topic "N244-012"
    And SWRI has strong SBIR experience with 200 awards
    And SWRI has a named POC "Dr. Rebecca Chen"
    And SWRI has a soft timeline commitment rated as caution
    And SWRI has unknown bandwidth rated as unknown
    And SWRI has preliminary scope agreement rated as caution
    When the screening recommendation is computed
    Then the recommendation is "PROCEED WITH CAUTION"
    And the screening lists 2 strengths and 3 risks
    And the screening suggests concrete next steps to resolve risks

  @skip
  Scenario: All positive signals produce proceed recommendation
    Given all 5 readiness signals are rated as ok for a potential partner
    When the screening recommendation is computed
    Then the recommendation is "PROCEED"
    And the screening suggests proceeding directly to partner setup

  @skip
  Scenario: Critical red flags produce do-not-proceed recommendation
    Given a potential partner has timeline rated as unknown
    And the partner has no named POC rated as unknown
    And the partner has no SBIR experience rated as caution
    And the partner has no scope agreement rated as unknown
    And the partner has unknown bandwidth rated as unknown
    When the screening recommendation is computed
    Then the recommendation is "DO NOT PROCEED"
    And the screening lists critical red flags

  @skip
  Scenario: Capability fit assessed when topic is provided
    Given Phil is screening "SWRI" with topic "N244-012" requiring "autonomous navigation, underwater sensing"
    And SWRI capabilities include "intelligent systems, sensor fusion, autonomy"
    When the screening includes capability fit assessment
    Then the capability fit is rated as HIGH
    And the assessment shows topic requirements alongside SWRI and Phil's capabilities

  @skip
  Scenario: Screening results save and reload correctly
    Given Phil has completed a screening for "SWRI" with recommendation "PROCEED WITH CAUTION"
    When the screening results are saved
    And the screening results are reloaded
    Then the reloaded recommendation is "PROCEED WITH CAUTION"
    And the reloaded screening has 5 signal ratings
    And the reloaded screening has next steps

  @skip
  Scenario: Screening without topic skips capability fit
    Given Phil runs screening for "SWRI" without specifying a topic
    When the screening is computed
    Then the capability fit is noted as not assessed
    And the screening recommends re-running with a topic for fit scoring

  @property @skip
  Scenario: Screening recommendation is always one of three valid values
    Given any combination of readiness signal ratings
    When the screening recommendation is computed
    Then the recommendation is one of "PROCEED", "PROCEED WITH CAUTION", or "DO NOT PROCEED"
