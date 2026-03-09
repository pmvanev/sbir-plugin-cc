"""Research domain models -- value objects for research findings.

Pure domain objects with no infrastructure imports.
ResearchFinding captures individual findings by category.
ResearchSummary aggregates all findings across six research categories.
MarketMetrics captures TAM/SAM/SOM for market analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ResearchCategory(Enum):
    """The six research categories for SBIR proposal research."""

    TECHNICAL_LANDSCAPE = "technical_landscape"
    PATENT_LANDSCAPE = "patent_landscape"
    PRIOR_AWARD_ANALYSIS = "prior_award_analysis"
    MARKET_ANALYSIS = "market_analysis"
    COMMERCIALIZATION_PATHWAY = "commercialization_pathway"
    TRL_REFINEMENT = "trl_refinement"


@dataclass(frozen=True)
class ResearchFinding:
    """A single research finding with category, content, and evidence source.

    Validates that category is a ResearchCategory enum member.
    """

    category: ResearchCategory
    content: str
    evidence_source: str

    def __post_init__(self) -> None:
        if not isinstance(self.category, ResearchCategory):
            raise TypeError(
                f"category must be a ResearchCategory, got {type(self.category).__name__}"
            )


@dataclass(frozen=True)
class MarketMetrics:
    """TAM/SAM/SOM metrics for market analysis."""

    tam: float
    sam: float
    som: float
    currency: str = "USD"


@dataclass
class ResearchSummary:
    """Aggregates research findings across all six categories."""

    findings: list[ResearchFinding] = field(default_factory=list)
    market_metrics: MarketMetrics | None = None
    caveats: list[str] = field(default_factory=list)

    @property
    def finding_count(self) -> int:
        """Total number of findings."""
        return len(self.findings)

    @property
    def covered_categories(self) -> set[ResearchCategory]:
        """Set of categories that have at least one finding."""
        return {f.category for f in self.findings}

    @property
    def is_complete(self) -> bool:
        """True when all six research categories have at least one finding."""
        return self.covered_categories == set(ResearchCategory)

    def get_findings_by_category(self, category: ResearchCategory) -> list[ResearchFinding]:
        """Return all findings for a given category."""
        return [f for f in self.findings if f.category == category]
