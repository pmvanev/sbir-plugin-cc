"""Keyword pre-filter -- pure domain logic for topic-capability matching.

Matches topic metadata (titles, codes) against company profile capability
keywords. No I/O dependencies -- operates on in-memory data structures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FilterResult:
    """Result of keyword pre-filtering."""

    candidates: list[dict[str, Any]] = field(default_factory=list)
    eliminated_count: int = 0
    warnings: list[str] = field(default_factory=list)


class KeywordPreFilter:
    """Filters topics against company profile capability keywords.

    Pure domain logic -- no I/O, no external dependencies.
    """

    def filter(
        self,
        topics: list[dict[str, Any]],
        capabilities: list[str],
    ) -> FilterResult:
        """Filter topics by matching against capability keywords.

        Args:
            topics: List of topic dicts with at least 'title' and 'topic_code'.
            capabilities: List of capability keyword strings from company profile.

        Returns:
            FilterResult with matched candidates and elimination count.
        """
        warnings: list[str] = []

        if not capabilities:
            warnings.append(
                "No capability keywords in profile -- all topics passed"
            )
            return FilterResult(
                candidates=list(topics),
                eliminated_count=0,
                warnings=warnings,
            )

        caps_lower = [c.lower() for c in capabilities]
        candidates: list[dict[str, Any]] = []
        eliminated = 0

        for topic in topics:
            title_lower = topic.get("title", "").lower()
            code_lower = topic.get("topic_code", "").lower()
            searchable = f"{title_lower} {code_lower}"

            matched = [cap for cap, cap_l in zip(capabilities, caps_lower)
                       if cap_l in searchable]

            if matched:
                candidate = dict(topic)
                candidate["matched_keywords"] = matched
                candidates.append(candidate)
            else:
                eliminated += 1

        if candidates:
            warnings.append(
                f"Keyword match: {len(candidates)} candidate topics "
                f"({eliminated} eliminated)"
            )
        else:
            warnings.append("No topics matched your company profile")
            warnings.append(
                "Review your profile capabilities or broaden your filters"
            )

        return FilterResult(
            candidates=candidates,
            eliminated_count=eliminated,
            warnings=warnings,
        )
