# ADR-030: Active Proposal Pointer Mechanism

## Status

Proposed

## Context

Multi-proposal workspaces need a mechanism to indicate which proposal is currently active. Every command and PES hook must resolve paths to the correct per-proposal namespace. The pointer must be readable by both Python (PES hooks) and markdown agents (via Claude Code file reading). It must be resilient to corruption and human-debuggable.

## Decision

Use a plain text file at `.sbir/active-proposal` containing the lowercase topic ID (e.g., `af263-042`). Single line, no JSON, no YAML, no structured format.

## Alternatives Considered

### Alternative 1: JSON configuration file (`.sbir/workspace-config.json`)

- **What**: JSON file with `{"active_proposal": "af263-042", "layout": "multi"}` and potential future workspace settings.
- **Evaluation**: More extensible. Supports additional workspace metadata.
- **Why rejected**: Over-engineering for a single value. JSON parsing adds failure modes (malformed JSON). The only data needed is the active proposal ID. Future workspace config can be added later if needed (YAGNI).

### Alternative 2: Symlink (`.sbir/active` -> `.sbir/proposals/af263-042/`)

- **What**: Filesystem symlink pointing to the active proposal directory.
- **Evaluation**: Path resolution becomes implicit (follow the symlink). No file reading needed.
- **Why rejected**: Windows symlinks require elevated privileges or developer mode. Git Bash symlink behavior is inconsistent across Windows configurations. Phil's environment is Windows with Git Bash -- symlinks are unreliable.

### Alternative 3: Convention-based (most recent `proposal-state.json` modification time)

- **What**: No pointer file. The most recently modified `proposal-state.json` is the active proposal.
- **Evaluation**: Zero additional files. Self-maintaining.
- **Why rejected**: Fragile. PES hooks reading state would change mtime. Background processes could touch files. No explicit user intent. Cannot switch without modifying state.

## Consequences

### Positive
- Maximally simple: one file, one line, one value
- Human-debuggable: `cat .sbir/active-proposal` shows the answer
- Human-fixable: `echo "n244-012" > .sbir/active-proposal` repairs a broken pointer
- Cross-platform: plain text works identically on Windows, macOS, Linux
- No parsing library needed: `Path.read_text().strip()` in Python

### Negative
- No room for additional workspace metadata in this file (separate file needed if future requirements arise)
- No schema validation (mitigated by proposal directory existence check after read)
