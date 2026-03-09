"""Unit tests for discrimination domain value objects.

Test Budget: 2 behaviors x 2 = 4 unit tests max.

These are pure domain value objects tested directly per step 03-01.
No driving port exists yet -- domain models are built first.

Behaviors:
1. DiscriminatorItem captures category, claim, and evidence citation (frozen VO)
2. DiscriminationTable holds a collection of discriminator items
"""

from __future__ import annotations

import pytest

from pes.domain.discrimination import DiscriminationTable, DiscriminatorItem


# ---------------------------------------------------------------------------
# Behavior 1: DiscriminatorItem captures category, claim, evidence citation
# ---------------------------------------------------------------------------


class TestDiscriminatorItemConstruction:
    def test_item_captures_category_claim_and_evidence(self):
        item = DiscriminatorItem(
            category="innovation",
            claim="Novel beam-steering algorithm reduces latency by 40%",
            evidence_citation="Phase I Final Report, Section 3.2",
        )

        assert item.category == "innovation"
        assert item.claim == "Novel beam-steering algorithm reduces latency by 40%"
        assert item.evidence_citation == "Phase I Final Report, Section 3.2"

    def test_item_is_frozen_value_object(self):
        item = DiscriminatorItem(
            category="cost",
            claim="30% cost reduction vs incumbent",
            evidence_citation="Market analysis, Table 4",
        )

        with pytest.raises(AttributeError):
            item.claim = "modified"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Behavior 2: DiscriminationTable holds collection of items
# ---------------------------------------------------------------------------


class TestDiscriminationTable:
    def test_table_holds_collection_of_items(self):
        items = [
            DiscriminatorItem(
                category="innovation",
                claim="Claim A",
                evidence_citation="Source A",
            ),
            DiscriminatorItem(
                category="performance",
                claim="Claim B",
                evidence_citation="Source B",
            ),
        ]
        table = DiscriminationTable(items=items)

        assert len(table.items) == 2
        assert table.items[0].category == "innovation"
        assert table.items[1].category == "performance"

    def test_empty_table_has_no_items(self):
        table = DiscriminationTable()

        assert len(table.items) == 0
