---
description: "Detect where you left off in the SBIR proposal lifecycle and get the exact next command to run"
argument-hint: "- No arguments required"
---

# /continue

Detect current SBIR proposal lifecycle state and suggest the next action.

## Usage

```
/sbir:continue
```

## What It Does

Reads all state files (company profile, proposal state, corpus, API key) and classifies your position in the lifecycle. Displays clear status with the exact command to run next.

Works at every stage: no setup, partial setup, no proposal, mid-wave, between waves, post-submission, lifecycle complete, archived, and error conditions.

## Context Files

- `~/.sbir/company-profile.json` -- global company profile
- `.sbir/proposal-state.json` -- project-local proposal state
- `.sbir/corpus/` -- corpus document directory
- `skills/continue/continue-detection.md` -- state detection patterns

## Agent Invocation

@sbir-continue

Detect where the user left off in the SBIR proposal lifecycle and display current state with the next command to run.

SKILL_LOADING: Load skills from `skills/continue/` before beginning work.
