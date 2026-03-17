---
description: "Update quality artifacts with new proposal cycle data from Wave 9 debrief"
argument-hint: "- No arguments required"
---

# /proposal quality update

Update quality artifacts with new evaluator feedback from the latest proposal cycle.

## Usage

```
/proposal quality update
```

## Flow

1. **Debrief ingestion** -- Read debrief artifacts from `./artifacts/wave-9-debrief/` to extract outcome and evaluator comments
2. **Existing artifact check** -- Verify quality artifacts exist at `~/.sbir/`; if missing, direct to full discovery
3. **Feedback extraction** -- Auto-categorize evaluator writing quality comments using keyword matching
4. **Stale pattern detection** -- Flag patterns with last_seen over 2 years old for user review
5. **Incremental update** -- Merge new data additively into existing artifacts, recalculate confidence
6. **Update summary** -- Display what changed across all quality artifacts

## Prerequisites

- Quality artifacts at `~/.sbir/` from prior `/proposal quality discover` run
- Debrief artifacts at `./artifacts/wave-9-debrief/` from Wave 9 debrief analysis
- If no quality artifacts exist, run `/proposal quality discover` first
- If no debrief artifacts exist, run debrief analysis first

## Artifacts Updated

| Artifact | Location | Update |
|----------|----------|--------|
| `winning-patterns.json` | `~/.sbir/` | New proposal outcome + winning practices added |
| `writing-quality-profile.json` | `~/.sbir/` | New evaluator feedback categorized and merged |
| `quality-preferences.json` | `~/.sbir/` | Unchanged (preferences are manual, not auto-updated) |

## Agent Invocation

@sbir-quality-discoverer

Launch quality update. Read debrief artifacts from `./artifacts/wave-9-debrief/`, check for existing quality artifacts at `~/.sbir/`, extract and categorize new evaluator feedback, flag stale patterns over 2 years old, merge new data additively, recalculate confidence, and display update summary. Operate in update mode -- not full discovery mode.
