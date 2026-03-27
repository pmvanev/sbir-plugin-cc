# JTBD Analysis: PES Figure Pipeline Enforcement

## Job Classification

**Job Type**: Brownfield Improvement (Job 2)
**Rationale**: PES enforcement system already exists with 5 evaluators. Problem is identified (agent bypassed pipeline). Scope is clear (2 new evaluators). No discovery phase needed -- enter execution loop.

## Job Stories

### JS-1: Pipeline Integrity Enforcement

**When** the sbir-formatter agent begins Wave 5 visual asset work and has not yet created a figure specification plan,
**I want to** be blocked from writing figure files directly to wave-5-visuals/,
**so I can** trust that every figure follows the structured pipeline (plan, detect tools, analyze style, specify, generate, critique) rather than ad-hoc hand-coding.

#### Functional Job
Prevent the formatter agent from writing figure artifacts before the planning phase (Phase 1 of the formatter workflow) is complete.

#### Emotional Job
Feel confident that the proposal's visual assets were produced through a rigorous, repeatable pipeline -- not shortcuts that degrade quality.

#### Social Job
Present a professional proposal with consistently high-quality figures that reflect well on the company and the principal investigator.

#### Forces Analysis
- **Push**: During the SF25D-T1201 proposal session, the formatter hand-coded raw inline SVGs, skipping tool detection, style analysis, and the structured critique loop. The resulting figures were inconsistent and low quality.
- **Pull**: PES hooks are Python code that runs as Claude Code hooks and can physically BLOCK non-compliant tool invocations. This is a harder enforcement boundary than markdown instructions.
- **Anxiety**: Could the gate be too aggressive and block legitimate early writes (e.g., writing the figure-specs.md file itself)?
- **Habit**: Markdown agent instructions ("never bypass the pipeline") were already present but ignored. The agent's natural tendency is to be helpful and generate content immediately.

### JS-2: Style Conversation Enforcement

**When** the formatter agent is ready to generate figures (Phase 2) but has not had a style recommendation conversation with the user,
**I want to** be blocked from figure generation until a style profile exists or the user has explicitly skipped style analysis,
**so I can** trust that the user was consulted about visual preferences before figures are produced.

#### Functional Job
Ensure the style profile conversation (agency style database lookup, palette/tone recommendation, user approval/adjustment/skip) occurs before any figure generation begins.

#### Emotional Job
Feel that the proposal's visual identity was a deliberate choice, not an afterthought -- the user had agency over how their figures look.

#### Social Job
Produce figures that match agency expectations and domain conventions, reflecting the PI's understanding of their audience.

#### Forces Analysis
- **Push**: In the SF25D-T1201 session, style analysis was skipped entirely. No style profile was created. Figures had no coherent visual identity.
- **Pull**: A style-profile.yaml gate ensures the user either approves a style profile or explicitly opts out. Either way, a conscious decision was made.
- **Anxiety**: What if the proposal has no Nano Banana figures planned and style analysis is genuinely optional? The gate needs an explicit skip mechanism.
- **Habit**: The agent's tendency is to jump straight to generation. Without enforcement, the style conversation is easily skipped because it feels like a delay.

## Outcome Statements

1. Minimize the likelihood that the formatter agent bypasses the figure planning phase
2. Minimize the likelihood that figures are generated without user input on visual style
3. Minimize the number of proposals with inconsistent or low-quality visual assets due to pipeline shortcuts
4. Maximize the confidence that every figure artifact traces back to a specification in figure-specs.md

## Personas

### Persona 1: Dr. Rafael Moreno -- SBIR Principal Investigator

Rafael is the founder and PI at a small defense tech company (8 employees). He is writing a DoD Phase I SBIR proposal for SF25D-T1201 (autonomous sensor fusion). He has limited graphic design skills and relies on the plugin to produce professional figures. He cares deeply about the visual quality of his proposal because reviewers form first impressions from figures. He was frustrated when his last proposal session produced hand-coded SVGs that looked amateurish.

### Persona 2: Phil -- Plugin Maintainer

Phil maintains the SBIR proposal plugin and has observed the formatter agent ignoring markdown instructions during real proposal sessions. He needs enforcement mechanisms that are harder to bypass than agent instructions. He wants PES evaluators (Python code running as hooks) because they operate at a layer the agent cannot override. He values the existing hexagonal architecture pattern and wants new evaluators to follow it exactly.
