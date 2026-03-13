# DESIGN Wave Handoff: Company Profile Builder

## Feature Summary

The Company Profile Builder automates creation and maintenance of `~/.sbir/company-profile.json`, which powers the fit scoring engine in the existing SBIR proposal plugin. Currently users must hand-craft this JSON file. This feature adds a conversational agent that interviews the user, extracts data from existing documents, validates the result, and writes the profile.

## Handoff Package

### Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| JTBD Analysis | `docs/feature/company-profile-builder/discuss/jtbd-analysis.md` | 3 job stories, forces analysis, opportunity scoring (8 outcomes), persona |
| Journey Visual | `docs/feature/company-profile-builder/discuss/journey-profile-builder-visual.md` | ASCII flow diagram, TUI mockups per step, emotional annotations, error paths |
| Journey Schema | `docs/feature/company-profile-builder/discuss/journey-profile-builder.yaml` | Machine-readable journey: 5 steps, 5 error paths, integration validation |
| Gherkin Scenarios | `docs/feature/company-profile-builder/discuss/journey-profile-builder.feature` | 23 scenarios covering setup, extraction, interview, preview, save, update |
| User Stories | `docs/feature/company-profile-builder/discuss/user-stories.md` | 5 stories (US-CPB-001 through US-CPB-005), all DoR PASSED |
| Shared Artifacts | `docs/feature/company-profile-builder/discuss/shared-artifacts-registry.md` | 7 tracked artifacts, 5 integration checkpoints |
| Peer Review | `docs/feature/company-profile-builder/discuss/peer-review.yaml` | 2 iterations, approved with 0 critical/high issues |

### User Stories Summary

| Story | Title | Effort | Scenarios | MoSCoW |
|-------|-------|--------|-----------|--------|
| US-CPB-001 | Guided Company Profile Interview | ~2 days | 5 | Must Have |
| US-CPB-002 | Profile Preview and Validation Gate | ~1 day | 3 | Must Have |
| US-CPB-003 | Profile Creation from Documents | ~3 days | 6 | Should Have |
| US-CPB-004 | Selective Profile Section Update | ~2 days | 4 | Should Have |
| US-CPB-005 | Existing Profile Overwrite Protection | ~1 day | 4 | Must Have |

**Total estimated effort**: ~9 days
**Total scenarios**: 22

### Story Dependencies

```
US-CPB-005 (Overwrite Protection) ----+
                                      |
US-CPB-001 (Guided Interview) --------+--> US-CPB-002 (Preview & Validate) --> US-CPB-004 (Update)
                                      |
US-CPB-003 (Document Extraction) -----+
```

- US-CPB-001 + US-CPB-003 produce the profile draft
- US-CPB-002 validates and gates the save (required by both)
- US-CPB-004 depends on an existing profile (created by 001+002)
- US-CPB-005 is an entry guard (runs before 001 or 003)

### Recommended Build Order

1. US-CPB-001 (Guided Interview) -- core flow, establishes the agent and command
2. US-CPB-002 (Preview and Validation) -- quality gate for all writes
3. US-CPB-005 (Overwrite Protection) -- safety net before any save
4. US-CPB-003 (Document Extraction) -- enhancement to the input path
5. US-CPB-004 (Selective Update) -- maintenance flow for existing profiles

## Integration Points

### Cross-Agent: sbir-topic-scout

The company profile is consumed by `sbir-topic-scout` in Phase 3 SCORE. The schema must match exactly:

```json
{
  "company_name": "string",
  "capabilities": ["string"],
  "certifications": {
    "sam_gov": { "active": true, "cage_code": "string", "uei": "string" },
    "socioeconomic": ["string"],
    "security_clearance": "none | confidential | secret | top_secret",
    "itar_registered": false
  },
  "employee_count": 15,
  "key_personnel": [
    { "name": "string", "role": "string", "expertise": ["string"] }
  ],
  "past_performance": [
    { "agency": "string", "topic_area": "string", "outcome": "string" }
  ],
  "research_institution_partners": ["string"]
}
```

Source: `skills/topic-scout/fit-scoring-methodology.md`

### Cross-Agent: sbir-topic-scout Warning Message

The topic scout currently warns: "Company profile not found. Scoring with available data only." After this feature ships, the warning should suggest: "Run `/sbir:proposal profile setup` to create your company profile."

### File System

- Profile location: `~/.sbir/company-profile.json`
- Backup location: `~/.sbir/company-profile.json.bak`
- Temp write location: `~/.sbir/company-profile.json.tmp`
- Atomic write pattern: write .tmp -> backup existing to .bak -> rename .tmp to target

### Plugin Architecture

This feature requires:
- New agent: `agents/sbir-profile-builder.md`
- New commands: `/sbir:proposal profile setup`, `/sbir:proposal profile update`
- No new PES enforcement (profile creation is not a wave-gated operation)
- No new skills needed (the agent uses existing Read/Bash tools for document extraction)

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PDF extraction accuracy varies by document formatting | High | Medium | Extract-then-confirm pattern; user reviews all extracted data |
| SAM.gov page structure may change, breaking URL extraction | Medium | Medium | Graceful fallback to interview when URL parsing fails |
| File permission issues on Windows vs Unix | Medium | Low | Document platform-specific guidance in error messages |
| Profile schema evolution (new fields added later) | Low | Medium | Design for forward compatibility; unknown fields preserved during update |

## Quality Notes

- All 5 stories passed DoR (8/8 items each)
- Peer review approved after 2 iterations (0 critical, 0 high issues remaining)
- 22 Gherkin scenarios provide comprehensive coverage including happy paths, edge cases, error paths, and the update flow
- Emotional arc validated: frustrated/blocked -> productive/guided -> confident/relieved
- Shared artifact registry documents 7 artifacts across 5 integration checkpoints
