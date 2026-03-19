# ADR-029: Partner Designation in Proposal State

## Status

Accepted

## Context

Multiple agents consume partner data during a proposal: topic-scout, solution-shaper, strategist, and writer. Each needs to know which partner is designated for the current proposal. Without a centralized designation, the user must specify the partner separately to each agent, and partner context is lost between sessions.

From user stories (US-PM-006): "Every downstream agent must be told separately about the partner. When Phil switches between proposals, the partner context is lost."

## Decision

Add a `partner` field to `.sbir/proposal-state.json` containing the designated partner slug. All consuming agents read the partner from proposal state rather than requiring separate configuration.

```json
{
  "partner": {
    "slug": "cu-boulder",
    "designated_at": "2026-03-19T10:00:00Z"
  }
}
```

- `null` for non-partnered proposals
- Set during `/proposal new` (for STTR topics, prompted)
- Changeable via `/proposal partner-set {slug}`
- Missing field treated as `null` for backward compatibility

## Alternatives Considered

### Alternative 1: Per-command partner specification

- **What**: User passes `--partner cu-boulder` to each command that needs partner awareness.
- **Evaluation**: No state change needed. Simple per-invocation.
- **Rejection**: Violates usability principle. User stories document the pain of specifying partner separately to each agent (US-PM-006). Context loss between sessions means re-specifying every time. Error-prone: forgetting `--partner` on one command produces inconsistent content.

### Alternative 2: Global active partner (not per-proposal)

- **What**: Store active partner in `~/.sbir/active-partner.json` globally.
- **Evaluation**: Simplest implementation.
- **Rejection**: Different proposals may use different partners. Global state would require switching when moving between proposals. Per-proposal state already exists (`proposal-state.json`) and is the natural location.

### Alternative 3: Partner designation in the partner profile itself

- **What**: Add an `active_for_proposals[]` field to each partner profile.
- **Evaluation**: Partner knows which proposals it is attached to.
- **Rejection**: Inverts the ownership. Proposal state owns the proposal context; partner profile owns partner data. A proposal should know its partner, not the other way around. Listing "which partner is on this proposal?" requires scanning all partner files instead of reading one state file.

## Consequences

- **Positive**: Single read of proposal state tells any agent which partner to use. No per-command configuration. Context persists across sessions.
- **Positive**: Backward compatible: existing proposals without the field continue to work (null default).
- **Positive**: Partner change in one place (`/proposal partner-set`) propagates to all agents.
- **Negative**: Partner change mid-proposal may create stale artifacts (approach brief, strategy brief reference the old partner). Mitigated by warning the user when changing partner (US-PM-006 scenario 3).
