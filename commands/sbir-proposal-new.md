# /proposal new

Start a new proposal from a solicitation document.

## Usage

```
/proposal new <solicitation-file-path>
```

## Flow

1. **Parse solicitation** -- Extract topic ID, agency, phase, deadline, and title from the provided document
2. **Search corpus** -- Find related past work from ingested documents using keyword matching
3. **Fit scoring** -- Score fit across subject matter, past performance, and certifications
4. **Go/No-Go checkpoint** -- Present analysis and wait for human decision:
   - **go** -- Record decision, unlock Wave 1 for proposal writing
   - **no-go** -- Archive the proposal
   - **defer** -- Save state for later decision

## Prerequisites

- No active proposal in current directory (run `/proposal status` to check)
- Solicitation document must contain extractable text (not scanned images)

## Required metadata

The parser extracts these fields from the solicitation text:

| Field | Required | Example |
|-------|----------|---------|
| Topic ID | Yes | AF243-001 |
| Agency | Yes | Air Force |
| Phase | No (defaults to I) | I, II |
| Deadline | No (prompts for manual entry) | 2026-04-15 |
| Title | Yes | Compact Directed Energy for Maritime UAS Defense |

## Examples

```
/proposal new ./solicitations/AF243-001.pdf
```

After parsing, you will see:
- Parsed metadata (topic ID, agency, phase, deadline, title)
- Related past work from corpus (if any documents ingested)
- Fit scoring and Go/No-Go recommendation

## Implementation

This command invokes `ProposalCreationService.create_proposal()` (driving port) which orchestrates:
- `SolicitationParser.parse()` (driven port) for metadata extraction
- Keyword-based corpus search against cataloged document paths
- `StateWriter.save()` (driven port) to persist initial proposal state

The Go/No-Go decision is recorded via `ProposalCreationService.record_decision()`.
