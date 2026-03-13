# DESIGN Wave Handoff: Solicitation Finder

## Handoff Summary

The solicitation finder enables automated discovery and scoring of SBIR/STTR topics against a company profile. Five user stories have passed the Definition of Ready gate and peer review. This document provides the solution architect with everything needed to begin the DESIGN wave.

---

## Stories Ready for DESIGN

| Story ID | Title | Effort Est. | Priority | Dependencies |
|----------|-------|-------------|----------|--------------|
| US-SF-001 | Fetch Open Topics from DSIP API | ~2 days | Must Have | ProfilePort (existing) |
| US-SF-002 | Score and Rank Topics Against Company Profile | ~3 days | Must Have | US-SF-001, fit-scoring-methodology |
| US-SF-003 | Review Results and Drill Into Topic Details | ~2 days | Must Have | US-SF-002 |
| US-SF-004 | Select Topic and Transition to Proposal Creation | ~1 day | Must Have | US-SF-003, /sbir:proposal new (existing) |
| US-SF-005 | Handle No Company Profile Gracefully | ~1 day | Must Have | ProfilePort (existing) |

**Total estimated effort**: 9 days (approximately 2 weeks with testing)

---

## Architecture Context

### Existing Infrastructure to Reuse

| Component | Location | Purpose |
|-----------|----------|---------|
| `TopicInfo` dataclass | `scripts/pes/domain/solicitation.py` | Topic metadata schema (topic_id, agency, phase, deadline, title) |
| `ProfilePort` | `scripts/pes/ports/profile_port.py` | Abstract interface for company profile read/write/exists |
| `JsonProfileAdapter` | `scripts/pes/adapters/json_profile_adapter.py` | JSON file adapter for company profile at `~/.sbir/company-profile.json` |
| Fit scoring model | `skills/topic-scout/fit-scoring-methodology.md` | Five-dimension weights, thresholds, recommendation rules |
| `sbir-topic-scout` agent | `agents/sbir-topic-scout.md` | Single-topic scoring agent (to be extended for batch) |

### New Components Needed

| Component | Layer | Purpose |
|-----------|-------|---------|
| DSIP API client | Adapter | Fetch topic listings from DSIP public API |
| BAA PDF parser | Adapter | Extract topics from BAA PDF (fallback) |
| Keyword pre-filter | Domain | Fast topic elimination by capability keyword matching |
| Batch scoring pipeline | Domain/Application | Orchestrate two-pass matching (pre-filter + LLM scoring) |
| Finder results persistence | Adapter | Write/read `.sbir/finder-results.json` |
| `/sbir:solicitation find` command | Command | CLI entry point with flags |
| Topic selection flow | Application | `details` and `pursue` interactive commands |

### Architecture Constraints

- **Ports-and-adapters**: Domain logic in `scripts/pes/domain/`, ports in `scripts/pes/ports/`, adapters in `scripts/pes/adapters/`
- **Agent extension**: Extend `sbir-topic-scout`, not a new agent (per ADR-005)
- **State location**: Finder results at `.sbir/finder-results.json` (project-local)
- **Company profile**: Read-only from `~/.sbir/company-profile.json` (global)
- **Atomic writes**: `.tmp` -> `.bak` -> rename pattern for finder results

---

## Key Design Decisions (from Discovery)

These decisions were validated during the DISCOVER wave and should be respected in DESIGN:

1. **Direct API access as primary data source**. The DSIP public API at `https://www.dodsbirsttr.mil/topics/api/public/topics/search` is unauthenticated and returns JSON. BAA PDF is the fallback, not the primary path.

2. **Two-pass matching**. Keyword pre-filter (fast, Python) reduces 300-500 topics to 20-50 candidates. LLM semantic scoring (Claude) produces five-dimension scores on the candidate set. This manages token budget.

3. **Five-dimension fit scoring reuse**. Same weights (SME 0.35, PP 0.25, Cert 0.15, Elig 0.15, STTR 0.10) and thresholds (GO >= 0.6, EVALUATE 0.3-0.6, NO-GO < 0.3 or hard disqualifier) as existing topic scout.

4. **Finder results schema** defined in discovery (see solution-testing.md). Includes finder_run_id, run_date, source, topics_parsed, topics_scored, per-topic dimension scores, recommendations, and profile_hash.

5. **TopicInfo handoff** to `/sbir:proposal new`. Selected topic maps to existing `TopicInfo(topic_id, agency, phase, deadline, title)` dataclass.

---

## DSIP API Details (confirmed 2026-03-13)

### Listing Endpoint

```
GET https://www.dodsbirsttr.mil/topics/api/public/topics/search
```

- **Authentication**: None (public)
- **Response**: JSON with `total` (int) and `data` (array of topic objects)
- **Topic fields**: topicId, topicCode, topicTitle, topicStatus, program (SBIR/STTR), component (ARMY/NAVY/USAF/DARPA/etc.), solicitationNumber, cycleName, topicStartDate, topicEndDate, cmmcLevel, phaseHierarchy
- **Query parameters**: `topicStatus`, `numPerPage`, `baa` (e.g., `DOD_SBIR_2025_P1_C5`)
- **Pagination**: numPerPage controls page size; investigate offset/page parameters during build
- **Note**: Listing returns metadata only (no descriptions/keywords). Full topic content via PDF download.

### Topic PDF Endpoint

```
GET https://www.dodsbirsttr.mil/topics/api/public/topics/{hash_id}/download/PDF
```

- Individual topic details as PDF
- Contains full description, keywords, objectives, TPOC information

### Rate Limiting

- Not formally documented; batch with 1-2 second delays between requests
- Graceful degradation: offer partial results if rate-limited mid-fetch

---

## Shared Artifacts and Integration Points

### Cross-Feature Data Flows

```
~/.sbir/company-profile.json  ──read──>  solicitation-finder
                                              |
DSIP API (or BAA PDF)  ────fetch──>          |
                                              v
                                    .sbir/finder-results.json
                                              |
                                    ┌─────────┴─────────┐
                                    v                     v
                              detail view            pursue -> /sbir:proposal new
                                                         (TopicInfo handoff)
```

### Integration Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| DSIP API changes or becomes restricted | Medium | BAA PDF fallback; API schema versioning |
| finder-results.json schema mismatch with consumers | High | JSON schema validation on write; version field in schema |
| TopicInfo field mismatch between finder and proposal | High | Both use same `TopicInfo` dataclass from `solicitation.py` |
| Company profile schema changes | Low | ProfilePort abstraction isolates changes |

---

## Non-Functional Requirements

| NFR | Threshold | Source |
|-----|-----------|--------|
| End-to-end completion | < 10 minutes for 50 candidate topics | Discovery H3, US-SF-002 AC |
| First output | < 100ms (CLI responsiveness) | TUI patterns |
| Progress indication | Update every 5 seconds during scoring | TUI patterns |
| API fetch timeout | 30 seconds per request, 3 retries | Resilience |
| Results persistence | Atomic write to .sbir/finder-results.json | Existing pattern |

---

## Risk Assessment

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| DSIP API becomes authenticated | Low | High | BAA PDF fallback is fully functional; monitor API access |
| Scoring accuracy insufficient for trust | Medium | High | Show dimension breakdown transparently; let user verify |

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Token budget exceeds limits for large candidate sets | Low | Medium | Batch in groups of 10-20; two-pass filtering keeps candidates manageable |
| BAA PDF format variation across agencies | Medium | Medium | Claude reads PDFs -- LLM handles format variation |
| DSIP API pagination parameters undocumented | Medium | Low | Explore during build; worst case, iterate with numPerPage |

### Project Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Scope creep into multi-source (NASA, DoE) | Medium | Medium | Explicitly deferred to v2 in discovery |

---

## Artifacts Produced

| Artifact | Path |
|----------|------|
| JTBD Analysis | `docs/feature/solicitation-finder/discuss/jtbd-analysis.md` |
| Journey Visual | `docs/feature/solicitation-finder/discuss/journey-solicitation-finder-visual.md` |
| Journey Schema | `docs/feature/solicitation-finder/discuss/journey-solicitation-finder.yaml` |
| Journey Gherkin | `docs/feature/solicitation-finder/discuss/journey-solicitation-finder.feature` |
| Shared Artifacts Registry | `docs/feature/solicitation-finder/discuss/shared-artifacts-registry.md` |
| User Stories | `docs/feature/solicitation-finder/discuss/user-stories.md` |
| Peer Review | `docs/feature/solicitation-finder/discuss/peer-review.md` |
| This Handoff | `docs/feature/solicitation-finder/discuss/handoff-design.md` |

---

## Recommended DESIGN Sequence

1. **Architecture**: Define ports for DSIP API client and BAA PDF parser. Define finder results schema as domain object.
2. **Domain**: Keyword pre-filter logic. Batch scoring orchestration. Finder results domain model.
3. **Adapters**: DSIP API adapter. BAA PDF parser adapter. Finder results JSON adapter.
4. **Agent extension**: Extend sbir-topic-scout with batch scoring capability and finder results formatting.
5. **Command**: `/sbir:solicitation find` command with flags and interactive results flow.
6. **Integration**: TopicInfo handoff to `/sbir:proposal new`. End-to-end testing.
