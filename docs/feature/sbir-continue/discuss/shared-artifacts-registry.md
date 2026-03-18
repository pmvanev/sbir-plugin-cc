# Shared Artifacts Registry: sbir-continue

## Artifact Inventory

### company_name

| Attribute | Value |
|-----------|-------|
| Source of truth | `~/.sbir/company-profile.json` -> `company_name` |
| Consumers | Step 2 (partial setup display), Step 3 (no proposal display) |
| Owner | sbir-profile-builder agent |
| Integration risk | MEDIUM -- profile may not exist; absence triggers setup routing |
| Validation | Read profile JSON, extract company_name field, verify non-empty string |

### corpus_status

| Attribute | Value |
|-----------|-------|
| Source of truth | `.sbir/corpus/` directory (file count) |
| Consumers | Step 2 (partial setup display), Step 3 (no proposal display) |
| Owner | sbir-corpus-librarian agent |
| Integration risk | LOW -- empty corpus is valid; count of 0 triggers "no documents" display |
| Validation | Count files in `.sbir/corpus/`, compare with `proposal-state.json -> corpus.document_count` if state exists |

### api_key_status

| Attribute | Value |
|-----------|-------|
| Source of truth | `GEMINI_API_KEY` environment variable |
| Consumers | Step 2 (partial setup display) |
| Owner | Environment (user-configured) |
| Integration risk | LOW -- absence is informational only, never blocks |
| Validation | Check env var existence, display "configured" or "not configured" |

### topic_id

| Attribute | Value |
|-----------|-------|
| Source of truth | `.sbir/proposal-state.json` -> `topic.id` |
| Consumers | Steps 4-7 (all active proposal displays) |
| Owner | sbir-orchestrator (set during `/proposal new`) |
| Integration risk | HIGH -- missing topic.id with existing state indicates corruption |
| Validation | Must be non-empty string matching pattern like "AF243-001" |

### topic_title

| Attribute | Value |
|-----------|-------|
| Source of truth | `.sbir/proposal-state.json` -> `topic.title` |
| Consumers | Steps 4-7 (all active proposal displays) |
| Owner | sbir-orchestrator (set during `/proposal new`) |
| Integration risk | MEDIUM -- cosmetic but important for user orientation |
| Validation | Must be non-empty string |

### current_wave

| Attribute | Value |
|-----------|-------|
| Source of truth | `.sbir/proposal-state.json` -> `current_wave` |
| Consumers | Steps 4-5 (wave display), task resolution logic, command suggestion |
| Owner | sbir-orchestrator (updated at wave transitions) |
| Integration risk | HIGH -- incorrect wave number leads to wrong command suggestions |
| Validation | Integer 0-9, must be consistent with `waves.{N}.status` values |

### wave_name

| Attribute | Value |
|-----------|-------|
| Source of truth | `skills/orchestrator/wave-agent-mapping.md` -> wave definitions table |
| Consumers | Steps 4-5 (wave display headings) |
| Owner | Plugin skill definition (static) |
| Integration risk | LOW -- static mapping, changes only with plugin updates |
| Validation | Lookup current_wave in wave definitions, verify name exists |

### deadline

| Attribute | Value |
|-----------|-------|
| Source of truth | `.sbir/proposal-state.json` -> `topic.deadline` |
| Consumers | Steps 4-5 (deadline display and countdown) |
| Owner | sbir-orchestrator (set during `/proposal new`) |
| Integration risk | MEDIUM -- null deadline is valid (some proposals lack fixed deadlines) |
| Validation | ISO 8601 date string or null; compute days_remaining only if non-null |

### days_remaining

| Attribute | Value |
|-----------|-------|
| Source of truth | Computed: `topic.deadline - current_date` |
| Consumers | Steps 4-5 (deadline countdown display), deadline warning logic |
| Owner | Continue command (computed at display time) |
| Integration risk | LOW -- pure computation from deadline artifact |
| Validation | Non-negative integer if deadline exists; warning at <=7, critical at <=3 |

### suggested_command

| Attribute | Value |
|-----------|-------|
| Source of truth | Computed: wave-specific state -> first incomplete task -> command-to-agent routing table |
| Consumers | Steps 4-6 (suggested next action display) |
| Owner | Continue command (computed from state analysis) |
| Integration risk | HIGH -- wrong suggestion sends user to wrong command |
| Validation | Must be a valid command from the command-to-agent routing table in wave-agent-mapping skill |

### output_format

| Attribute | Value |
|-----------|-------|
| Source of truth | `.sbir/proposal-state.json` -> `output_format` |
| Consumers | Step 4 (Wave 4+ display shows format) |
| Owner | sbir-orchestrator / FormatConfigService |
| Integration risk | LOW -- informational display only in continue output |
| Validation | "latex" or "docx"; treat missing as "docx" |

---

## Consistency Rules

1. **company_name** must come from `~/.sbir/company-profile.json` in all steps. Never hardcode or cache across sessions.
2. **topic_id** and **topic_title** must come from `.sbir/proposal-state.json` in all steps. Never derive from filesystem paths or artifact filenames.
3. **current_wave** must be read fresh from state at command invocation time. Never rely on session memory.
4. **suggested_command** must be computed from the command-to-agent routing table, not hardcoded per wave. If the routing table changes, suggestions update automatically.
5. **days_remaining** must be computed at display time from the current date. Never cached.

## Integration Failure Modes

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Profile JSON corrupt | JSON parse error on `~/.sbir/company-profile.json` | Route to setup with what/why/do error |
| State JSON corrupt | JSON parse error on `.sbir/proposal-state.json` | Surface PES recovery option; suggest `/proposal status` |
| Wave number out of range | `current_wave` < 0 or > 9 | Surface error; suggest manual state inspection |
| Wave status inconsistency | `current_wave` = 3 but `waves.3.status` = "not_started" | Surface warning; display state as-is with note |
| Missing topic fields | `topic.id` or `topic.title` null/missing | Display "Unknown topic" with suggestion to check state |
| Stale deadline | `topic.deadline` in the past | Display "Deadline passed" with days overdue |
