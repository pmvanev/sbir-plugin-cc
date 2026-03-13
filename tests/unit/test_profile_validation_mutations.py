"""Targeted tests for profile_validation.py mutation coverage.

These tests assert on specific field values, exact message content,
boundary conditions, and absent-key behaviors that BDD acceptance
tests don't cover at sufficient granularity.
"""

from __future__ import annotations

import pytest

from pes.domain.profile_validation import (
    ProfileValidationService,
    ValidationError,
    ValidationResult,
)


@pytest.fixture()
def service():
    return ProfileValidationService()


def _valid_profile(**overrides):
    """Build a minimal valid profile with optional overrides."""
    profile = {
        "company_name": "Acme Corp",
        "employee_count": 50,
        "capabilities": ["directed energy"],
        "certifications": {
            "sam_gov": {
                "active": True,
                "cage_code": "1A2B3",
                "uei": "ABC123456789",
            },
            "socioeconomic": [],
        },
        "key_personnel": [{"name": "Jane", "role": "PI"}],
        "past_performance": [{"agency": "DoD"}],
    }
    for key, val in overrides.items():
        if "." in key:
            parts = key.split(".")
            target = profile
            for p in parts[:-1]:
                target = target.setdefault(p, {})
            target[parts[-1]] = val
        else:
            profile[key] = val
    return profile


# --- Dataclass default tests (kills mutants 2, 3, 5) ---


class TestDataclassDefaults:
    def test_validation_error_expected_defaults_to_empty_string(self):
        err = ValidationError(field="x", message="y")
        assert err.expected == ""
        assert isinstance(err.expected, str)

    def test_validation_result_errors_defaults_to_empty_list(self):
        result = ValidationResult(valid=True)
        assert result.errors == []
        assert isinstance(result.errors, list)


# --- Exact message and expected field tests (kills mutants 21, 22, 40, 41, 46, 47) ---


class TestCageCodeValidation:
    def test_cage_wrong_length_message(self, service):
        profile = _valid_profile(**{"certifications.sam_gov.cage_code": "ABC"})
        result = service.validate(profile)
        cage_errors = [e for e in result.errors if "cage_code" in e.field]
        assert len(cage_errors) == 1
        assert cage_errors[0].message == "CAGE code must be exactly 5 alphanumeric characters"
        assert cage_errors[0].expected == "5 alphanumeric characters"

    def test_cage_invalid_chars_message(self, service):
        profile = _valid_profile(**{"certifications.sam_gov.cage_code": "AB!@#"})
        result = service.validate(profile)
        cage_errors = [e for e in result.errors if "cage_code" in e.field]
        assert len(cage_errors) == 1
        assert cage_errors[0].message == "CAGE code must contain only alphanumeric characters (5 alphanumeric)"
        assert cage_errors[0].expected == "5 alphanumeric characters"

    def test_absent_cage_code_with_active_sam_no_error(self, service):
        """When cage_code key is absent but SAM is active, no CAGE error."""
        profile = _valid_profile()
        del profile["certifications"]["sam_gov"]["cage_code"]
        result = service.validate(profile)
        cage_errors = [e for e in result.errors if "cage_code" in e.field]
        assert len(cage_errors) == 0


# --- SAM active default tests (kills mutants 32, 73) ---


class TestSamActiveDefault:
    def test_absent_active_key_treated_as_inactive(self, service):
        """When 'active' key is absent from sam_gov, default is False (inactive)."""
        profile = _valid_profile()
        del profile["certifications"]["sam_gov"]["active"]
        del profile["certifications"]["sam_gov"]["cage_code"]
        del profile["certifications"]["sam_gov"]["uei"]
        result = service.validate(profile)
        # No CAGE or UEI errors because SAM is treated as inactive
        cage_errors = [e for e in result.errors if "cage_code" in e.field]
        uei_errors = [e for e in result.errors if "uei" in e.field]
        assert len(cage_errors) == 0
        assert len(uei_errors) == 0

    def test_absent_active_key_with_bad_cage_skips_validation(self, service):
        """Bad CAGE code should NOT be flagged when 'active' key is absent."""
        profile = _valid_profile()
        del profile["certifications"]["sam_gov"]["active"]
        profile["certifications"]["sam_gov"]["cage_code"] = "BAD"
        result = service.validate(profile)
        cage_errors = [e for e in result.errors if "cage_code" in e.field]
        assert len(cage_errors) == 0


# --- Company name tests (kills mutants 50, 55, 56) ---


class TestCompanyNameValidation:
    def test_absent_company_name_key(self, service):
        """When company_name key is entirely absent, no company name error."""
        profile = _valid_profile()
        del profile["company_name"]
        result = service.validate(profile)
        name_errors = [e for e in result.errors if e.field == "company_name"]
        # absent key → get returns "" → empty string → error
        # But if mutant changes default to "XXXX", no error
        assert len(name_errors) == 1
        assert name_errors[0].message == "Company name is required and must not be empty"
        assert name_errors[0].expected == "non-empty string"

    def test_empty_company_name_message(self, service):
        profile = _valid_profile(company_name="")
        result = service.validate(profile)
        name_errors = [e for e in result.errors if e.field == "company_name"]
        assert len(name_errors) == 1
        assert name_errors[0].message == "Company name is required and must not be empty"
        assert name_errors[0].expected == "non-empty string"


# --- Capabilities tests (kills mutants 64, 65) ---


class TestCapabilitiesValidation:
    def test_empty_capabilities_message(self, service):
        profile = _valid_profile(capabilities=[])
        result = service.validate(profile)
        cap_errors = [e for e in result.errors if e.field == "capabilities"]
        assert len(cap_errors) == 1
        assert cap_errors[0].message == "At least one capability is required"
        assert cap_errors[0].expected == "non-empty array"


# --- UEI tests (kills mutants 75, 79, 80) ---


class TestUeiValidation:
    def test_absent_uei_with_active_sam(self, service):
        """When uei key is absent and SAM is active, UEI error is raised."""
        profile = _valid_profile()
        del profile["certifications"]["sam_gov"]["uei"]
        result = service.validate(profile)
        uei_errors = [e for e in result.errors if "uei" in e.field]
        assert len(uei_errors) == 1
        assert uei_errors[0].message == "UEI is required when SAM.gov registration is active"
        assert uei_errors[0].expected == "non-empty UEI string"


# --- Employee count boundary test (kills mutant 85) ---


class TestEmployeeCountBoundary:
    def test_employee_count_one_is_valid(self, service):
        """employee_count=1 is valid (boundary: <= 0 triggers error, not <= 1)."""
        profile = _valid_profile(employee_count=1)
        result = service.validate(profile)
        count_errors = [e for e in result.errors if e.field == "employee_count"]
        assert len(count_errors) == 0

    def test_employee_count_zero_message(self, service):
        profile = _valid_profile(employee_count=0)
        result = service.validate(profile)
        count_errors = [e for e in result.errors if e.field == "employee_count"]
        assert len(count_errors) == 1
        assert count_errors[0].message == "Employee count must be a positive integer greater than 0"
        assert count_errors[0].expected == "positive integer"


# --- Socioeconomic validation (kills mutants 90-95, 105, 106, 107) ---


class TestSocioeconomicValidation:
    @pytest.mark.parametrize("cert", ["8(a)", "HUBZone", "SDVOSB", "WOSB", "EDWOSB", "SDB"])
    def test_each_valid_socioeconomic_accepted(self, service, cert):
        """Each valid socioeconomic value must be accepted without error."""
        profile = _valid_profile(**{"certifications.socioeconomic": [cert]})
        result = service.validate(profile)
        socio_errors = [e for e in result.errors if "socioeconomic" in e.field]
        assert len(socio_errors) == 0

    def test_invalid_socioeconomic_message(self, service):
        profile = _valid_profile(**{"certifications.socioeconomic": ["INVALID"]})
        result = service.validate(profile)
        socio_errors = [e for e in result.errors if "socioeconomic" in e.field]
        assert len(socio_errors) == 1
        assert socio_errors[0].message.startswith("Invalid socioeconomic certification")
        assert "Allowed values:" in socio_errors[0].message
        assert socio_errors[0].expected.startswith("one of")


# --- Schema validation expected field (kills mutant 21) ---


class TestSchemaValidationExpected:
    def test_schema_error_includes_type_in_expected(self, service):
        """JSON Schema errors should extract 'type' from schema, not 'XXtypeXX'."""
        profile = _valid_profile(employee_count="not-a-number")
        result = service.validate(profile)
        schema_errors = [e for e in result.errors if e.field == "employee_count"]
        # At least one schema error should have a non-empty expected from type key
        type_expected = [e for e in schema_errors if e.expected]
        assert len(type_expected) > 0
