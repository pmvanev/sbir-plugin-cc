"""Tests for housekeeping -- through EnforcementEngine driving port + targeted domain tests.

Tests invoke EnforcementEngine.check_session_start() with a real
housekeeping module and fake adapters at port boundaries.

Targeted domain tests (B8-B14) test CrashSignalCleaner and AuditLogRotator
directly for mutation coverage.

Test Budget: 14 behaviors x 2 = 28 max unit tests
Behaviors:
  B1 - Single crash signal removed and cleanup audited
  B2 - Multiple crash signals all removed, each cleanup audited
  B3 - Locked/unremovable crash signal produces warning, session continues
  B4 - Clean workspace starts normally, no cleanup entries
  B5 - Retention rotation archives old entries and preserves current ones
  B6 - Boundary entries (exactly 365 days) are preserved, not archived
  B7 - Size rotation archives oversized file and starts fresh
  --- Targeted domain tests for mutation coverage ---
  B8 - CrashSignalCleaner.clean returns list of cleaned paths
  B9 - CrashSignalCleaner.clean handles missing dir
  B10 - CrashSignalCleaner.clean handles locked files
  B11 - AuditLogRotator._retention_cutoff_date returns correct boundary
  B12 - AuditLogRotator._partition_entries splits by cutoff date
  B13 - AuditLogRotator._write_retention_archive writes archive file
  B14 - AuditLogRotator size rotation threshold boundary
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pes.domain.engine import EnforcementEngine
from pes.domain.rules import Decision
from pes.ports.audit_port import AuditLogger
from pes.ports.rule_port import RuleLoader


# --- Fake adapters at port boundaries ---


class FakeRuleLoader(RuleLoader):
    def load_rules(self):
        return []


class FakeAuditLogger(AuditLogger):
    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    def log(self, entry: dict[str, Any]) -> None:
        self.entries.append(entry)


# --- Fixtures ---


@pytest.fixture()
def audit_logger() -> FakeAuditLogger:
    return FakeAuditLogger()


@pytest.fixture()
def engine(audit_logger: FakeAuditLogger) -> EnforcementEngine:
    return EnforcementEngine(FakeRuleLoader(), audit_logger)


@pytest.fixture()
def base_state() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "proposal_id": "test-uuid-hk",
        "go_no_go": "pending",
        "current_wave": 0,
        "topic": {"id": "AF243-001", "deadline": "2026-04-15"},
    }


@pytest.fixture()
def proposal_dir(tmp_path: Path) -> Path:
    sbir_dir = tmp_path / ".sbir"
    sbir_dir.mkdir()
    return tmp_path


def _create_crash_signal(sbir_dir: Path, name: str = "session-crash.signal") -> Path:
    signal = sbir_dir / name
    signal.write_text(json.dumps({
        "session_id": "prev-001",
        "timestamp": "2026-03-17T14:30:00Z",
        "reason": "unexpected_termination",
    }))
    return signal


# --- B1: Single crash signal removed and cleanup audited ---


class TestSingleCrashSignalCleanup:

    def test_crash_signal_removed_on_session_start(
        self,
        engine: EnforcementEngine,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        signal = _create_crash_signal(proposal_dir / ".sbir")
        assert signal.exists()

        result = engine.check_session_start(
            base_state, proposal_dir=str(proposal_dir)
        )

        assert result.decision == Decision.ALLOW
        assert not signal.exists()

    def test_crash_signal_cleanup_is_audited(
        self,
        engine: EnforcementEngine,
        audit_logger: FakeAuditLogger,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        _create_crash_signal(proposal_dir / ".sbir")

        engine.check_session_start(base_state, proposal_dir=str(proposal_dir))

        cleanup_entries = [
            e for e in audit_logger.entries
            if e.get("event") == "crash_signal_cleanup"
        ]
        assert len(cleanup_entries) >= 1


# --- B2: Multiple crash signals all removed, each audited ---


class TestMultipleCrashSignalCleanup:

    def test_all_crash_signals_removed(
        self,
        engine: EnforcementEngine,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        sbir_dir = proposal_dir / ".sbir"
        signals = [
            _create_crash_signal(sbir_dir, f"session-crash-{i}.signal")
            for i in range(3)
        ]

        engine.check_session_start(base_state, proposal_dir=str(proposal_dir))

        for s in signals:
            assert not s.exists(), f"Signal still exists: {s}"

    def test_each_cleanup_individually_audited(
        self,
        engine: EnforcementEngine,
        audit_logger: FakeAuditLogger,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        sbir_dir = proposal_dir / ".sbir"
        for i in range(3):
            _create_crash_signal(sbir_dir, f"session-crash-{i}.signal")

        engine.check_session_start(base_state, proposal_dir=str(proposal_dir))

        cleanup_entries = [
            e for e in audit_logger.entries
            if e.get("event") == "crash_signal_cleanup"
        ]
        assert len(cleanup_entries) == 3


# --- B3: Locked crash signal produces warning, session continues ---


class TestLockedCrashSignalWarning:

    @pytest.mark.skipif(
        __import__("os").getuid() == 0 if hasattr(__import__("os"), "getuid") else False,
        reason="Root can delete read-only files; test requires non-root",
    )
    def test_locked_signal_produces_warning_message(
        self,
        engine: EnforcementEngine,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        import os
        import stat

        signal = _create_crash_signal(proposal_dir / ".sbir")
        os.chmod(str(signal), stat.S_IREAD)

        try:
            result = engine.check_session_start(
                base_state, proposal_dir=str(proposal_dir)
            )

            assert result.decision == Decision.ALLOW
            warning_msgs = [
                m for m in result.messages
                if "could not be removed" in m.lower()
                or "unable to remove" in m.lower()
                or "locked" in m.lower()
                or "permission" in m.lower()
            ]
            assert len(warning_msgs) >= 1
        finally:
            # Restore permissions for cleanup
            os.chmod(str(signal), stat.S_IWRITE | stat.S_IREAD)


# --- B4: Clean workspace, no cleanup entries ---


class TestCleanWorkspaceNoCleanup:

    def test_no_cleanup_entries_when_no_crash_signals(
        self,
        engine: EnforcementEngine,
        audit_logger: FakeAuditLogger,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        result = engine.check_session_start(
            base_state, proposal_dir=str(proposal_dir)
        )

        assert result.decision == Decision.ALLOW
        cleanup_entries = [
            e for e in audit_logger.entries
            if e.get("event") == "crash_signal_cleanup"
        ]
        assert len(cleanup_entries) == 0
        # But session_start audit entry IS present
        session_entries = [
            e for e in audit_logger.entries
            if e.get("event") == "session_start"
        ]
        assert len(session_entries) == 1


# --- Helpers for audit log rotation tests ---


def _create_audit_log(audit_dir: Path, entries_data: list[dict]) -> Path:
    """Write audit entries as JSON lines to the standard audit log file."""
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_file = audit_dir / "pes-audit.log"
    lines = [json.dumps(entry) for entry in entries_data]
    audit_file.write_text("\n".join(lines) + "\n")
    return audit_file


# --- B5: Retention rotation archives old entries, preserves current ---


class TestRetentionRotation:

    def test_old_entries_archived_and_current_preserved(
        self,
        engine: EnforcementEngine,
        audit_logger: FakeAuditLogger,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        from datetime import UTC, datetime, timedelta

        audit_dir = proposal_dir / ".sbir" / "audit"
        old_ts = (datetime.now(UTC) - timedelta(days=400)).isoformat()
        recent_ts = datetime.now(UTC).isoformat()
        _create_audit_log(audit_dir, [
            {"timestamp": old_ts, "event": "evaluate", "decision": "allow"},
            {"timestamp": recent_ts, "event": "evaluate", "decision": "block"},
        ])

        engine.check_session_start(base_state, proposal_dir=str(proposal_dir))

        # Active log should NOT contain the old entry
        active_file = audit_dir / "pes-audit.log"
        assert active_file.exists()
        active_lines = [
            l for l in active_file.read_text().strip().split("\n") if l.strip()
        ]
        active_timestamps = [
            json.loads(l).get("timestamp") for l in active_lines
            if "evaluate" in l
        ]
        assert old_ts not in active_timestamps

        # Archive file should exist with old entry
        archive_files = list(audit_dir.glob("pes-audit.log.archive*"))
        assert len(archive_files) >= 1

    def test_retention_rotation_is_audited(
        self,
        engine: EnforcementEngine,
        audit_logger: FakeAuditLogger,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        from datetime import UTC, datetime, timedelta

        audit_dir = proposal_dir / ".sbir" / "audit"
        old_ts = (datetime.now(UTC) - timedelta(days=400)).isoformat()
        _create_audit_log(audit_dir, [
            {"timestamp": old_ts, "event": "evaluate", "decision": "allow"},
        ])

        engine.check_session_start(base_state, proposal_dir=str(proposal_dir))

        rotation_entries = [
            e for e in audit_logger.entries
            if e.get("event") == "audit_log_retention_rotation"
        ]
        assert len(rotation_entries) >= 1


# --- B6: Boundary entries (exactly 365 days) preserved ---


class TestBoundaryRetention:

    def test_entries_at_exactly_365_days_are_preserved(
        self,
        engine: EnforcementEngine,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        from datetime import UTC, datetime, timedelta

        audit_dir = proposal_dir / ".sbir" / "audit"
        boundary_ts = (datetime.now(UTC) - timedelta(days=365)).isoformat()
        _create_audit_log(audit_dir, [
            {"timestamp": boundary_ts, "event": "evaluate", "decision": "allow"},
        ])

        engine.check_session_start(base_state, proposal_dir=str(proposal_dir))

        # No archive file should be created
        archive_files = list(audit_dir.glob("pes-audit.log.archive*"))
        assert len(archive_files) == 0

        # Entry should still be in active log
        active_file = audit_dir / "pes-audit.log"
        active_lines = [
            l for l in active_file.read_text().strip().split("\n") if l.strip()
        ]
        evaluate_entries = [l for l in active_lines if "evaluate" in l]
        assert len(evaluate_entries) >= 1

    def test_entries_at_366_days_are_archived(
        self,
        engine: EnforcementEngine,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        from datetime import UTC, datetime, timedelta

        audit_dir = proposal_dir / ".sbir" / "audit"
        past_ts = (datetime.now(UTC) - timedelta(days=366)).isoformat()
        recent_ts = datetime.now(UTC).isoformat()
        _create_audit_log(audit_dir, [
            {"timestamp": past_ts, "event": "evaluate", "decision": "allow"},
            {"timestamp": recent_ts, "event": "evaluate", "decision": "block"},
        ])

        engine.check_session_start(base_state, proposal_dir=str(proposal_dir))

        archive_files = list(audit_dir.glob("pes-audit.log.archive*"))
        assert len(archive_files) >= 1


# --- B7: Size rotation archives oversized file, starts fresh ---


class TestSizeRotation:

    def test_oversized_file_archived_with_timestamp_and_fresh_started(
        self,
        engine: EnforcementEngine,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        from datetime import UTC, datetime

        audit_dir = proposal_dir / ".sbir" / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        audit_file = audit_dir / "pes-audit.log"
        # Write 11MB of content
        entry = json.dumps({
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "evaluate",
            "decision": "allow",
        })
        line = entry + "\n"
        target_size = 11 * 1024 * 1024
        audit_file.write_text(line * (target_size // len(line) + 1))

        engine.check_session_start(base_state, proposal_dir=str(proposal_dir))

        # Archive file should exist
        archive_files = list(audit_dir.glob("pes-audit.log.archive*"))
        assert len(archive_files) >= 1

        # Fresh log should be small
        assert audit_file.exists()
        assert audit_file.stat().st_size < 1024 * 1024

    def test_size_rotation_is_audited(
        self,
        engine: EnforcementEngine,
        audit_logger: FakeAuditLogger,
        base_state: dict[str, Any],
        proposal_dir: Path,
    ) -> None:
        from datetime import UTC, datetime

        audit_dir = proposal_dir / ".sbir" / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        audit_file = audit_dir / "pes-audit.log"
        entry = json.dumps({
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "evaluate",
            "decision": "allow",
        })
        line = entry + "\n"
        target_size = 11 * 1024 * 1024
        audit_file.write_text(line * (target_size // len(line) + 1))

        engine.check_session_start(base_state, proposal_dir=str(proposal_dir))

        rotation_entries = [
            e for e in audit_logger.entries
            if e.get("event") == "audit_log_size_rotation"
        ]
        assert len(rotation_entries) >= 1


# =============================================================================
# Targeted domain tests for mutation coverage
# =============================================================================
# These test CrashSignalCleaner and AuditLogRotator directly to catch
# fine-grained mutations that the EnforcementEngine driving-port tests miss.

from datetime import UTC, datetime, timedelta

from pes.domain.housekeeping import AuditLogRotator, CrashSignalCleaner


# --- B8: CrashSignalCleaner.clean returns list of cleaned paths ---


class TestCrashSignalCleanerDirect:

    def test_clean_returns_removed_status_with_filename(self, tmp_path: Path) -> None:
        sbir_dir = tmp_path / ".sbir"
        sbir_dir.mkdir()
        signal = sbir_dir / "test.signal"
        signal.write_text("crash")

        cleaner = CrashSignalCleaner()
        results = cleaner.clean(str(tmp_path))

        assert len(results) == 1
        assert results[0]["file"] == "test.signal"
        assert results[0]["status"] == "removed"

    def test_clean_removes_multiple_signals_sorted(self, tmp_path: Path) -> None:
        sbir_dir = tmp_path / ".sbir"
        sbir_dir.mkdir()
        for name in ["b.signal", "a.signal", "c.signal"]:
            (sbir_dir / name).write_text("crash")

        cleaner = CrashSignalCleaner()
        results = cleaner.clean(str(tmp_path))

        assert len(results) == 3
        filenames = [r["file"] for r in results]
        assert filenames == ["a.signal", "b.signal", "c.signal"]
        assert all(r["status"] == "removed" for r in results)

    def test_clean_does_not_touch_non_signal_files(self, tmp_path: Path) -> None:
        sbir_dir = tmp_path / ".sbir"
        sbir_dir.mkdir()
        (sbir_dir / "state.json").write_text("{}")
        (sbir_dir / "test.signal").write_text("crash")

        cleaner = CrashSignalCleaner()
        results = cleaner.clean(str(tmp_path))

        assert len(results) == 1
        assert (sbir_dir / "state.json").exists()


# --- B9: CrashSignalCleaner.clean handles missing dir ---


class TestCrashSignalCleanerMissingDir:

    def test_clean_returns_empty_list_when_sbir_dir_missing(self, tmp_path: Path) -> None:
        cleaner = CrashSignalCleaner()
        results = cleaner.clean(str(tmp_path))
        assert results == []

    def test_clean_returns_empty_list_when_no_signals(self, tmp_path: Path) -> None:
        sbir_dir = tmp_path / ".sbir"
        sbir_dir.mkdir()

        cleaner = CrashSignalCleaner()
        results = cleaner.clean(str(tmp_path))
        assert results == []


# --- B10: CrashSignalCleaner.clean handles locked files ---


class TestCrashSignalCleanerLockedFiles:

    @pytest.mark.skipif(
        __import__("os").name != "nt",
        reason="Read-only removal test only reliable on Windows",
    )
    def test_locked_file_returns_failed_status(self, tmp_path: Path) -> None:
        import os
        import stat

        sbir_dir = tmp_path / ".sbir"
        sbir_dir.mkdir()
        signal = sbir_dir / "locked.signal"
        signal.write_text("crash")
        os.chmod(str(signal), stat.S_IREAD)

        try:
            cleaner = CrashSignalCleaner()
            results = cleaner.clean(str(tmp_path))

            assert len(results) == 1
            assert results[0]["status"] == "failed"
            assert results[0]["file"] == "locked.signal"
            assert "reason" in results[0]
        finally:
            os.chmod(str(signal), stat.S_IWRITE | stat.S_IREAD)


# --- B11: AuditLogRotator._retention_cutoff_date ---


class TestAuditLogRotatorCutoffDate:

    def test_default_retention_is_365_days(self) -> None:
        rotator = AuditLogRotator()
        cutoff = rotator._retention_cutoff_date()
        expected = (datetime.now(UTC) - timedelta(days=365)).date()
        assert cutoff == expected

    def test_custom_retention_days(self) -> None:
        rotator = AuditLogRotator(retention_days=30)
        cutoff = rotator._retention_cutoff_date()
        expected = (datetime.now(UTC) - timedelta(days=30)).date()
        assert cutoff == expected


# --- B12: AuditLogRotator._partition_entries ---


class TestAuditLogRotatorPartition:

    def test_old_entries_go_to_archived(self) -> None:
        cutoff = datetime(2026, 1, 15, tzinfo=UTC).date()
        old_entry = json.dumps({"timestamp": "2025-12-01T00:00:00+00:00", "event": "x"})
        new_entry = json.dumps({"timestamp": "2026-02-01T00:00:00+00:00", "event": "y"})

        current, archived = AuditLogRotator._partition_entries(
            [old_entry, new_entry], cutoff
        )

        assert len(archived) == 1
        assert len(current) == 1
        assert "2025-12-01" in archived[0]
        assert "2026-02-01" in current[0]

    def test_entry_on_cutoff_date_stays_current(self) -> None:
        cutoff = datetime(2026, 1, 15, tzinfo=UTC).date()
        boundary_entry = json.dumps({"timestamp": "2026-01-15T12:00:00+00:00", "event": "x"})

        current, archived = AuditLogRotator._partition_entries(
            [boundary_entry], cutoff
        )

        assert len(current) == 1
        assert len(archived) == 0

    def test_entry_one_day_before_cutoff_is_archived(self) -> None:
        cutoff = datetime(2026, 1, 15, tzinfo=UTC).date()
        old_entry = json.dumps({"timestamp": "2026-01-14T23:59:59+00:00", "event": "x"})

        current, archived = AuditLogRotator._partition_entries(
            [old_entry], cutoff
        )

        assert len(archived) == 1
        assert len(current) == 0

    def test_unparseable_lines_stay_in_current(self) -> None:
        cutoff = datetime(2026, 1, 15, tzinfo=UTC).date()

        current, archived = AuditLogRotator._partition_entries(
            ["not valid json", ""], cutoff
        )

        assert len(current) == 1  # "not valid json" kept; empty stripped
        assert len(archived) == 0

    def test_entry_without_timestamp_stays_current(self) -> None:
        cutoff = datetime(2026, 1, 15, tzinfo=UTC).date()
        no_ts = json.dumps({"event": "x"})

        current, archived = AuditLogRotator._partition_entries(
            [no_ts], cutoff
        )

        assert len(current) == 1
        assert len(archived) == 0

    def test_naive_timestamp_treated_as_utc(self) -> None:
        cutoff = datetime(2026, 1, 15, tzinfo=UTC).date()
        naive_old = json.dumps({"timestamp": "2025-06-01T00:00:00", "event": "x"})

        current, archived = AuditLogRotator._partition_entries(
            [naive_old], cutoff
        )

        assert len(archived) == 1


# --- B13: AuditLogRotator._write_retention_archive ---


class TestAuditLogRotatorWriteArchive:

    def test_write_archive_creates_archive_file(self, tmp_path: Path) -> None:
        log_file = tmp_path / "pes-audit.log"
        log_file.write_text("")

        result = AuditLogRotator._write_retention_archive(
            log_file,
            current_entries=["current1", "current2"],
            archived_entries=["old1", "old2"],
        )

        assert result is not None
        assert result["action"] == "retention_rotation"
        assert result["archived_count"] == 2
        assert "archive" in result["archive_file"]

        # Verify archive file content
        archive_files = list(tmp_path.glob("pes-audit.log.archive*"))
        assert len(archive_files) == 1
        archive_content = archive_files[0].read_text()
        assert "old1" in archive_content
        assert "old2" in archive_content

        # Verify active log rewritten
        active_content = log_file.read_text()
        assert "current1" in active_content
        assert "current2" in active_content
        assert "old1" not in active_content


# --- B14: AuditLogRotator size rotation threshold boundary ---


class TestAuditLogRotatorSizeThreshold:

    def test_file_at_exact_threshold_is_not_rotated(self, tmp_path: Path) -> None:
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()
        log_file = audit_dir / "pes-audit.log"

        rotator = AuditLogRotator(max_file_size_bytes=100)
        # Write exactly 100 bytes
        log_file.write_text("x" * 100)

        results = rotator.rotate(str(audit_dir))

        # At threshold = no size rotation (only > triggers it)
        size_results = [r for r in results if r.get("action") == "size_rotation"]
        assert len(size_results) == 0

    def test_file_one_byte_over_threshold_is_rotated(self, tmp_path: Path) -> None:
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()
        log_file = audit_dir / "pes-audit.log"

        rotator = AuditLogRotator(max_file_size_bytes=100)
        log_file.write_text("x" * 101)

        results = rotator.rotate(str(audit_dir))

        size_results = [r for r in results if r.get("action") == "size_rotation"]
        assert len(size_results) == 1
        assert size_results[0]["original_size"] == 101

    def test_file_under_threshold_not_rotated(self, tmp_path: Path) -> None:
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()
        log_file = audit_dir / "pes-audit.log"

        rotator = AuditLogRotator(max_file_size_bytes=100)
        log_file.write_text("x" * 50)

        results = rotator.rotate(str(audit_dir))

        size_results = [r for r in results if r.get("action") == "size_rotation"]
        assert len(size_results) == 0

    def test_rotate_returns_empty_when_no_log_file(self, tmp_path: Path) -> None:
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()

        rotator = AuditLogRotator()
        results = rotator.rotate(str(audit_dir))

        assert results == []

    def test_size_rotation_creates_fresh_empty_file(self, tmp_path: Path) -> None:
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()
        log_file = audit_dir / "pes-audit.log"

        rotator = AuditLogRotator(max_file_size_bytes=100)
        log_file.write_text("x" * 200)

        rotator.rotate(str(audit_dir))

        assert log_file.exists()
        assert log_file.read_text() == ""
        archive_files = list(audit_dir.glob("pes-audit.log.archive*"))
        assert len(archive_files) == 1
