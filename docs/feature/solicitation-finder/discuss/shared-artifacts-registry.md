# Shared Artifacts Registry: Solicitation Finder

## Artifact Inventory

### company_name

- **Source of truth**: `~/.sbir/company-profile.json` -> `company_name`
- **Consumers**: Step 1 header, Step 3 results header, `.sbir/finder-results.json`
- **Owner**: company-profile-builder feature (existing)
- **Integration risk**: LOW -- single read at start, immutable during run
- **Validation**: Value in results header must match company profile file

### company_profile

- **Source of truth**: `~/.sbir/company-profile.json`
- **Consumers**: Step 1 (validation/display), Step 2 (keyword pre-filter), Step 2 (LLM scoring), Step 3 (disqualifier reasons), Step 4 (key personnel match)
- **Owner**: company-profile-builder feature (existing)
- **Integration risk**: MEDIUM -- profile changes between runs produce different results (expected)
- **Validation**: Profile schema matches expected fields (capabilities, certifications, key_personnel, past_performance, employee_count, research_institution_partners)

### topic_count

- **Source of truth**: DSIP API response `total` field (or BAA parse count)
- **Consumers**: Step 1 progress, Step 2 pre-filter progress, Step 3 results header
- **Owner**: solicitation-finder data retrieval
- **Integration risk**: LOW -- immutable after fetch
- **Validation**: Count in Step 1 progress must equal count in Step 3 header ("347 topics parsed")

### candidate_count

- **Source of truth**: Keyword pre-filter output count
- **Consumers**: Step 2 progress, Step 3 results header ("42 candidates scored")
- **Owner**: solicitation-finder pre-filter
- **Integration risk**: LOW -- immutable after pre-filter
- **Validation**: candidate_count + eliminated_count = topic_count

### finder_results

- **Source of truth**: `.sbir/finder-results.json`
- **Consumers**: Step 3 (display), Step 4 (detail view), Step 5 (topic selection), `/sbir:proposal new` (TopicInfo handoff)
- **Owner**: solicitation-finder feature
- **Integration risk**: HIGH -- single source for all downstream steps; corruption or schema mismatch breaks the entire flow
- **Validation**: JSON schema validation on write. File must contain: finder_run_id, run_date, source, topics_parsed, topics_scored, results array, company_profile_used, profile_hash.

### selected_topic (TopicInfo)

- **Source of truth**: `.sbir/finder-results.json` -> `results[selected_topic_id]`
- **Consumers**: Step 5 (confirmation display), `/sbir:proposal new` (pre-loaded topic data)
- **Owner**: solicitation-finder feature (produces), proposal feature (consumes)
- **Integration risk**: HIGH -- data must map exactly to existing `TopicInfo(topic_id, agency, phase, deadline, title)` dataclass
- **Validation**: Selected topic fields must map 1:1 to `TopicInfo` fields in `scripts/pes/domain/solicitation.py`

### profile_hash

- **Source of truth**: SHA-256 of `~/.sbir/company-profile.json` at scoring time
- **Consumers**: `.sbir/finder-results.json` (stored for audit), re-run comparison
- **Owner**: solicitation-finder feature
- **Integration risk**: LOW -- informational only
- **Validation**: Hash matches file content at scoring time

---

## Integration Checkpoints

### Checkpoint 1: Profile Availability (Step 1)

- **Check**: Company profile exists and is readable
- **Failure mode**: No profile -> error with guidance to create one
- **Failure mode**: Profile exists but missing required fields -> warning with degraded accuracy
- **Test**: Gherkin scenarios "No company profile exists" and "Company profile has incomplete data"

### Checkpoint 2: Data Source Reliability (Step 1-2)

- **Check**: DSIP API responds with topic data OR user provides BAA PDF
- **Failure mode**: API timeout -> prompt for BAA PDF fallback
- **Failure mode**: API rate limited -> offer partial results or retry
- **Failure mode**: BAA PDF unparseable -> error with specific extraction failure
- **Test**: Gherkin scenarios "DSIP API unavailable", "API rate limiting", "Fall back to BAA PDF"

### Checkpoint 3: Results Persistence (Step 3)

- **Check**: Results written to `.sbir/finder-results.json` with valid schema
- **Failure mode**: Write failure -> error, results displayed but not persisted
- **Failure mode**: Schema violation -> validation error before write
- **Test**: Gherkin scenario "Results persisted to finder-results.json"

### Checkpoint 4: TopicInfo Handoff (Step 5)

- **Check**: Selected topic maps to `TopicInfo(topic_id, agency, phase, deadline, title)`
- **Failure mode**: Missing field -> error before transition
- **Failure mode**: Stale results (topic expired since scoring) -> warning before transition
- **Test**: Gherkin scenario "Confirm topic selection starts proposal workflow"

---

## Cross-Feature Dependencies

| Artifact | Producing Feature | Consuming Feature | Schema Contract |
|----------|------------------|-------------------|-----------------|
| `~/.sbir/company-profile.json` | company-profile-builder | solicitation-finder | Company profile schema (fit-scoring-methodology.md) |
| `.sbir/finder-results.json` | solicitation-finder | solicitation-finder (detail/select), proposal (new) | Finder results schema (solution-testing.md) |
| `TopicInfo` dataclass | solicitation-finder (via finder-results) | proposal feature (`/sbir:proposal new`) | `TopicInfo(topic_id, agency, phase, deadline, title)` in `solicitation.py` |
| Fit scoring model | fit-scoring-methodology skill | solicitation-finder (batch scoring) | Five-dimension weights and thresholds |
