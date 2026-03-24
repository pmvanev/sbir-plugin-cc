"""CLI for DSIP topic retrieval, enrichment, and scoring.

This is the entry point that agents call via Bash. It wires all adapters
and services internally -- callers just pass flags and read JSON output.

Commands:
  fetch     -- Fetch topic metadata from DSIP API
  enrich    -- Fetch + enrich candidates with PDF descriptions/instructions/Q&A
  score     -- Fetch + enrich + score against company profile
  detail    -- Enrich a single topic by ID

Examples:
  python scripts/dsip_cli.py fetch --status Open
  python scripts/dsip_cli.py enrich --status Open --capabilities "software,AI"
  python scripts/dsip_cli.py score --status Open
  python scripts/dsip_cli.py detail --topic-id 123456
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from dataclasses import asdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pes.adapters.dsip_api_adapter import DsipApiAdapter
from pes.adapters.dsip_enrichment_adapter import DsipEnrichmentAdapter
from pes.adapters.json_finder_results_adapter import JsonFinderResultsAdapter
from pes.adapters.json_topic_cache_adapter import JsonTopicCacheAdapter
from pes.domain.finder_service import FinderService
from pes.domain.topic_scoring import TopicScoringService

PROFILE_PATH = Path.home() / ".sbir" / "company-profile.json"
DEFAULT_STATE_DIR = Path(".sbir")


def _load_profile(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _build_filters(args: argparse.Namespace) -> dict[str, str]:
    filters: dict[str, str] = {}
    if getattr(args, "status", None):
        filters["topicStatus"] = args.status
    if getattr(args, "component", None):
        filters["component"] = args.component
    return filters


def _build_service(
    args: argparse.Namespace,
    profile: dict[str, Any] | None,
    with_enrichment: bool,
) -> FinderService:
    state_dir = Path(getattr(args, "state_dir", DEFAULT_STATE_DIR))
    fetcher = DsipApiAdapter(
        page_size=args.limit,
        max_pages=args.max_pages,
    )
    enricher = DsipEnrichmentAdapter(rate_limit_seconds=1.0) if with_enrichment else None
    cache = JsonTopicCacheAdapter(str(state_dir))

    return FinderService(
        topic_fetch=fetcher,
        profile=profile,
        enrichment_port=enricher,
        cache_port=cache,
    )


def _override_capabilities(
    profile: dict[str, Any] | None,
    capabilities_csv: str,
) -> dict[str, Any] | None:
    if not capabilities_csv:
        return profile
    caps = [c.strip() for c in capabilities_csv.split(",") if c.strip()]
    if profile is None:
        profile = {"company_name": "", "capabilities": caps}
    else:
        profile = dict(profile)
        profile["capabilities"] = caps
    return profile


def _result_to_dict(result: Any) -> dict[str, Any]:
    return {
        "source": result.source,
        "total": result.total,
        "total_fetched": result.total_fetched,
        "candidates_count": result.candidates_count,
        "eliminated_count": result.eliminated_count,
        "partial": result.partial,
        "error": result.error,
        "messages": result.messages,
        "topics": result.topics,
    }


# --- Commands ---


def cmd_fetch(args: argparse.Namespace) -> None:
    """Fetch topic metadata (no PDF enrichment)."""
    profile = _load_profile(Path(args.profile))
    profile = _override_capabilities(profile, args.capabilities)

    service = _build_service(args, profile, with_enrichment=False)
    result = service.search_and_enrich(filters=_build_filters(args))

    json.dump(_result_to_dict(result), sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def cmd_enrich(args: argparse.Namespace) -> None:
    """Fetch + enrich candidates with descriptions, instructions, Q&A."""
    profile = _load_profile(Path(args.profile))
    profile = _override_capabilities(profile, args.capabilities)

    service = _build_service(args, profile, with_enrichment=True)
    result = service.search_and_enrich(filters=_build_filters(args))

    json.dump(_result_to_dict(result), sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def cmd_score(args: argparse.Namespace) -> None:
    """Fetch + enrich + score against company profile."""
    profile = _load_profile(Path(args.profile))
    if profile is None:
        json.dump({"error": f"Profile not found at {args.profile}"}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        sys.exit(1)

    profile = _override_capabilities(profile, args.capabilities)
    service = _build_service(args, profile, with_enrichment=True)
    result = service.search_and_enrich(filters=_build_filters(args))

    scorer = TopicScoringService()
    scored = scorer.score_batch(result.topics, profile)

    # Persist
    if not args.no_persist:
        state_dir = Path(getattr(args, "state_dir", DEFAULT_STATE_DIR))
        results_port = JsonFinderResultsAdapter(str(state_dir))
        results_port.write({
            "source": result.source,
            "total": result.total,
            "scored": [
                {
                    "topic_id": s.topic_id,
                    "composite_score": s.composite_score,
                    "recommendation": s.recommendation,
                    "dimensions": s.dimensions,
                    "disqualifiers": s.disqualifiers,
                    "warnings": s.warnings,
                    "key_personnel_match": s.key_personnel_match,
                }
                for s in scored
            ],
        })

    output = _result_to_dict(result)
    output["scored"] = [
        {
            "topic_id": s.topic_id,
            "composite_score": s.composite_score,
            "recommendation": s.recommendation,
            "dimensions": s.dimensions,
            "disqualifiers": s.disqualifiers,
            "warnings": s.warnings,
            "key_personnel_match": s.key_personnel_match,
        }
        for s in scored
    ]
    json.dump(output, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def cmd_detail(args: argparse.Namespace) -> None:
    """Enrich a single topic by ID."""
    enricher = DsipEnrichmentAdapter(rate_limit_seconds=0.5)
    result = enricher.enrich(topics=[{"topic_id": args.topic_id}])

    output: dict[str, Any] = {
        "topic_id": args.topic_id,
        "enriched": result.enriched,
        "errors": result.errors,
        "completeness": result.completeness,
    }
    json.dump(output, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


# --- Argument parsing ---


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--status", help="topicStatus filter (Open, Pre-Release, Closed)")
    parser.add_argument("--component", help="Component filter (ARMY, NAVY, USAF, ...)")
    parser.add_argument("--limit", type=int, default=100, help="Topics per page (default 100)")
    parser.add_argument("--max-pages", type=int, default=0, help="Max pages (0=all, default 0)")
    parser.add_argument("--capabilities", type=str, default="",
                        help="Override capabilities (comma-separated)")
    parser.add_argument("--profile", type=str, default=str(PROFILE_PATH),
                        help="Company profile path")
    parser.add_argument("--state-dir", type=str, default=str(DEFAULT_STATE_DIR),
                        help="State directory for cache/results")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DSIP topic retrieval, enrichment, and scoring CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_fetch = sub.add_parser("fetch", help="Fetch topic metadata (no enrichment)")
    _add_common_args(p_fetch)

    p_enrich = sub.add_parser("enrich", help="Fetch + enrich with PDF descriptions/Q&A")
    _add_common_args(p_enrich)

    p_score = sub.add_parser("score", help="Fetch + enrich + score against profile")
    _add_common_args(p_score)
    p_score.add_argument("--no-persist", action="store_true",
                         help="Skip writing finder-results.json")

    p_detail = sub.add_parser("detail", help="Enrich a single topic by ID")
    p_detail.add_argument("--topic-id", required=True, help="DSIP topic ID")
    p_detail.add_argument("--profile", type=str, default=str(PROFILE_PATH))
    p_detail.add_argument("--state-dir", type=str, default=str(DEFAULT_STATE_DIR))

    args = parser.parse_args()

    commands = {
        "fetch": cmd_fetch,
        "enrich": cmd_enrich,
        "score": cmd_score,
        "detail": cmd_detail,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
