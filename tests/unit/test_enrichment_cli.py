"""Unit tests for enrichment_cli.py -- CLI composition root.

Tests exercise the CLI entry point by invoking the run() function with
crafted argv and capturing stdout. Service and adapter dependencies are
faked at the port boundary.

Test Budget: 5 behaviors x 2 = 10 max unit tests. Using 7.
Behaviors:
  B1: enrich mode -> EnrichmentResult JSON on stdout
  B2: diff mode -> ProfileDiff JSON on stdout
  B3: validate-key mode -> valid/invalid JSON on stdout
  B4: save-key mode -> reads stdin, confirmation JSON on stdout
  B5: error conditions -> structured JSON error on stdout (no stack traces)
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from pes.domain.enrichment import (
    EnrichedField,
    EnrichmentResult,
    FieldSource,
    SourceError,
)
from pes.domain.profile_diff import DiffEntry, ProfileDiff


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TIMESTAMP = "2026-03-26T14:00:00Z"


def _make_source(api_name: str) -> FieldSource:
    return FieldSource(api_name=api_name, api_url=f"https://{api_name}/test", accessed_at=_TIMESTAMP)


def _make_field(path: str, value: str, api_name: str) -> EnrichedField:
    return EnrichedField(
        field_path=path, value=value, source=_make_source(api_name), confidence="high",
    )


def _run_cli(argv: list[str], stdin_text: str = "") -> tuple[str, int]:
    """Run the CLI with given argv and return (stdout_text, exit_code)."""
    from pes.enrichment_cli import run

    captured = io.StringIO()
    stdin_backup = sys.stdin
    try:
        sys.stdin = io.StringIO(stdin_text)
        exit_code = run(argv, out=captured)
    finally:
        sys.stdin = stdin_backup
    return captured.getvalue(), exit_code


# ---------------------------------------------------------------------------
# B1: enrich mode -> EnrichmentResult JSON on stdout
# ---------------------------------------------------------------------------


def test_enrich_mode_outputs_enrichment_result_json(tmp_path: Path):
    """Given mode 'enrich' and a valid UEI, outputs EnrichmentResult JSON."""
    key_file = tmp_path / "api-keys.json"
    key_file.write_text(json.dumps({"sam_gov": "test-key-123"}))

    result = EnrichmentResult(
        uei="DKJF84NXLE73",
        fields=[_make_field("company_name", "Acme Corp", "SAM.gov")],
        missing_fields=["capabilities"],
        sources_attempted=["SAM.gov", "SBIR.gov", "USASpending.gov"],
        sources_succeeded=["SAM.gov"],
        errors=[],
    )

    with patch("pes.enrichment_cli.create_enrichment_service") as mock_create:
        mock_create.return_value.enrich.return_value = result
        stdout, exit_code = _run_cli(
            ["enrich", "--uei", "DKJF84NXLE73", "--key-dir", str(tmp_path)]
        )

    data = json.loads(stdout)
    assert exit_code == 0
    assert data["uei"] == "DKJF84NXLE73"
    assert data["sources_attempted"] == ["SAM.gov", "SBIR.gov", "USASpending.gov"]
    assert len(data["fields"]) == 1
    assert data["fields"][0]["field_path"] == "company_name"


# ---------------------------------------------------------------------------
# B2: diff mode -> ProfileDiff JSON on stdout
# ---------------------------------------------------------------------------


def test_diff_mode_outputs_profile_diff_json(tmp_path: Path):
    """Given mode 'diff' with UEI and profile path, outputs ProfileDiff JSON."""
    key_file = tmp_path / "api-keys.json"
    key_file.write_text(json.dumps({"sam_gov": "test-key-123"}))

    profile_path = tmp_path / "profile.json"
    profile_path.write_text(json.dumps({"company_name": "Old Name"}))

    diff = ProfileDiff(
        additions=[DiffEntry(field_path="cage_code", new_value="ABC12", source="SAM.gov")],
        changes=[DiffEntry(field_path="company_name", new_value="New Name", old_value="Old Name", source="SAM.gov")],
        matches=[],
        api_missing=[],
    )

    result = EnrichmentResult(
        uei="DKJF84NXLE73",
        fields=[_make_field("company_name", "New Name", "SAM.gov")],
        missing_fields=[],
        sources_attempted=["SAM.gov"],
        sources_succeeded=["SAM.gov"],
        errors=[],
    )

    with patch("pes.enrichment_cli.create_enrichment_service") as mock_create, \
         patch("pes.enrichment_cli.diff_profile") as mock_diff:
        mock_create.return_value.enrich.return_value = result
        mock_diff.return_value = diff
        stdout, exit_code = _run_cli([
            "diff", "--uei", "DKJF84NXLE73",
            "--profile-path", str(profile_path),
            "--key-dir", str(tmp_path),
        ])

    data = json.loads(stdout)
    assert exit_code == 0
    assert data["has_changes"] is True
    assert len(data["additions"]) == 1
    assert len(data["changes"]) == 1


# ---------------------------------------------------------------------------
# B3: validate-key mode -> valid/invalid JSON on stdout
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key_present,expected_valid", [
    (True, True),
    (False, False),
])
def test_validate_key_mode_outputs_validation_status(
    tmp_path: Path, key_present: bool, expected_valid: bool,
):
    """Given mode 'validate-key', outputs JSON with valid/invalid status."""
    if key_present:
        key_file = tmp_path / "api-keys.json"
        key_file.write_text(json.dumps({"sam_gov": "test-key-123"}))

    stdout, exit_code = _run_cli([
        "validate-key", "--service", "sam_gov", "--key-dir", str(tmp_path),
    ])

    data = json.loads(stdout)
    assert exit_code == 0
    assert data["valid"] is expected_valid
    assert data["service"] == "sam_gov"


# ---------------------------------------------------------------------------
# B4: save-key mode -> reads stdin, confirmation JSON on stdout
# ---------------------------------------------------------------------------


def test_save_key_mode_reads_stdin_and_confirms(tmp_path: Path):
    """Given mode 'save-key' with key on stdin, saves and outputs confirmation."""
    stdout, exit_code = _run_cli(
        ["save-key", "--service", "sam_gov", "--key-dir", str(tmp_path)],
        stdin_text="my-secret-api-key\n",
    )

    data = json.loads(stdout)
    assert exit_code == 0
    assert data["saved"] is True
    assert data["service"] == "sam_gov"

    # Verify key was actually persisted
    key_file = tmp_path / "api-keys.json"
    assert key_file.exists()
    stored = json.loads(key_file.read_text())
    assert stored["sam_gov"] == "my-secret-api-key"


# ---------------------------------------------------------------------------
# B5: Error conditions -> structured JSON error (no stack traces)
# ---------------------------------------------------------------------------


def test_enrich_with_invalid_uei_outputs_error_json(tmp_path: Path):
    """Given an invalid UEI, outputs structured JSON error."""
    stdout, exit_code = _run_cli([
        "enrich", "--uei", "SHORT", "--key-dir", str(tmp_path),
    ])

    data = json.loads(stdout)
    assert exit_code == 1
    assert data["error"] is True
    assert "UEI" in data["message"]
    assert "type" in data
    # No stack traces in output
    assert "Traceback" not in stdout


def test_enrich_service_exception_outputs_error_json(tmp_path: Path):
    """Given a service-level exception, outputs structured error (no stack trace)."""
    key_file = tmp_path / "api-keys.json"
    key_file.write_text(json.dumps({"sam_gov": "test-key-123"}))

    with patch("pes.enrichment_cli.create_enrichment_service") as mock_create:
        mock_create.return_value.enrich.side_effect = RuntimeError("Connection pool exhausted")
        stdout, exit_code = _run_cli([
            "enrich", "--uei", "DKJF84NXLE73", "--key-dir", str(tmp_path),
        ])

    data = json.loads(stdout)
    assert exit_code == 1
    assert data["error"] is True
    assert "Connection pool exhausted" in data["message"]
    assert "Traceback" not in stdout


# ---------------------------------------------------------------------------
# Mutation-killing tests
# ---------------------------------------------------------------------------


class TestEnrichmentCliMutationKillers:
    """Targeted tests to kill surviving mutants in enrichment_cli.py."""

    def test_default_key_dir_value(self):
        """Kill mutant: DEFAULT_KEY_DIR string mutation."""
        from pes.enrichment_cli import DEFAULT_KEY_DIR
        assert DEFAULT_KEY_DIR == "~/.sbir"

    def test_required_fields_exact_list(self):
        """Kill mutant: REQUIRED_FIELDS list mutations."""
        from pes.enrichment_cli import REQUIRED_FIELDS
        assert REQUIRED_FIELDS == [
            "company_name",
            "certifications.sam_gov.cage_code",
            "certifications.sam_gov.uei",
            "certifications.sam_gov.active",
            "naics_codes",
            "sbir_awards",
            "federal_awards.total_amount",
        ]
        assert len(REQUIRED_FIELDS) == 7

    def test_error_response_structure(self):
        """Kill mutant: _error_response dict key/value mutations."""
        from pes.enrichment_cli import _error_response
        result = _error_response("test message", "test_type")
        assert result == {"error": True, "message": "test message", "type": "test_type"}

    def test_error_response_default_type(self):
        """Kill mutant: default error_type='error' mutation."""
        from pes.enrichment_cli import _error_response
        result = _error_response("msg")
        assert result["type"] == "error"

    def test_enrich_serialization_field_structure(self, tmp_path: Path):
        """Kill mutant: _serialize_enrichment_result dict key mutations."""
        key_file = tmp_path / "api-keys.json"
        key_file.write_text(json.dumps({"sam_gov": "test-key"}))

        source = _make_source("SAM.gov")
        err = SourceError(api_name="SBIR.gov", error_type="timeout", message="timed out", http_status=None)
        result = EnrichmentResult(
            uei="DKJF84NXLE73",
            fields=[EnrichedField(field_path="company_name", value="Acme", source=source, confidence="high")],
            missing_fields=["naics_codes"],
            sources_attempted=["SAM.gov", "SBIR.gov"],
            sources_succeeded=["SAM.gov"],
            errors=[err],
        )

        with patch("pes.enrichment_cli.create_enrichment_service") as mock_create:
            mock_create.return_value.enrich.return_value = result
            stdout, exit_code = _run_cli(
                ["enrich", "--uei", "DKJF84NXLE73", "--key-dir", str(tmp_path)]
            )

        data = json.loads(stdout)
        assert exit_code == 0
        # Exact key names in serialized output
        field = data["fields"][0]
        assert field["field_path"] == "company_name"
        assert field["value"] == "Acme"
        assert field["source"]["api_name"] == "SAM.gov"
        assert field["source"]["api_url"] == "https://SAM.gov/test"
        assert field["source"]["accessed_at"] == _TIMESTAMP
        assert field["confidence"] == "high"
        # Error serialization
        error = data["errors"][0]
        assert error["api_name"] == "SBIR.gov"
        assert error["error_type"] == "timeout"
        assert error["message"] == "timed out"
        assert error["http_status"] is None
        # Top-level fields
        assert data["missing_fields"] == ["naics_codes"]
        assert data["sources_succeeded"] == ["SAM.gov"]

    def test_diff_serialization_structure(self, tmp_path: Path):
        """Kill mutant: _serialize_profile_diff dict key mutations."""
        key_file = tmp_path / "api-keys.json"
        key_file.write_text(json.dumps({"sam_gov": "key"}))
        profile_path = tmp_path / "profile.json"
        profile_path.write_text(json.dumps({"company_name": "Old"}))

        diff = ProfileDiff(
            additions=[DiffEntry(field_path="cage", new_value="X", source="SAM.gov")],
            changes=[DiffEntry(field_path="name", new_value="New", old_value="Old", source="SAM.gov")],
            matches=[DiffEntry(field_path="uei", new_value="ABC", old_value="ABC", source="SAM.gov")],
            api_missing=[DiffEntry(field_path="phone", old_value="555-1234")],
        )
        result = EnrichmentResult(
            uei="DKJF84NXLE73", fields=[], missing_fields=[],
            sources_attempted=["SAM.gov"], sources_succeeded=["SAM.gov"], errors=[],
        )

        with patch("pes.enrichment_cli.create_enrichment_service") as mock_create, \
             patch("pes.enrichment_cli.diff_profile") as mock_diff:
            mock_create.return_value.enrich.return_value = result
            mock_diff.return_value = diff
            stdout, exit_code = _run_cli([
                "diff", "--uei", "DKJF84NXLE73",
                "--profile-path", str(profile_path),
                "--key-dir", str(tmp_path),
            ])

        data = json.loads(stdout)
        assert exit_code == 0
        # Exact keys in diff entries
        addition = data["additions"][0]
        assert addition["field_path"] == "cage"
        assert addition["new_value"] == "X"
        assert addition["old_value"] is None
        assert addition["source"] == "SAM.gov"
        change = data["changes"][0]
        assert change["old_value"] == "Old"
        match = data["matches"][0]
        assert match["field_path"] == "uei"
        api_miss = data["api_missing"][0]
        assert api_miss["field_path"] == "phone"
        assert api_miss["old_value"] == "555-1234"

    def test_invalid_arguments_returns_error(self):
        """Kill mutant: SystemExit catch and error response."""
        stdout, exit_code = _run_cli([])
        data = json.loads(stdout)
        assert exit_code == 1
        assert data["error"] is True
        assert data["type"] == "argument_error"
        assert "Invalid arguments" in data["message"]

    def test_save_key_empty_stdin_returns_error(self, tmp_path: Path):
        """Kill mutant: empty key check and validation_error type."""
        stdout, exit_code = _run_cli(
            ["save-key", "--service", "sam_gov", "--key-dir", str(tmp_path)],
            stdin_text="",
        )
        data = json.loads(stdout)
        assert exit_code == 1
        assert data["error"] is True
        assert data["type"] == "validation_error"
        assert "No key provided" in data["message"]

    def test_diff_missing_profile_file_returns_error(self, tmp_path: Path):
        """Kill mutant: FileNotFoundError handling in diff mode."""
        key_file = tmp_path / "api-keys.json"
        key_file.write_text(json.dumps({"sam_gov": "key"}))

        stdout, exit_code = _run_cli([
            "diff", "--uei", "DKJF84NXLE73",
            "--profile-path", str(tmp_path / "nonexistent.json"),
            "--key-dir", str(tmp_path),
        ])
        data = json.loads(stdout)
        assert exit_code == 1
        assert data["error"] is True
        assert data["type"] == "file_error"

    def test_diff_malformed_profile_returns_error(self, tmp_path: Path):
        """Kill mutant: JSONDecodeError handling in diff mode."""
        key_file = tmp_path / "api-keys.json"
        key_file.write_text(json.dumps({"sam_gov": "key"}))
        profile_path = tmp_path / "bad.json"
        profile_path.write_text("{not json!!!")

        stdout, exit_code = _run_cli([
            "diff", "--uei", "DKJF84NXLE73",
            "--profile-path", str(profile_path),
            "--key-dir", str(tmp_path),
        ])
        data = json.loads(stdout)
        assert exit_code == 1
        assert data["error"] is True
        assert data["type"] == "file_error"

    def test_diff_invalid_uei_returns_validation_error(self, tmp_path: Path):
        """Kill mutant: _validate_uei_or_error in diff mode."""
        stdout, exit_code = _run_cli([
            "diff", "--uei", "BAD",
            "--profile-path", str(tmp_path / "profile.json"),
            "--key-dir", str(tmp_path),
        ])
        data = json.loads(stdout)
        assert exit_code == 1
        assert data["error"] is True
        assert data["type"] == "validation_error"

    def test_validate_key_returns_service_name(self, tmp_path: Path):
        """Kill mutant: service field in validate-key response."""
        stdout, exit_code = _run_cli([
            "validate-key", "--service", "sbir_gov", "--key-dir", str(tmp_path),
        ])
        data = json.loads(stdout)
        assert exit_code == 0
        assert data["service"] == "sbir_gov"
        assert data["valid"] is False

    def test_save_key_returns_service_name(self, tmp_path: Path):
        """Kill mutant: service field in save-key response."""
        stdout, exit_code = _run_cli(
            ["save-key", "--service", "sbir_gov", "--key-dir", str(tmp_path)],
            stdin_text="my-key\n",
        )
        data = json.loads(stdout)
        assert exit_code == 0
        assert data["service"] == "sbir_gov"
        assert data["saved"] is True

    def test_runtime_error_type_in_response(self, tmp_path: Path):
        """Kill mutant: 'runtime_error' type string mutation."""
        key_file = tmp_path / "api-keys.json"
        key_file.write_text(json.dumps({"sam_gov": "key"}))

        with patch("pes.enrichment_cli.create_enrichment_service") as mock_create:
            mock_create.return_value.enrich.side_effect = RuntimeError("boom")
            stdout, exit_code = _run_cli([
                "enrich", "--uei", "DKJF84NXLE73", "--key-dir", str(tmp_path),
            ])

        data = json.loads(stdout)
        assert exit_code == 1
        assert data["type"] == "runtime_error"
