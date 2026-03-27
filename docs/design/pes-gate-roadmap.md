# PES Gate Roadmap

Tracked enforcement gaps across the proposal lifecycle. Prioritized by likelihood of agent bypass and impact on proposal quality.

## Delivered

| Gate | Evaluator | Wave | Delivered |
|------|-----------|------|-----------|
| Wave sequence | WaveOrderingEvaluator | Cross-cutting | C1 |
| PDC green required | PdcGateEvaluator | Cross-cutting | C1 |
| Deadline blocking | DeadlineBlockingEvaluator | Cross-cutting | C1 |
| Submitted artifacts immutable | SubmissionImmutabilityEvaluator | 8 | C1 |
| Corpus win/loss append-only | CorpusIntegrityEvaluator | Cross-cutting | C1 |
| Figure specs before figures | FigurePipelineGateEvaluator | 5 | 2026-03-27 |
| Style profile before generation | StyleProfileGateEvaluator | 5 | 2026-03-27 |
| Writing style before drafting | WritingStyleGateEvaluator | 4 | 2026-03-27 |
| Outline before drafting | OutlineGateEvaluator | 4 | 2026-03-27 |

## Backlog (prioritized)

### ~~P1: Outline gate for Wave 4~~ — DELIVERED 2026-03-27

### P2: Figure plan gate for Wave 5

- **Gap**: Formatter can write figure-specs.md without a figure plan from the outline
- **Gate**: Block figure-specs.md writes to wave-5-visuals/ when figure-plan.md does not exist in wave-3-outline/
- **Pattern**: Cross-directory check — target is wave-5-visuals/ but prerequisite is in wave-3-outline/
- **Risk**: High — formatter invents figure specs without the writer's figure plan
- **Scope**: 1 evaluator + config rule. Hook adapter needs cross-directory resolution (new capability)

### P3: Compliance matrix gate

- **Gap**: Writer and formatter can work without a compliance matrix
- **Gate**: Block wave-4-drafting/ and wave-6-formatted/ writes when compliance-matrix.md does not exist in .sbir/
- **Pattern**: Similar to WritingStyleGateEvaluator (state-dir artifact check)
- **Risk**: Moderate — compliance traceability is a core principle, without matrix nothing is traceable
- **Scope**: 1 evaluator + config rule. Two target directories (wave-4 + wave-6)

### P4: Strategy brief gate for Wave 3

- **Gap**: Writer can outline without strategy brief from Wave 1
- **Gate**: Block wave-3-outline/ writes when strategy-brief.md does not exist in wave-1-strategy/
- **Pattern**: Cross-directory check (target: wave-3, prerequisite: wave-1)
- **Risk**: Moderate — outline without strategy misses discriminators, Phase III pathway
- **Scope**: 1 evaluator + config rule + hook adapter wave-3 detection

### P5: All sections gate for Wave 6

- **Gap**: Formatter can assemble/format with missing section drafts
- **Gate**: Block wave-6-formatted/ writes when required sections not present in wave-4-drafting/sections/
- **Pattern**: Multi-file check — needs outline to know which sections are required
- **Risk**: Moderate — incomplete assembly, missing sections in final document
- **Scope**: Complex — evaluator needs to know expected sections from outline. May be better as a wave checkpoint than a PES gate.

### P6: Company profile gate for scoring

- **Gap**: Topic scout can score without a company profile
- **Gate**: Block scoring operations when ~/.sbir/company-profile.json does not exist
- **Pattern**: Global artifact check (same as WritingStyleGateEvaluator)
- **Risk**: Low — topic scout already warns and degrades gracefully
- **Scope**: 1 evaluator + config rule. May be unnecessary given existing degradation.

### P7: Drafts gate for Wave 7 review

- **Gap**: Reviewer could attempt review without drafted sections
- **Gate**: Block wave-7-review/ writes when wave-4-drafting/sections/ is empty
- **Pattern**: Directory content check
- **Risk**: Low — reviewer agent already checks for content
- **Scope**: 1 evaluator + config rule
