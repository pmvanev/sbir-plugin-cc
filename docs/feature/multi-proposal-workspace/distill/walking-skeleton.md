# Walking Skeleton: Multi-Proposal Workspace

## Walking Skeletons (3)

### WS-1: Path Resolution in Multi-Proposal Workspace
- **User Goal**: Phil resolves correct paths for his active proposal
- **Observable Outcome**: State and artifact directories point to the active proposal namespace
- **Layers Touched**: Workspace layout detector -> Active proposal reader -> Path deriver
- **Feature File**: `walking-skeleton.feature`, Scenario 1

### WS-2: Legacy Workspace Continues Working
- **User Goal**: Phil's existing single-proposal workspace works unchanged after plugin update
- **Observable Outcome**: State and artifact directories point to root (legacy) paths
- **Layers Touched**: Workspace layout detector -> Legacy fallback
- **Feature File**: `walking-skeleton.feature`, Scenario 2

### WS-3: Second Proposal Preserves Existing Work
- **User Goal**: Phil starts a second proposal without risking his first
- **Observable Outcome**: New namespace created, existing state unchanged, active pointer updated
- **Layers Touched**: Namespace creation -> State isolation -> Active pointer write
- **Feature File**: `walking-skeleton.feature`, Scenario 3

## Implementation Sequence

1. Enable WS-1 first (path resolution is foundational -- US-MPW-004)
2. Enable WS-2 second (backward compatibility -- US-MPW-005)
3. Enable WS-3 third (namespace creation -- US-MPW-001)

## Stakeholder Demo Script

Each walking skeleton is demo-able:
- WS-1: "Given two proposals in the workspace, all commands target the correct one"
- WS-2: "Your existing single-proposal setup works exactly as before"
- WS-3: "Start a new proposal -- your first proposal is completely untouched"
