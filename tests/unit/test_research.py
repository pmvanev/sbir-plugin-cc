"""Unit tests for research domain value objects.

Test Budget: 5 behaviors x 2 = 10 unit tests max.

These are pure domain value objects tested directly per step 02-01.
No driving port exists yet -- domain models are built first.

Behaviors:
1. ResearchFinding construction with valid category
2. ResearchFinding rejects invalid category
3. ResearchSummary aggregates findings and provides access by category
4. ResearchSummary reports completeness (all 6 categories present)
5. MarketMetrics captures TAM/SAM/SOM
"""

from __future__ import annotations

import pytest

from pes.domain.research import (
    MarketMetrics,
    ResearchCategory,
    ResearchFinding,
    ResearchSummary,
)


# ---------------------------------------------------------------------------
# Behavior 1: ResearchFinding captures category, content, and evidence source
# ---------------------------------------------------------------------------


class TestResearchFindingConstruction:
    def test_finding_captures_category_content_and_source(self):
        finding = ResearchFinding(
            category=ResearchCategory.TECHNICAL_LANDSCAPE,
            content="Solid-state lasers dominate the compact weapons space.",
            evidence_source="DOD SBIR solicitation N241-035",
        )

        assert finding.category == ResearchCategory.TECHNICAL_LANDSCAPE
        assert finding.content == "Solid-state lasers dominate the compact weapons space."
        assert finding.evidence_source == "DOD SBIR solicitation N241-035"

    def test_finding_is_frozen_value_object(self):
        finding = ResearchFinding(
            category=ResearchCategory.PATENT_LANDSCAPE,
            content="Patent US12345 covers beam steering.",
            evidence_source="USPTO search",
        )

        with pytest.raises(AttributeError):
            finding.content = "modified"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Behavior 2: ResearchFinding rejects invalid category
# ---------------------------------------------------------------------------


class TestResearchFindingValidation:
    def test_category_must_be_research_category_enum(self):
        with pytest.raises((TypeError, ValueError)):
            ResearchFinding(
                category="invalid_category",  # type: ignore[arg-type]
                content="some content",
                evidence_source="some source",
            )


# ---------------------------------------------------------------------------
# Behavior 3: ResearchSummary aggregates findings by category
# ---------------------------------------------------------------------------


class TestResearchSummaryAggregation:
    def test_summary_provides_findings_by_category(self):
        findings = [
            ResearchFinding(
                category=ResearchCategory.TECHNICAL_LANDSCAPE,
                content="Finding A",
                evidence_source="Source A",
            ),
            ResearchFinding(
                category=ResearchCategory.TECHNICAL_LANDSCAPE,
                content="Finding B",
                evidence_source="Source B",
            ),
            ResearchFinding(
                category=ResearchCategory.PATENT_LANDSCAPE,
                content="Finding C",
                evidence_source="Source C",
            ),
        ]
        summary = ResearchSummary(findings=findings)

        tech = summary.get_findings_by_category(ResearchCategory.TECHNICAL_LANDSCAPE)
        assert len(tech) == 2

        patent = summary.get_findings_by_category(ResearchCategory.PATENT_LANDSCAPE)
        assert len(patent) == 1

        empty = summary.get_findings_by_category(ResearchCategory.TRL_REFINEMENT)
        assert len(empty) == 0

    def test_summary_reports_total_finding_count(self):
        findings = [
            ResearchFinding(
                category=ResearchCategory.MARKET_ANALYSIS,
                content="TAM is $2B",
                evidence_source="Market report",
            ),
        ]
        summary = ResearchSummary(findings=findings)

        assert summary.finding_count == 1


# ---------------------------------------------------------------------------
# Behavior 4: ResearchSummary reports completeness
# ---------------------------------------------------------------------------


class TestResearchSummaryCompleteness:
    def test_complete_when_all_six_categories_present(self):
        findings = [
            ResearchFinding(category=cat, content=f"Content for {cat.value}", evidence_source="src")
            for cat in ResearchCategory
        ]
        summary = ResearchSummary(findings=findings)

        assert summary.is_complete is True

    def test_incomplete_when_categories_missing(self):
        findings = [
            ResearchFinding(
                category=ResearchCategory.TECHNICAL_LANDSCAPE,
                content="Only one category",
                evidence_source="src",
            ),
        ]
        summary = ResearchSummary(findings=findings)

        assert summary.is_complete is False

    def test_covered_categories_returns_present_set(self):
        findings = [
            ResearchFinding(
                category=ResearchCategory.TECHNICAL_LANDSCAPE,
                content="A",
                evidence_source="src",
            ),
            ResearchFinding(
                category=ResearchCategory.PATENT_LANDSCAPE,
                content="B",
                evidence_source="src",
            ),
        ]
        summary = ResearchSummary(findings=findings)

        assert summary.covered_categories == {
            ResearchCategory.TECHNICAL_LANDSCAPE,
            ResearchCategory.PATENT_LANDSCAPE,
        }


# ---------------------------------------------------------------------------
# Behavior 5: MarketMetrics captures TAM/SAM/SOM
# ---------------------------------------------------------------------------


class TestMarketMetrics:
    def test_market_metrics_captures_tam_sam_som(self):
        metrics = MarketMetrics(
            tam=2_000_000_000.0,
            sam=500_000_000.0,
            som=50_000_000.0,
            currency="USD",
        )

        assert metrics.tam == 2_000_000_000.0
        assert metrics.sam == 500_000_000.0
        assert metrics.som == 50_000_000.0
        assert metrics.currency == "USD"

    def test_market_metrics_is_frozen_value_object(self):
        metrics = MarketMetrics(
            tam=1000.0,
            sam=500.0,
            som=100.0,
        )

        with pytest.raises(AttributeError):
            metrics.tam = 999.0  # type: ignore[misc]
