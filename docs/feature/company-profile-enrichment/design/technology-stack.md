# Technology Stack: Company Profile Enrichment

## Stack Summary

No new technology introductions. All choices reuse existing project dependencies or standard library.

| Component | Technology | Version | License | Already in Project | Rationale |
|-----------|-----------|---------|---------|-------------------|-----------|
| HTTP client | httpx | 0.27+ | BSD-3-Clause | Yes (ADR-018) | Timeout control, connection pooling, retry. Already adopted for DSIP adapter. |
| Schema validation | jsonschema | existing | MIT | Yes | Profile validation already uses this. Extended schema validated automatically. |
| Python runtime | Python | 3.12+ | PSF (OSS) | Yes | Project standard. |
| JSON parsing | stdlib json | 3.12+ | PSF (OSS) | Yes | Standard library. No external JSON library needed. |
| File permissions | stdlib os/pathlib | 3.12+ | PSF (OSS) | Yes | `os.chmod(path, 0o600)` for API key file. |
| CLI argument parsing | stdlib argparse | 3.12+ | PSF (OSS) | Yes | Consistent with existing CLI patterns (feedback_cli.py). |
| Testing | pytest + pytest-bdd | existing | MIT | Yes | Existing test framework. |
| Mutation testing | mutmut 2.4.x | existing | Apache-2.0 | Yes | Existing mutation testing setup via Docker. |

## Dependency Analysis

### New pip Dependencies: None

httpx is already a project dependency (installed via `pip install httpx` in CI and Docker). No new packages required.

### API Authentication

| API | Auth Method | Key Storage | Cost |
|-----|------------|-------------|------|
| SAM.gov Entity API v3 | API key in query parameter | `~/.sbir/api-keys.json` | Free (1,000 req/day with entity role) |
| SBIR.gov Company/Awards API | None | N/A | Free (no documented limits) |
| USASpending.gov API | None | N/A | Free (no documented limits) |

### API Rate Limits

| API | Limit | Impact on Enrichment |
|-----|-------|---------------------|
| SAM.gov | 1,000 req/day (personal key with entity role) | No concern -- enrichment makes 1 call per profile setup |
| SBIR.gov | Not documented | Implement 10s timeout + single retry |
| USASpending.gov | Not documented | Implement 10s timeout + single retry |

## httpx Configuration

Enrichment adapters share consistent httpx configuration:

| Setting | Value | Rationale |
|---------|-------|-----------|
| Connect timeout | 5s | Fail fast on unreachable hosts |
| Read timeout | 10s | Government APIs can be slow; 10s balances patience with user experience |
| Follow redirects | True | Government APIs may redirect |
| Retry | 1 retry with 2s delay | Transient failures common on government APIs |
| User-Agent | `sbir-plugin/{version}` | Identify plugin traffic for API operators |

## File Formats

### ~/.sbir/api-keys.json

```json
{
  "sam_gov_api_key": "abc123..."
}
```

Extensible for future API keys. File permissions: owner-read-write only (0600 on Unix; on Windows, relies on user directory ACLs).

### Enrichment CLI JSON Output (enrich mode)

```json
{
  "uei": "DKJF84NXLE73",
  "fields": [
    {
      "field_path": "company_name",
      "value": "Radiant Defense Systems, LLC",
      "source": {"api_name": "SAM.gov", "api_url": "...", "accessed_at": "..."},
      "confidence": "high"
    }
  ],
  "missing_fields": ["capabilities", "security_clearance", "key_personnel"],
  "sources_attempted": ["SAM.gov", "SBIR.gov", "USASpending.gov"],
  "sources_succeeded": ["SAM.gov", "SBIR.gov", "USASpending.gov"],
  "disambiguation_needed": [],
  "errors": []
}
```

### Enrichment CLI JSON Output (diff mode)

```json
{
  "additions": [
    {"field_path": "naics_codes", "api_value": "334220", "source": {"api_name": "SAM.gov"}}
  ],
  "changes": [],
  "matches": ["company_name", "certifications.sam_gov.cage_code"],
  "api_missing": ["capabilities", "key_personnel"]
}
```
