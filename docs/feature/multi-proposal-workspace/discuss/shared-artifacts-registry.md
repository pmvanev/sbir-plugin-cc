# Shared Artifacts Registry: Multi-Proposal Workspace

## Artifacts

### active_proposal
- **Source of truth**: `.sbir/active-proposal` (plain text file containing topic ID)
- **Consumers**:
  - All slash commands (path resolution for state reads/writes)
  - PES hook adapter (scoping enforcement to correct proposal)
  - `/sbir:continue` dashboard (currently active indicator)
  - `/sbir:proposal switch` (read before, write after)
  - `/sbir:proposal status` (header display)
  - All wave commands (header display)
- **Owner**: Orchestrator (sets on `/proposal new`, `/proposal switch`, auto-switch on completion)
- **Integration risk**: HIGH -- wrong active proposal means commands read/write wrong state and artifacts
- **Validation**: After every switch, verify `.sbir/active-proposal` content matches intended proposal. After every state read, verify path includes active proposal namespace.

### proposal_state_path
- **Source of truth**: Derived: `.sbir/proposals/${active_proposal}/proposal-state.json`
- **Consumers**:
  - `JsonStateAdapter` (constructor receives state_dir)
  - Hook adapter (`main()` resolves `state_dir` from CWD)
  - All agents that read state (orchestrator, continue, every wave agent)
- **Owner**: State adapter layer (path resolution)
- **Integration risk**: HIGH -- hardcoded `.sbir/` path in hook adapter `main()` must change to support multi-proposal resolution
- **Validation**: State adapter receives resolved path. Path includes active proposal namespace. Legacy path still works when `.sbir/proposals/` absent.

### artifact_write_path
- **Source of truth**: Derived: `artifacts/${active_proposal}/wave-N-name/`
- **Consumers**:
  - All wave agents (write artifacts)
  - `FilesystemArtifactWriterAdapter` (creates directories, writes files)
  - Status commands (read artifact paths for display)
  - PES post-action validator (verifies artifact writes in correct location)
- **Owner**: Orchestrator dispatches with artifact base path; agents resolve wave subdirectory
- **Integration risk**: HIGH -- every agent references `./artifacts/wave-N-name/` in their markdown. All must be updated or path resolution must happen transparently.
- **Validation**: Every artifact write goes to `artifacts/${active_proposal}/`. No writes to root `artifacts/` in multi-proposal mode.

### company_name
- **Source of truth**: `~/.sbir/company-profile.json` (field: `company_name`)
- **Consumers**:
  - Dashboard header
  - Proposal new (shared resources display)
- **Owner**: Company profile builder (global, unchanged by this feature)
- **Integration risk**: LOW -- global resource, read-only in this feature
- **Validation**: Same value displayed everywhere.

### partner_list
- **Source of truth**: `~/.sbir/partners/*.json` (one file per partner)
- **Consumers**:
  - Proposal new (shared resources display)
  - Per-proposal state (partner.slug references slug from this list)
- **Owner**: Partnership management (global, unchanged by this feature)
- **Integration risk**: LOW -- global resource, read-only in this feature
- **Validation**: Partner slugs in per-proposal state match files in `~/.sbir/partners/`.

### corpus
- **Source of truth**: `.sbir/corpus/` (shared directory)
- **Consumers**:
  - All proposals (corpus search during any wave)
  - Proposal new (shared resources count display)
  - Corpus librarian agent
- **Owner**: Corpus librarian (shared across all proposals)
- **Integration risk**: MEDIUM -- corpus is shared but per-proposal compliance matrices reference specific corpus documents. If a corpus document is removed, references break.
- **Validation**: Corpus paths referenced in per-proposal artifacts still resolve.

### per_proposal_state_files
- **Source of truth**: `.sbir/proposals/${topic_id}/proposal-state.json`
- **Consumers**:
  - State adapter (load/save for active proposal)
  - Dashboard (enumerate for multi-proposal view)
  - Switch command (verify target exists)
- **Owner**: Per-proposal orchestrator context
- **Integration risk**: MEDIUM -- enumeration must handle corrupted state in one proposal without breaking dashboard for others
- **Validation**: Each `.sbir/proposals/*/proposal-state.json` is valid JSON. Corrupted file for one proposal shows error for that row, not crash.

---

## Integration Checkpoints

### Checkpoint 1: Proposal Creation Isolation
**When**: After `/proposal new` creates a second proposal
**Verify**:
- Existing proposal state file byte-identical before and after
- New proposal state file exists at namespaced path
- Active proposal pointer updated
- No files written to existing proposal's artifact directory

### Checkpoint 2: Path Resolution Consistency
**When**: After any context switch
**Verify**:
- `JsonStateAdapter` receives `.sbir/proposals/${active_proposal}/` as state_dir
- Hook adapter resolves state_dir to active proposal namespace
- Artifact writer resolves to `artifacts/${active_proposal}/`
- All three paths agree on which proposal is active

### Checkpoint 3: PES Enforcement Scoping
**When**: During any PES hook evaluation in multi-proposal workspace
**Verify**:
- PES reads state from active proposal (not root, not another proposal)
- Wave ordering enforcement uses active proposal's wave state
- Audit log entries tagged with proposal ID
- Block messages reference the active proposal by name

### Checkpoint 4: Backward Compatibility
**When**: Any command runs in legacy single-proposal workspace
**Verify**:
- No `.sbir/proposals/` directory created
- State read from `.sbir/proposal-state.json` (root)
- Artifacts written to `artifacts/wave-N-name/` (root)
- No multi-proposal UI elements displayed
- No migration forced or suggested (except during `/proposal new`)

### Checkpoint 5: Dashboard Resilience
**When**: Dashboard renders with one corrupted proposal state
**Verify**:
- Healthy proposals display normally
- Corrupted proposal shows error indicator with what/why/do guidance
- Dashboard does not crash or show partial output
- Active proposal indicator still shown correctly

---

## Impact Analysis: Components Requiring Changes

### Python (PES)
| Component | Current Path | Multi-Proposal Path | Change Type |
|-----------|-------------|---------------------|-------------|
| `hook_adapter.main()` | `os.path.join(os.getcwd(), ".sbir")` | Resolve via active-proposal file | Path resolution |
| `JsonStateAdapter` | Receives `state_dir` | No change (already parameterized) | None |
| `FileAuditAdapter` | `os.path.join(state_dir, "audit")` | Per-proposal audit dir | Path resolution |
| `FilesystemArtifactWriterAdapter` | Fixed artifact path | Receives namespaced path | Path resolution |
| `PostActionValidator` | Validates artifact paths | Must validate against namespaced paths | Validation rules |

### Markdown (Agents)
| Agent | Path References | Change |
|-------|----------------|--------|
| `sbir-orchestrator` | `.sbir/proposal-state.json` | Read from resolved path |
| `sbir-continue` | `.sbir/proposal-state.json`, `.sbir/corpus/` | Enumerate `.sbir/proposals/*/`, display multi-proposal dashboard |
| `sbir-writer` | `.sbir/compliance-matrix.json`, `.sbir/tpoc-answers.json` | Read from per-proposal namespace |
| `sbir-debrief-analyst` | `.sbir/proposal-state.json`, `./artifacts/wave-9-debrief/` | Read/write from per-proposal namespace |
| `sbir-formatter` | `./artifacts/wave-5-visuals/`, `./artifacts/wave-6-formatted/` | Write to per-proposal artifact namespace |
| `sbir-compliance-sheriff` | Compliance matrix path | Read/write from per-proposal namespace |
| All wave agents | Artifact paths | Write to `artifacts/${active_proposal}/` |

### Skills
| Skill | Path References | Change |
|-------|----------------|--------|
| `continue-detection` | `.sbir/proposal-state.json`, `.sbir/corpus/` | Add multi-proposal detection priority |
| `proposal-state-schema` | Schema documentation | Add `active-proposal` file spec |
| `wave-agent-mapping` | Artifact path patterns | Document namespaced paths |
