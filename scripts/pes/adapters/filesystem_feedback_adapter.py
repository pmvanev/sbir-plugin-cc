"""Filesystem adapter for feedback entry persistence.

Implements FeedbackWriterPort using JSON files with atomic write pattern:
write .tmp -> backup .bak -> rename .tmp to target.
"""

from __future__ import annotations

import json
from pathlib import Path

from pes.domain.feedback import FeedbackEntry
from pes.ports.feedback_port import FeedbackWriterPort


class FilesystemFeedbackAdapter(FeedbackWriterPort):
    """JSON file-based feedback persistence with atomic writes."""

    def write(self, entry: FeedbackEntry, output_dir: Path) -> Path:
        """Persist a feedback entry atomically.

        Creates output_dir if absent.
        Filename: feedback-{timestamp}.json with colons replaced by hyphens.
        Writes to .tmp, backs up existing to .bak, renames .tmp to target.

        Returns the Path of the written file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = "feedback-" + entry.timestamp.replace(":", "-") + ".json"
        target_file = output_dir / filename
        tmp_file = output_dir / (filename + ".tmp")
        bak_file = output_dir / (filename + ".bak")

        # Write to temporary file first
        tmp_file.write_text(
            json.dumps(entry.to_dict(), indent=2), encoding="utf-8"
        )

        # Backup existing file if present
        if target_file.exists():
            bak_file.write_bytes(target_file.read_bytes())

        # Atomic rename: .tmp -> target
        tmp_file.replace(target_file)

        return target_file
