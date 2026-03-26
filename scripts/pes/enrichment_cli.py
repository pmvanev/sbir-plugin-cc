"""Enrichment CLI -- composition root for company profile enrichment.

Entry point for the enrichment subsystem. Wires concrete adapters to the
EnrichmentService and dispatches to the requested mode. All output is JSON
to stdout for consumption by the agent layer.

Modes:
  enrich       -- Run three-API cascade for a UEI
  diff         -- Compare enrichment result against existing profile
  validate-key -- Check if an API key is stored for a service
  save-key     -- Save an API key from stdin
"""

from __future__ import annotations

import json
import sys
from io import StringIO
from typing import Any

import httpx

from pes.adapters.json_api_key_adapter import JsonApiKeyAdapter
from pes.adapters.sam_gov_adapter import SamGovAdapter
from pes.adapters.sbir_gov_adapter import SbirGovAdapter
from pes.adapters.usa_spending_adapter import UsaSpendingAdapter
from pes.domain.enrichment import EnrichmentResult, validate_uei
from pes.domain.enrichment_service import EnrichmentService
from pes.domain.profile_diff import ProfileDiff, diff_profile

DEFAULT_KEY_DIR = "~/.sbir"

REQUIRED_FIELDS = [
    "company_name",
    "certifications.sam_gov.cage_code",
    "certifications.sam_gov.uei",
    "certifications.sam_gov.active",
    "naics_codes",
    "sbir_awards",
    "federal_awards.total_amount",
]


def create_enrichment_service(key_dir: str) -> EnrichmentService:
    """Wire concrete adapters and return an EnrichmentService instance."""
    client = httpx.Client()
    sam = SamGovAdapter(client=client)
    sbir = SbirGovAdapter(client=client)
    usa = UsaSpendingAdapter(client=client)
    return EnrichmentService(
        sam_adapter=sam,
        sbir_adapter=sbir,
        usa_spending_adapter=usa,
        required_fields=REQUIRED_FIELDS,
    )


def _serialize_enrichment_result(result: EnrichmentResult) -> dict[str, Any]:
    """Convert EnrichmentResult to a JSON-serializable dict."""
    fields = [
        {
            "field_path": f.field_path,
            "value": f.value,
            "source": {
                "api_name": f.source.api_name,
                "api_url": f.source.api_url,
                "accessed_at": f.source.accessed_at,
            },
            "confidence": f.confidence,
        }
        for f in result.fields
    ]

    errors = [
        {
            "api_name": e.api_name,
            "error_type": e.error_type,
            "message": e.message,
            "http_status": e.http_status,
        }
        for e in result.errors
    ]

    return {
        "uei": result.uei,
        "fields": fields,
        "missing_fields": result.missing_fields,
        "sources_attempted": result.sources_attempted,
        "sources_succeeded": result.sources_succeeded,
        "errors": errors,
    }


def _serialize_profile_diff(diff: ProfileDiff) -> dict[str, Any]:
    """Convert ProfileDiff to a JSON-serializable dict."""
    def _entry(e: Any) -> dict[str, Any]:
        return {
            "field_path": e.field_path,
            "new_value": e.new_value,
            "old_value": e.old_value,
            "source": e.source,
        }

    return {
        "has_changes": diff.has_changes,
        "additions": [_entry(a) for a in diff.additions],
        "changes": [_entry(c) for c in diff.changes],
        "matches": [_entry(m) for m in diff.matches],
        "api_missing": [_entry(am) for am in diff.api_missing],
    }


def _error_response(message: str, error_type: str = "error") -> dict[str, Any]:
    """Build a structured error response."""
    return {"error": True, "message": message, "type": error_type}


def _validate_uei_or_error(uei: str, out: StringIO) -> bool:
    """Validate UEI and write error response if invalid. Returns True if valid."""
    validation = validate_uei(uei)
    if not validation.is_valid:
        json.dump(_error_response(validation.error or "Invalid UEI", "validation_error"), out)
        out.write("\n")
        return False
    return True


def _run_enrichment(uei: str, key_dir: str) -> EnrichmentResult:
    """Read API key, create service, and run enrichment cascade."""
    key_adapter = JsonApiKeyAdapter(key_dir)
    api_key = key_adapter.read_key("sam_gov")
    service = create_enrichment_service(key_dir)
    return service.enrich(uei=uei, api_key=api_key)


def _cmd_enrich(args: Any, key_dir: str, out: StringIO) -> int:
    """Handle 'enrich' subcommand."""
    if not _validate_uei_or_error(args.uei, out):
        return 1

    result = _run_enrichment(args.uei, key_dir)
    json.dump(_serialize_enrichment_result(result), out)
    out.write("\n")
    return 0


def _cmd_diff(args: Any, key_dir: str, out: StringIO) -> int:
    """Handle 'diff' subcommand."""
    if not _validate_uei_or_error(args.uei, out):
        return 1

    try:
        with open(args.profile_path, encoding="utf-8") as f:
            existing_profile = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        json.dump(_error_response(str(exc), "file_error"), out)
        out.write("\n")
        return 1

    result = _run_enrichment(args.uei, key_dir)
    diff = diff_profile(result, existing_profile)
    json.dump(_serialize_profile_diff(diff), out)
    out.write("\n")
    return 0


def _cmd_validate_key(args: Any, key_dir: str, out: StringIO) -> int:
    """Handle 'validate-key' subcommand."""
    key_adapter = JsonApiKeyAdapter(key_dir)
    key = key_adapter.read_key(args.service)

    response = {
        "valid": bool(key),
        "service": args.service,
    }
    json.dump(response, out)
    out.write("\n")
    return 0


def _cmd_save_key(args: Any, key_dir: str, out: StringIO) -> int:
    """Handle 'save-key' subcommand."""
    key = sys.stdin.readline().strip()
    if not key:
        json.dump(_error_response("No key provided on stdin", "validation_error"), out)
        out.write("\n")
        return 1

    key_adapter = JsonApiKeyAdapter(key_dir)
    key_adapter.write_key(args.service, key)

    response = {"saved": True, "service": args.service}
    json.dump(response, out)
    out.write("\n")
    return 0


def run(argv: list[str], out: StringIO | None = None) -> int:
    """Parse arguments and dispatch to the appropriate handler.

    Args:
        argv: Command-line arguments (without program name).
        out: Output stream (defaults to sys.stdout).

    Returns:
        Exit code (0 = success, 1 = error).
    """
    import argparse

    if out is None:
        out = sys.stdout  # type: ignore[assignment]

    parser = argparse.ArgumentParser(prog="enrichment_cli", description="Company profile enrichment CLI")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # Shared argument added to each subparser (avoids argparse ordering issues)
    def _add_key_dir(sub: argparse.ArgumentParser) -> None:
        sub.add_argument("--key-dir", default=DEFAULT_KEY_DIR, help="Directory for API key storage")

    # enrich
    enrich_parser = subparsers.add_parser("enrich", help="Run enrichment cascade for a UEI")
    enrich_parser.add_argument("--uei", required=True, help="12-character Unique Entity Identifier")
    enrich_parser.add_argument("--company-name", default=None, help="Company name (optional fallback)")
    _add_key_dir(enrich_parser)

    # diff
    diff_parser = subparsers.add_parser("diff", help="Compare enrichment against existing profile")
    diff_parser.add_argument("--uei", required=True, help="12-character Unique Entity Identifier")
    diff_parser.add_argument("--profile-path", required=True, help="Path to existing profile JSON")
    _add_key_dir(diff_parser)

    # validate-key
    validate_parser = subparsers.add_parser("validate-key", help="Check if API key is stored")
    validate_parser.add_argument("--service", required=True, help="Service name (e.g., sam_gov)")
    _add_key_dir(validate_parser)

    # save-key
    save_parser = subparsers.add_parser("save-key", help="Save API key from stdin")
    save_parser.add_argument("--service", required=True, help="Service name (e.g., sam_gov)")
    _add_key_dir(save_parser)

    try:
        args = parser.parse_args(argv)
    except SystemExit:
        json.dump(_error_response("Invalid arguments", "argument_error"), out)
        out.write("\n")
        return 1

    key_dir = args.key_dir

    handlers = {
        "enrich": _cmd_enrich,
        "diff": _cmd_diff,
        "validate-key": _cmd_validate_key,
        "save-key": _cmd_save_key,
    }

    try:
        handler = handlers.get(args.mode)
        if handler is None:
            json.dump(_error_response(f"Unknown mode: {args.mode}", "argument_error"), out)
            out.write("\n")
            return 1
        return handler(args, key_dir, out)
    except Exception as exc:
        json.dump(_error_response(str(exc), "runtime_error"), out)
        out.write("\n")
        return 1


def main() -> None:
    """CLI entry point."""
    exit_code = run(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
