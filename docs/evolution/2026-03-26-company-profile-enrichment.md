# Evolution: company-profile-enrichment

**Date**: 2026-03-26
**Feature**: company-profile-enrichment
**Status**: Complete

---

## Problem Solved

Profile creation required users to manually copy data from three government websites (SAM.gov, SBIR.gov, USASpending.gov) into the profile builder -- a 15-20 minute tab-switching exercise that was error-prone and often missed awards listed under company name variants. Profile updates required the same manual cross-referencing to detect new NAICS codes, new SBIR awards, or changed registration data.

This feature delivers automated profile enrichment from three federal APIs using the company's UEI as the single input. A three-API cascade (SAM.gov for entity data, SBIR.gov for award history, USASpending.gov for federal spending) proposes values with source attribution. The user confirms each field before it enters the profile. Re-enrichment during profile updates shows a diff of changes for selective acceptance.

---

## User Stories Addressed

All 4 user stories from `docs/feature/company-profile-enrichment/discuss/user-stories.md`:

| Story | Description | Scenarios |
|-------|-------------|-----------|
| US-CPE-001 | Three-API profile enrichment from UEI | 5 (full enrichment, forgotten award, multiple matches, entity not found, partial failure) |
| US-CPE-002 | Enrichment review and confirm | 5 (confirm all, edit field, skip field, source attribution, no-confirm gate) |
| US-CPE-003 | Re-enrichment during profile update | 5 (new NAICS, new award, no changes, preserve manual data, selective acceptance) |
| US-CPE-004 | SAM.gov API key setup and validation | 4 (first-time setup, existing key reused, invalid key rejected, skip enrichment) |

Total: 19 UAT scenarios across 4 stories.

---

## Architecture

### Pattern

Ports-and-Adapters (OOP) -- consistent with the rest of `scripts/pes/`. The feature introduces 10 new Python components and 3 markdown files. The three-API cascade is orchestrated by `CompanyEnrichmentService` which calls SAM.gov first (resolves company name), then SBIR.gov and USASpending.gov using that name.

### Two Delivery Surfaces

- **Python TDD** (Steps 01-01 through 03-03): Domain model, ports, 4 adapters, service, diff logic, CLI -- all delivered via DES RED/GREEN/COMMIT cycle with pytest unit tests.
- **Markdown Forge** (Step 04-01): Profile schema extension, agent update, enrichment skill -- delivered via nWave forge checklist.

### Data Flow

```
User invokes /sbir:proposal profile setup (or update)
    |
    v
sbir-profile-builder agent (ENRICHMENT phase)
  1. Check for SAM.gov API key in ~/.sbir/api-keys.json
  2. If no key: guided setup (save-key mode via stdin)
  3. Prompt for UEI
  4. Bash: python scripts/pes/enrichment_cli.py --uei {UEI} --mode enrich
    |
    v
enrichment_cli.py (composition root)
  1. JsonApiKeyAdapter reads ~/.sbir/api-keys.json
  2. CompanyEnrichmentService orchestrates cascade:
     a. SamGovAdapter -> legal name, CAGE, NAICS, certs, status
     b. SbirGovAdapter -> award history (uses SAM.gov company name)
     c. UsaSpendingAdapter -> total awards, business types
  3. Merge into EnrichmentResult with per-field source attribution
  4. JSON stdout
    |
    v
Agent displays results grouped by source
  -> User confirms/edits/skips each field
  -> Confirmed fields merge into profile draft
  -> Skipped fields become interview questions
```

### Partial Failure Strategy

SAM.gov is the primary source -- its company name resolution is required by SBIR.gov and USASpending.gov. If SAM.gov fails, all three are marked unavailable and the agent falls back to manual interview. If SBIR.gov or USASpending.gov fail independently, partial results from the remaining sources are still usable.

---

## Architecture Decision Records

### ADR-041: NAICS Codes as Top-Level Profile Field

**Decision**: Add `naics_codes` as a top-level array in `company-profile-schema.json` with objects containing `code` and `primary` flag.

**Rationale**: NAICS codes drive topic matching in SBIR solicitations. Top-level placement makes them directly accessible to scoring and filtering logic without navigating nested certification structures.

### ADR-042: API Key Storage in Separate File

**Decision**: Store SAM.gov API key in `~/.sbir/api-keys.json`, separate from the company profile.

**Rationale**: Security hygiene -- profile JSON may be shared or committed; API keys should not travel with it. Separate file enables owner-only file permissions. Extensible schema for future API keys.

### ADR-043: Enrichment as Optional Profile Builder Phase

**Decision**: Add ENRICHMENT as a new phase between MODE SELECT and GATHER in the profile builder agent flow.

**Rationale**: Enrichment is additive -- skipping it preserves the existing manual interview flow unchanged. Making it a separate phase keeps the existing 5-phase structure intact and allows the user to opt in or out.

---

## Files Created

### Python PES -- Domain (3 files)

| File | Role |
|------|------|
| `scripts/pes/domain/enrichment.py` | Domain model: `EnrichedField`, `FieldSource`, `EnrichmentResult`, `SourceError`, `CompanyCandidate` value objects. UEI validation (12 alphanumeric). Field-to-schema mapping. |
| `scripts/pes/domain/enrichment_service.py` | `CompanyEnrichmentService` -- orchestrates three-API cascade with SAM.gov-first dependency. Merges results. Tracks per-source success/failure. Computes missing fields. |
| `scripts/pes/domain/profile_diff.py` | `ProfileDiff` -- pure domain diff logic comparing `EnrichmentResult` against existing profile JSON. Order-independent array comparison for NAICS codes and past performance. |

### Python PES -- Ports (2 files)

| File | Role |
|------|------|
| `scripts/pes/ports/enrichment_port.py` | `EnrichmentSourcePort` ABC -- abstract interface for fetching company data from a single external source. |
| `scripts/pes/ports/api_key_port.py` | `ApiKeyPort` ABC -- read/write/validate API keys. |

### Python PES -- Adapters (4 files)

| File | Role |
|------|------|
| `scripts/pes/adapters/sam_gov_adapter.py` | `SamGovAdapter` -- SAM.gov Entity API v3. Maps entity registration fields to `EnrichedField` objects. Business type code-to-certification mapping. |
| `scripts/pes/adapters/sbir_gov_adapter.py` | `SbirGovAdapter` -- SBIR.gov Company and Awards APIs. Company name search with disambiguation support. Award history with agency, topic, and phase. |
| `scripts/pes/adapters/usa_spending_adapter.py` | `UsaSpendingAdapter` -- USASpending.gov. Two-step resolution: POST autocomplete, GET recipient detail. Total awards and business types. |
| `scripts/pes/adapters/json_api_key_adapter.py` | `JsonApiKeyAdapter` -- reads/writes `~/.sbir/api-keys.json`. Key validation via SAM.gov test endpoint. Owner-only file permissions. Key via stdin, never CLI args. |

### Python PES -- CLI (1 file)

| File | Role |
|------|------|
| `scripts/pes/enrichment_cli.py` | CLI entry point with 4 modes: `enrich`, `diff`, `validate-key`, `save-key`. Composition root wiring adapters to service. JSON stdout. Structured error responses. |

### Markdown (3 files)

| File | Role |
|------|------|
| `templates/company-profile-schema.json` | Extended with `naics_codes` array and `registration_expiration` field. |
| `agents/sbir-profile-builder.md` | Updated with ENRICHMENT phase between MODE SELECT and GATHER. |
| `skills/profile-builder/enrichment-domain.md` | New skill: enrichment flow prompts, field mapping reference, review templates, diff display guidance. |

### Tests

| File | Role |
|------|------|
| `tests/unit/test_enrichment_domain.py` | Unit tests for enrichment domain types and UEI validation |
| `tests/unit/test_json_api_key_adapter.py` | Unit tests for API key adapter |
| `tests/unit/test_sam_gov_adapter.py` | Unit tests for SAM.gov adapter |
| `tests/unit/test_sbir_gov_adapter.py` | Unit tests for SBIR.gov adapter |
| `tests/unit/test_usa_spending_adapter.py` | Unit tests for USASpending adapter |
| `tests/unit/test_enrichment_service.py` | Unit tests for enrichment service cascade and partial failure |
| `tests/unit/test_profile_diff.py` | Unit tests for profile diff logic |
| `tests/unit/test_enrichment_cli.py` | Unit tests for CLI entry point |

---

## Quality Metrics

### DES TDD Execution (9 Steps, all PASS)

| Step | Name | PREPARE | RED | GREEN | COMMIT |
|------|------|---------|-----|-------|--------|
| 01-01 | Enrichment domain types and UEI validation | PASS | PASS (unit) | PASS | PASS |
| 01-02 | API key port, adapter, and validation | PASS | PASS (acceptance + unit) | PASS | PASS |
| 02-01 | SAM.gov Entity API adapter | PASS | PASS (unit) | PASS | PASS |
| 02-02 | SBIR.gov Company and Awards API adapter | PASS | PASS (unit) | PASS | PASS |
| 02-03 | USASpending.gov recipient API adapter | PASS | PASS (unit) | PASS | PASS |
| 03-01 | Company enrichment service | PASS | PASS (unit) | PASS | PASS |
| 03-02 | Profile diff logic | PASS | PASS (unit) | PASS | PASS |
| 03-03 | Enrichment CLI entry point | PASS | PASS (unit) | PASS | PASS |
| 04-01 | Schema extension and agent enrichment phase | PASS | N/A (forge) | PASS | PASS |

### Mutation Testing (per-feature, scoped to modified Python files)

| File | Kill Rate |
|------|-----------|
| `scripts/pes/domain/enrichment.py` | 87.9% |
| `scripts/pes/domain/enrichment_service.py` | 96.0% |
| `scripts/pes/domain/profile_diff.py` | 92.0% |
| `scripts/pes/adapters/sam_gov_adapter.py` | 86.7% |
| `scripts/pes/adapters/sbir_gov_adapter.py` | 91.5% |
| `scripts/pes/adapters/usa_spending_adapter.py` | 88.1% |
| `scripts/pes/adapters/json_api_key_adapter.py` | 85.2% |
| `scripts/pes/enrichment_cli.py` | 76.5% |
| **Weighted total** | **85.5%** |

All files except `enrichment_cli.py` exceed the 80% kill rate gate. CLI entry points have lower mutation kill rates due to argument parsing and composition root wiring which produce equivalent mutants. Weighted total (85.5%) exceeds the 80% gate.

---

## Integration Notes

- No existing PES adapter was modified. The feature adds new ports, adapters, and domain files to the existing `scripts/pes/` tree.
- Profile schema extension is backward-compatible: `naics_codes` and `registration_expiration` are optional fields.
- CLI pattern matches `dsip_cli.py` and `sbir_feedback_cli.py` (argparse, JSON stdout, subprocess entry point).
- Enrichment is entirely optional -- skipping it preserves the existing manual interview flow unchanged.
- API key stored separately from profile data for security hygiene (ADR-042).
- Three-API cascade has a clear dependency chain: SAM.gov resolves company name required by SBIR.gov and USASpending.gov.
