"""Automated tests for the DSIP topic pipeline using recorded fixtures.

Mocks HTTP at the adapter level using real API responses and PDFs captured
from live testing. Verifies the full pipeline (fetch -> filter -> enrich ->
score -> persist) produces correct results without hitting the network.

Fixtures recorded from: tests/manual/test_dsip_live.py
Raw API response: tests/fixtures/dsip_live/raw_api_search_response.json
Raw topic PDF:    tests/fixtures/dsip_live/raw_topic_68491.pdf
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

# Add scripts/ to path so dsip_cli can be imported directly
_scripts_dir = str(Path(__file__).resolve().parent.parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

import pytest

import httpx

from pes.adapters.dsip_api_adapter import DsipApiAdapter, _normalize_topic
from pes.adapters.dsip_enrichment_adapter import DsipEnrichmentAdapter
from pes.adapters.json_finder_results_adapter import JsonFinderResultsAdapter
from pes.adapters.json_topic_cache_adapter import JsonTopicCacheAdapter
from pes.domain.finder_service import FinderService
from pes.domain.keyword_prefilter import KeywordPreFilter
from pes.domain.topic_enrichment import combine_topics_with_enrichment, completeness_report
from pes.domain.topic_scoring import TopicScoringService

# For detail command tests
from dsip_cli import PROFILE_PATH

FIXTURE_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "dsip_live"


# --- fixture loading ---


@pytest.fixture
def raw_api_response() -> dict[str, Any]:
    """Correct-format fixture with hash IDs, cycle metadata, Q&A counts."""
    path = FIXTURE_DIR / "raw_api_search_correct_format.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def raw_api_response_legacy() -> dict[str, Any]:
    """Legacy broken-format fixture (numeric IDs, 32K topics)."""
    path = FIXTURE_DIR / "raw_api_search_response.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def raw_pdf_bytes() -> bytes:
    path = FIXTURE_DIR / "raw_topic_68491.pdf"
    return path.read_bytes()


@pytest.fixture
def raw_details_response() -> dict[str, Any]:
    """Recorded details API response for topic A254-049."""
    path = FIXTURE_DIR / "raw_api_details_response.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def raw_qa_response() -> list[dict[str, Any]]:
    """Recorded Q&A API response for topic A254-049 (7 entries)."""
    path = FIXTURE_DIR / "raw_api_qa_response.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def raw_component_instructions_pdf() -> bytes:
    """Recorded ARMY component instructions PDF."""
    path = FIXTURE_DIR / "raw_component_instructions_army.pdf"
    return path.read_bytes()


@pytest.fixture
def raw_solicitation_instructions_pdf() -> bytes:
    """Recorded BAA preface PDF."""
    path = FIXTURE_DIR / "raw_solicitation_instructions.pdf"
    return path.read_bytes()


@pytest.fixture
def sample_profile() -> dict[str, Any]:
    path = FIXTURE_DIR / "sample_profile.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def expected_fetch() -> dict[str, Any]:
    path = FIXTURE_DIR / "cli_fetch_response.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def expected_enrich() -> dict[str, Any]:
    path = FIXTURE_DIR / "cli_enrich_response.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def expected_score() -> dict[str, Any]:
    path = FIXTURE_DIR / "cli_score_response.json"
    return json.loads(path.read_text(encoding="utf-8"))


# ===================================================================
# Test 1: DsipApiAdapter normalizes raw API responses correctly
# ===================================================================


class TestDsipApiAdapterNormalization:
    """Tests for _normalize_topic and DsipApiAdapter.fetch() using correct-format fixture."""

    def test_normalize_topic_maps_all_fields(self, raw_api_response: dict[str, Any]) -> None:
        """Normalize a topic from the correct-format API response with all new fields."""
        raw_topic = raw_api_response["data"][0]
        normalized = _normalize_topic(raw_topic)

        # Hash ID (not numeric)
        assert normalized["topic_id"] == "7051b2da4a1e4c52bd0e7daf80d514f7_86352"
        assert "_" in normalized["topic_id"]
        assert normalized["topic_code"] == "A254-049"
        assert "Ka-Band" in normalized["title"]
        assert normalized["status"] == "Pre-Release"
        assert normalized["program"] == "SBIR"
        assert normalized["component"] == "ARMY"
        assert normalized["solicitation_number"] == "25.4"
        assert normalized["cycle_name"] == "DOD_SBIR_2025_P1_C4"
        # New fields from step 01-01
        assert normalized["release_number"] == 12
        assert normalized["published_qa_count"] == 7
        assert isinstance(normalized["baa_instructions"], list)
        assert len(normalized["baa_instructions"]) == 1
        assert normalized["baa_instructions"][0]["file_name"] == "Army_SBIR_254_R12.pdf"

    def test_normalize_preserves_all_expected_fields(
        self, raw_api_response: dict[str, Any],
    ) -> None:
        raw_topic = raw_api_response["data"][0]
        normalized = _normalize_topic(raw_topic)

        expected_fields = {
            "topic_id", "topic_code", "title", "status", "program",
            "component", "solicitation_number", "cycle_name",
            "start_date", "deadline", "cmmc_level", "phase",
            "release_number", "published_qa_count", "baa_instructions",
        }
        assert expected_fields == set(normalized.keys())

    def test_fetch_uses_searchparam_json_format(self, raw_api_response: dict[str, Any]) -> None:
        """DsipApiAdapter.fetch() sends searchParam JSON with size pagination."""
        mock_response = MagicMock()
        mock_response.json.return_value = raw_api_response
        mock_response.raise_for_status = MagicMock()

        with patch("pes.adapters.dsip_api_adapter.httpx.get", return_value=mock_response) as mock_get:
            adapter = DsipApiAdapter(page_size=100, max_pages=1)
            result = adapter.fetch(filters={"topicStatus": "Open"})

        # Verify the HTTP call used correct format
        call_kwargs = mock_get.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
        assert "searchParam" in params, "Must use searchParam JSON format"
        assert "size" in params, "Must use 'size' not 'numPerPage'"
        assert "numPerPage" not in params, "Must not use broken 'numPerPage' param"

        # Verify search param contains correct status IDs
        import json as _json
        search_param = _json.loads(params["searchParam"])
        assert search_param["topicReleaseStatus"] == [592], (
            "Open status should map to [592]"
        )

        # Verify results
        assert result.source == "dsip_api"
        assert result.error is None
        assert len(result.topics) == 3
        assert result.total == 24

    @pytest.mark.parametrize("status_filter,expected_ids", [
        ("Open", [592]),
        ("Pre-Release", [591]),
        (None, [591, 592]),
    ])
    def test_status_filter_maps_to_correct_release_status_ids(
        self,
        raw_api_response: dict[str, Any],
        status_filter: str | None,
        expected_ids: list[int],
    ) -> None:
        """Status filter values map to correct topicReleaseStatus IDs."""
        mock_response = MagicMock()
        mock_response.json.return_value = raw_api_response
        mock_response.raise_for_status = MagicMock()

        with patch("pes.adapters.dsip_api_adapter.httpx.get", return_value=mock_response) as mock_get:
            adapter = DsipApiAdapter(page_size=100, max_pages=1)
            filters = {"topicStatus": status_filter} if status_filter else None
            adapter.fetch(filters=filters)

        call_kwargs = mock_get.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
        import json as _json
        search_param = _json.loads(params["searchParam"])
        assert search_param["topicReleaseStatus"] == expected_ids


# ===================================================================
# Test 2: DsipEnrichmentAdapter extracts sections from real PDF
# ===================================================================


class TestDsipEnrichmentAdapterParsing:
    """Legacy PDF-based tests removed in step 02-01 (replaced by API-based enrichment).

    The adapter no longer downloads topic PDFs -- it uses 3 API endpoints.
    See TestDsipEnrichmentAdapterApiEnrichment for the replacement tests.
    """

    pass


# ===================================================================
# Test 2b: DsipEnrichmentAdapter — API-based enrichment (step 02-01)
# ===================================================================


class TestDsipEnrichmentAdapterApiEnrichment:
    """Tests for API-based enrichment: details, Q&A, and instruction PDFs.

    Test Budget: 8 behaviors x 2 = 16 unit tests max.
    All tests invoke through DsipEnrichmentAdapter.enrich() (driving port).
    HTTP client is mocked at the port boundary.
    """

    def _make_topic(
        self,
        topic_id: str = "7051b2da4a1e4c52bd0e7daf80d514f7_86352",
        cycle_name: str = "DOD_SBIR_2025_P1_C4",
        release_number: int = 12,
        component: str = "ARMY",
        published_qa_count: int = 7,
    ) -> dict[str, Any]:
        return {
            "topic_id": topic_id,
            "topic_code": "A254-049",
            "title": "Affordable Ka-Band Radar",
            "cycle_name": cycle_name,
            "release_number": release_number,
            "component": component,
            "published_qa_count": published_qa_count,
            "baa_instructions": [{"upload_id": 1715189, "file_name": "Army_SBIR_254_R12.pdf",
                                   "upload_type_code": "COMPONENT_FINAL_DOCUMENT_UPLOAD"}],
        }

    def _mock_client_for_api(
        self,
        details_json: dict[str, Any] | None = None,
        qa_json: list[dict[str, Any]] | None = None,
        component_pdf: bytes | None = None,
        solicitation_pdf: bytes | None = None,
        details_error: Exception | None = None,
        qa_error: Exception | None = None,
        component_error: Exception | None = None,
        solicitation_error: Exception | None = None,
    ) -> MagicMock:
        """Build a mock httpx.Client that routes by URL pattern."""
        mock_client = MagicMock()

        def route_get(url: str, **kwargs: Any) -> MagicMock:
            resp = MagicMock()
            resp.raise_for_status = MagicMock()

            if "/details" in url:
                if details_error:
                    resp.raise_for_status.side_effect = details_error
                else:
                    resp.json.return_value = details_json or {}
                    resp.status_code = 200
            elif "/questions" in url:
                if qa_error:
                    resp.raise_for_status.side_effect = qa_error
                else:
                    resp.json.return_value = qa_json or []
                    resp.status_code = 200
            elif "documentType=INSTRUCTIONS&component=" in url or "component=" in url and "INSTRUCTIONS" in url:
                if component_error:
                    resp.raise_for_status.side_effect = component_error
                else:
                    resp.content = component_pdf or b""
                    resp.status_code = 200
            elif "RELEASE_PREFACE" in url:
                if solicitation_error:
                    resp.raise_for_status.side_effect = solicitation_error
                else:
                    resp.content = solicitation_pdf or b""
                    resp.status_code = 200
            else:
                resp.raise_for_status.side_effect = httpx.HTTPStatusError(
                    "404 Not Found", request=MagicMock(), response=MagicMock(),
                )
            return resp

        mock_client.get.side_effect = route_get
        return mock_client

    # --- Behavior 1: Details endpoint returns structured fields ---

    def test_details_returns_description_objective_keywords(
        self,
        raw_details_response: dict[str, Any],
        raw_qa_response: list[dict[str, Any]],
        raw_component_instructions_pdf: bytes,
        raw_solicitation_instructions_pdf: bytes,
    ) -> None:
        """Enrichment fetches details API and returns structured fields."""
        client = self._mock_client_for_api(
            details_json=raw_details_response,
            qa_json=raw_qa_response,
            component_pdf=raw_component_instructions_pdf,
            solicitation_pdf=raw_solicitation_instructions_pdf,
        )
        adapter = DsipEnrichmentAdapter(http_client=client, rate_limit_seconds=0)
        result = adapter.enrich(topics=[self._make_topic()])

        assert len(result.enriched) == 1
        entry = result.enriched[0]
        # Description: HTML tags stripped, contains "Ka band" or "Ka-Band"
        assert "Ka" in entry["description"] or "metamaterials" in entry["description"].lower()
        # Objective is present
        assert entry.get("objective")
        assert "low-cost" in entry["objective"].lower() or "Ka-Band" in entry["objective"]
        # Keywords is a list (parsed from semicolons)
        assert isinstance(entry["keywords"], list)
        assert len(entry["keywords"]) >= 3
        assert "Radar" in entry["keywords"]
        # Technology areas
        assert isinstance(entry["technology_areas"], list)
        assert "Information Systems" in entry["technology_areas"]
        assert "Materials" in entry["technology_areas"]
        # Focus areas
        assert isinstance(entry["focus_areas"], list)
        assert len(entry["focus_areas"]) > 0
        # ITAR and CMMC
        assert entry["itar"] is False

    # --- Behavior 2: Keywords parsed from semicolon-separated string ---

    def test_keywords_parsed_into_trimmed_list(
        self,
        raw_details_response: dict[str, Any],
        raw_component_instructions_pdf: bytes,
        raw_solicitation_instructions_pdf: bytes,
    ) -> None:
        """Keywords semicolon-separated string becomes a trimmed list."""
        client = self._mock_client_for_api(
            details_json=raw_details_response,
            qa_json=[],
            component_pdf=raw_component_instructions_pdf,
            solicitation_pdf=raw_solicitation_instructions_pdf,
        )
        adapter = DsipEnrichmentAdapter(http_client=client, rate_limit_seconds=0)
        result = adapter.enrich(topics=[self._make_topic(published_qa_count=0)])

        keywords = result.enriched[0]["keywords"]
        assert len(keywords) == 5  # "Radar; antenna; metamaterials; scanning; array"
        for kw in keywords:
            assert kw == kw.strip(), f"Keyword '{kw}' has leading/trailing whitespace"

    # --- Behavior 3: Q&A entries parsed with double-JSON answer ---

    def test_qa_entries_parsed_with_nested_json_answer(
        self,
        raw_details_response: dict[str, Any],
        raw_qa_response: list[dict[str, Any]],
        raw_component_instructions_pdf: bytes,
        raw_solicitation_instructions_pdf: bytes,
    ) -> None:
        """Q&A answers with nested JSON {"content": "<HTML>"} are parsed."""
        client = self._mock_client_for_api(
            details_json=raw_details_response,
            qa_json=raw_qa_response,
            component_pdf=raw_component_instructions_pdf,
            solicitation_pdf=raw_solicitation_instructions_pdf,
        )
        adapter = DsipEnrichmentAdapter(http_client=client, rate_limit_seconds=0)
        result = adapter.enrich(topics=[self._make_topic()])

        qa_entries = result.enriched[0]["qa_entries"]
        assert len(qa_entries) == 7
        # First entry: question_no, question, answer, status
        first = qa_entries[0]
        assert first["question_no"] == 1
        assert first["question"]  # non-empty
        assert "seeker design is not of interest" in first["answer"]
        assert first["status"] == "COMPLETED"

    # --- Behavior 4: Malformed answer falls back to raw string ---

    def test_malformed_qa_answer_falls_back_to_raw(
        self,
        raw_details_response: dict[str, Any],
        raw_component_instructions_pdf: bytes,
        raw_solicitation_instructions_pdf: bytes,
    ) -> None:
        """If answer field is not valid JSON, raw string is used."""
        malformed_qa = [{
            "questionId": 999,
            "questionNo": 1,
            "question": "<p>Test question</p>",
            "questionStatus": "COMPLETED",
            "questionStatusDisplay": "Completed",
            "questionSubmittedOn": 1762366997779,
            "answers": [{"answerId": 1, "answer": "not valid json at all"}],
        }]
        client = self._mock_client_for_api(
            details_json=raw_details_response,
            qa_json=malformed_qa,
            component_pdf=raw_component_instructions_pdf,
            solicitation_pdf=raw_solicitation_instructions_pdf,
        )
        adapter = DsipEnrichmentAdapter(http_client=client, rate_limit_seconds=0)
        result = adapter.enrich(topics=[self._make_topic()])

        qa_entries = result.enriched[0]["qa_entries"]
        assert len(qa_entries) == 1
        assert qa_entries[0]["answer"] == "not valid json at all"

    # --- Behavior 5: Q&A skipped for topics with published_qa_count == 0 ---

    def test_qa_skipped_when_published_count_zero(
        self,
        raw_details_response: dict[str, Any],
        raw_component_instructions_pdf: bytes,
        raw_solicitation_instructions_pdf: bytes,
    ) -> None:
        """No Q&A request when published_qa_count == 0."""
        client = self._mock_client_for_api(
            details_json=raw_details_response,
            qa_json=[],  # should not be called
            component_pdf=raw_component_instructions_pdf,
            solicitation_pdf=raw_solicitation_instructions_pdf,
        )
        adapter = DsipEnrichmentAdapter(http_client=client, rate_limit_seconds=0)
        result = adapter.enrich(topics=[self._make_topic(published_qa_count=0)])

        # Verify no Q&A request was made
        calls = [str(c) for c in client.get.call_args_list]
        qa_calls = [c for c in calls if "/questions" in c]
        assert len(qa_calls) == 0, f"Q&A endpoint should not be called: {qa_calls}"
        # Q&A entries empty
        assert result.enriched[0]["qa_entries"] == []
        # Q&A completeness not incremented
        assert result.completeness.get("qa", 0) == 0

    # --- Behavior 6: Instruction PDFs cached within batch ---

    def test_instruction_pdfs_cached_per_cycle_component(
        self,
        raw_details_response: dict[str, Any],
        raw_qa_response: list[dict[str, Any]],
        raw_component_instructions_pdf: bytes,
        raw_solicitation_instructions_pdf: bytes,
    ) -> None:
        """Two topics with same cycle+component download instructions only once."""
        client = self._mock_client_for_api(
            details_json=raw_details_response,
            qa_json=raw_qa_response,
            component_pdf=raw_component_instructions_pdf,
            solicitation_pdf=raw_solicitation_instructions_pdf,
        )
        topic1 = self._make_topic(topic_id="hash_A")
        topic2 = self._make_topic(topic_id="hash_B")

        adapter = DsipEnrichmentAdapter(http_client=client, rate_limit_seconds=0)
        result = adapter.enrich(topics=[topic1, topic2])

        assert len(result.enriched) == 2
        # Both topics should have the same instruction text
        text1 = result.enriched[0].get("component_instructions")
        text2 = result.enriched[1].get("component_instructions")
        assert text1 is not None, "Component instructions should be present"
        assert text1 == text2, "Same cycle+component should share cached instructions"

        # Count instruction download calls (component + solicitation)
        calls = [str(c) for c in client.get.call_args_list]
        component_calls = [c for c in calls if "INSTRUCTIONS" in c and "component" in c.lower()]
        solicitation_calls = [c for c in calls if "RELEASE_PREFACE" in c]
        # Each should be called only once despite 2 topics
        assert len(component_calls) == 1, f"Expected 1 component download, got {len(component_calls)}"
        assert len(solicitation_calls) == 1, f"Expected 1 solicitation download, got {len(solicitation_calls)}"

    # --- Behavior 7: Per-endpoint failure isolation ---

    def test_details_failure_does_not_block_qa_or_instructions(
        self,
        raw_qa_response: list[dict[str, Any]],
        raw_component_instructions_pdf: bytes,
        raw_solicitation_instructions_pdf: bytes,
    ) -> None:
        """If details endpoint fails, Q&A and instructions still retrieved."""
        client = self._mock_client_for_api(
            details_error=httpx.HTTPStatusError("500", request=MagicMock(), response=MagicMock()),
            qa_json=raw_qa_response,
            component_pdf=raw_component_instructions_pdf,
            solicitation_pdf=raw_solicitation_instructions_pdf,
        )
        adapter = DsipEnrichmentAdapter(http_client=client, rate_limit_seconds=0, max_retries=1)
        result = adapter.enrich(topics=[self._make_topic()])

        assert len(result.enriched) == 1
        entry = result.enriched[0]
        # Details failed: description/objective empty
        assert entry.get("description", "") == ""
        # Q&A and instructions still present
        assert len(entry["qa_entries"]) == 7
        assert entry.get("component_instructions") is not None
        assert entry.get("solicitation_instructions") is not None

    def test_qa_failure_does_not_block_details_or_instructions(
        self,
        raw_details_response: dict[str, Any],
        raw_component_instructions_pdf: bytes,
        raw_solicitation_instructions_pdf: bytes,
    ) -> None:
        """If Q&A endpoint fails, details and instructions still returned."""
        client = self._mock_client_for_api(
            details_json=raw_details_response,
            qa_error=httpx.HTTPStatusError("500", request=MagicMock(), response=MagicMock()),
            component_pdf=raw_component_instructions_pdf,
            solicitation_pdf=raw_solicitation_instructions_pdf,
        )
        adapter = DsipEnrichmentAdapter(http_client=client, rate_limit_seconds=0, max_retries=1)
        result = adapter.enrich(topics=[self._make_topic()])

        assert len(result.enriched) == 1
        entry = result.enriched[0]
        assert entry["description"]  # details still present
        assert entry["qa_entries"] == []  # Q&A failed
        assert entry.get("component_instructions") is not None

    # --- Behavior 8: Enrichment status "partial" ---

    def test_enrichment_status_partial_when_data_source_fails(
        self,
        raw_qa_response: list[dict[str, Any]],
        raw_component_instructions_pdf: bytes,
        raw_solicitation_instructions_pdf: bytes,
    ) -> None:
        """Topic gets enrichment_status 'partial' when any data source fails."""
        client = self._mock_client_for_api(
            details_error=httpx.HTTPStatusError("500", request=MagicMock(), response=MagicMock()),
            qa_json=raw_qa_response,
            component_pdf=raw_component_instructions_pdf,
            solicitation_pdf=raw_solicitation_instructions_pdf,
        )
        adapter = DsipEnrichmentAdapter(http_client=client, rate_limit_seconds=0, max_retries=1)
        result = adapter.enrich(topics=[self._make_topic()])

        entry = result.enriched[0]
        assert entry.get("enrichment_status") == "partial"

    def test_all_sources_ok_gives_status_ok(
        self,
        raw_details_response: dict[str, Any],
        raw_qa_response: list[dict[str, Any]],
        raw_component_instructions_pdf: bytes,
        raw_solicitation_instructions_pdf: bytes,
    ) -> None:
        """Topic gets enrichment_status 'ok' when all data sources succeed."""
        client = self._mock_client_for_api(
            details_json=raw_details_response,
            qa_json=raw_qa_response,
            component_pdf=raw_component_instructions_pdf,
            solicitation_pdf=raw_solicitation_instructions_pdf,
        )
        adapter = DsipEnrichmentAdapter(http_client=client, rate_limit_seconds=0)
        result = adapter.enrich(topics=[self._make_topic()])

        entry = result.enriched[0]
        assert entry.get("enrichment_status") == "ok"


# ===================================================================
# Test 3: KeywordPreFilter matches expected topics
# ===================================================================


class TestKeywordPreFilter:

    def test_prefilter_matches_recorded_results(
        self, raw_api_response_legacy: dict[str, Any],
    ) -> None:
        """Pre-filter with known capabilities should match the same topics as live run."""
        topics = [_normalize_topic(t) for t in raw_api_response_legacy["data"]]
        capabilities = ["software", "sensor", "AI", "intelligence"]

        prefilter = KeywordPreFilter()
        result = prefilter.filter(topics, capabilities)

        # From live run: 2 candidates, 8 eliminated
        assert result.eliminated_count == 8
        assert len(result.candidates) == 2

        candidate_ids = {c["topic_id"] for c in result.candidates}
        assert "68491" in candidate_ids  # "...Command, Control, Communications, and Intelligence"
        assert "68492" in candidate_ids  # "Self-Containing Munitions" (matches "AI" via "Artificial intelligence")

    def test_empty_capabilities_passes_all(
        self, raw_api_response_legacy: dict[str, Any],
    ) -> None:
        topics = [_normalize_topic(t) for t in raw_api_response_legacy["data"]]
        result = KeywordPreFilter().filter(topics, [])
        assert len(result.candidates) == len(topics)
        assert result.eliminated_count == 0


# ===================================================================
# Test 4: Full pipeline (FinderService) with all mocks
# ===================================================================


class TestFullPipelineMocked:

    def test_search_and_enrich_pipeline_with_api_enrichment(
        self,
        raw_api_response: dict[str, Any],
        raw_details_response: dict[str, Any],
        raw_qa_response: list[dict[str, Any]],
        raw_component_instructions_pdf: bytes,
        raw_solicitation_instructions_pdf: bytes,
        sample_profile: dict[str, Any],
        tmp_path: Path,
    ) -> None:
        """Full pipeline with API-based enrichment produces enriched topics."""
        # Mock fetch adapter
        mock_http_response = MagicMock()
        mock_http_response.json.return_value = raw_api_response
        mock_http_response.raise_for_status = MagicMock()

        # Mock enrichment HTTP client -- route by URL
        mock_enrich_client = MagicMock()

        def route_get(url: str, **kwargs: Any) -> MagicMock:
            resp = MagicMock()
            resp.raise_for_status = MagicMock()
            if "/details" in url:
                resp.json.return_value = raw_details_response
                resp.status_code = 200
            elif "/questions" in url:
                resp.json.return_value = raw_qa_response
                resp.status_code = 200
            elif "RELEASE_PREFACE" in url:
                resp.content = raw_solicitation_instructions_pdf
                resp.status_code = 200
            elif "INSTRUCTIONS" in url:
                resp.content = raw_component_instructions_pdf
                resp.status_code = 200
            else:
                resp.raise_for_status.side_effect = httpx.HTTPStatusError(
                    "404", request=MagicMock(), response=MagicMock(),
                )
            return resp

        mock_enrich_client.get.side_effect = route_get

        with patch("pes.adapters.dsip_api_adapter.httpx.get", return_value=mock_http_response):
            fetcher = DsipApiAdapter(page_size=100, max_pages=1)
            enricher = DsipEnrichmentAdapter(
                http_client=mock_enrich_client, rate_limit_seconds=0,
            )
            cache = JsonTopicCacheAdapter(str(tmp_path))

            # Use capabilities that match all 3 topics in fixture
            profile = dict(sample_profile)
            profile["capabilities"] = [
                "radar", "metamaterials", "battery", "respirator",
            ]

            service = FinderService(
                topic_fetch=fetcher,
                profile=profile,
                enrichment_port=enricher,
                cache_port=cache,
            )

            result = service.search_and_enrich()

        # Pipeline should complete without error
        assert result.error is None
        assert result.source == "dsip_api"
        assert result.total_fetched == 3  # 3 topics from correct-format fixture

        # All candidates should be enriched with API data
        for topic in result.topics:
            assert topic.get("enrichment_status") == "ok"
            assert topic["description"]
            assert isinstance(topic.get("keywords"), list)
            assert isinstance(topic.get("technology_areas"), list)

        # Cache should have been written
        assert cache.exists()
        assert cache.is_fresh(ttl_hours=1)

    def test_completeness_report_includes_four_data_types(
        self,
        tmp_path: Path,
    ) -> None:
        """Completeness messages report descriptions, Q&A, solicitation and component instructions."""
        from pes.ports.topic_enrichment_port import EnrichmentResult

        # Stub enrichment port returning known completeness
        mock_enrichment = MagicMock()
        mock_enrichment.enrich.return_value = EnrichmentResult(
            enriched=[
                {"topic_id": "T1", "description": "desc", "instructions": "instr",
                 "component_instructions": "comp", "qa_entries": [{"q": "?", "a": "!"}],
                 "keywords": [], "technology_areas": [], "focus_areas": [],
                 "objective": None, "itar": False, "cmmc_level": None,
                 "solicitation_instructions": "sol_instr"},
            ],
            errors=[],
            completeness={
                "descriptions": 1, "qa": 1,
                "solicitation_instructions": 1, "component_instructions": 1,
                "total": 1,
            },
        )

        # Stub fetch port returning one topic
        mock_fetch = MagicMock()
        from pes.ports.topic_fetch_port import FetchResult
        mock_fetch.fetch.return_value = FetchResult(
            topics=[{"topic_id": "T1", "title": "Test", "topic_code": "X",
                     "status": "Open", "program": "SBIR", "component": "ARMY",
                     "cycle_name": "C4", "release_number": 12,
                     "published_qa_count": 1, "baa_instructions": []}],
            total=1,
            source="dsip_api",
        )

        service = FinderService(
            topic_fetch=mock_fetch,
            profile={"company_name": "X", "capabilities": ["test"]},
            enrichment_port=mock_enrichment,
        )
        result = service.search_and_enrich()

        # Verify 4 completeness lines in messages
        assert any("Descriptions:" in m for m in result.messages)
        assert any("Q&A:" in m for m in result.messages)
        assert any("Solicitation Instructions:" in m for m in result.messages)
        assert any("Component Instructions:" in m for m in result.messages)

        # Verify combined topics include new enrichment fields
        assert len(result.topics) == 1
        t = result.topics[0]
        assert t.get("solicitation_instructions") == "sol_instr"
        assert t.get("keywords") == []

    def test_cache_hit_skips_fetch(self, tmp_path: Path) -> None:
        """When cache is fresh, FinderService returns cached data."""
        # Pre-populate cache
        cache = JsonTopicCacheAdapter(str(tmp_path))
        cache.write(
            [{"topic_id": "12345", "title": "Cached Topic", "description": "cached"}],
            {"scrape_date": "2099-01-01T00:00:00", "source": "dsip_api", "ttl_hours": 24},
        )

        fetcher = MagicMock()  # Should NOT be called
        service = FinderService(
            topic_fetch=fetcher,
            profile={"company_name": "X", "capabilities": []},
            cache_port=cache,
        )

        result = service.search_and_enrich()

        fetcher.fetch.assert_not_called()
        assert "Using cached enriched data" in result.messages
        assert len(result.topics) == 1
        assert result.topics[0]["topic_id"] == "12345"


# ===================================================================
# Test 5: TopicScoringService with recorded data
# ===================================================================


class TestScoringMocked:

    def test_scoring_matches_live_output(
        self,
        expected_score: dict[str, Any],
        sample_profile: dict[str, Any],
    ) -> None:
        """Score the same enriched topics and verify same recommendations."""
        enriched_topics = expected_score["topics"]
        scorer = TopicScoringService()
        scored = scorer.score_batch(enriched_topics, sample_profile)

        live_scored = {s["topic_id"]: s for s in expected_score["scored"]}

        for s in scored:
            live = live_scored[s.topic_id]
            assert s.recommendation == live["recommendation"], (
                f"Topic {s.topic_id}: expected {live['recommendation']}, got {s.recommendation}"
            )
            assert abs(s.composite_score - live["composite_score"]) < 0.01, (
                f"Topic {s.topic_id}: score {s.composite_score} != {live['composite_score']}"
            )
            for dim, val in s.dimensions.items():
                assert abs(val - live["dimensions"][dim]) < 0.01, (
                    f"Topic {s.topic_id} dim {dim}: {val} != {live['dimensions'][dim]}"
                )

    def test_scoring_recommendations_are_valid(
        self, sample_profile: dict[str, Any],
    ) -> None:
        scorer = TopicScoringService()
        topics = [
            {"topic_id": "1", "title": "AI Software", "program": "SBIR"},
            {"topic_id": "2", "title": "Unrelated Basketweaving", "program": "SBIR"},
        ]
        scored = scorer.score_batch(topics, sample_profile)
        for s in scored:
            assert s.recommendation in ("GO", "EVALUATE", "NO-GO")
            assert 0.0 <= s.composite_score <= 1.0


# ===================================================================
# Test 6: Results persistence
# ===================================================================


class TestResultsPersistence:

    def test_finder_results_round_trip(self, tmp_path: Path) -> None:
        port = JsonFinderResultsAdapter(str(tmp_path))
        data = {
            "source": "dsip_api",
            "scored": [{"topic_id": "123", "score": 0.75}],
        }
        port.write(data)

        assert port.exists()
        loaded = port.read()
        assert loaded is not None
        assert loaded["source"] == "dsip_api"
        assert loaded["scored"][0]["topic_id"] == "123"

    def test_topic_cache_round_trip(self, tmp_path: Path) -> None:
        cache = JsonTopicCacheAdapter(str(tmp_path))
        topics = [{"topic_id": "456", "title": "Test"}]
        metadata = {
            "scrape_date": "2099-01-01T00:00:00",
            "source": "dsip_api",
            "ttl_hours": 24,
            "total_topics": 1,
        }
        cache.write(topics, metadata)

        assert cache.exists()
        assert cache.is_fresh(ttl_hours=24)
        result = cache.read()
        assert result is not None
        assert len(result.topics) == 1
        assert result.topics[0]["topic_id"] == "456"


# ===================================================================
# Test 7: Detail command with hash ID format (step 03-01)
# ===================================================================


class TestDetailCommand:
    """Tests for cmd_detail CLI command with hash ID and API enrichment.

    Test Budget: 2 behaviors x 2 = 4 unit tests max.
    Behaviors:
      1. Detail command passes topic dict to enricher (not topic_ids kwarg)
      2. Detail command works with hash ID format containing underscores
    """

    def _make_enrichment_result(
        self,
        topic_id: str,
    ) -> Any:
        from pes.ports.topic_enrichment_port import EnrichmentResult
        return EnrichmentResult(
            enriched=[{
                "topic_id": topic_id,
                "description": "Test description",
                "objective": "Test objective",
                "keywords": ["radar", "AI"],
                "technology_areas": ["Information Systems"],
                "focus_areas": ["Autonomy"],
                "itar": False,
                "cmmc_level": None,
                "qa_entries": [{"question_no": 1, "question": "Q?", "answer": "A.", "status": "COMPLETED"}],
                "instructions": None,
                "component_instructions": None,
                "solicitation_instructions": None,
                "enrichment_status": "ok",
            }],
            errors=[],
            completeness={"descriptions": 1, "qa": 1, "total": 1},
        )

    def test_detail_passes_topic_dict_to_enricher(self) -> None:
        """Detail command constructs a topic dict and passes it via topics= kwarg."""
        hash_id = "7051b2da4a1e4c52bd0e7daf80d514f7_86352"
        enrichment_result = self._make_enrichment_result(hash_id)

        with patch(
            "dsip_cli.DsipEnrichmentAdapter",
        ) as MockAdapter:
            mock_instance = MockAdapter.return_value
            mock_instance.enrich.return_value = enrichment_result

            # Capture stdout
            import io
            captured = io.StringIO()
            with patch("sys.stdout", captured):
                from dsip_cli import cmd_detail
                args = argparse.Namespace(topic_id=hash_id, profile=str(PROFILE_PATH), state_dir=".sbir")
                cmd_detail(args)

            # Verify enricher was called with topics=[{...}], not topic_ids=[...]
            mock_instance.enrich.assert_called_once()
            call_kwargs = mock_instance.enrich.call_args
            # Must use topics= keyword with a list of dicts
            if call_kwargs.kwargs:
                topics_arg = call_kwargs.kwargs.get("topics")
            else:
                topics_arg = call_kwargs.args[0] if call_kwargs.args else None
            assert topics_arg is not None, "enricher.enrich must be called with topics argument"
            assert isinstance(topics_arg, list), "topics must be a list"
            assert len(topics_arg) == 1
            assert topics_arg[0]["topic_id"] == hash_id

            # Verify output contains enriched data
            output = json.loads(captured.getvalue())
            assert output["topic_id"] == hash_id
            assert len(output["enriched"]) == 1
            assert output["enriched"][0]["objective"] == "Test objective"
            assert output["enriched"][0]["keywords"] == ["radar", "AI"]

    @pytest.mark.parametrize("topic_id", [
        "7051b2da4a1e4c52bd0e7daf80d514f7_86352",  # hash ID with underscore
        "68492",  # legacy numeric ID
        "abc_def_123",  # multi-underscore ID
    ])
    def test_detail_works_with_various_id_formats(self, topic_id: str) -> None:
        """Detail command accepts hash IDs, numeric IDs, and multi-underscore IDs."""
        enrichment_result = self._make_enrichment_result(topic_id)

        with patch("dsip_cli.DsipEnrichmentAdapter") as MockAdapter:
            mock_instance = MockAdapter.return_value
            mock_instance.enrich.return_value = enrichment_result

            import io
            captured = io.StringIO()
            with patch("sys.stdout", captured):
                from dsip_cli import cmd_detail
                args = argparse.Namespace(topic_id=topic_id, profile=str(PROFILE_PATH), state_dir=".sbir")
                cmd_detail(args)

            output = json.loads(captured.getvalue())
            assert output["topic_id"] == topic_id
            assert output["enriched"][0]["topic_id"] == topic_id
