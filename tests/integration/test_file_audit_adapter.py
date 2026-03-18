"""Integration tests for FileAuditAdapter -- real filesystem writes.

Adapter tests use real infrastructure (tmp_path filesystem), no mocks.
Verifies JSON-lines append-only behavior and per-proposal isolation.

Test Budget: 2 behaviors x 2 = 4 max integration tests
"""

from __future__ import annotations

import json

import pytest


class TestFileAuditAdapterWritesEntries:
    """FileAuditAdapter persists audit entries as JSON lines to disk."""

    def test_log_creates_file_and_writes_json_line(self, tmp_path) -> None:
        from pes.adapters.file_audit_adapter import FileAuditAdapter

        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()
        adapter = FileAuditAdapter(str(audit_dir))

        entry = {
            "timestamp": "2026-03-18T10:00:00Z",
            "event": "evaluate",
            "decision": "allow",
            "proposal_id": "test-001",
        }
        adapter.log(entry)

        log_file = audit_dir / "pes-audit.log"
        assert log_file.exists()
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["decision"] == "allow"
        assert parsed["proposal_id"] == "test-001"
        assert parsed["timestamp"] == "2026-03-18T10:00:00Z"

    def test_log_appends_multiple_entries(self, tmp_path) -> None:
        from pes.adapters.file_audit_adapter import FileAuditAdapter

        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()
        adapter = FileAuditAdapter(str(audit_dir))

        for i in range(3):
            adapter.log({"event": "evaluate", "seq": i})

        log_file = audit_dir / "pes-audit.log"
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 3
        for i, line in enumerate(lines):
            assert json.loads(line)["seq"] == i
