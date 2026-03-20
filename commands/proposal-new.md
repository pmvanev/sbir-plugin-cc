---
description: "Start a new SBIR/STTR proposal from a solicitation document"
argument-hint: "<solicitation-file-path> [--name <namespace>] - Path to solicitation PDF or text file"
---

# /proposal new

Start a new proposal from a solicitation document. Creates a per-proposal namespace under `.sbir/proposals/{topic-id}/` and `artifacts/{topic-id}/`. Multiple proposals can coexist in the same workspace with shared corpus and company profile.

## Usage

```
/proposal new <solicitation-file-path> [--name <namespace>]
```

### Flags

| Flag | Description |
|------|-------------|
| `--name <namespace>` | Override the default namespace (derived from topic ID). Useful for resubmissions where the topic ID collides with an existing proposal. Example: `--name af263-042-v2`. |

## Flow

1. **Parse solicitation** -- Extract topic ID, agency, phase, deadline, and title from the provided document
2. **Derive namespace** -- Lowercase the topic ID for filesystem safety (e.g., `AF263-042` -> `af263-042`). If `--name` is provided, use that instead.
3. **Collision check** -- If `.sbir/proposals/{namespace}/` already exists, fail with error: "A proposal with topic ID '{topic-id}' already exists. Use `--name {topic-id}-v2` to create a differently-named proposal." No files are created or modified.
4. **Legacy detection** -- If a legacy workspace is detected (`.sbir/proposal-state.json` at root, no `.sbir/proposals/`), prompt for migration before proceeding.
5. **Create namespace** -- Create `.sbir/proposals/{namespace}/`, `.sbir/proposals/{namespace}/audit/`, and `artifacts/{namespace}/`
6. **Set active proposal** -- Write namespace to `.sbir/active-proposal` (plain text, single line)
7. **Initialize state** -- Create `proposal-state.json` in the namespace directory with parsed metadata
8. **Search corpus** -- Find related past work from ingested documents using keyword matching. List shared resources (corpus, company profile, partners).
9. **Fit scoring** -- Score fit across subject matter, past performance, and certifications
10. **Format selection** -- Prompt for output format (LaTeX or DOCX). Default is DOCX (press Enter to accept). If the solicitation hints at PDF submission (e.g. "submit as PDF", "PDF format required"), a LaTeX recommendation is displayed. The choice is recorded as `output_format` in proposal state.
11. **Go/No-Go checkpoint** -- Present analysis and wait for human decision:
    - **go** -- Record decision, unlock Wave 1 for proposal writing
    - **no-go** -- Archive the proposal
    - **defer** -- Save state for later decision

## Prerequisites

- Solicitation document must contain extractable text (not scanned images)
- If a proposal with the same topic ID already exists, use `--name` to provide an alternative namespace

## Required metadata

The parser extracts these fields from the solicitation text:

| Field | Required | Example |
|-------|----------|---------|
| Topic ID | Yes | AF243-001 |
| Agency | Yes | Air Force |
| Phase | No (defaults to I) | I, II |
| Deadline | No (prompts for manual entry) | 2026-04-15 |
| Title | Yes | Compact Directed Energy for Maritime UAS Defense |

## Multi-Proposal Behavior

- **Fresh workspace**: Creates multi-proposal layout from the first proposal. No legacy root-level state file is created.
- **Existing multi-proposal workspace**: Creates a new namespace alongside existing proposals. Existing proposal state files are unchanged.
- **Legacy workspace**: Detects root-level `proposal-state.json` and prompts for migration before creating the second proposal.
- **Active proposal**: Automatically set to the newly created proposal. Use `/proposal switch` to return to a previous proposal.

## Examples

### First proposal in a fresh workspace
```
/proposal new ./solicitations/AF263-042.pdf
```

Creates `.sbir/proposals/af263-042/`, sets active proposal to `af263-042`, proceeds with fit scoring.

### Second proposal alongside an existing one
```
/proposal new ./solicitations/N244-012.pdf
```

Creates `.sbir/proposals/n244-012/` without modifying the existing proposal. Active proposal switches to `n244-012`.

### Resubmission with namespace override
```
/proposal new ./solicitations/AF263-042-resubmit.pdf --name af263-042-v2
```

Creates namespace `af263-042-v2` to avoid collision with existing `af263-042`.

After parsing, you will see:
- Parsed metadata (topic ID, agency, phase, deadline, title)
- Related past work from corpus (if any documents ingested)
- Shared resources available (corpus document count, company profile, partners)
- Fit scoring and Go/No-Go recommendation
- Output format prompt (with LaTeX recommendation if PDF submission hinted)

## Implementation

This command invokes `ProposalCreationService.create_proposal()` (driving port) which orchestrates:
- `SolicitationParser.parse()` (driven port) for metadata extraction
- Namespace derivation and collision check
- Directory creation for per-proposal namespace
- Active proposal pointer update
- Keyword-based corpus search against cataloged document paths
- `StateWriter.save()` (driven port) to persist initial proposal state in the namespace

The Go/No-Go decision is recorded via `ProposalCreationService.record_decision()`.

## Agent Invocation

@sbir-orchestrator

Parse the solicitation document, create per-proposal namespace, score fit, and present the Go/No-Go checkpoint for human decision.
