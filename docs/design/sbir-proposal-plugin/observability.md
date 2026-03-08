# Observability -- sbir-proposal-plugin

## Context

This is a local CLI plugin. There are no servers to monitor, no metrics to scrape, no distributed traces to collect. Observability is limited to what exists on the user's machine.

## PES Audit Log (sole observability mechanism)

The PES enforcement system writes an append-only audit log to `.sbir/audit/`. This is the only observability surface for the plugin.

### What Gets Logged

| Event | Data |
|-------|------|
| Enforcement decisions | Rule evaluated, state at time of evaluation, allow/block/warn result, timestamp |
| Human checkpoint decisions | Approve/revise/skip/quit, artifact affected, timestamp |
| Waivers | Rule waived, reason provided, timestamp |
| Session startup findings | Orphaned files, state corruption, deadline warnings |

### Log Format

Structured JSON, one entry per line. Human-readable via `jq` or any JSON viewer.

### Retention

Default: 365 days. Configured in `pes-config.json`. Local disk only -- no external shipping.

## What This Plugin Does NOT Need

- Application performance monitoring
- Metrics collection (Prometheus, Datadog, etc.)
- Distributed tracing
- Log aggregation services
- SLO dashboards
- Alerting tiers
- Incident response procedures

These concerns apply to deployed services. A local CLI plugin has none of these needs.

## Future Consideration (Phase C2+)

If plugin usage telemetry becomes valuable (with explicit user consent), it could be implemented as opt-in anonymous usage statistics. This is not a Phase C1 concern.
