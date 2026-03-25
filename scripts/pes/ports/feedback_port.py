"""Port interface for feedback persistence.

FeedbackWriterPort defines the business contract for writing feedback entries.
Adapters implement this for specific infrastructure (filesystem, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from pes.domain.feedback import FeedbackEntry


class FeedbackWriterPort(ABC):
    """Write a feedback entry to a persistent store -- driven port."""

    @abstractmethod
    def write(self, entry: FeedbackEntry, output_dir: Path) -> Path:
        """Persist a feedback entry atomically.

        Creates output_dir if absent.
        Filename: feedback-{timestamp}.json with colons replaced by hyphens.
        Writes to .tmp, backs up existing to .bak, renames .tmp to target.

        Returns the Path of the written file.
        """
