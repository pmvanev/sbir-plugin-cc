Feature: Company Profile Builder
  As a small business founder pursuing SBIR/STTR grants
  I want to create my company profile through guided conversation and document extraction
  So that fit scoring can accurately match me to solicitation topics

  Background:
    Given the SBIR proposal plugin is installed
    And the company profile schema requires: company_name, capabilities, certifications, employee_count, key_personnel, past_performance, research_institution_partners

  # --- Step 1: Start Profile Builder ---

  Scenario: Start profile builder with no existing profile
    Given Rafael Medina has no company profile at ~/.sbir/company-profile.json
    When Rafael runs "/sbir:proposal profile setup"
    Then the builder explains that the profile powers fit scoring
    And the builder offers three approaches: documents, interview, or both
    And the target path ~/.sbir/company-profile.json is displayed

  Scenario: Start profile builder with existing profile
    Given Rafael Medina has an existing company profile at ~/.sbir/company-profile.json
    And the profile was last modified on 2026-01-15
    And the profile contains company name "Radiant Defense Systems, LLC"
    When Rafael runs "/sbir:proposal profile setup"
    Then the builder warns that an existing profile was found
    And the builder shows the company name and last modified date
    And the builder offers: start fresh (with backup), update existing, or cancel

  Scenario: Existing profile is backed up before overwrite
    Given Rafael has an existing profile and chose "start fresh"
    When the builder proceeds with a new profile
    Then the existing profile is copied to company-profile.json.bak
    And the builder confirms the backup location

  # --- Step 2: Document Extraction ---

  Scenario: Extract profile data from capability statement PDF
    Given Rafael chose the "documents first" approach
    When Rafael provides the path "./docs/radiant-cap-statement.pdf"
    And the builder reads the document
    Then the builder extracts and displays:
      | Field            | Value                                    |
      | company_name     | Radiant Defense Systems, LLC             |
      | capabilities     | directed energy, RF systems, power electronics, thermal management, embedded firmware |
      | employee_count   | 23                                       |
      | key_personnel    | 2 people extracted                       |
      | past_performance | 2 entries extracted                       |
    And the builder lists fields not found in the document:
      | Missing Field              |
      | SAM.gov registration       |
      | socioeconomic certifications |
      | security clearance         |
      | ITAR registration          |
      | research institution partners |

  Scenario: Extract profile data from SAM.gov URL
    Given Rafael chose the "documents first" approach
    When Rafael provides a SAM.gov entity page URL
    And the builder fetches the page content
    Then the builder extracts SAM.gov registration status, CAGE code, and UEI
    And the builder extracts socioeconomic certifications if listed
    And the builder displays what was found and what remains missing

  Scenario: Document cannot be read
    Given Rafael chose the "documents first" approach
    When Rafael provides "./docs/cap-statement.docx"
    And the builder cannot read the file format
    Then the builder displays an error explaining the format is not supported
    And the builder suggests: export to PDF, copy to text, or skip to interview
    And Rafael can continue without the document

  Scenario: No relevant data extracted from document
    Given Rafael chose the "documents first" approach
    When Rafael provides a document that contains no profile-relevant information
    Then the builder reports that no profile fields were found
    And the builder suggests trying a different document or switching to interview mode
    And the profile draft remains empty

  # --- Step 3: Interview for Gaps ---

  Scenario: Fill SAM.gov details through interview
    Given the builder has extracted some fields from documents
    And SAM.gov registration details are missing
    When the builder asks about SAM.gov registration
    And Rafael responds that SAM.gov is active with CAGE code "7X2K9" and UEI "DKJF84NXLE73"
    Then the builder records sam_gov.active as true
    And the builder records sam_gov.cage_code as "7X2K9"
    And the builder records sam_gov.uei as "DKJF84NXLE73"

  Scenario: Fill socioeconomic certifications through interview
    Given socioeconomic certifications are missing from the profile draft
    When the builder presents the certification options: 8(a), HUBZone, WOSB, SDVOSB, VOSB, None
    And Rafael selects "None of the above"
    Then the builder records socioeconomic as an empty list
    And the builder notes this can be updated later

  Scenario: Fill security clearance through interview
    Given security clearance level is missing from the profile draft
    When the builder asks about the highest facility clearance level
    And Rafael responds "Secret"
    Then the builder records security_clearance as "secret"

  Scenario: Add research institution partner through interview
    Given research institution partners are missing from the profile draft
    When the builder asks about formal university or research lab partnerships
    And Rafael responds "We have an MOU with Georgia Tech Research Institute"
    Then the builder adds "Georgia Tech Research Institute" to research_institution_partners

  Scenario: Full interview mode without documents
    Given Rafael chose the "interview only" approach
    When the builder begins the interview
    Then the builder asks about each profile section in order:
      | Section                      | Question Pattern                        |
      | company_name                 | What is your company's legal name?      |
      | capabilities                 | What are your core technical capabilities? |
      | certifications               | SAM.gov, socioeconomic, clearance, ITAR |
      | employee_count               | How many employees?                     |
      | key_personnel                | Who are your key technical personnel?   |
      | past_performance             | What SBIR/STTR awards or contracts?     |
      | research_institution_partners | Any university/lab partnerships?        |
    And each question explains why the field matters for fit scoring

  # --- Step 4: Preview and Validate ---

  Scenario: Preview shows complete validated profile
    Given all profile fields have been populated through extraction and interview
    And the profile draft passes schema validation
    When the builder displays the profile preview
    Then all fields are shown in a human-readable format
    And validation status shows "PASSED (all required fields present)"
    And Rafael is asked to confirm with "yes", "edit", or "cancel"

  Scenario: Preview shows validation failures
    Given the profile draft has a CAGE code "7X2K" (4 characters instead of 5)
    And employee_count is 0
    When the builder displays the profile preview
    Then validation status shows "2 issues found"
    And the builder explains each issue:
      | Issue                              | Detail                          |
      | CAGE code format                   | 4 characters, expected 5        |
      | Employee count                     | 0 is invalid for SBIR eligibility |
    And Rafael is asked to fix the issues before saving

  Scenario: Edit a field during preview
    Given the profile preview is displayed
    And Rafael notices that a capability keyword is wrong
    When Rafael says "edit capabilities"
    Then the builder presents the current capabilities list
    And Rafael can add, remove, or replace keywords
    And the preview updates with the corrected values

  # --- Step 5: Confirm and Save ---

  Scenario: Save profile after confirmation
    Given Rafael has reviewed the profile preview
    And validation status is "PASSED"
    When Rafael confirms with "yes"
    Then the profile is saved to ~/.sbir/company-profile.json
    And the file is valid JSON matching the expected schema
    And the builder confirms the save location
    And the builder suggests "/sbir:proposal new" as the next step

  Scenario: Cancel without saving
    Given Rafael has reviewed the profile preview
    When Rafael responds with "cancel"
    Then no file is written to ~/.sbir/company-profile.json
    And the builder confirms that no changes were made
    And the profile draft is discarded

  Scenario: Save uses atomic write pattern
    Given Rafael confirmed the profile
    When the builder writes the profile
    Then the builder writes to company-profile.json.tmp first
    And if an existing profile exists, it is backed up to company-profile.json.bak
    And company-profile.json.tmp is renamed to company-profile.json
    And the write is atomic (no partial file on disk)

  Scenario: File system permission error during save
    Given Rafael confirmed the profile
    And the ~/.sbir/ directory does not exist or is not writable
    When the builder attempts to save
    Then the builder displays a permission error with the specific path
    And the builder suggests: check permissions, create directory, or use --output flag
    And the profile draft is preserved (not discarded)

  # --- Update Flow ---

  Scenario: Update single section of existing profile
    Given Rafael has an existing company profile
    And his company recently won a NASA Phase I award
    When Rafael runs "/sbir:proposal profile update"
    And the builder asks which section to update
    And Rafael selects "past_performance"
    Then the builder shows current past performance entries
    And Rafael adds: agency "NASA", topic_area "Lunar Surface Power", outcome "awarded"
    And the builder validates the updated profile
    And the updated profile is saved with the new entry appended

  Scenario: Update preserves unmodified sections
    Given Rafael has an existing company profile with 5 capabilities
    And Rafael runs "/sbir:proposal profile update" to add a key personnel
    When Rafael adds Dr. James Chen with expertise in "signal processing"
    And the builder saves the updated profile
    Then the capabilities list still contains all 5 original entries
    And employee_count and certifications are unchanged
