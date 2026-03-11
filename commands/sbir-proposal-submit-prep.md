---
description: "Prepare submission package for portal upload with compliance verification"
argument-hint: "[approve|revise] - Optional subcommand for checkpoint action"
---

# /proposal submit prep

Prepare submission package for portal upload. Identifies portal, applies packaging rules, verifies compliance, and stages files for manual submission.

## Usage

```
/proposal submit prep              # Run full submission preparation
/proposal submit prep approve      # Approve staged package and unlock submission
/proposal submit prep revise       # Revise with feedback
```

## Prerequisites

- Wave 7 final review complete and approved (sign-off recorded)
- Formatted proposal assembled in `./artifacts/wave-6-formatted/`
- Compliance matrix fully resolved (all items covered or waived)

## Flow

1. **Identify submission portal** -- Determine portal (DSIP, Grants.gov, NSPIRES) based on agency from proposal state
2. **Surface deadline** -- Display deadline and time remaining; warn if under 48 hours
3. **Load portal packaging rules** -- Read portal-specific rules from `templates/portal-rules/` for naming, size limits, and required files
4. **Inventory assembled files** -- Read all files from `./artifacts/wave-6-formatted/` and catalog volumes, attachments, and forms
5. **Apply portal naming conventions** -- Rename files to match portal-required patterns and verify size limits
6. **Verify package integrity** -- Check PDF validity, budget consistency, and company name/PI/UEI consistency across documents
7. **Stage submission files** -- Write packaged files to `./artifacts/wave-8-submission/staged/`
8. **Write packaging report** -- Document each file with portal slot, naming applied, size, and verification results
9. **Present human checkpoint** -- Package is ready to submit | fix flagged issues

## Agent Invocation

@sbir-submission-agent

Dispatch to sbir-submission-agent (Wave 8: Phases 1-4). The agent loads these skills during execution:
- `skills/submission-agent/portal-packaging-rules.md` -- portal identification, naming conventions, size limits, required files, and upload procedures

SKILL_LOADING: The submission agent MUST load its skills from `skills/submission-agent/` before beginning work. Skills contain portal-specific packaging rules without which generic packaging causes portal rejections.

## Context Files

- `.sbir/proposal-state.json` -- Agency, topic ID, deadline, and current wave status
- `.sbir/compliance-matrix.md` -- Full compliance coverage for verification
- `./artifacts/wave-6-formatted/` -- Assembled proposal volumes (formatter output)
- `./artifacts/wave-7-review/sign-off-record.md` -- Wave 7 sign-off confirmation
- `templates/portal-rules/{portal}.json` -- Portal-specific packaging rules (DSIP, Grants.gov, NSPIRES)

## Implementation

This command invokes `SubmissionService` (driving port):

| Method | Purpose |
|--------|---------|
| `prepare_package()` | Identify portal, apply naming conventions, verify size limits, detect missing files |
| `confirm_submission()` | Present human confirmation checkpoint before user submits |
| `record_submission()` | After user provides confirmation number, create immutable archive with checksums |

Domain models: `PortalRules`, `PackageFile`, `PackageResult`, `ConfirmationPrompt`, `SubmissionRecord` (from `pes.domain.submission`).

Portal identification uses `PortalRulesLoader.identify_portal()` (driven port) to map agency name to portal ID.

## Success Criteria

- [ ] Portal identified and confirmed with user
- [ ] Deadline surfaced with time remaining
- [ ] All files renamed per portal naming convention
- [ ] File sizes verified against portal limits
- [ ] PDF integrity verified (valid, no passwords, pages render)
- [ ] Budget consistency verified across cost volume and justification
- [ ] Company name, PI name, and UEI consistent across all documents
- [ ] Staged files written to `./artifacts/wave-8-submission/staged/`
- [ ] Packaging report written to `./artifacts/wave-8-submission/packaging-report.md`
- [ ] Verification checklist written to `./artifacts/wave-8-submission/verification-report.md`

## Next Wave

**Handoff To**: User performs manual portal upload, then returns to confirm submission (triggers archive and Wave 9)
**Deliverables**: Staged submission package | Packaging report | Verification report | Upload guide

## Expected outputs

- `./artifacts/wave-8-submission/staged/` -- Portal-ready files with correct naming
- `./artifacts/wave-8-submission/packaging-report.md`
- `./artifacts/wave-8-submission/verification-report.md`
- `./artifacts/wave-8-submission/upload-guide.md`

## Examples

Package ready:
```
Portal: DSIP (Air Force)
Deadline: 2026-04-15 (34 days remaining)
Files staged: 3 volumes + 2 attachments
Size checks: all within 50 MB limit
Verification: 47/47 compliance items covered | budget consistent | PI/UEI consistent
Package ready for manual submission -- follow upload guide.
```

Deadline warning:
```
Portal: Grants.gov (NSF)
Deadline: 2026-03-13 (36 hours remaining)
WARNING: Under 48-hour buffer. Complete submission within 12 hours to allow for portal issues.
Grants.gov technical support: 1-800-518-4726
```

Missing required file:
```
Portal: NSPIRES (NASA)
Missing required file: quad_chart
Guidance: NASA requires a 1-page quad chart (under 1 MB). Add to artifacts/wave-6-formatted/ and re-run.
Package blocked -- resolve missing files before staging.
```

Size violation:
```
Portal: DSIP (DoD)
Size violation: volume-1-technical.pdf (62.3 MB) exceeds 50.0 MB limit
Reduce file size (compress images, reduce resolution) and re-run.
```
