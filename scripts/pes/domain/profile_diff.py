"""Profile diff logic -- comparing EnrichmentResult against existing profile.

Pure domain module. No infrastructure imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pes.domain.enrichment import EnrichmentResult


@dataclass(frozen=True)
class DiffEntry:
    """A single diff entry for a profile field."""

    field_path: str
    new_value: Any = None
    old_value: Any = None
    source: str = ""


@dataclass(frozen=True)
class ProfileDiff:
    """Result of comparing EnrichmentResult against existing profile."""

    additions: list[DiffEntry] = field(default_factory=list)
    changes: list[DiffEntry] = field(default_factory=list)
    matches: list[DiffEntry] = field(default_factory=list)
    api_missing: list[DiffEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.additions or self.changes)


def _resolve_path(profile: dict[str, Any], path: str) -> tuple[bool, Any]:
    """Resolve a dotted field path in a nested dict. Returns (found, value)."""
    parts = path.split(".")
    current: Any = profile
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _normalize_item(item: Any) -> Any:
    """Normalize a value for set-based comparison. Dicts become frozensets."""
    if isinstance(item, dict):
        return frozenset(item.items())
    return item


def _values_equal(old: Any, new: Any) -> bool:
    """Compare two values, using order-independent comparison for lists."""
    if isinstance(old, list) and isinstance(new, list):
        return _sets_equal(old, new)
    return old == new


def _sets_equal(old_list: list, new_list: list) -> bool:
    """Order-independent list comparison. Handles dicts by converting to frozensets."""
    if len(old_list) != len(new_list):
        return False
    return set(_normalize_item(x) for x in old_list) == set(_normalize_item(x) for x in new_list)


def _list_has_additions(old_list: list, new_list: list) -> bool:
    """Check if new_list contains items not in old_list."""
    old_set = set(_normalize_item(x) for x in old_list)
    new_set = set(_normalize_item(x) for x in new_list)
    return len(new_set - old_set) > 0


def diff_profile(
    enrichment: EnrichmentResult,
    existing_profile: dict[str, Any],
) -> ProfileDiff:
    """Compare enrichment result fields against existing profile JSON.

    For each enriched field, compares against the existing profile value
    at the same path. Array comparisons are order-independent.
    Existing profile fields not covered by any enriched field are
    flagged as api_missing.
    """
    additions: list[DiffEntry] = []
    changes: list[DiffEntry] = []
    matches: list[DiffEntry] = []
    api_missing: list[DiffEntry] = []

    enriched_paths: set[str] = set()

    for ef in enrichment.fields:
        enriched_paths.add(ef.field_path)
        found, old_value = _resolve_path(existing_profile, ef.field_path)
        source = ef.source.api_name

        if not found:
            # Field is new -- not in existing profile at all
            additions.append(DiffEntry(
                field_path=ef.field_path, new_value=ef.value, source=source,
            ))
        elif _values_equal(old_value, ef.value):
            matches.append(DiffEntry(
                field_path=ef.field_path, new_value=ef.value, old_value=old_value, source=source,
            ))
        elif isinstance(old_value, list) and isinstance(ef.value, list) and _list_has_additions(old_value, ef.value):
            # List with new items -- treat as addition (superset of old)
            additions.append(DiffEntry(
                field_path=ef.field_path, new_value=ef.value, old_value=old_value, source=source,
            ))
        else:
            changes.append(DiffEntry(
                field_path=ef.field_path, new_value=ef.value, old_value=old_value, source=source,
            ))

    # Identify existing profile fields not covered by any enrichment field
    _collect_api_missing(existing_profile, "", enriched_paths, api_missing)

    return ProfileDiff(
        additions=additions,
        changes=changes,
        matches=matches,
        api_missing=api_missing,
    )


def _collect_api_missing(
    profile: dict[str, Any],
    prefix: str,
    enriched_paths: set[str],
    api_missing: list[DiffEntry],
) -> None:
    """Recursively find top-level profile keys not covered by enrichment."""
    for key, value in profile.items():
        path = f"{prefix}.{key}" if prefix else key
        if path not in enriched_paths:
            # Check if any enriched path is a child of this path
            has_enriched_child = any(ep.startswith(path + ".") for ep in enriched_paths)
            if not has_enriched_child:
                api_missing.append(DiffEntry(field_path=path, old_value=value))
