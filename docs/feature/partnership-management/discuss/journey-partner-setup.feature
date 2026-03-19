Feature: Partner Profile Setup
  As an SBIR proposal writer with research institution partners,
  I want to build rich partner profiles through conversational interview,
  so that all proposal agents can generate partnership-aware content.

  Background:
    Given Phil Santos has a company profile at ~/.sbir/company-profile.json
    And the company profile includes capabilities "directed energy, RF engineering, machine learning"

  # Step 1: Mode Select

  Scenario: List existing partners on setup entry
    Given partner profiles exist for "CU Boulder" and "NDSU" in ~/.sbir/partners/
    When Phil runs "/proposal partner-setup"
    Then the tool displays "CU Boulder (university)" in the partner list
    And the tool displays "NDSU (university)" in the partner list
    And the tool offers options: new, update, list, cancel

  Scenario: Start new partner profile
    Given no partner profile exists for "SWRI"
    When Phil runs "/proposal partner-setup" and selects "new"
    Then the tool asks for the partner name and type
    And the tool proceeds to the research phase

  Scenario: Update existing partner profile
    Given a partner profile exists for "CU Boulder" last updated 2026-01-15
    When Phil runs "/proposal partner-setup" and selects "update" for "CU Boulder"
    Then the tool loads the existing CU Boulder profile
    And the tool asks which sections to update

  # Step 2: Research

  Scenario: Web research pre-populates partner data
    Given Phil is creating a new partner profile for "Southwest Research Institute"
    When the tool searches for SWRI's public information
    Then the tool displays SBIR/STTR award count
    And the tool displays research areas
    And the tool displays key personnel found
    And the tool displays a confidence level
    And Phil can continue with findings or discard them

  Scenario: Web research finds nothing for unknown institution
    Given Phil is creating a new partner profile for "Acme Research Lab"
    When the tool searches for public information and finds nothing
    Then the tool reports "No public data found for Acme Research Lab"
    And the tool proceeds directly to interview mode
    And the workflow is not blocked

  # Step 3: Gather

  Scenario: Interview collects all six sections with fit scoring explanations
    Given Phil is in interview mode for partner "SWRI"
    When the tool walks through section "Capabilities"
    Then the tool explains that capabilities keywords are matched against solicitations alongside the company keywords
    And the tool explains that the COMBINED keyword set determines partnership fit scoring
    And Phil can provide capability keywords

  Scenario: Pre-populated fields from research can be confirmed or edited
    Given research found capabilities "intelligent systems, space science, defense technology" for SWRI
    When the tool presents section "Capabilities" during interview
    Then the tool shows the pre-populated values from research
    And Phil can confirm with "y", reject with "n", or edit individual values

  Scenario: Skipping optional sections records empty values
    Given Phil is in interview mode for partner "SWRI"
    When Phil says "skip" for section "Past Collaborations"
    Then the tool records an empty array for past_collaborations
    And the tool proceeds to the next section
    And the tool does not warn about scoring impact for past_collaborations

  # Step 4: Preview

  Scenario: Preview shows partner profile and combined analysis
    Given Phil has completed all interview sections for SWRI
    And SWRI capabilities are "intelligent systems, autonomy, sensor fusion, applied ML"
    And Phil's company capabilities are "directed energy, RF engineering, machine learning"
    When the tool displays the preview
    Then the tool shows the complete SWRI profile
    And the tool shows a combined profile analysis
    And the tool identifies "machine learning / applied ML" as capability overlap
    And the tool identifies "directed energy, RF engineering" as unique to Phil's company
    And the tool identifies "autonomy, sensor fusion" as unique to SWRI

  Scenario: Edit from preview returns to specific section
    Given Phil is viewing the preview for SWRI
    When Phil selects "edit" and specifies "Key Personnel"
    Then the tool returns to the Key Personnel section
    And Phil can modify the data
    And the tool returns to preview after the edit

  # Step 5: Validate and Save

  Scenario: Successful save with atomic write
    Given Phil confirms save for the SWRI partner profile
    And the profile passes schema validation
    When the tool saves the profile
    Then the file is written to ~/.sbir/partners/swri.json
    And the tool confirms the save location
    And the tool lists which commands can now use the partner data
    And the tool suggests next steps

  Scenario: Validation failure with actionable errors
    Given Phil confirms save for a partner profile
    And the profile has empty capabilities array
    When the tool validates the profile
    Then the tool displays "capabilities: must have at least 1 keyword"
    And the tool returns to preview for correction
    And no file is written

  Scenario: Cancel at any point writes no files
    Given Phil is in the middle of partner interview for SWRI
    When Phil says "cancel"
    Then the tool confirms "Partner profile creation cancelled. No files written or modified."
    And no partner profile file exists for SWRI

  # Overwrite Protection

  Scenario: Existing partner profile triggers overwrite protection
    Given a partner profile exists for "CU Boulder"
    When Phil selects "new" and enters "CU Boulder" as the partner name
    Then the tool detects the existing profile
    And the tool offers: fresh (backup + overwrite), update (modify sections), cancel
    And the tool does not silently overwrite

  # Error: Partner Profile Schema

  @property
  Scenario: Partner profile schema mirrors company profile structure
    Given a partner profile is saved
    Then the profile contains capabilities as an array of keyword strings
    And the profile contains key_personnel with name, role, and expertise arrays
    And the profile contains a type field with valid institution type
    And the profile contains facilities as an array of strings
    And the profile contains past_collaborations as an array of records
