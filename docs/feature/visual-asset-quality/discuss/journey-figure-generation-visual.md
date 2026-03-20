# Journey: High-Quality Figure Generation

## Overview

Phil generates visual assets for an SBIR proposal. The journey spans from solicitation analysis through final approved figures, incorporating domain-aware style, engineered prompts, structured critique, and optional TikZ generation for LaTeX.

## Emotional Arc

```
Confidence
  ^
  |                                              *  Proud/Satisfied
  |                                           *     (all figures approved,
  |                                        *         consistent style)
  |                                     *
  |                     *  *  *  *  *     Engaged/In-Control
  |                  *                    (critique loop, convergence)
  |               *
  |            *   Focused/Curious
  |         *     (style review, prompt preview)
  |      *
  |   *  Cautious/Hopeful
  |  *   (new workflow, will it work?)
  +-----------------------------------------------------------> Steps
     1        2        3        4        5        6        7
   Style   Prompt   Generate  Critique  Refine  Approve  Conclude
  Analysis Preview            & Rate    & Regen
```

**Start**: Cautious/Hopeful -- Phil is starting a new visual workflow, uncertain whether it will produce better results than before.
**Middle**: Focused/Engaged -- Phil sees the style recommendations, reviews the prompt, and enters an iterative critique loop where each round shows visible improvement.
**End**: Proud/Satisfied -- Phil has a set of figures that look professional, domain-appropriate, and visually consistent.

---

## Journey Flow

```
+---------------------------+
| Step 1: STYLE ANALYSIS    |
| /proposal wave visuals    |
| (enhanced)                |
+---------------------------+
  |
  | Reads solicitation, proposal context, agency
  | Recommends visual style (domain, palette, tone)
  v
+---------------------------+
| Step 2: PROMPT PREVIEW    |
| (per figure, before gen)  |
+---------------------------+
  |
  | Shows engineered prompt with style applied
  | Phil reviews, adjusts, confirms
  v
+---------------------------+     +---------------------------+
| Step 3: GENERATE          | --> | Step 3b: TikZ PATH       |
| Standard: Nano Banana,    |     | (LaTeX proposals only)   |
| SVG, Mermaid, etc.        |     | Generate TikZ, compile,  |
+---------------------------+     | verify, preview          |
  |                               +---------------------------+
  |                                 |
  v                                 v
+---------------------------+
| Step 4: STRUCTURED        |
| CRITIQUE                  |
| Rate: composition, labels,|
| accuracy, style, scale    |
+---------------------------+
  |
  | If issues found:
  v
+---------------------------+
| Step 5: REFINE            |
| System adjusts prompt     |   <-- Max 3 iterations
| based on critique         |   <-- Then: approve, replace,
| Regenerate with feedback  |       or defer to external
+---------------------------+
  |
  | Loop back to Step 4
  | OR proceed to Step 6
  v
+---------------------------+
| Step 6: APPROVE           |
| Figure meets quality bar  |
| Status -> approved        |
+---------------------------+
  |
  | After all figures:
  v
+---------------------------+
| Step 7: CONCLUDE          |
| Style consistency check   |
| Cross-reference validation|
| Quality summary           |
+---------------------------+
```

---

## Step Details with TUI Mockups

### Step 1: Style Analysis

**Command**: `/proposal wave visuals` (enhanced)
**What happens**: System reads solicitation, identifies agency (e.g., Navy), domain (e.g., directed energy), and proposal context. Recommends a visual style profile.

```
+-- Wave 5: Visual Assets -- Style Analysis -------------------------+
|                                                                     |
|  Solicitation: N241-033 (Navy, Directed Energy Systems)             |
|  Proposal Format: LaTeX                                             |
|  Figures Planned: 6                                                 |
|                                                                     |
|  Recommended Visual Style:                                          |
|  +-----------------------------------------------------------------+
|  | Domain:     Maritime/Naval defense                               |
|  | Palette:    Navy blue (#003366), steel gray (#6B7B8D),           |
|  |             signal orange (#FF6B35), ocean teal (#2B7A8C)        |
|  | Tone:       Technical-authoritative, clean sightlines            |
|  | Detail:     High -- evaluators expect engineering precision       |
|  | Avoid:      Cartoon/sketch style, excessive gradients            |
|  | TikZ:       Available (LaTeX detected)                           |
|  +-----------------------------------------------------------------+
|                                                                     |
|  Rationale: Naval evaluators expect precise technical               |
|  illustrations with clear component labeling. Maritime domain       |
|  uses blue-gray palettes. High-contrast labels for readability.     |
|                                                                     |
|  [approve style] [adjust palette] [adjust tone] [skip style]       |
+---------------------------------------------------------------------+
```

**Emotional State**: Cautious -> Curious. Phil sees the system understands his domain. The recommendations feel reasonable. He may adjust a color or two.

---

### Step 2: Prompt Preview (per figure)

**Command**: `/proposal draft figure "system-architecture"` (enhanced)
**What happens**: Before generating, system shows the engineered prompt incorporating style profile and figure specification.

```
+-- Figure 3: System Architecture -- Prompt Preview ------------------+
|                                                                      |
|  Type:     System diagram                                            |
|  Method:   Nano Banana (recommended) | TikZ (available)              |
|  Section:  3.1 Technical Approach                                    |
|                                                                      |
|  Engineered Prompt:                                                  |
|  +-----------------------------------------------------------------+
|  | Technical illustration of a compact directed energy weapon        |
|  | system architecture for naval vessel integration.                 |
|  |                                                                   |
|  | COMPOSITION: Exploded isometric view showing three subsystem      |
|  | layers -- power supply (bottom), beam director (middle),          |
|  | targeting/tracking (top). Each layer connected by labeled         |
|  | interfaces.                                                       |
|  |                                                                   |
|  | STYLE: Clean technical illustration, navy blue (#003366) and      |
|  | steel gray (#6B7B8D) color scheme. White background. Thin        |
|  | black outlines. Sans-serif component labels in 10pt.              |
|  |                                                                   |
|  | LABELS: "Power Conditioning Unit", "Beam Director Assembly",      |
|  | "Target Acquisition Sensor", "Thermal Management System",         |
|  | "C2 Interface", "Ship Power Bus 450V DC".                         |
|  |                                                                   |
|  | AVOID: Photorealistic rendering, motion blur, decorative          |
|  | elements, unlabeled components.                                   |
|  |                                                                   |
|  | RESOLUTION: 2K, 16:9 aspect ratio.                                |
|  +-----------------------------------------------------------------+
|                                                                      |
|  [generate] [edit prompt] [switch to TikZ] [skip figure]            |
+----------------------------------------------------------------------+
```

**Emotional State**: Curious -> Focused. Phil can see exactly what will be sent to Gemini. He can edit the prompt if something is wrong before wasting a generation cycle.

---

### Step 3: Generate

**What happens**: System invokes Nano Banana (or TikZ compiler) and produces the figure.

```
+-- Generating Figure 3: System Architecture -------------------------+
|                                                                      |
|  Method: Nano Banana (Gemini)                                        |
|  [################............] 60% -- Generating image...           |
|                                                                      |
+----------------------------------------------------------------------+
```

For TikZ path (Step 3b):

```
+-- Generating Figure 3: System Architecture (TikZ) ------------------+
|                                                                      |
|  Step 1/3: Generating TikZ code...              done                 |
|  Step 2/3: Compiling with pdflatex...            done                 |
|  Step 3/3: Rendering preview...                  done                 |
|                                                                      |
|  Compilation: SUCCESS (0 errors, 0 warnings)                         |
|  Output: ./artifacts/wave-5-visuals/system-architecture.tex          |
|  Preview: ./artifacts/wave-5-visuals/system-architecture.pdf         |
|                                                                      |
+----------------------------------------------------------------------+
```

**Emotional State**: Focused -> Anticipating. Generation is underway. Phil waits to see results.

---

### Step 4: Structured Critique

**What happens**: Figure is displayed with structured critique categories. Phil rates each dimension rather than giving unstructured feedback.

```
+-- Figure 3: System Architecture -- Review --------------------------+
|                                                                      |
|  [Figure displayed/opened in viewer]                                 |
|                                                                      |
|  Critique Categories:                                                |
|  +------+------------------+------------------------------------------+
|  | Rate | Category         | Question                                |
|  +------+------------------+------------------------------------------+
|  | ___  | Composition      | Layout clear? Hierarchy readable?       |
|  | ___  | Labels           | All components labeled? Text readable?  |
|  | ___  | Accuracy         | Technical content correct?              |
|  | ___  | Style Match      | Consistent with proposal domain?        |
|  | ___  | Scale/Proportion | Elements sized appropriately?           |
|  +------+------------------+------------------------------------------+
|  Rate each 1-5 (5=excellent). Categories rated <3 will be refined.   |
|                                                                      |
|  Overall impression: ____________________________________________    |
|  Specific issues:    ____________________________________________    |
|                                                                      |
|  [submit critique] [approve as-is] [replace method] [defer]          |
+----------------------------------------------------------------------+
```

**Emotional State**: Anticipating -> Engaged. Phil has structured categories to evaluate rather than staring at an image and trying to articulate what's wrong.

---

### Step 5: Refine

**What happens**: System incorporates critique into prompt refinement and regenerates.

```
+-- Figure 3: System Architecture -- Refinement (Round 1/3) ----------+
|                                                                      |
|  Your Critique:                                                      |
|    Composition: 4/5   Labels: 2/5   Accuracy: 4/5                   |
|    Style Match: 5/5   Scale: 3/5                                     |
|    Notes: "Labels are too small and some overlap. Power bus           |
|            connection should be more prominent."                      |
|                                                                      |
|  Prompt Adjustments:                                                 |
|  + Added: "Large, clear sans-serif labels with no overlap.           |
|    Minimum 12pt equivalent. High contrast label backgrounds."         |
|  + Added: "Power bus connection drawn as thick bold line with         |
|    voltage annotation prominently displayed."                         |
|  - Removed: "10pt labels" (was too small)                            |
|                                                                      |
|  [regenerate with adjustments] [edit adjustments] [approve current]  |
+----------------------------------------------------------------------+
```

**Emotional State**: Engaged -> In Control. Phil sees his feedback translated into concrete prompt changes. The system is learning from his critique.

---

### Step 6: Approve

```
+-- Figure 3: System Architecture -- APPROVED ------------------------+
|                                                                      |
|  [Final figure displayed]                                            |
|                                                                      |
|  Quality Summary:                                                    |
|    Composition: 4/5   Labels: 4/5   Accuracy: 4/5                   |
|    Style Match: 5/5   Scale: 4/5                                     |
|    Iterations: 2 (initial + 1 refinement)                            |
|    Method: Nano Banana                                               |
|    File: ./artifacts/wave-5-visuals/system-architecture.png          |
|                                                                      |
|  Status: APPROVED                                                    |
|                                                                      |
|  Next figure: Figure 4 (Project Timeline)                            |
|  [proceed to next] [reopen critique]                                 |
+----------------------------------------------------------------------+
```

**Emotional State**: In Control -> Satisfied. The figure looks professional. On to the next one.

---

### Step 7: Conclude

```
+-- Wave 5: Visual Assets -- Quality Summary -------------------------+
|                                                                      |
|  Proposal: N241-033 (Compact DE System)                              |
|  Style: Maritime/Naval (approved)                                    |
|  Figures: 6 total                                                    |
|                                                                      |
|  +---+---------------------------+--------+------+----------+--------+
|  | # | Title                     | Method | Iter | Quality  | Status |
|  +---+---------------------------+--------+------+----------+--------+
|  | 1 | Operational Scenario      | NB     | 2    | 4.2/5    | OK     |
|  | 2 | System Block Diagram      | TikZ   | 1    | 4.6/5    | OK     |
|  | 3 | System Architecture       | NB     | 2    | 4.2/5    | OK     |
|  | 4 | Project Timeline          | Mermaid | 0   | --       | OK     |
|  | 5 | TRL Progression           | Chart  | 0    | --       | OK     |
|  | 6 | Deployment Environment    | NB     | 3    | 3.8/5    | OK     |
|  +---+---------------------------+--------+------+----------+--------+
|                                                                      |
|  Style Consistency: PASS (all NB figures use approved palette)        |
|  Cross-References: PASS (6/6 figures cited in text)                  |
|  Average Quality: 4.2/5 across critiqued figures                     |
|                                                                      |
|  Wave 5 complete. Ready for Wave 6 formatting.                       |
+----------------------------------------------------------------------+
```

**Emotional State**: Satisfied -> Proud. Phil has a complete set of figures that are visually consistent, domain-appropriate, and individually critiqued. This is a clear improvement over the old "generate and accept" workflow.
