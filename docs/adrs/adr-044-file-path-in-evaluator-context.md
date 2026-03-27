# ADR-044: Passing File Path to Evaluators via Tool Context Parameter

## Status

Accepted

## Context

Existing evaluators receive `(rule, state, tool_name)` in their `triggers()` method. The five existing evaluators (wave_ordering, pdc_gate, deadline_blocking, submission_immutability, corpus_integrity) only need `tool_name` to match against wave patterns or tool categories.

The two new evaluators (figure_pipeline_gate, style_profile_gate) need the `file_path` of the Write/Edit target to determine:

1. Whether the target is in a `wave-5-visuals/` directory
2. Whether the target IS a prerequisite file (figure-specs.md, style-profile.yaml)
3. Where to check for prerequisite artifact existence on disk

The file_path is already available in the hook input at `hook_input["tool"]["file_path"]` -- it is extracted for PostToolUse but not passed through PreToolUse to the engine.

A secondary concern: the evaluators need to check whether prerequisite files exist on disk. Evaluators are pure domain objects with no infrastructure imports. File existence checking is an infrastructure concern.

## Decision

**Part 1 -- File path delivery**: Add a `tool_context` dict parameter to `engine.evaluate()` and pass it through to `_rule_triggers()` and then to `evaluator.triggers()`. The hook adapter extracts file_path from hook_input and passes it as `tool_context={"file_path": file_path}`. Existing evaluators ignore the new parameter (Python allows extra `**kwargs` or the parameter can have a default value).

**Part 2 -- Artifact existence**: Pass artifact existence information in `tool_context` as well. The hook adapter resolves the artifact directory from the file_path and checks for prerequisite files, adding `{"artifacts_present": ["figure-specs.md"]}` (or empty list) to tool_context. This keeps filesystem access in the adapter layer while giving evaluators the data they need as plain values.

## Alternatives Considered

### Alternative 1: Inject file_path into state dict

- **Evaluation**: Least code change -- add `state["_tool_file_path"] = file_path` in the hook adapter before calling evaluate. Evaluators read it from state like any other field.
- **Rejection**: state dict represents proposal state (persistent domain data). Mixing transient per-invocation tool data into it violates the state dict's semantic contract. Future evaluators might accidentally persist or log file_path as state. Underscore prefix is a convention smell.

### Alternative 2: Encode file_path in rule condition

- **Evaluation**: Put path patterns in pes-config.json rule conditions. Evaluator matches file_path against patterns from the rule.
- **Rejection**: file_path comes from the hook event, not from configuration. Rules define WHEN to enforce, not WHERE the tool is writing. This conflates configuration-time patterns with runtime context. Also does not solve the artifact existence check problem.

### Alternative 3: Evaluator port for filesystem access

- **Evaluation**: Create an ArtifactExistencePort interface injected into evaluators. Evaluators call `port.exists("figure-specs.md")` to check prerequisites.
- **Rejection**: Overcomplicated for a boolean check. Every evaluator would need constructor injection, changing the simple `_evaluators` dict from instances to a factory pattern. The engine would need to manage port lifecycle. The two new evaluators are the only ones that need this, and the information is simple enough to pass as data.

## Consequences

- Positive: Evaluator interface gains extensibility for future path-aware rules without further changes
- Positive: Artifact existence stays in adapter layer (pure domain evaluators)
- Positive: Existing evaluators unaffected (default parameter value)
- Negative: `triggers()` signature grows by one parameter -- acceptable for 7 evaluators
- Negative: Hook adapter takes on artifact directory resolution logic -- but it already resolves workspace context
