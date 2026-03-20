# Technology Stack: Multi-Proposal Workspace

## No New Technologies

This feature requires zero new technology additions. All changes use the existing stack.

| Component | Technology | License | Role in This Feature |
|-----------|-----------|---------|---------------------|
| Path resolution | Python 3.12+ (existing) | PSF (OSS) | New module in `scripts/pes/` using `pathlib` and `os` only |
| State persistence | JSON files (existing) | N/A | Per-proposal `proposal-state.json` in namespaced directories |
| Active pointer | Plain text file (new file, existing tech) | N/A | `.sbir/active-proposal` -- single line of text |
| Agent updates | Markdown (existing) | N/A | Path reference updates in agent behavioral specs via `/nw:forge` or direct edit |
| New command | Markdown (existing) | N/A | `proposal-switch.md` created via `/nw:forge` |
| New skill | Markdown (existing) | N/A | `multi-proposal-dashboard.md` created via `/nw:forge` or direct write |
| Skill updates | Markdown (existing) | N/A | Multi-proposal detection patterns added to continue-detection |
| Testing (Python) | pytest (existing) | MIT | Unit tests for path resolution module |
| Testing (Agents) | Manual + acceptance scenarios | N/A | Agent behavioral changes validated via nWave forge checklist |

## Technology Decision: No New Dependencies

The feature is entirely implementable with Python stdlib (`pathlib`, `os`, `json`, `shutil`). No external libraries needed.

### Rationale

- Path resolution is string derivation from filesystem structure
- Layout detection is directory/file existence checks
- Migration is file copy/rename operations
- All operations are synchronous, single-process, local filesystem

### Alternatives Considered

| Alternative | Why Rejected |
|------------|-------------|
| SQLite for proposal registry | Adds dependency for what is essentially directory enumeration. Plain text pointer + filesystem structure is simpler and human-debuggable. |
| TOML/YAML config for active proposal | Adds parsing dependency for a single value. Plain text file is maximally simple. |
