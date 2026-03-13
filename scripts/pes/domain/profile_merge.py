"""Profile extraction merge service.

Assembles extracted data from documents into profile drafts.
Supports additive merging of multiple extractions and
completeness checking against the full profile schema.
"""

from __future__ import annotations

from typing import Any


# Sections that must be populated for a complete profile.
REQUIRED_SECTIONS = frozenset({
    "capabilities",
    "certifications",
    "key_personnel",
    "past_performance",
    "research_institution_partners",
})


def assemble_draft(extraction: dict[str, Any]) -> dict[str, Any]:
    """Assemble extracted data into a profile draft.

    Returns a dict containing only the fields present in the extraction.
    Empty extractions produce an empty dict.
    """
    if not extraction:
        return {}
    # Return a shallow copy -- extraction IS the draft
    return dict(extraction)


def merge_extractions(*extractions: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple extraction dicts additively into a single draft.

    Later extractions add to (not replace) earlier ones.
    Nested dicts (like certifications) are deep-merged.
    Lists are concatenated with deduplication.
    Scalars from later extractions overwrite earlier ones.
    """
    result: dict[str, Any] = {}
    for ext in extractions:
        _deep_merge(result, ext)
    return result


def check_completeness(draft: dict[str, Any]) -> list[str]:
    """Return a list of profile sections that are missing from the draft.

    A section is missing if it is absent or has an empty value
    (empty list, empty dict, None).
    """
    missing: list[str] = []
    for section in sorted(REQUIRED_SECTIONS):
        value = draft.get(section)
        if value is None or value == [] or value == {}:
            missing.append(section)
    return missing


def _deep_merge(target: dict[str, Any], source: dict[str, Any]) -> None:
    """Deep-merge source into target, mutating target in place."""
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_merge(target[key], value)
        elif key in target and isinstance(target[key], list) and isinstance(value, list):
            # Additive: extend, deduplicate preserving order
            seen = set()
            merged: list[Any] = []
            for item in target[key] + value:
                item_key = _hashable(item)
                if item_key not in seen:
                    seen.add(item_key)
                    merged.append(item)
            target[key] = merged
        else:
            target[key] = value


def _hashable(item: Any) -> Any:
    """Make an item hashable for deduplication."""
    if isinstance(item, dict):
        return tuple(sorted(item.items()))
    return item
