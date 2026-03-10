# Shared Artifacts Registry -- Phase C3 (Waves 5-9)

## Purpose

Extends the C1/C2 shared artifacts registry with new artifacts introduced in Phase C3. Every `${variable}` in C3 TUI mockups has a documented source. All data values appearing across multiple C3 waves have a single source of truth.

See also: `docs/feature/sbir-proposal-plugin/discuss/shared-artifacts-registry.md` (C1/C2 artifacts -- not modified by C3).

---

## C3 Wave Artifacts

### Wave 5 -- Visual Assets

| Artifact | Source of Truth | Created | Consumers | Integration Risk |
|----------|----------------|---------|-----------|-----------------|
| `${figure_count}` | Computed from `./artifacts/wave-5-visuals/figure-inventory.md` | Wave 5 | Status display, Wave 6 figure insertion count | MEDIUM |
| `${section_count}` | Computed from figure inventory (unique sections) | Wave 5 | Status display | LOW |
| Figure inventory | `./artifacts/wave-5-visuals/figure-inventory.md` | Wave 5 | Wave 5 generation, Wave 6 insertion, Wave 7 cross-ref check | HIGH -- missing figure breaks assembly |
| Cross-reference log | `./artifacts/wave-5-visuals/cross-reference-log.md` | Wave 5 | Wave 6 assembly, Wave 7 final review | MEDIUM |
| Generated figures | `./artifacts/wave-5-visuals/figures/` | Wave 5 | Wave 6 figure insertion, Wave 8 submission package | HIGH -- missing file breaks submission |

### Wave 6 -- Formatting & Assembly

| Artifact | Source of Truth | Created | Consumers | Integration Risk |
|----------|----------------|---------|-----------|-----------------|
| `${output_medium}` | User selection during Wave 6 | Wave 6 | Wave 6 formatting engine, Wave 8 file format verification | MEDIUM |
| `${current_pages}` / `${max_pages}` | Computed from assembled document / solicitation requirements | Wave 6 | Status display, Wave 7 final review | HIGH -- over limit = rejection |
| `${page_count_status}` | Derived from page count vs. limit comparison | Wave 6 | Status display | LOW |
| Compliance final check | `./artifacts/wave-6-format/compliance-final-check.md` | Wave 6 | Wave 7 final review, Wave 8 pre-submission | HIGH -- same matrix from Wave 1 |
| Jargon audit | `./artifacts/wave-6-format/jargon-audit.md` | Wave 6 | Wave 7 review reference | LOW |
| Assembled volumes | `./artifacts/wave-6-format/assembled/` | Wave 6 | Wave 7 review input, Wave 8 submission package | HIGH -- this IS the submission |
| `${vol1_pages}`, `${vol2_pages}`, `${vol3_pages}` | Computed from assembled volumes | Wave 6 | Status display, submission prep | MEDIUM |
| `${reference_count}` | Computed from formatted document | Wave 6 | Status display | LOW |

### Wave 7 -- Final Review

| Artifact | Source of Truth | Created | Consumers | Integration Risk |
|----------|----------------|---------|-----------|-----------------|
| Reviewer scorecard | `./artifacts/wave-7-review/reviewer-scorecard.md` | Wave 7 | Sign-off decision, Wave 9 win/loss comparison | MEDIUM |
| `${score_technical}`, etc. | Extracted from reviewer scorecard | Wave 7 | Status display, sign-off decision | MEDIUM |
| `${score_overall}` | Computed average from individual scores | Wave 7 | Status display | LOW |
| Red team findings | `./artifacts/wave-7-review/red-team-findings.md` | Wave 7 | Issue resolution loop, Wave 9 post-mortem | MEDIUM |
| `${red_team_count}` | Computed from red team findings | Wave 7 | Status display | LOW |
| Debrief cross-check | `./artifacts/wave-7-review/debrief-cross-check.md` | Wave 7 | Issue resolution, lessons learned | MEDIUM |
| Sign-off record | `./artifacts/wave-7-review/sign-off-record.md` | Wave 7 | PES gate (Wave 8 requires sign-off), proposal-state.json | HIGH -- gate dependency |
| `${evaluation_criteria_count}` | Derived from solicitation evaluation criteria | Wave 7 | Status display | LOW |

### Wave 8 -- Submission

| Artifact | Source of Truth | Created | Consumers | Integration Risk |
|----------|----------------|---------|-----------|-----------------|
| `${portal_name}` | Derived from `proposal-state.json#topic.agency` | Wave 8 | File naming rules, submission instructions | HIGH -- wrong portal = rejection |
| `${portal_url}` | Portal lookup from agency | Wave 8 | Status display, submission guidance | MEDIUM |
| `${naming_convention}` | Portal-specific rule set | Wave 8 | File naming verification | HIGH -- wrong naming = rejection |
| Submission package | `./artifacts/wave-8-submission/package/` | Wave 8 | Submission, immutable archive | HIGH |
| `${vol1_filename}`, etc. | Derived from naming convention + topic_id | Wave 8 | Package contents display | HIGH |
| `${vol1_size}`, etc. | Computed from package files | Wave 8 | Size limit verification display | MEDIUM |
| Pre-submission checklist | `./artifacts/wave-8-submission/pre-submission-checklist.md` | Wave 8 | Human confirmation decision | HIGH |
| Confirmation record | `./artifacts/wave-8-submission/confirmation-record.md` | Wave 8 | proposal-state.json update, status display, Wave 9 | HIGH -- proof of submission |
| `${confirmation_number}` | From portal submission response (manually entered) | Wave 8 | Confirmation record, status display | HIGH |
| `${submission_timestamp}` | System time at submission confirmation | Wave 8 | Confirmation record, status display | MEDIUM |
| Immutable archive | `./artifacts/wave-8-submission/archive/` | Wave 8 | Compliance audit, corpus (read-only) | HIGH -- immutability enforced by PES |

### Wave 9 -- Post-Submission & Learning

| Artifact | Source of Truth | Created | Consumers | Integration Risk |
|----------|----------------|---------|-----------|-----------------|
| `${proposal_outcome}` | `proposal-state.json#volumes.*.outcome` | Wave 9 | Corpus tagging, pattern analysis, status display | HIGH -- append-only |
| `${debrief_source}` | User-provided file path | Wave 9 | Debrief parsing | LOW |
| Debrief structured | `./artifacts/wave-9-learning/debrief-structured.md` | Wave 9 | Critique mapping, pattern analysis, corpus annotation | MEDIUM |
| `${debrief_score_technical}`, etc. | Extracted from debrief structured | Wave 9 | Status display, pattern comparison | MEDIUM |
| Critique-section map | `./artifacts/wave-9-learning/critique-section-map.md` | Wave 9 | Lessons learned, future Wave 7 debrief cross-check | HIGH -- feeds future reviews |
| Pattern analysis | `./artifacts/wave-9-learning/pattern-analysis.md` | Wave 9 | Future Wave 0 fit scoring, future Wave 7 reviewer heuristics | MEDIUM |
| `${corpus_proposal_count}` | Computed from corpus | Wave 9 | Status display | LOW |
| `${win_rate}` | Computed from corpus outcomes | Wave 9 | Status display, pattern analysis | MEDIUM |
| Win/loss tags | `proposal-state.json#volumes.*.outcome` | Wave 9 | Corpus librarian, pattern analysis | HIGH -- append-only, PES enforced |
| Debrief request draft | `./artifacts/wave-9-learning/debrief-request-draft.md` | Wave 9 | Phil sends to contracting officer | LOW |
| Lessons learned | `./artifacts/wave-9-learning/lessons-learned.md` | Wave 9 | Corpus enrichment, future proposal reference | MEDIUM |

---

## Cross-Wave Artifact Flow (C3)

```
Wave 5                  Wave 6                Wave 7              Wave 8              Wave 9
figures/ ──────────────> assembled/ ─────────> reviewed ──────────> package/ ──────────> corpus
figure-inventory.md ───> figure insertion      scorecard           archive/             outcome tags
cross-ref-log.md ──────> cross-ref verify      red-team            confirmation         debrief
                         compliance-final       debrief-cross       immutable            pattern-analysis
                         jargon-audit           sign-off-record     snapshot             lessons-learned
```

---

## Artifacts Inherited from C1/C2 (Used in C3, Not Modified)

These artifacts are defined in the C1/C2 shared-artifacts-registry. C3 consumes them but does not change their source of truth.

| Artifact | Source | Used in C3 Waves | Role in C3 |
|----------|--------|-----------------|------------|
| `${topic_id}` | `proposal-state.json#topic.id` | 5, 6, 7, 8, 9 | Headers, filenames, portal packaging |
| `${topic_title}` | `proposal-state.json#topic.title` | 7, 9 | Review headers, debrief context |
| `${deadline}` / `${days_to_deadline}` | `proposal-state.json#topic.deadline` | 5, 6, 7, 8 | PES deadline blocking, status display |
| Compliance matrix | `./artifacts/wave-1-strategy/compliance-matrix.md` | 6, 7 | Final compliance check (same living document) |
| PDC files | `./pdcs/*.pdc` | 5 (gate check) | PES PDC gate for Wave 5 entry |
| Discrimination table | `./artifacts/wave-3-outline/discrimination-table.md` | 7 | Reviewer checks discriminators are evidenced |
| Proposal outline | `./artifacts/wave-3-outline/proposal-outline.md` | 5 | Figure placeholder inventory |

---

## Validation Rules (C3-Specific)

### Rule 5: Submission Immutability

Once a proposal is submitted (Wave 8 confirmation exists), all artifacts in the proposal directory tree are read-only. PES blocks all write operations. The immutable archive is the exact snapshot of what was submitted. No retroactive edits.

### Rule 6: Append-Only Corpus Operations

Win/loss tags in proposal-state.json are append-only. Debrief annotations are a layer on top of source documents -- the source is never modified. This ensures historical data integrity for pattern analysis.

### Rule 7: Figure-to-Text Consistency

Every figure file in the figures directory must be referenced in the assembled document text. Every figure reference in text must resolve to a file. Orphaned figures and broken references are flagged during Wave 6 assembly and Wave 7 review.

---

## Integration Checkpoints (C3)

| Checkpoint | Validation | Enforcement | Failure Action |
|------------|-----------|-------------|---------------|
| Wave 4 -> Wave 5 | All sections Tier 1+2 PDCs GREEN; human review per section | **PES hard gate** | PES blocks Wave 5 entry |
| Wave 5 -> Wave 6 | All figure placeholders addressed (generated, manual, or skipped) | Human checkpoint (approve/revise) | Human reviews figure inventory before formatting |
| Wave 6 -> Wave 7 | All compliance items covered or waived; all figures inserted; page count within limit | Human checkpoint (approve/revise) | Human reviews assembled package before final review |
| Wave 7 -> Wave 8 | Final sign-off recorded | **PES hard gate** | PES blocks submission prep |
| Wave 8 -> Wave 9 | Submission confirmation captured | **PES hard gate** | PES blocks debrief ingestion |
| Any wave (C3) | `${days_to_deadline}` <= critical threshold | **PES hard gate** | PES warning + optional wave skip |

---

## New Command Names (C3)

| Command | Canonical Definition | Phase | Integration Risk |
|---------|---------------------|-------|-----------------|
| `/proposal wave visuals` | Wave 5 visual asset generation | C3 | HIGH -- name mismatch = undiscoverable |
| `/proposal wave visuals --replace <n> <file>` | Manual figure replacement | C3 | MEDIUM |
| `/proposal format` | Wave 6 formatting and assembly | C3 | HIGH |
| `/proposal wave final-review` | Wave 7 final review simulation | C3 | HIGH |
| `/proposal submit prep` | Wave 8 submission preparation and verification | C3 | HIGH |
| `/proposal submit` | Wave 8 submission confirmation and archiving | C3 | HIGH |
| `/proposal debrief ingest <path>` | Wave 9 debrief feedback ingestion | C3 | HIGH |
