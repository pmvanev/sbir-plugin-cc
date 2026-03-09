"""Shared research fixtures used across unit and acceptance tests."""

from __future__ import annotations

from pes.domain.research import (
    ResearchCategory,
    ResearchFinding,
    ResearchSummary,
)


def make_research_summary() -> ResearchSummary:
    """Build a complete research summary covering all six categories."""
    return ResearchSummary(
        findings=[
            ResearchFinding(
                category=cat,
                content=f"Finding for {cat.value}",
                evidence_source=f"Source for {cat.value}",
            )
            for cat in ResearchCategory
        ],
    )
