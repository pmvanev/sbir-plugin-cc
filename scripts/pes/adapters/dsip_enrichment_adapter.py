"""DSIP enrichment adapter -- fetches topic details via 3 API data sources.

Implements TopicEnrichmentPort using the DSIP public API to fetch:
1. Structured topic details (description, objective, keywords, etc.)
2. Q&A entries with double-JSON answer parsing
3. Instruction PDFs (solicitation + component) with text extraction via pypdf

Features:
- Per-endpoint failure isolation (one failing source does not block others)
- Per-cycle+component instruction PDF caching within a batch
- Q&A skipped for topics with published_qa_count == 0
- HTML tag stripping for detail fields
- Configurable rate limiting and retry with exponential backoff
"""

from __future__ import annotations

import io
import json
import logging
import re
import time
from typing import Any

import httpx
from pypdf import PdfReader

from pes.ports.topic_enrichment_port import EnrichmentResult, TopicEnrichmentPort

logger = logging.getLogger(__name__)

DSIP_BASE_URL = "https://www.dodsbirsttr.mil"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_RATE_LIMIT_SECONDS = 1.0
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; sbir-plugin/1.0)",
    "Accept": "application/json",
}

DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BASE_SECONDS = 5.0

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(html: str | None) -> str:
    """Strip HTML tags and decode common entities."""
    if not html:
        return ""
    text = _HTML_TAG_RE.sub("", html)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">")
    return text.strip()


class DsipEnrichmentAdapter(TopicEnrichmentPort):
    """DSIP adapter for API-based topic enrichment.

    Fetches structured details, Q&A, and instruction PDFs from DSIP API.

    Args:
        base_url: Base URL for DSIP API endpoints.
        timeout: HTTP request timeout in seconds.
        rate_limit_seconds: Delay between per-topic requests.
        http_client: Optional pre-configured httpx.Client (for testing).
        max_retries: Maximum retry attempts on transient failure.
        retry_base_seconds: Base delay for exponential backoff between retries.
    """

    def __init__(
        self,
        base_url: str = DSIP_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        rate_limit_seconds: float = DEFAULT_RATE_LIMIT_SECONDS,
        http_client: httpx.Client | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_base_seconds: float = DEFAULT_RETRY_BASE_SECONDS,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._rate_limit_seconds = rate_limit_seconds
        self._client = http_client or httpx.Client(
            timeout=timeout, headers=DEFAULT_HEADERS,
        )
        self._max_retries = max_retries
        self._retry_base_seconds = retry_base_seconds

    def enrich(
        self,
        topics: list[dict[str, Any]],
        on_progress: Any | None = None,
    ) -> EnrichmentResult:
        """Enrich topics via 3 API data sources: details, Q&A, instructions.

        Per-topic failures are isolated: one failing data source does not
        block others for the same or different topics.
        """
        enriched: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        desc_count = 0
        qa_count = 0
        sol_instr_count = 0
        comp_instr_count = 0

        # Instruction PDF cache: (cycle_name, component, release_number) -> text
        instruction_cache: dict[tuple[str, str, int], str | None] = {}
        solicitation_cache: dict[tuple[str, int], str | None] = {}

        for i, topic in enumerate(topics):
            topic_id = topic.get("topic_id", "")
            cycle_name = topic.get("cycle_name", "")
            release_number = topic.get("release_number", 0)
            component = topic.get("component", "")
            published_qa_count = topic.get("published_qa_count", 0)

            progress: dict[str, Any] = {
                "index": i + 1,
                "total": len(topics),
                "topic_id": topic_id,
            }

            entry: dict[str, Any] = {
                "topic_id": topic_id,
                "description": "",
                "objective": None,
                "keywords": [],
                "technology_areas": [],
                "focus_areas": [],
                "itar": None,
                "cmmc_level": None,
                "qa_entries": [],
                "instructions": None,
                "component_instructions": None,
                "solicitation_instructions": None,
            }
            has_failure = False

            # --- Source 1: Details API ---
            try:
                details = self._fetch_details(topic_id)
                entry["description"] = _strip_html(details.get("description"))
                entry["objective"] = _strip_html(details.get("objective"))
                entry["keywords"] = self._parse_keywords(details.get("keywords", ""))
                entry["technology_areas"] = details.get("technologyAreas", [])
                entry["focus_areas"] = details.get("focusAreas", [])
                entry["itar"] = details.get("itar")
                entry["cmmc_level"] = details.get("cmmcLevel")
                desc_count += 1
            except Exception as exc:
                logger.warning("Details fetch failed for topic %s: %s", topic_id, exc)
                has_failure = True

            # --- Source 2: Q&A API ---
            if published_qa_count > 0:
                try:
                    qa_raw = self._fetch_qa(topic_id)
                    entry["qa_entries"] = self._parse_qa_entries(qa_raw)
                    qa_count += 1
                except Exception as exc:
                    logger.warning("Q&A fetch failed for topic %s: %s", topic_id, exc)
                    has_failure = True

            # --- Source 3a: Solicitation instructions PDF ---
            sol_key = (cycle_name, release_number)
            if sol_key in solicitation_cache:
                entry["solicitation_instructions"] = solicitation_cache[sol_key]
                entry["instructions"] = solicitation_cache[sol_key]
                if solicitation_cache[sol_key] is not None:
                    sol_instr_count += 1
            else:
                try:
                    sol_text = self._fetch_solicitation_instructions(
                        cycle_name, release_number,
                    )
                    solicitation_cache[sol_key] = sol_text
                    entry["solicitation_instructions"] = sol_text
                    entry["instructions"] = sol_text
                    if sol_text:
                        sol_instr_count += 1
                except Exception as exc:
                    logger.warning(
                        "Solicitation instructions fetch failed for %s: %s",
                        cycle_name, exc,
                    )
                    solicitation_cache[sol_key] = None
                    has_failure = True

            # --- Source 3b: Component instructions PDF ---
            comp_key = (cycle_name, component, release_number)
            if comp_key in instruction_cache:
                entry["component_instructions"] = instruction_cache[comp_key]
                if instruction_cache[comp_key] is not None:
                    comp_instr_count += 1
            else:
                try:
                    comp_text = self._fetch_component_instructions(
                        cycle_name, component, release_number,
                    )
                    instruction_cache[comp_key] = comp_text
                    entry["component_instructions"] = comp_text
                    if comp_text:
                        comp_instr_count += 1
                except Exception as exc:
                    logger.warning(
                        "Component instructions fetch failed for %s/%s: %s",
                        cycle_name, component, exc,
                    )
                    instruction_cache[comp_key] = None
                    has_failure = True

            # Set enrichment status
            entry["enrichment_status"] = "partial" if has_failure else "ok"

            enriched.append(entry)
            progress["status"] = entry["enrichment_status"]

            if has_failure:
                errors.append({
                    "topic_id": topic_id,
                    "error": "one or more data sources failed",
                })

            self._notify_and_delay(on_progress, progress, i, len(topics))

        return EnrichmentResult(
            enriched=enriched,
            errors=errors,
            completeness={
                "descriptions": desc_count,
                "qa": qa_count,
                "solicitation_instructions": sol_instr_count,
                "component_instructions": comp_instr_count,
                "total": len(topics),
            },
        )

    # --- API fetch methods ---

    def _fetch_details(self, topic_id: str) -> dict[str, Any]:
        """Fetch topic details from /topics/api/public/topics/{id}/details."""
        url = f"{self._base_url}/topics/api/public/topics/{topic_id}/details"
        return self._get_json(url)

    def _fetch_qa(self, topic_id: str) -> list[dict[str, Any]]:
        """Fetch Q&A from /topics/api/public/topics/{id}/questions."""
        url = f"{self._base_url}/topics/api/public/topics/{topic_id}/questions"
        return self._get_json(url)

    def _fetch_solicitation_instructions(
        self, cycle_name: str, release_number: int,
    ) -> str | None:
        """Fetch BAA preface PDF and extract text."""
        url = (
            f"{self._base_url}/submissions/api/public/download/"
            f"solicitationDocuments?solicitation={cycle_name}"
            f"&release={release_number}&documentType=RELEASE_PREFACE"
        )
        pdf_bytes = self._get_bytes(url)
        return self._extract_text_from_pdf(pdf_bytes)

    def _fetch_component_instructions(
        self, cycle_name: str, component: str, release_number: int,
    ) -> str | None:
        """Fetch component instructions PDF and extract text."""
        url = (
            f"{self._base_url}/submissions/api/public/download/"
            f"solicitationDocuments?solicitation={cycle_name}"
            f"&documentType=INSTRUCTIONS&component={component}"
            f"&release={release_number}"
        )
        pdf_bytes = self._get_bytes(url)
        return self._extract_text_from_pdf(pdf_bytes)

    # --- HTTP helpers ---

    def _get_json(self, url: str) -> Any:
        """GET JSON with retry and exponential backoff."""
        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                response = self._client.get(url)
                response.raise_for_status()
                return response.json()
            except (httpx.TimeoutException, httpx.HTTPStatusError) as exc:
                last_error = exc
                if attempt < self._max_retries - 1:
                    backoff = self._retry_base_seconds * (2 ** attempt)
                    logger.warning(
                        "Transient failure for %s (attempt %d/%d), retrying in %.1fs: %s",
                        url, attempt + 1, self._max_retries, backoff, exc,
                    )
                    time.sleep(backoff)
            except httpx.HTTPError as exc:
                last_error = exc
                break
        raise RuntimeError(f"GET {url} failed after {self._max_retries} attempts: {last_error}")

    def _get_bytes(self, url: str) -> bytes:
        """GET binary content with retry and exponential backoff."""
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
                        "Transient failure for %s (attempt %d/%d), retrying in %.1fs: %s",
                        url, attempt + 1, self._max_retries, backoff, exc,
                    )
                    time.sleep(backoff)
            except httpx.HTTPError as exc:
                last_error = exc
                break
        raise RuntimeError(f"GET {url} failed after {self._max_retries} attempts: {last_error}")

    # --- Parsing helpers ---

    @staticmethod
    def _parse_keywords(keywords_str: str) -> list[str]:
        """Parse semicolon-separated keywords into trimmed list."""
        if not keywords_str:
            return []
        return [kw.strip() for kw in keywords_str.split(";") if kw.strip()]

    @staticmethod
    def _parse_qa_entries(qa_raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Parse Q&A entries, extracting nested JSON answers."""
        entries: list[dict[str, Any]] = []
        for item in qa_raw:
            question = item.get("question", "")
            question_no = item.get("questionNo", 0)
            status = item.get("questionStatus", "")

            # Extract answer from double-JSON format
            answer_text = ""
            answers = item.get("answers", [])
            if answers:
                raw_answer = answers[0].get("answer", "")
                try:
                    parsed = json.loads(raw_answer)
                    answer_text = parsed.get("content", raw_answer)
                except (json.JSONDecodeError, TypeError, AttributeError):
                    answer_text = raw_answer

            entries.append({
                "question_no": question_no,
                "question": question,
                "answer": answer_text,
                "status": status,
            })
        return entries

    @staticmethod
    def _extract_text_from_pdf(pdf_bytes: bytes) -> str | None:
        """Extract text from PDF bytes using pypdf."""
        if not pdf_bytes:
            return None
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            pages_text: list[str] = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            return "\n".join(pages_text) if pages_text else None
        except Exception as exc:
            logger.warning("PDF text extraction failed: %s", exc)
            return None

    def _notify_and_delay(
        self,
        on_progress: Any | None,
        progress: dict[str, Any],
        index: int,
        total: int,
    ) -> None:
        """Send progress callback and apply rate limiting delay."""
        if on_progress is not None:
            on_progress(progress)
        self._rate_limit_delay(index, total)

    def _rate_limit_delay(self, index: int, total: int) -> None:
        """Apply rate limiting delay between requests (skip after last)."""
        if index < total - 1 and self._rate_limit_seconds > 0:
            time.sleep(self._rate_limit_seconds)
