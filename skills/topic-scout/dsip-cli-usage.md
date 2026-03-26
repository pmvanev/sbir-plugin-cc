---
name: dsip-cli-usage
description: How to call the DSIP topic CLI for fetching, enriching, scoring, and inspecting topics from dodsbirsttr.mil
---

# DSIP CLI Usage

The DSIP CLI (`scripts/dsip_cli.py`) is the entry point for all topic retrieval from the DoD SBIR/STTR portal. It wires all adapters and services internally. You call it via Bash and read JSON from stdout.

**Always use this CLI. Never import or instantiate adapters directly.**

**Path resolution**: The CLI lives in the plugin installation directory, not the user's project. Always invoke it as `python "${CLAUDE_PLUGIN_ROOT}/scripts/dsip_cli.py"`. The `CLAUDE_PLUGIN_ROOT` environment variable is set automatically by Claude Code when the plugin loads.

## Commands

### fetch -- Topic metadata only (fast, no API detail calls)

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/dsip_cli.py" fetch --status Open
python "${CLAUDE_PLUGIN_ROOT}/scripts/dsip_cli.py" fetch --status Pre-Release --component NAVY
python "${CLAUDE_PLUGIN_ROOT}/scripts/dsip_cli.py" fetch --limit 50
```

Returns JSON with topic list (topic_id, title, status, component, dates, cycle info, Q&A count) but no descriptions, Q&A text, or instructions. Use for quick scans.

### enrich -- Full enrichment (descriptions, Q&A, instructions)

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/dsip_cli.py" enrich --status Open
python "${CLAUDE_PLUGIN_ROOT}/scripts/dsip_cli.py" enrich --status Open --capabilities "software,cyber,AI"
```

Fetches topics, then enriches each candidate via the DSIP API:
- Topic details (description, objective, keywords, technology areas, phase descriptions, ITAR, CMMC)
- Q&A entries (questions and answers from the government)
- Solicitation instructions (BAA preface PDF, extracted as text)
- Component instructions (component-specific PDF, extracted as text)

Applies keyword pre-filter if capabilities are provided. Writes cache to `{state_dir}/dsip_topics.json`.

### score -- Full pipeline with fit scoring

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/dsip_cli.py" score --status Open
python "${CLAUDE_PLUGIN_ROOT}/scripts/dsip_cli.py" score --status Open --no-persist
```

Runs enrich + five-dimension scoring against the company profile. Requires `~/.sbir/company-profile.json`. Writes scored results to `{state_dir}/finder-results.json` (unless --no-persist).

Output includes a `scored` array with per-topic: composite_score, recommendation (GO/EVALUATE/NO-GO), dimensions, disqualifiers, key_personnel_match.

### detail -- Single topic enrichment

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/dsip_cli.py" detail --topic-id 7051b2da4a1e4c52bd0e7daf80d514f7_86352
```

Enriches one specific topic by hash ID. Returns description, Q&A, and all detail fields. Use when drilling into a topic from a previous fetch.

Topic IDs are hash format (e.g., `7051b2da...86352`), returned by the fetch and enrich commands.

## Common Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--status` | (none) | Filter: Open, Pre-Release. No filter returns both. |
| `--component` | (none) | Filter: ARMY, NAVY, USAF, DARPA, CBD, etc. |
| `--limit` | 100 | Topics per API page |
| `--max-pages` | 0 (all) | Cap pagination (0 = fetch all matching) |
| `--capabilities` | (from profile) | Override pre-filter keywords (comma-separated) |
| `--profile` | `~/.sbir/company-profile.json` | Company profile path |
| `--state-dir` | `.sbir` | State dir for cache and results |

## Output Format

All commands write JSON to stdout. The structure for fetch/enrich/score:

```json
{
  "source": "dsip_api",
  "total": 24,
  "total_fetched": 24,
  "candidates_count": 5,
  "eliminated_count": 19,
  "partial": false,
  "error": null,
  "messages": [
    "Keyword match: 5 candidate topics (19 eliminated)",
    "Descriptions: 5/5",
    "Q&A: 3/5",
    "Solicitation Instructions: 5/5",
    "Component Instructions: 5/5"
  ],
  "topics": [ ... ],
  "scored": [ ... ]
}
```

Each enriched topic dict contains:

```json
{
  "topic_id": "7051b2da4a1e4c52bd0e7daf80d514f7_86352",
  "topic_code": "A254-049",
  "title": "Affordable Ka-Band Metamaterial-Based Electronically Scanned Array...",
  "status": "Pre-Release",
  "component": "ARMY",
  "cycle_name": "DOD_SBIR_2025_P1_C4",
  "release_number": 12,
  "published_qa_count": 7,
  "description": "The Test and Evaluation community...",
  "objective": "The objective of this topic is...",
  "keywords": ["Radar", "antenna", "metamaterials"],
  "technology_areas": ["Information Systems", "Materials"],
  "focus_areas": ["Advanced Computing and Software", "Advanced Materials"],
  "itar": false,
  "cmmc_level": "",
  "phase1_description": "...",
  "phase2_description": "...",
  "phase3_description": "...",
  "qa_entries": [
    {"question_no": 1, "question": "<p>...</p>", "answer": "<p>...</p>"}
  ],
  "solicitation_instructions": "extracted text from BAA preface PDF...",
  "component_instructions": "extracted text from component instructions PDF...",
  "enrichment_status": "ok"
}
```

## Completeness Tracking

The `messages` array reports completeness for all 4 data types:
- **Descriptions**: from the `/details` API endpoint
- **Q&A**: from the `/questions` API endpoint (0 is valid when no Q&A posted)
- **Solicitation Instructions**: from BAA preface PDF download
- **Component Instructions**: from component-specific PDF download

When a data source fails for a topic, `enrichment_status` is `"partial"` and specific errors appear in the messages.

## Caching

The CLI caches enriched data in `{state_dir}/dsip_topics.json`. On the second call within 24 hours, cached data is returned without re-fetching. Delete the cache file to force a fresh fetch.

## Error Handling

- If the DSIP API is down, `error` is non-null and `messages` contains fallback guidance.
- Per-topic enrichment failures are isolated and reported per data source.
- If the company profile is missing for `score`, the CLI exits with code 1 and an error JSON.
