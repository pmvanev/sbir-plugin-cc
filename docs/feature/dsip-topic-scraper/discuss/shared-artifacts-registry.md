# Shared Artifacts Registry: DSIP Topic Scraper

## Artifacts

### company_profile

- **Source of truth**: `~/.sbir/company-profile.json`
- **Consumers**:
  - Step 1: validation that profile exists
  - Step 2: capability keywords for pre-filtering
  - Step 4: fit scoring (subject matter, certifications, eligibility, past performance)
- **Owner**: Company Profile Builder feature (existing)
- **Integration risk**: MEDIUM -- profile format is stable but capability keywords drive pre-filtering accuracy
- **Validation**: Profile schema matches expected structure; capabilities array is non-empty

### dsip_api_endpoint

- **Source of truth**: Scraper configuration (hardcoded or config file)
- **Consumers**:
  - Step 2: API request URL construction
- **Owner**: DSIP Scraper port implementation
- **Integration risk**: HIGH -- DSIP can change their API URL without notice
- **Validation**: HTTP GET returns expected JSON structure with `total` and `data` keys

### dsip_raw_topics

- **Source of truth**: DSIP API response (`data[]` array from search endpoint)
- **Consumers**:
  - Step 3: enrichment input (topic IDs to fetch details for)
  - `.sbir/dsip_topics.json`: cached raw data
- **Owner**: DSIP Scraper port
- **Integration risk**: HIGH -- API response schema can change; field names may differ from expected
- **Validation**: Each topic has `topicId`, `title`, `statusId`; total count matches `total` field

### enriched_topics

- **Source of truth**: Combined API metadata + detail page content
- **Consumers**:
  - Step 4: scoring pipeline input
  - `.sbir/dsip_topics.json`: cached enriched data
- **Owner**: DSIP Scraper port (enrichment phase)
- **Integration risk**: MEDIUM -- detail page DOM structure can change, breaking extraction
- **Validation**: Each enriched topic has description (string, non-empty); instruction and Q&A presence tracked

### enrichment_completeness

- **Source of truth**: Computed during enrichment (counts of successful extractions)
- **Consumers**:
  - User display: completeness summary line
  - Scoring: confidence weighting (topics without descriptions score lower)
- **Owner**: DSIP Scraper port
- **Integration risk**: LOW -- derived metric
- **Validation**: desc_count + instr_count + qa_count are non-negative integers; desc_count <= total_count

### scored_topics

- **Source of truth**: `TopicScoringService.score_batch()` output
- **Consumers**:
  - User display: ranked table
  - `.sbir/finder-results.json`: persisted results
  - `pursue <topic-id>`: topic selection for `/proposal new`
- **Owner**: Existing fit-scoring pipeline
- **Integration risk**: LOW -- existing interface, well-tested
- **Validation**: Each scored topic has composite score (0.0-1.0), per-dimension scores, recommendation

### finder_results

- **Source of truth**: `.sbir/finder-results.json`
- **Consumers**:
  - `pursue <topic-id>` command
  - `/proposal new` with pre-loaded TopicInfo
  - `/proposal status` (shows last finder results date)
- **Owner**: Topic Scout agent
- **Integration risk**: LOW -- existing file format
- **Validation**: JSON schema valid; each entry has topic_id, score, recommendation

### dsip_topics_cache

- **Source of truth**: `.sbir/dsip_topics.json`
- **Consumers**:
  - Subsequent `/solicitation find` runs (skip re-scrape if cache is fresh)
  - Manual inspection by user
  - Topic Scout agent (offline access)
- **Owner**: DSIP Scraper port
- **Integration risk**: MEDIUM -- cache staleness
- **Validation**: Contains `scrape_date`, `source`, `total_topics`, `topics[]` fields

## Integration Risk Summary

| Risk Level | Artifacts | Mitigation |
|------------|-----------|------------|
| HIGH | dsip_api_endpoint, dsip_raw_topics | API response validation; fallback to --file; clear error messages |
| MEDIUM | company_profile, enriched_topics, dsip_topics_cache | Schema validation; graceful degradation; cache TTL |
| LOW | enrichment_completeness, scored_topics, finder_results | Derived or existing stable interfaces |
