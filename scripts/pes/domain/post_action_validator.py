"""Post-action validation -- artifact placement and state file verification.

Validates that write operations produced correct results:
- Artifacts land in the correct wave directory
- State files are well-formed JSON after writes
"""

from __future__ import annotations

import json
import re
from typing import Any


# Wave number to directory name mapping
WAVE_DIR_NAMES: dict[int, str] = {
    0: "wave-0-discovery",
    1: "wave-1-strategy",
    2: "wave-2-research",
    3: "wave-3-outline",
    4: "wave-4-drafting",
    5: "wave-5-visuals",
    6: "wave-6-format",
    7: "wave-7-review",
    8: "wave-8-submission",
    9: "wave-9-learning",
}

# Tools that produce writable artifacts
WRITE_TOOLS = {"Write", "Edit"}


class PostActionValidator:
    """Validates post-action results for write operations."""

    def validate(
        self,
        state: dict[str, Any],
        tool_name: str,
        artifact_info: dict[str, Any],
    ) -> list[str]:
        """Validate a post-action result, returning warning messages.

        Returns empty list if everything is valid.
        Returns list of warning strings if issues are found.
        """
        if tool_name not in WRITE_TOOLS:
            return []

        file_path = artifact_info.get("file_path", "")
        messages: list[str] = []

        # Check artifact placement if writing to artifacts/ directory
        if "artifacts/" in file_path or "artifacts\\" in file_path:
            messages.extend(self._check_artifact_placement(state, file_path))

        # Check state file well-formedness if writing to proposal-state.json
        if file_path.endswith("proposal-state.json"):
            messages.extend(self._check_state_file(file_path))

        return messages

    def _check_artifact_placement(
        self, state: dict[str, Any], file_path: str,
    ) -> list[str]:
        """Check if artifact is in the correct wave directory."""
        current_wave = state.get("current_wave", 0)
        expected_dir = WAVE_DIR_NAMES.get(current_wave, f"wave-{current_wave}")

        # Normalize path separators
        normalized = file_path.replace("\\", "/")

        # Extract wave directory from path
        match = re.search(r"artifacts/(wave-\d+-\w+)", normalized)
        if not match:
            return []

        actual_dir = match.group(1)
        if actual_dir != expected_dir:
            return [
                f"Artifact placed in '{actual_dir}' but current wave expects "
                f"'{expected_dir}'. File: {file_path}"
            ]

        return []

    def _check_state_file(self, file_path: str) -> list[str]:
        """Check if a state file is well-formed JSON."""
        try:
            with open(file_path, "r") as f:
                json.load(f)
        except FileNotFoundError:
            return [f"State file not found: {file_path}"]
        except json.JSONDecodeError as e:
            return [f"State file is malformed JSON: {e}"]
        return []
