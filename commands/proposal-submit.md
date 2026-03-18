---
description: "Execute portal submission with human-in-the-loop confirmation and immutable archival"
argument-hint: "[confirm] - Optional subcommand to provide confirmation number after upload"
---

# /proposal submit

Execute portal submission with human-in-the-loop confirmation capture and immutable archival. The user performs the actual portal upload; this command guides the process and records the result.

## Usage

```
/proposal submit              # Begin submission execution flow
/proposal submit confirm      # Provide confirmation number after portal upload
```

## Prerequisites

- Wave 7 complete (final review signed off)
- Submission package staged in `./artifacts/wave-8-submission/staged/` (from `/proposal submit prep`)
- User has approved the staged package

## Flow

1. **Confirm readiness** -- Human gate: explicit confirmation that user is ready to submit. Surface deadline and time remaining.
2. **Read staged package** -- Inventory all files in `./artifacts/wave-8-submission/staged/` with sizes and checksums
3. **Present upload guide** -- Step-by-step portal upload instructions per identified portal type (from `./artifacts/wave-8-submission/upload-guide.md`)
4. **User performs upload** -- User submits manually to the portal. Agent waits for confirmation.
5. **Capture confirmation** -- User provides confirmation number, submission timestamp, and any portal receipts
6. **Create immutable archive** -- Copy staged files to `./artifacts/wave-8-submission/submitted/`
7. **Write manifest** -- SHA-256 checksums for every archived file, confirmation number, timestamp, topic ID
8. **Update proposal state** -- Record submission timestamp and confirmation in `.sbir/proposal-state.json`
9. **Lock proposal** -- Set immutability flag; PES enforcement blocks all subsequent write operations on submitted artifacts

## Agent Invocation

@sbir-submission-agent

Dispatch to sbir-submission-agent (Wave 8: Phase 4 PREPARE SUBMISSION GUIDE and Phase 5 ARCHIVE AND CONFIRM).

SKILL_LOADING: The submission agent MUST load its skills from `skills/submission-agent/` before beginning work. Skills contain portal-specific packaging rules, naming conventions, size limits, and upload procedures.

The agent also references:
- `skills/corpus-librarian/proposal-archive-reader.md` -- for archive structure and manifest conventions

## Context Files

- `.sbir/proposal-state.json` -- Current wave, agency, deadline, topic metadata
- `./artifacts/wave-8-submission/staged/` -- Pre-approved submission package
- `./artifacts/wave-8-submission/upload-guide.md` -- Portal-specific upload instructions (from prep phase)
- `./artifacts/wave-8-submission/verification-report.md` -- Pre-submission verification results
- `.sbir/compliance-matrix.md` -- Final compliance status

## Implementation

This command invokes `SubmissionService` (driving port):

| Method | Purpose |
|--------|---------|
| `confirm_submission()` | Present confirmation prompt requiring explicit human approval |
| `record_submission()` | Archive files, compute checksums, record confirmation number |

Immutability enforcement via `SubmissionImmutabilityEvaluator`:
- After `record_submission()` sets `immutable=True`, PES hooks block all write operations on submitted artifacts
- Domain models: `ConfirmationPrompt`, `SubmissionRecord` (from `pes.domain.submission`)

## Success Criteria

- [ ] Human confirmation obtained before proceeding
- [ ] Staged package inventoried with file sizes
- [ ] Upload guide presented to user
- [ ] Confirmation number and timestamp captured from user
- [ ] Immutable archive created at `./artifacts/wave-8-submission/submitted/`
- [ ] Manifest written with SHA-256 checksums for every archived file
- [ ] Proposal state updated with submission timestamp and confirmation
- [ ] Immutability flag set -- PES blocks subsequent writes

## Next Wave

**Handoff To**: Wave 9 (Post-submission debrief and lessons learned)
**Deliverables**: Submission manifest | Confirmation receipt | Immutable archive

## Expected outputs

- `./artifacts/wave-8-submission/submitted/` (immutable archive of all submitted files)
- `./artifacts/wave-8-submission/submission-manifest.md`
- `./artifacts/wave-8-submission/confirmation/confirmation-receipt.md`

## Examples

Successful DoD submission:
```
Submission confirmed.
Portal: DSIP | Confirmation: DSIP-2026-AF243-001-0042
Archived: 4 files to submitted/ (SHA-256 verified)
Proposal state updated: wave 8 complete, immutable=true
Next: Wave 9 -- run /proposal debrief when ready
```

Missing confirmation number:
```
A confirmation number is required to record the submission.
Please provide the confirmation number from the portal receipt.
```

Deadline under 6 hours:
```
WARNING: Deadline in 5 hours 23 minutes.
Submit now to allow buffer for portal validation.
Portal tech support: 1-800-XXX-XXXX (DSIP Help Desk)
```

Already submitted (immutability enforced):
```
Proposal AF243-001 is submitted. Artifacts are read-only.
No further modifications permitted. Contact support if correction needed.
```
