# ADR-021: Separate Image Registry from Text Corpus Registry

## Status

Accepted

## Context

The corpus image reuse feature needs to store metadata for extracted images. Two options: extend the existing `proposal-state.json` corpus section, or create a separate `image-registry.json` file. The existing corpus section tracks `directories_ingested`, `document_count`, and `file_hashes` -- a flat structure.

Image metadata is significantly richer: 18+ fields per entry including source provenance, quality assessment, figure classification, compliance flags, and duplicate tracking. A typical user (Marcus Chen persona) may have 180+ images across 40 proposals.

## Decision

Create a separate **`.sbir/corpus/image-registry.json`** file for image metadata, independent of `proposal-state.json`.

## Alternatives Considered

### Alternative 1: Embed in proposal-state.json

- **What**: Add an `images` array to the existing `corpus` section in `proposal-state.json`
- **Pros**: Single state file, consistent with existing pattern, no new file to manage
- **Cons**: 180+ images at 18 fields each would balloon `proposal-state.json` by ~100KB. Every state read/write (including PES enforcement hooks on every command) would serialize/deserialize the image registry. State schema evolution becomes coupled between proposal metadata and image metadata.
- **Rejected**: Performance impact on PES hooks (called on every PreToolUse) is unacceptable. Schema coupling between proposal state and image registry violates single responsibility.

### Alternative 2: Per-image sidecar files

- **What**: Store one `.json` sidecar per image in `.sbir/corpus/images/`
- **Pros**: No single large file, trivial per-image updates
- **Cons**: Search requires reading 180+ files for a single query. No atomic batch operations. File enumeration on Windows is slower than single-file JSON read. List/search commands become O(n) filesystem operations.
- **Rejected**: Search performance is the #1 user priority (JTBD score 18.0). Per-file approach makes search O(n) filesystem reads instead of one JSON parse.

## Consequences

### Positive

- Image registry is independent of proposal state -- PES hooks never touch image data
- Single file for all image metadata -- search and list are one JSON parse
- Schema versioning is independent (image registry can evolve without touching proposal state)
- Atomic writes via the existing temp-file-then-rename pattern

### Negative

- Two state files to manage in `.sbir/corpus/` instead of one
- Backup/restore must include both files
- 180+ entry JSON file at ~100KB -- acceptable for single-file read, but may need pagination display for the `list` command

### Quality Attribute Impact

- **Maintainability**: Independent evolution of image schema without risk to proposal state
- **Testability**: Image registry port can be tested in isolation from state port
- **Performance**: PES hooks unaffected; image operations read only the image registry
