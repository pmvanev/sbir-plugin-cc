# Delivery Surfaces — sbir-developer-feedback

## Surface 1: Python PES (TDD)

**Files to create:**

| File | Type | Quality gate |
|------|------|-------------|
| `scripts/pes/domain/feedback.py` | Domain model | Unit tests + acceptance |
| `scripts/pes/domain/feedback_service.py` | Domain service | Unit tests + acceptance |
| `scripts/pes/ports/feedback_port.py` | Port interface | Covered by adapter tests |
| `scripts/pes/adapters/filesystem_feedback_adapter.py` | Adapter | Acceptance M02 |
| `scripts/sbir_feedback_cli.py` | CLI entry point | Acceptance M03 + walking skeleton |

**Test artifacts** (already created in this DISTILL wave):
- `tests/acceptance/sbir_developer_feedback/walking-skeleton.feature`
- `tests/acceptance/sbir_developer_feedback/milestone-01-domain-model.feature`
- `tests/acceptance/sbir_developer_feedback/milestone-02-adapter.feature`
- `tests/acceptance/sbir_developer_feedback/milestone-03-cli.feature`
- `tests/acceptance/sbir_developer_feedback/milestone-04-privacy-and-guards.feature`
- `tests/acceptance/sbir_developer_feedback/steps/common_steps.py`

**Mutation testing**: Scope to `feedback.py`, `feedback_service.py`, `filesystem_feedback_adapter.py`. Kill rate ≥ 80%.

---

## Surface 2: Markdown Agent + Command (Forge)

**Files to create:**

| File | Type | Quality gate |
|------|------|-------------|
| `commands/proposal-developer-feedback.md` | Slash command | `/nw:forge` validation |
| `agents/sbir-feedback-collector.md` | Interactive agent | `/nw:forge` validation |

**No pytest tests for these files.** Markdown agents/commands are validated via the nWave forge checklist, which evaluates:
- YAML frontmatter correctness (name, description, model, tools, maxTurns)
- Behavioral specification completeness
- Scenario walkthrough coverage (including edge paths)
- Size constraint (agent ≤ 400 lines)
- Skills loading strategy (this agent needs no skills — all logic delegated to CLI)

**What forge validates for `sbir-feedback-collector.md`**:
- [ ] AskUserQuestion flow: type → ratings (conditional on Quality) → free text
- [ ] Empty-submission guard: confirms before saving with no details
- [ ] Bash call to `sbir_feedback_cli.py save` with correct arguments
- [ ] Parses CLI JSON output and confirms to user with feedback_id and file_path
- [ ] Graceful handling when CLI returns non-zero exit code

**What forge validates for `proposal-developer-feedback.md`**:
- [ ] Correct command name: `/sbir:developer-feedback`
- [ ] Dispatches to `sbir-feedback-collector` agent
- [ ] No required context files (command works without any state)
- [ ] YAML frontmatter is complete and correct

---

## Delivery Step Mapping

When `/nw:deliver` produces a roadmap, steps should be labeled with their surface:

| Step | Surface | Delivery method |
|------|---------|----------------|
| 01 — Domain model (FeedbackEntry, FeedbackSnapshot) | Python | `nw:execute` → nw-software-crafter |
| 02 — Domain service (FeedbackSnapshotService) | Python | `nw:execute` → nw-software-crafter |
| 03 — Port + Adapter (FeedbackWriterPort, FilesystemFeedbackAdapter) | Python | `nw:execute` → nw-software-crafter |
| 04 — CLI (sbir_feedback_cli.py) | Python | `nw:execute` → nw-software-crafter |
| 05 — Command + Agent (proposal-developer-feedback.md, sbir-feedback-collector.md) | Markdown | `nw:forge` for each file |
