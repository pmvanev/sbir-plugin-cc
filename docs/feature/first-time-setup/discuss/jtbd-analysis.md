# JTBD Analysis: First-Time Setup

## Job Classification

**Job Type**: Build Something New (Greenfield command on brownfield system)
**Workflow**: discuss -> design -> distill -> baseline -> roadmap -> split -> execute -> review

The first-time setup is a new command that orchestrates existing capabilities (profile builder, corpus ingestion) into a single guided experience. The underlying agents exist; the orchestration layer does not.

---

## Job Stories

### JS-1: First-Time Onboarding

**When** I have just installed the SBIR proposal plugin and want to start finding solicitations,
**I want to** be guided through all the setup steps without having to read documentation,
**so I can** get to the point of searching for topics as fast as possible without missing critical configuration.

#### Functional Job
Complete all prerequisites (profile, corpus, optional API key) in a single guided session so the plugin is fully operational.

#### Emotional Job
Feel confident that the plugin is properly configured and nothing was missed -- not anxious about whether I did it right.

#### Social Job
Be seen as someone who can adopt new tools efficiently -- not someone who needs hand-holding or wastes time on setup.

---

### JS-2: Prerequisite Verification

**When** I am about to install the SBIR plugin but am not sure my environment is ready,
**I want to** have the tool check my system for required dependencies (Python, Git, Claude Code),
**so I can** fix any issues upfront rather than hitting cryptic errors mid-setup.

#### Functional Job
Verify all system prerequisites are present and at the correct version before starting the setup workflow.

#### Emotional Job
Feel reassured that the foundation is solid before investing time in configuration.

#### Social Job
Not look foolish by running into basic environment errors that block setup.

---

### JS-3: Corpus Organization and Ingestion

**When** I have past proposals, debriefs, and capability statements scattered across directories,
**I want to** be guided to locate and organize these documents for the plugin,
**so I can** build a corpus that actually improves my fit scoring and proposal drafting without spending hours organizing files.

#### Functional Job
Locate, organize, and ingest past work documents into the corpus with minimal manual file management.

#### Emotional Job
Feel relief that years of past work are now accessible and useful, not sitting in forgotten folders.

#### Social Job
Demonstrate to colleagues that past work (including losses) has tangible value for future proposals.

---

### JS-4: Resume Interrupted Setup

**When** I started setup but had to stop mid-way (got called into a meeting, needed to find a document),
**I want to** resume where I left off without repeating completed steps,
**so I can** finish setup without wasting time or worrying about inconsistent state.

#### Functional Job
Detect what has already been configured and skip completed steps, offering to update rather than redo.

#### Emotional Job
Feel like the tool respects my time and remembers what I already did.

#### Social Job
Not feel punished for having a busy schedule that forces interruptions.

---

### JS-5: Returning User Re-Setup

**When** I have already used the plugin for a previous proposal and am setting up a new project,
**I want to** have the tool detect my existing profile and corpus and offer to reuse or update them,
**so I can** get started on a new proposal in minutes, not repeat the full onboarding process.

#### Functional Job
Detect existing global profile and project-local corpus. Offer reuse, update, or fresh start options.

#### Emotional Job
Feel rewarded for being a returning user -- the tool gets smarter and faster the more I use it.

#### Social Job
Show team members that the tool has a learning curve that pays off with repeat use.

---

## Four Forces Analysis

### Force 1: Push of Current Situation

- README has 6 manual steps spanning profile setup, corpus ingestion, and API configuration
- Users must read and follow documentation sequentially -- any missed step causes failures downstream
- No validation that setup is complete before attempting to use the plugin
- First-time users do not know what documents they need to gather until they read the README
- Error messages when profile or corpus is missing are helpful but reactive, not proactive
- Phil Santos quotes: "I wasted 20 minutes figuring out I needed my SAM.gov data before I could even start"

### Force 2: Pull of New Solution

- Single command guides through entire setup interactively
- Prerequisites checked automatically -- no surprise failures
- Profile builder invoked in context, not as a separate manual step
- Corpus setup with guided discovery of where past documents live
- Validation at the end confirms everything is ready
- Clear next step: "Run /sbir:solicitation find to discover topics"
- Idempotent: running again detects existing config and offers updates

### Force 3: Anxiety of New Solution

- "Will the setup wizard lock me into choices I cannot change later?"
- "What if I do not have all my documents ready -- will it force me to start over?"
- "Will it overwrite my existing profile if I run it by accident?"
- "How long will this take? I have a meeting in 30 minutes."
- "Can I trust it extracted my company data correctly from documents?"

### Force 4: Habit of Present

- Experienced SBIR writers already know the manual steps and have muscle memory
- Some users prefer reading documentation over interactive wizards
- Manual process gives more control over exact sequence and timing
- Existing profile builder works fine standalone -- why add another layer?
- "I already organized my corpus directory the way I like it"

### Assessment

- Switch likelihood: **High** -- strong push (manual steps cause errors and delays) and strong pull (single guided command)
- Key blocker: Anxiety about overwriting existing config and losing partial progress
- Key enabler: Automated prerequisite checking eliminates most common first-time failures
- Design implication: Setup must be idempotent, resumable, and respect existing configuration. Cancel-safe at every step. Show time estimate upfront.

---

## 8-Step Universal Job Map

### 1. Define -- Determine what is needed

**User needs to know**: What documents to gather, what information the profile needs, how long setup takes.
**Current gap**: User must read the entire README to understand prerequisites.
**Outcome**: "Minimize the time it takes to determine what I need before starting setup."

### 2. Locate -- Gather inputs

**User needs to find**: SAM.gov registration data, capability statements, past proposals, debriefs, TPOC notes.
**Current gap**: User must already know where these documents are on their filesystem.
**Outcome**: "Minimize the likelihood of missing a critical document during setup."

### 3. Prepare -- Set up environment

**User needs to do**: Install Python 3.12+, Git, Claude Code. Organize documents into a directory.
**Current gap**: Prerequisites listed in README but not checked automatically.
**Outcome**: "Minimize the time to verify my environment is ready for the plugin."

### 4. Confirm -- Verify readiness

**User needs to verify**: Python version is correct, Claude Code is authenticated, documents are accessible.
**Current gap**: No automated verification -- user discovers problems only when commands fail.
**Outcome**: "Minimize the likelihood of proceeding with an incomplete environment."

### 5. Execute -- Perform setup

**User needs to do**: Build company profile, ingest corpus, configure API key.
**Current gap**: Three separate manual commands with no orchestration.
**Outcome**: "Minimize the time to complete all setup steps from start to finish."

### 6. Monitor -- Check progress

**User needs to know**: Which steps are done, which remain, how far along they are.
**Current gap**: No progress tracking across setup steps -- user must remember what they did.
**Outcome**: "Minimize the likelihood of missing a setup step."

### 7. Modify -- Handle exceptions

**User needs to handle**: Missing documents, wrong Python version, interrupted session, invalid profile data.
**Current gap**: Errors are per-command; no setup-level recovery guidance.
**Outcome**: "Minimize the time to recover from a setup problem."

### 8. Conclude -- Finalize and assess

**User needs to see**: Confirmation that everything is configured correctly, what to do next.
**Current gap**: No unified validation or "you are ready" confirmation.
**Outcome**: "Minimize the likelihood of an incomplete setup going undetected."

---

## Opportunity Scoring

Scoring based on team estimate (primary dev + product context). Confidence: Medium.

| # | Outcome Statement | Imp. (%) | Sat. (%) | Score | Priority |
|---|-------------------|----------|----------|-------|----------|
| 1 | Minimize the time to complete all setup steps from start to finish | 90 | 30 | 15.0 | Extremely Underserved |
| 2 | Minimize the likelihood of an incomplete setup going undetected | 85 | 25 | 14.5 | Extremely Underserved |
| 3 | Minimize the likelihood of proceeding with an incomplete environment | 80 | 20 | 14.0 | Underserved |
| 4 | Minimize the time to determine what I need before starting setup | 75 | 35 | 11.5 | Appropriately Served |
| 5 | Minimize the likelihood of missing a critical document during setup | 70 | 30 | 11.0 | Appropriately Served |
| 6 | Minimize the time to verify my environment is ready for the plugin | 70 | 25 | 10.5 | Appropriately Served |
| 7 | Minimize the likelihood of missing a setup step | 75 | 40 | 10.5 | Appropriately Served |
| 8 | Minimize the time to recover from a setup problem | 60 | 30 | 9.0 | Overserved |

### Top Opportunities (Score >= 12)

1. **Complete setup in single guided session** -- Score: 15.0 -- Maps to JS-1 (core setup wizard)
2. **Validate setup completeness** -- Score: 14.5 -- Maps to JS-1 validation step + JS-4 resume
3. **Environment prerequisite check** -- Score: 14.0 -- Maps to JS-2 (prereq verification)

### Data Quality Notes

- Source: team estimates based on README friction points and support patterns
- Sample size: N/A (team estimate)
- Confidence: Medium -- directional, not absolute

---

## Persona Summary

### Primary: Dr. Elena Vasquez -- First-Time PI

- **Role**: Principal Investigator at a 25-person defense tech startup
- **Context**: Won 2 SBIRs manually, wants to scale to 4-5 proposals/year
- **Technical**: Comfortable with CLI, uses Git daily, PhD in electrical engineering
- **Documents**: SAM.gov active (CAGE: 7XY3Z, UEI: K5M2N8P1Q4R6T), past proposals in ~/Documents/sbir/, debriefs in email attachments
- **Pain**: Spent 45 minutes on first setup attempt, missed the corpus ingestion step, got confused when fit scoring returned low confidence
- **Goal**: Get from "plugin installed" to "searching for topics" in under 15 minutes

### Secondary: Marcus Chen -- Experienced SBIR Writer

- **Role**: Business development lead at a 120-person systems engineering firm
- **Context**: 15+ SBIR submissions, 8 wins, organized corpus of past work
- **Technical**: Power user, reads docs, prefers control over automation
- **Documents**: Maintained corpus directory at ~/sbir-archive/ with 40+ proposals, all debriefs, organized by agency
- **Pain**: Not the setup itself (he follows docs fine) but re-doing it for each new project directory
- **Goal**: Reuse existing profile and corpus across projects without manual copying

### Tertiary: Sarah Kim -- Consultant Setting Up for Client

- **Role**: SBIR consultant helping Meridian Photonics (client company) adopt the plugin
- **Context**: Does not have all client documents yet, needs partial setup that can be completed later
- **Technical**: Developer, comfortable with any CLI tool
- **Documents**: Has capability statement PDF from client, awaiting SAM.gov data and past proposals
- **Pain**: Cannot complete full setup in one session because client documents arrive over days
- **Goal**: Do what she can now, resume later when more documents arrive, without losing progress
