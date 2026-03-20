# JTBD Analysis: Visual Asset Quality

## Job Classification

**Job Type**: Brownfield Improvement (Job 2)
**Rationale**: Phil knows what needs to change -- the existing Wave 5 visual asset pipeline produces low-quality figures that hurt proposal scoring. The system is understood, the problems are identified, and the desired outcomes are clear.

**Workflow**: `[research] -> discuss -> design -> distill -> deliver`
**Note**: Discovery phase included because the improvement touches multiple concerns (prompt engineering, iteration workflow, style intelligence, TikZ generation) requiring requirements elicitation before architecture.

---

## Job Stories

### JS-1: Professional Figure Generation

**When** I am generating concept figures and technical illustrations for a DoD SBIR proposal using Nano Banana,
**I want to** produce images that look like they came from a professional technical illustration firm,
**so I can** score well on the visual impression evaluators form within seconds of opening my proposal.

#### Functional Job
Generate publication-quality technical illustrations from text prompts that convey complex engineering concepts clearly and professionally.

#### Emotional Job
Feel proud of my proposal's visual quality rather than embarrassed by flat, generic-looking AI images that signal low effort.

#### Social Job
Be perceived by DoD evaluators as a serious, competent proposer who invests in clear communication -- not someone who pasted in quick AI clip art.

#### Forces Analysis

**Demand-Generating**
- **Push**: Current Nano Banana prompts produce flat, generic images. Phil sees the gap between what Gemini can produce with good prompts and what the plugin sends. The images look like they were generated in 5 seconds because they were. Evaluators form visual impressions in the first page scan.
- **Pull**: Engineered prompts that specify lighting, composition, labeling, perspective, and domain-appropriate style would produce figures rivaling professional illustration firms. Gemini is capable -- the prompts are the bottleneck.

**Demand-Reducing**
- **Anxiety**: What if heavily-engineered prompts still produce inconsistent results? What if Phil invests time in prompt tuning and the output is still not good enough for DoD evaluators?
- **Habit**: The current approach "works" -- it produces an image that fills the placeholder. Phil has been manually tweaking images outside the tool or accepting mediocre quality because the iteration cost is high.

**Assessment**
- Switch likelihood: HIGH
- Key blocker: Anxiety about prompt engineering reliability
- Key enabler: Strong push -- Phil sees the quality gap every proposal cycle
- Design implication: Prompt templates must be domain-aware and produce consistently professional results. The system should show Phil the prompt before generating so he can verify and adjust.

---

### JS-2: Iterative Figure Refinement

**When** I receive a generated figure that has errors, quality issues, or doesn't match my vision,
**I want to** critique what's wrong and have the system refine the image based on my feedback,
**so I can** converge on a high-quality figure without starting from scratch each time or switching to an external tool.

#### Functional Job
Iterate on generated figures through a structured critique-and-refine loop until the figure meets proposal quality standards.

#### Emotional Job
Feel in control of the creative process rather than stuck with "take it or leave it" on the first generation attempt.

#### Social Job
Produce figures that reflect the care and attention that evaluators expect from a serious proposer.

#### Forces Analysis

**Demand-Generating**
- **Push**: The current workflow offers "revise" but it is shallow -- there is no structured critique, no prompt refinement, no progressive improvement. Phil either accepts a mediocre image or abandons the tool entirely and uses an external editor. The "revise" option regenerates without learning from what went wrong.
- **Pull**: A critique loop where Phil says "the phased array is too small, the beam angle is wrong, add component labels" and the system incorporates that feedback into a refined prompt would dramatically reduce time-to-quality.

**Demand-Reducing**
- **Anxiety**: Iteration loops could become time sinks. What if 5 iterations still don't produce what Phil needs? The fear of an infinite loop where each revision introduces new problems.
- **Habit**: Phil currently handles revisions by exporting the image and editing in an external tool, or by accepting "good enough" to stay on schedule.

**Assessment**
- Switch likelihood: HIGH
- Key blocker: Iteration becoming a time sink
- Key enabler: Push is very strong -- current "revise" is functionally broken for quality work
- Design implication: Limit iterations (suggest max 3 before offering alternative paths). Structured critique categories (composition, labeling, scale, style, accuracy). Each iteration preserves what worked.

---

### JS-3: Domain-Aware Visual Style

**When** I am starting figure generation for a new proposal targeting a specific agency and domain,
**I want to** have the system analyze my solicitation and proposal context to recommend appropriate visual styles,
**so I can** produce figures that feel native to the evaluator's domain rather than generic across all proposals.

#### Functional Job
Determine the appropriate visual style (color palette, illustration style, technical detail level, aesthetic tone) based on the solicitation's agency, domain, and technical context.

#### Emotional Job
Feel confident that my figures will resonate with the specific audience rather than worrying that a Navy evaluator is seeing the same generic style as an Air Force proposal.

#### Social Job
Signal domain expertise through visual language -- a directed energy proposal should look different from a biomedical device proposal.

#### Forces Analysis

**Demand-Generating**
- **Push**: Currently all Nano Banana prompts use the same generic "clean, professional, white background" style regardless of whether the proposal targets Navy shipboard systems, Air Force space platforms, or Army ground vehicles. Phil manually thinks about style but the tool doesn't help.
- **Pull**: A style intelligence layer that reads the solicitation, identifies the domain (maritime, aerospace, ground, cyber, medical), and recommends visual characteristics (color palettes, illustration styles, technical detail levels) that match evaluator expectations.

**Demand-Reducing**
- **Anxiety**: What if the style recommendations are wrong or stereotypical? A Navy proposal doesn't need to be all blue. Over-stylization could look gimmicky.
- **Habit**: Phil has developed intuitions about what "looks right" for different agencies over years of proposal writing. He may not trust automated style recommendations.

**Assessment**
- Switch likelihood: MEDIUM-HIGH
- Key blocker: Trust in automated style recommendations
- Key enabler: The push of generic-looking figures across different domains
- Design implication: Style should be a recommendation that Phil reviews and adjusts, not an automatic application. Show the style rationale. Allow Phil to set style preferences that persist across a proposal's figures.

---

### JS-4: Native LaTeX Figure Integration

**When** I am producing a LaTeX-format proposal that includes diagrams and technical figures,
**I want to** generate figures as TikZ code that compiles natively in my LaTeX document,
**so I can** have vector-sharp figures that match my document's typography and scale perfectly at any resolution.

#### Functional Job
Generate TikZ/PGF code for diagrams and technical figures that compile natively within LaTeX documents, producing vector graphics that integrate seamlessly with the document's typographic system.

#### Emotional Job
Feel that the figures are first-class citizens of the document rather than imported foreign objects that don't quite match the text around them.

#### Social Job
Present proposals where figures and text form a unified, polished whole -- the hallmark of a technically sophisticated proposer.

#### Forces Analysis

**Demand-Generating**
- **Push**: Currently, even in LaTeX proposals, figures are raster PNGs or SVGs embedded as external files. They don't match the document's fonts, their resolution is fixed, and they look different from the surrounding text. This is particularly jarring for technical diagrams (system architectures, block diagrams, flowcharts) where the visual mismatch is obvious.
- **Pull**: TikZ produces native vector graphics compiled by the same LaTeX engine. Fonts match. Scaling is infinite. The result looks like it was hand-crafted by someone who cares about typographic quality.

**Demand-Reducing**
- **Anxiety**: TikZ code generation could produce compilation errors that are hard to debug. Claude may generate TikZ that doesn't compile, and Phil would need TikZ expertise to fix it.
- **Habit**: SVG/PNG figures work. They may not be perfect, but they don't risk compilation failures. Phil knows how to replace a PNG; debugging TikZ errors is harder.

**Assessment**
- Switch likelihood: MEDIUM
- Key blocker: TikZ compilation reliability anxiety
- Key enabler: The visual quality difference between native TikZ and embedded raster images in LaTeX
- Design implication: TikZ generation must include compilation verification. Generate, compile, verify, present. If compilation fails, offer SVG fallback. Show Phil a rendered preview before he commits to TikZ.

---

## 8-Step Universal Job Map

Applied to the overarching job: "Produce high-quality visual assets for SBIR proposals."

| Step | Current State | Desired State | Gap |
|------|--------------|---------------|-----|
| 1. **Define** | Figure plan exists from Wave 3 with types and methods | Figure plan also captures style intent, domain context, and quality expectations per figure | No style or quality metadata in figure plan |
| 2. **Locate** | Tool availability check (mmdc, dot, python3, GEMINI_API_KEY) | Also analyze solicitation for domain, agency, visual conventions; locate relevant style references | No domain analysis or style reference gathering |
| 3. **Prepare** | Figure specification written with type, method, caption | Specification also includes engineered prompt, style parameters, TikZ option for LaTeX, quality criteria | Specifications lack prompt engineering and style |
| 4. **Confirm** | User reviews figure plan and approves methods | User also reviews and adjusts style recommendations and prompt drafts before generation | No prompt or style preview before generation |
| 5. **Execute** | Generate figure, write to artifacts directory | Generate with engineered prompt, apply domain style, offer TikZ for LaTeX, produce high-quality output | Generic prompts, no TikZ, no style application |
| 6. **Monitor** | Present figure for human review (approve/revise/replace) | Structured critique with categories; show what the prompt was so user can target feedback | Review is unstructured; prompt not visible |
| 7. **Modify** | "Revise" regenerates without structured feedback loop | Critique-refine loop: user identifies issues by category, system refines prompt, regenerates, compares | Revision is shallow, no prompt refinement |
| 8. **Conclude** | Figure approved, cross-references validated | Quality assessment recorded; style consistency verified across all figures; lessons captured for next proposal | No quality tracking or cross-figure consistency |

---

## Outcome Statements and Opportunity Scoring

Source: Phil's described problems + job analysis above. Ratings are owner estimates (N=1, Phil).

| # | Outcome Statement | Imp. | Sat. | Score | Priority |
|---|-------------------|------|------|-------|----------|
| 1 | Minimize the likelihood of generating flat, generic-looking proposal figures | 95% | 15% | 17.5 | Extremely Underserved |
| 2 | Minimize the number of iterations needed to reach an acceptable figure | 90% | 20% | 16.0 | Extremely Underserved |
| 3 | Minimize the time to determine the appropriate visual style for a proposal domain | 80% | 10% | 14.8 | Underserved |
| 4 | Maximize the likelihood that LaTeX proposals have natively integrated vector figures | 70% | 0% | 14.0 | Underserved |
| 5 | Minimize the likelihood of accepting a figure with uncritiqued quality issues | 85% | 25% | 13.5 | Underserved |
| 6 | Minimize the time to refine a figure based on specific feedback | 85% | 20% | 13.5 | Underserved |
| 7 | Maximize the likelihood that all figures in a proposal share a consistent visual style | 75% | 15% | 13.5 | Underserved |
| 8 | Minimize the likelihood of TikZ compilation errors blocking proposal assembly | 60% | 0% | 12.0 | Underserved |
| 9 | Minimize the time to set up visual style parameters for a new proposal | 65% | 25% | 10.5 | Appropriately Served |
| 10 | Maximize the likelihood that figure captions and numbering are correct | 80% | 70% | 9.0 | Overserved |

### Scoring Method
- Importance: Phil's assessment of how much this matters for proposal success (0-100%)
- Satisfaction: Phil's assessment of how well the current system serves this need (0-100%)
- Score: Importance + max(0, Importance - Satisfaction)
- Data quality: owner estimate (N=1), directional only

### Top Opportunities (Score >= 12)

1. **Professional figure quality** (17.5) -- Prompt engineering for Nano Banana
2. **Iteration efficiency** (16.0) -- Structured critique-and-refine loop
3. **Domain-appropriate style** (14.8) -- Solicitation-aware style intelligence
4. **Native LaTeX figures** (14.0) -- TikZ generation method
5. **Quality critique coverage** (13.5) -- Structured review categories
6. **Feedback-driven refinement** (13.5) -- Prompt refinement from critique
7. **Cross-figure style consistency** (13.5) -- Style persisted across proposal figures
8. **TikZ compilation reliability** (12.0) -- Compile-verify-present workflow

### Overserved Areas (Score < 10)

1. **Caption/numbering correctness** (9.0) -- Current system handles this well via CrossReferenceLog validation. No additional investment needed.

---

## Job-to-Story Mapping Preview

| Job Story | Mapped User Stories (Phase 4) |
|-----------|------------------------------|
| JS-1: Professional Figure Generation | US-1 (Prompt Engineering), US-3 (Style Intelligence) |
| JS-2: Iterative Figure Refinement | US-2 (Critique-Refine Loop) |
| JS-3: Domain-Aware Visual Style | US-3 (Style Intelligence) |
| JS-4: Native LaTeX Figure Integration | US-4 (TikZ Generation) |
