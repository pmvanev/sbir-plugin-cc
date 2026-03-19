# ADR-028: Partner Profiles as Separate Files Per Partner

## Status

Accepted

## Context

Partner profile data must be persisted for reuse across proposals. The user works with multiple partners (CU Boulder, NDSU, SWRI) and may designate different partners for different proposals. The company profile is a single file at `~/.sbir/company-profile.json`. Partner profiles need a storage strategy.

Key requirements from discovery:
- Multiple partners exist simultaneously (Q3: 3 named partners)
- Partners are reused across proposals (Q7: "usually with a prior partner")
- Each partner has independent lifecycle (created, updated, potentially removed)
- Partner profiles are global (not per-proposal) -- same partner data used across proposals

## Decision

Store each partner profile as a separate JSON file at `~/.sbir/partners/{slug}.json`, where `slug` is derived from the partner name (lowercase, hyphens, no spaces).

Directory structure:
```
~/.sbir/
  company-profile.json
  partners/
    cu-boulder.json
    ndsu.json
    swri.json
```

## Alternatives Considered

### Alternative 1: Embed partners in company profile

- **What**: Add `partners[]` array to `~/.sbir/company-profile.json`.
- **Evaluation**: Simple (single file). But company profile is a single-entity document with its own validation schema. Adding partners conflates two domain concepts. Schema migration required for all existing profiles. Per-partner updates require rewriting the entire company profile. Listing/filtering partners requires parsing the company profile.
- **Rejection**: Violates single responsibility. Company profile schema is established and validated (ADR-015). Adding partners would require schema migration and complicate validation.

### Alternative 2: Single partners collection file

- **What**: Store all partners in `~/.sbir/partners.json` as a JSON array or object.
- **Evaluation**: Simpler than directory approach (one file). But per-partner updates require rewriting all partners. File grows with partner count. Atomic writes more complex (backup/restore affects all partners). Concurrent access (unlikely but possible) risks data loss.
- **Rejection**: Per-partner atomic writes are cleaner with separate files. The backup (.bak) pattern works per-partner rather than all-or-nothing. File-per-partner mirrors the company profile pattern (one file = one entity).

### Alternative 3: Per-proposal partner storage

- **What**: Store partner profiles in `.sbir/partners/` within each proposal directory.
- **Evaluation**: Keeps partner data local to proposal.
- **Rejection**: Contradicts discovery evidence: partners are reused across proposals (Q7, Q3). Storing per-proposal would require copying partner data for each new proposal, defeating the reuse goal.

## Consequences

- **Positive**: Each partner has independent lifecycle (create, update, backup, delete). Atomic writes work per-partner. Listing partners is a directory glob. Schema validation per-file.
- **Positive**: Mirrors the existing single-entity-per-file pattern (company-profile.json).
- **Positive**: Global storage enables partner reuse across proposals without copying.
- **Negative**: Slug collisions possible (two partners with similar names). Mitigated by deterministic slug generation and collision detection at creation time.
- **Negative**: Directory creation required on first partner setup. Minor operational detail.
