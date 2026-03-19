"""DSIP enrichment adapter -- downloads topic PDFs and extracts detail data.

Implements TopicEnrichmentPort using the DSIP public API to download
per-topic PDF documents and extract description, submission instructions,
component instructions, and Q&A entries using pypdf.

Features:
- Per-topic PDF download from DSIP API
- Text extraction and section parsing via pypdf
- Per-topic failure isolation (log and continue)
- Progress callback per topic
- Configurable rate limiting between requests
- Completeness metrics (descriptions, instructions, Q&A counts)
"""

from __future__ import annotations

import io
import logging
import time
from typing import Any

import httpx
from pypdf import PdfReader

from pes.ports.topic_enrichment_port import EnrichmentResult, TopicEnrichmentPort

logger = logging.getLogger(__name__)

DSIP_TOPIC_PDF_URL = "https://www.dodsbirsttr.mil/topics/api/public/topics"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_RATE_LIMIT_SECONDS = 1.0


DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BASE_SECONDS = 5.0


class DsipEnrichmentAdapter(TopicEnrichmentPort):
    """DSIP adapter for per-topic PDF enrichment.

    Downloads topic PDFs from DSIP API, extracts text via pypdf,
    and parses sections into structured enrichment data.

    Args:
        base_url: Base URL for topic PDF download endpoint.
        timeout: HTTP request timeout in seconds.
        rate_limit_seconds: Delay between per-topic requests.
        http_client: Optional pre-configured httpx.Client (for testing).
        max_retries: Maximum retry attempts per download on transient failure.
        retry_base_seconds: Base delay for exponential backoff between retries.
    """

    def __init__(
        self,
        base_url: str = DSIP_TOPIC_PDF_URL,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        rate_limit_seconds: float = DEFAULT_RATE_LIMIT_SECONDS,
        http_client: httpx.Client | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_base_seconds: float = DEFAULT_RETRY_BASE_SECONDS,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._rate_limit_seconds = rate_limit_seconds
        self._client = http_client or httpx.Client(timeout=timeout)
        self._max_retries = max_retries
        self._retry_base_seconds = retry_base_seconds

    def enrich(
        self,
        topic_ids: list[str],
        on_progress: Any | None = None,
    ) -> EnrichmentResult:
        """Enrich topics by downloading PDFs and extracting detail data.

        Per-topic failures are isolated: logged in errors, do not stop batch.
        Progress callback invoked per topic with status updates.
        """
        enriched: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        desc_count = 0
        instr_count = 0
        qa_count = 0

        for i, topic_id in enumerate(topic_ids):
            progress: dict[str, Any] = {
                "index": i + 1,
                "total": len(topic_ids),
                "topic_id": topic_id,
            }

            try:
                pdf_bytes = self._download_pdf(topic_id)
            except Exception as exc:
                logger.warning("Download failed for topic %s: %s", topic_id, exc)
                progress["status"] = "download_failed"
                errors.append({
                    "topic_id": topic_id,
                    "error": f"document download failed: {exc}",
                })
                if on_progress is not None:
                    on_progress(progress)
                self._rate_limit_delay(i, len(topic_ids))
                continue

            try:
                data = self._extract_from_pdf(pdf_bytes)
            except Exception as exc:
                logger.warning("Extraction failed for topic %s: %s", topic_id, exc)
                progress["status"] = "extraction_failed"
                errors.append({
                    "topic_id": topic_id,
                    "error": f"extraction failed: {exc}",
                })
                if on_progress is not None:
                    on_progress(progress)
                self._rate_limit_delay(i, len(topic_ids))
                continue

            progress["status"] = "ok"
            enriched.append({
                "topic_id": topic_id,
                "description": data.get("description", ""),
                "instructions": data.get("instructions"),
                "component_instructions": data.get("component_instructions"),
                "qa_entries": data.get("qa_entries", []),
            })

            desc_count += 1 if data.get("description") else 0
            instr_count += 1 if data.get("instructions") else 0
            qa_count += 1 if data.get("qa_entries") else 0

            if on_progress is not None:
                on_progress(progress)

            self._rate_limit_delay(i, len(topic_ids))

        return EnrichmentResult(
            enriched=enriched,
            errors=errors,
            completeness={
                "descriptions": desc_count,
                "instructions": instr_count,
                "qa": qa_count,
                "total": len(topic_ids),
            },
        )

    def _download_pdf(self, topic_id: str) -> bytes:
        """Download topic PDF from DSIP API with retry and exponential backoff.

        Retries on transient failures (HTTP 5xx, timeouts) up to max_retries.

        Raises:
            RuntimeError: After all retry attempts exhausted.
        """
        url = f"{self._base_url}/{topic_id}/download/PDF"
        last_error: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                response = self._client.get(url)
                response.raise_for_status()
                return response.content
            except (httpx.TimeoutException, httpx.HTTPStatusError) as exc:
                last_error = exc
                if attempt < self._max_retries - 1:
                    backoff = self._retry_base_seconds * (2 ** attempt)
                    logger.warning(
                        "Transient failure for topic %s (attempt %d/%d), "
                        "retrying in %.1fs: %s",
                        topic_id, attempt + 1, self._max_retries, backoff, exc,
                    )
                    time.sleep(backoff)
            except httpx.HTTPError as exc:
                last_error = exc
                break

        msg = (
            f"document download failed after {self._max_retries} attempts "
            f"for topic {topic_id}"
        )
        if last_error:
            msg = f"{msg}: {last_error}"
        raise RuntimeError(msg)

    def _extract_from_pdf(self, pdf_bytes: bytes) -> dict[str, Any]:
        """Extract structured data from PDF bytes using pypdf.

        Parses the PDF text looking for known section markers:
        - DESCRIPTION
        - SUBMISSION INSTRUCTIONS
        - COMPONENT INSTRUCTIONS
        - QUESTIONS AND ANSWERS

        Returns:
            Dict with keys: description, instructions, component_instructions, qa_entries.
        """
        reader = PdfReader(io.BytesIO(pdf_bytes))
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"

        return self._parse_sections(full_text)

    def _parse_sections(self, text: str) -> dict[str, Any]:
        """Parse extracted text into structured sections."""
        result: dict[str, Any] = {
            "description": "",
            "instructions": None,
            "component_instructions": None,
            "qa_entries": [],
        }

        # Normalize whitespace
        text = text.strip()
        if not text:
            return result

        # Define section markers (case-insensitive search)
        upper_text = text.upper()

        sections = {
            "DESCRIPTION": "description",
            "SUBMISSION INSTRUCTIONS": "instructions",
            "COMPONENT INSTRUCTIONS": "component_instructions",
            "QUESTIONS AND ANSWERS": "qa_section",
        }

        # Find positions of each section marker
        positions: list[tuple[int, str, str]] = []
        for marker, key in sections.items():
            pos = upper_text.find(marker)
            if pos >= 0:
                positions.append((pos, marker, key))

        positions.sort(key=lambda x: x[0])

        # Extract content between markers
        for idx, (pos, marker, key) in enumerate(positions):
            start = pos + len(marker)
            end = positions[idx + 1][0] if idx + 1 < len(positions) else len(text)
            content = text[start:end].strip()

            if key == "qa_section":
                result["qa_entries"] = self._parse_qa(content)
            elif key == "description":
                result["description"] = content
            else:
                result[key] = content if content else None

        return result

    def _parse_qa(self, text: str) -> list[dict[str, str]]:
        """Parse Q&A section into list of question/answer dicts."""
        entries: list[dict[str, str]] = []
        if not text.strip():
            return entries

        # Split on Q: markers
        parts = text.split("Q:")
        for part in parts[1:]:  # Skip text before first Q:
            part = part.strip()
            if "A:" in part:
                q_part, a_part = part.split("A:", 1)
                entries.append({
                    "question": q_part.strip(),
                    "answer": a_part.strip(),
                })
            elif part.strip():
                entries.append({
                    "question": part.strip(),
                    "answer": "",
                })

        return entries

    def _rate_limit_delay(self, index: int, total: int) -> None:
        """Apply rate limiting delay between requests (skip after last)."""
        if index < total - 1 and self._rate_limit_seconds > 0:
            time.sleep(self._rate_limit_seconds)
