# Architecture Design — sbir-developer-feedback

## Summary

`/sbir:developer-feedback` is a lightweight, fully local feedback command. A markdown agent handles the interactive UX; a Python CLI script assembles and persists the context snapshot. Architecture reuses all existing PES adapters — no new infrastructure is required.

**Pattern**: Ports-and-Adapters (OOP) — consistent with the rest of `scripts/pes/`.
**Paradigm**: OOP (project-wide convention per CLAUDE.md).
**New components**: 5 (domain model, domain service, port, adapter, CLI) + 2 markdown files.
**Reused components**: 5 existing adapters read by the CLI.

---

## C4 System Context Diagram

```mermaid
C4Context
    title System Context — /sbir:developer-feedback

    Person(user, "Plugin User", "Proposal writer or developer using the SBIR plugin in Claude Code")

    System(plugin, "SBIR Plugin (Claude Code)", "Multi-agent proposal lifecycle system. Provides /sbir:developer-feedback command.")

    System_Ext(fs, "Local Filesystem", "Stores .sbir/ state, ~/.sbir/ company profile, git repository")

    Rel(user, plugin, "Invokes /sbir:developer-feedback, provides feedback type / ratings / free text")
    Rel(plugin, fs, "Reads proposal state, rigor profile, company profile, finder results. Writes feedback entry.")
    Rel(fs, plugin, "Returns state data for snapshot assembly")
```

---

## C4 Container Diagram

```mermaid
C4Container
    title Container Diagram — /sbir:developer-feedback

    Person(user, "Plugin User")

    Container(cmd, "proposal-developer-feedback.md", "Claude Code Command", "Slash command entry point. Dispatches to feedback-collector agent.")
    Container(agent, "sbir-feedback-collector.md", "Claude Code Agent", "Interactive UX: type selection, optional quality ratings, free text. Calls CLI via Bash.")
    Container(cli, "sbir_feedback_cli.py", "Python CLI", "Wires existing adapters, reads all state, calls FeedbackSnapshotService, writes entry via FilesystemFeedbackAdapter.")
    Container(domain, "feedback.py + feedback_service.py", "Python Domain", "FeedbackEntry / FeedbackSnapshot dataclasses. FeedbackSnapshotService.build_snapshot() assembles snapshot from pre-read dicts.")
    Container(port, "feedback_port.py", "Python Port", "FeedbackWriterPort interface. Dependency inversion boundary.")
    Container(adapter, "filesystem_feedback_adapter.py", "Python Adapter", "Implements FeedbackWriterPort. Atomic JSON write to .sbir/feedback/feedback-{ts}.json.")

    ContainerDb(sbir_state, ".sbir/proposals/{id}/", "JSON Files", "proposal-state.json, rigor-profile.json, artifacts/")
    ContainerDb(sbir_root, ".sbir/", "JSON Files", "finder-results.json, feedback/")
    ContainerDb(home_sbir, "~/.sbir/", "JSON File", "company-profile.json")

    Rel(user, cmd, "Types /sbir:developer-feedback")
    Rel(cmd, agent, "Dispatches with feature context")
    Rel(agent, user, "Asks type, ratings, free text via AskUserQuestion")
    Rel(agent, cli, "Calls via Bash: python scripts/sbir_feedback_cli.py save ...")
    Rel(cli, domain, "Passes pre-read state dicts to build_snapshot()")
    Rel(cli, port, "Calls write() via FilesystemFeedbackAdapter")
    Rel(port, adapter, "Implements")
    Rel(adapter, sbir_root, "Writes feedback-{ts}.json atomically")
    Rel(cli, sbir_state, "Reads via JsonStateAdapter, FilesystemRigorAdapter")
    Rel(cli, sbir_root, "Reads finder-results.json via JsonFinderResultsAdapter")
    Rel(cli, home_sbir, "Reads company-profile.json via JsonProfileAdapter")
```

---

## C4 Component Diagram — Python CLI + Domain

```mermaid
C4Component
    title Component Diagram — sbir_feedback_cli.py and PES Domain

    Component(cli_main, "main() / cmd_save()", "CLI entry", "Parses args (type, ratings, free_text, state_dir, profile_path). Wires adapters. Calls service. Writes. Prints confirmation.")

    Component(workspace, "WorkspaceResolver", "Existing", "resolve_workspace(cwd) -> WorkspaceContext. Finds active proposal dir.")
    Component(state_adapter, "JsonStateAdapter", "Existing adapter", "load() -> dict. Raises StateNotFoundError if missing.")
    Component(rigor_adapter, "FilesystemRigorAdapter", "Existing adapter", "read_active_profile(proposal_dir) -> dict | None")
    Component(profile_adapter, "JsonProfileAdapter", "Existing adapter", "read() -> dict | None. Reads ~/.sbir/company-profile.json.")
    Component(finder_adapter, "JsonFinderResultsAdapter", "Existing adapter", "read() -> dict | None. Reads .sbir/finder-results.json.")

    Component(service, "FeedbackSnapshotService", "New domain service", "build_snapshot(state, rigor, profile, profile_mtime, finder, finder_mtime, cwd) -> FeedbackSnapshot. Pure function — no IO.")
    Component(domain_model, "FeedbackEntry / FeedbackSnapshot / QualityRatings", "New domain models", "Dataclasses. FeedbackType enum. Serialization helpers.")
    Component(port, "FeedbackWriterPort", "New port", "Abstract: write(entry: FeedbackEntry, output_dir: Path) -> Path")
    Component(adapter_fb, "FilesystemFeedbackAdapter", "New adapter", "Implements FeedbackWriterPort. Writes .sbir/feedback/feedback-{ts}.json atomically. Creates dir if absent.")

    Rel(cli_main, workspace, "resolve_workspace(Path.cwd())")
    Rel(cli_main, state_adapter, "load() — catches StateNotFoundError -> None")
    Rel(cli_main, rigor_adapter, "read_active_profile(proposal_dir) — catches FileNotFoundError -> None")
    Rel(cli_main, profile_adapter, "read() — returns None if absent")
    Rel(cli_main, finder_adapter, "read() — returns None if absent")
    Rel(cli_main, service, "build_snapshot(all pre-read dicts + mtimes + cwd)")
    Rel(service, domain_model, "Constructs FeedbackSnapshot")
    Rel(cli_main, domain_model, "Constructs FeedbackEntry(type, ratings, free_text, snapshot)")
    Rel(cli_main, port, "write(entry, output_dir)")
    Rel(port, adapter_fb, "implements")
```

---

## Data Flow

```
User invokes /sbir:developer-feedback
       │
       ▼
sbir-feedback-collector agent
  1. AskUserQuestion: type (Bug/Suggestion/Quality)
  2. If Quality: AskUserQuestion: ratings (1-5 or skip per dimension)
  3. AskUserQuestion: free text (optional)
  4. Bash: python scripts/sbir_feedback_cli.py save \
              --type "{type}" \
              --ratings "{json}" \
              --free-text "{text}"
       │
       ▼
sbir_feedback_cli.py
  1. WorkspaceResolver.resolve_workspace(cwd) -> WorkspaceContext
  2. JsonStateAdapter(state_dir).load() -> state_dict | None
  3. FilesystemRigorAdapter().read_active_profile(proposal_dir) -> rigor | None
  4. JsonProfileAdapter(~/.sbir).read() -> profile | None  (+ stat mtime)
  5. JsonFinderResultsAdapter(.sbir).read() -> finder | None  (+ stat mtime)
  6. subprocess: git rev-parse --short HEAD -> version_str
  7. FeedbackSnapshotService.build_snapshot(...) -> FeedbackSnapshot
  8. FeedbackEntry(id=uuid4(), ts=now(), type, ratings, free_text, snapshot)
  9. FilesystemFeedbackAdapter.write(entry, .sbir/feedback/)
  10. print JSON: {feedback_id, file_path}
       │
       ▼
Agent reads CLI output, confirms to user:
  "Feedback saved. ID: {uuid}. File: .sbir/feedback/feedback-{ts}.json"
```

---

## Integration Points with Existing PES

| Existing Component | How Used | Change Required |
|--------------------|----------|-----------------|
| `workspace_resolver.py` | Resolve active proposal path | None |
| `json_state_adapter.py` | Read proposal-state.json | None |
| `filesystem_rigor_adapter.py` | Read rigor-profile.json | None |
| `json_profile_adapter.py` | Read company-profile.json | None |
| `json_finder_results_adapter.py` | Read finder-results.json | None |

All five are read-only consumers. No existing adapter is modified.

---

## Quality Attribute Decisions

| Attribute | Decision | Rationale |
|-----------|----------|-----------|
| **Testability** | Domain service receives pre-read dicts (not adapter instances) | `build_snapshot()` is a pure function — no mocking needed in unit tests |
| **Maintainability** | CLI pattern matches `dsip_cli.py` | Consistent entry point convention across all PES CLI scripts |
| **Privacy** | Snapshot builder enforces field exclusion at domain layer | Privacy boundary in code, not just documentation |
| **Fault tolerance** | All adapter reads wrapped in try/except at CLI layer | No missing file can crash or block feedback submission |
| **Portability** | No network calls, no external services | Works air-gapped, works on first-time setup |
