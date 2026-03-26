# ADR-042: API Key Storage in Separate File

## Status

Accepted

## Context

The SAM.gov Entity API requires a free personal API key. The plugin needs to store this key persistently so the user enters it once. The question is where to store it: in the existing `~/.sbir/company-profile.json`, in a new dedicated file, or in environment variables.

Security considerations: the API key grants access to federal entity data queries. It is not highly sensitive (free, personal-tier, read-only access) but should not be exposed casually in profile data that may be shared or version-controlled.

## Decision

Store API keys in a separate file `~/.sbir/api-keys.json` with owner-only file permissions (0600 on Unix). Schema: `{"sam_gov_api_key": "..."}`. Extensible for future API keys.

The key is never passed as a CLI argument (visible in process listing). The enrichment CLI reads the key directly from the file.

## Alternatives Considered

### Alternative 1: Store in ~/.sbir/company-profile.json

- **Evaluation**: No new file. Profile already has a `certifications.sam_gov` section.
- **Rejection**: Mixes credential data with profile data. Company profile may be shared with team members or displayed in status output. API key would be exposed inadvertently. Violates principle of least privilege.

### Alternative 2: Environment variable (SBIR_SAM_GOV_API_KEY)

- **Evaluation**: Standard approach for API keys. No file to manage.
- **Rejection**: User must set the variable in their shell profile. Not persistent across terminal restarts without shell configuration. Claude Code agents cannot reliably set environment variables for future sessions. Higher friction than a one-time file save.

### Alternative 3: System keychain (keyring library)

- **Evaluation**: Most secure option. Uses OS-level credential storage (macOS Keychain, Windows Credential Manager, Linux Secret Service).
- **Rejection**: Requires `keyring` Python library as new dependency. Behavior varies across OS and desktop environment. Headless/SSH environments often lack a keychain daemon. Adds complexity disproportionate to the security level of a free, read-only API key.

## Consequences

### Positive

- Credential data separated from profile data
- Simple JSON file -- no new dependencies
- Owner-only permissions limit access
- Extensible for future API keys (SBIR.gov if they add auth, Grants.gov, etc.)
- Consistent with existing project pattern (JSON files in ~/.sbir/)
- Key never visible in CLI process listings

### Negative

- Additional file to manage (~/.sbir/api-keys.json)
- File permissions are Unix-only; Windows relies on user directory ACLs
- Not as secure as OS keychain (file is readable by any process running as the user)
