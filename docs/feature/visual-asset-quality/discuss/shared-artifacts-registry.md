# Shared Artifacts Registry: Visual Asset Quality

## Artifacts

### style_profile

- **Source of truth**: `{artifact_base}/wave-5-visuals/style-profile.yaml`
- **Consumers**:
  - Step 1 (Style Analysis): created and displayed
  - Step 2 (Prompt Preview): palette and tone injected into engineered prompts
  - Step 4 (Structured Critique): style match category compared against profile
  - Step 7 (Conclude): consistency check verifies all NB figures match profile
- **Owner**: sbir-formatter agent (Wave 5)
- **Integration risk**: HIGH -- palette/tone mismatch between style analysis and prompt engineering produces visually inconsistent figures
- **Validation**: Compare palette hex codes in style-profile.yaml against hex codes embedded in each generated prompt

### solicitation_context

- **Source of truth**: `{state_dir}/solicitation-parsed.md`
- **Consumers**:
  - Step 1 (Style Analysis): agency, domain, topic area extracted for style recommendation
  - Step 2 (Prompt Preview): domain-specific content and terminology in prompts
- **Owner**: sbir-compliance-sheriff agent (Wave 1)
- **Integration risk**: MEDIUM -- if solicitation is re-parsed between style analysis and prompt generation, domain classification could shift
- **Validation**: Verify solicitation_id matches across style-profile.yaml and prompt metadata

### figure_plan

- **Source of truth**: `{artifact_base}/wave-3-outline/figure-plan.md`
- **Consumers**:
  - Step 1 (Style Analysis): enumerates all planned figures
  - Step 2 (Prompt Preview): figure type, section, description per figure
  - Step 7 (Conclude): completeness check -- all planned figures accounted for
- **Owner**: sbir-writer agent (Wave 3)
- **Integration risk**: HIGH -- if figure plan is modified after Wave 5 starts, generated figures may not match updated plan
- **Validation**: Count of figures in plan matches count of approved + deferred figures at conclusion

### engineered_prompt

- **Source of truth**: generated in-memory per figure from style_profile + figure_spec
- **Consumers**:
  - Step 3 (Generate): input to Nano Banana or TikZ generation
  - Step 5 (Refine): baseline for critique-driven adjustments
- **Owner**: sbir-formatter agent (Wave 5)
- **Integration risk**: MEDIUM -- prompt text is ephemeral; refinement modifies it in place
- **Validation**: Prompt hash recorded in figure log for audit; original and refined prompts both logged

### critique_ratings

- **Source of truth**: user input during Step 4 review
- **Consumers**:
  - Step 5 (Refine): categories rated <3 targeted for prompt adjustment
  - Step 7 (Conclude): quality summary aggregates ratings
- **Owner**: Phil (user)
- **Integration risk**: LOW -- ratings are per-figure, consumed in same session
- **Validation**: All 5 categories rated (no nulls); ratings in range 1-5

### generated_figure

- **Source of truth**: `{artifact_base}/wave-5-visuals/{figure-filename}`
- **Consumers**:
  - Step 4 (Critique): displayed for review
  - Step 6 (Approve): final approved file
  - Step 7 (Conclude): consistency check and cross-reference validation
  - Wave 6 (Format/Assembly): inserted at outline position
- **Owner**: sbir-formatter agent (Wave 5)
- **Integration risk**: HIGH -- file path must match figure log entry and cross-reference log
- **Validation**: File exists at recorded path; format matches figure log entry (PNG for NB, PDF/TEX for TikZ, SVG for others)

### quality_summary

- **Source of truth**: `{artifact_base}/wave-5-visuals/quality-summary.md`
- **Consumers**:
  - Wave 6 (Assembly Report): references quality summary for visual asset section
- **Owner**: sbir-formatter agent (Wave 5)
- **Integration risk**: LOW -- produced at conclusion, consumed downstream
- **Validation**: Summary figure count matches figure log count; all statuses are "approved" or "pending-external"

## Integration Checkpoints

| Checkpoint | Between Steps | Validation |
|------------|---------------|------------|
| Style-to-prompt consistency | 1 -> 2 | Palette hex codes in prompt match style-profile.yaml |
| Plan-to-generation completeness | 1 -> 7 | Every planned figure has an approved figure or external brief |
| Prompt-to-critique traceability | 2 -> 4 | Prompt hash in figure log matches generation input |
| Critique-to-refinement targeting | 4 -> 5 | Only categories rated <3 are modified in prompt adjustments |
| Cross-figure style consistency | 7 | All Nano Banana figures use same palette from style-profile.yaml |
| Cross-reference validity | 7 | CrossReferenceLog.all_valid = true |
