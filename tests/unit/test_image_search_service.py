"""Unit tests for ImageSearchService -- driving port for image search and browse.

Test Budget: 5 behaviors x 2 = 10 max unit tests.

Behaviors:
1. List all images returns all entries
2. List with filters returns filtered subset (parametrized)
3. Search with relevance ranking scores correctly
4. Search with no matches returns guidance
5. Empty catalog list returns onboarding guidance
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta

import pytest

from tests.acceptance.corpus_image_reuse.conftest import (
    SYNTHETIC_PNG_BYTES,
    make_registry_entry,
)
from tests.acceptance.corpus_image_reuse.fakes import InMemoryImageRegistryAdapter


def _make_populated_registry() -> InMemoryImageRegistryAdapter:
    """Create a registry with a mix of images for testing."""
    registry = InMemoryImageRegistryAdapter()
    # 3 system-diagrams from USAF/WIN
    for i in range(3):
        registry.add(make_registry_entry(
            image_id=f"usaf-sd-{i:02d}",
            source_proposal="AF243-001",
            agency="USAF",
            outcome="WIN",
            figure_type="system-diagram",
            caption=f"Figure {i}: System Architecture Diagram {i}",
            content_hash=hashlib.sha256(f"usaf-sd-{i}".encode()).hexdigest(),
        ))
    # 2 trl-roadmaps from DARPA/WIN
    for i in range(2):
        registry.add(make_registry_entry(
            image_id=f"darpa-trl-{i:02d}",
            source_proposal="DARPA-HR-22",
            agency="DARPA",
            outcome="WIN",
            figure_type="trl-roadmap",
            caption=f"Figure {i}: TRL Roadmap {i}",
            content_hash=hashlib.sha256(f"darpa-trl-{i}".encode()).hexdigest(),
        ))
    # 1 org-chart from USAF/LOSS
    registry.add(make_registry_entry(
        image_id="usaf-org-00",
        source_proposal="AF244-005",
        agency="USAF",
        outcome="LOSS",
        figure_type="org-chart",
        caption="Figure 1: Organization Chart",
        content_hash=hashlib.sha256(b"usaf-org").hexdigest(),
    ))
    return registry


class TestImageSearchServiceList:
    """Tests for list_images through the ImageSearchService driving port."""

    def test_list_all_returns_all_entries(self) -> None:
        """List without filters returns every image in the registry."""
        from pes.domain.image_search_service import ImageSearchService

        registry = _make_populated_registry()
        service = ImageSearchService(registry=registry)

        result = service.list_images()

        assert len(result.entries) == 6
        assert result.message is None

    @pytest.mark.parametrize(
        "filter_kwargs,expected_count",
        [
            ({"figure_type": "system-diagram"}, 3),
            ({"figure_type": "trl-roadmap"}, 2),
            ({"outcome": "WIN"}, 5),
            ({"outcome": "LOSS"}, 1),
            ({"agency": "USAF"}, 4),
            ({"agency": "DARPA"}, 2),
            ({"source": "AF243-001"}, 3),
        ],
        ids=[
            "type-system-diagram",
            "type-trl-roadmap",
            "outcome-WIN",
            "outcome-LOSS",
            "agency-USAF",
            "agency-DARPA",
            "source-AF243-001",
        ],
    )
    def test_list_with_filter_returns_matching_subset(
        self, filter_kwargs: dict, expected_count: int,
    ) -> None:
        """List with a single filter returns only matching images."""
        from pes.domain.image_search_service import ImageSearchService

        registry = _make_populated_registry()
        service = ImageSearchService(registry=registry)

        result = service.list_images(**filter_kwargs)

        assert len(result.entries) == expected_count

    def test_empty_catalog_returns_onboarding_guidance(self) -> None:
        """Empty registry returns a message suggesting corpus add."""
        from pes.domain.image_search_service import ImageSearchService

        registry = InMemoryImageRegistryAdapter()
        service = ImageSearchService(registry=registry)

        result = service.list_images()

        assert len(result.entries) == 0
        assert result.message is not None
        assert "no images in catalog" in result.message.lower()


class TestImageSearchServiceSearch:
    """Tests for search through the ImageSearchService driving port."""

    def test_search_ranks_agency_match_higher(self) -> None:
        """Images matching current agency score higher than non-matching."""
        from pes.domain.image_search_service import ImageSearchService

        registry = InMemoryImageRegistryAdapter()
        registry.add(make_registry_entry(
            image_id="usaf-sys-01",
            source_proposal="AF243-001",
            agency="USAF",
            outcome="WIN",
            figure_type="system-diagram",
            caption="Figure 1: System Architecture Overview",
            content_hash=hashlib.sha256(b"usaf-sys").hexdigest(),
        ))
        registry.add(make_registry_entry(
            image_id="darpa-sys-01",
            source_proposal="DARPA-HR-22",
            agency="DARPA",
            outcome="WIN",
            figure_type="system-diagram",
            caption="Figure 2: System Architecture Design",
            content_hash=hashlib.sha256(b"darpa-sys").hexdigest(),
        ))
        service = ImageSearchService(registry=registry)

        result = service.search(query="system architecture", current_agency="USAF")

        assert len(result.scored_results) == 2
        usaf_scores = [
            sr.score for sr in result.scored_results
            if sr.entry.source_proposal == "AF243-001"
        ]
        darpa_scores = [
            sr.score for sr in result.scored_results
            if sr.entry.source_proposal == "DARPA-HR-22"
        ]
        assert max(usaf_scores) > max(darpa_scores)

    def test_search_results_sorted_descending(self) -> None:
        """Search results are sorted by descending relevance score."""
        from pes.domain.image_search_service import ImageSearchService

        registry = _make_populated_registry()
        service = ImageSearchService(registry=registry)

        result = service.search(query="system architecture", current_agency="USAF")

        scores = [sr.score for sr in result.scored_results]
        assert scores == sorted(scores, reverse=True)
        assert len(scores) > 0

    def test_search_no_matches_returns_guidance(self) -> None:
        """Search with no matching images returns a guidance message."""
        from pes.domain.image_search_service import ImageSearchService

        registry = _make_populated_registry()
        service = ImageSearchService(registry=registry)

        result = service.search(query="quantum entanglement sensor", current_agency="USAF")

        assert len(result.scored_results) == 0
        assert result.message is not None
        assert "no matching images found" in result.message.lower()

    def test_search_outcome_boost_favors_wins(self) -> None:
        """WIN proposals score higher than LOSS proposals, all else equal."""
        from pes.domain.image_search_service import ImageSearchService

        registry = InMemoryImageRegistryAdapter()
        # Same caption, same agency, different outcome
        registry.add(make_registry_entry(
            image_id="win-img",
            source_proposal="WIN-PROP",
            agency="USAF",
            outcome="WIN",
            caption="Figure 1: Radar Detection System",
            content_hash=hashlib.sha256(b"win-radar").hexdigest(),
        ))
        registry.add(make_registry_entry(
            image_id="loss-img",
            source_proposal="LOSS-PROP",
            agency="USAF",
            outcome="LOSS",
            caption="Figure 2: Radar Detection System",
            content_hash=hashlib.sha256(b"loss-radar").hexdigest(),
        ))
        service = ImageSearchService(registry=registry)

        result = service.search(query="radar detection", current_agency="USAF")

        assert len(result.scored_results) == 2
        win_score = next(
            sr.score for sr in result.scored_results
            if sr.entry.source_proposal == "WIN-PROP"
        )
        loss_score = next(
            sr.score for sr in result.scored_results
            if sr.entry.source_proposal == "LOSS-PROP"
        )
        assert win_score > loss_score
