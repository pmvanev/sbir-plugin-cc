# ADR-040: Feedback Snapshot Privacy Boundary — Metadata Only

## Status
Accepted

## Context

The feedback context snapshot reads from company-profile.json, proposal-state.json, and finder-results.json. These files contain sensitive business information: company capability descriptions, past performance narratives, key personnel details, and draft proposal content.

Two positions were considered for the privacy boundary:

**Option A**: Include all available state in the snapshot (full fidelity, maximum debug value).

**Option B**: Include metadata only — names, ages, counts, scores, IDs. Exclude prose content (capabilities text, past performance descriptions, draft sections).

## Decision

**Option B**: Metadata only in the snapshot.

## Rationale

1. **Shareability**: The developer may ask a colleague to share the feedback file to diagnose an issue. If the file contains full company profile text or draft proposal content, the user must review it for sensitive information before sharing. Metadata-only snapshots can be shared without review.

2. **Sufficiency**: The developer needs to know *what was happening* (wave, topic, rigor, profile freshness, scoring recency), not *what the content was*. The snapshot answers "why did the plugin behave this way?" — not "what did it produce?"

3. **Principle of minimum necessary data**: Capturing more data than needed for the diagnostic purpose violates data minimization. The free text field is available for the user to voluntarily include specific content quotes.

4. **Defense in depth**: Even if `.sbir/feedback/` is accidentally committed to git or shared, it contains no company IP or proposal strategy.

## Fields Excluded from Snapshot

From `~/.sbir/company-profile.json`:
- `capabilities` (list of capability descriptions)
- `past_performance` (array of past project descriptions)
- `key_personnel` (names + expertise details)
- `certifications` (detailed certification status)

From `.sbir/proposals/{id}/proposal-state.json`:
- `current_draft` (any draft section content)
- `corpus_matches` (matched past proposal content)
- `discrimination_table` entries

From `.sbir/finder-results.json`:
- Full topic descriptions, objectives, Q&A entries
- Solicitation and component instructions

## Fields Included (Metadata)

- `company_name` (string identifier only)
- `company_profile_age_days` (integer)
- `proposal_id`, `topic_id`, `topic_title`, `topic_agency`, `topic_deadline`, `topic_phase`
- `current_wave`, `completed_waves`, `skipped_waves`
- `rigor_profile` (profile name only)
- `finder_results_age_days`
- `top_scored_topics` (topic_id, composite_score, recommendation — no descriptions)
- `generated_artifacts` (filename list — no file contents)
- `plugin_version` (git SHA)

## Consequences

- `FeedbackSnapshotService.build_snapshot()` explicitly extracts only the allowed fields
- Privacy boundary is enforced in Python (testable) not just in documentation
- Developers who need more content context can request a specific artifact file from the user separately
