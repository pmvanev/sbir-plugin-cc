# Problem Validation -- SBIR Proposal Writing Plugin

## Problem Statement (Customer Words)

Small business engineers who write SBIR/STTR proposals spend excessive hours on a process that is fragmented, compliance-heavy, and poorly supported by existing AI tools. In their words:

- "Long time" -- the sheer person-hours required
- "Searching through documents" -- finding relevant past performance, evidence, and boilerplate
- "AI writes garbage sometimes" -- current AI tools produce unreliable output
- "Hallucinatory technical promises" -- AI-generated content is overly verbose and makes claims the company cannot support
- "Agents must be micromanaged" -- autonomous AI iteration does not work with current tools

## Evidence Base

### Sources

| Source | Type | Evidence Quality |
|---|---|---|
| Product owner (1 person) | First-person proposal writer | Strong -- past behavior, specific pain points |
| 8 internal proposal writers | Engineers who also write proposals | Moderate -- same company; independently confirmed pain |
| Past spending on proposal firms | Behavioral signal | Strong -- $5-10K per proposal spent |
| Internal AI scrubbing tool built | Behavioral signal | Very strong -- coded a solution to part of the problem |
| Procura Federal exists commercially | Market signal | Strong -- others pay for this problem space |

### Interview Evidence Summary

**Total sources consulted:** 9
**Confirmation rate:** ~100% (all confirm the problem is real and painful)

#### Pain Points Ranked by Frequency and Intensity

| Pain Point | Sources Confirming | Intensity |
|---|---|---|
| Time spent searching/gathering documents | 9/9 | High |
| Compliance tracking and requirements management | 9/9 | High |
| AI output quality and trust | 8/8 writers + owner | High |
| Understanding vague solicitation language | Owner | High |
| Competitive positioning ("why us") | Owner | High |
| Formatting (orphans, widows, margins) | Owner | Medium |
| Win/loss pattern understanding | Owner | Medium |
| Creating images and diagrams | Owner | Medium |

#### Workarounds Currently Used (Willingness to Pay)

| Workaround | Cost | Effectiveness |
|---|---|---|
| Proposal writing firms | $5-10K per proposal | Same win rate as internal; unclear ROI |
| Internal AI scrubbing tool | Engineering time to build | Works for topic discovery; tailor-made preference |
| Manual compliance checklists | Person-hours | Inadequate; items get missed |
| ChatGPT/Claude for boilerplate | API costs | Works for boilerplate; fails for technical narrative |
| Manual document search | Person-hours | Slow and frustrating |

#### AI Tool Experience (8 Writers)

- All 8 have tried AI tools for proposal work
- **What works:** Boilerplate generation
- **What does NOT work:** Automatic iteration, review, research, autonomous workflows
- **Root cause (reframed):** Current tools lack guardrails, defined targets, and enforcement mechanisms -- not that autonomous agents are inherently unviable

## Gate G1 Evaluation

| Criterion | Target | Result |
|---|---|---|
| Interviews/sources | 5+ | PASS (9) |
| Problem confirmation | >60% | PASS (~100%) |
| Problem in customer words | Yes | PASS (direct quotes captured) |
| Frequency | Weekly+ | PASS (recurring business activity) |
| Current spending | >$0 | PASS ($5-10K/proposal + internal tooling) |
| Emotional intensity | Frustration evident | PASS ("garbage", "hallucinatory", "micromanaged") |

**Gate G1: PASS -- Proceed to Opportunity Mapping**
