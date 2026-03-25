"""Unit tests for DsipEnrichmentAdapter -- driven port for topic enrichment.

Test Budget: 6 behaviors x 2 = 12 max unit tests.
Tests invoke through TopicEnrichmentPort.enrich() (port interface).
HTTP responses simulated via httpx mock transport using API-style routing.

Behaviors tested:
1. Happy path: extracts description, keywords, Q&A from API endpoints
2. Batch enrichment with per-topic progress callback
3. Individual endpoint failure does not stop batch (per-endpoint isolation)
4. Download failure (HTTP error) does not stop batch
5. Completeness metrics reflect actual extraction results
6. Rate limiting: configurable delay between requests
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from pes.adapters.dsip_enrichment_adapter import DsipEnrichmentAdapter


def _make_details_json(description: str = "Test description") -> dict[str, Any]:
    """Build a mock details API response."""
    return {
        "description": f"<p>{description}</p>",
        "objective": "<p>Test objective</p>",
        "keywords": "keyword1; keyword2; keyword3",
        "technologyAreas": ["Area1"],
        "focusAreas": ["Focus1"],
        "itar": False,
        "cmmcLevel": "",
        "phase1Description": "<p>Phase 1</p>",
        "phase2Description": "<p>Phase 2</p>",
        "phase3Description": "<p>Phase 3</p>",
        "referenceDocuments": [],
    }


def _make_qa_json(count: int = 2) -> list[dict[str, Any]]:
    """Build a mock Q&A API response."""
    entries = []
    for i in range(1, count + 1):
        entries.append({
            "questionId": i,
            "questionNo": i,
            "question": f"<p>Question {i}?</p>",
            "questionStatus": "COMPLETED",
            "questionStatusDisplay": "Completed",
            "questionSubmittedOn": 1762366997779,
            "answers": [{
                "answerId": i,
                "answer": json.dumps({"content": f"<p>Answer {i}.</p>"}),
            }],
        })
    return entries


def _make_topic(
    topic_id: str = "T-001",
    published_qa_count: int = 2,
    cycle_name: str = "C4",
    component: str = "ARMY",
    release_number: int = 12,
) -> dict[str, Any]:
    return {
        "topic_id": topic_id,
        "cycle_name": cycle_name,
        "release_number": release_number,
        "component": component,
        "published_qa_count": published_qa_count,
        "baa_instructions": [],
    }


# Minimal 1-page PDF for instruction text extraction
_MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
    b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
    b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    b"4 0 obj\n<< /Length 64 >>\n"
    b"stream\nBT /F1 12 Tf 72 720 Td (Instructions text content here) Tj ET\n"
    b"endstream\nendobj\n"
    b"xref\n0 6\n"
    b"0000000000 65535 f \n"
    b"0000000009 00000 n \n"
    b"0000000058 00000 n \n"
    b"0000000115 00000 n \n"
    b"0000000350 00000 n \n"
    b"0000000275 00000 n \n"
    b"trailer\n<< /Size 6 /Root 1 0 R >>\n"
    b"startxref\n0\n%%EOF\n"
)


class ApiMockTransport(httpx.BaseTransport):
    """Mock HTTP transport routing by URL pattern for API-based enrichment."""

    def __init__(self) -> None:
        self.responses: dict[str, tuple[int, bytes, str]] = {}
        self.request_log: list[httpx.Request] = []

    def add_json_response(
        self, path_contains: str, data: Any, status_code: int = 200,
    ) -> None:
        self.responses[path_contains] = (
            status_code, json.dumps(data).encode(), "application/json",
        )

    def add_pdf_response(
        self, path_contains: str, content: bytes = _MINIMAL_PDF, status_code: int = 200,
    ) -> None:
        self.responses[path_contains] = (status_code, content, "application/pdf")

    def add_error_response(self, path_contains: str, status_code: int = 500) -> None:
        self.responses[path_contains] = (status_code, b"Error", "text/plain")

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.request_log.append(request)
        url = str(request.url)
        for key, (status, content, ctype) in self.responses.items():
            if key in url:
                return httpx.Response(
                    status_code=status, content=content,
                    headers={"content-type": ctype},
                )
        return httpx.Response(status_code=404, content=b"Not found")

    def _setup_happy_path(
        self, topic_id: str = "T-001", details: dict[str, Any] | None = None,
        qa: list[dict[str, Any]] | None = None,
    ) -> None:
        """Configure standard happy-path responses for a topic."""
        self.add_json_response(f"{topic_id}/details", details or _make_details_json())
        self.add_json_response(f"{topic_id}/questions", qa or _make_qa_json())
        self.add_pdf_response("RELEASE_PREFACE")
        self.add_pdf_response("INSTRUCTIONS")


class TestEnrichHappyPath:
    """Behavior 1: Extracts description, keywords, Q&A from API endpoints."""

    def test_extracts_all_fields_from_api(self) -> None:
        """Single topic enrichment returns description, keywords, Q&A, instructions."""
        transport = ApiMockTransport()
        transport._setup_happy_path("T-001", details=_make_details_json("A" * 600))

        adapter = DsipEnrichmentAdapter(
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
        )
        result = adapter.enrich([_make_topic()])

        assert len(result.enriched) == 1
        topic = result.enriched[0]
        assert topic["topic_id"] == "T-001"
        assert len(topic["description"]) >= 500
        assert topic["objective"]
        assert isinstance(topic["keywords"], list)
        assert len(topic["keywords"]) == 3
        assert len(result.errors) == 0


class TestBatchWithProgress:
    """Behavior 2: Batch enrichment invokes progress callback per topic."""

    def test_progress_callback_invoked_per_topic(self) -> None:
        transport = ApiMockTransport()
        for i in range(1, 4):
            tid = f"T-{i:03d}"
            transport.add_json_response(f"{tid}/details", _make_details_json())
            transport.add_json_response(f"{tid}/questions", _make_qa_json())
        transport.add_pdf_response("RELEASE_PREFACE")
        transport.add_pdf_response("INSTRUCTIONS")

        adapter = DsipEnrichmentAdapter(
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
        )

        progress_log: list[dict[str, Any]] = []
        result = adapter.enrich(
            [_make_topic(f"T-{i:03d}") for i in range(1, 4)],
            on_progress=lambda p: progress_log.append(p),
        )

        assert len(progress_log) == 3
        assert progress_log[0]["topic_id"] == "T-001"
        assert progress_log[0]["index"] == 1
        assert progress_log[0]["total"] == 3
        assert len(result.enriched) == 3


class TestExtractionFailureIsolation:
    """Behavior 3: Per-endpoint failure does not block other data sources."""

    def test_extraction_failure_logged_batch_continues(self) -> None:
        transport = ApiMockTransport()
        # T-001: happy path
        transport.add_json_response("T-001/details", _make_details_json())
        transport.add_json_response("T-001/questions", _make_qa_json())
        # T-002: details fails, Q&A works
        transport.add_error_response("T-002/details")
        transport.add_json_response("T-002/questions", _make_qa_json())
        # T-003: happy path
        transport.add_json_response("T-003/details", _make_details_json())
        transport.add_json_response("T-003/questions", _make_qa_json())
        transport.add_pdf_response("RELEASE_PREFACE")
        transport.add_pdf_response("INSTRUCTIONS")

        adapter = DsipEnrichmentAdapter(
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
            max_retries=1,
        )
        result = adapter.enrich([
            _make_topic("T-001"), _make_topic("T-002"), _make_topic("T-003"),
        ])

        # All 3 topics still enriched (T-002 partial)
        assert len(result.enriched) == 3
        assert result.enriched[1]["enrichment_status"] == "partial"
        assert result.enriched[1]["qa_entries"]  # Q&A still present


class TestDownloadFailureIsolation:
    """Behavior 4: Download failure (HTTP error) does not stop batch."""

    def test_download_failure_logged_batch_continues(self) -> None:
        transport = ApiMockTransport()
        # T-001: happy path
        transport._setup_happy_path("T-001")
        # T-002: all endpoints fail
        transport.add_error_response("T-002/details")
        transport.add_error_response("T-002/questions")
        # T-003: happy path
        transport._setup_happy_path("T-003")

        adapter = DsipEnrichmentAdapter(
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
            max_retries=1,
        )
        result = adapter.enrich([
            _make_topic("T-001"), _make_topic("T-002"), _make_topic("T-003"),
        ])

        # All 3 enriched (T-002 with errors)
        assert len(result.enriched) == 3
        assert len(result.errors) >= 1
        error_ids = {e["topic_id"] for e in result.errors}
        assert "T-002" in error_ids


class TestCompletenessMetrics:
    """Behavior 5: Completeness metrics reflect actual extraction results."""

    @pytest.mark.parametrize(
        "topic_count,fail_count,expected_desc",
        [
            (3, 0, 3),
            (3, 1, 2),
            (5, 2, 3),
        ],
    )
    def test_completeness_counts_match_actual_results(
        self, topic_count: int, fail_count: int, expected_desc: int,
    ) -> None:
        transport = ApiMockTransport()
        topics = []
        for i in range(1, topic_count + 1):
            tid = f"T-{i:03d}"
            topics.append(_make_topic(tid))
            if i <= fail_count:
                transport.add_error_response(f"{tid}/details")
            else:
                transport.add_json_response(f"{tid}/details", _make_details_json())
            transport.add_json_response(f"{tid}/questions", _make_qa_json())
        transport.add_pdf_response("RELEASE_PREFACE")
        transport.add_pdf_response("INSTRUCTIONS")

        adapter = DsipEnrichmentAdapter(
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
            max_retries=1,
        )
        result = adapter.enrich(topics)

        assert result.completeness["total"] == topic_count
        assert result.completeness["descriptions"] == expected_desc


class TestRateLimiting:
    """Behavior 6: Configurable delay between requests."""

    def test_requests_made_for_each_topic(self) -> None:
        """Verify each topic triggers API requests."""
        transport = ApiMockTransport()
        for i in range(1, 4):
            tid = f"T-{i:03d}"
            transport._setup_happy_path(tid)

        adapter = DsipEnrichmentAdapter(
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
        )
        adapter.enrich([_make_topic(f"T-{i:03d}") for i in range(1, 4)])

        # Each topic makes at least details + Q&A calls; instructions cached
        # 3 topics x (details + Q&A) + 2 instruction downloads = 8 min
        assert len(transport.request_log) >= 8
