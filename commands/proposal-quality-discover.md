---
description: "Discover proposal quality patterns from past performance and writing preferences"
argument-hint: "- No arguments required"
---

# /proposal quality discover

Launch quality discovery to build writing intelligence from your SBIR/STTR proposal history.

## Usage

```
/proposal quality discover
```

## Flow

1. **Past proposal review** -- Rate each past proposal as weak, adequate, or strong with optional follow-up on practices
2. **Writing style interview** -- Capture tone, detail level, evidence style, and organization preferences
3. **Evaluator feedback extraction** -- Categorize evaluator comments as meta-writing or content feedback
4. **Artifact assembly** -- Write quality artifacts to ~/.sbir/ for downstream agent consumption

Skip any step or cancel at any point. Partial discovery is still valuable.

## Prerequisites

- Company profile at `~/.sbir/company-profile.json` (run `/proposal profile setup` first if needed)
- Past performance entries in company profile improve discovery quality but are not required

## Artifacts Produced

| Artifact | Location | Description |
|----------|----------|-------------|
| `quality-preferences.json` | `~/.sbir/` | Writing style preferences (tone, detail, organization) |
| `winning-patterns.json` | `~/.sbir/` | Proposal ratings, winning practices, cross-proposal patterns |
| `writing-quality-profile.json` | `~/.sbir/` | Categorized evaluator feedback with agency patterns |

## Agent Invocation

@sbir-quality-discoverer

Launch quality discovery. Start with past proposal review -- read past performance entries from the company profile and collect quality ratings for each. Then proceed through writing style interview, evaluator feedback extraction, and artifact assembly.
