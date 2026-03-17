---
description: "Display current quality artifact status -- existence, freshness, and confidence"
argument-hint: "- No arguments required"
---

# /proposal quality status

Display the current state of quality discovery artifacts. Shows which artifacts exist, when they were last updated, and key summary statistics.

## Usage

```
/proposal quality status
```

## Flow

1. Check each quality artifact at `~/.sbir/`:
   - `quality-preferences.json`
   - `winning-patterns.json`
   - `writing-quality-profile.json`
2. For each artifact: report existence, `updated_at` timestamp, and key statistics
3. Display consumer agents and related commands

## Status Display

Run this Python script to check artifact status, then format the output:

```bash
python -c "
import json, os, sys
sbir_dir = os.path.expanduser('~/.sbir')
artifacts = {
    'quality-preferences.json': {
        'stats': lambda d: [
            f\"Tone: {d.get('preferences', {}).get('tone', 'unknown')}\",
            f\"Practices: {len(d.get('practices_to_replicate', []))} to replicate, {len(d.get('practices_to_avoid', []))} to avoid\"
        ]
    },
    'winning-patterns.json': {
        'stats': lambda d: [
            f\"Confidence: {d.get('confidence_level', 'unknown')} ({len(d.get('rated_proposals', []))} rated)\",
            f\"Patterns: {len(d.get('cross_proposal_patterns', []))} detected\"
        ]
    },
    'writing-quality-profile.json': {
        'stats': lambda d: [
            f\"Feedback entries: {len(d.get('evaluator_feedback', []))}\",
            f\"Agency patterns: {len(d.get('agency_patterns', []))}\"
        ]
    }
}
results = []
for name, config in artifacts.items():
    path = os.path.join(sbir_dir, name)
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        stats = config['stats'](data)
        results.append(json.dumps({'name': name, 'exists': True, 'updated_at': data.get('updated_at', 'unknown'), 'stats': stats}))
    else:
        results.append(json.dumps({'name': name, 'exists': False}))
for r in results:
    print(r)
"
```

Parse the JSON output from the script and display the status in this format:

```
--------------------------------------------
QUALITY ARTIFACT STATUS
--------------------------------------------

quality-preferences.json    [ok] exists    updated: <date>
  Tone: <tone>
  Practices: <n> to replicate, <m> to avoid

winning-patterns.json       [ok] exists    updated: <date>
  Confidence: <level> (<n> rated)
  Patterns: <n> detected

writing-quality-profile.json [!!] not found
  Run /sbir:proposal quality discover to create

Consumer agents:
  sbir-strategist -- reads winning patterns
  sbir-writer     -- reads all three artifacts
  sbir-reviewer   -- reads quality profile + preferences

Commands:
  /sbir:proposal quality discover -- full discovery
  /sbir:proposal quality update   -- update from debrief
--------------------------------------------
```

For artifacts that exist, show `[ok]` with the updated date and key stats from the script output.
For artifacts that do not exist, show `[!!] not found` and direct the user to run quality discovery.

## No Agent Invocation

This command is self-contained. It reads artifact files directly and displays status. No agent delegation required.
