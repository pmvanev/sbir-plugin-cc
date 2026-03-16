# Shared Artifacts Registry: Corpus Image Reuse

## Artifact Inventory

### image_registry

- **Source of truth**: `.sbir/corpus/image-registry.json`
- **Owner**: Corpus Librarian agent (writes during ingestion)
- **Consumers**:
  - Step 1 (Extraction): writes entries during `corpus add`
  - Step 2 (List): reads for filtered tabular display
  - Step 3 (Search): reads for relevance-ranked query results
  - Step 4 (Show): reads for full detail view of single image
  - Step 5 (Use): reads to copy image and generate adapted caption
- **Integration risk**: HIGH -- this is the central data store for the entire feature. Schema changes break all downstream consumers.
- **Validation**: All 5 consumer steps must read the same entry format. Any schema addition must be backward-compatible.

### image_files

- **Source of truth**: `.sbir/corpus/images/` directory
- **Owner**: Corpus Librarian agent (writes during ingestion)
- **Consumers**:
  - Step 4 (Show): references file path for display/assessment
  - Step 5 (Use): copies file to `./artifacts/wave-5-visuals/`
- **Integration risk**: MEDIUM -- file naming convention must be deterministic and match registry `file_path` field.
- **Validation**: Every `file_path` in image_registry must resolve to an actual file in `.sbir/corpus/images/`.

### current_proposal_context

- **Source of truth**: `.sbir/proposal-state.json`
- **Owner**: Orchestrator (existing -- not modified by this feature)
- **Consumers**:
  - Step 3 (Search): reads agency and topic for relevance scoring
  - Step 4 (Show): reads agency for fitness assessment (agency match)
- **Integration risk**: LOW -- reads existing fields only. No writes.
- **Validation**: Proposal state must have `agency` and `topic` fields populated before image search/assessment works correctly.

### figure_inventory

- **Source of truth**: `./artifacts/wave-5-visuals/figure-inventory.json`
- **Owner**: Visual Asset Service (existing domain model, extended)
- **Consumers**:
  - Step 5 (Use): adds new entry with `method: "corpus-reuse"`
  - Step 6 (Formatter): reads inventory to route corpus-reuse figures to review (not generation)
  - Cross-reference validation reads all entries including corpus-reuse
- **Integration risk**: HIGH -- the existing `FigurePlaceholder` and `FigureInventory` domain objects must support the new `corpus-reuse` generation method. Formatter routing logic must handle this method.
- **Validation**: Figure inventory entry created by `corpus images use` must be parseable by the existing `VisualAssetService` and `FileVisualAssetAdapter`.

### figure_log

- **Source of truth**: `./artifacts/wave-5-visuals/figure-log.md`
- **Owner**: Formatter agent (existing, extended with corpus-reuse entries)
- **Consumers**:
  - Step 5 (Use): records source attribution when image is selected
  - Wave 5 figure review checkpoint: includes corpus-reuse figures
  - Wave 6 assembly: preserves attribution through to final document
- **Integration risk**: MEDIUM -- existing figure log format must accommodate a new "corpus-reuse" method column and source attribution fields.
- **Validation**: Figure log entries for corpus-reuse must include: source proposal ID, original figure number, and "corpus-reuse" method tag.

### cross_reference_log

- **Source of truth**: `./artifacts/wave-5-visuals/cross-reference-log.json`
- **Owner**: Visual Asset Service (existing domain model)
- **Consumers**:
  - Step 6 (Formatter): includes corpus-reused figures in cross-reference validation
  - Wave 6 assembly: verifies all figure references resolve
- **Integration risk**: MEDIUM -- existing `CrossReferenceLog` and `CrossReferenceEntry` domain objects must include figures with method "corpus-reuse" in validation.
- **Validation**: `CrossReferenceLog.all_valid` must account for corpus-reused figures alongside generated figures.

### corpus_text_registry

- **Source of truth**: `.sbir/proposal-state.json` (corpus section)
- **Owner**: Corpus Librarian (existing -- not directly modified by image feature)
- **Consumers**:
  - Step 1 (Extraction): text ingestion happens alongside image extraction in the same `corpus add` command
- **Integration risk**: LOW -- existing text ingestion is unchanged. Image extraction is additive.
- **Validation**: Text corpus counts must still be accurate after the `corpus add` command gains image extraction.

---

## Integration Checkpoints

### Checkpoint 1: Extraction -> Registry Consistency

**After**: Step 1 (Image Extraction)
**Verify**:
- Every image file in `.sbir/corpus/images/` has a corresponding entry in `image-registry.json`
- Every entry in `image-registry.json` has a valid `file_path` pointing to an existing file
- Content hashes in registry match actual file hashes (deduplication integrity)
- Text corpus counts are unaffected by image extraction (additive only)

### Checkpoint 2: Registry -> Search/List Consistency

**After**: Step 2-3 (List and Search)
**Verify**:
- All filters (type, outcome, source, agency) operate on the same registry data
- Search results reference valid image IDs that resolve in `corpus images show`
- Outcome data comes from the existing win/loss tracking in corpus state (not duplicated)

### Checkpoint 3: Show -> Use Data Flow

**After**: Step 4-5 (Show and Use)
**Verify**:
- Image detail view and use command reference the same registry entry
- File copy from `.sbir/corpus/images/` to `./artifacts/wave-5-visuals/` preserves file integrity (hash match)
- Adapted caption correctly identifies proposal-specific terms for removal
- Figure inventory entry is valid per `FigurePlaceholder` schema with `generation_method: "corpus-reuse"`

### Checkpoint 4: Use -> Formatter Handoff

**After**: Step 5-6 (Use and Formatter)
**Verify**:
- `FigureInventory` correctly loads entries with `generation_method: "corpus-reuse"`
- Formatter routing logic skips generation for corpus-reuse figures
- Formatter review checkpoint presents corpus-reuse figures with approve/revise/replace options
- Cross-reference validation includes corpus-reuse figures alongside generated figures
- Figure log attribution persists through Wave 6 assembly

---

## CLI Vocabulary Consistency

| Command | Pattern | Notes |
|---------|---------|-------|
| `corpus add <dir>` | Existing command, extended | Image extraction is additive behavior |
| `corpus images list` | `noun noun verb` | Follows existing `corpus list` pattern |
| `corpus images search "<query>"` | `noun noun verb` | Consistent with `corpus images list` |
| `corpus images show <id>` | `noun noun verb` | Consistent |
| `corpus images use <id>` | `noun noun verb` | "use" = select for reuse in current proposal |
| `corpus images flag <id>` | `noun noun verb` | "flag" = mark for compliance review |
| `corpus images unflag <id>` | `noun noun verb` | "unflag" = clear compliance flag |
| `corpus images skip <id>` | `noun noun verb` | "skip" = mark as not relevant (optional) |

All image commands live under the `corpus images` subcommand namespace, maintaining the existing `corpus` command structure.

---

## New Data Schema: Image Registry Entry

```json
{
  "id": "af243-001-fig-03",
  "source_proposal": "AF243-001",
  "proposal_title": "Compact Directed Energy for Maritime UAS Defense",
  "agency": "USAF",
  "outcome": "WIN",
  "page_number": 7,
  "section": "Technical Approach",
  "original_figure_number": 3,
  "caption": "Figure 3: CDES System Architecture showing phased array subsystem, beam control unit, and power management",
  "surrounding_text": "The proposed system architecture leverages our proven CDES platform...",
  "figure_type": "system-diagram",
  "file_path": ".sbir/corpus/images/af243-001-fig-03.png",
  "content_hash": "a3f2b7c...",
  "resolution_width": 2048,
  "resolution_height": 1536,
  "dpi": 300,
  "quality_level": "high",
  "size_bytes": 867328,
  "extraction_date": "2026-03-16",
  "origin_type": "company-created",
  "compliance_flag": null,
  "duplicate_sources": []
}
```
