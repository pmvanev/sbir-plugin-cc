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
