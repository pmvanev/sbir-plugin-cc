# Journey: PES Figure Pipeline Enforcement

## Journey Flow

```
[Formatter dispatched to Wave 5]
    |
    v
[Agent attempts Write to wave-5-visuals/]
    |
    +-- figure-specs.md exists? --NO--> [PES BLOCKS] --> Agent sees block message
    |                                        |            "Create figure-specs.md first"
    |                                        |            Agent redirects to Phase 1
    |                                        v
    |                                   [Agent runs Phase 1]
    |                                   - Reads figure plan
    |                                   - Checks tool availability
    |                                   - Runs style analysis
    |                                   - Writes figure-specs.md  <-- ALLOWED (prerequisite file)
    |                                   - Writes style-profile.yaml (or records skip)
    |                                        |
    +-- figure-specs.md exists? --YES--> [Check Style Gate]
                                              |
                                         style-profile.yaml exists
                                         OR skip marker in state?
                                              |
                                         NO --+--> [PES BLOCKS]
                                              |    "Complete style analysis first"
                                              |    Agent runs style conversation
                                              |
                                         YES -+--> [PES ALLOWS]
                                                   Agent generates figures
                                                   (Phase 2 proceeds normally)
```

## Emotional Arc

```
Start: Invisible         Middle: Redirective       End: Confident
(PES works silently)     (blocks with guidance)    (pipeline guaranteed)

Dr. Moreno:              Dr. Moreno:               Dr. Moreno:
"I asked for figures"    "Oh, the system is        "Every figure was planned,
                          making sure we plan        styled, and reviewed.
                          first. Makes sense."       The figures look professional."

Phil:                    Phil:                     Phil:
"Will the agent          "The hook fired.          "The pipeline held.
 follow instructions      The agent cannot skip     No more hand-coded SVGs."
 this time?"              Phase 1."
```

## Step-by-Step Detail

### Step 1: Formatter Agent Dispatched to Wave 5

The orchestrator dispatches sbir-formatter for Wave 5 visual asset work. PES SubagentStart hook verifies the agent is authorized for Wave 5 (existing behavior).

```
+-- Wave 5: Visual Assets ----------------------------------------+
|                                                                   |
| sbir-formatter dispatched                                         |
| State: current_wave = 5                                           |
| Artifacts dir: artifacts/{topic-id}/wave-5-visuals/               |
|                                                                   |
+-------------------------------------------------------------------+
```

**Emotional state**: Neutral. The user has asked the formatter to create figures.

### Step 2: Agent Attempts to Write a Figure File (No figure-specs.md)

The formatter agent, following its natural tendency, attempts to Write an SVG or image file directly to wave-5-visuals/ without first creating figure-specs.md.

PES PreToolUse hook fires. The FigurePipelineGateEvaluator checks:
- Is the tool Write or Edit?
- Is the target path in wave-5-visuals/?
- Is the file being written NOT figure-specs.md itself (allow prerequisite creation)?
- Does figure-specs.md exist in wave-5-visuals/?

If figure-specs.md does not exist and the file being written is not figure-specs.md: BLOCK.

```
+-- PES: Figure Pipeline Gate -- BLOCKED --------------------------+
|                                                                   |
| BLOCKED: Cannot write figure files to wave-5-visuals/ before      |
| creating figure specifications.                                   |
|                                                                   |
| Required: artifacts/{topic-id}/wave-5-visuals/figure-specs.md     |
|                                                                   |
| The figure specification plan must be created first:              |
|  1. Read the figure plan from wave-3-outline/figure-plan.md      |
|  2. Check available generation tools (mmdc, dot, python3, etc.)  |
|  3. Write figure specifications to wave-5-visuals/figure-specs.md |
|                                                                   |
| After figure-specs.md exists, figure generation may proceed.      |
|                                                                   |
+-------------------------------------------------------------------+
```

**Emotional state**: Redirective. The agent receives clear guidance on what to do first.

### Step 3: Agent Creates figure-specs.md (Allowed)

The agent follows its Phase 1 workflow: reads the figure plan, checks tool availability, writes figure-specs.md. PES allows this write because the target IS figure-specs.md (the prerequisite artifact itself).

```
+-- PES: Figure Pipeline Gate -- ALLOWED --------------------------+
|                                                                   |
| Writing: artifacts/{topic-id}/wave-5-visuals/figure-specs.md      |
| (prerequisite artifact creation -- allowed)                       |
|                                                                   |
+-------------------------------------------------------------------+
```

**Emotional state**: Progressive. The agent is building the foundation correctly.

### Step 4: Agent Attempts Figure Generation (No style-profile.yaml)

With figure-specs.md now in place, the agent attempts to generate the first figure. PES PreToolUse hook fires again. The StyleProfileGateEvaluator checks:
- Is the tool Write or Edit?
- Is the target path in wave-5-visuals/?
- Is the file NOT figure-specs.md and NOT style-profile.yaml?
- Does style-profile.yaml exist OR does state contain a style_analysis_skipped marker?

If neither condition is met: BLOCK.

```
+-- PES: Style Profile Gate -- BLOCKED ----------------------------+
|                                                                   |
| BLOCKED: Cannot generate figures before style analysis.           |
|                                                                   |
| Required (one of):                                                |
|  - artifacts/{topic-id}/wave-5-visuals/style-profile.yaml         |
|  - Style analysis skip recorded in proposal state                 |
|                                                                   |
| Complete the style recommendation conversation:                   |
|  1. Analyze agency/domain style conventions                       |
|  2. Recommend palette, tone, and detail level                     |
|  3. Get user approval, adjustment, or skip                        |
|  4. Write style-profile.yaml (or record skip in state)            |
|                                                                   |
+-------------------------------------------------------------------+
```

**Emotional state**: Redirective. The agent is guided to the style conversation.

### Step 5: Style Conversation and Profile Creation

The agent runs the style analysis: looks up the agency in the style database, recommends a profile, presents it to the user. The user approves, adjusts, or skips. The result is either:
- style-profile.yaml written to wave-5-visuals/ (PES allows this -- it is the prerequisite itself)
- OR style_analysis_skipped: true recorded in proposal state

```
+-- Style Analysis Conversation -----------------------------------+
|                                                                   |
| Agency: DoD / Air Force                                           |
| Domain: Autonomous sensor fusion                                  |
|                                                                   |
| Recommended style profile:                                        |
|   Palette: #1B3A5C, #4A90D9, #E8EEF4, #2D2D2D                   |
|   Tone: Technical-professional                                    |
|   Detail level: High (defense audience expects precision)         |
|   Avoid: Cartoon elements, gradient fills, decorative borders     |
|                                                                   |
| Options: [approve] [adjust] [skip style analysis]                 |
|                                                                   |
+-------------------------------------------------------------------+
```

**Emotional state**: Engaged. Dr. Moreno makes a conscious choice about visual identity.

### Step 6: Figure Generation Proceeds (Both Gates Passed)

Both gates are satisfied. PES allows all subsequent writes to wave-5-visuals/. The agent generates figures using the tiered method hierarchy, applies the style profile, runs the structured critique loop.

```
+-- PES: Both Gates Passed -- ALLOWED -----------------------------+
|                                                                   |
| figure-specs.md: EXISTS                                           |
| style-profile.yaml: EXISTS (or skip recorded)                     |
|                                                                   |
| Figure generation proceeds through normal Phase 2 pipeline.       |
|                                                                   |
+-------------------------------------------------------------------+
```

**Emotional state**: Confident. Every figure follows the full pipeline.

## Integration Points

| From | To | Artifact | Validation |
|------|----|----------|------------|
| Wave 3 outline | Wave 5 figure pipeline gate | figure-plan.md must exist | Agent reads plan before writing specs |
| Phase 1 (specs) | Phase 2 (generation) | figure-specs.md | PES gate checks existence |
| Phase 1 (style) | Phase 2 (generation) | style-profile.yaml OR state marker | PES gate checks existence or state |
| PES config | Engine evaluator dispatch | rule_type strings | New types registered in engine |
| Hook adapter | PreToolUse handler | file_path from tool input | Path extraction for gate checks |
