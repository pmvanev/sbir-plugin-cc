# Journey Visual: First-Time Setup

## Journey Flow

```
[Trigger]              [Step 1]            [Step 2]            [Step 3]
User runs              Prerequisites       Company Profile     Corpus
/sbir:setup            Check               Creation            Setup
    |                     |                    |                   |
    v                     v                    v                   v
Feels: Curious       Feels: Reassured     Feels: Engaged     Feels: Productive
Sees: Welcome +       Sees: Green/red      Sees: Profile       Sees: Document
time estimate          checkmarks           builder flow        discovery
    |                     |                    |                   |
    +---------------------+--------------------+-------------------+
                                                                   |
                          +----------------------------------------+
                          |
[Step 4]            [Step 5]            [Step 6]
API Key             Validation          Next Steps
(Optional)          Summary             Guidance
    |                  |                    |
    v                  v                    v
Feels: Informed    Feels: Confident    Feels: Empowered
Sees: Skip/         Sees: All-green     Sees: Clear
configure option    checklist           next command
```

## Emotional Arc

- **Start**: Curious but slightly anxious ("Will this be complicated? Do I have everything I need?")
- **Middle**: Engaged and building confidence ("Each step completes, progress is visible, I am in control")
- **End**: Confident and empowered ("Everything is set up correctly. I know exactly what to do next.")

Pattern: **Confidence Building** -- progressive small wins reduce anxiety through visible progress.

---

## Step 1: Welcome and Prerequisites Check

**Command**: `/sbir:setup`

**Emotional state**: Curious -> Reassured (or Informed if issues found)

```
+-- First-Time Setup -------------------------------------------+
|                                                                |
|  Welcome to the SBIR Proposal Plugin setup.                    |
|  Estimated time: 10-15 minutes                                 |
|                                                                |
|  Checking prerequisites...                                     |
|                                                                |
|  [ok]  Python 3.12.4                                           |
|  [ok]  Git 2.44.0                                              |
|  [ok]  Claude Code authenticated                               |
|                                                                |
|  All prerequisites met. Ready to continue.                     |
|                                                                |
|  (c) continue   (q) quit                                       |
+----------------------------------------------------------------+
```

**Error variant** -- missing prerequisite:

```
+-- First-Time Setup -------------------------------------------+
|                                                                |
|  Welcome to the SBIR Proposal Plugin setup.                    |
|  Estimated time: 10-15 minutes                                 |
|                                                                |
|  Checking prerequisites...                                     |
|                                                                |
|  [ok]  Python 3.12.4                                           |
|  [!!]  Git not found                                           |
|  [ok]  Claude Code authenticated                               |
|                                                                |
|  1 issue found:                                                |
|    Git is required but not found in PATH.                      |
|    Install: https://git-scm.com/downloads                      |
|                                                                |
|  Fix the issue above, then run /sbir:setup again.              |
+----------------------------------------------------------------+
```

**Shared artifacts**: `${python_version}`, `${git_version}`, `${claude_code_status}`

---

## Step 2: Company Profile Creation

**Command**: Delegates to `sbir-profile-builder` agent

**Emotional state**: Reassured -> Engaged

### 2a: Detect Existing Profile

```
+-- Company Profile --------------------------------------------+
|                                                                |
|  Checking for existing company profile...                      |
|                                                                |
|  EXISTING PROFILE DETECTED                                     |
|  Company: Meridian Photonics LLC                               |
|  Last updated: 2026-02-15                                      |
|                                                                |
|  (k) keep current profile and continue                         |
|  (u) update profile (opens profile builder)                    |
|  (f) fresh start (backs up current, creates new)               |
|  (q) quit setup                                                |
+----------------------------------------------------------------+
```

### 2b: No Existing Profile

```
+-- Company Profile --------------------------------------------+
|                                                                |
|  No company profile found at ~/.sbir/company-profile.json      |
|                                                                |
|  Your company profile feeds directly into fit scoring.         |
|  The better your profile, the more accurate your topic         |
|  recommendations will be.                                      |
|                                                                |
|  How would you like to build your profile?                     |
|                                                                |
|  (d) documents -- point to capability statements, SAM.gov      |
|  (i) interview -- I'll walk through each section               |
|  (b) both      -- extract from documents, fill gaps via Q&A    |
|                                                                |
|  Tip: If you have a SAM.gov entity page or capability          |
|  statement handy, "both" is the fastest option.                |
+----------------------------------------------------------------+
```

After profile creation completes, the setup wizard resumes:

```
+-- Company Profile -- COMPLETE --------------------------------+
|                                                                |
|  Profile saved: ~/.sbir/company-profile.json                   |
|  Company: Meridian Photonics LLC                               |
|  Capabilities: 8 keywords                                      |
|  Key Personnel: 3 entries                                      |
|  SAM.gov: active (CAGE: 7XY3Z)                                |
|                                                                |
|  Continuing to corpus setup...                                 |
+----------------------------------------------------------------+
```

**Shared artifacts**: `${company_name}`, `${profile_path}`, `${profile_exists}`

---

## Step 3: Corpus Setup

**Command**: Guided corpus discovery + delegates to corpus ingestion

**Emotional state**: Engaged -> Productive

### 3a: Corpus Discovery

```
+-- Corpus Setup -----------------------------------------------+
|                                                                |
|  Your corpus is past proposals, debriefs, and capability       |
|  statements. It powers fit scoring and informs drafting.       |
|                                                                |
|  Do you have past proposals or related documents?              |
|                                                                |
|  (y) yes -- I have documents to add                            |
|  (n) no  -- I'm starting fresh (skip corpus for now)           |
|  (q) quit setup                                                |
+----------------------------------------------------------------+
```

### 3b: Directory Selection

```
+-- Corpus Setup -----------------------------------------------+
|                                                                |
|  Where are your past proposals and documents?                  |
|                                                                |
|  Enter a directory path (or multiple, separated by commas):    |
|  > ~/Documents/sbir-proposals, ~/Downloads/debriefs            |
|                                                                |
|  Supported formats: PDF, Word (.docx/.doc), text, Markdown     |
+----------------------------------------------------------------+
```

### 3c: Ingestion Results

```
+-- Corpus Setup -- COMPLETE -----------------------------------+
|                                                                |
|  Scanned 2 directories:                                        |
|    ~/Documents/sbir-proposals/  -- 12 files found              |
|    ~/Downloads/debriefs/        -- 4 files found               |
|                                                                |
|  Ingested: 14 documents                                        |
|    8 proposals (PDF)                                           |
|    4 debriefs (Word)                                           |
|    2 capability statements (PDF)                               |
|  Skipped: 2 unsupported files (.xlsx)                          |
|                                                                |
|  Your corpus is ready for semantic search.                     |
|                                                                |
|  Continuing to optional configuration...                       |
+----------------------------------------------------------------+
```

### 3d: Skip Variant

```
+-- Corpus Setup -- SKIPPED ------------------------------------+
|                                                                |
|  No corpus documents added.                                    |
|                                                                |
|  Fit scoring will work with your profile alone, but            |
|  accuracy improves with past proposals. You can add            |
|  documents anytime with:                                       |
|    /sbir:proposal corpus add <directory>                       |
|                                                                |
|  Continuing to optional configuration...                       |
+----------------------------------------------------------------+
```

**Shared artifacts**: `${corpus_directories}`, `${corpus_document_count}`, `${corpus_path}`

---

## Step 4: API Key Configuration (Optional)

**Command**: Environment variable guidance

**Emotional state**: Productive -> Informed

```
+-- Image Generation (Optional) --------------------------------+
|                                                                |
|  The plugin can generate concept figures using Google           |
|  Gemini during Wave 5 (Visual Assets). This is optional --     |
|  without it, the plugin produces figure specs you create       |
|  manually.                                                     |
|                                                                |
|  GEMINI_API_KEY: not detected                                  |
|                                                                |
|  (s) skip -- I'll set this up later                            |
|  (c) configure -- show me how to get an API key                |
|  (q) quit setup                                                |
+----------------------------------------------------------------+
```

### 4a: Configure Guidance

```
+-- Image Generation -- Configuration --------------------------+
|                                                                |
|  1. Visit https://ai.google.dev/ and create a free account    |
|  2. Generate an API key (free tier: 500 images/day)            |
|  3. Add to your shell profile:                                 |
|                                                                |
|     export GEMINI_API_KEY="your-key-here"                      |
|                                                                |
|  4. Restart your terminal (or source your profile)             |
|                                                                |
|  The plugin will detect the key automatically during           |
|  Wave 5. You can set this up anytime -- it's not needed        |
|  until you reach visual asset generation.                      |
|                                                                |
|  (c) continue setup   (q) quit                                 |
+----------------------------------------------------------------+
```

### 4b: Key Already Present

```
+-- Image Generation (Optional) --------------------------------+
|                                                                |
|  GEMINI_API_KEY: detected                                      |
|                                                                |
|  Concept figure generation is available for Wave 5.            |
|                                                                |
|  Continuing to validation...                                   |
+----------------------------------------------------------------+
```

**Shared artifacts**: `${gemini_api_key_status}`

---

## Step 5: Validation Summary

**Command**: Automated verification of all setup steps

**Emotional state**: Informed -> Confident

### 5a: All Checks Pass

```
+-- Setup Validation -------------------------------------------+
|                                                                |
|  Verifying your setup...                                       |
|                                                                |
|  Prerequisites                                                 |
|    [ok]  Python 3.12.4                                         |
|    [ok]  Git 2.44.0                                            |
|    [ok]  Claude Code authenticated                             |
|                                                                |
|  Company Profile                                               |
|    [ok]  ~/.sbir/company-profile.json                          |
|    [ok]  SAM.gov active (CAGE: 7XY3Z)                          |
|    [ok]  8 capabilities, 3 key personnel                       |
|                                                                |
|  Corpus                                                        |
|    [ok]  14 documents indexed                                  |
|    [ok]  8 proposals, 4 debriefs, 2 capability statements      |
|                                                                |
|  Optional                                                      |
|    [--]  GEMINI_API_KEY not configured (Wave 5 only)           |
|                                                                |
|  STATUS: READY                                                 |
+----------------------------------------------------------------+
```

### 5b: Issues Found

```
+-- Setup Validation -------------------------------------------+
|                                                                |
|  Verifying your setup...                                       |
|                                                                |
|  Prerequisites                                                 |
|    [ok]  Python 3.12.4                                         |
|    [ok]  Git 2.44.0                                            |
|    [ok]  Claude Code authenticated                             |
|                                                                |
|  Company Profile                                               |
|    [ok]  ~/.sbir/company-profile.json                          |
|    [!!]  SAM.gov not active -- all topics will be NO-GO        |
|    [ok]  5 capabilities, 2 key personnel                       |
|                                                                |
|  Corpus                                                        |
|    [--]  No documents indexed                                  |
|                                                                |
|  Optional                                                      |
|    [--]  GEMINI_API_KEY not configured (Wave 5 only)           |
|                                                                |
|  STATUS: READY (with warnings)                                 |
|                                                                |
|  Warnings:                                                     |
|  - SAM.gov inactive: every topic scores NO-GO until fixed.     |
|    Update with: /sbir:proposal profile update                  |
|  - Empty corpus: fit scoring works but accuracy is reduced.    |
|    Add documents: /sbir:proposal corpus add <directory>        |
+----------------------------------------------------------------+
```

**Shared artifacts**: `${setup_status}`, `${warning_count}`, `${profile_path}`, `${corpus_document_count}`

---

## Step 6: Next Steps

**Command**: Guidance output

**Emotional state**: Confident -> Empowered

```
+-- Setup Complete ---------------------------------------------+
|                                                                |
|  Your SBIR Proposal Plugin is ready.                           |
|                                                                |
|  What to do next:                                              |
|                                                                |
|  1. Find solicitations:                                        |
|     /sbir:solicitation find                                    |
|                                                                |
|  2. Filter by agency:                                          |
|     /sbir:solicitation find --agency "Air Force"               |
|                                                                |
|  3. Start a proposal:                                          |
|     /sbir:proposal new <topic-id>                              |
|                                                                |
|  4. Check status anytime:                                      |
|     /sbir:proposal status                                      |
|                                                                |
|  Run /sbir:setup again anytime to update your configuration.   |
+----------------------------------------------------------------+
```

**Shared artifacts**: `${next_commands}`

---

## Resume Flow (Idempotent Re-run)

When `/sbir:setup` is run and setup was previously completed:

```
+-- First-Time Setup -------------------------------------------+
|                                                                |
|  Existing setup detected. Checking configuration...            |
|                                                                |
|  Prerequisites                                                 |
|    [ok]  Python 3.12.4                                         |
|    [ok]  Git 2.44.0                                            |
|    [ok]  Claude Code authenticated                             |
|                                                                |
|  Company Profile                                               |
|    [ok]  Meridian Photonics LLC (updated 2026-02-15)           |
|                                                                |
|  Corpus                                                        |
|    [ok]  14 documents indexed                                  |
|                                                                |
|  Optional                                                      |
|    [--]  GEMINI_API_KEY not configured                         |
|                                                                |
|  Everything looks good. What would you like to do?             |
|                                                                |
|  (u) update profile or corpus                                  |
|  (v) view full validation summary                              |
|  (q) exit -- nothing to change                                 |
+----------------------------------------------------------------+
```
