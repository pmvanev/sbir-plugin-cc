Feature: Company Profile Enrichment from Federal APIs
  As a small business technical founder creating or updating a company profile,
  I want to provide my UEI and have the system pull registration data,
  certifications, and SBIR award history from SAM.gov, SBIR.gov, and USASpending.gov,
  so I can get an accurate profile without retyping data that already exists
  in government systems.

  Background:
    Given the SBIR plugin is installed
    And the company profile schema is defined at templates/company-profile-schema.json

  # === Step 1: API Key Check and Setup ===

  Scenario: SAM.gov API key found in config
    Given Rafael Medina has a SAM.gov API key stored in ~/.sbir/api-keys.json
    When the profile builder offers enrichment
    Then the system confirms "SAM.gov API key found"
    And displays the last 4 characters of the key for identification
    And prompts Rafael for his UEI

  Scenario: SAM.gov API key not found -- user provides key
    Given no SAM.gov API key exists in ~/.sbir/api-keys.json
    When the profile builder offers enrichment
    Then the system explains how to get a free API key at https://sam.gov/profile/details
    And Rafael enters his API key "abc123def456ghi789"
    And the system validates the key with a test call to SAM.gov
    And the key is saved to ~/.sbir/api-keys.json with owner-only permissions
    And Rafael is prompted for his UEI

  Scenario: SAM.gov API key not found -- user skips enrichment
    Given no SAM.gov API key exists in ~/.sbir/api-keys.json
    When the profile builder offers enrichment
    And Rafael chooses to skip enrichment
    Then the profile builder continues with the manual interview flow
    And no API calls are made

  Scenario: SAM.gov API key validation fails
    Given Rafael enters an invalid SAM.gov API key
    When the system validates the key with a test call
    And SAM.gov returns HTTP 403
    Then the system reports "API key validation failed"
    And offers to re-enter the key, generate a new one, or skip enrichment

  # === Step 2: User Provides UEI ===

  Scenario: Valid UEI accepted
    Given Rafael has a valid SAM.gov API key
    When Rafael enters UEI "DKJF84NXLE73"
    Then the system validates the UEI is 12 alphanumeric characters
    And the system begins the three-API enrichment cascade

  Scenario: Invalid UEI format rejected
    Given Rafael has a valid SAM.gov API key
    When Rafael enters UEI "SHORT"
    Then the system reports "UEI must be 12 alphanumeric characters. You entered 5."
    And prompts Rafael to re-enter the UEI

  # === Step 3: Three-API Enrichment Cascade ===

  Scenario: SAM.gov returns full entity data
    Given the enrichment service calls SAM.gov for UEI "DKJF84NXLE73"
    When SAM.gov responds with entity data
    Then enrichment result includes legal_name "Radiant Defense Systems, LLC"
    And enrichment result includes cage_code "7X2K9"
    And enrichment result includes naics_codes "334511, 541715, 334220"
    And enrichment result includes registration_status "Active" with expiration "2027-01-15"
    And enrichment result includes socioeconomic_certifications as empty list
    And each field is tagged with source "SAM.gov"

  Scenario: SBIR.gov returns award history including forgotten award
    Given the enrichment service queries SBIR.gov for company "Radiant Defense Systems"
    When SBIR.gov responds with company and award data
    Then enrichment result includes 3 SBIR awards
    And award 1 is agency "Air Force", topic "Compact DE for Maritime UAS", phase "Phase I"
    And award 2 is agency "DARPA", topic "High-Power RF Source", outcome "Completed"
    And award 3 is agency "Navy", topic "Shipboard Power Conditioning", phase "Phase I"
    And each award is tagged with source "SBIR.gov"

  Scenario: USASpending returns federal award totals
    Given the enrichment service queries USASpending for "Radiant Defense Systems"
    When USASpending responds with recipient data
    Then enrichment result includes total_federal_awards "$2.4M"
    And enrichment result includes transaction_count 5
    And enrichment result includes business_types "Small Business, For-Profit"

  Scenario: SAM.gov returns no entity for UEI
    Given the enrichment service calls SAM.gov for UEI "XYZABC123456"
    When SAM.gov responds with an empty result
    Then the system reports "No entity found in SAM.gov for UEI XYZABC123456"
    And offers to re-enter UEI, look up at sam.gov/search, or skip enrichment

  Scenario: SBIR.gov times out
    Given the enrichment service calls SBIR.gov
    When SBIR.gov does not respond within 10 seconds
    Then the system reports "SBIR.gov timed out"
    And SAM.gov and USASpending results are still available
    And the user can continue with partial data or retry SBIR.gov

  Scenario: All three APIs called -- partial failure is acceptable
    Given SAM.gov returns entity data successfully
    And SBIR.gov times out
    And USASpending returns recipient data successfully
    When enrichment results are assembled
    Then the results include SAM.gov and USASpending data
    And SBIR.gov fields are listed as "unavailable -- API did not respond"
    And those fields will be asked about during the interview

  Scenario: SBIR.gov returns multiple company matches
    Given the enrichment service queries SBIR.gov for "Radiant Defense"
    When SBIR.gov returns 3 companies with similar names
    Then the system displays all 3 with name, city, state, and award count
    And Rafael selects "Radiant Defense Systems, LLC (Huntsville, AL)"
    And awards for only the selected company are included in results

  # === Step 4: Review Enriched Data ===

  Scenario: User confirms all enriched fields
    Given enrichment returned legal_name, cage_code, naics_codes, registration_status, and 3 past_performance entries
    When Rafael reviews each field with its source attribution
    And Rafael confirms all fields
    Then all fields are marked as accepted
    And source attribution is preserved for each field

  Scenario: User edits an enriched field
    Given enrichment returned cage_code "7X2K9" from SAM.gov
    When Rafael edits the cage_code to "7X2K8"
    Then the profile draft uses "7X2K8" as the cage_code
    And the source is recorded as "user (overriding SAM.gov)"

  Scenario: User skips an enriched field to answer manually later
    Given enrichment returned socioeconomic_certifications as empty
    When Rafael chooses "enter manually" for socioeconomic certifications
    Then the field is left unpopulated in the enrichment result
    And it is added to the missing fields list for the interview step

  Scenario: Source attribution displayed for every enriched field
    Given enrichment returned data from SAM.gov, SBIR.gov, and USASpending
    When the review screen displays each field
    Then each field shows the API source name (SAM.gov, SBIR.gov, or USASpending)
    And fields from different sources are visually distinguishable

  # === Step 5: Merge into Profile Draft ===

  Scenario: Confirmed enrichment data merged into profile draft
    Given Rafael confirmed company_name, cage_code, naics_codes, registration_status, and 3 past_performance entries
    When the system merges confirmed data into the profile draft
    Then the profile draft contains all confirmed values with correct schema field paths
    And the source metadata is preserved in the profile draft

  Scenario: Interview targets only remaining gaps after enrichment
    Given enrichment populated company_name, certifications.sam_gov, certifications.cage, naics_codes, and past_performance
    When the interview step begins
    Then the interview asks about capabilities, security_clearance, itar_registered, employee_count, key_personnel, and research_institution_partners
    And the interview does not re-ask about fields already populated by enrichment

  Scenario: Enrichment data preserved through preview and save
    Given the profile draft contains enrichment data merged in Step 5
    When Rafael completes the interview for remaining fields
    And the preview displays the complete profile
    Then enrichment-sourced fields show their API source in the preview
    And the saved profile includes a sources section listing which APIs contributed data

  # === Update Flow: Re-Enrichment ===

  Scenario: Re-enrichment detects new SBIR award
    Given Rafael has an existing profile with 2 past_performance entries
    And Rafael runs profile update with enrichment
    When SBIR.gov now returns 3 awards (1 new: Navy Shipboard Power)
    Then the system shows the difference: "1 new award found"
    And Rafael can choose to add the new award to his profile
    And existing past_performance entries are not modified

  Scenario: Re-enrichment detects updated NAICS codes
    Given Rafael has an existing profile with naics_codes [334511, 541715]
    And Rafael runs profile update with enrichment
    When SAM.gov now returns naics_codes [334511, 541715, 334220]
    Then the system shows the difference: "1 new NAICS code: 334220"
    And Rafael can choose to add the new NAICS code
    And existing NAICS codes are not removed

  Scenario: Re-enrichment does not overwrite user-entered data
    Given Rafael has an existing profile with capabilities entered manually
    And capabilities are not available from any API
    When enrichment runs during profile update
    Then the manually-entered capabilities are untouched
    And no API attempts to populate the capabilities field

  # === API Key Management ===

  Scenario: API key stored securely with restricted permissions
    Given Rafael enters a valid SAM.gov API key
    When the system saves the key to ~/.sbir/api-keys.json
    Then the file permissions are set to owner-read-write only
    And the key is never displayed in full after initial entry
    And the key is never passed as a command-line argument

  Scenario: API key reused across enrichment sessions
    Given Rafael stored a SAM.gov API key during a previous session
    When Rafael starts a new profile setup or update with enrichment
    Then the system finds and uses the existing key
    And does not prompt Rafael to re-enter it
