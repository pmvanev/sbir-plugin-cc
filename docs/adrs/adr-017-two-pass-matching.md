# ADR-017: Two-Pass Matching (Keyword Pre-Filter + LLM Scoring)

## Status

Accepted

## Context

The solicitation finder must score 300-500 topics per cycle against a company profile. LLM-based five-dimension scoring (fit-scoring-methodology) produces high-quality semantic matches but costs ~1500-2500 tokens per topic. Scoring all 500 topics would consume ~750K-1.25M tokens per run -- expensive and slow (20-40 minutes).

Quality attributes driving this decision: performance (< 10 minutes end-to-end), cost efficiency (token budget), and accuracy (> 80% precision, > 70% recall).

## Decision

Implement a two-pass matching pipeline:

1. **Pass 1 -- Keyword pre-filter (Python, fast)**: Match topic titles and codes against company profile capability keywords. Eliminate obviously irrelevant topics (biodefense, social science, medical when company does directed energy). Runs in seconds on 500 topics. Pure domain logic, no LLM.

2. **Pass 2 -- LLM semantic scoring (Claude, accurate)**: Score remaining 20-50 candidates using the five-dimension fit model (SME 0.35, PP 0.25, Cert 0.15, Elig 0.15, STTR 0.10). Reads topic PDFs for full descriptions. Batched in groups of 10-20.

Pre-filter is intentionally loose (high recall, moderate precision) -- it catches obvious mismatches, not borderline cases. The LLM handles terminology variation and semantic matching in pass 2.

## Alternatives Considered

### Alternative 1: LLM-only scoring (no pre-filter)

- **Evaluation**: Simpler architecture. Every topic scored by Claude. Produces highest accuracy.
- **Rejection**: 500 topics x 2000 tokens = 1M tokens. 20-40 minutes runtime. Exceeds the 10-minute target. Token cost is 5-10x higher. Unacceptable for a CLI tool that should feel responsive.

### Alternative 2: Keyword-only scoring (no LLM)

- **Evaluation**: Pure Python. Fast. Zero token cost. Testable.
- **Rejection**: Keyword matching misses terminology variation -- the core problem this feature solves (Problem P2 in lean canvas). "RF power management" and "directed energy" share no keywords but are semantically related. Keyword-only scoring would achieve ~50% recall at best.

### Alternative 3: Embedding-based similarity (vector search)

- **Evaluation**: Encode company profile and topics as embeddings. Compute cosine similarity. Fast after initial encoding.
- **Rejection**: Requires embedding model dependency (sentence-transformers or API call). Adds infrastructure complexity. Claude already provides semantic understanding. Embeddings would duplicate capability already available in the LLM scoring pass. Over-engineering for 50-100 candidates.

## Consequences

### Positive

- Token budget reduced by 80-90% (500 topics -> 50 candidates scored)
- Runtime under 10 minutes for typical cycles
- Pre-filter is testable pure Python (no LLM dependency in tests)
- Two-pass architecture enables independent improvement of each pass
- Loose pre-filter preserves recall; LLM pass provides precision

### Negative

- Two-component architecture is more complex than single-pass
- Pre-filter may have false negatives for topics with no keyword overlap to profile (mitigated by intentionally loose matching)
- Requires maintaining keyword extraction logic as profile schema evolves
