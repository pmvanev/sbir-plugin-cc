# Four Forces Analysis -- Solution Shaper

## Forces Analysis: Approach Selection Before Proposal Writing

### Demand-Generating

**Push (Current Frustrations)**

1. **Implicit approach decision**: Phil arrives at Wave 1 with an approach already in his head but no structured evaluation of alternatives. If the approach is wrong, weeks of proposal effort are wasted.

2. **Company fit stops at company level**: The topic-scout scores "does our company fit this topic?" but not "which of several technical approaches best leverages our specific people, past work, and IP?" A company may fit a directed energy topic at 70% but the fiber laser approach might score 90% and the solid-state approach 40%.

3. **Commercialization assessed too late**: The researcher builds TAM/SAM/SOM in Wave 2 after the strategy is already set. Two approaches to the same problem can have wildly different Phase III pathways -- one dual-use with a $2B commercial market, the other purely military with a $50M niche. By Wave 2 it is too late to change approaches.

4. **No audit trail for approach decisions**: When debriefs come back, Phil cannot reconstruct why he chose one approach over another. The decision was mental. Learning from win/loss patterns at the approach level is impossible.

5. **Adjacent topics are riskiest**: Phil's growth strategy involves pursuing topics adjacent to core expertise. These are precisely the topics where multiple approaches exist and the "obvious" choice is most likely to be wrong.

**Push Strength**: STRONG -- structural gap confirmed by 5 codebase evidence points and user's explicit statement.

---

**Pull (Attractions of New Solution)**

1. **Systematic option-space exploration**: Generate 3-5 technically distinct approaches instead of defaulting to the first idea. Include non-obvious combinations (company capability reverse-mapping).

2. **Company-specific scoring**: Score each approach against personnel expertise, past performance, IP, TRL starting point, and solicitation fit. Different from generic "which approach is best?" -- this is "which approach is best FOR US."

3. **Early commercialization signal**: Quick Phase III pathway assessment per approach before committing to strategy. Dual-use screening. Market size delta analysis.

4. **Documented rationale**: An approach-brief.md artifact that carries the selection rationale into Wave 1, feeds the discrimination table in Wave 3, and provides debrief traceability.

5. **Under 10 minutes**: Structured process that produces a defensible recommendation faster than Phil's current mental noodling (hours to days).

**Pull Strength**: STRONG -- fills explicit gap with clear value proposition.

---

### Demand-Reducing

**Anxiety (Fears About New Solution)**

1. **Will the LLM generate useful approaches?**: If the generated approaches are trivial variations of the same idea or technically incoherent, the step adds overhead without value. Mitigation: this is a core LLM strength (reasoning about technical approaches given domain context).

2. **Will the scoring actually differentiate?**: If all approaches score within 5% of each other, the scoring framework adds false precision. Mitigation: approach-level scoring should produce 20%+ spread due to company-specific dimensions.

3. **Will Phil actually use it?**: If Phil's mental model is faster and the structured process feels bureaucratic, he will skip it. Mitigation: keep the step fast (<10 minutes), make it skippable, and prove value on the first real solicitation.

4. **Does this add another step to an already 10-wave workflow?**: Complexity cost. Mitigation: the step is lightweight (single agent, single artifact) and optional.

**Anxiety Strength**: MODERATE -- primarily around LLM output quality and adoption, not architectural risk.

---

**Habit (Inertia of Current Approach)**

1. **Mental approach selection works fine for core expertise topics**: When Phil has deep domain knowledge, he arrives at Wave 1 with a strong intuitive approach. The solution-shaper adds most value for adjacent topics.

2. **"I already know what to propose"**: For experienced proposers, the approach feels obvious. The risk is not seeing alternatives that might be stronger.

3. **Zero current effort**: The current "process" (thinking about it) costs nothing. Any structured step must prove its value exceeds its time cost.

**Habit Strength**: LOW-MODERATE -- the user explicitly asked for this capability, suggesting habit force is already overcome.

---

### Assessment

- **Switch likelihood**: HIGH
- **Key blocker**: Anxiety about LLM approach generation quality (will it produce technically coherent, non-obvious approaches?)
- **Key enabler**: Push from structural gap + Pull of documented rationale + explicit user request
- **Design implication**: The approach generation must surface at least 1-2 approaches Phil would not have considered independently. If every generated approach is obvious, the feature fails its core value proposition.

### Force Balance

```
Push (STRONG) + Pull (STRONG) >> Anxiety (MODERATE) + Habit (LOW-MODERATE)

Switch decision: CLEAR GO
```

The user explicitly described the gap. The codebase confirms no agent owns approach selection. The four forces favor adoption. The primary risk (H4: will Phil actually use structured approach selection?) can only be validated through real use with an upcoming solicitation.
