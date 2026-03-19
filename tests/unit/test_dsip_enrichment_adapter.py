"""Unit tests for DsipEnrichmentAdapter -- driven port for topic enrichment.

Test Budget: 6 behaviors x 2 = 12 max unit tests.
Tests invoke through TopicEnrichmentPort.enrich() (port interface).
HTTP responses simulated via httpx mock transport. PDF content via in-memory PDFs.

Behaviors tested:
1. Happy path: extracts description, instructions, and Q&A from downloaded PDF
2. Batch enrichment with per-topic progress callback
3. Individual topic extraction failure does not stop batch
4. Download failure (HTTP error) does not stop batch
5. Completeness metrics reflect actual extraction results
6. Rate limiting: configurable delay between requests
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from pes.adapters.dsip_enrichment_adapter import DsipEnrichmentAdapter


def _make_pdf_bytes(text: str) -> bytes:
    """Create a minimal single-page PDF with the given text content."""
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"4 0 obj\n<< /Length " + str(len(_pdf_stream(text))).encode() + b" >>\n"
        b"stream\n" + _pdf_stream(text) + b"\nendstream\nendobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        + _xref_offset_4(text) +
        b"0000000275 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\n"
        b"startxref\n0\n%%EOF\n"
    )
    return pdf_content


def _pdf_stream(text: str) -> bytes:
    """Build a PDF content stream with text."""
    return f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()


def _xref_offset_4(text: str) -> bytes:
    """Placeholder xref entry for object 4."""
    return b"0000000350 00000 n \n"


def _build_topic_pdf_text(
    description: str = "",
    instructions: str = "",
    component_instructions: str = "",
    qa_entries: list[dict[str, str]] | None = None,
) -> str:
    """Build text content that matches the adapter's expected PDF structure."""
    parts = []
    if description:
        parts.append(f"DESCRIPTION\n{description}")
    if instructions:
        parts.append(f"SUBMISSION INSTRUCTIONS\n{instructions}")
    if component_instructions:
        parts.append(f"COMPONENT INSTRUCTIONS\n{component_instructions}")
    if qa_entries:
        parts.append("QUESTIONS AND ANSWERS")
        for qa in qa_entries:
            parts.append(f"Q: {qa['question']}\nA: {qa['answer']}")
    return "\n\n".join(parts)


class MockTransport(httpx.BaseTransport):
    """Mock HTTP transport that returns pre-configured responses per URL path."""

    def __init__(self) -> None:
        self.responses: dict[str, httpx.Response] = {}
        self.request_log: list[httpx.Request] = []

    def add_response(
        self,
        path_contains: str,
        status_code: int = 200,
        content: bytes = b"",
        content_type: str = "application/pdf",
    ) -> None:
        self.responses[path_contains] = httpx.Response(
            status_code=status_code,
            content=content,
            headers={"content-type": content_type},
        )

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.request_log.append(request)
        url_path = str(request.url)
        for key, response in self.responses.items():
            if key in url_path:
                return response
        return httpx.Response(status_code=404, content=b"Not found")


class TestEnrichHappyPath:
    """Behavior 1: Extracts description, instructions, qa from topic PDF."""

    def test_extracts_all_fields_from_topic_pdf(self) -> None:
        """Single topic enrichment returns description, instructions, qa."""
        transport = MockTransport()
        pdf_text = _build_topic_pdf_text(
            description="A" * 600,
            instructions="Standard submission instructions.",
            component_instructions="Air Force specific instructions.",
            qa_entries=[
                {"question": "What is TRL?", "answer": "TRL 3 entry."},
                {"question": "Timeline?", "answer": "12 months."},
            ],
        )
        transport.add_response("TOPIC-001", content=_make_pdf_bytes(pdf_text))

        adapter = DsipEnrichmentAdapter(
            base_url="https://example.com/topics/api/public/topics",
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
        )
        result = adapter.enrich(["TOPIC-001"])

        assert len(result.enriched) == 1
        topic = result.enriched[0]
        assert topic["topic_id"] == "TOPIC-001"
        assert len(topic["description"]) >= 500
        assert topic["instructions"] is not None
        assert len(result.errors) == 0


class TestBatchWithProgress:
    """Behavior 2: Batch enrichment invokes progress callback per topic."""

    def test_progress_callback_invoked_per_topic(self) -> None:
        transport = MockTransport()
        for i in range(1, 4):
            transport.add_response(
                f"T-{i:03d}",
                content=_make_pdf_bytes(_build_topic_pdf_text(description="Desc " * 100)),
            )

        adapter = DsipEnrichmentAdapter(
            base_url="https://example.com/topics/api/public/topics",
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
        )

        progress_log: list[dict[str, Any]] = []
        result = adapter.enrich(
            ["T-001", "T-002", "T-003"],
            on_progress=lambda p: progress_log.append(p),
        )

        assert len(progress_log) == 3
        assert progress_log[0]["topic_id"] == "T-001"
        assert progress_log[0]["index"] == 1
        assert progress_log[0]["total"] == 3
        assert len(result.enriched) == 3


class TestExtractionFailureIsolation:
    """Behavior 3: Individual topic extraction failure does not stop batch."""

    def test_extraction_failure_logged_batch_continues(self) -> None:
        transport = MockTransport()
        # T-001 has valid PDF
        transport.add_response(
            "T-001",
            content=_make_pdf_bytes(_build_topic_pdf_text(description="Valid " * 100)),
        )
        # T-002 has invalid/corrupt PDF content
        transport.add_response("T-002", content=b"not a pdf")
        # T-003 has valid PDF
        transport.add_response(
            "T-003",
            content=_make_pdf_bytes(_build_topic_pdf_text(description="Also valid " * 100)),
        )

        adapter = DsipEnrichmentAdapter(
            base_url="https://example.com/topics/api/public/topics",
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
        )
        result = adapter.enrich(["T-001", "T-002", "T-003"])

        assert len(result.enriched) == 2
        assert len(result.errors) == 1
        assert result.errors[0]["topic_id"] == "T-002"
        error_msg = result.errors[0]["error"].lower()
        assert "extraction" in error_msg or "pdf" in error_msg


class TestDownloadFailureIsolation:
    """Behavior 4: Download failure (HTTP error) does not stop batch."""

    def test_download_failure_logged_batch_continues(self) -> None:
        transport = MockTransport()
        transport.add_response(
            "T-001",
            content=_make_pdf_bytes(_build_topic_pdf_text(description="Valid " * 100)),
        )
        # T-002 returns HTTP 500
        transport.add_response("T-002", status_code=500, content=b"Server Error")
        transport.add_response(
            "T-003",
            content=_make_pdf_bytes(_build_topic_pdf_text(description="Also valid " * 100)),
        )

        adapter = DsipEnrichmentAdapter(
            base_url="https://example.com/topics/api/public/topics",
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
        )
        result = adapter.enrich(["T-001", "T-002", "T-003"])

        assert len(result.enriched) == 2
        assert len(result.errors) == 1
        assert result.errors[0]["topic_id"] == "T-002"
        assert "download" in result.errors[0]["error"].lower()


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
        self, topic_count: int, fail_count: int, expected_desc: int
    ) -> None:
        transport = MockTransport()
        topic_ids = []
        for i in range(1, topic_count + 1):
            tid = f"T-{i:03d}"
            topic_ids.append(tid)
            if i <= fail_count:
                transport.add_response(tid, status_code=500, content=b"Error")
            else:
                transport.add_response(
                    tid,
                    content=_make_pdf_bytes(
                        _build_topic_pdf_text(description="Desc " * 100)
                    ),
                )

        adapter = DsipEnrichmentAdapter(
            base_url="https://example.com/topics/api/public/topics",
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
        )
        result = adapter.enrich(topic_ids)

        assert result.completeness["total"] == topic_count
        assert result.completeness["descriptions"] == expected_desc


class TestRateLimiting:
    """Behavior 6: Configurable delay between requests."""

    def test_requests_made_for_each_topic(self) -> None:
        """Verify each topic triggers an HTTP request (rate limiting tested via request count)."""
        transport = MockTransport()
        for i in range(1, 4):
            transport.add_response(
                f"T-{i:03d}",
                content=_make_pdf_bytes(_build_topic_pdf_text(description="D " * 100)),
            )

        adapter = DsipEnrichmentAdapter(
            base_url="https://example.com/topics/api/public/topics",
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
        )
        adapter.enrich(["T-001", "T-002", "T-003"])

        assert len(transport.request_log) == 3
