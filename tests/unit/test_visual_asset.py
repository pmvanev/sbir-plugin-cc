"""Unit tests for visual asset domain models.

Test Budget: 3 behaviors x 2 = 6 unit tests max.

These are pure domain value objects tested directly per step 02-01.
No driving port (VisualAssetService) exists yet -- domain models built first.

Behaviors:
1. FigurePlaceholder captures type, generation method, and section (frozen)
2. FigureInventory aggregates placeholders with count
3. CrossReferenceLog validates figure-to-text consistency
"""

from __future__ import annotations

import pytest

from pes.domain.visual_asset import (
    CrossReferenceEntry,
    CrossReferenceLog,
    FigureInventory,
    FigurePlaceholder,
)

# ---------------------------------------------------------------------------
# Behavior 1: FigurePlaceholder captures fields as frozen value object
# ---------------------------------------------------------------------------


class TestFigurePlaceholder:
    def test_captures_type_method_and_section(self):
        placeholder = FigurePlaceholder(
            figure_number=1,
            section_id="3.1",
            description="System architecture block diagram",
            figure_type="block_diagram",
            generation_method="Mermaid",
        )

        assert placeholder.figure_number == 1
        assert placeholder.section_id == "3.1"
        assert placeholder.description == "System architecture block diagram"
        assert placeholder.figure_type == "block_diagram"
        assert placeholder.generation_method == "Mermaid"

    def test_is_frozen_value_object(self):
        placeholder = FigurePlaceholder(
            figure_number=1,
            section_id="3.1",
            description="Diagram",
            figure_type="block_diagram",
            generation_method="Mermaid",
        )

        with pytest.raises(AttributeError):
            placeholder.figure_type = "flowchart"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Behavior 2: FigureInventory aggregates placeholders with count
# ---------------------------------------------------------------------------


class TestFigureInventory:
    def test_aggregates_placeholders_with_count(self):
        placeholders = [
            FigurePlaceholder(
                figure_number=i,
                section_id=f"3.{i}",
                description=f"Figure {i}",
                figure_type="diagram",
                generation_method="Mermaid",
            )
            for i in range(1, 4)
        ]

        inventory = FigureInventory(placeholders=placeholders)

        assert inventory.count == 3
        assert len(inventory.placeholders) == 3
        assert inventory.placeholders[0].figure_number == 1

    def test_empty_inventory_has_zero_count(self):
        inventory = FigureInventory(placeholders=[])

        assert inventory.count == 0


# ---------------------------------------------------------------------------
# Behavior 3: CrossReferenceLog validates figure-to-text consistency
# ---------------------------------------------------------------------------


class TestCrossReferenceLog:
    def test_detects_orphaned_references(self):
        """References to figures that do not exist are flagged."""
        entries = [
            CrossReferenceEntry(
                section_id="3.3",
                referenced_figure=6,
                exists=False,
            ),
        ]
        log = CrossReferenceLog(entries=entries)

        orphans = log.orphaned_references
        assert len(orphans) == 1
        assert orphans[0].referenced_figure == 6
        assert orphans[0].section_id == "3.3"
        assert not log.all_valid

    def test_all_valid_when_no_orphans(self):
        """All references resolve to existing figures."""
        entries = [
            CrossReferenceEntry(
                section_id="3.1",
                referenced_figure=1,
                exists=True,
            ),
            CrossReferenceEntry(
                section_id="3.2",
                referenced_figure=2,
                exists=True,
            ),
        ]
        log = CrossReferenceLog(entries=entries)

        assert log.all_valid
        assert log.orphaned_references == []
