# JTBD Analysis: Outline Gate Enforcement

## Job Classification

**Job Type**: Brownfield Improvement (Job 2)
**Rationale**: PES enforcement system already exists with 8 evaluators and 11 config rules. Problem is identified (writer agent can draft without approved outline). Scope is clear (1 new evaluator, cross-directory artifact check). Established pattern from FigurePipelineGateEvaluator. No discovery phase needed -- enter execution loop.

## Job Stories

### JS-1: Outline Enforcement

**When** the writer agent begins Wave 4 drafting and no approved outline exists in wave-3-outline/,
**I want to** be blocked from writing draft sections,
**so I can** trust that every section follows the approved structure with correct page budgets and compliance mapping.

#### Functional Job

Prevent the writer agent from writing draft section files to wave-4-drafting/ before proposal-outline.md exists in wave-3-outline/. The outline provides section structure, page budgets, compliance item mapping, thesis statements, and the discrimination table.

#### Emotional Job

Feel confident that every drafted section traces back to an approved plan -- not a fabricated structure the agent invented on the spot.

#### Social Job

Present a proposal whose structure follows the approved outline, demonstrating disciplined execution to reviewers and co-PIs who reviewed the outline.

#### Forces Analysis

- **Push**: During the SF25D-T1201 proposal session, the writer agent began drafting sections without referencing the outline, fabricating section structure that did not match the approved plan. Page budgets were ignored, compliance items were missed, and the discrimination table was not reflected in the narrative.
- **Pull**: PES hooks run as Python code at the Claude Code layer -- a harder enforcement boundary than markdown instructions. The FigurePipelineGateEvaluator pattern already proves this works for local artifact checks. This gate extends the pattern to cross-directory checks.
- **Anxiety**: Could the gate block legitimate writes? The writer agent must be able to write proposal-outline.md to wave-3-outline/ (but that is the outliner agent's job, not the writer's). The writer only writes to wave-4-drafting/, and the gate only triggers on wave-4-drafting/ paths. Minimal false-positive risk.
- **Habit**: The writer agent's markdown instructions already say "read the approved outline first." But agents skip instructions when trying to be helpful. Without enforcement, the outline is easily ignored because the agent can still produce plausible-looking draft sections without it.

## Outcome Statements

1. Minimize the likelihood that the writer agent drafts sections without an approved outline
2. Minimize the number of proposals with section structure that diverges from the approved plan
3. Maximize the confidence that every draft section traces back to outline page budgets and compliance mapping
4. Minimize the time wasted on rework when draft sections do not match the outline

## Personas

### Persona 1: Dr. Rafael Moreno -- SBIR Principal Investigator

Rafael is the founder and PI at a small defense tech company (8 employees). He is writing a DoD Phase I SBIR proposal for SF25D-T1201 (autonomous sensor fusion). He spent significant effort in Wave 3 developing a detailed outline with section structure, page budgets, compliance item mapping, thesis statements, and a discrimination table. He expects Wave 4 drafting to follow that outline exactly. He was frustrated when the writer agent fabricated section structure during drafting, ignoring the outline he had approved.

### Persona 2: Phil -- Plugin Maintainer

Phil maintains the SBIR proposal plugin and has 8 existing PES evaluators. He needs the outline gate to follow the established hexagonal pattern (domain evaluator, engine registration, config rule). The cross-directory check (wave-4-drafting/ target, wave-3-outline/ prerequisite) is a new adapter concern -- the existing FigurePipelineGateEvaluator checks a same-directory artifact. Phil wants the adapter to derive the sibling wave directory path from the target path.
