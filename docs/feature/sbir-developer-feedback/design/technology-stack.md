# Technology Stack — sbir-developer-feedback

## Stack Summary

No new dependencies. The feature is implemented entirely with Python stdlib and existing project libraries.

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Python domain + adapter | Python 3.12, stdlib only | Matches existing PES codebase. No new packages. |
| UUID generation | `uuid` (stdlib) | `uuid.uuid4()` for feedback IDs |
| Datetime | `datetime` (stdlib) | UTC timestamps |
| JSON serialization | `json` (stdlib) | Feedback file output |
| Git SHA | `subprocess` (stdlib) | `git rev-parse --short HEAD` |
| File I/O | `pathlib.Path` (stdlib) | Atomic write: tmp → rename |
| CLI argument parsing | `argparse` (stdlib) | Matches `dsip_cli.py` pattern |
| Testing | `pytest` (existing) | Unit + acceptance tests |
| Markdown agents | Claude Code agent format | Existing plugin convention |

## No New Dependencies

All required functionality is covered by Python stdlib + existing `pytest` test infrastructure. The `requirements.txt` / `pyproject.toml` do not need modification for production code.

`pytest` is already a dev dependency — no change there either.

## Git SHA Capture

```python
import subprocess
try:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, timeout=5,
    )
    version = result.stdout.strip() if result.returncode == 0 else "unknown"
except Exception:
    version = "unknown"
```

Falls back to `"unknown"` if git is unavailable (fresh clone, no git, container without git).
