"""FeedbackSnapshotService -- pure context assembly for developer feedback.

All IO is performed by the caller. build_snapshot() accepts pre-read dicts
and mtimes; no file reads occur inside this module.

Privacy boundary: only the approved field list is extracted from incoming
dicts. Capability text, past_performance descriptions, draft content, and
key_personnel details are never added to the snapshot.
"""

from __future__ import annotations

import subprocess
import time
from typing import Any

from pes.domain.feedback import FeedbackSnapshot

# Fields allowed from finder topic entries.
_TOPIC_ALLOWED_FIELDS = {"topic_id", "composite_score", "recommendation"}

# Maximum number of top-scored topics to include.
_MAX_TOPICS = 5


class FeedbackSnapshotService:
    """Assembles a FeedbackSnapshot from pre-read state, profile, and finder dicts.

    No IO is performed inside build_snapshot(). All inputs are plain dicts or None.
    """

    def build_snapshot(
        self,
        *,
        state: dict[str, Any] | None,
        rigor: dict[str, Any] | None,
        profile: dict[str, Any] | None,
        finder: dict[str, Any] | None,
        mtimes: dict[str, float | None],
        cwd: str,
    ) -> FeedbackSnapshot:
        """Build a privacy-safe context snapshot from pre-read state.

        Args:
            state: Contents of active-proposal.json, or None if not present.
            rigor: Contents of rigor-profile.json, or None if not present.
            profile: Contents of company-profile.json, or None if not present.
            finder: Contents of finder-results.json, or None if not present.
            mtimes: Dict with keys 'state', 'profile', 'finder' holding float
                    mtime seconds-since-epoch, or None when file absent.
            cwd: Working directory for git rev-parse (project root).

        Returns:
            An immutable FeedbackSnapshot value object.
        """
        now = time.time()

        plugin_version = self._get_plugin_version(cwd)

        # --- From state ---
        proposal_id: str | None = None
        topic_id: str | None = None
        topic_title: str | None = None
        topic_agency: str | None = None
        topic_deadline: str | None = None
        topic_phase: str | None = None
        current_wave: int | None = None
        completed_waves: list[int] = []
        skipped_waves: list[int] = []
        generated_artifacts: list[str] = []

        if state is not None:
            proposal_id = state.get("id")
            topic_id = state.get("topic_id")
            topic_title = state.get("topic_title")
            topic_agency = state.get("topic_agency")
            topic_deadline = state.get("topic_deadline")
            topic_phase = state.get("topic_phase")
            generated_artifacts = list(state.get("generated_artifacts") or [])

            waves: dict[str, Any] = state.get("waves") or {}
            for wave_key, wave_data in waves.items():
                try:
                    wave_num = int(wave_key)
                except (ValueError, TypeError):
                    continue
                status = wave_data.get("status") if isinstance(wave_data, dict) else None
                if status == "completed":
                    completed_waves.append(wave_num)
                elif status == "skipped":
                    skipped_waves.append(wave_num)
                elif status == "active":
                    current_wave = wave_num

        # --- From rigor ---
        rigor_profile: str | None = None
        if rigor is not None:
            rigor_profile = rigor.get("profile")

        # --- From profile (privacy boundary: only company_name extracted) ---
        company_name: str | None = None
        if profile is not None:
            company_name = profile.get("company_name")

        # --- Age days from mtimes ---
        company_profile_age_days: int | None = _age_days(mtimes.get("profile"), now)
        finder_results_age_days: int | None = _age_days(mtimes.get("finder"), now)

        # --- From finder (top topics, limited and filtered) ---
        top_scored_topics: list[dict[str, Any]] = []
        if finder is not None:
            raw_topics: list[dict[str, Any]] = finder.get("topics") or []
            for topic in raw_topics[:_MAX_TOPICS]:
                top_scored_topics.append(
                    {k: topic[k] for k in _TOPIC_ALLOWED_FIELDS if k in topic}
                )

        return FeedbackSnapshot(
            plugin_version=plugin_version,
            proposal_id=proposal_id,
            topic_id=topic_id,
            topic_title=topic_title,
            topic_agency=topic_agency,
            topic_deadline=topic_deadline,
            topic_phase=topic_phase,
            current_wave=current_wave,
            completed_waves=completed_waves,
            skipped_waves=skipped_waves,
            rigor_profile=rigor_profile,
            company_name=company_name,
            company_profile_age_days=company_profile_age_days,
            finder_results_age_days=finder_results_age_days,
            top_scored_topics=top_scored_topics,
            generated_artifacts=generated_artifacts,
        )

    @staticmethod
    def _get_plugin_version(cwd: str) -> str:
        """Run git rev-parse --short HEAD in cwd. Returns 'unknown' on any error."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                cwd=cwd,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:  # noqa: BLE001
            pass
        return "unknown"


def _age_days(mtime: float | None, now: float) -> int | None:
    """Compute floor(age_days) from mtime seconds-since-epoch, or None."""
    if mtime is None:
        return None
    elapsed = now - mtime
    return int(elapsed / 86400)
