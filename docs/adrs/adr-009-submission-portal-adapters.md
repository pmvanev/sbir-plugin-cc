# ADR-009: Submission Portal Packaging as Data-Driven Adapters

## Status

Accepted

## Context

Wave 8 requires packaging proposals according to portal-specific rules. Three portals supported initially: DSIP (DoD), Grants.gov (multi-agency), NSPIRES (NASA). Each has different file naming conventions, size limits, required attachments, and format requirements. Portal rules change between solicitation cycles.

Key design question: how to handle portal variation without hardcoding rules.

## Decision

Portal packaging rules stored as JSON data files in `templates/portal-rules/`. A single `PortalRulesPort` interface with a `JsonPortalRulesAdapter` loads rules by portal name. The SubmissionService applies rules generically -- no portal-specific logic in domain code.

Phil can edit JSON rule files directly to handle rule changes between solicitation cycles without waiting for a code update.

## Alternatives Considered

### Alternative 1: Hardcoded portal classes
- **What**: One Python class per portal (DSIPPortal, GrantsGovPortal, NSPIRESPortal) with baked-in rules
- **Expected impact**: Works for initial 3 portals
- **Why rejected**: Adding a new portal requires code change. Rule changes between cycles require code update, PR, and release. Violates extensibility principle. Phil cannot self-service.

### Alternative 2: Plugin extension system
- **What**: Each portal as a separate plugin/module loaded dynamically
- **Expected impact**: Maximum extensibility
- **Why rejected**: Over-engineered for 3 portals. Plugin loading adds complexity. JSON data files provide the same extensibility with simpler implementation.

### Alternative 3: YAML configuration
- **What**: Same as chosen approach but YAML instead of JSON
- **Expected impact**: Equivalent functionality, more human-readable
- **Why rejected**: Project convention is JSON for all data files (proposal-state.json, pes-config.json, plugin.json). Adding YAML introduces a second data format and a new dependency (PyYAML). Consistency wins.

## Consequences

- **Positive**: New portals added by creating a JSON file. Zero code changes.
- **Positive**: Phil can update rules when portals change conventions. Self-service.
- **Positive**: Consistent with project convention (JSON everywhere).
- **Negative**: JSON is less human-readable than YAML for nested structures. Acceptable given project consistency.
- **Negative**: Complex validation rules (conditional requirements) may eventually outgrow JSON. Cross that bridge when reached -- current requirements are simple conditionals.
