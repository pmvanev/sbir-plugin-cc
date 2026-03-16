Feature: First-Time Setup
  As a small business PI installing the SBIR proposal plugin for the first time,
  I want a single guided command that checks prerequisites, builds my profile,
  ingests my corpus, and validates the configuration,
  so I can start searching for solicitations without reading documentation.

  Background:
    Given the SBIR proposal plugin is installed via Claude Code

  # ─── Step 1: Prerequisites Check ───────────────────────────────

  Scenario: All prerequisites met
    Given Python 3.12.4 is installed and in PATH
    And Git 2.44.0 is installed and in PATH
    And Claude Code is authenticated
    When Dr. Elena Vasquez runs "/sbir:setup"
    Then the tool displays "Welcome to the SBIR Proposal Plugin setup"
    And displays "Estimated time: 10-15 minutes"
    And displays "[ok]" next to Python, Git, and Claude Code
    And displays "All prerequisites met"
    And offers "(c) continue" and "(q) quit"

  Scenario: Python not found blocks setup
    Given Python is not installed or not in PATH
    And Git 2.44.0 is installed
    And Claude Code is authenticated
    When Dr. Elena Vasquez runs "/sbir:setup"
    Then the tool displays "[!!] Python not found"
    And displays a link to python.org for installation
    And displays "Fix the issue above, then run /sbir:setup again"
    And setup does not proceed to Step 2

  Scenario: Python version too old blocks setup
    Given Python 3.10.2 is installed
    When Dr. Elena Vasquez runs "/sbir:setup"
    Then the tool displays "[!!] Python 3.10.2 -- version 3.12+ required"
    And displays upgrade instructions
    And setup does not proceed to Step 2

  Scenario: Git not found blocks setup
    Given Python 3.12.4 is installed
    And Git is not installed or not in PATH
    And Claude Code is authenticated
    When Dr. Elena Vasquez runs "/sbir:setup"
    Then the tool displays "[!!] Git not found"
    And displays a link to git-scm.com/downloads
    And setup does not proceed to Step 2

  # ─── Step 2: Company Profile ───────────────────────────────────

  Scenario: No existing profile -- user creates via interview
    Given all prerequisites pass
    And no company profile exists at ~/.sbir/company-profile.json
    When setup proceeds to the company profile step
    Then the tool displays "No company profile found"
    And offers mode selection: documents, interview, or both
    When Dr. Elena Vasquez selects "(i) interview"
    Then the profile builder agent is invoked in interview mode
    And after profile creation the tool displays "Profile saved"
    And displays the company name, capability count, and SAM.gov status
    And setup continues to Step 3

  Scenario: Existing profile detected -- user keeps it
    Given all prerequisites pass
    And a company profile exists for "Meridian Photonics LLC" at ~/.sbir/company-profile.json
    When setup proceeds to the company profile step
    Then the tool displays "EXISTING PROFILE DETECTED"
    And displays "Company: Meridian Photonics LLC"
    And offers "(k) keep" and "(u) update" and "(f) fresh" and "(q) quit"
    When Dr. Elena Vasquez selects "(k) keep"
    Then the existing profile is not modified
    And setup continues to Step 3

  Scenario: Existing profile detected -- user updates it
    Given all prerequisites pass
    And a company profile exists for "Meridian Photonics LLC"
    When Dr. Elena Vasquez selects "(u) update"
    Then the profile builder agent is invoked in update mode
    And the existing profile is loaded as the starting point
    And after update the tool displays "Profile saved"
    And setup continues to Step 3

  Scenario: Existing profile detected -- user starts fresh
    Given all prerequisites pass
    And a company profile exists for "Meridian Photonics LLC"
    When Dr. Elena Vasquez selects "(f) fresh"
    Then the existing profile is backed up to company-profile.json.bak
    And the profile builder agent is invoked for a new profile
    And after creation the tool displays "Profile saved"
    And setup continues to Step 3

  Scenario: User cancels during profile creation
    Given all prerequisites pass
    And the profile builder agent is active
    When Dr. Elena Vasquez says "cancel"
    Then the profile builder exits without writing any file
    And setup displays "Profile creation cancelled. You can resume with /sbir:setup later."
    And setup exits cleanly

  # ─── Step 3: Corpus Setup ──────────────────────────────────────

  Scenario: User provides directory with mixed documents
    Given company profile is complete
    And Dr. Elena Vasquez has a directory ~/Documents/sbir-proposals/ containing 8 PDFs and 4 Word documents and 2 Excel files
    When setup proceeds to the corpus step
    And Dr. Elena Vasquez selects "(y) yes" and enters "~/Documents/sbir-proposals/"
    Then the tool ingests 12 supported documents
    And skips 2 unsupported files
    And displays "Ingested: 12 documents"
    And displays "Skipped: 2 unsupported files (.xlsx)"
    And setup continues to Step 4

  Scenario: User provides multiple directories
    Given company profile is complete
    And Dr. Elena Vasquez has documents in ~/Documents/sbir-proposals/ and ~/Downloads/debriefs/
    When Dr. Elena Vasquez enters "~/Documents/sbir-proposals/, ~/Downloads/debriefs/"
    Then the tool scans both directories
    And reports total documents found per directory
    And ingests all supported documents from both
    And setup continues to Step 4

  Scenario: User skips corpus setup
    Given company profile is complete
    When setup proceeds to the corpus step
    And Dr. Elena Vasquez selects "(n) no"
    Then the tool displays "No corpus documents added"
    And displays guidance about adding documents later with /sbir:proposal corpus add
    And setup continues to Step 4

  Scenario: User provides nonexistent directory
    Given company profile is complete
    When Dr. Elena Vasquez enters "~/nonexistent-dir/"
    Then the tool displays "Directory not found: ~/nonexistent-dir/"
    And offers to enter a different path or skip

  Scenario: User provides empty directory
    Given company profile is complete
    And ~/empty-dir/ exists but contains no supported files
    When Dr. Elena Vasquez enters "~/empty-dir/"
    Then the tool displays "No supported documents found in ~/empty-dir/"
    And lists supported file formats
    And offers to enter a different path or skip

  # ─── Step 4: API Key Configuration ─────────────────────────────

  Scenario: Gemini API key not present -- user skips
    Given corpus step is complete
    And GEMINI_API_KEY environment variable is not set
    When setup proceeds to the API key step
    Then the tool displays "GEMINI_API_KEY: not detected"
    And offers "(s) skip" and "(c) configure"
    When Dr. Elena Vasquez selects "(s) skip"
    Then setup continues to Step 5

  Scenario: Gemini API key not present -- user views instructions
    Given GEMINI_API_KEY is not set
    When Dr. Elena Vasquez selects "(c) configure"
    Then the tool displays step-by-step instructions for obtaining a Gemini API key
    And displays the export command to add to shell profile
    And displays "You can set this up anytime"
    And offers to continue setup

  Scenario: Gemini API key already present
    Given corpus step is complete
    And GEMINI_API_KEY environment variable is set
    When setup proceeds to the API key step
    Then the tool displays "GEMINI_API_KEY: detected"
    And displays "Concept figure generation is available for Wave 5"
    And setup continues to Step 5 automatically

  # ─── Step 5: Validation Summary ────────────────────────────────

  Scenario: Full validation -- all green
    Given Dr. Elena Vasquez has completed all setup steps
    And company profile exists with SAM.gov active and 8 capabilities and 3 key personnel
    And corpus has 14 documents indexed
    And GEMINI_API_KEY is not set
    When setup proceeds to validation
    Then the tool displays "[ok]" for Python, Git, Claude Code
    And displays "[ok]" for company profile with SAM.gov status
    And displays "[ok]" for corpus with document count
    And displays "[--]" for GEMINI_API_KEY with "not configured (Wave 5 only)"
    And displays "STATUS: READY"

  Scenario: Validation with SAM.gov warning
    Given company profile exists but SAM.gov is not active
    When setup proceeds to validation
    Then the tool displays "[!!] SAM.gov not active"
    And displays warning "all topics will be NO-GO until fixed"
    And displays "Update with: /sbir:proposal profile update"
    And displays "STATUS: READY (with warnings)"

  Scenario: Validation with empty corpus
    Given company profile exists and is valid
    And no corpus documents have been ingested
    When setup proceeds to validation
    Then the tool displays "[--] No documents indexed"
    And displays guidance to add documents later
    And displays "STATUS: READY (with warnings)"

  # ─── Step 6: Next Steps ────────────────────────────────────────

  Scenario: Next steps after successful setup
    Given validation displays "STATUS: READY"
    When setup proceeds to next steps
    Then the tool displays "Your SBIR Proposal Plugin is ready"
    And displays "/sbir:solicitation find" as the primary next command
    And displays "/sbir:proposal status" for checking status
    And displays "Run /sbir:setup again to update your configuration"

  # ─── Resume / Idempotent Re-run ────────────────────────────────

  Scenario: Re-running setup with everything already configured
    Given Dr. Elena Vasquez previously completed full setup
    And company profile exists for "Meridian Photonics LLC"
    And corpus has 14 documents indexed
    When Dr. Elena Vasquez runs "/sbir:setup"
    Then the tool displays "Existing setup detected"
    And runs validation checks on all configuration items
    And displays current status for profile, corpus, and optional items
    And offers "(u) update" and "(v) view full summary" and "(q) exit"

  Scenario: Re-running setup with partial configuration
    Given Dr. Elena Vasquez previously created a profile but skipped corpus
    When Dr. Elena Vasquez runs "/sbir:setup"
    Then the tool displays "Existing setup detected"
    And displays "[ok]" for company profile
    And displays "[--]" for corpus with "No documents indexed"
    And offers to add corpus documents or exit

  # ─── Quit at Any Step ──────────────────────────────────────────

  Scenario: User quits at prerequisites step
    Given all prerequisites pass
    When Dr. Elena Vasquez selects "(q) quit" at the prerequisites step
    Then setup exits cleanly
    And no files are written or modified

  Scenario: User quits at corpus step
    Given company profile is complete
    When Dr. Elena Vasquez selects "(q) quit" at the corpus step
    Then setup exits cleanly
    And the company profile remains saved
    And no corpus changes are made
