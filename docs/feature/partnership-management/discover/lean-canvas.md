# Lean Canvas: Partnership Management Feature

## Discovery State

- **Phase**: 4 context (prepared early for completeness -- will be validated in Phase 4)
- **Feature ID**: partnership-management
- **Scope**: Plugin feature, not standalone product

## 1. Problem (Phase 1 Validated)

1. **New partner onboarding is slow and risky**: 14 calendar days, 2-3 exchanges, and partners can back out after weeks of investment (Q6, Q8)
2. **Partner coordination is the bottleneck**: Waiting on SOW/budget info is the hardest part of partnered proposals (Q4)
3. **No AI leverage on the partnership**: Company profile enables AI suggestions for the primary entity, but partner capabilities are opaque to the plugin (Q10)

## 2. Customer Segments (by JTBD)

- **Primary**: Small-business SBIR/STTR proposal writers who work with research institution partners (the plugin author's exact profile)
- **Secondary**: SBIR teams with rotating or expanding partner networks (less validated -- would benefit most from O5)

## 3. Unique Value Proposition

"Your partner's profile is as rich as your company's -- so the plugin can make suggestions for both entities individually and as a partnered pair."

(Derived directly from customer words, Q10)

## 4. Solution (Top 3 from OST)

1. **Rich partner profiles** with AI-assisted partnership suggestions (O1 + O4 as enabler)
2. **Structured coordination templates** -- SOW/budget/technical profile templates that reduce the 14-day cycle (O2)
3. **Partner readiness screening** -- early commitment/fit detection before heavy investment (O3)

## 5. Channels

- Plugin is already installed by target users (sbir-plugin-cc)
- Feature discovered via `/partner` commands in existing workflow
- No separate acquisition needed -- feature adoption = usage within existing plugin

## 6. Revenue Streams

- N/A for standalone revenue -- this is a feature that increases overall plugin value
- Contributes to plugin retention and STTR proposal coverage (currently a gap)

## 7. Cost Structure

- Development cost: agent markdown + partner profile schema + templates
- Minimal ongoing cost: partner profiles stored in `.sbir/` (user's local filesystem)
- No external API costs beyond existing Claude Code usage

## 8. Key Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Partner profile completion | >80% of fields populated | Schema validation |
| Coordination cycle time | <7 days (from 14) | User-reported |
| Partnership suggestion quality | User accepts >50% of suggestions | Usage tracking |
| STTR proposal coverage | 100% of STTR proposals use partner features | Plugin usage |

## 9. Unfair Advantage

- Mirrors the existing company-profile architecture (already validated and shipped)
- Plugin already has the AI agent infrastructure for suggestion generation
- Partner data combined with company data enables unique cross-entity analysis no standalone tool provides

## 4 Big Risks Assessment

| Risk | Status | Evidence | Mitigation |
|------|--------|----------|------------|
| **Value** | GREEN | Strong commitment signal (Q10), quantified pain (Q6), failure case (Q8) | Phase 3 prototype testing will validate |
| **Usability** | YELLOW | Company profile builder is the precedent -- similar UX pattern. Untested for partner-specific flows | Mirror company profile UX; test in Phase 3 |
| **Feasibility** | GREEN | Company profile schema exists as template. AI agents already generate suggestions from structured profiles. No new infrastructure needed | Technical spike for partner-topic matching (A6) |
| **Viability** | GREEN | No revenue model needed (plugin feature). Development cost is bounded. Leverages existing architecture | -- |

## Pre-Phase 3 Notes

This canvas is prepared from Phase 1-2 evidence. Phase 3 (Solution Testing) will validate:
- Whether the partner profile schema is intuitive to populate
- Whether AI suggestions from combined profiles are useful
- Whether coordination templates actually reduce cycle time
- Usability of the partner readiness screening flow
