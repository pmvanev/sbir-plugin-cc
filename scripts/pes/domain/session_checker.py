"""Session startup integrity checker -- domain service.

Detects orphaned files, deadline proximity, and corrupted state.
Called by EnforcementEngine.check_session_start().
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

DEADLINE_CRITICAL_DAYS = 3
DEADLINE_WARNING_DAYS = 7
DRAFT_EXTENSIONS = {".md", ".txt", ".docx"}


class SessionChecker:
    """Check proposal integrity at session startup."""

    def check(
        self,
        state: dict,
        proposal_dir: str | None = None,
    ) -> list[str]:
        """Run all integrity checks and return warning messages.

        Returns empty list for clean state.
        """
        messages: list[str] = []
        messages.extend(self._check_corrupted_state(state))
        messages.extend(self._check_deadline_proximity(state))
        if proposal_dir:
            messages.extend(self._check_orphaned_files(state, proposal_dir))
        return messages

    def _check_corrupted_state(self, state: dict) -> list[str]:
        """Check for corrupted state flag set by adapter layer."""
        if not state.get("_corrupted"):
            return []

        messages = ["Proposal state appears corrupted."]
        recovered = state.get("_recovered_state")
        if recovered:
            messages.append(
                "Recovery from backup succeeded. "
                "Review recovered state and re-save to confirm."
            )
        else:
            messages.append(
                "No backup available for recovery. "
                "Manual state reconstruction may be required."
            )
        return messages

    def _check_deadline_proximity(self, state: dict) -> list[str]:
        """Check if deadline is within warning threshold."""
        topic = state.get("topic", {})
        deadline_str = topic.get("deadline")
        if not deadline_str:
            return []

        try:
            deadline = date.fromisoformat(deadline_str)
        except ValueError:
            return []

        days_remaining = (deadline - date.today()).days
        if days_remaining <= DEADLINE_CRITICAL_DAYS:
            return [
                f"Critical deadline warning: {days_remaining} days remaining. "
                f"Prioritize completing in-progress work. "
                f"Consider: submit with available work or skip non-essential waves."
            ]
        if days_remaining <= DEADLINE_WARNING_DAYS:
            return [
                f"Deadline warning: {days_remaining} days remaining. "
                f"Prioritize completing in-progress work before starting new sections."
            ]
        return []

    def _check_orphaned_files(self, state: dict, proposal_dir: str) -> list[str]:
        """Detect draft files not tracked in state artifacts list."""
        tracked = set(state.get("artifacts", []))
        project_path = Path(proposal_dir)
        drafts_dir = project_path / "drafts"

        if not drafts_dir.exists():
            return []

        messages: list[str] = []
        for draft_file in sorted(drafts_dir.iterdir()):
            if draft_file.suffix not in DRAFT_EXTENSIONS:
                continue
            relative = f"drafts/{draft_file.name}"
            if relative not in tracked:
                section = draft_file.stem.replace("section-", "Section ")
                messages.append(
                    f"{section} draft exists but has no compliance matrix entry. "
                    f"Run compliance check to resolve."
                )
        return messages
