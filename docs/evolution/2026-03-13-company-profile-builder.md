# Evolution: Company Profile Builder

**Date**: 2026-03-13
**Feature**: company-profile-builder
**Status**: COMPLETE

## Summary

Implemented the Company Profile Builder feature — a complete company profile management system for SBIR/STTR proposals. The feature enables profile creation, validation, persistence, extraction merge, and selective update through a ports-and-adapters architecture.

## Scope

### Phase 01: Foundation — Validation & Persistence (2 steps)

| Step | Description | Result |
|------|-------------|--------|
| 01-01 | ProfileValidationService: JSON Schema + business rules (CAGE, UEI, employee count, socioeconomic) | PASS |
| 01-02 | JsonProfileAdapter: atomic file persistence with .tmp/.bak safety | PASS |

### Phase 02: Agent & Commands (2 steps)

| Step | Description | Result |
|------|-------------|--------|
| 02-01 | sbir-profile-builder agent: 4-phase workflow (MODE SELECT → GATHER → PREVIEW → VALIDATE AND SAVE) | PASS |
| 02-02 | Slash commands: `/sbir:proposal profile setup` and `/sbir:proposal profile update` | PASS |

### Phase 03: Extraction & Update (2 steps)

| Step | Description | Result |
|------|-------------|--------|
| 03-01 | Profile extraction merge: additive deep merge with list deduplication, completeness checking | PASS |
| 03-02 | Selective section update: append (arrays) and replace (scalars/dot-path) semantics | PASS |

## Architecture

- **Domain services**: ProfileValidationService, profile_merge, profile_update (pure Python, no infrastructure imports)
- **Port**: ProfilePort (abstract interface for read/write/exists/metadata)
- **Adapter**: JsonProfileAdapter (atomic file I/O with .tmp → .bak → rename pattern)
- **Agent**: sbir-profile-builder.md (single agent handles setup + update per ADR-014)
- **Skill**: profile-domain.md (field-by-field fit scoring knowledge)
- **Schema**: company-profile-schema.json (JSON Schema Draft 2020-12, source of truth per ADR-015)

## ADRs

- ADR-013: Profile Validation Service — Python domain service for deterministic validation
- ADR-014: Single Agent Profile Builder — one agent handles both setup and update flows
- ADR-015: JSON Schema as Profile Source of Truth — schema template as contract

## Test Coverage

- **Acceptance tests**: 34 BDD scenarios (pytest-bdd) across walking skeleton + 3 milestones
- **Unit tests**: 33 targeted tests for mutation coverage
- **Mutation testing**: 96.2% aggregate kill rate (183 mutants, 176 killed)
  - profile_validation.py: 98.1% (105/107)
  - profile_merge.py: 100.0% (25/25)
  - profile_update.py: 100.0% (23/23)
  - json_profile_adapter.py: 82.1% (23/28)

## Artifacts

```
scripts/pes/domain/profile_validation.py
scripts/pes/domain/profile_merge.py
scripts/pes/domain/profile_update.py
scripts/pes/ports/profile_port.py
scripts/pes/adapters/json_profile_adapter.py
agents/sbir-profile-builder.md
skills/profile-builder/profile-domain.md
commands/sbir-proposal-profile-setup.md
commands/sbir-proposal-profile-update.md
templates/company-profile-schema.json
tests/acceptance/company_profile_builder/
tests/unit/test_profile_validation_mutations.py
tests/unit/test_profile_merge_mutations.py
tests/unit/test_profile_update_mutations.py
```

## Waves Completed

- DISCOVER → DISCUSS → DESIGN → DISTILL → DELIVER (all 6 waves)
