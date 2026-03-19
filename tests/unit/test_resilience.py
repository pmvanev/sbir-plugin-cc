"""Unit tests for resilience features -- step 02-02.

Test Budget: 6 behaviors x 2 = 12 max unit tests.
Tests invoke through driving ports:
- FinderService.search() for structural change detection and message propagation
- DsipEnrichmentAdapter.enrich() for retry, timeout, structural detection

Behaviors tested:
1. Structural change detection (missing expected keys in fetch response)
2. Diagnostic save on structural change (raw response to debug file)
3. What/why/do error messages for structural change
4. Retry with exponential backoff on transient enrichment failures
5. All retries exhausted produces clear failure with what/why/do
6. Configurable timeout per enrichment request
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from pes.adapters.dsip_enrichment_adapter import DsipEnrichmentAdapter
from pes.domain.finder_service import FinderService
from tests.acceptance.dsip_topic_scraper.fakes import InMemoryTopicFetchAdapter


def _make_profile() -> dict[str, Any]:
    """Minimal profile for FinderService."""
    return {
        "company_name": "Test Corp",
        "capabilities": ["testing"],
        "certifications": {"sam_gov": {"active": True}},
        "past_performance": [{"agency": "Test"}],
        "key_personnel": [{"name": "Test Person"}],
    }


# ---------------------------------------------------------------------------
# Behavior 1: Structural change detection
# ---------------------------------------------------------------------------


class TestStructuralChangeDetection:
    """FinderService detects structural_change prefix in fetch errors
    and produces specific what/why/do messages."""

    def test_structural_change_error_produces_what_why_do_messages(self) -> None:
        """When fetch returns structural_change error, FinderService messages
        contain what/why/do pattern explaining the API change."""
        adapter = InMemoryTopicFetchAdapter(
            topics=[],
            available=True,
            structural_change=True,
        )
        service = FinderService(topic_fetch=adapter, profile=_make_profile())

        result = service.search()

        assert result.error is not None
        all_messages = " ".join(result.messages).lower()
        # What: explains what happened
        assert "what:" in all_messages or "structure" in all_messages
        # Why: explains possible reason
        assert "why:" in all_messages or "api" in all_messages
        # Do: suggests fallback action
        assert "--file" in " ".join(result.messages) or "file" in all_messages


# ---------------------------------------------------------------------------
# Behavior 2: Diagnostic save on structural change
# ---------------------------------------------------------------------------


class TestDiagnosticSave:
    """FinderService saves raw response to .sbir/dsip_debug_response.json
    on structural change detection."""

    def test_structural_change_saves_debug_response(self, tmp_path: Path) -> None:
        """When structural change detected, raw response saved to debug file."""
        sbir_dir = tmp_path / ".sbir"
        sbir_dir.mkdir()
        debug_path = sbir_dir / "dsip_debug_response.json"

        adapter = InMemoryTopicFetchAdapter(
            topics=[],
            available=True,
            structural_change=True,
        )
        service = FinderService(
            topic_fetch=adapter,
            profile=_make_profile(),
            diagnostic_dir=sbir_dir,
        )

        service.search()

        assert debug_path.exists(), "Debug response file should be saved"
        data = json.loads(debug_path.read_text())
        assert "error" in data or "raw_error" in data


# ---------------------------------------------------------------------------
# Behavior 3: What/why/do error messages format
# ---------------------------------------------------------------------------


class TestStructuralChangeMessageContent:
    """Structural change messages contain actionable guidance for the user."""

    def test_structural_change_messages_contain_actionable_content(self) -> None:
        """When FinderService detects a structural_change error from the fetch port,
        the returned messages contain:
        - What: identifies the specific structural change detected
        - Why: explains the likely cause (API schema update)
        - Do: provides a concrete fallback action (use --file with BAA PDF)
        """
        adapter = InMemoryTopicFetchAdapter(
            topics=[],
            available=True,
            structural_change=True,
        )
        service = FinderService(topic_fetch=adapter, profile=_make_profile())

        result = service.search()

        # Verify error is propagated
        assert result.error is not None
        assert "structural_change" in result.error

        messages = result.messages
        assert len(messages) >= 3, f"Expected at least 3 messages (what/why/do), got {len(messages)}"

        # What message includes the specific change detail from the error
        what_msgs = [m for m in messages if m.lower().startswith("what:")]
        assert len(what_msgs) == 1, f"Expected exactly 1 'What:' message, got: {messages}"
        assert "expected" in what_msgs[0].lower() or "structure" in what_msgs[0].lower(), \
            f"What message should describe the structural issue: {what_msgs[0]}"

        # Why message references the API
        why_msgs = [m for m in messages if m.lower().startswith("why:")]
        assert len(why_msgs) == 1, f"Expected exactly 1 'Why:' message, got: {messages}"
        assert "api" in why_msgs[0].lower() or "schema" in why_msgs[0].lower(), \
            f"Why message should reference API change: {why_msgs[0]}"

        # Do message provides actionable fallback
        do_msgs = [m for m in messages if m.lower().startswith("do:")]
        assert len(do_msgs) == 1, f"Expected exactly 1 'Do:' message, got: {messages}"
        assert "--file" in do_msgs[0], \
            f"Do message should suggest --file fallback: {do_msgs[0]}"


# ---------------------------------------------------------------------------
# Behavior 4: Retry with exponential backoff on transient failures
# ---------------------------------------------------------------------------


class RetryMockTransport(httpx.BaseTransport):
    """Mock transport that fails N times then succeeds."""

    def __init__(self, fail_count: int, success_content: bytes) -> None:
        self._fail_count = fail_count
        self._success_content = success_content
        self.attempt_count = 0
        self.request_timestamps: list[float] = []

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        import time
        self.attempt_count += 1
        self.request_timestamps.append(time.monotonic())
        if self.attempt_count <= self._fail_count:
            return httpx.Response(status_code=503, content=b"Service Unavailable")
        return httpx.Response(
            status_code=200,
            content=self._success_content,
            headers={"content-type": "application/pdf"},
        )


class TimeoutMockTransport(httpx.BaseTransport):
    """Mock transport that always raises timeout."""

    def __init__(self) -> None:
        self.attempt_count = 0

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.attempt_count += 1
        raise httpx.TimeoutException("Connection timed out")


def _make_simple_pdf() -> bytes:
    """Minimal PDF bytes that pypdf can parse (with description marker)."""
    stream = b"BT /F1 12 Tf 72 720 Td (DESCRIPTION Test topic description content for validation purposes) Tj ET"
    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"4 0 obj\n<< /Length " + str(len(stream)).encode() + b" >>\n"
        b"stream\n" + stream + b"\nendstream\nendobj\n"
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
    return pdf


class TestRetryWithBackoff:
    """Enrichment adapter retries transient failures with exponential backoff."""

    def test_retries_after_transient_failure_and_succeeds(self) -> None:
        """Adapter retries on 503 and succeeds on subsequent attempt."""
        pdf_bytes = _make_simple_pdf()
        transport = RetryMockTransport(fail_count=1, success_content=pdf_bytes)
        adapter = DsipEnrichmentAdapter(
            base_url="https://example.com/topics/api/public/topics",
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
            max_retries=3,
            retry_base_seconds=0.01,  # Fast for tests
        )

        result = adapter.enrich(["TOPIC-001"])

        assert len(result.enriched) == 1
        assert len(result.errors) == 0
        assert transport.attempt_count == 2  # 1 fail + 1 success

    def test_backoff_increases_between_retries(self) -> None:
        """Adapter waits longer between successive retries."""
        pdf_bytes = _make_simple_pdf()
        transport = RetryMockTransport(fail_count=2, success_content=pdf_bytes)
        adapter = DsipEnrichmentAdapter(
            base_url="https://example.com/topics/api/public/topics",
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
            max_retries=3,
            retry_base_seconds=0.05,
        )

        result = adapter.enrich(["TOPIC-001"])

        assert len(result.enriched) == 1
        assert transport.attempt_count == 3
        # Verify backoff: second wait should be longer than first
        if len(transport.request_timestamps) >= 3:
            wait_1 = transport.request_timestamps[1] - transport.request_timestamps[0]
            wait_2 = transport.request_timestamps[2] - transport.request_timestamps[1]
            assert wait_2 > wait_1, "Exponential backoff should increase wait time"


# ---------------------------------------------------------------------------
# Behavior 5: All retries exhausted
# ---------------------------------------------------------------------------


class TestRetriesExhausted:
    """When all retries fail, adapter reports error with what/why/do."""

    def test_all_retries_exhausted_reports_error(self) -> None:
        """After max retries, topic is recorded as error with retry info."""
        transport = TimeoutMockTransport()
        adapter = DsipEnrichmentAdapter(
            base_url="https://example.com/topics/api/public/topics",
            rate_limit_seconds=0.0,
            http_client=httpx.Client(transport=transport),
            max_retries=3,
            retry_base_seconds=0.01,
        )

        result = adapter.enrich(["TOPIC-001"])

        assert len(result.enriched) == 0
        assert len(result.errors) == 1
        error_msg = result.errors[0]["error"].lower()
        assert "retry" in error_msg or "attempt" in error_msg or "failed" in error_msg
        assert transport.attempt_count == 3


# ---------------------------------------------------------------------------
# Behavior 6: Configurable timeout
# ---------------------------------------------------------------------------


class TestConfigurableTimeout:
    """Enrichment adapter accepts configurable timeout per request."""

    def test_timeout_parameter_accepted(self) -> None:
        """Adapter constructor accepts timeout parameter."""
        adapter = DsipEnrichmentAdapter(
            base_url="https://example.com/topics",
            timeout=45.0,
        )
        assert adapter._timeout == 45.0

    def test_default_timeout_is_30_seconds(self) -> None:
        """Default timeout is 30 seconds."""
        adapter = DsipEnrichmentAdapter(
            base_url="https://example.com/topics",
        )
        assert adapter._timeout == 30.0
