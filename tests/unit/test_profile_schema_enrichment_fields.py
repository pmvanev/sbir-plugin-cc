"""Schema validation for enrichment-related profile fields.

Test Budget: 1 behavior x 2 = 2 max unit tests
- B1: Schema enforces naics_codes structure (valid structured array passes,
      invalid structure -- e.g., plain string items -- is rejected)
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "templates" / "company-profile-schema.json"


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _minimal_valid_profile() -> dict:
    """Minimal profile that satisfies all required fields."""
    return {
        "company_name": "Acme Defense",
        "capabilities": ["directed energy"],
        "certifications": {
            "sam_gov": {"active": True, "cage_code": "1ABC2", "uei": "DKJF84NXLE73"},
            "socioeconomic": [],
            "security_clearance": "none",
            "itar_registered": False,
        },
        "employee_count": 42,
        "key_personnel": [{"name": "Jane Doe", "role": "PI", "expertise": ["optics"]}],
        "past_performance": [{"agency": "DoD", "topic_area": "lasers", "outcome": "WIN"}],
        "research_institution_partners": ["MIT"],
    }


def test_naics_codes_with_valid_structured_objects_validates():
    """Schema accepts naics_codes as array of objects with code (required) and optional fields."""
    schema = _load_schema()
    profile = _minimal_valid_profile()
    profile["naics_codes"] = [
        {"code": "334511", "primary": True, "description": "Search and Navigation Equipment"},
        {"code": "541715", "primary": False},
    ]
    jsonschema.validate(profile, schema)


def test_naics_codes_rejects_plain_string_items():
    """Schema rejects naics_codes when items are plain strings instead of objects."""
    schema = _load_schema()
    profile = _minimal_valid_profile()
    profile["naics_codes"] = ["334511", "541715"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(profile, schema)
