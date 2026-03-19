---
name: proposal-state-schema
description: Schema reference for proposal-state.json fields. Shared across all agents that read or write proposal state.
---

# Proposal State Schema

## output_format

| Attribute | Value |
|-----------|-------|
| Field path | `output_format` |
| Type | string |
| Valid values | `"latex"`, `"docx"` |
| Default | `"docx"` |
| Required | Yes (set during proposal setup) |
| Added in | proposal-format-selection feature |

### When it is set

The `output_format` field is set during `/proposal new`, after fit scoring and before the Go/No-Go checkpoint.

- **Default (Enter)**: Sets `output_format` to `"docx"`.
- **Explicit selection**: Sets `output_format` to the chosen value (`"latex"` or `"docx"`).
- **PDF-submission hint**: When the solicitation text contains PDF submission indicators (e.g. "submit as PDF", "PDF format required"), the prompt recommends LaTeX for higher-fidelity PDF output.

### Mid-proposal changes

Format can be changed later via `/proposal format change`. Changes at Wave 3 or later trigger a rework warning because outline and draft artifacts may need adjustment.

### Legacy states

States created before the format-selection feature may lack `output_format`. When reading state, treat a missing field as `"docx"` (the default). The `FormatConfigService.get_effective_format()` method handles this.

### Status dashboard

The `/proposal status` dashboard includes the current `output_format` value so the engineer always knows which pipeline is active.

### Validation

Invalid values (anything other than `"latex"` or `"docx"`) are rejected by schema validation. The `FormatConfigService.validate_format()` method performs this check.

## partner

| Attribute | Value |
|-----------|-------|
| Field path | `partner` |
| Type | object or null |
| Fields | `slug` (string), `designated_at` (ISO-8601 string) |
| Default | `null` |
| Required | No (null for non-partnered proposals) |
| Added in | partnership-management feature |

### Structure

```json
{
  "partner": {
    "slug": "cu-boulder",
    "designated_at": "2026-03-19T10:00:00Z"
  }
}
```

Or `null` for non-partnered proposals.

### When it is set

The `partner` field is set in two ways:

- **During `/proposal new`**: For STTR topics, the user is prompted to select a partner from `~/.sbir/partners/`. If no partner profiles exist, a helpful message suggests running `/proposal partner-setup` first.
- **Via `/proposal partner-set`**: Can change the designated partner at any point. Warns about stale artifacts if current wave > 0.

### How consuming agents use it

All partnership-aware agents read `partner.slug` from proposal state, then load the full partner profile from `~/.sbir/partners/{slug}.json`. If `partner` is null or missing, agents fall back to current non-partnered behavior. This makes the extension fully backward compatible.

| Agent | What it reads | Behavior when null |
|-------|--------------|-------------------|
| sbir-topic-scout | partner profile capabilities | Solo scoring only |
| sbir-strategist | partner profile (all fields) | Standard teaming section |
| sbir-solution-shaper | partner profile capabilities | Approaches without work splits |
| sbir-writer | partner profile (all fields) | Standard draft without partner references |

### Legacy states

States created before the partnership-management feature lack the `partner` field. When reading state, treat a missing field as `null`. All consuming agents handle this gracefully.

### Stale artifact warning

When the partner is changed via `/proposal partner-set` after Wave 0, the command warns that scoring results, strategy briefs, and approach briefs may reference the previous partner. The user decides whether to regenerate.
