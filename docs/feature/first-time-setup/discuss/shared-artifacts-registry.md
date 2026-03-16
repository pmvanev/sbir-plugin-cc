# Shared Artifacts Registry: First-Time Setup

## Registry

### python_version

- **Source of truth**: `python3 --version` runtime check
- **Consumers**: Step 1 (prerequisites display), Step 5 (validation summary)
- **Owner**: Setup agent (runtime detection)
- **Integration risk**: LOW -- read-only system query, same across steps within a session
- **Validation**: Must be >= 3.12. Compared as semantic version.

### git_version

- **Source of truth**: `git --version` runtime check
- **Consumers**: Step 1 (prerequisites display), Step 5 (validation summary)
- **Owner**: Setup agent (runtime detection)
- **Integration risk**: LOW -- read-only system query
- **Validation**: Must be present and parseable.

### claude_code_status

- **Source of truth**: Claude Code authentication check
- **Consumers**: Step 1 (prerequisites display), Step 5 (validation summary)
- **Owner**: Setup agent (runtime detection)
- **Integration risk**: LOW -- read-only check
- **Validation**: Must be "authenticated".

### profile_path

- **Source of truth**: `~/.sbir/company-profile.json` (canonical path)
- **Consumers**: Step 2 (profile display), Step 5 (validation summary)
- **Owner**: sbir-profile-builder agent
- **Integration risk**: HIGH -- path mismatch between setup agent and profile builder would break detection
- **Validation**: File exists at canonical path after Step 2 completes.

### profile_exists

- **Source of truth**: `JsonProfileAdapter.metadata().exists`
- **Consumers**: Step 2 (branching: create vs keep/update), Step 5 (validation), Resume flow
- **Owner**: PES adapters (JsonProfileAdapter)
- **Integration risk**: HIGH -- drives control flow for profile step
- **Validation**: Boolean. Must agree with filesystem state.

### company_name

- **Source of truth**: `~/.sbir/company-profile.json -> company_name`
- **Consumers**: Step 2 (profile display), Step 5 (validation summary), Resume flow (existing setup detection)
- **Owner**: sbir-profile-builder agent
- **Integration risk**: MEDIUM -- display-only, but mismatch would confuse user
- **Validation**: Non-empty string matching profile schema.

### sam_status

- **Source of truth**: `~/.sbir/company-profile.json -> certifications.sam_gov.active`
- **Consumers**: Step 2 (profile completion display), Step 5 (validation warnings)
- **Owner**: sbir-profile-builder agent
- **Integration risk**: HIGH -- inactive SAM triggers NO-GO warning in validation
- **Validation**: Boolean. If false, warning must appear in Step 5.

### cage_code

- **Source of truth**: `~/.sbir/company-profile.json -> certifications.sam_gov.cage_code`
- **Consumers**: Step 2 (profile display), Step 5 (validation summary)
- **Owner**: sbir-profile-builder agent
- **Integration risk**: LOW -- display only
- **Validation**: 5 alphanumeric characters when sam_gov.active is true.

### corpus_document_count

- **Source of truth**: `.sbir/corpus/` index after ingestion
- **Consumers**: Step 3 (ingestion results), Step 5 (validation summary)
- **Owner**: Corpus ingestion logic
- **Integration risk**: MEDIUM -- count must reflect actual indexed files
- **Validation**: Non-negative integer. Zero is valid (skipped corpus).

### corpus_directories

- **Source of truth**: User input during Step 3
- **Consumers**: Step 3 (display confirmation), Step 5 (validation detail)
- **Owner**: Setup agent (user input)
- **Integration risk**: LOW -- used only in display
- **Validation**: Valid filesystem paths (verified during ingestion).

### gemini_api_key_status

- **Source of truth**: `GEMINI_API_KEY` environment variable presence
- **Consumers**: Step 4 (API key display), Step 5 (validation summary)
- **Owner**: Setup agent (environment check)
- **Integration risk**: LOW -- binary check (detected/not detected)
- **Validation**: "detected" or "not detected". Not validated for correctness (that happens in Wave 5).

### setup_status

- **Source of truth**: Computed from all validation checks in Step 5
- **Consumers**: Step 5 (status display), Step 6 (next steps conditional)
- **Owner**: Setup agent (computed)
- **Integration risk**: MEDIUM -- must accurately reflect all prior step results
- **Validation**: One of: "READY", "READY (with warnings)", "INCOMPLETE".

### warning_count

- **Source of truth**: Count of non-blocking issues in Step 5
- **Consumers**: Step 5 (warnings section)
- **Owner**: Setup agent (computed)
- **Integration risk**: LOW -- display only
- **Validation**: Non-negative integer.

---

## Integration Checkpoints

| Checkpoint | Location | Validates |
|------------|----------|-----------|
| Prerequisites gate | Between Step 1 and Step 2 | All three prereqs pass |
| Profile existence | Between Step 2 and Step 3 | Profile file exists and validates |
| Corpus completion | Between Step 3 and Step 4 | Ingestion complete or explicitly skipped |
| Validation consistency | Step 5 | All shared artifacts from Steps 1-4 still valid |
| Resume detection | Start of /sbir:setup | Profile and corpus state checked before entering flow |

## Cross-Step Consistency Rules

1. `python_version` displayed in Step 1 must match value displayed in Step 5
2. `company_name` displayed in Step 2 must match value displayed in Step 5
3. `corpus_document_count` from Step 3 must match Step 5 count
4. `gemini_api_key_status` from Step 4 must match Step 5 status
5. `sam_status` from Step 2 must drive warning display in Step 5
6. `profile_exists` must be true after Step 2 completes (unless user cancelled)
