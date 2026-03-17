"""Domain service for mid-proposal format configuration changes.

FormatConfigService validates format values, determines rework risk
by wave number, and persists updates via the StateWriter port.

Pure domain logic -- no infrastructure imports.
"""

from __future__ import annotations

from typing import Any

VALID_FORMATS = ("latex", "docx")
REWORK_WARNING_WAVE_THRESHOLD = 3


class FormatConfigService:
    """Driving port: manages output format changes for an active proposal.

    Collaborators injected via constructor:
    - state_writer: object with save(state) method (StateWriter port)
    """

    def __init__(self, state_writer: Any) -> None:
        self._state_writer = state_writer

    def change_format(
        self, state: dict[str, Any], new_format: str
    ) -> dict[str, Any]:
        """Validate and apply a format change to the proposal state.

        Returns a result dict with keys:
        - success: bool
        - rework_warning: bool
        - error: str (only when success is False)
        - warning_message: str (only when rework_warning is True)
        - warning_wave: int (only when rework_warning is True)
        """
        normalized = new_format.strip().lower()

        if normalized not in VALID_FORMATS:
            return {
                "success": False,
                "error": (
                    f"Invalid format '{new_format}'. "
                    f"Valid options: {', '.join(VALID_FORMATS)}"
                ),
                "rework_warning": False,
            }

        current_format = state.get("output_format", "docx")

        # Same format = no-op
        if normalized == current_format:
            return {
                "success": True,
                "rework_warning": False,
            }

        current_wave = state.get("current_wave", 0)

        # Apply the change
        state["output_format"] = normalized
        self._state_writer.save(state)

        # Wave 3+ triggers rework warning
        if current_wave >= REWORK_WARNING_WAVE_THRESHOLD:
            return {
                "success": True,
                "rework_warning": True,
                "warning_wave": current_wave,
                "warning_message": (
                    f"Changing format at Wave {current_wave} may require "
                    "rework. Outline and draft work may need adjustment."
                ),
            }

        return {
            "success": True,
            "rework_warning": False,
        }
