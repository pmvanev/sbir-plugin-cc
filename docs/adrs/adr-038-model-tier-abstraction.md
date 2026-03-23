# ADR-038: Model Tier Abstraction Over Concrete Model Names

## Status

Accepted

## Context

Rigor profiles must map agent roles to models. Anthropic releases new models periodically (Haiku 4, Sonnet 4, Opus 4, etc.). If profiles reference concrete model names (e.g., `claude-sonnet-4-20250514`), every model release requires updating profile definitions and potentially re-validating behavior.

### Option A: Concrete model names in profile definitions

Profiles directly reference model IDs like `claude-sonnet-4-20250514`.

- **Pros**: No indirection. Explicit and verifiable.
- **Cons**: Every Anthropic model release requires profile updates. If a user's subscription doesn't include a specific model, profiles break silently. Tight coupling to Anthropic's versioning scheme.

### Option B: Model tier abstraction with separate tier-to-model mapping

Profiles reference tiers (basic/standard/strongest). A separate `config/model-tiers.json` maps tiers to concrete model IDs. When Anthropic releases a new model, only the tier mapping file changes.

- **Pros**: Profile definitions stable across model releases. Single file to update on new model release. Users can customize tier mapping for their subscription level. Tier names are meaningful to users ("basic" vs "strongest" vs "claude-haiku-4-20250506").
- **Cons**: One additional indirection. If tier mapping is wrong, all profiles affected.

### Option C: Let Claude Code handle model selection entirely

Tiers map to model capability classes that Claude Code resolves at runtime.

- **Pros**: Zero maintenance.
- **Cons**: Claude Code does not expose a model capability API. No mechanism exists for this.

## Decision

**Option B: Three-tier abstraction (basic/standard/strongest) with `config/model-tiers.json` mapping.**

Tiers:
- **basic**: Fastest, cheapest model suitable for go/no-go screening (maps to Haiku-class)
- **standard**: Balanced capability for most proposal work (maps to Sonnet-class)
- **strongest**: Maximum capability for must-win proposals (maps to Opus-class)

The mapping file is plugin-level, user-overridable by placing a `model-tiers.json` in `.sbir/`.

## Consequences

### Positive

- Profile definitions never need updating for new model releases
- Users see meaningful tier names, not opaque model IDs
- Tier mapping customizable per workspace (e.g., team without Opus access maps "strongest" to Sonnet)
- Single maintenance point for model updates

### Negative

- One additional file read during resolution (negligible)
- Three tiers may not capture all nuance (acceptable -- covers 95% of use cases)
