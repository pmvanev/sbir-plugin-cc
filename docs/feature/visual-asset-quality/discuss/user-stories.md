<!-- markdownlint-disable MD024 -->

# Visual Asset Quality -- User Stories

## US-VAQ-1: Engineered Prompt Generation for Nano Banana

### Problem

Phil Van Every is a solo SBIR proposal writer who generates concept figures and technical illustrations using Nano Banana (Gemini image generation). He finds it frustrating that the current prompts produce flat, generic-looking images because the plugin sends minimal prompt text without composition, style, labeling, or technical illustration directives. Phil ends up with figures that look like quick AI clip art rather than professional technical illustrations, which hurts his scoring with DoD evaluators who form visual impressions within seconds.

### Who

- Solo SBIR proposal writer | Writing a 25-page technical volume for Navy topic N241-033 | Wants figures that look like they came from a professional illustration firm

### Solution

Enhance the figure generation workflow to construct engineered prompts from figure specifications. Prompts include composition directives, labeled component lists, style parameters, aspect ratio, and explicit avoid instructions. The prompt is shown to Phil before generation so he can review and adjust it.

### Domain Examples

#### 1: Happy Path -- Phil generates a system architecture figure

Phil is generating Figure 3 (System Architecture) for his Navy directed energy proposal. The system constructs a prompt: "Technical illustration of a compact directed energy weapon system architecture. COMPOSITION: Exploded isometric view with three subsystem layers. STYLE: Navy blue (#003366), steel gray (#6B7B8D), clean technical illustration, white background. LABELS: Power Conditioning Unit, Beam Director Assembly, Target Acquisition Sensor, Thermal Management System, C2 Interface, Ship Power Bus 450V DC. AVOID: Photorealistic rendering, unlabeled components, decorative elements. RESOLUTION: 2K, 16:9." Phil reviews, confirms, and the generated image shows clearly labeled subsystems in a professional isometric layout.

#### 2: Edge Case -- Phil edits the prompt before generation

Phil is generating Figure 1 (Operational Scenario) for an Air Force space-based ISR proposal. The system constructs a prompt with aerospace-themed composition. Phil reviews it and adds "Include LEO orbital mechanics arc showing satellite ground track" and changes "white background" to "dark star field background with Earth limb visible." The system regenerates the prompt with his edits and produces an image reflecting both the engineered template and Phil's domain-specific additions.

#### 3: Error/Boundary -- GEMINI_API_KEY not set

Phil runs `/proposal draft figure "deployment-scenario"` for a concept figure. The system detects GEMINI_API_KEY is not set. Instead of failing silently, it displays: "Nano Banana unavailable (GEMINI_API_KEY not set). For concept figures, Nano Banana is the recommended method. Set GEMINI_API_KEY or choose: [switch to SVG] [write external brief]." The engineered prompt is still shown so Phil can use it with an external image generation tool.

### UAT Scenarios (BDD)

#### Scenario: Engineered prompt constructed from figure specification

Given Phil has Figure 3 specified as type "system-diagram" for section 3.1
And the figure description is "Compact DE weapon system architecture for naval integration"
When the system prepares the generation prompt
Then the prompt includes COMPOSITION, STYLE, LABELS, AVOID, and RESOLUTION sections
And the LABELS section lists all components from the figure description
And the RESOLUTION specifies "2K" and the aspect ratio from the figure spec

#### Scenario: Prompt shown to user before generation

Given the engineered prompt for Figure 3 has been constructed
When Phil runs "/proposal draft figure system-architecture"
Then the full prompt text is displayed in the terminal
And Phil is offered: generate, edit prompt, switch method, skip figure
And generation does not begin until Phil confirms

#### Scenario: User edits prompt before generation

Given the engineered prompt for Figure 1 is displayed
When Phil adds "Include LEO orbital arc" to the prompt text
Then the updated prompt includes Phil's addition
And the original engineered sections are preserved
And generation proceeds with the combined prompt

#### Scenario: Prompt includes figure-plan metadata

Given the figure plan specifies Figure 3 cross-references section 3.1 and compliance item R-7
When the system constructs the prompt
Then the prompt content reflects the technical approach described in section 3.1
And the compliance item context is used to ensure relevant elements are included

#### Scenario: Graceful handling when GEMINI_API_KEY not set

Given GEMINI_API_KEY is not set
And Figure 5 is specified with method "nano-banana"
When Phil runs "/proposal draft figure deployment-scenario"
Then the system displays "Nano Banana unavailable" with the reason
And the engineered prompt is shown for external use
And Phil is offered: switch to SVG, write external brief

### Acceptance Criteria

- [ ] Engineered prompts include COMPOSITION, STYLE, LABELS, AVOID, and RESOLUTION sections
- [ ] Prompt is displayed to user before generation begins
- [ ] User can edit the prompt and additions are preserved alongside engineered sections
- [ ] Prompt content reflects figure plan metadata (type, section, compliance items)
- [ ] Graceful fallback with prompt display when GEMINI_API_KEY is not set

### Technical Notes

- Prompt construction is a formatting concern in the sbir-formatter agent and visual-asset-generator skill, not a PES domain model change
- Prompt template structure lives in the skill file; figure-specific content comes from figure plan
- Prompt hash should be recorded in figure log for audit traceability
- No new Python domain objects required; this enhances the agent's prompt crafting behavior

### Dependencies

- Existing figure plan from Wave 3 (already implemented)
- Existing Nano Banana generation script (`scripts/nano-banana-generate.sh`)
- Existing figure specification format in visual-asset-generator skill

### Job Story Trace

- JS-1: Professional Figure Generation (primary)

### MoSCoW: Must Have

---

## US-VAQ-2: Structured Critique and Refinement Loop

### Problem

Phil Van Every is a solo SBIR proposal writer who reviews generated figures before approving them. He finds it inefficient that the current "revise" option is shallow -- he can say "revise" but there is no structured way to articulate what is wrong (composition? labels? scale? accuracy?) and no mechanism for the system to refine the prompt based on his specific feedback. Phil either accepts mediocre figures or abandons the tool to edit images externally, losing the workflow continuity that makes the plugin valuable.

### Who

- Solo SBIR proposal writer | Reviewing Figure 3 (System Architecture) generated via Nano Banana | Wants to converge on a high-quality figure through targeted feedback without leaving the tool

### Solution

Replace the unstructured "revise" option with a structured critique using five categories (composition, labels, accuracy, style match, scale/proportion), each rated 1-5. Categories rated below 3 are flagged. The system translates the critique into specific prompt adjustments, shows the adjustments to Phil, and regenerates. Maximum 3 refinement rounds before offering escape paths (approve, replace method, defer).

### Domain Examples

#### 1: Happy Path -- Phil critiques labels and scale, system refines

Phil reviews Figure 3 (System Architecture, Nano Banana). He rates: composition 4, labels 2, accuracy 4, style match 5, scale 3. Notes: "Labels too small, overlapping on the beam director. Power bus connection not prominent enough." The system prepares adjustments: adds "large clear labels, min 12pt, no overlap, high-contrast label backgrounds" and "power bus as thick bold line with voltage annotation." Removes "10pt labels." Phil approves the adjustments and the system regenerates. Round 2: all categories rate 3+, Phil approves.

#### 2: Edge Case -- Phil approves on first review without refinement

Phil reviews Figure 4 (Project Timeline, Mermaid). He rates all categories 4 or 5. The system highlights "approve as-is" prominently. Phil approves. No refinement loop entered. Total iterations: 0.

#### 3: Error/Boundary -- 3 iterations exhausted without convergence

Phil is refining Figure 6 (Deployment Environment, Nano Banana). After 3 rounds, the labels category is still 2/5 because Gemini keeps rendering overlapping text. The system presents: "Maximum refinement rounds reached. Options: [approve current] [switch to TikZ for precise label control] [defer to external editor] [write external brief]." Phil switches to TikZ, which renders labels precisely.

### UAT Scenarios (BDD)

#### Scenario: Five critique categories presented for each figure

Given Figure 3 has been generated via Nano Banana
When Phil reviews the figure
Then 5 categories are presented: composition, labels, accuracy, style match, scale/proportion
And each category has a description and accepts a 1-5 rating
And a free-text notes field is available

#### Scenario: Low-rated categories flagged for refinement

Given Phil rates labels 2/5 and scale 3/5 for Figure 3
And Phil notes "Labels too small and overlapping"
When Phil submits the critique
Then Labels is flagged for refinement (rated below 3)
And Scale is not flagged (rated 3, threshold boundary)
And the system prepares prompt adjustments targeting Labels only

#### Scenario: Prompt adjustments shown before regeneration

Given Labels is flagged with note "too small, overlapping"
When the system prepares refinement round 1
Then the additions include "large clear labels, no overlap, minimum 12pt"
And the removals include the original small-label instruction
And Phil can edit the adjustments before regeneration

#### Scenario: Refinement preserves well-rated elements

Given Phil rated style match 5/5 and composition 4/5
When the system modifies the prompt for refinement
Then style and composition prompt sections are unchanged
And only label-related sections are modified

#### Scenario: Maximum 3 refinement rounds then escape

Given Phil has completed 3 refinement rounds for Figure 6
When the 3rd iteration result is presented
Then Phil is offered: approve current, replace method, defer to external
And no 4th refinement round is available

#### Scenario: Approve on first review without refinement

Given Phil rates all 5 categories 4 or higher for Figure 4
When Phil submits the critique
Then "approve as-is" is prominently offered
And the system does not require entering the refinement loop

### Acceptance Criteria

- [ ] Five structured critique categories presented for every reviewed figure
- [ ] Categories rated below 3 are flagged for refinement
- [ ] Prompt adjustments derived from critique are shown to user before regeneration
- [ ] Well-rated elements are preserved during prompt modification
- [ ] Maximum 3 refinement iterations with clear escape paths after exhaustion
- [ ] Figures can be approved on first review without entering refinement loop
- [ ] Quality ratings recorded in figure log for each figure

### Technical Notes

- Critique categories and ratings are a user interaction concern in the formatter agent, not a PES domain model change
- The 3-iteration limit is a workflow policy enforced by the agent, not a domain rule
- Prompt adjustment logic lives in the visual-asset-generator skill (addition/removal patterns per category)
- Quality ratings should be persisted to figure log for the Wave 5 quality summary

### Dependencies

- US-VAQ-1 (Engineered Prompt Generation) -- refinement modifies the engineered prompt
- Existing figure review checkpoint in sbir-formatter agent

### Job Story Trace

- JS-2: Iterative Figure Refinement (primary)

### MoSCoW: Must Have

---

## US-VAQ-3: Domain-Aware Visual Style Intelligence

### Problem

Phil Van Every is a solo SBIR proposal writer who generates figures across proposals targeting different agencies and domains (Navy maritime, Air Force space, Army ground, DARPA advanced tech). He finds it time-consuming and risky that the current workflow applies the same generic "clean, professional, white background" style to every proposal regardless of domain. A Navy evaluator expects different visual language than an Air Force evaluator, and Phil has to manually think through appropriate styles without tool support, risking generic-looking figures that don't signal domain expertise.

### Who

- Solo SBIR proposal writer | Starting Wave 5 for a Navy directed energy proposal (N241-033) | Wants figures that feel native to the evaluator's domain without manually researching visual conventions

### Solution

Add a style analysis step at the start of Wave 5 that reads the solicitation context (agency, domain, topic area), recommends a visual style profile (palette, tone, detail level, avoid list), and persists the profile for use in all subsequent prompt engineering. Phil reviews and can adjust the style. The style profile applies automatically to all Nano Banana prompts in the proposal.

### Domain Examples

#### 1: Happy Path -- Navy directed energy proposal style

Phil starts Wave 5 for topic N241-033 (Navy, Directed Energy Systems). The system reads the solicitation, identifies the domain as "maritime/naval defense," and recommends: palette navy blue (#003366), steel gray (#6B7B8D), signal orange (#FF6B35), ocean teal (#2B7A8C); tone "technical-authoritative, clean sightlines"; detail level "high"; avoid "cartoon/sketch style, excessive gradients." Phil approves, adjusting ocean teal to a darker shade. All subsequent Nano Banana prompts use this palette.

#### 2: Edge Case -- Air Force space-based ISR proposal style

Phil starts Wave 5 for topic AF242-015 (Air Force, Space-Based ISR). The system recommends: palette midnight blue (#191970), silver (#C0C0C0), electric blue (#0047AB), accent gold (#FFD700); tone "precision-aerospace, high-contrast on dark backgrounds allowed for space scenes"; detail level "high"; avoid "ground-centric imagery, atmospheric effects." Phil notes this is unusual (dark backgrounds in a government proposal) and adjusts tone to "clean white background with aerospace color accents." The system updates the profile.

#### 3: Error/Boundary -- Unknown agency with generic fallback

Phil starts Wave 5 for a NIST solicitation (rare for SBIR). The system cannot identify a domain-specific style convention. It displays: "Agency NIST not in style database. Recommending generic professional style: blue/gray palette, neutral tone, medium detail. You can adjust or provide style preferences." Phil provides: "Research-academic tone, muted palette, data visualization emphasis." The system creates a custom profile.

### UAT Scenarios (BDD)

#### Scenario: Style recommended from solicitation analysis

Given Phil has a solicitation for Navy directed energy systems (N241-033)
And the figure plan contains 6 planned figures
When Phil runs "/proposal wave visuals"
Then the system recommends a "maritime/naval" visual style
And the palette includes navy blue (#003366) and steel gray (#6B7B8D)
And the tone is "technical-authoritative"
And the detail level is "high"

#### Scenario: Phil adjusts recommended palette

Given the system recommended a maritime/naval palette with ocean teal (#2B7A8C)
When Phil selects "adjust palette" and replaces ocean teal with dark teal (#1A5F6D)
Then the style profile is updated with the new color
And subsequent Nano Banana prompts use dark teal instead of ocean teal

#### Scenario: Style profile persists across all figures in proposal

Given Phil approved the maritime/naval style profile
When Phil generates Figure 1, Figure 3, and Figure 6 via Nano Banana
Then all three engineered prompts include the same palette colors
And all three prompts include the same tone directive

#### Scenario: Unknown agency falls back to generic style

Given Phil has a solicitation from NIST (not in style database)
When Phil runs "/proposal wave visuals"
Then the system recommends a generic professional style
And displays "Agency NIST not in style database"
And Phil can provide custom style preferences

#### Scenario: Style analysis optional for non-NB methods

Given all figures in the plan use Mermaid or SVG generation
When Phil runs "/proposal wave visuals"
Then style analysis is offered but marked as optional
And Phil can proceed without creating a style profile

### Acceptance Criteria

- [ ] Style analysis reads solicitation agency and domain to recommend a visual style
- [ ] Style profile includes palette (hex colors), tone, detail level, and avoid list
- [ ] Phil can review and adjust every aspect of the style profile
- [ ] Approved style profile persists and applies to all Nano Banana prompts in the proposal
- [ ] Unknown agencies fall back to generic professional style with option for custom input
- [ ] Style analysis is optional when no Nano Banana figures are planned

### Technical Notes

- Style profile is a YAML file at `{artifact_base}/wave-5-visuals/style-profile.yaml`
- Style database is domain knowledge in the visual-asset-generator skill, not a separate data store
- Style recommendation logic is inference by the formatter agent based on solicitation keywords, not a lookup table
- The style profile is a new shared artifact that the skill documents

### Dependencies

- Solicitation parsing (already implemented in compliance-sheriff Wave 1)
- US-VAQ-1 (Engineered Prompt Generation) -- style profile feeds into prompt construction

### Job Story Trace

- JS-3: Domain-Aware Visual Style (primary)
- JS-1: Professional Figure Generation (secondary -- style feeds prompt quality)

### MoSCoW: Should Have

---

## US-VAQ-4: TikZ Generation for LaTeX Proposals

### Problem

Phil Van Every is a solo SBIR proposal writer who uses LaTeX for some proposals. He finds it visually jarring that even in LaTeX proposals, all diagrams are embedded as raster PNGs or external SVGs that don't match the document's typography. The fonts are different, the scaling is fixed, and the figures look like foreign objects pasted into an otherwise unified document. For technical diagrams (system architectures, block diagrams, flowcharts), the visual mismatch undermines the impression of a polished, technically sophisticated proposal.

### Who

- Solo SBIR proposal writer | Generating Figure 2 (System Block Diagram) for a LaTeX-format Navy proposal | Wants vector-sharp diagrams that compile natively with the document and match its typographic system

### Solution

Add TikZ/PGF as a generation method for diagram-type figures when the proposal uses LaTeX format and a LaTeX compiler (pdflatex, xelatex, or lualatex) is detected. The system generates TikZ code, compiles it to verify correctness, renders a PDF preview, and saves both the .tex source and the preview. If compilation fails, the system shows the error and offers fallback to SVG.

### Domain Examples

#### 1: Happy Path -- Phil generates a block diagram as TikZ

Phil is generating Figure 2 (System Block Diagram) for his LaTeX-format Navy proposal. The system offers both Nano Banana and TikZ. Phil selects TikZ. The system generates TikZ code with nodes for each subsystem, arrows for data flow, and labels matching the document's font. pdflatex compiles the code with 0 errors. Phil sees a PDF preview showing crisp vector graphics with fonts matching his proposal text. He approves.

#### 2: Edge Case -- TikZ compilation fails, SVG fallback offered

Phil selects TikZ for Figure 5 (Complex Process Flow). The generated TikZ code has a syntax error in a nested scope. pdflatex reports "Missing } inserted" at line 47. The system shows Phil the error, highlights the problematic line, and offers: "edit TikZ source" (for Phil to fix), "switch to SVG" (automatic fallback), "defer to external." Phil chooses SVG fallback and the system generates an SVG version of the same diagram.

#### 3: Error/Boundary -- No LaTeX compiler detected

Phil's proposal is set to LaTeX format but no LaTeX compiler is installed (pdflatex, xelatex, lualatex all missing). When Phil views the method options for a diagram figure, TikZ is listed as "unavailable (no LaTeX compiler detected)." The system recommends SVG or Mermaid instead and notes: "Install pdflatex to enable TikZ generation. See /proposal setup for installation help."

### UAT Scenarios (BDD)

#### Scenario: TikZ offered for diagram figures in LaTeX proposals

Given the proposal format is LaTeX
And pdflatex is available
And Figure 2 is type "block-diagram"
When Phil views generation options for Figure 2
Then TikZ is listed as an available method alongside Nano Banana, SVG, and Mermaid

#### Scenario: TikZ code generated and compiled successfully

Given Phil selected TikZ for Figure 2 "System Block Diagram"
When the system generates TikZ code
Then pdflatex compiles the code with 0 errors and 0 warnings
And a PDF preview is rendered at `wave-5-visuals/system-block-diagram.pdf`
And the .tex source is saved at `wave-5-visuals/system-block-diagram.tex`
And Phil reviews the PDF preview in the standard critique flow

#### Scenario: TikZ compilation error with fallback

Given Phil selected TikZ for Figure 5
When the generated TikZ code fails to compile
Then the compilation error message and line number are displayed
And Phil is offered: edit TikZ source, switch to SVG, defer to external
And no broken figure file is written to artifacts

#### Scenario: TikZ unavailable when no LaTeX compiler detected

Given the proposal format is LaTeX
And no LaTeX compiler is detected (pdflatex, xelatex, lualatex all absent)
When Phil views generation options for Figure 2
Then TikZ is listed as "unavailable (no LaTeX compiler detected)"
And alternative methods (SVG, Mermaid, Nano Banana) are available
And a note references "/proposal setup" for installation help

#### Scenario: TikZ not offered for non-LaTeX proposals

Given the proposal format is DOCX
When Phil views generation options for Figure 2
Then TikZ is not listed as a generation method
And SVG, Mermaid, and Nano Banana are available

### Acceptance Criteria

- [ ] TikZ listed as generation method for diagram-type figures when LaTeX format and compiler detected
- [ ] Generated TikZ code is compiled and verified before presenting to user
- [ ] Both .tex source and PDF preview saved to wave-5-visuals directory
- [ ] Compilation errors displayed with line numbers and fallback options offered
- [ ] TikZ marked unavailable with helpful message when no LaTeX compiler detected
- [ ] TikZ not offered for non-LaTeX proposal formats

### Technical Notes

- TikZ generation is a new generation method routed in the formatter agent, alongside existing SVG, Mermaid, Graphviz, chart, and Nano Banana
- Compilation verification requires invoking the detected LaTeX compiler (pdflatex/xelatex/lualatex) as a subprocess
- LaTeX compiler detection already exists from the "LaTeX Detection in Setup" feature -- reuse that detection
- The PES domain model's `FigurePlaceholder.generation_method` needs "tikz" as an allowed value
- `FigureGenerator` port may need a `generate_tikz(placeholder) -> str` method, or TikZ generation can be routed through the existing `generate_svg` with format detection
- TikZ figures enter the same critique/refinement loop as other figures via PDF preview

### Dependencies

- LaTeX compiler detection (already implemented in first-time setup)
- US-VAQ-2 (Structured Critique) -- TikZ figures go through the same critique loop
- Proposal format selection (already implemented)

### Job Story Trace

- JS-4: Native LaTeX Figure Integration (primary)

### MoSCoW: Should Have

---

## US-VAQ-5: Wave 5 Quality Summary and Style Consistency

### Problem

Phil Van Every is a solo SBIR proposal writer who generates 4-8 figures per proposal across different methods (Nano Banana, TikZ, Mermaid, SVG). He finds it uncertain whether his figures form a visually coherent set because there is no cross-figure quality assessment or style consistency check. He reviews each figure individually but never sees the big picture -- do the Nano Banana figures all use the same palette? Are there quality outliers that drag down the proposal's visual impression? Phil only discovers inconsistencies when he sees the assembled document in Wave 6, when rework is expensive.

### Who

- Solo SBIR proposal writer | Completing Wave 5 with 6 approved figures across 3 generation methods | Wants confidence that the figure set is visually coherent before entering Wave 6 assembly

### Solution

Add a quality summary step at the conclusion of Wave 5 that aggregates critique ratings, verifies style consistency across Nano Banana figures (all use approved palette from style profile), validates cross-references, and presents a summary table. Flag any inconsistencies so Phil can address them before Wave 6.

### Domain Examples

#### 1: Happy Path -- All figures consistent, quality summary clean

Phil has approved 6 figures: 3 via Nano Banana (all using maritime/naval style), 1 via TikZ, 2 via Mermaid. The quality summary shows average quality 4.2/5 across critiqued figures (NB and TikZ), style consistency PASS, cross-references all valid. Phil proceeds to Wave 6 with confidence.

#### 2: Edge Case -- Style inconsistency detected

Phil approved Figure 6 (Deployment Environment) after changing the palette mid-proposal. The quality summary shows style consistency WARN: "Figure 6 uses updated palette (#1A5F6D) vs. original approved palette (#2B7A8C)." Phil is offered to regenerate Figure 6 with the original palette or accept the inconsistency.

#### 3: Error/Boundary -- Quality outlier flagged

Phil rushed through Figure 5, approving with composition rated 2/5. The quality summary flags Figure 5 as a quality outlier: "Figure 5 has composition 2/5 -- below the proposal average of 4.0. Consider reopening critique." Phil reopens the critique and refines Figure 5.

### UAT Scenarios (BDD)

#### Scenario: Quality summary displayed after all figures approved

Given all 6 figures have been approved
When the system produces the Wave 5 summary
Then a table shows each figure's title, method, iteration count, quality rating, and status
And the average quality score across critiqued figures is displayed
And cross-reference validation status is shown

#### Scenario: Style consistency check across Nano Banana figures

Given 3 figures were generated via Nano Banana
And the approved style profile has palette "#003366, #6B7B8D, #FF6B35, #2B7A8C"
When the system checks style consistency
Then all 3 NB figure prompts are verified against the approved palette
And style consistency is "PASS" if all match

#### Scenario: Style inconsistency flagged

Given Figure 6 was regenerated after a palette adjustment
And its prompt uses "#1A5F6D" instead of the approved "#2B7A8C"
When the system checks style consistency
Then style consistency is "WARN" for Figure 6
And Phil is offered to regenerate with the original approved palette

#### Scenario: Quality outlier flagged

Given Figure 5 was approved with composition rated 2/5
And the average composition across other figures is 4.2
When the system produces the quality summary
Then Figure 5 is flagged as a quality outlier
And Phil is offered to reopen critique for Figure 5

### Acceptance Criteria

- [ ] Quality summary table shows all figures with method, iterations, quality ratings, and status
- [ ] Style consistency verified across all Nano Banana figures against approved style profile
- [ ] Style inconsistencies flagged with specific figure and color mismatch details
- [ ] Quality outliers (any category 2+ points below average) flagged with reopen option
- [ ] Cross-reference validation included in summary (all_valid status)
- [ ] Summary persisted to `wave-5-visuals/quality-summary.md`

### Technical Notes

- Quality summary is a new output of the formatter agent at Wave 5 conclusion, not a PES domain model change
- Style consistency checking compares prompt metadata (stored in figure log) against style-profile.yaml
- Quality outlier detection is a simple threshold: any category rated 2+ points below the proposal average
- This step runs automatically after the last figure is approved, before the Wave 5 checkpoint

### Dependencies

- US-VAQ-2 (Structured Critique) -- quality ratings are the input for this summary
- US-VAQ-3 (Style Intelligence) -- style profile is the baseline for consistency checking
- Existing cross-reference validation in VisualAssetService

### Job Story Trace

- JS-1: Professional Figure Generation (secondary -- quality assurance)
- JS-3: Domain-Aware Visual Style (secondary -- consistency verification)

### MoSCoW: Should Have

---

## Definition of Ready Validation

### US-VAQ-1: Engineered Prompt Generation

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Phil's frustration with flat, generic Nano Banana output described in domain language |
| User/persona identified | PASS | Solo SBIR writer, Navy N241-033, needs professional illustrations |
| 3+ domain examples | PASS | 3 examples: happy path (system architecture), edge (prompt editing), error (no API key) |
| UAT scenarios (3-7) | PASS | 5 scenarios covering prompt construction, preview, editing, metadata, and error handling |
| AC derived from UAT | PASS | 5 AC items mapped from scenarios |
| Right-sized | PASS | Estimated 2-3 days, 5 scenarios, single demonstrable feature |
| Technical notes | PASS | Skill-level change, prompt hash audit, no new domain objects |
| Dependencies tracked | PASS | Figure plan (implemented), nano-banana script (implemented) |

### DoR Status: PASSED

---

### US-VAQ-2: Structured Critique and Refinement Loop

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Shallow revision, no structured feedback, Phil abandons tool for external editing |
| User/persona identified | PASS | Solo SBIR writer reviewing Figure 3 via Nano Banana |
| 3+ domain examples | PASS | 3 examples: labels/scale critique, first-review approval, max iterations exhausted |
| UAT scenarios (3-7) | PASS | 6 scenarios covering categories, flagging, adjustments, preservation, max iterations, first-approve |
| AC derived from UAT | PASS | 7 AC items mapped from scenarios |
| Right-sized | PASS | Estimated 2-3 days, 6 scenarios, single demonstrable feature |
| Technical notes | PASS | Agent workflow policy, skill-level adjustment patterns, figure log persistence |
| Dependencies tracked | PASS | US-VAQ-1 (prompt engineering), existing review checkpoint |

### DoR Status: PASSED

---

### US-VAQ-3: Domain-Aware Visual Style Intelligence

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Generic style across all proposals, manual style thinking, domain mismatch risk |
| User/persona identified | PASS | Solo SBIR writer starting Wave 5 for Navy DE proposal |
| 3+ domain examples | PASS | 3 examples: Navy maritime, Air Force aerospace, unknown NIST fallback |
| UAT scenarios (3-7) | PASS | 5 scenarios covering recommendation, adjustment, persistence, fallback, optional skip |
| AC derived from UAT | PASS | 6 AC items mapped from scenarios |
| Right-sized | PASS | Estimated 2 days, 5 scenarios, single demonstrable feature |
| Technical notes | PASS | YAML style profile, skill-level domain knowledge, agent inference |
| Dependencies tracked | PASS | Solicitation parsing (implemented), US-VAQ-1 (prompt feeds style) |

### DoR Status: PASSED

---

### US-VAQ-4: TikZ Generation for LaTeX Proposals

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Raster/SVG figures look foreign in LaTeX documents, font/scale mismatch |
| User/persona identified | PASS | Solo SBIR writer generating block diagram for LaTeX Navy proposal |
| 3+ domain examples | PASS | 3 examples: successful TikZ compile, compilation failure with fallback, no compiler detected |
| UAT scenarios (3-7) | PASS | 5 scenarios covering TikZ offering, compilation, error handling, unavailable, non-LaTeX |
| AC derived from UAT | PASS | 6 AC items mapped from scenarios |
| Right-sized | PASS | Estimated 2-3 days, 5 scenarios, single demonstrable feature |
| Technical notes | PASS | New generation method, compiler subprocess, reuse setup detection, domain model extension |
| Dependencies tracked | PASS | LaTeX detection (implemented), US-VAQ-2 (critique loop), format selection (implemented) |

### DoR Status: PASSED

---

### US-VAQ-5: Wave 5 Quality Summary and Style Consistency

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | No cross-figure quality assessment, style inconsistencies discovered at Wave 6 |
| User/persona identified | PASS | Solo SBIR writer completing Wave 5 with 6 figures across 3 methods |
| 3+ domain examples | PASS | 3 examples: clean summary, style inconsistency, quality outlier |
| UAT scenarios (3-7) | PASS | 4 scenarios covering summary, consistency pass, consistency warn, outlier flagging |
| AC derived from UAT | PASS | 6 AC items mapped from scenarios |
| Right-sized | PASS | Estimated 1-2 days, 4 scenarios, single demonstrable feature |
| Technical notes | PASS | Formatter agent output, prompt metadata comparison, threshold detection |
| Dependencies tracked | PASS | US-VAQ-2 (ratings input), US-VAQ-3 (style profile baseline), existing xref validation |

### DoR Status: PASSED
