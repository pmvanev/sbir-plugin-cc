# ADR-010: Debrief Parsing Strategy -- Best-Effort with Freeform Fallback

## Status

Accepted

## Context

Wave 9 requires parsing debrief feedback to extract scores, critique comments, and map them to proposal sections. Debriefs vary wildly: some agencies provide structured score tables, others send a single paragraph of narrative feedback. Some debriefs are PDF, others are plain text or email.

Key design question: how to handle the spectrum from structured to completely unstructured debriefs.

## Decision

Best-effort structured parsing with freeform fallback. The DebriefParserPort attempts structured extraction (scores, individual critiques). When structured parsing fails or produces low-confidence results, the full text is preserved as freeform feedback. The LLM agent (debrief-analyst) does the actual parsing; the PES domain service validates the output and manages the critique-to-section mapping.

Parsing confidence reported to Phil so he knows what was extracted vs. preserved as-is.

## Alternatives Considered

### Alternative 1: Strict structured parsing only
- **What**: Require debriefs to match an expected format; reject unparseable debriefs
- **Expected impact**: High-quality structured data when it works; complete loss when it doesn't
- **Why rejected**: 40% of Phil's submissions get no debrief at all. Of those that do, format varies by agency, reviewer, and year. Rejecting unparseable debriefs loses valuable feedback. NFR-007 requires near-zero effort -- making Phil reformat debriefs defeats the purpose.

### Alternative 2: Manual tagging by Phil
- **What**: Phil manually tags each critique in the debrief with section references
- **Expected impact**: 100% accuracy on mapping
- **Why rejected**: Violates NFR-007 (under 5 minutes). Manual tagging of a 3-page debrief with 4 critiques takes 15-20 minutes. Phil will skip it, defeating the learning loop.

### Alternative 3: NLP pipeline (spaCy/NLTK)
- **What**: Local NLP pipeline for entity extraction and section matching
- **Expected impact**: Better structured extraction than regex, worse than LLM
- **Why rejected**: Adds heavyweight dependencies (spaCy models ~100MB). The LLM (Claude Code) is already available and better at understanding government evaluation language. Using the agent for parsing is simpler and more accurate.

## Consequences

- **Positive**: Every debrief produces something useful -- structured data or preserved freeform text.
- **Positive**: LLM-based parsing handles government evaluation language better than rule-based approaches.
- **Positive**: Confidence level sets correct expectations ("3 of 4 critiques mapped with high confidence").
- **Negative**: LLM parsing is non-deterministic. Same debrief may produce slightly different structured output on re-parse. Acceptable because Phil reviews the output.
- **Negative**: Freeform fallback is less useful for automated pattern analysis. Keyword-based matching still works on freeform text.
