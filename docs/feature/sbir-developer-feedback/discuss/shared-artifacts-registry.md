# Shared Artifacts Registry — sbir-developer-feedback

All variables referenced in the journey and their single authoritative source.

| Variable | Source File | Field Path | Nullable |
|----------|-------------|------------|----------|
| `proposal_id` | `.sbir/proposals/{id}/proposal-state.json` | `proposal_id` | Yes (no active proposal) |
| `topic.id` | `.sbir/proposals/{id}/proposal-state.json` | `topic.id` | Yes |
| `topic.title` | `.sbir/proposals/{id}/proposal-state.json` | `topic.title` | Yes |
| `topic.agency` | `.sbir/proposals/{id}/proposal-state.json` | `topic.agency` | Yes |
| `topic.deadline` | `.sbir/proposals/{id}/proposal-state.json` | `topic.deadline` | Yes |
| `topic.phase` | `.sbir/proposals/{id}/proposal-state.json` | `topic.phase` | Yes |
| `current_wave` | `.sbir/proposals/{id}/proposal-state.json` | `current_wave` | Yes |
| `completed_waves` | `.sbir/proposals/{id}/proposal-state.json` | `waves[*]` where `status == completed` | No (empty list) |
| `skipped_waves` | `.sbir/proposals/{id}/proposal-state.json` | `waves[*]` where `status == skipped` | No (empty list) |
| `rigor_profile` | `.sbir/proposals/{id}/rigor-profile.json` | `profile_name` | Yes |
| `company_name` | `~/.sbir/company-profile.json` | `company_name` | Yes |
| `company_profile_age_days` | `~/.sbir/company-profile.json` | file `mtime` vs. now | Yes |
| `finder_results_age_days` | `.sbir/finder-results.json` | file `mtime` vs. now | Yes |
| `top_scored_topics` | `.sbir/finder-results.json` | `scored[0:5]` | No (empty list) |
| `generated_artifacts` | `.sbir/proposals/{id}/artifacts/` | directory listing | No (empty list) |
| `plugin_version` | git | `git rev-parse --short HEAD` | No (fallback: "unknown") |

## Active Proposal Resolution

The "active proposal" is resolved by `workspace_resolver.py` using `.sbir/active-proposal.json` or by scanning `.sbir/proposals/` for the most recently modified state file. The feedback command uses the same resolver.

## Privacy Boundary

**Included in snapshot**: metadata only (names, ages, counts, IDs, scores).
**Excluded from snapshot**: full company profile contents (capabilities text, past performance descriptions, key personnel details), full topic descriptions, draft proposal text.

Rationale: The snapshot must be reviewable and shareable without exposing sensitive proposal strategy or company IP.
