# Data Models: Multi-Proposal Workspace

## New File: `.sbir/active-proposal`

- **Format**: Plain text, single line, no trailing newline
- **Content**: Lowercase topic ID (e.g., `af263-042`)
- **Location**: `.sbir/active-proposal` (workspace root)
- **Created by**: `/proposal new` (first proposal or subsequent), `/proposal switch`
- **Read by**: Path resolution service (every command, every hook)

Example:
```
af263-042
```

## Directory Layout: Multi-Proposal

```
.sbir/
    active-proposal              # Plain text: "af263-042"
    corpus/                      # SHARED -- unchanged, all proposals access
    proposals/
        af263-042/
            proposal-state.json  # Per-proposal state (same schema as today)
            audit/
                pes-audit.log    # Per-proposal audit log
        n244-012/
            proposal-state.json
            audit/
                pes-audit.log

artifacts/
    af263-042/
        wave-1-strategy/
            compliance-matrix.md
            strategy-brief.md
        wave-3-outline/
            ...
    n244-012/
        wave-1-strategy/
            ...

~/.sbir/                         # GLOBAL -- unchanged
    company-profile.json
    partners/
        partner-a.json
```

## Directory Layout: Legacy (Unchanged)

```
.sbir/
    proposal-state.json          # Root-level state (legacy)
    corpus/
    audit/
        pes-audit.log

artifacts/
    wave-1-strategy/
        compliance-matrix.md
    wave-3-outline/
        ...
```

## Path Resolution Output Model

The path resolution service produces a resolved workspace context:

| Field | Multi-Proposal Value | Legacy Value |
|-------|---------------------|-------------|
| `layout` | `"multi"` | `"legacy"` |
| `state_dir` | `.sbir/proposals/{active}/` | `.sbir/` |
| `artifact_base` | `artifacts/{active}/` | `artifacts/` |
| `audit_dir` | `.sbir/proposals/{active}/audit/` | `.sbir/audit/` |
| `active_proposal` | `"{topic-id}"` | `null` |
| `is_legacy` | `false` | `true` |

## Proposal State Schema Changes

No schema changes to `proposal-state.json` itself. The existing schema (version 2.0.0) is used as-is within each per-proposal namespace. The state file is identical whether at root (legacy) or in namespace (multi-proposal).

One optional field addition for namespace tracking:

| Field | Type | Description |
|-------|------|-------------|
| `namespace` | `string \| null` | The namespace identifier if different from topic ID (set by `--name` flag). `null` when namespace equals topic ID. |

## Migration Data Model

When migrating from legacy to multi-proposal:

### Source (Legacy)
```
.sbir/proposal-state.json           -> read topic.id to derive namespace
.sbir/audit/pes-audit.log           -> per-proposal audit
artifacts/wave-*/                    -> per-proposal artifacts
```

### Target (Multi-Proposal)
```
.sbir/proposals/{topic-id}/proposal-state.json
.sbir/proposals/{topic-id}/audit/pes-audit.log
artifacts/{topic-id}/wave-*/
.sbir/active-proposal = {topic-id}
```

### Safety Net
```
.sbir/proposal-state.json.migrated  # Original preserved
.sbir/audit.migrated/               # Original audit preserved
```

Original files renamed with `.migrated` suffix (not deleted). User can restore by removing `.migrated` suffix and deleting `.sbir/proposals/` directory.

## Dashboard Display Model

The dashboard enumeration produces a list of proposal summaries:

| Field | Source |
|-------|--------|
| `topic_id` | `state["topic"]["id"]` |
| `title` | `state["topic"]["title"]` (truncated for display) |
| `current_wave` | `state["current_wave"]` |
| `deadline` | `state["topic"]["deadline"]` |
| `days_remaining` | Computed at display time |
| `status` | `"active"` / `"completed"` / `"archived"` / `"corrupted"` |
| `is_active` | `true` if this is the active proposal |
| `error` | Error message if state corrupted, `null` otherwise |

### Completion Determination

A proposal is "completed" when any of:
- `waves["8"]["status"] == "completed"` (submitted)
- `archived == true`
- `go_no_go == "no-go"`
