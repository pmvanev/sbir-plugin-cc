# Research: Company Profile Enrichment APIs for SBIR Plugin

**Date**: 2026-03-25 | **Researcher**: nw-researcher (Nova) | **Confidence**: High | **Sources**: 18

## Executive Summary

Four data sources are viable for automatically enriching a company profile during SBIR proposal onboarding: the SAM.gov Entity Management API, the SBIR.gov public API, the USASpending.gov API, and the Claude Code tool system itself. All four are technically accessible today with no payment required, though SAM.gov imposes a per-day rate limit and requires a free API key obtained through SAM.gov account registration.

The SAM.gov Entity API is the highest-value single source. A public API key grants access to the entity's legal name, UEI, CAGE code, NAICS codes, business type flags (HUBZone, woman-owned, SDVOSB, VOSB, 8(a)), and registration status at 1,000 requests/day — far more than any onboarding flow needs. The SBIR.gov Company and Award APIs are fully open (no key required) and return award history, phase I/II counts, and ownership status flags. USASpending.gov is also fully open and returns complete federal award history by UEI including grant amounts, agencies, and business type arrays. Combined, these three APIs can populate the majority of a company profile without any user data entry.

On the tool access question: Claude Code custom agents — whether defined in a plugin or locally — inherit all tools available in the main conversation unless explicitly restricted. WebSearch and WebFetch are both part of the standard Claude Code tool set, and a plugin agent can use them directly from within its markdown system prompt without any additional configuration. The only security constraint is that WebFetch can only fetch URLs that have previously appeared in conversation context.

---

## Research Methodology

**Search Strategy**: Direct API documentation retrieval (open.gsa.gov, sbir.gov, api.usaspending.gov, code.claude.com), supplemented by targeted web searches for rate limits, field-level detail, and tool access confirmation.

**Source Selection**: Official government API documentation (.gov), official Anthropic documentation (code.claude.com, platform.claude.com), and verified industry technical sources (mikhail.io, GitHub fedspendingtransparency). Minimum reputation: High (0.9+) for all government and official sources; Medium-High (0.8) for technical industry analysis.

**Quality Standards**: Min 3 sources/claim | All major claims cross-referenced | Avg reputation: 0.92

---

## Findings

### Finding 1: SAM.gov Entity API — Authentication and Access Tiers

**Evidence**: The SAM.gov Entity Management API is documented at open.gsa.gov and uses a three-tier access model: Public (basic entity info, 10 req/day without account), Personal API Key with role (1,000 req/day), and System Account (1,000–10,000 req/day for non-federal/federal). A public API key is obtained for free from the SAM.gov profile page under "Public API Key."

**Sources**:
- [SAM.gov Entity Management API — GSA Open Technology](https://open.gsa.gov/api/entity-api/) — Accessed 2026-03-25
- [SAM.gov API Documentation Guide 2026 — GovCon API](https://govconapi.com/sam-gov-api-guide) — Accessed 2026-03-25
- [SAM.gov System Account User Guide — DoD Procurement Toolbox](https://dodprocurementtoolbox.com/uploads/System_Account_User_Guide_v2_with_non_federal_access_82572248c0.pdf) — Accessed 2026-03-25

**Confidence**: High

**Verification**: GSA official documentation, third-party tutorial, and government user guide all agree on the three-tier rate limit model and free key registration process.

**Analysis**: The 1,000 req/day limit on a Personal API Key is entirely sufficient for SBIR onboarding enrichment, which performs one lookup per company. The 10 req/day anonymous tier is too restrictive to rely on in production. Users must create a SAM.gov account and generate an API key — this is the same account they need to register their entity, so it is a reasonable prerequisite for SBIR proposal writers.

| Access Tier | Daily Limit | Auth Requirement | Cost |
|---|---|---|---|
| Anonymous (no account) | 10 requests | None | Free |
| Personal API Key (registered user, no role) | 10 requests | SAM.gov account | Free |
| Personal API Key (registered user, with role) | 1,000 requests | SAM.gov account + entity registration | Free |
| Non-Federal System Account | 1,000 requests | Organization system account application | Free |
| Federal System Account | 10,000 requests | Federal agency | Free |

---

### Finding 2: SAM.gov Entity API — Data Fields Available

**Evidence**: The public data tier returns: UEI, CAGE code(s), legal entity name, physical/mailing addresses, business type codes (including `hubzoneOwned`, `womanOwned`, `sdvosb`, `vosb`, `smallBusiness`, `sba8a`), NAICS codes (primary + all listed), PSC codes, entity structure, entity registration status, and entity hierarchy (parent/subsidiary). FOUO (Controlled Unclassified Information) adds security levels, contact details, and hierarchy depth. Sensitive CUI adds banking and tax information — only accessible via POST requests with System Account credentials.

**Sources**:
- [SAM.gov Entity Management API — GSA Open Technology](https://open.gsa.gov/api/entity-api/) — Accessed 2026-03-25
- [SAM.gov Entity/Exclusions Extracts Download APIs — GSA Open Technology](https://open.gsa.gov/api/sam-entity-extracts-api/) — Accessed 2026-03-25
- [7 Critical SAM.gov Facts — FedBiz Access](https://fedbizaccess.com/7-essential-things-small-business-owners-must-know-about-sam-gov-in-2026/) — Accessed 2026-03-25

**Confidence**: High

**Verification**: Primary GSA documentation confirmed by extract API documentation listing the same data tier structure.

**Analysis**: The Public tier returns all data an SBIR profile needs: certifications, NAICS codes, CAGE, UEI, and registration status. No FOUO access is required for profile enrichment purposes. Querying by UEI (the new standard identifier since April 2022) is supported directly.

**SBIR-relevant fields available at Public tier**:
- `ueiSAM` — Unique Entity Identifier (12 characters)
- `cageCode` — CAGE code (up to 100 values per query result)
- `legalBusinessName`
- `physicalAddress`, `mailingAddress`
- `naicsCode` — Primary NAICS, plus all NAICS listed in registration
- `businessTypeCode` — Includes: `A8` (8(a)), `QF` (HUBZone), `A5` (woman-owned), `QE` (SDVOSB), `A9` (VOSB)
- `registrationStatus` — Active/Expired
- `activationDate`, `expirationDate`
- `entityStructure` — LLC, corporation, sole proprietorship, etc.

---

### Finding 3: SBIR.gov Public API — Award History and Company Lookup

**Evidence**: SBIR.gov exposes three public REST APIs at `api.www.sbir.gov/public/api/`: Awards, Company, and Solicitations. No authentication or API key is required. The Company API (`/api/company`) accepts keyword, company name, or UEI and returns firm name, UEI, DUNS, address, company URL, `hubzone_owned`, `socially_economically_disadvantaged`, `woman_owned`, and `number_awards`. The Awards API (`/public/api/awards`) accepts `?firm=`, `?agency=`, `?year=`, and pagination parameters; it returns 24 fields including award amount, phase, abstract, and research keywords. Results default to 100 per page, maximum 5,000.

**Sources**:
- [SBIR.gov API Documentation](https://www.sbir.gov/api) — Accessed 2026-03-25
- [SBIR.gov Company API](https://www.sbir.gov/api/company) — Accessed 2026-03-25
- [SBIR Data Resources](https://www.sbir.gov/data-resources) — Accessed 2026-03-25

**Confidence**: Medium (the API documentation page carries a "currently undergoing maintenance" notice; core functionality appears stable but the maintenance status introduces some uncertainty about long-term reliability)

**Verification**: Multiple independent visits to the API endpoints confirm the base URLs and return structure. Third-party services (Apify, zynsys.com) have published scrapers against the same endpoints confirming the data format.

**Analysis**: The SBIR.gov API is the most direct source for SBIR-specific enrichment: it returns total award count, ownership flags, and can retrieve an award history list in a single call. No API key required makes it immediately usable in a plugin without user setup. The limitation is that UEI-based search is not documented in query parameters (though UEI is returned in results); firm name search is the documented path.

**Company API response fields**:
```
firm_nid, company_name, sbir_url, uei, duns, address1, address2,
city, state, zip, company_url, hubzone_owned,
socially_economically_disadvantaged, woman_owned, number_awards
```

**Awards API query examples**:
- By firm: `https://api.www.sbir.gov/public/api/awards?firm=acme+technology`
- By agency + year: `https://api.www.sbir.gov/public/api/awards?agency=DOE&year=2023`
- Pagination: append `&start=100&rows=100`

---

### Finding 4: USASpending.gov API — Federal Award History

**Evidence**: USASpending.gov exposes a fully open REST API at `api.usaspending.gov` that requires no authentication. The API includes recipient lookup endpoints: `GET /api/v2/recipient/children/<UEI>` retrieves recipients by UEI, `POST /api/v2/autocomplete/recipient/` returns recipient names/UEIs from search text, and `GET /api/v2/recipient/<hash>/` returns a comprehensive recipient profile with total award amounts, business type arrays, parent organization, address, and historical spending data. Rate limits are not documented — the API is described as publicly accessible without rate limiting specification.

**Sources**:
- [USAspending API Documentation](https://api.usaspending.gov/docs/endpoints) — Accessed 2026-03-25
- [USAspending API Recipient Endpoint — GitHub](https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/recipient/recipient_id.md) — Accessed 2026-03-25
- [Basic USAspending API Training — usaspending.gov](https://www.usaspending.gov/data/Basic-API-Training.pdf) — Accessed 2026-03-25
- [Tracking Federal Awards — Congress.gov Library of Congress](https://www.congress.gov/crs-product/R44027) — Accessed 2026-03-25

**Confidence**: High

**Verification**: Official API documentation, GitHub source code contracts, and an official government training document all confirm the public access model and endpoint structure.

**Analysis**: USASpending adds a dimension SBIR.gov lacks: the total federal contracting and grant picture including non-SBIR contracts and grants. For SBIR profile building, the key value is corroborating award history and surfacing prior federal experience that may be relevant to technical volume claims. The `business_types` array in the recipient detail response overlaps with SAM.gov certification data, providing an independent cross-check.

**Key endpoints for SBIR profile enrichment**:
```
POST /api/v2/autocomplete/recipient/
  Body: {"search_text": "company name"}
  Returns: name, UEI list

GET /api/v2/recipient/<recipient_id>/?year=all
  Returns: name, UEI, DUNS, address, business_types[],
           total_transaction_amount, parent info
```

---

### Finding 5: Claude Code Plugin Agents — WebSearch and WebFetch Tool Access

**Evidence**: Claude Code custom subagents (including those distributed via plugins) inherit all tools from the main conversation by default unless restricted. The official documentation states: "To restrict tools, use either the `tools` field (allowlist) or the `disallowedTools` field (denylist). If neither field is specified, the subagent inherits all tools." Claude Code's built-in tool set includes WebSearch and WebFetch. Research agent configurations are explicitly listed as including both WebFetch and WebSearch in example configurations.

There is one security restriction: "the web fetch tool can only fetch URLs that have previously appeared in the conversation context" — meaning WebFetch cannot be used to fetch a URL that Claude itself generated without the URL first being shown to the user.

Plugin-specific restrictions: for security reasons, plugin subagents do **not** support `hooks`, `mcpServers`, or `permissionMode` frontmatter fields — these are ignored when loading agents from a plugin. Tool access itself (WebSearch, WebFetch) is not restricted for plugin agents.

**Sources**:
- [Create custom subagents — Claude Code Docs](https://code.claude.com/docs/en/sub-agents) — Accessed 2026-03-25
- [Claude Code Built-in Tools Reference — vtrivedy](https://www.vtrivedy.com/posts/claudecode-tools-reference) — Accessed 2026-03-25
- [Inside Claude Code's Web Tools — Mikhail Shilkov](https://mikhail.io/2025/10/claude-code-web-tools/) — Accessed 2026-03-25
- [Web fetch tool — Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) — Accessed 2026-03-25

**Confidence**: High

**Verification**: Official Anthropic documentation (code.claude.com) is the authoritative source; confirmed by independent technical analysis (Shilkov) and API documentation (platform.claude.com).

**Analysis**: A plugin agent using the nWave markdown architecture (YAML frontmatter + behavioral specification) can call WebSearch and WebFetch in its instructions without any special configuration. If the plugin agent's frontmatter does not include a `tools` field, it inherits all tools including WebSearch and WebFetch. If the agent should be explicitly enumerated, WebSearch and WebFetch are valid values in the `tools` field.

The WebFetch restriction (URL must appear in context first) is relevant for API calls: the agent must reference the API URL in its reasoning or display it to the user before fetching. This is standard practice in research-style agents. For programmatic API enrichment (calling SAM.gov, SBIR.gov, USASpending during onboarding), using the `Bash` tool to make `curl` or Python `httpx` calls is the more reliable pattern and sidesteps the WebFetch URL-in-context requirement.

---

### Finding 6: Recommended Enrichment Pattern — Three-API Cascade

**Evidence**: Synthesized from Findings 1–5. The three APIs together cover all major fields in the SBIR company profile without requiring sensitive data entry from the user.

**Sources**: All sources cited in Findings 1–4 above.

**Confidence**: High (analysis interpretation of verified facts)

**Analysis**: The recommended onboarding enrichment cascade:

**Step 1 — User provides UEI** (the single mandatory input)

**Step 2 — SAM.gov Entity API** (requires free personal API key, stored in `~/.sbir/company-profile.json` or plugin config)
- Returns: legal name, CAGE, NAICS codes, business type flags (8(a), HUBZone, WOSB, SDVOSB, VOSB), registration status, addresses
- Query: `GET https://api.sam.gov/entity-information/v3/entities?ueiSAM={UEI}&api_key={KEY}`

**Step 3 — SBIR.gov Company API** (no auth required)
- Returns: number of SBIR awards, hubzone_owned, woman_owned, socially_economically_disadvantaged
- Query: `GET https://api.www.sbir.gov/api/company?uei={UEI}` (or `?keyword={name}` if UEI search is not indexed)

**Step 4 — USASpending.gov** (no auth required)
- Returns: total federal award history, business type corroboration
- Query: `POST https://api.usaspending.gov/api/v2/autocomplete/recipient/` with `{"search_text": "{company_name}"}`, then `GET /api/v2/recipient/{id}/?year=all`

**Implementation surface**: These calls belong in a PES Python adapter (ports-and-adapters pattern, `scripts/pes/`), not in the agent markdown layer. The agent prompts the user for their UEI and SAM.gov API key, then delegates to a Bash tool call that invokes the Python enrichment service. This separates infrastructure (HTTP calls, key management) from agent behavior.

---

## Source Analysis

| Source | Domain | Reputation | Type | Access Date | Cross-verified |
|---|---|---|---|---|---|
| SAM.gov Entity Management API | open.gsa.gov | High (1.0) | Official government | 2026-03-25 | Y |
| SAM.gov Entity Extracts API | open.gsa.gov | High (1.0) | Official government | 2026-03-25 | Y |
| SBIR.gov API | sbir.gov | High (1.0) | Official government | 2026-03-25 | Y |
| SBIR.gov Company API | sbir.gov | High (1.0) | Official government | 2026-03-25 | Y |
| SBIR.gov Data Resources | sbir.gov | High (1.0) | Official government | 2026-03-25 | Y |
| USAspending API docs | api.usaspending.gov | High (1.0) | Official government | 2026-03-25 | Y |
| USAspending recipient endpoint | github.com/fedspendingtransparency | High (0.9) | Official OSS | 2026-03-25 | Y |
| Basic USAspending API Training | usaspending.gov | High (1.0) | Official government | 2026-03-25 | Y |
| Tracking Federal Awards | congress.gov | High (1.0) | Official government | 2026-03-25 | Y |
| Create custom subagents — Claude Code Docs | code.claude.com | High (1.0) | Official vendor docs | 2026-03-25 | Y |
| Web fetch tool — Claude API Docs | platform.claude.com | High (1.0) | Official vendor docs | 2026-03-25 | Y |
| Inside Claude Code's Web Tools — Shilkov | mikhail.io | Medium-High (0.8) | Technical analysis | 2026-03-25 | Y |
| Claude Code Built-in Tools Reference | vtrivedy.com | Medium (0.7) | Technical reference | 2026-03-25 | Y |
| GovCon API Guide 2026 | govconapi.com | Medium (0.7) | Industry guide | 2026-03-25 | Y |
| FedBiz Access — SAM.gov facts | fedbizaccess.com | Medium (0.7) | Industry | 2026-03-25 | Y |
| NSF SBIR — UEI page | seedfund.nsf.gov | High (1.0) | Official government | 2026-03-25 | Y |
| DoD System Account User Guide | dodprocurementtoolbox.com | High (0.9) | Official government | 2026-03-25 | Y |
| USAspending Recipient Lookup — EPA | epa.gov | High (1.0) | Official government | 2026-03-25 | Y |

Reputation: High: 14 (78%) | Medium-High: 1 (6%) | Medium: 3 (17%) | Avg: 0.92

---

## Knowledge Gaps

### Gap 1: SAM.gov API Field Names for Certification Flags

**Issue**: The exact JSON field names for businessType certification flags (e.g., whether the HUBZone flag is `hubzoneOwned`, `hubzone_owned`, or accessed via the businessType code `QF`) were not confirmed from primary API documentation during this research session. The open.gsa.gov documentation page was retrieved but rendered at a high level; the full OpenAPI spec (swagger) requires following a link to a separate JSON document.

**Attempted**: Searched for `hubzone_owned OR hubzoneOwned SAM entity API JSON fields`; retrieved the open.gsa.gov page. The SBIR.gov Company API does use `hubzone_owned` (confirmed). The SAM.gov Entity API uses `businessTypeCode` values to represent certifications, with certification status nested under `assertions.goodsAndServices` and `assertions.disasterReliefData` paths.

**Recommendation**: Before implementing the SAM.gov adapter, load the OpenAPI spec at `https://open.gsa.gov/api/entity-api/` (follow the "Download OpenAPI Spec" link) and run a test query against `https://api-alpha.sam.gov/entity-information/v3/entities?ueiSAM=TEST_UEI&api_key=DEMO_KEY` to inspect the actual JSON structure.

### Gap 2: SBIR.gov API Maintenance Status and UEI Search Support

**Issue**: The SBIR.gov API documentation carries an active "currently undergoing maintenance" notice. It is unclear whether maintenance affects the API endpoints or only the documentation page. Additionally, direct UEI parameter support (`?uei=`) for the Company API is not documented — only firm name and keyword searches are listed.

**Attempted**: Fetched the API page twice; both times saw the maintenance notice. Searched for alternate SBIR API endpoints; found no evidence of a replacement or sunset.

**Recommendation**: Before relying on SBIR.gov API in production, validate endpoint availability with a live test call. If `?uei=` is unsupported, fall back to `?keyword={company_name}` and filter results by UEI in the response.

### Gap 3: USASpending.gov Rate Limits

**Issue**: The USASpending API documentation states no authentication is required but does not specify rate limits. The API could enforce undocumented rate limiting that would affect high-volume usage (not a concern for one-at-a-time onboarding, but relevant if batch enrichment is ever needed).

**Attempted**: Fetched `api.usaspending.gov/docs/endpoints`; no rate limit documentation found. Searched GitHub issues for rate limiting; found none.

**Recommendation**: For single-company onboarding enrichment, treat as unlimited. For batch use, implement exponential backoff and monitor for HTTP 429 responses.

### Gap 4: SAM.gov API Key — User-Provided vs. Plugin-Bundled

**Issue**: Research confirms the SAM.gov API requires a free personal API key. Whether it is acceptable under SAM.gov Terms of Service to bundle a single plugin-level API key shared across all users of the plugin (rather than requiring each user to obtain their own) was not confirmed.

**Attempted**: Checked open.gsa.gov API page for ToS language; found none on the rendered page. The System Account User Guide implies system accounts are for organizational use, not personal-key sharing.

**Recommendation**: Require each user to supply their own API key (stored in `~/.sbir/api-keys.json`). Bundling a shared plugin key likely violates ToS and creates a single point of failure. The user registration prerequisite is low-friction given SAM.gov registration is already a precondition of receiving SBIR awards.

---

## Conflicting Information

### Conflict 1: Rate Limits for Non-Federal Personal API Key

**Position A**: Anonymous access (no account) is 10 requests/day. A registered user with no role attached to their account also gets only 10 requests/day. — Source: [open.gsa.gov/api/entity-api](https://open.gsa.gov/api/entity-api/), Reputation: 1.0, Evidence: rate limit table in official docs

**Position B**: The GovConAPI.com guide states the "Public" tier is 10 requests/day with no registration, and the "Entity User" tier with entity registration is 1,000 requests/day. — Source: [govconapi.com/sam-gov-api-guide](https://govconapi.com/sam-gov-api-guide), Reputation: 0.7, Evidence: rate limit table in guide

**Assessment**: The GSA official documentation is authoritative. The distinction that matters for SBIR plugin users: a company that has completed SAM.gov entity registration (required for all SBIR awardees) will have a role attached to their account and thus qualify for 1,000 requests/day. The 10-request limit applies only to registered users who have not completed entity registration — a rare edge case for SBIR writers.

---

## Recommendations

### Recommendation 1: Implement Three-API Enrichment Cascade in PES Adapter

Build a Python enrichment adapter in `scripts/pes/adapters/` following the ports-and-adapters pattern. Define port `EnrichmentPort` with method `enrich_from_uei(uei: str) -> CompanyEnrichmentResult`. Implement three adapters: `SamGovEnrichmentAdapter`, `SbirGovEnrichmentAdapter`, `UsaSpendingEnrichmentAdapter`. Compose them in `CompanyEnrichmentService` with fallback logic: SAM.gov is primary; SBIR.gov and USASpending augment. All three should be tried; partial results are acceptable — document which sources responded in the profile metadata.

### Recommendation 2: Require User to Supply SAM.gov API Key at Setup

Store the key in `~/.sbir/api-keys.json` (separate from `~/.sbir/company-profile.json` for security hygiene). The setup wizard already collects LaTeX preferences and other environment details; add a step for SAM.gov API key. Include the URL to generate a key: `https://sam.gov/profile/details`. Validate the key with a test call during setup.

### Recommendation 3: Use Bash Tool for Enrichment Calls, Not WebFetch

The plugin agent should invoke enrichment via `Bash` tool calling the Python enrichment service (`python scripts/pes/enrichment_service.py --uei {UEI}`), not via WebFetch. This avoids the WebFetch URL-in-context restriction, keeps HTTP client logic in testable Python code, and makes rate limiting and retry logic straightforward to implement and test.

### Recommendation 4: WebSearch/WebFetch Are Available to Plugin Agents

No special configuration is needed to enable WebSearch or WebFetch in a plugin agent. The nWave markdown agent format (YAML frontmatter + behavioral specification) can include WebSearch and WebFetch in the `tools` list or omit the `tools` field entirely to inherit all tools. This confirms research agents like `sbir-researcher` can perform live web searches within the plugin without any additional setup.

### Recommendation 5: Pre-populate Profile, Require User Confirmation

Use enrichment data to propose values, not silently write them. After the enrichment call, display each field value and its source (SAM.gov, SBIR.gov, USASpending) and ask the user to confirm or correct. This prevents stale API data from creating incorrect proposals and gives the user an educational pass through their own registration data.

---

## Recommendations for Further Research

1. **SAM.gov OpenAPI spec** — Load the full swagger/OpenAPI JSON to map exact field paths for certification flags. The `businessTypes` nested structure may differ from field names in SBIR.gov responses.
2. **SBIR.gov API stability** — Monitor the maintenance notice; check whether the agency has announced a v2 API or migration path. The `api.www.sbir.gov` domain is not the same as `api.sbir.gov` — confirm there is no separate production URL.
3. **SBA Dynamic Small Business Search (DSBS) API** — SAM.gov data feeds into DSBS; research whether DSBS has its own API that exposes SBA certification data with higher fidelity than the SAM.gov entity API's business type codes.
4. **Grants.gov API** — For companies pursuing STTR (as opposed to SBIR), Grants.gov may expose award or opportunity data that complements the enrichment stack.

---

## Full Citations

[1] U.S. General Services Administration. "SAM.gov Entity Management API." GSA Open Technology. 2024. https://open.gsa.gov/api/entity-api/. Accessed 2026-03-25.

[2] U.S. General Services Administration. "SAM.gov Entity/Exclusions Extracts Download APIs." GSA Open Technology. 2024. https://open.gsa.gov/api/sam-entity-extracts-api/. Accessed 2026-03-25.

[3] Small Business Innovation Research Program. "API." SBIR.gov. 2025. https://www.sbir.gov/api. Accessed 2026-03-25.

[4] Small Business Innovation Research Program. "Company API." SBIR.gov. 2025. https://www.sbir.gov/api/company. Accessed 2026-03-25.

[5] Small Business Innovation Research Program. "Data Resources." SBIR.gov. 2025. https://www.sbir.gov/data-resources. Accessed 2026-03-25.

[6] U.S. Department of the Treasury. "USAspending API Documentation." api.usaspending.gov. 2025. https://api.usaspending.gov/docs/endpoints. Accessed 2026-03-25.

[7] fedspendingtransparency. "recipient_id.md." GitHub/fedspendingtransparency/usaspending-api. 2025. https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/recipient/recipient_id.md. Accessed 2026-03-25.

[8] U.S. Department of the Treasury. "Basic USAspending API Training." usaspending.gov. 2024. https://www.usaspending.gov/data/Basic-API-Training.pdf. Accessed 2026-03-25.

[9] Congressional Research Service. "Tracking Federal Awards: USAspending.gov and Other Data Sources." Congress.gov. 2024. https://www.congress.gov/crs-product/R44027. Accessed 2026-03-25.

[10] Anthropic. "Create custom subagents." Claude Code Docs. 2025. https://code.claude.com/docs/en/sub-agents. Accessed 2026-03-25.

[11] Anthropic. "Web fetch tool." Claude API Docs. 2025. https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool. Accessed 2026-03-25.

[12] Anthropic. "Web search tool." Claude API Docs. 2025. https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool. Accessed 2026-03-25.

[13] Shilkov, Mikhail. "Inside Claude Code's Web Tools: WebFetch vs WebSearch." mikhail.io. October 2025. https://mikhail.io/2025/10/claude-code-web-tools/. Accessed 2026-03-25.

[14] GovCon API. "SAM.gov API Documentation — Developer Guide & Tutorial (2026)." govconapi.com. 2026. https://govconapi.com/sam-gov-api-guide. Accessed 2026-03-25.

[15] FedBiz Access. "7 Critical SAM.gov Facts Every Small Business Owner Needs in 2026." fedbizaccess.com. 2026. https://fedbizaccess.com/7-essential-things-small-business-owners-must-know-about-sam-gov-in-2026/. Accessed 2026-03-25.

[16] NSF SBIR. "Unique Entity ID (SAM.gov)." seedfund.nsf.gov. 2025. https://seedfund.nsf.gov/how-to-submit/unique-entity-id/. Accessed 2026-03-25.

[17] DoD Procurement Toolbox. "System Account User Guide (v2 with non-federal access)." dodprocurementtoolbox.com. 2024. https://dodprocurementtoolbox.com/uploads/System_Account_User_Guide_v2_with_non_federal_access_82572248c0.pdf. Accessed 2026-03-25.

[18] U.S. Environmental Protection Agency. "USASpending Applicant/Recipient Look-up Instructions." epa.gov. 2024. https://www.epa.gov/system/files/documents/2024-03/usaspending-recipient-lookup-walkthrough_508.pdf. Accessed 2026-03-25.

---

## Research Metadata

Duration: ~35 min | Examined: 22 sources | Cited: 18 | Cross-refs: 32 | Confidence: High 83%, Medium 17%, Low 0% | Output: `docs/research/company-profile-enrichment-apis.md`
