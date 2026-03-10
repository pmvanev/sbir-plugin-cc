# C3 Data Models -- State Schema Extension and Domain Objects

---

## Proposal State Schema v2.0.0

Extends the existing v1.0.0 schema. All existing fields remain unchanged. New top-level sections added for Waves 5-9.

### Migration Strategy

Schema version bumps from `1.0.0` to `2.0.0`. Existing proposals created under v1.0.0 are forward-compatible: missing C3 fields default to `null` or empty objects. No migration script needed -- domain services check for field existence before access.

### New State Fields

```json
{
    "schema_version": "2.0.0",

    "visuals": {
        "status": "not_started | in_progress | completed",
        "figure_count": 0,
        "generated_count": 0,
        "external_count": 0,
        "cross_refs_valid": null,
        "completed_at": null
    },

    "formatting": {
        "status": "not_started | in_progress | completed",
        "output_medium": null,
        "page_count": null,
        "page_limit": null,
        "jargon_issues": 0,
        "completed_at": null
    },

    "assembly": {
        "status": "not_started | in_progress | completed",
        "volume_count": 0,
        "volumes": [],
        "compliance_check_status": null,
        "completed_at": null
    },

    "final_review": {
        "status": "not_started | in_progress | signed_off",
        "review_round": 0,
        "sign_off_at": null,
        "signed_off_by": null,
        "high_findings_count": 0,
        "completed_at": null
    },

    "submission": {
        "status": "not_started | prepared | submitted",
        "portal": null,
        "confirmation_number": null,
        "submitted_at": null,
        "archive_path": null,
        "immutable": false
    },

    "learning": {
        "outcome": null,
        "outcome_recorded_at": null,
        "debrief_requested": null,
        "debrief_ingested": false,
        "critique_count": 0,
        "known_weaknesses_flagged": 0,
        "pattern_analysis_updated": false
    },

    "waves": {
        "5": { "status": "not_started", "completed_at": null },
        "6": { "status": "not_started", "completed_at": null },
        "7": { "status": "not_started", "completed_at": null },
        "8": { "status": "not_started", "completed_at": null },
        "9": { "status": "not_started", "completed_at": null }
    }
}
```

---

## New Domain Objects (Value Objects)

All domain objects are frozen dataclasses (immutable value objects), consistent with existing C1/C2 pattern (see `SectionDraft`, `EnforcementRule`).

### Wave 5 -- Visual Assets

**FigurePlaceholder**: Extracted from outline. Represents a location where a figure is expected.
- Fields: `figure_id`, `section_id`, `caption`, `figure_type`, `generation_method`
- `figure_type`: `block_diagram | flow_chart | gantt | data_chart | concept_illustration | photograph | table`
- `generation_method`: `mermaid | graphviz | svg | gemini_api | external`

**FigureInventory**: Collection of all placeholders for a proposal.
- Fields: `proposal_id`, `figures: list[FigurePlaceholder]`, `created_at`

**GeneratedFigure**: A figure that has been generated or provided.
- Fields: `figure_id`, `file_path`, `generation_method`, `status`, `review_status`
- `status`: `generated | manual_replacement | external_brief`
- `review_status`: `pending | approved | revision_requested`

**CrossReferenceEntry**: A single text-to-figure reference.
- Fields: `section_id`, `reference_text`, `figure_id`, `valid`

**CrossReferenceLog**: Full log of all references.
- Fields: `entries: list[CrossReferenceEntry]`, `orphaned_refs: list[str]`, `unreferenced_figures: list[str]`

### Wave 6 -- Formatting & Assembly

**FormatTemplate**: Agency-specific formatting rules loaded from templates.
- Fields: `agency`, `font_family`, `font_size_pt`, `margin_inches`, `page_limit`, `header_format`, `footer_format`, `section_numbering_style`

**JargonAuditEntry**: An undefined acronym found in text.
- Fields: `acronym`, `location_section`, `location_page`, `defined_on_first_use`

**JargonAudit**: Full audit result.
- Fields: `entries: list[JargonAuditEntry]`, `total_acronyms`, `undefined_count`

**PageCountReport**: Page count vs. limit.
- Fields: `current_pages`, `max_pages`, `within_limit`, `largest_sections: list[tuple[str, int]]`

**AssembledVolume**: A single assembled volume.
- Fields: `volume_id`, `title`, `file_path`, `page_count`, `file_size_bytes`

### Wave 7 -- Final Review

**ReviewScore**: A single evaluation criterion score.
- Fields: `criterion`, `score`, `max_score`, `rationale`

**ReviewerScorecard**: Full reviewer simulation output.
- Fields: `scores: list[ReviewScore]`, `overall_score`, `evaluation_criteria_source`

**RedTeamFinding**: A single adversarial objection.
- Fields: `finding_id`, `severity`, `section_id`, `page`, `description`, `recommendation`
- `severity`: `HIGH | MEDIUM | LOW`

**DebriefCrossCheckEntry**: Match between current proposal and past debrief critique.
- Fields: `past_proposal_id`, `critique_text`, `current_section_id`, `addressed`

**SignOffRecord**: Human sign-off for submission gate.
- Fields: `signed_off_by`, `signed_off_at`, `unresolved_findings: list[str]`, `review_rounds_completed`

### Wave 8 -- Submission

**PortalRule**: Portal-specific packaging requirement.
- Fields: `portal_name`, `naming_convention`, `max_file_size_mb`, `required_formats`, `required_attachments: list[str]`

**PackageFile**: A file in the submission package.
- Fields: `filename`, `original_path`, `file_size_bytes`, `format`, `status`
- `status`: `ok | missing | naming_error | size_exceeded`

**PreSubmissionChecklist**: Verification result.
- Fields: `files: list[PackageFile]`, `all_present`, `all_named_correctly`, `all_within_size`, `can_submit`

**ConfirmationRecord**: Submission confirmation.
- Fields: `confirmation_number`, `submitted_at`, `portal_name`, `topic_id`

### Wave 9 -- Learning

**DebriefScore**: A single score from debrief feedback.
- Fields: `criterion`, `score`, `max_score`

**DebriefCritique**: A single critique comment from debrief.
- Fields: `critique_id`, `text`, `section_id`, `page`, `is_known_weakness`, `matching_past_proposals: list[str]`

**StructuredDebrief**: Parsed debrief output.
- Fields: `proposal_id`, `scores: list[DebriefScore]`, `critiques: list[DebriefCritique]`, `freeform_text`, `parsing_confidence`

**CritiqueSectionMap**: Full mapping of critiques to sections.
- Fields: `proposal_id`, `mappings: list[DebriefCritique]`, `strengths: list[DebriefCritique]`, `weaknesses: list[DebriefCritique]`

**PatternEntry**: A recurring pattern across proposals.
- Fields: `pattern_text`, `pattern_type`, `occurrence_count`, `proposals: list[str]`
- `pattern_type`: `recurring_weakness | recurring_strength`

**PatternAnalysis**: Cumulative analysis across corpus.
- Fields: `corpus_proposal_count`, `win_rate`, `patterns: list[PatternEntry]`, `confidence_level`

**OutcomeRecord**: Win/loss outcome for a proposal.
- Fields: `proposal_id`, `outcome`, `recorded_at`, `debrief_requested`, `debrief_received`
- `outcome`: `awarded | not_selected | withdrawn`

**LessonsLearned**: Summary produced for human review.
- Fields: `proposal_id`, `key_findings: list[str]`, `actionable_improvements: list[str]`, `acknowledged_by`, `acknowledged_at`

---

## Template Schemas

### Format Template (templates/format-rules/dod-phase-i.json)

```json
{
    "agency": "DoD",
    "solicitation_type": "Phase I",
    "formatting": {
        "font_family": "Times New Roman",
        "font_size_pt": 12,
        "margin_inches": 1.0,
        "line_spacing": 1.0,
        "header": "{topic_number} | {company_name} | Page {page_number}",
        "footer": "SBIR/STTR Proposal -- {topic_title}",
        "section_numbering": "decimal"
    },
    "page_limits": {
        "technical_volume": 20,
        "cost_volume": null,
        "company_info": null
    },
    "volumes": [
        { "id": "vol1", "title": "Technical Volume", "required": true },
        { "id": "vol2", "title": "Cost Volume", "required": true },
        { "id": "vol3", "title": "Company Information", "required": true }
    ]
}
```

### Portal Rules Template (templates/portal-rules/dsip.json)

```json
{
    "portal_name": "DSIP",
    "portal_url": "https://www.dodsbirsttr.mil/submissions",
    "agencies": ["Air Force", "Army", "Navy", "DARPA", "DHA", "MDA", "DTRA", "CBD", "SOCOM"],
    "naming_convention": "{topic_id}_{company_name}_{volume_label}.pdf",
    "max_file_size_mb": 10,
    "required_formats": ["pdf"],
    "required_attachments": [
        { "name": "Firm Certification", "form_id": "firm-cert", "required": true },
        { "name": "Fraud, Waste, and Abuse Training", "form_id": "fwa-cert", "required": true }
    ]
}
```

### Debrief Request Template (templates/debrief-request/dod-far-15-505.md)

```markdown
[Date]

[Contracting Officer Name/Office]
[Agency Address]

Subject: Request for Post-Award Debrief -- Topic {topic_id}

Dear Sir/Madam,

Pursuant to FAR 15.505(a)(1), [company_name] respectfully requests a debrief
regarding the evaluation of our proposal submitted under Topic {topic_id},
"{topic_title}."

Our submission confirmation number is {confirmation_number}, submitted on
{submission_date}.

We would welcome the opportunity to receive feedback on the evaluation of our
proposal to improve future submissions.

Respectfully,

{signatory_name}
{signatory_title}
{company_name}
```
