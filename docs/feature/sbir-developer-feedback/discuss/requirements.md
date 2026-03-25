# Requirements — sbir-developer-feedback

## Functional Requirements

### FR-01: Command Invocation
The plugin MUST provide a `/sbir:developer-feedback` slash command invokable from any Claude Code session, regardless of whether an active proposal exists.

### FR-02: Feedback Type Selection
The command MUST ask the user to classify their feedback as one of: **Bug**, **Suggestion**, or **Quality Issue** before proceeding.

### FR-03: Quality Ratings (conditional)
When the user selects "Quality Issue", the command MUST present optional 1–5 ratings for each of the following dimensions:
- Past performance relevance (were the right past projects selected?)
- Image quality (were generated figures appropriate and clear?)
- Writing quality (was the drafted text coherent and on-target?)
- Topic scoring accuracy (were the fit scores and recommendations accurate?)

Ratings are optional — the user may skip any or all dimensions (null = N/A for this session).

### FR-04: Free Text Entry
The command MUST offer an optional free-text field for any feedback type. The user may skip it.

### FR-05: Context Snapshot — Proposal State
When an active proposal exists, the command MUST automatically read and include in the feedback entry:
- `proposal_id` — from `proposal-state.json`
- `topic` (id, title, agency, deadline, phase) — from `proposal-state.json`
- `current_wave` — current wave number
- `completed_waves` — list of wave numbers with status "completed"
- `skipped_waves` — list of wave numbers with status "skipped"

### FR-06: Context Snapshot — Configuration State
The command MUST automatically include:
- `rigor_profile` — from `rigor-profile.json` (`profile_name` field); null if no profile set
- `company_name` — from `~/.sbir/company-profile.json`; null if no profile
- `company_profile_age_days` — days since company profile file last modified; null if no profile
- `finder_results_age_days` — days since finder-results.json last modified; null if not run
- `top_scored_topics` — top 5 entries from `finder-results.json` (topic_id, composite_score, recommendation); empty list if not run

### FR-07: Context Snapshot — Environment
The command MUST automatically include:
- `plugin_version` — short git SHA of the current HEAD; "unknown" if git is unavailable
- `generated_artifacts` — alphabetical list of filenames in the active proposal's artifacts directory; empty list if no proposal or no artifacts

### FR-08: Output File
The feedback entry MUST be written as a JSON file to `.sbir/feedback/feedback-{ISO-timestamp}.json` (using UTC timestamp, colons replaced with hyphens for filesystem compatibility). The directory MUST be created if absent. Writes MUST use the atomic pattern (tmp → rename).

### FR-09: Graceful Degradation
If any state file is missing or unreadable, the corresponding snapshot fields MUST be null or empty list. The feedback MUST still be saved. The command MUST NOT crash or block on missing state.

### FR-10: Empty Submission Guard
If the user provides no ratings AND no free text, the command MUST prompt once for confirmation before saving. An empty-details entry is valid and must be saveable.

### FR-11: Confirmation
After saving, the command MUST display the feedback ID (UUID) and the full file path of the saved entry.

## Non-Functional Requirements

### NFR-01: Latency
The command MUST complete (from invocation to confirmation) in under 5 seconds for the common path (active proposal, all state files present).

### NFR-02: Privacy
Company profile capability text, past performance descriptions, and draft proposal content MUST NOT be included in the feedback snapshot. Only metadata (names, ages, counts, scores) is captured.

### NFR-03: Portability
The feedback file MUST be valid JSON, human-readable without tooling, and self-contained (no external references).

### NFR-04: No External Dependencies
The command MUST work without network access. No webhook, GitHub API, or cloud service is required. All state is local.

## Out of Scope

- Sending feedback to GitHub, Discord, or any remote destination (future enhancement)
- Aggregating or summarizing feedback across multiple entries (future `/sbir:feedback-report` command)
- Feedback on behalf of multiple users / multi-user workflows
- Automated plugin improvement triggered by feedback (requires separate ML pipeline)
