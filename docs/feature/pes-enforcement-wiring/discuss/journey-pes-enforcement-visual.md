# Journey: PES Enforcement Wiring -- Visual Map

## Overview

PES enforcement is invisible when everything is valid -- it only surfaces when an action would violate a proposal invariant. This journey maps the four enforcement touchpoints across the proposal lifecycle.

---

## Enforcement Touchpoint Map

```
Proposal Lifecycle
==================

Wave 0       Wave 1-4        Wave 5          Post-Submit       Debrief
[Go/NoGo] -> [Strategy..] -> [PDC Review] -> [Submitted] ->  [Outcomes]
                  |               |               |               |
                  v               v               v               v
            +----------+   +-----------+   +------------+   +-----------+
            | DEADLINE  |   | PDC GATE  |   | SUBMISSION |   | CORPUS    |
            | BLOCKING  |   |           |   | IMMUTABLE  |   | INTEGRITY |
            +----------+   +-----------+   +------------+   +-----------+
            Blocks non-    Blocks Wave 5   Blocks ALL       Blocks outcome
            essential      entry if RED    writes after     tag changes
            waves within   Tier 1/2 PDC   submit+immutable (append-only)
            3 days of      items exist
            deadline
```

---

## Touchpoint 1: Deadline Blocking

**When**: PreToolUse event on non-essential wave tool, within critical_days of deadline
**Evaluator**: `deadline_blocking.py`

```
+-- PES BLOCK: Deadline Proximity ------------------------------------+
|                                                                     |
|  Phil runs: /proposal wave research                                 |
|                                                                     |
|  PES reads:                                                         |
|    state.current_wave = 2  (non-essential wave)                     |
|    state.topic.deadline = "2026-04-15"                              |
|    rule.condition.critical_days = 3                                  |
|    days_remaining = 2                                               |
|                                                                     |
|  BLOCK: "Deadline approaching: non-essential waves blocked.         |
|   2 days remaining until deadline. Consider: submit with available  |
|   work or skip non-essential waves."                                |
|                                                                     |
|  Emotion: Grateful -> "PES just saved me from wasting time"        |
+---------------------------------------------------------------------+
```

**State fields read**: `current_wave`, `topic.deadline`
**Rule condition fields**: `critical_days`, `non_essential_waves`
**Tool name match**: `wave_{current_wave}` must appear in tool_name

---

## Touchpoint 2: PDC Gate

**When**: PreToolUse event targeting Wave 5, when RED Tier 1 or Tier 2 PDC items exist
**Evaluator**: `pdc_gate.py`

```
+-- PES BLOCK: PDC Gate ----------------------------------------------+
|                                                                      |
|  Phil runs: /proposal wave_5 draft                                   |
|                                                                      |
|  PES reads:                                                          |
|    rule.condition.target_wave = 5                                    |
|    rule.condition.requires_pdc_green = true                          |
|    state.pdc_status.technical_approach.tier_1 = "RED"                |
|    state.pdc_status.technical_approach.red_items =                   |
|      ["TRL justification missing"]                                   |
|                                                                      |
|  BLOCK: "Wave 5 requires all PDC items to be GREEN.                  |
|   RED PDC items: Section technical_approach: Tier 1 RED              |
|   (TRL justification missing)"                                      |
|                                                                      |
|  Emotion: Relieved -> "Caught a gap before I started drafting"       |
+----------------------------------------------------------------------+
```

**State fields read**: `pdc_status.{section_id}.tier_1`, `pdc_status.{section_id}.tier_2`, `pdc_status.{section_id}.red_items`
**Rule condition fields**: `target_wave`, `requires_pdc_green`
**Tool name match**: `wave_{target_wave}` must appear in tool_name

---

## Touchpoint 3: Submission Immutability

**When**: PreToolUse event on ANY tool, when proposal is submitted and marked immutable
**Evaluator**: `submission_immutability.py`

```
+-- PES BLOCK: Submission Immutability --------------------------------+
|                                                                       |
|  Phil runs: /proposal wave research  (any write tool)                 |
|                                                                       |
|  PES reads:                                                           |
|    rule.condition.requires_immutable = true                           |
|    state.submission.status = "submitted"                              |
|    state.submission.immutable = true                                  |
|    state.topic.id = "AF243-001"                                      |
|                                                                       |
|  BLOCK: "Proposal AF243-001 is submitted. Artifacts are read-only."   |
|                                                                       |
|  Emotion: Protected -> "Can't accidentally edit the submitted version" |
+-----------------------------------------------------------------------+
```

**State fields read**: `submission.status`, `submission.immutable`, `topic.id`
**Rule condition fields**: `requires_immutable`
**Tool name match**: None -- blocks ALL tools when triggered

---

## Touchpoint 4: Corpus Integrity

**When**: PreToolUse event on outcome/record_outcome tools, when existing outcome would be changed
**Evaluator**: `corpus_integrity.py`

```
+-- PES BLOCK: Corpus Integrity ----------------------------------------+
|                                                                        |
|  Phil runs: /proposal record_outcome loss  (but outcome already "win") |
|                                                                        |
|  PES reads:                                                            |
|    rule.condition.append_only_tags = true                              |
|    state.learning.outcome = "win"                                      |
|    state.requested_outcome_change = "loss"                             |
|                                                                        |
|  BLOCK: "Cannot modify existing outcome tag. Current: win.             |
|   Outcome tags are append-only to preserve corpus integrity."          |
|                                                                        |
|  Emotion: Informed -> "Right, outcomes are permanent for learning"     |
+------------------------------------------------------------------------+
```

**State fields read**: `learning.outcome`, `requested_outcome_change`
**Rule condition fields**: `append_only_tags`
**Tool name match**: `outcome` or `record_outcome` must appear in tool_name

---

## Emotional Arc

```
Start: Unaware           Middle: Surprised/Grateful        End: Confident
"Working as normal"  ->  "PES caught something I missed" -> "System has my back"
```

The emotional design goal: PES enforcement should feel like a helpful guardrail, not a bureaucratic gate. Block messages must be specific, actionable, and appreciative of context.

---

## Hook Pipeline Flow (All Evaluators)

```
Claude Code Event (PreToolUse)
    |
    v
hooks.json -> python3 -m pes.adapters.hook_adapter pre-tool-use
    |
    v
hook_adapter.process_hook_event()
    |
    v
JsonStateAdapter.load()  -->  proposal-state.json
JsonRuleAdapter.load()   -->  pes-config.json
    |
    v
EnforcementEngine.evaluate(state, tool_name)
    |
    v
For each rule in pes-config.json["rules"]:
    engine._rule_triggers(rule, state, tool_name)
        |
        +-- rule_type == "pdc_gate"                -> PdcGateEvaluator.triggers()
        +-- rule_type == "deadline_blocking"        -> DeadlineBlockingEvaluator.triggers()
        +-- rule_type == "submission_immutability"  -> SubmissionImmutabilityEvaluator.triggers()
        +-- rule_type == "corpus_integrity"         -> CorpusIntegrityEvaluator.triggers()
    |
    v
If any rule triggers: exit_code=1, message=joined block messages
If no rule triggers:  exit_code=0
```
