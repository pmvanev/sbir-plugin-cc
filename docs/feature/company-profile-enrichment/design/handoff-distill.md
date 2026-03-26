# Handoff to DISTILL Wave: Company Profile Enrichment

## Design Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Architecture Design | `docs/feature/company-profile-enrichment/design/architecture-design.md` | C4 diagrams (L1+L2), component architecture, integration patterns, roadmap (9 steps), quality gates |
| Component Boundaries | `docs/feature/company-profile-enrichment/design/component-boundaries.md` | Port/adapter/service structure, dependency direction, domain value objects, agent integration points |
| Technology Stack | `docs/feature/company-profile-enrichment/design/technology-stack.md` | httpx reuse, API auth details, rate limits, CLI JSON formats |
| Data Models | `docs/feature/company-profile-enrichment/design/data-models.md` | Domain types, SAM.gov/SBIR.gov/USASpending field mappings, schema extensions |
| ADR-041 | `docs/adrs/adr-041-naics-codes-profile-field.md` | NAICS codes as top-level optional profile field |
| ADR-042 | `docs/adrs/adr-042-api-key-storage.md` | API keys in separate ~/.sbir/api-keys.json file |
| ADR-043 | `docs/adrs/adr-043-enrichment-optional-phase.md` | Enrichment as optional phase in profile builder flow |

## DISCUSS Artifacts (Upstream)

| Artifact | Path |
|----------|------|
| JTBD Analysis | `docs/feature/company-profile-enrichment/discuss/jtbd-analysis.md` |
| User Stories (4, all DoR PASSED) | `docs/feature/company-profile-enrichment/discuss/user-stories.md` |
| Journey YAML | `docs/feature/company-profile-enrichment/discuss/journey-enrichment.yaml` |
| Journey Visual | `docs/feature/company-profile-enrichment/discuss/journey-enrichment-visual.md` |
| Gherkin Scenarios (26) | `docs/feature/company-profile-enrichment/discuss/journey-enrichment.feature` |
| Shared Artifacts Registry | `docs/feature/company-profile-enrichment/discuss/shared-artifacts-registry.md` |
| API Research (18 sources) | `docs/research/company-profile-enrichment-apis.md` |

## Architecture Summary

- **Style**: Ports-and-adapters (existing PES pattern, no new architecture)
- **New port**: `EnrichmentSourcePort` -- abstract interface for fetching company data from external APIs
- **New port**: `ApiKeyPort` -- abstract interface for API key persistence
- **3 adapters**: SamGovAdapter, SbirGovAdapter, UsaSpendingAdapter (each implements EnrichmentSourcePort)
- **1 adapter**: JsonApiKeyAdapter (implements ApiKeyPort)
- **Domain**: enrichment.py (value objects, UEI validation), profile_diff.py (diff logic for re-enrichment)
- **Service**: enrichment_service.py (cascade orchestration, partial failure handling)
- **CLI**: enrichment_cli.py (composition root, 4 modes: enrich, diff, validate-key, save-key)
- **Agent**: sbir-profile-builder.md updated with ENRICHMENT phase
- **Schema**: company-profile-schema.json extended with naics_codes, registration_expiration

## Delivery Surfaces

| Surface | Scope | Validation |
|---------|-------|------------|
| Python TDD | 10 production files (ports, adapters, domain, service, CLI) | pytest + mutation testing >= 80% kill rate |
| Markdown Forge | 2 files (agent update, enrichment skill) | nw:forge checklist |

## Roadmap Overview

| Phase | Steps | Focus |
|-------|-------|-------|
| 01 Foundation | 2 | Domain types + API key management |
| 02 API Adapters | 3 | SAM.gov, SBIR.gov, USASpending adapters |
| 03 Service + CLI | 3 | Enrichment service, diff logic, CLI entry point |
| 04 Agent Integration | 1 | Schema extension, agent ENRICHMENT phase, skill |
| **Total** | **9 steps** | **~12 production files** |

## Story Delivery Order

US-CPE-004 (API key setup) -> US-CPE-001 (three-API enrichment) -> US-CPE-002 (review and confirm) -> US-CPE-003 (re-enrichment on update)

## Key Design Decisions

1. **SAM.gov is primary** -- provides company name needed by SBIR.gov and USASpending. If SAM.gov fails, downstream APIs cannot proceed.
2. **Partial enrichment accepted** -- each API failure is independent (except SAM.gov dependency). Available data is always usable.
3. **Agent owns confirmation** -- Python CLI returns structured data; agent drives the conversational review. No enriched data enters the profile without user action.
4. **API key via stdin** -- save-key mode reads from stdin, never CLI arguments. Other modes read from file.
5. **Schema backward-compatible** -- naics_codes is optional. Existing profiles remain valid.
6. **Enrichment is optional** -- skip option at every decision point. Manual interview flow is unchanged fallback.

## Knowledge Gaps for DELIVER to Resolve

1. **SAM.gov exact JSON paths** -- the field mapping table in data-models.md is based on documentation analysis. Run a test API call to confirm exact paths during adapter implementation.
2. **SBIR.gov UEI search** -- documentation shows keyword/firm name search only. Test whether `?uei=` parameter works. If not, fall back to name search with UEI filtering in response.
3. **USASpending recipient_id format** -- the autocomplete endpoint returns a recipient hash/ID. Confirm the format and whether it is stable across calls.

## For Acceptance-Designer

The 26 Gherkin scenarios in `journey-enrichment.feature` cover all happy paths, error paths, and edge cases across all 4 user stories. The roadmap's 9 steps map to these scenarios via the traceability table in the architecture design document. The acceptance-designer should derive acceptance tests from these scenarios, focusing on:

- Python domain/service tests (pure logic, mockable ports)
- Adapter integration tests (real HTTP calls to test endpoints or recorded responses)
- Agent behavioral validation (enrichment offered/skipped correctly, confirmation flow)
