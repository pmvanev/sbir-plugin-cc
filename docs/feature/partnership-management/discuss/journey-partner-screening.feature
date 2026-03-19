Feature: New Partner Readiness Screening
  As an SBIR proposal writer evaluating a potential new partner,
  I want to quickly assess their commitment, bandwidth, and fit,
  so that I can avoid investing weeks in a partnership that may fail.

  Background:
    Given Phil Santos has an active proposal for STTR topic N244-012
    And the proposal deadline is 32 days away

  # Trigger and Setup

  Scenario: Start screening for a new potential partner
    Given Phil is considering SWRI as a new partner
    When Phil runs "/proposal partner-screen"
    Then the tool explains the screening purpose ("assess before investing time")
    And the tool asks for the partner name
    And the tool optionally asks for a target topic reference

  # Readiness Assessment

  Scenario: Timeline commitment assessment with soft signal
    Given Phil enters "SWRI" and topic "N244-012"
    When the tool asks about timeline commitment
    And Phil answers "They said probably in our initial call"
    Then the tool flags this as CAUTION with note "Probably is not a commitment"
    And the tool suggests getting an explicit yes/no by a specific date

  Scenario: Strong commitment signals detected
    Given the tool asks about commitment signals for SWRI
    And Phil reports a named POC (Dr. Rebecca Chen) and preliminary scope agreement
    When the tool evaluates commitment signals
    Then the tool marks named POC as positive signal
    And the tool marks scope agreement as partial (needs formalization)

  Scenario: Prior SBIR/STTR experience assessment
    Given the tool asks about SWRI's SBIR/STTR experience
    And Phil reports "200+ awards across DoD, NASA, DoE"
    When the tool evaluates SBIR experience
    Then the tool marks this as strong positive signal
    And the tool notes the experience reduces coordination risk

  # Capability Fit (when topic provided)

  Scenario: Capability fit assessment against target topic
    Given Phil provided topic N244-012 requiring "autonomous navigation, underwater sensing, real-time processing"
    And SWRI capabilities include "intelligent systems, sensor fusion, autonomy"
    When the tool performs capability fit assessment
    Then the tool shows topic requirements alongside SWRI capabilities and Phil's capabilities
    And the tool identifies SWRI overlap as HIGH (3/3 areas)
    And the tool identifies complementarity as STRONG

  Scenario: Screening without topic skips capability fit
    Given Phil runs "/proposal partner-screen" without specifying a topic
    When the tool proceeds through the screening
    Then the tool evaluates readiness signals only
    And the tool skips the capability fit assessment
    And the tool notes that re-running with a topic would include fit scoring

  # Recommendation

  Scenario: Proceed with caution recommendation
    Given SWRI has strong SBIR experience and a named POC
    And SWRI has a soft timeline commitment and unknown bandwidth
    When the tool generates the screening recommendation
    Then the recommendation is "PROCEED WITH CAUTION"
    And the tool lists 2 strengths and 2 risks
    And the tool suggests 3 concrete next steps to resolve risks
    And Phil can proceed to /proposal partner-setup or wait

  Scenario: Clear proceed recommendation
    Given a potential partner has confirmed timeline, assigned a POC, has SBIR experience, and agreed on scope
    When the tool generates the screening recommendation
    Then the recommendation is "PROCEED"
    And the tool lists all positive signals
    And the tool suggests proceeding directly to /proposal partner-setup

  Scenario: Do not proceed recommendation with critical red flags
    Given a potential partner has no timeline commitment, no named POC, and no SBIR experience
    When the tool generates the screening recommendation
    Then the recommendation is "DO NOT PROCEED"
    And the tool lists 3 critical red flags
    And the tool suggests considering alternative partners
    And the tool references the Q8 risk pattern ("2 of 3 red flags match prior partner dropout")

  # Save and Follow-up

  Scenario: Save screening notes for later review
    Given Phil has completed the screening for SWRI with "PROCEED WITH CAUTION"
    When Phil selects "save"
    Then the screening results are saved to .sbir/partner-screenings/swri.json
    And Phil can retrieve the screening later when following up

  Scenario: Proceed directly to partner setup after positive screening
    Given Phil has completed the screening for SWRI with "PROCEED"
    When Phil selects "proceed"
    Then the tool transitions to /proposal partner-setup with SWRI pre-populated
    And research findings from screening carry forward to the setup interview
