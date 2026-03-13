Feature: Company Profile Extraction and Update
  As a small business founder pursuing SBIR/STTR grants
  I want to extract profile data from documents and update sections selectively
  So that I can maintain my profile efficiently as my company changes

  Background:
    Given the profile builder system is available

  # --- US-CPB-003: Document Extraction ---
  # Note: Document extraction is agent behavior (LLM-driven).
  # These scenarios validate the Python-testable outcomes:
  # merge logic, gap identification, and validation of extracted data.

  # Happy path: extracted data merges into profile draft
  @skip
  Scenario: Extracted fields from a document populate the profile draft
    Given a document extraction produced company name "Radiant Defense Systems, LLC"
    And the extraction produced capabilities "directed energy, RF systems"
    And the extraction produced employee count 23
    When the extracted data is assembled into a profile draft
    Then the draft contains company name "Radiant Defense Systems, LLC"
    And the draft contains 2 capabilities
    And the draft contains employee count 23

  # Happy path: multiple extractions merge additively
  @skip
  Scenario: Data from multiple documents combines into a single profile
    Given a first extraction produced company name and capabilities
    And a second extraction produced SAM.gov details with CAGE "7X2K9" and UEI "DKJF84NXLE73"
    When both extractions are merged into the profile draft
    Then the draft contains data from both sources
    And the SAM.gov section shows active with CAGE "7X2K9"

  # Edge: partial extraction leaves gaps
  @skip
  Scenario: Partially extracted profile identifies missing fields
    Given a document extraction produced only company name and employee count
    When the draft is checked for completeness
    Then the following sections are identified as missing:
      | missing_section          |
      | capabilities             |
      | certifications           |
      | key_personnel            |
      | past_performance         |
      | research_institution_partners |

  # Error: no extractable data produces empty draft
  @skip
  Scenario: Extraction with no profile data leaves the draft empty
    Given a document extraction found no profile-relevant fields
    When the extracted data is assembled into a profile draft
    Then the draft has no populated fields

  # Error: extracted data fails validation
  @skip
  Scenario: Extracted data with invalid values is caught during validation
    Given a document extraction produced CAGE code "AB" and employee count 0
    When the extracted profile draft is validated
    Then validation reports errors for the invalid fields

  # --- US-CPB-004: Selective Section Update ---

  # Happy path: add past performance entry
  @skip
  Scenario: Adding a past performance entry to an existing profile
    Given Rafael has a saved profile with 2 past performance entries
    When Rafael adds a past performance entry for agency "NASA" with topic "Lunar Surface Power" and outcome "awarded"
    And the updated profile is validated and saved
    Then the profile contains 3 past performance entries
    And the new entry shows agency "NASA"
    And the previous 2 entries are unchanged

  # Happy path: add key personnel
  @skip
  Scenario: Adding a team member preserves existing personnel
    Given Rafael has a saved profile with 2 key personnel
    When Rafael adds key personnel "Dr. James Chen" as "Senior RF Engineer" with expertise "signal processing, antenna design"
    And the updated profile is validated and saved
    Then the profile contains 3 key personnel entries
    And the original 2 personnel entries are unchanged

  # Happy path: update scalar field
  @skip
  Scenario: Updating employee count replaces the value
    Given Rafael has a saved profile with employee count 23
    When Rafael updates the employee count to 28
    And the updated profile is validated and saved
    Then the profile shows employee count 28

  # Error: update when no profile exists
  @skip
  Scenario: Updating a profile that does not exist reports the absence
    Given no company profile exists
    When Rafael attempts to update a profile section
    Then the system reports that no profile was found
    And suggests creating a profile first

  # Edge: update preserves all unmodified sections
  @skip
  Scenario: Updating one section leaves all other sections intact
    Given Rafael has a saved profile with:
      | section              | entry_count |
      | capabilities         | 5           |
      | key_personnel        | 2           |
      | past_performance     | 2           |
      | research_partners    | 1           |
    When Rafael updates only the employee count to 30
    And the updated profile is validated and saved
    Then capabilities still has 5 entries
    And key personnel still has 2 entries
    And past performance still has 2 entries
    And research partners still has 1 entry

  # Error: update with invalid data is rejected
  @skip
  Scenario: Update that introduces invalid data is rejected
    Given Rafael has a saved profile with valid CAGE code "7X2K9"
    When Rafael attempts to update the CAGE code to "AB"
    And the updated profile is validated
    Then validation rejects the update with a CAGE code error
    And the original profile is not modified

  # Edge: update SAM.gov from inactive to active
  @skip
  Scenario: Activating SAM.gov registration requires CAGE and UEI
    Given Rafael has a saved profile with SAM.gov inactive
    When Rafael updates SAM.gov to active with CAGE "7X2K9" and UEI "DKJF84NXLE73"
    And the updated profile is validated and saved
    Then the profile shows SAM.gov active with CAGE "7X2K9"

  @property
  @skip
  Scenario: Updating a section never changes unrelated sections
    Given any valid existing profile and any valid section update
    When the update is applied to the selected section
    Then all unrelated sections remain identical to the original
