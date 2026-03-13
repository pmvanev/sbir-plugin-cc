"""Profile section update service.

Applies selective updates to an existing company profile:
- Array fields (past_performance, key_personnel, capabilities,
  research_institution_partners) append new entries.
- Scalar fields (employee_count, company_name) replace the value.
- Nested dot-path fields (certifications.sam_gov.cage_code) replace
  at the specified path.
"""

from __future__ import annotations

import copy
from typing import Any


def apply_section_update(
    profile: dict[str, Any],
    update: dict[str, Any],
) -> dict[str, Any]:
    """Apply a single section update to a profile and return the result.

    The update dict must contain:
        section: str   -- field name or dot-path (e.g. "employee_count",
                          "certifications.sam_gov")
        action:  str   -- "append" or "replace"
        value:   Any   -- the new value or entry to append

    Returns a new dict; the original profile is not mutated.
    """
    result = copy.deepcopy(profile)
    section = update["section"]
    action = update["action"]
    value = update["value"]

    if action == "append":
        _append_to_array(result, section, value)
    else:
        _replace_value(result, section, value)

    return result


def _append_to_array(
    profile: dict[str, Any],
    section: str,
    value: Any,
) -> None:
    """Append a value to an array field in the profile."""
    current = profile.get(section, [])
    if not isinstance(current, list):
        current = []
    current.append(value)
    profile[section] = current


def _replace_value(
    profile: dict[str, Any],
    section: str,
    value: Any,
) -> None:
    """Replace a scalar or nested value at the given dot-path."""
    parts = section.split(".")
    target = profile
    for part in parts[:-1]:
        target = target.setdefault(part, {})
    target[parts[-1]] = value
