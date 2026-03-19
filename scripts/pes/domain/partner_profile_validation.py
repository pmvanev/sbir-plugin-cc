"""Partner profile validation service -- driving port for partner schema enforcement.

Validates partner profile dicts against the JSON Schema template
and additional business rules (slug format, STTR eligibility, etc.).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema


@dataclass
class PartnerValidationError:
    """A single validation error with field and message."""

    field: str
    message: str
    expected: str = ""


@dataclass
class PartnerValidationResult:
    """Result of partner profile validation."""

    valid: bool
    errors: list[PartnerValidationError] = field(default_factory=list)


_SCHEMA_PATH = Path(__file__).resolve().parents[3] / "templates" / "partner-profile-schema.json"


def _load_schema() -> dict[str, Any]:
    """Load the partner profile JSON Schema."""
    text = _SCHEMA_PATH.read_text(encoding="utf-8")
    result: dict[str, Any] = json.loads(text)
    return result


def generate_slug(name: str) -> str:
    """Generate a deterministic slug from a partner name.

    Lowercase, replace non-alphanumeric with hyphens, collapse multiples, trim.
    """
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug


class PartnerProfileValidationService:
    """Validates partner profiles against schema and business rules."""

    def __init__(self) -> None:
        self._schema = _load_schema()

    def validate(self, profile: dict[str, Any]) -> PartnerValidationResult:
        """Validate a partner profile dict."""
        errors: list[PartnerValidationError] = []

        validator = jsonschema.Draft202012Validator(self._schema)
        for error in validator.iter_errors(profile):
            field_path = ".".join(str(p) for p in error.absolute_path) or error.json_path
            errors.append(PartnerValidationError(
                field=field_path,
                message=error.message,
                expected=str(error.schema.get("type", "")),
            ))

        errors.extend(self._validate_partner_name(profile))
        errors.extend(self._validate_slug_consistency(profile))
        errors.extend(self._validate_capabilities(profile))
        errors.extend(self._validate_partner_type(profile))
        errors.extend(self._validate_key_personnel(profile))

        return PartnerValidationResult(
            valid=len(errors) == 0,
            errors=errors,
        )

    def _validate_partner_name(self, profile: dict[str, Any]) -> list[PartnerValidationError]:
        """Validate partner name is non-empty."""
        errors: list[PartnerValidationError] = []
        name = profile.get("partner_name", "")
        if isinstance(name, str) and not name.strip():
            errors.append(PartnerValidationError(
                field="partner_name",
                message="Partner name is required and must not be empty",
                expected="non-empty string",
            ))
        return errors

    def _validate_slug_consistency(self, profile: dict[str, Any]) -> list[PartnerValidationError]:
        """Validate slug matches what would be generated from the name."""
        errors: list[PartnerValidationError] = []
        name = profile.get("partner_name", "")
        slug = profile.get("partner_slug", "")
        if name and slug:
            expected_slug = generate_slug(name)
            if slug != expected_slug:
                errors.append(PartnerValidationError(
                    field="partner_slug",
                    message=f"Slug '{slug}' does not match expected '{expected_slug}' derived from partner name",
                    expected=expected_slug,
                ))
        return errors

    def _validate_capabilities(self, profile: dict[str, Any]) -> list[PartnerValidationError]:
        """Validate capabilities has at least one entry."""
        errors: list[PartnerValidationError] = []
        caps = profile.get("capabilities")
        if isinstance(caps, list) and len(caps) == 0:
            errors.append(PartnerValidationError(
                field="capabilities",
                message="At least one capability is required",
                expected="non-empty array",
            ))
        return errors

    _VALID_TYPES = frozenset({"university", "federally_funded_rdc", "nonprofit_research"})

    def _validate_partner_type(self, profile: dict[str, Any]) -> list[PartnerValidationError]:
        """Validate partner type is one of the allowed values."""
        errors: list[PartnerValidationError] = []
        ptype = profile.get("partner_type", "")
        if ptype and ptype not in self._VALID_TYPES:
            errors.append(PartnerValidationError(
                field="partner_type",
                message=f"Partner type must be one of {sorted(self._VALID_TYPES)}, got '{ptype}'",
                expected=f"one of {sorted(self._VALID_TYPES)}",
            ))
        return errors

    def _validate_key_personnel(self, profile: dict[str, Any]) -> list[PartnerValidationError]:
        """Validate each key personnel entry has required fields."""
        errors: list[PartnerValidationError] = []
        personnel = profile.get("key_personnel", [])
        if not isinstance(personnel, list):
            return errors
        for i, person in enumerate(personnel):
            if not isinstance(person, dict):
                continue
            expertise = person.get("expertise", [])
            if isinstance(expertise, list) and len(expertise) == 0:
                errors.append(PartnerValidationError(
                    field=f"key_personnel.{i}.expertise",
                    message="Each key personnel entry requires at least one expertise keyword",
                    expected="non-empty array",
                ))
        return errors
