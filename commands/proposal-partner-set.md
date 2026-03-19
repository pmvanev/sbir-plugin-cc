---
description: "Change the designated partner for the current proposal"
argument-hint: "- Required: partner slug (e.g., 'cu-boulder') or partner name"
---

# /proposal partner-set

Designate or change the research institution partner for the active proposal.

## Usage

```
/proposal partner-set cu-boulder
/proposal partner-set "CU Boulder"
```

## Flow

1. **Validate** -- Check that a proposal is active (.sbir/proposal-state.json exists)
2. **Resolve partner** -- Find partner profile at ~/.sbir/partners/{slug}.json. If name given, derive slug.
3. **Stale artifact warning** -- If current wave > 0, warn that existing artifacts may reference the previous partner
4. **Confirm** -- Show current vs. new partner, ask for confirmation
5. **Update state** -- Set `partner.slug` and `partner.designated_at` in proposal-state.json

## Stale Artifact Warning

When changing partners after Wave 0, the following artifacts may need regeneration:

```
WARNING: Changing partner mid-proposal

Current partner: NDSU
New partner:     CU Boulder

The following artifacts may reference the previous partner:
- Fit scoring results (Wave 0)
- Strategy brief teaming section (Wave 1)
- Approach briefs with work splits (Wave 1)

(c) continue -- change partner, regenerate artifacts manually
(q) quit     -- keep current partner
```

## Prerequisites

- Active proposal (.sbir/proposal-state.json exists)
- Partner profile exists at ~/.sbir/partners/{slug}.json
- Run `/proposal partner-setup` first if no partner profiles exist

## Agent Invocation

@sbir-orchestrator

Change the designated partner for the active proposal. Read the current proposal state, resolve the partner slug, check for stale artifacts if wave > 0, confirm with the user, and update the partner field in proposal-state.json.
