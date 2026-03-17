"""Domain service for proposal format configuration.

FormatConfigService validates format values, applies defaults, reads
effective format from state, determines rework risk by wave number,
and persists updates via the StateWriter port.

Pure domain logic -- no infrastructure imports.
"""

from __future__ import annotations

from typing import Any

VALID_FORMATS = ("latex", "docx")
DEFAULT_FORMAT = "docx"
REWORK_WARNING_WAVE_THRESHOLD = 3


class FormatConfigService:
    """Driving port: manages output format configuration for a proposal.

    Collaborators injected via constructor:
    - state_writer: object with save(state) method (StateWriter port)

    Static/class methods (get_effective_format, validate_format) require
    no collaborators and operate on state dicts directly.
    """

    def __init__(self, state_writer: Any) -> None:
        self._state_writer = state_writer

    # --- Setup-phase methods (US-PFS-001) ---

    def apply_selected_format(
        self, state: dict[str, Any], selected_format: str
    ) -> None:
        """Apply a user-selected format during proposal setup and persist.

        Normalizes and validates the format value, sets it on state,
        and saves via StateWriter.

        Raises ValueError for invalid format values.
        """
        normalized = selected_format.strip().lower()
        if normalized not in VALID_FORMATS:
            msg = (
                f"Invalid format '{selected_format}'. "
                f"Valid options: {', '.join(VALID_FORMATS)}"
            )
            raise ValueError(msg)
        state["output_format"] = normalized
        self._state_writer.save(state)

    def apply_default_format(self, state: dict[str, Any]) -> None:
        """Ensure output_format is set to the default and persist.

        Used when no explicit format selection is made during setup.
        """
        if "output_format" not in state:
            state["output_format"] = DEFAULT_FORMAT
        self._state_writer.save(state)

    @staticmethod
    def get_effective_format(state: dict[str, Any]) -> str:
        """Return the effective output format from a state dict.

        Missing output_format field defaults to 'docx' (legacy states).
        """
        return state.get("output_format", DEFAULT_FORMAT)

    @staticmethod
    def validate_format(state: dict[str, Any]) -> dict[str, Any]:
        """Validate the output_format field in a proposal state dict.

        Returns a result dict with keys:
        - valid: bool
        - error: str (only when valid is False)
        """
        fmt = state.get("output_format", "")
        if fmt not in VALID_FORMATS:
            return {
                "valid": False,
                "error": (
                    f"Invalid output_format '{fmt}'. "
                    f"Must be one of: {', '.join(VALID_FORMATS)}"
                ),
            }
        return {"valid": True}

    # --- Mid-proposal change method (US-PFS-002) ---

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
