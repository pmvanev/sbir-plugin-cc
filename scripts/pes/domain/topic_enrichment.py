"""Topic enrichment -- domain logic for combining and reporting enrichment data.

Pure domain module: combines fetched topic metadata with enrichment data
(descriptions, instructions, Q&A) and produces completeness reports.
No I/O dependencies.
"""

from __future__ import annotations

from typing import Any


def combine_topics_with_enrichment(
    candidates: list[dict[str, Any]],
    enriched: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge enrichment data into candidate topic dicts.

    For each candidate, looks up enrichment by topic_id and merges
    description, instructions, component_instructions, qa_entries,
    and enrichment_status.

    Args:
        candidates: Pre-filtered candidate topics (dicts with topic_id).
        enriched: Enrichment results (dicts with topic_id + detail fields).

    Returns:
        List of combined topic dicts with enrichment fields merged in.
    """
    enrichment_by_id = {e["topic_id"]: e for e in enriched}
    combined: list[dict[str, Any]] = []

    for candidate in candidates:
        topic_id = candidate.get("topic_id", "")
        enrichment = enrichment_by_id.get(topic_id)
        if enrichment is None:
            continue  # topic failed enrichment, skip

        merged = dict(candidate)
        merged["description"] = enrichment.get("description", "")
        merged["instructions"] = enrichment.get("instructions")
        merged["component_instructions"] = enrichment.get("component_instructions")
        merged["qa_entries"] = enrichment.get("qa_entries", [])
        merged["keywords"] = enrichment.get("keywords", [])
        merged["technology_areas"] = enrichment.get("technology_areas", [])
        merged["focus_areas"] = enrichment.get("focus_areas", [])
        merged["objective"] = enrichment.get("objective")
        merged["itar"] = enrichment.get("itar")
        merged["cmmc_level"] = enrichment.get("cmmc_level")
        merged["solicitation_instructions"] = enrichment.get("solicitation_instructions")
        merged["enrichment_status"] = "ok"
        combined.append(merged)

    return combined


def completeness_report(
    completeness: dict[str, int],
    errors: list[dict[str, Any]],
) -> list[str]:
    """Generate human-readable completeness messages.

    Args:
        completeness: Dict with keys descriptions, instructions, qa, total.
        errors: List of error dicts with topic_id and error fields.

    Returns:
        List of message strings.
    """
    messages: list[str] = []
    total = completeness.get("total", 0)
    desc = completeness.get("descriptions", 0)
    qa = completeness.get("qa", 0)
    sol_instr = completeness.get("solicitation_instructions", 0)
    comp_instr = completeness.get("component_instructions", 0)

    messages.append(f"Descriptions: {desc}/{total}")
    if qa > 0:
        messages.append(f"Q&A: {qa}/{total}")
    if sol_instr > 0:
        messages.append(f"Solicitation Instructions: {sol_instr}/{total}")
    if comp_instr > 0:
        messages.append(f"Component Instructions: {comp_instr}/{total}")

    if errors:
        failed_ids = [e.get("topic_id", "unknown") for e in errors]
        messages.append(
            f"Enrichment failed for {len(errors)} topics: "
            + ", ".join(failed_ids)
        )

    return messages
