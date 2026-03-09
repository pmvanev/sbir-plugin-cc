"""Draft domain models -- value objects for section drafting.

Pure domain objects with no infrastructure imports.
SectionDraft captures a section draft with compliance traceability,
word count (computed from content), and iteration tracking.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectionDraft:
    """A single section draft with compliance traceability and iteration tracking.

    Word count is computed from content automatically.
    Frozen value object -- immutable after creation.
    """

    section_id: str
    content: str
    compliance_item_ids: list[str]
    iteration: int

    @property
    def word_count(self) -> int:
        """Word count computed from content."""
        if not self.content:
            return 0
        return len(self.content.split())
