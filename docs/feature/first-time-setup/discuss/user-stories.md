<!-- markdownlint-disable MD024 -->

# User Stories: First-Time Setup

Scope: Interactive setup wizard that guides first-time users through plugin configuration.
All stories trace to JTBD analysis job stories (JS-1 through JS-5).
Feature: `first-time-setup`

---

## US-FTS-001: Prerequisites Check

### Problem

Dr. Elena Vasquez is a PI at a 25-person defense tech startup who just installed the SBIR proposal plugin. She finds it frustrating to discover missing dependencies mid-setup because it wastes time and forces her to restart. Today she reads the README prerequisites section and hopes she has everything installed -- there is no automated verification.

### Who

- PI / Business Development Lead | First plugin session | Needs confidence that the environment is ready before investing time in configuration

### Solution

When the user runs the setup command, automatically check for Python 3.12+, Git, and Claude Code authentication before proceeding. Display pass/fail for each prerequisite with actionable fix instructions for failures.

### Domain Examples

#### 1: Happy Path -- Elena has all prerequisites

Dr. Elena Vasquez has Python 3.12.4, Git 2.44.0, and an authenticated Claude Code session on her Windows workstation. She runs `/sbir:setup`. The tool checks all three prerequisites, displays green checkmarks for each, and shows "All prerequisites met. Ready to continue." Elena presses (c) to continue to profile setup.

#### 2: Edge Case -- Elena has Python 3.10 installed

Dr. Elena Vasquez has Python 3.10.2 installed from an older project. She runs `/sbir:setup`. The tool displays "[!!] Python 3.10.2 -- version 3.12+ required" with a link to python.org. Setup halts with "Fix the issue above, then run /sbir:setup again." No partial state is written.

#### 3: Error Path -- Git not found in PATH

Dr. Elena Vasquez installed Git but it is not in her PATH (common on Windows). She runs `/sbir:setup`. The tool displays "[!!] Git not found" with a link to git-scm.com/downloads and a note about adding Git to PATH. Setup halts cleanly.

### UAT Scenarios (BDD)

#### Scenario: All prerequisites pass

Given Dr. Elena Vasquez has Python 3.12.4, Git 2.44.0, and authenticated Claude Code
When she runs "/sbir:setup"
Then the tool displays "[ok]" for Python, Git, and Claude Code
And displays "All prerequisites met"
And displays estimated setup time of 10-15 minutes
And offers to continue or quit

#### Scenario: Python version too old

Given Dr. Elena Vasquez has Python 3.10.2 installed
When she runs "/sbir:setup"
Then the tool displays "[!!] Python 3.10.2 -- version 3.12+ required"
And displays installation link for Python
And setup does not proceed beyond prerequisites

#### Scenario: Git not found

Given Git is not installed or not in PATH
When Dr. Elena Vasquez runs "/sbir:setup"
Then the tool displays "[!!] Git not found"
And displays installation link for Git
And setup does not proceed beyond prerequisites

#### Scenario: Multiple prerequisites missing

Given Python is not installed and Git is not installed
And Claude Code is authenticated
When Dr. Elena Vasquez runs "/sbir:setup"
Then the tool displays "[!!]" for both Python and Git
And displays fix instructions for each missing prerequisite
And setup does not proceed

### Acceptance Criteria

- [ ] Setup checks for Python 3.12+, Git, and Claude Code authentication
- [ ] Each prerequisite displays pass or fail with version number when available
- [ ] Failed prerequisites show actionable fix instructions with links
- [ ] Setup does not proceed past prerequisites if any fail
- [ ] No files are written or modified when prerequisites fail
- [ ] Welcome message includes estimated setup time

### Technical Notes

- Python version check: `python3 --version` or `python --version` (Windows compatibility)
- Git version check: `git --version`
- Claude Code auth check: verify Claude Code session is active (mechanism TBD in DESIGN)
- Windows/Git Bash environment: both `python3` and `python` commands may be needed
- Depends on: nothing (first step in setup flow)

---

## US-FTS-002: Guided Profile Creation

### Problem

Dr. Elena Vasquez is a PI who needs to create a company profile but finds it daunting to run a separate command she has never used before, with no context about why each field matters. The profile builder exists but it feels disconnected from the setup flow -- she has to know to run `/sbir:proposal profile setup` and understand that it is a prerequisite for everything else. Today she reads the README, runs the command separately, and hopes she provided enough information.

### Who

- PI / Business Development Lead | First-time setup | Wants profile creation woven into the setup flow with context about why it matters

### Solution

After prerequisites pass, the setup wizard checks for an existing profile. If none exists, it explains why the profile matters (feeds into fit scoring) and invokes the profile builder agent inline. If a profile exists, it offers to keep, update, or start fresh. After profile creation, the wizard resumes with a confirmation summary.

### Domain Examples

#### 1: Happy Path -- Elena creates profile via "both" mode

Dr. Elena Vasquez has no existing profile. Setup displays "No company profile found" and explains that the profile powers fit scoring. She selects "(b) both" mode and provides her capability statement PDF and SAM.gov entity page. The profile builder extracts company name "Meridian Photonics LLC", CAGE code 7XY3Z, and 6 capabilities. It interviews her for key personnel (Dr. Vasquez as PI, Dr. James Park as Co-PI) and past performance (2 Air Force wins, 1 Navy loss). Profile validates and saves. Setup resumes showing "Profile saved: Meridian Photonics LLC, 8 capabilities, 3 key personnel, SAM.gov active."

#### 2: Edge Case -- Marcus has existing profile, keeps it

Marcus Chen runs `/sbir:setup` in a new project directory. His profile at ~/.sbir/company-profile.json already exists for "Pacific Systems Engineering." Setup displays "EXISTING PROFILE DETECTED -- Company: Pacific Systems Engineering -- Last updated: 2026-01-20." He selects "(k) keep" and setup continues to corpus setup without modifying the profile.

#### 3: Edge Case -- Sarah cancels mid-interview

Sarah Kim is setting up for a client but realizes she does not have the SAM.gov data yet. She cancels during the profile builder interview. The profile builder exits cleanly ("Profile creation cancelled. No files were written or modified."). Setup displays "You can resume with /sbir:setup later." and exits.

### UAT Scenarios (BDD)

#### Scenario: New profile created through setup wizard

Given all prerequisites pass
And no company profile exists at ~/.sbir/company-profile.json
When setup proceeds to the profile step
Then the tool displays "No company profile found"
And explains that the profile feeds into fit scoring
And offers mode selection: documents, interview, or both
When Dr. Elena Vasquez selects "(b) both"
Then the profile builder agent is invoked within the setup flow
And after profile creation the tool displays company name, capability count, and SAM.gov status
And setup continues to corpus step

#### Scenario: Existing profile kept without modification

Given all prerequisites pass
And a company profile exists for "Pacific Systems Engineering"
When setup proceeds to the profile step
Then the tool displays "EXISTING PROFILE DETECTED"
And offers keep, update, fresh, or quit options
When Marcus Chen selects "(k) keep"
Then the profile is not modified
And setup continues to corpus step

#### Scenario: Existing profile updated through setup wizard

Given a company profile exists for "Pacific Systems Engineering"
When Marcus Chen selects "(u) update" at the profile step
Then the profile builder is invoked in update mode with existing data loaded
And after update the tool displays the updated profile summary
And setup continues to corpus step

#### Scenario: Profile creation cancelled mid-setup

Given no profile exists
And the profile builder is active in interview mode
When Sarah Kim says "cancel"
Then no profile file is written
And setup displays "You can resume with /sbir:setup later"
And setup exits cleanly

#### Scenario: Fresh profile replaces existing with backup

Given a company profile exists for "Pacific Systems Engineering"
When Marcus Chen selects "(f) fresh"
Then the existing profile is backed up to company-profile.json.bak
And the profile builder starts a new profile from scratch
And after creation setup continues to corpus step

### Acceptance Criteria

- [ ] Setup checks for existing profile before creating
- [ ] No existing profile: explains fit scoring context and offers mode selection
- [ ] Existing profile: offers keep, update, fresh, or quit options
- [ ] Profile builder agent is invoked inline (not as a separate command)
- [ ] After profile creation, setup displays summary and continues to next step
- [ ] Cancel during profile builder exits setup cleanly with no files written
- [ ] Fresh start backs up existing profile before creating new one

### Technical Notes

- Delegates to `sbir-profile-builder` agent for actual profile creation
- Uses `JsonProfileAdapter.metadata()` to detect existing profile
- Profile path is always `~/.sbir/company-profile.json` (global)
- Setup wizard must resume after profile builder completes (not terminate)
- Depends on: US-FTS-001 (prerequisites pass first)

---

## US-FTS-003: Guided Corpus Setup

### Problem

Dr. Elena Vasquez is a PI who has past proposals and debriefs scattered across directories on her workstation. She finds it confusing to figure out which files the plugin can use, how to organize them, and what command to run. The corpus ingestion command exists but she has to discover it in the README and know the exact path syntax. Today she either skips corpus setup entirely (reducing fit scoring accuracy) or spends 20 minutes organizing files before running the command.

### Who

- PI / Business Development Lead | Has past proposals in various directories | Wants guided document discovery with batch ingestion

### Solution

After profile creation, the setup wizard asks if the user has past documents. If yes, it accepts one or more directory paths, runs corpus ingestion, and reports results. If no, it skips gracefully with guidance about adding documents later. Multiple directories accepted in a single prompt.

### Domain Examples

#### 1: Happy Path -- Elena ingests two directories

Dr. Elena Vasquez has past proposals in ~/Documents/sbir-proposals/ (8 PDFs, 2 Excel files) and debriefs in ~/Downloads/debriefs/ (4 Word documents). Setup asks "Do you have past proposals or related documents?" She selects "(y) yes" and enters both paths. The tool scans both directories, ingests 12 supported documents, skips 2 Excel files, and reports: "Ingested: 12 documents (8 proposals, 4 debriefs). Skipped: 2 unsupported files (.xlsx)."

#### 2: Edge Case -- Marcus skips corpus (already has one)

Marcus Chen is in a new project directory but his corpus is in a previous project. He selects "(n) no" at the corpus step. Setup displays: "No corpus documents added. Fit scoring works with your profile alone, but accuracy improves with past proposals. Add anytime with: /sbir:proposal corpus add <directory>." Setup continues to the API key step.

#### 3: Error Path -- Sarah provides bad directory path

Sarah Kim enters "~/client-docs/meridian/" but the directory does not exist. The tool displays "Directory not found: ~/client-docs/meridian/". Sarah corrects to "~/client-docs/meridian-photonics/" and ingestion proceeds with 3 documents found.

### UAT Scenarios (BDD)

#### Scenario: Ingest documents from multiple directories

Given company profile is complete
And Dr. Elena Vasquez has ~/Documents/sbir-proposals/ with 8 PDFs and 2 Excel files
And ~/Downloads/debriefs/ with 4 Word documents
When setup proceeds to corpus step and she selects "(y) yes"
And enters "~/Documents/sbir-proposals/, ~/Downloads/debriefs/"
Then the tool ingests 12 supported documents from both directories
And skips 2 unsupported files
And displays ingestion summary with counts by type
And setup continues to API key step

#### Scenario: Skip corpus setup gracefully

Given company profile is complete
When setup proceeds to corpus step
And Marcus Chen selects "(n) no"
Then the tool displays "No corpus documents added"
And displays guidance about /sbir:proposal corpus add
And setup continues to API key step without error

#### Scenario: Invalid directory path with recovery

Given company profile is complete
When Sarah Kim enters "~/nonexistent-dir/"
Then the tool displays "Directory not found: ~/nonexistent-dir/"
And offers to enter a different path or skip

#### Scenario: Empty directory handled gracefully

Given company profile is complete
And ~/empty-dir/ exists but contains no supported files
When Dr. Elena Vasquez enters "~/empty-dir/"
Then the tool displays "No supported documents found"
And lists supported file formats
And offers to enter a different path or skip

#### Scenario: Re-running setup with existing corpus adds only new files

Given Dr. Elena Vasquez previously ingested 12 documents
And has added 2 new PDFs to ~/Documents/sbir-proposals/
When she re-runs /sbir:setup and enters the same directory
Then the tool detects 12 already-ingested documents
And ingests only the 2 new documents
And reports "2 new documents ingested. 12 already in corpus."

### Acceptance Criteria

- [ ] Corpus step asks if user has past documents before requesting paths
- [ ] Accepts one or more directory paths in a single prompt
- [ ] Runs corpus ingestion and reports count by document type
- [ ] Skips unsupported file types with count and format list
- [ ] Skip option continues setup without error or warning tone
- [ ] Invalid directory path produces helpful error with recovery option
- [ ] Re-ingestion is incremental (adds only new files)

### Technical Notes

- Delegates to existing corpus ingestion logic (same as /sbir:proposal corpus add)
- Multiple directories: split on comma, trim whitespace, validate each path
- Corpus stored in `.sbir/corpus/` (project-local)
- Deduplication by content hash (SHA-256) -- existing behavior
- Depends on: US-FTS-002 (profile step completes or is skipped by returning user)

---

## US-FTS-004: Validation Summary and Next Steps

### Problem

Dr. Elena Vasquez is a PI who just completed setup but has no way to know if everything is actually configured correctly. She finds it unsettling to proceed without confirmation because a misconfigured profile or missing corpus means wasted effort on low-confidence fit scoring. Today there is no unified validation -- she has to trust that each individual step worked and remember what she skipped.

### Who

- PI / Business Development Lead | Just completed setup | Needs confirmation that everything is properly configured before proceeding to solicitation search

### Solution

After all setup steps complete (or are skipped), display a unified validation summary re-checking all configuration items. Show pass/warning/missing for each category. Display warnings for items that reduce effectiveness (inactive SAM.gov, empty corpus). End with concrete next-step commands.

### Domain Examples

#### 1: Happy Path -- Elena sees all green

Dr. Elena Vasquez completed all setup steps. Validation shows: Python 3.12.4 [ok], Git 2.44.0 [ok], Claude Code [ok], profile for "Meridian Photonics LLC" [ok], SAM.gov active [ok], 14 documents indexed [ok], GEMINI_API_KEY [--] not configured (Wave 5 only). Status: READY. Next steps: "/sbir:solicitation find" to discover topics.

#### 2: Edge Case -- Elena has inactive SAM.gov

Dr. Elena Vasquez completed setup but her SAM.gov registration lapsed. Validation shows [!!] for SAM.gov: "SAM.gov not active -- all topics will be NO-GO until fixed. Update with: /sbir:proposal profile update." Status: READY (with warnings). Setup still completes -- the warning is informational, not blocking.

#### 3: Edge Case -- Marcus re-runs setup, everything already configured

Marcus Chen runs `/sbir:setup` on a project where he previously completed setup. The tool detects existing configuration, runs validation, and shows all items as [ok]. It offers "(u) update profile or corpus", "(v) view full validation summary", or "(q) exit -- nothing to change." Marcus selects (q) and exits in under 5 seconds.

### UAT Scenarios (BDD)

#### Scenario: Full validation with all items passing

Given Dr. Elena Vasquez completed all setup steps
And profile exists with SAM.gov active and 8 capabilities
And corpus has 14 documents indexed
And GEMINI_API_KEY is not set
When setup proceeds to validation
Then the tool displays "[ok]" for all prerequisites
And displays "[ok]" for profile with company name and SAM.gov status
And displays "[ok]" for corpus with document count
And displays "[--]" for GEMINI_API_KEY (not configured, Wave 5 only)
And displays "STATUS: READY"
And displays next-step commands starting with /sbir:solicitation find

#### Scenario: Validation with SAM.gov warning

Given profile exists but SAM.gov is inactive
When setup proceeds to validation
Then the tool displays "[!!] SAM.gov not active -- all topics will be NO-GO"
And displays "Update with: /sbir:proposal profile update"
And displays "STATUS: READY (with warnings)"

#### Scenario: Validation with empty corpus warning

Given profile exists and is valid
And no corpus documents are indexed
When setup proceeds to validation
Then the tool displays "[--] No documents indexed"
And displays "Add documents: /sbir:proposal corpus add <directory>"
And displays "STATUS: READY (with warnings)"

#### Scenario: Re-run setup detects existing configuration

Given Dr. Elena Vasquez previously completed full setup
When she runs "/sbir:setup" again
Then the tool displays "Existing setup detected"
And runs validation checks showing current status
And offers to update, view details, or exit

#### Scenario: Next steps display after validation

Given validation shows "STATUS: READY"
When next steps are displayed
Then the tool shows "/sbir:solicitation find" as primary next command
And shows "/sbir:proposal new <topic-id>" for starting a proposal
And shows "/sbir:proposal status" for checking status
And shows "Run /sbir:setup again to update your configuration"

### Acceptance Criteria

- [ ] Validation re-checks all configuration items (not just trusting prior steps)
- [ ] Each item displays [ok], [!!] (warning), or [--] (not configured) indicator
- [ ] SAM.gov inactive produces explicit warning about NO-GO consequence
- [ ] Empty corpus produces guidance about adding documents later
- [ ] Overall status computed: READY, READY (with warnings)
- [ ] Next-step commands displayed with the primary command first
- [ ] Re-running setup shows existing configuration and offers update/exit
- [ ] GEMINI_API_KEY absence is informational, not a warning

### Technical Notes

- Validation reads profile via JsonProfileAdapter, checks corpus index, checks env var
- Status computation: READY if profile valid; READY (with warnings) if SAM inactive or corpus empty
- Re-run detection: check profile_exists and corpus_document_count before entering flow
- Depends on: US-FTS-001, US-FTS-002, US-FTS-003 (all prior steps)

---

## US-FTS-005: API Key Configuration Guidance

### Problem

Dr. Elena Vasquez is a PI who does not know what the Gemini API key is for or whether she needs it right now. She finds it confusing when setup tools ask about optional configuration without explaining the consequences of skipping. Today, the Gemini API key is mentioned in the README under "Image Generation Setup (Optional)" but first-time users do not know if they need it before they reach Wave 5.

### Who

- PI / Business Development Lead | Mid-setup, past corpus step | Needs to understand what is optional and what skipping means

### Solution

After corpus setup, check for the GEMINI_API_KEY environment variable. If present, confirm it and move on. If absent, explain what it enables (concept figure generation in Wave 5), make clear it is optional and not needed immediately, and offer skip or step-by-step configuration instructions.

### Domain Examples

#### 1: Happy Path -- Elena skips API key

Dr. Elena Vasquez reaches the API key step. GEMINI_API_KEY is not set. The tool explains "The plugin can generate concept figures using Google Gemini during Wave 5. This is optional." Elena selects "(s) skip" and sees "You can set this up anytime." Setup continues to validation.

#### 2: Edge Case -- Marcus already has the key

Marcus Chen has GEMINI_API_KEY configured from a previous project. The tool detects it and displays "GEMINI_API_KEY: detected. Concept figure generation is available for Wave 5." Setup continues to validation automatically.

#### 3: Edge Case -- Elena wants instructions

Dr. Elena Vasquez selects "(c) configure" to learn how to get the key. The tool displays: visit ai.google.dev, create account, generate key, add export command to shell profile, restart terminal. It notes "You can set this up anytime -- it's not needed until Wave 5." Setup continues after she reads the instructions.

### UAT Scenarios (BDD)

#### Scenario: API key not present -- user skips

Given corpus step is complete
And GEMINI_API_KEY is not set
When setup proceeds to the API key step
Then the tool explains what Gemini enables and that it is optional
And offers skip and configure options
When Dr. Elena Vasquez selects "(s) skip"
Then setup continues to validation

#### Scenario: API key already present

Given corpus step is complete
And GEMINI_API_KEY environment variable is set
When setup proceeds to the API key step
Then the tool displays "GEMINI_API_KEY: detected"
And setup continues to validation automatically

#### Scenario: User requests configuration instructions

Given GEMINI_API_KEY is not set
When Dr. Elena Vasquez selects "(c) configure"
Then the tool displays step-by-step instructions for obtaining a key
And displays the shell export command
And notes the key is not needed until Wave 5
And offers to continue setup

### Acceptance Criteria

- [ ] Checks GEMINI_API_KEY environment variable presence
- [ ] Explains what the key enables (concept figures in Wave 5)
- [ ] Makes clear the key is optional and not needed immediately
- [ ] Skip option continues setup without negative tone
- [ ] Configuration instructions include: where to get key, how to set env var, when it is needed
- [ ] Already-present key is confirmed and setup continues automatically

### Technical Notes

- Environment variable check: read GEMINI_API_KEY from process environment
- No validation of key format or validity (that happens in Wave 5 agent)
- Instructions reference Google AI Studio at ai.google.dev
- Shell-specific export syntax may vary (bash vs PowerShell) -- show bash by default, note alternatives
- Depends on: US-FTS-003 (corpus step completes or is skipped)

---

## Story Dependency Map

```
US-FTS-001 (Prerequisites Check)
  |
  +-- US-FTS-002 (Guided Profile Creation)
  |     |
  |     +-- US-FTS-003 (Guided Corpus Setup)
  |           |
  |           +-- US-FTS-005 (API Key Guidance)
  |                 |
  |                 +-- US-FTS-004 (Validation & Next Steps)
```

Build order:
1. US-FTS-001 -- Prerequisites (no dependencies)
2. US-FTS-002 -- Profile (depends on US-FTS-001)
3. US-FTS-003 -- Corpus (depends on US-FTS-002)
4. US-FTS-005 -- API Key (depends on US-FTS-003)
5. US-FTS-004 -- Validation (depends on all above)

---

## Story Sizing Summary

| Story | Scenarios | Est. Days | Right-Sized? |
|-------|-----------|-----------|-------------|
| US-FTS-001 | 4 | 1 | Yes |
| US-FTS-002 | 5 | 2 | Yes |
| US-FTS-003 | 5 | 1-2 | Yes |
| US-FTS-004 | 5 | 1-2 | Yes |
| US-FTS-005 | 3 | 1 | Yes |

Total: 22 scenarios, 6-8 days estimated effort.

---

## Non-Functional Requirements

### NFR-FTS-001: Setup Time

Complete first-time setup (all steps, no skips) in under 15 minutes. The time estimate displayed at the start must be accurate to within 5 minutes.

### NFR-FTS-002: Idempotency

Running `/sbir:setup` multiple times produces no side effects beyond what the user explicitly chooses. Existing profile is never overwritten without confirmation. Existing corpus is only added to, never deleted.

### NFR-FTS-003: Cancel Safety

User can quit at any step. No partial state is written. Steps completed before quitting (e.g., profile saved) remain valid. Resuming setup later detects prior progress.

### NFR-FTS-004: CLI Output Consistency

All setup output follows the what/why/what-to-do error pattern. Color is not the only indicator (use [ok], [!!], [--] text indicators). NO_COLOR environment variable respected.
