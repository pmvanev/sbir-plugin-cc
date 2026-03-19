# Shared Artifacts Registry: Partnership Management

## Artifacts

### partner_profile

- **Source of truth**: `~/.sbir/partners/{partner_slug}.json`
- **Owner**: sbir-partner-builder agent (new)
- **Consumers**:
  - sbir-topic-scout: partnership-aware scoring (SME, PP, STTR dimensions)
  - sbir-solution-shaper: approach generation with partner capabilities
  - sbir-strategist: teaming section in strategy brief
  - sbir-writer: partnership content in proposal sections
  - sbir-partner-builder: partner list display, update flow
- **Integration risk**: HIGH -- all downstream agents depend on this schema. Schema changes break 5 consumers.
- **Validation**: Schema validation before write. All consumers must handle missing partner profile gracefully (fallback to non-partnered behavior).

### partner_slug

- **Source of truth**: Derived from partner name (slugify: lowercase, hyphens, no spaces)
- **Owner**: sbir-partner-builder agent
- **Consumers**:
  - File naming: `~/.sbir/partners/{partner_slug}.json`
  - Partner list display (Step 1 of setup journey)
  - Screening results: `.sbir/partner-screenings/{partner_slug}.json`
- **Integration risk**: MEDIUM -- slug must be deterministic and collision-free.
- **Validation**: Slug generation must produce same result given same input name.

### company_profile

- **Source of truth**: `~/.sbir/company-profile.json` (existing)
- **Owner**: sbir-profile-builder agent (existing)
- **Consumers** (new):
  - Partner setup preview: combined capability analysis
  - Partnership scoring: solo column computation
  - Approach generation: company capabilities for work-split
- **Integration risk**: LOW -- existing artifact, well-established schema. New consumers read-only.
- **Validation**: Existing validation via profile_validation module.

### combined_capability_analysis

- **Source of truth**: Computed at runtime from company_profile + partner_profile
- **Owner**: Computed by each consuming agent independently
- **Consumers**:
  - Partner setup preview (Step 4): overlap, unique-to-company, unique-to-partner
  - Topic scoring: combined SME score
  - Approach generation: combined capability set for matching
- **Integration risk**: MEDIUM -- each agent computes independently, results must be consistent.
- **Validation**: Same input profiles must produce same capability overlap analysis. Consider extracting shared computation.

### work_split_percentages

- **Source of truth**: `artifacts/wave-0-go-nogo/approach-brief.md` (the selected approach)
- **Owner**: sbir-solution-shaper agent
- **Consumers**:
  - sbir-strategist: teaming section references work split
  - sbir-writer: proposal sections reference work split
  - STTR compliance: 30% minimum for research institution
- **Integration risk**: HIGH -- inconsistent percentages across agents undermines proposal credibility.
- **Validation**: Percentages in strategy brief must match approach brief. Draft must match strategy brief.

### partner_personnel

- **Source of truth**: `~/.sbir/partners/{partner_slug}.json` (key_personnel array)
- **Owner**: sbir-partner-builder agent
- **Consumers**:
  - sbir-strategist: names Co-PI in teaming section
  - sbir-writer: names Co-PI and personnel in proposal narrative
  - sbir-reviewer: verifies personnel consistency
- **Integration risk**: HIGH -- name mismatches between strategy and draft look unprofessional.
- **Validation**: Personnel names in generated content must exactly match partner profile.

### screening_results

- **Source of truth**: `.sbir/partner-screenings/{partner_slug}.json`
- **Owner**: sbir-partner-screener (new command, not a full agent)
- **Consumers**:
  - sbir-partner-builder: carry forward research findings when proceeding from screening
  - User: reference during follow-up conversations with partner
- **Integration risk**: LOW -- screening results are advisory, not consumed by other agents.
- **Validation**: JSON schema with readiness signals, fit assessment, recommendation.

## Integration Checkpoints

### Checkpoint 1: Partner Profile Readable by All Consumers

All agents that consume partner profiles must:
1. Discover partners via `~/.sbir/partners/*.json` glob
2. Handle zero partners (non-partnered proposal -- existing behavior)
3. Handle multiple partners (future: multi-partner proposals)
4. Fail gracefully if partner file is corrupted or missing

### Checkpoint 2: Scoring Consistency

Topic scoring with partnerships must:
1. Show solo AND partnership scores (never hide solo score)
2. Compute partnership SME from union of company + partner capabilities
3. Compute partnership STTR from partner type validation
4. Display delta column for quick comparison

### Checkpoint 3: Content Traceability

All generated partnership content must:
1. Reference partner profile as data source (citation)
2. Use personnel names exactly as stored in partner profile
3. Use facility names exactly as stored in partner profile
4. Use capability keywords from partner profile (not synonyms or paraphrases)

### Checkpoint 4: STTR Compliance

For STTR proposals:
1. Partner must be a qualifying institution type (university, federally_funded_rdc, nonprofit_research)
2. Work split must allocate >= 30% to the research institution
3. Topic scoring must validate STTR eligibility at scoring time
4. Strategy brief must explicitly state STTR work split percentage

## CLI Vocabulary

| Term | Usage | Context |
|------|-------|---------|
| partner | Research institution partner for STTR/teaming | Not "subcontractor" or "collaborator" |
| partner profile | Structured data about a partner | Mirrors "company profile" |
| partner-setup | Build/update a partner profile | Mirrors "profile-setup" |
| partner-screen | Lightweight readiness assessment | Distinct from setup (screening is advisory, setup creates the profile) |
| partnership scoring | Combined company+partner fit scoring | "Partnership-aware scoring" in display |
| work split | Division of effort between entities | Not "scope of work" (SOW is the document) |
| complementarity | How capabilities combine | Not "synergy" (too vague) |
