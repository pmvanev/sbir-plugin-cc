"""Unit tests for draft domain value objects.

Test Budget: 2 behaviors x 2 = 4 unit tests max.

These are pure domain value objects tested directly per step 04-01.
No driving port exists yet -- domain models are built first.

Behaviors:
1. SectionDraft captures fields with word count computed from content
2. SectionDraft is a frozen value object with iteration tracking
"""

from __future__ import annotations

import pytest

from pes.domain.draft import SectionDraft


# ---------------------------------------------------------------------------
# Behavior 1: SectionDraft captures fields with computed word count
# ---------------------------------------------------------------------------


class TestSectionDraftConstruction:
    def test_draft_captures_fields_and_computes_word_count(self):
        draft = SectionDraft(
            section_id="tech-approach",
            content="Our novel beam-steering algorithm reduces latency significantly.",
            compliance_item_ids=["CI-001", "CI-002"],
            iteration=1,
        )

        assert draft.section_id == "tech-approach"
        assert draft.content == "Our novel beam-steering algorithm reduces latency significantly."
        assert draft.compliance_item_ids == ["CI-001", "CI-002"]
        assert draft.word_count == 7
        assert draft.iteration == 1

    def test_draft_word_count_handles_empty_content(self):
        draft = SectionDraft(
            section_id="intro",
            content="",
            compliance_item_ids=[],
            iteration=1,
        )

        assert draft.word_count == 0


# ---------------------------------------------------------------------------
# Behavior 2: SectionDraft is frozen with iteration tracking
# ---------------------------------------------------------------------------


class TestSectionDraftImmutability:
    def test_draft_is_frozen_value_object(self):
        draft = SectionDraft(
            section_id="intro",
            content="Introduction text here.",
            compliance_item_ids=[],
            iteration=1,
        )

        with pytest.raises(AttributeError):
            draft.content = "modified"  # type: ignore[misc]

    def test_draft_tracks_iteration_round(self):
        draft = SectionDraft(
            section_id="tech-approach",
            content="First draft content.",
            compliance_item_ids=["CI-001"],
            iteration=3,
        )

        assert draft.iteration == 3
