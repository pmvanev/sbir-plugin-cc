"""Automated tests for the DSIP topic pipeline using recorded fixtures.

Mocks HTTP at the adapter level using real API responses and PDFs captured
from live testing. Verifies the full pipeline (fetch -> filter -> enrich ->
score -> persist) produces correct results without hitting the network.

Fixtures recorded from: tests/manual/test_dsip_live.py
Raw API response: tests/fixtures/dsip_live/raw_api_search_response.json
Raw topic PDF:    tests/fixtures/dsip_live/raw_topic_68491.pdf
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from pes.adapters.dsip_api_adapter import DsipApiAdapter, _normalize_topic
from pes.adapters.dsip_enrichment_adapter import DsipEnrichmentAdapter
from pes.adapters.json_finder_results_adapter import JsonFinderResultsAdapter
from pes.adapters.json_topic_cache_adapter import JsonTopicCacheAdapter
from pes.domain.finder_service import FinderService
from pes.domain.keyword_prefilter import KeywordPreFilter
from pes.domain.topic_enrichment import combine_topics_with_enrichment, completeness_report
from pes.domain.topic_scoring import TopicScoringService

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

    def test_extract_description_from_real_pdf(self, raw_pdf_bytes: bytes) -> None:
        """Parse the recorded PDF and verify description extraction."""
        adapter = DsipEnrichmentAdapter()
        data = adapter._extract_from_pdf(raw_pdf_bytes)

        assert data["description"], "Description should not be empty"
        assert len(data["description"]) > 100
        # This PDF is for topic 68491 (Distributed Command, Control, ...)
        assert "command" in data["description"].lower() or "control" in data["description"].lower()

    def test_enrich_with_mocked_http(self, raw_pdf_bytes: bytes) -> None:
        """DsipEnrichmentAdapter.enrich() with mocked HTTP returns parsed sections."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = raw_pdf_bytes
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        adapter = DsipEnrichmentAdapter(http_client=mock_client, rate_limit_seconds=0)
        result = adapter.enrich(topic_ids=["68491"])

        assert len(result.enriched) == 1
        assert result.errors == []
        entry = result.enriched[0]
        assert entry["topic_id"] == "68491"
        assert entry["description"]
        assert "instructions" in entry
        assert "component_instructions" in entry
        assert "qa_entries" in entry
        assert result.completeness["descriptions"] == 1
        assert result.completeness["total"] == 1

    def test_enrich_isolates_http_failure(self, raw_pdf_bytes: bytes) -> None:
        """Bad topic doesn't crash the batch."""
        import httpx

        mock_client = MagicMock()
        ok_response = MagicMock()
        ok_response.content = raw_pdf_bytes
        ok_response.raise_for_status = MagicMock()

        fail_response = MagicMock()
        fail_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "403", request=MagicMock(), response=MagicMock(),
        )

        mock_client.get.side_effect = [ok_response, fail_response]

        adapter = DsipEnrichmentAdapter(
            http_client=mock_client, rate_limit_seconds=0, max_retries=1,
        )
        result = adapter.enrich(topic_ids=["68491", "BAD_ID"])

        assert len(result.enriched) == 1
        assert len(result.errors) == 1
        assert result.errors[0]["topic_id"] == "BAD_ID"


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

    def test_search_and_enrich_matches_live_output(
        self,
        raw_api_response_legacy: dict[str, Any],
        raw_pdf_bytes: bytes,
        sample_profile: dict[str, Any],
        expected_enrich: dict[str, Any],
        tmp_path: Path,
    ) -> None:
        """Full pipeline with mocked HTTP should match recorded live output."""
        # Mock fetch adapter
        mock_http_response = MagicMock()
        mock_http_response.json.return_value = raw_api_response_legacy
        mock_http_response.raise_for_status = MagicMock()

        # Mock enrichment HTTP client (returns same PDF for any topic)
        mock_client = MagicMock()
        mock_pdf_response = MagicMock()
        mock_pdf_response.content = raw_pdf_bytes
        mock_pdf_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_pdf_response

        with patch("pes.adapters.dsip_api_adapter.httpx.get", return_value=mock_http_response):
            fetcher = DsipApiAdapter(page_size=10, max_pages=1)
            enricher = DsipEnrichmentAdapter(
                http_client=mock_client, rate_limit_seconds=0,
            )
            cache = JsonTopicCacheAdapter(str(tmp_path))

            # Override capabilities to match live run
            profile = dict(sample_profile)
            profile["capabilities"] = ["software", "sensor", "AI", "intelligence"]

            service = FinderService(
                topic_fetch=fetcher,
                profile=profile,
                enrichment_port=enricher,
                cache_port=cache,
            )

            result = service.search_and_enrich()

        # Verify against recorded live output
        assert result.error is None
        assert result.source == "dsip_api"
        assert result.total_fetched == expected_enrich["total_fetched"]
        assert result.candidates_count == expected_enrich["candidates_count"]
        assert result.eliminated_count == expected_enrich["eliminated_count"]

        # Enriched topics should have descriptions
        for topic in result.topics:
            assert topic.get("enrichment_status") == "ok"
            assert topic["description"]

        # Cache should have been written
        assert cache.exists()
        assert cache.is_fresh(ttl_hours=1)

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
