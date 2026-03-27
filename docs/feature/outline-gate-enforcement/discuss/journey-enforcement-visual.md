# Journey: Outline Gate Enforcement

## Journey Flow

```
[Writer dispatched to Wave 4]
    |
    v
[Agent attempts Write to wave-4-drafting/]
    |
    +-- proposal-outline.md exists    --NO--> [PES BLOCKS] --> Agent sees block message
    |   in wave-3-outline/?                        |            "Complete the outline first"
    |                                              |            Agent cannot proceed to drafting
    |                                              v
    |                                         [Outliner must complete Wave 3]
    |                                         - Write proposal-outline.md
    |                                         - Get user approval on outline
    |                                         - Then writer can retry
    |                                              |
    +-- proposal-outline.md exists    --YES--> [PES ALLOWS]
        in wave-3-outline/?                    Agent drafts sections
                                               following the approved outline
```

## Emotional Arc

```
Start: Invisible         Middle: Redirective       End: Confident
(PES works silently)     (blocks with guidance)    (outline enforced)

Dr. Moreno:              Dr. Moreno:               Dr. Moreno:
"I asked the writer      "Oh, the system is        "Every section follows
 to draft sections"       making sure the outline    my approved outline.
                          exists first. Good."       Page budgets are right."

Phil:                    Phil:                     Phil:
"Will the writer         "The hook fired.          "The outline gate held.
 follow the outline      The agent cannot skip      No more fabricated
 this time?"              the outline."              section structure."
```

## Step-by-Step Detail

### Step 1: Writer Agent Dispatched to Wave 4

The orchestrator dispatches sbir-writer for Wave 4 drafting work. PES SubagentStart hook verifies the agent is authorized for Wave 4 (existing behavior from wave ordering evaluator).

```
+-- Wave 4: Drafting -----------------------------------------------+
|                                                                     |
| sbir-writer dispatched                                              |
| State: current_wave = 4                                             |
| Target dir: artifacts/{topic-id}/wave-4-drafting/                   |
| Prerequisite dir: artifacts/{topic-id}/wave-3-outline/              |
|                                                                     |
+---------------------------------------------------------------------+
```

**Emotional state**: Neutral. The user has asked the writer to draft sections.

### Step 2: Agent Attempts to Write a Draft Section (No proposal-outline.md)

The writer agent, following its natural tendency, attempts to Write a section file directly to wave-4-drafting/ without an approved outline in wave-3-outline/.

PES PreToolUse hook fires. The OutlineGateEvaluator checks:
- Is the tool Write or Edit?
- Is the target path in wave-4-drafting/?
- Does proposal-outline.md exist in the sibling wave-3-outline/ directory?

If proposal-outline.md does not exist in wave-3-outline/: BLOCK.

```
+-- PES: Outline Gate -- BLOCKED ------------------------------------+
|                                                                     |
| BLOCKED: Cannot write draft sections to wave-4-drafting/ before     |
| the proposal outline is approved.                                   |
|                                                                     |
| Required: artifacts/{topic-id}/wave-3-outline/proposal-outline.md   |
|                                                                     |
| The approved outline must exist before drafting can begin:           |
|  1. Complete Wave 3 (outline) with the outliner agent               |
|  2. Approve the outline (proposal-outline.md in wave-3-outline/)    |
|  3. Then Wave 4 drafting may proceed                                |
|                                                                     |
+---------------------------------------------------------------------+
```

**Emotional state**: Redirective. The agent receives clear guidance on what must happen first.

### Step 3: Outline Created in Wave 3 (Prerequisite Satisfied)

The outliner agent completes Wave 3: builds the section structure, assigns page budgets, maps compliance items, writes thesis statements, creates the discrimination table, and writes proposal-outline.md to wave-3-outline/. The user approves the outline.

Note: The outline gate evaluator does NOT gate writes to wave-3-outline/. That is a different wave directory. The gate only activates on wave-4-drafting/ paths.

```
+-- Wave 3: Outline (completed) ------------------------------------+
|                                                                     |
| artifacts/{topic-id}/wave-3-outline/proposal-outline.md EXISTS      |
| Contains: section structure, page budgets, compliance mapping,      |
|           thesis statements, discrimination table                   |
|                                                                     |
+---------------------------------------------------------------------+
```

**Emotional state**: Progressive. The foundation is in place.

### Step 4: Writer Agent Drafts Sections (Gate Passes)

With proposal-outline.md in wave-3-outline/, the writer agent attempts to Write section files to wave-4-drafting/. PES PreToolUse hook fires. The OutlineGateEvaluator checks: proposal-outline.md exists in the sibling wave-3-outline/ directory. Decision: ALLOW.

```
+-- PES: Outline Gate -- ALLOWED ------------------------------------+
|                                                                     |
| proposal-outline.md: EXISTS in wave-3-outline/                      |
|                                                                     |
| Draft writing proceeds. Writer agent reads the approved outline     |
| and follows section structure, page budgets, and compliance mapping. |
|                                                                     |
+---------------------------------------------------------------------+
```

**Emotional state**: Confident. Every draft section follows the approved outline.

## Integration Points

| From | To | Artifact | Validation |
|------|----|----------|------------|
| Wave 3 outline | Wave 4 drafting (outline gate) | proposal-outline.md must exist | PES evaluator checks existence in wave-3-outline/ |
| Hook adapter | OutlineGateEvaluator | Sibling directory path resolution | Adapter derives wave-3-outline/ from wave-4-drafting/ target path |
| PES config | Engine evaluator dispatch | rule_type "outline_gate" | New type registered in engine |
| Hook adapter | PreToolUse handler | file_path from tool input | Path extraction for gate check |
