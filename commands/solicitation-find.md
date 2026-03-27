---
description: "Search open SBIR/STTR solicitations and score topics against your company profile"
argument-hint: "--agency <name> --phase <I|II> --solicitation <cycle-id> --file <path>"
---

# /solicitation find

Discover and score open SBIR/STTR solicitation topics against your company profile.

## Usage

```
/solicitation find
/solicitation find --agency "Air Force" --phase I
/solicitation find --solicitation "DOD_SBIR_2026_P1_C3"
/solicitation find --file ./solicitation-baa.pdf
```

## Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--agency` | Filter topics by sponsoring agency | `--agency "Air Force"` |
| `--phase` | Filter by SBIR phase (I or II) | `--phase I` |
| `--solicitation` | Filter by solicitation cycle ID | `--solicitation "DOD_SBIR_2026_P1_C3"` |
| `--file` | Use a BAA PDF document as topic source (fallback when DSIP API unavailable) | `--file ./baa.pdf` |

## Flow

1. **Load profile** -- Read company profile from `~/.sbir/company-profile.json`
2. **Fetch topics** -- Query DSIP API for open solicitations (or extract from BAA PDF via `--file`)
3. **Pre-filter** -- Keyword match against company capabilities to eliminate irrelevant topics
4. **Score** -- Five-dimension fit analysis: subject matter expertise, past performance, certifications, eligibility, STTR partnership
5. **Rank and display** -- Present scored topics in descending order with GO/EVALUATE/NO-GO recommendations
6. **Persist** -- Save results to `.sbir/finder-results.json` for later reference

## Pursue Flow

After viewing results, use `pursue <topic-id>` to:
- Display topic confirmation with metadata (ID, title, agency, phase, deadline, score)
- Confirm to transition directly to `/proposal new` with TopicInfo pre-loaded
- Cancel to return to results list

Expired topics cannot be pursued.

## Prerequisites

- Company profile at `~/.sbir/company-profile.json` (create via `/proposal profile setup`)
- Without a profile, search runs in degraded mode with reduced scoring accuracy

## Agent Invocation

@sbir-topic-scout

Search for open SBIR/STTR solicitation topics. **You MUST load the `dsip-cli-usage` skill first and use the DSIP CLI** (`python "${CLAUDE_PLUGIN_ROOT}/scripts/dsip_cli.py"`) for all topic retrieval. Never access dodsbirsttr.mil or sbir.gov directly via web fetch -- the CLI handles all API access. Parse the user's flags (--agency, --phase, --solicitation, --file) and execute the full pipeline: fetch topics from DSIP API or BAA document, pre-filter by company capabilities, score with five-dimension fit analysis, rank results, and display with GO/EVALUATE/NO-GO recommendations. Persist results for later reference. If the user requests pursue, validate the topic deadline and hand off TopicInfo to /proposal new.
