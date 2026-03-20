---
name: wave-agent-mapping
description: Wave definitions, agent routing table, and checkpoint gates for the SBIR proposal lifecycle
---

# Wave-Agent Mapping

## Wave Definitions

| Wave | Name | Primary Agents | Exit Gate |
|------|------|---------------|-----------|
| 0 | Intelligence & Fit | corpus-librarian, solution-shaper | Go/No-Go human checkpoint, Approach Selection checkpoint |
| 1 | Requirements & Strategy | compliance-sheriff, tpoc-analyst, strategist | Strategy alignment checkpoint |
| 2 | Research | researcher, strategist | Research completeness review |
| 3 | Discrimination & Outline | writer, reviewer | Discrimination table + outline approval |
| 4 | Drafting | writer, reviewer | Section draft approvals |
| 5 | Visual Assets | formatter, writer | Visual asset review |
| 6 | Formatting & Assembly | formatter, compliance-sheriff | Format compliance check |
| 7 | Final Review | reviewer, compliance-sheriff | Final review approval |
| 8 | Submission | submission-agent | Submission package verification |
| 9 | Post-Submission | debrief-analyst, corpus-librarian | Debrief ingestion complete |

## Command-to-Agent Routing

| Command | Dispatches To | Wave Context |
|---------|--------------|-------------|
| `proposal config format <format>` | FormatConfigService (orchestrator-inline) | Any wave (rework warning at 3+) |
| `proposal new` | corpus-librarian (+ topic-scout, fit-scorer in C2) | Wave 0 |
| `proposal shape` | sbir-solution-shaper | Wave 0 (post-Go) |
| `proposal corpus add <path>` | sbir-corpus-librarian | Any wave |
| `proposal corpus list` | sbir-corpus-librarian | Any wave |
| `proposal compliance check` | sbir-compliance-sheriff | Wave 1+ |
| `proposal tpoc questions` | sbir-tpoc-analyst | Wave 1 |
| `proposal tpoc ingest` | sbir-tpoc-analyst | Wave 1 |
| `proposal draft <section>` | sbir-writer | Wave 4 |
| `proposal iterate <section>` | sbir-writer + sbir-reviewer | Wave 4 |
| `proposal format` | sbir-formatter | Wave 6 |
| `proposal submit prep` | sbir-submission-agent | Wave 8 |
| `proposal debrief ingest <path>` | sbir-debrief-analyst | Wave 9 |
| `proposal review` | sbir-reviewer | Current wave |
| `proposal status` | Self (orchestrator reads state directly) | Any wave |
| `proposal switch <topic-id>` | Self (orchestrator validates target, updates active pointer) | Any wave |
| `proposal wave <name>` | Self (state transition) | Any wave |

## Wave Transition Rules

Waves are sequential with PES enforcement. The orchestrator does not duplicate enforcement logic -- PES hooks block invalid transitions at the platform level.

Orchestrator responsibilities for transitions:
1. Read current wave from `.sbir/proposal-state.json`
2. Present checkpoint at wave exit gates
3. Record human decisions (approve/revise/skip/quit) in state
4. Update `current_wave` on approval
5. Surface deadline warnings when within threshold

## Async Event Handling

TPOC calls are async external events. Valid states:
- `not_started` -- no questions generated yet
- `questions_generated` -- questions written, call pending
- `answers_ingested` -- call happened, answers captured

"Pending" is valid indefinitely. No wave is blocked by a pending TPOC call. Strategy brief generates without TPOC data if call has not happened.

## Wave-Specific Artifact Paths

| Wave | Artifacts Directory |
|------|-------------------|
| 0 | `./artifacts/wave-0-intelligence/` |
| 1 | `./artifacts/wave-1-strategy/` |
| 2 | `./artifacts/wave-2-research/` |
| 3 | `./artifacts/wave-3-outline/` |
| 4 | `./artifacts/wave-4-drafts/` |
| 5 | `./artifacts/wave-5-visuals/` |
| 6 | `./artifacts/wave-6-formatted/` |
| 7 | `./artifacts/wave-7-review/` |
| 8 | `./artifacts/wave-8-submission/` |
| 9 | `./artifacts/wave-9-debrief/` |

## Checkpoint Definitions

| Checkpoint | Wave | Trigger | Decision Options |
|-----------|------|---------|-----------------|
| Go/No-Go | 0 | After fit scoring | go, no-go, defer |
| Approach Selection | 0 | After approach scoring (post-Go) | approve, revise, explore, restart, quit |
| Strategy Alignment | 1 | After strategy brief | approve, revise, skip |
| Research Completeness | 2 | After research synthesis | approve, revise, skip |
| Discrimination Table | 3 | After discrimination table | approve, revise, skip |
| Outline Review | 3 | After outline draft | approve, revise, skip |
| Section Draft (per section) | 4 | After each section draft | approve, revise, skip |
| Visual Assets | 5 | After visual asset creation | approve, revise, skip |
| Format Compliance | 6 | After formatting complete | approve, revise, skip |
| Final Review | 7 | After reviewer + compliance | approve, revise, reject |
| Submission Verification | 8 | After package assembly | submit, hold, abort |
| Debrief Complete | 9 | After debrief ingestion | archive, iterate |
