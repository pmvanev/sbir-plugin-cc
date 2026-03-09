---
name: solicitation-intelligence
description: Domain knowledge for SBIR/STTR solicitation sources, scraping patterns, document format parsing, and metadata extraction into TopicInfo schema
---

# Solicitation Intelligence

## Source Catalog

| Source | URL | Content Type | Update Cadence |
|--------|-----|-------------|----------------|
| SBIR.gov | sbir.gov/solicitations | Central aggregator for all SBIR/STTR topics | Continuous (agency-dependent) |
| Grants.gov | grants.gov/search-grants | Federal grants including SBIR/STTR | Real-time posting |
| SAM.gov | sam.gov/search | Contract opportunities, some SBIR | Real-time posting |
| NSPIRES | nspires.nasaprs.com | NASA-specific solicitations | Periodic (NASA schedule) |
| DoD SBIR/STTR Portal | dodsbirsttr.mil | DoD-specific topics, BAAs | Annual + rolling |
| Agency portals | Varies by agency | Agency-specific solicitation pages | Agency-dependent |

## Agency-Specific Solicitation Formats

### DoD (Air Force, Army, Navy, DARPA, MDA, SOCOM, etc.)
- Format: Annual BAA (Broad Agency Announcement) with numbered topics
- Topic ID pattern: `{Service}{FY}-{NNN}` (e.g., AF243-001, N241-054)
- Structure: Background, Description, Phase I expectations, Phase II expectations, References
- Evaluation criteria: typically Technical Merit, Qualifications, Price (in that order)
- Pre-release period: topics visible before open window

### NASA (via NSPIRES)
- Format: Annual SBIR/STTR solicitations with subtopics
- Topic ID pattern: `{Subtopic area}.{Number}` (e.g., S17.01-T001)
- Structure: Scope, Expected TRL, References, Required deliverables
- Evaluation criteria: Scientific/Technical Merit, Experience/Capability, Price

### DoE
- Format: Rolling FOAs (Funding Opportunity Announcements)
- Topic ID pattern: DE-FOA-{NNNNNNNN}
- Structure: Full FOA document with multiple areas of interest
- Evaluation criteria vary significantly by program office

### NIH / HHS
- Format: Omnibus solicitation with standing topics + special topics
- Topic ID pattern: varies (PA-XX-XXX for parent, RFA-XX-XXX for special)
- Key difference: emphasis on Specific Aims, Innovation, Approach, Investigator, Environment

## Metadata Extraction Rules

Parse each solicitation into `TopicInfo` (defined in `scripts/pes/domain/solicitation.py`):

```
TopicInfo:
  topic_id: str    -- exact topic number from solicitation
  agency: str      -- sponsoring agency name (standardize to common names)
  phase: str       -- "I", "II", or "Direct-to-Phase-II"
  deadline: str    -- ISO 8601 date (YYYY-MM-DD), convert from any format
  title: str       -- topic title verbatim from solicitation
```

Additional fields to extract (not in TopicInfo but needed for scoring):
- Evaluation criteria with weights (if stated)
- Award amounts (typical and maximum)
- Period of performance
- Special requirements: STTR institution, clearance, ITAR, prior Phase I
- Keywords and technical areas
- Program manager / TPOC contact information

## Agency Name Standardization

| Raw Value | Standardized |
|-----------|-------------|
| USAF, Air Force, AF | Air Force |
| USN, Navy, N | Navy |
| USA, Army, A | Army |
| DARPA | DARPA |
| MDA, Missile Defense Agency | MDA |
| NASA | NASA |
| DoE, DOE, Department of Energy | DoE |
| NIH, National Institutes of Health | NIH |
| DHS, Department of Homeland Security | DHS |
| SOCOM, Special Operations Command | SOCOM |

## Deadline Handling

- Convert all date formats to ISO 8601 (YYYY-MM-DD)
- Common formats encountered: "April 15, 2026" | "04/15/2026" | "15 Apr 2026" | "2026-04-15T23:59:59Z"
- Deadline times: if time specified, note it; default assumption is 23:59 ET on the deadline date
- Classification:
  - Expired: deadline < today
  - Critical: deadline within 3 days
  - Warning: deadline within 7 days
  - Open: deadline > 7 days out
  - Pre-release: open date in future (topic visible but not yet accepting)

## Document Format Parsing

### PDF Solicitations
- Most common format for full BAAs and FOAs
- Claude Code reads PDF content directly -- no separate OCR needed for text-based PDFs
- Scanned/image PDFs: flag as "requires OCR preprocessing" and provide guidance

### HTML / Web Pages
- Agency portal pages: use Bash with curl to fetch content
- Extract relevant sections, ignore navigation and boilerplate
- Follow pagination if topic list spans multiple pages

### Plain Text / Markdown
- Direct reading, simplest format
- Common for downloaded/converted solicitations

## Multi-Topic Solicitation Handling

DoD BAAs and NASA solicitations contain many topics in one document:
1. Identify topic boundaries (topic number headings, page breaks)
2. Extract each topic independently into its own TopicInfo
3. Parse shared metadata (deadline, evaluation criteria) from the BAA header
4. Apply shared metadata to each topic unless topic-level overrides exist
