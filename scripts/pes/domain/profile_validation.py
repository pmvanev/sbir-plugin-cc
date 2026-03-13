"""Profile validation service -- driving port for schema enforcement.

Validates company profile dicts against the JSON Schema template
and additional business rules (CAGE code format, employee count, etc.).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema


@dataclass
class ValidationError:
    """A single validation error with field and message."""

    field: str
    message: str
    expected: str = ""


@dataclass
class ValidationResult:
    """Result of profile validation."""

    valid: bool
    errors: list[ValidationError] = field(default_factory=list)


# Path to the JSON Schema template
_SCHEMA_PATH = Path(__file__).resolve().parents[3] / "templates" / "company-profile-schema.json"


def _load_schema() -> dict[str, Any]:
    """Load the company profile JSON Schema."""
    text = _SCHEMA_PATH.read_text(encoding="utf-8")
    result: dict[str, Any] = json.loads(text)
    return result


class ProfileValidationService:
    """Validates company profiles against schema and business rules."""

    def __init__(self) -> None:
        self._schema = _load_schema()

    def validate(self, profile: dict[str, Any]) -> ValidationResult:
        """Validate a company profile dict.

        Runs JSON Schema validation first, then additional business rules
        for CAGE code format, conditional requirements, etc.
        """
        errors: list[ValidationError] = []

        # JSON Schema validation
        validator = jsonschema.Draft202012Validator(self._schema)
        for error in validator.iter_errors(profile):
            field_path = ".".join(str(p) for p in error.absolute_path) or error.json_path
            errors.append(ValidationError(
                field=field_path,
                message=error.message,
                expected=str(error.schema.get("type", "")),
            ))

        # Business rules beyond JSON Schema
        errors.extend(self._validate_cage_code(profile))
        errors.extend(self._validate_employee_count(profile))

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
        )

    def _validate_cage_code(self, profile: dict[str, Any]) -> list[ValidationError]:
        """Validate CAGE code format: exactly 5 alphanumeric characters when SAM active."""
        errors: list[ValidationError] = []
        certs = profile.get("certifications", {})
        sam = certs.get("sam_gov", {})

        if not sam.get("active", False):
            return errors

        cage = sam.get("cage_code", "")
        if cage and len(cage) != 5:
            errors.append(ValidationError(
                field="certifications.sam_gov.cage_code",
                message="CAGE code must be exactly 5 alphanumeric characters",
                expected="5 alphanumeric characters",
            ))
        elif cage and not re.match(r"^[A-Za-z0-9]{5}$", cage):
            errors.append(ValidationError(
                field="certifications.sam_gov.cage_code",
                message="CAGE code must contain only alphanumeric characters (5 alphanumeric)",
                expected="5 alphanumeric characters",
            ))

        return errors

    def _validate_employee_count(self, profile: dict[str, Any]) -> list[ValidationError]:
        """Validate employee count is positive."""
        errors: list[ValidationError] = []
        count = profile.get("employee_count")

        if isinstance(count, int) and count <= 0:
            errors.append(ValidationError(
                field="employee_count",
                message="Employee count must be a positive integer greater than 0",
                expected="positive integer",
            ))

        return errors
