"""Tests for EnforcementEngine -- driving port for PES rule evaluation.

Tests invoke through the EnforcementEngine public API with fake adapters
at port boundaries (RuleLoader, AuditLogger). No mocks inside the hexagon.

Test Budget: 13 behaviors x 2 = 26 max unit tests
"""

from __future__ import annotations

from typing import Any

import pytest

from pes.domain.engine import EnforcementEngine
from pes.domain.rules import Decision, EnforcementRule
from pes.ports.audit_port import AuditLogger
from pes.ports.rule_port import RuleLoader

# --- Fake adapters at port boundaries ---


class FakeRuleLoader(RuleLoader):
    """Fake rule loader returning preconfigured rules."""

    def __init__(self, rules: list[EnforcementRule] | None = None) -> None:
        self._rules = rules or []

    def load_rules(self) -> list[EnforcementRule]:
        return self._rules


class FakeAuditLogger(AuditLogger):
    """Fake audit logger capturing entries for assertion."""

    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    def log(self, entry: dict[str, Any]) -> None:
        self.entries.append(entry)


class FailingAuditLogger(AuditLogger):
    """Audit logger that raises on every log call -- simulates I/O failure."""

    def log(self, entry: dict[str, Any]) -> None:
        raise OSError("Audit directory not writable")


# --- Fixtures ---


@pytest.fixture()
def audit_logger() -> FakeAuditLogger:
    return FakeAuditLogger()


@pytest.fixture()
def clean_state() -> dict[str, Any]:
    """Consistent proposal state with Go decision, no orphaned files."""
    return {
        "schema_version": "1.0.0",
        "proposal_id": "test-uuid-001",
        "go_no_go": "go",
        "current_wave": 1,
        "waves": {
            "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
            "1": {"status": "active", "completed_at": None},
        },
        "topic": {"deadline": "2026-04-15"},
        "strategy_brief": {"status": "not_started"},
        "compliance_matrix": {"item_count": 0},
    }


@pytest.fixture()
def pending_state() -> dict[str, Any]:
    """Proposal state with Go/No-Go pending -- Wave 0."""
    return {
        "schema_version": "1.0.0",
        "proposal_id": "test-uuid-002",
        "go_no_go": "pending",
        "current_wave": 0,
        "waves": {
            "0": {"status": "active", "completed_at": None},
        },
        "topic": {"deadline": "2026-04-15"},
        "strategy_brief": {"status": "not_started"},
        "compliance_matrix": {"item_count": 0},
    }


def _wave_ordering_rule() -> EnforcementRule:
    """Rule: Wave 1 requires Go decision in Wave 0."""
    return EnforcementRule(
        rule_id="wave-1-requires-go",
        description="Wave 1 strategy work requires Go decision",
        rule_type="wave_ordering",
        condition={"requires_go_no_go": "go", "target_wave": 1},
        message="Wave 1 requires Go decision in Wave 0",
    )


# --- Test Classes ---


class TestEnforcementEngineSessionStart:
    """Session startup integrity check through driving port."""

    def test_clean_state_returns_allow_with_no_messages(
        self, audit_logger: FakeAuditLogger, clean_state: dict[str, Any]
    ) -> None:
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        result = engine.check_session_start(clean_state)
        assert result.decision == Decision.ALLOW
        assert result.messages == []

    def test_session_start_logs_audit_entry(
        self, audit_logger: FakeAuditLogger, clean_state: dict[str, Any]
    ) -> None:
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        engine.check_session_start(clean_state)
        assert len(audit_logger.entries) == 1
        assert "timestamp" in audit_logger.entries[0]
        assert audit_logger.entries[0]["event"] == "session_start"


class TestEnforcementEngineEvaluate:
    """Rule evaluation for tool invocations through driving port."""

    def test_blocks_wave_1_when_go_decision_pending(
        self, audit_logger: FakeAuditLogger, pending_state: dict[str, Any]
    ) -> None:
        rules = [_wave_ordering_rule()]
        engine = EnforcementEngine(FakeRuleLoader(rules), audit_logger)
        result = engine.evaluate(pending_state, tool_name="wave_1_strategy")
        assert result.decision == Decision.BLOCK
        assert "Wave 1 requires Go decision in Wave 0" in result.messages

    def test_allows_wave_1_when_go_decision_made(
        self, audit_logger: FakeAuditLogger, clean_state: dict[str, Any]
    ) -> None:
        rules = [_wave_ordering_rule()]
        engine = EnforcementEngine(FakeRuleLoader(rules), audit_logger)
        result = engine.evaluate(clean_state, tool_name="wave_1_strategy")
        assert result.decision == Decision.ALLOW

    def test_allows_action_when_no_rules_configured(
        self, audit_logger: FakeAuditLogger, clean_state: dict[str, Any]
    ) -> None:
        engine = EnforcementEngine(FakeRuleLoader([]), audit_logger)
        result = engine.evaluate(clean_state, tool_name="any_tool")
        assert result.decision == Decision.ALLOW
        assert result.messages == []


class TestEnforcementEngineAuditLogging:
    """Audit logging of enforcement decisions."""

    @pytest.mark.parametrize(
        "state_fixture,tool,expected_decision",
        [
            ("pending_state", "wave_1_strategy", "block"),
            ("clean_state", "wave_1_strategy", "allow"),
        ],
    )
    def test_audit_entry_records_lowercase_decision_with_required_fields(
        self,
        audit_logger: FakeAuditLogger,
        state_fixture: str,
        tool: str,
        expected_decision: str,
        request,
    ) -> None:
        state = request.getfixturevalue(state_fixture)
        rules = [_wave_ordering_rule()]
        engine = EnforcementEngine(FakeRuleLoader(rules), audit_logger)
        engine.evaluate(state, tool_name=tool)
        assert len(audit_logger.entries) == 1
        entry = audit_logger.entries[0]
        assert entry["decision"] == expected_decision
        assert "timestamp" in entry
        assert "proposal_id" in entry
        assert entry["tool_name"] == tool

    def test_session_start_audit_entry_has_lowercase_decision(
        self, audit_logger: FakeAuditLogger, clean_state: dict[str, Any]
    ) -> None:
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        engine.check_session_start(clean_state)
        assert len(audit_logger.entries) == 1
        entry = audit_logger.entries[0]
        assert entry["decision"] == "allow"
        assert entry["event"] == "session_start"
        assert "proposal_id" in entry


class TestEnforcementEngineNonBlockingAudit:
    """Audit write failures must not block enforcement decisions."""

    def test_evaluate_returns_correct_decision_when_audit_fails(
        self, clean_state: dict[str, Any]
    ) -> None:
        rules = [_wave_ordering_rule()]
        engine = EnforcementEngine(FakeRuleLoader(rules), FailingAuditLogger())
        result = engine.evaluate(clean_state, tool_name="wave_1_strategy")
        assert result.decision == Decision.ALLOW

    def test_session_start_returns_result_when_audit_fails(
        self, clean_state: dict[str, Any]
    ) -> None:
        engine = EnforcementEngine(FakeRuleLoader(), FailingAuditLogger())
        result = engine.check_session_start(clean_state)
        assert result.decision == Decision.ALLOW
        assert result.messages == []


class TestEnforcementEngineAuditIsolation:
    """Separate proposals with separate audit loggers produce isolated audit trails."""

    def test_concurrent_proposals_write_to_isolated_audit_loggers(
        self, clean_state: dict[str, Any]
    ) -> None:
        """Two engines with separate audit loggers produce independent entries."""
        logger_a = FakeAuditLogger()
        logger_b = FakeAuditLogger()
        state_a = {**clean_state, "proposal_id": "proposal-A"}
        state_b = {**clean_state, "proposal_id": "proposal-B"}

        engine_a = EnforcementEngine(FakeRuleLoader(), logger_a)
        engine_b = EnforcementEngine(FakeRuleLoader(), logger_b)

        engine_a.check_session_start(state_a)
        engine_b.check_session_start(state_b)

        # Each logger has exactly one entry
        assert len(logger_a.entries) == 1
        assert len(logger_b.entries) == 1
        # No cross-contamination
        assert logger_a.entries[0]["proposal_id"] == "proposal-A"
        assert logger_b.entries[0]["proposal_id"] == "proposal-B"


class TestEnforcementEngineAppendOnly:
    """Audit entries are append-only -- prior entries never change."""

    def test_prior_entries_unchanged_after_new_decisions(
        self, audit_logger: FakeAuditLogger, clean_state: dict[str, Any]
    ) -> None:
        """Recording new decisions does not modify previously written entries."""
        import copy

        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)

        # Record first decision
        engine.evaluate(clean_state, tool_name="tool_a")
        snapshot = copy.deepcopy(audit_logger.entries)

        # Record second decision
        engine.evaluate(clean_state, tool_name="tool_b")

        # Prior entry unchanged
        assert len(audit_logger.entries) == 2
        assert audit_logger.entries[0] == snapshot[0]
        # New entry appended, not inserted
        assert audit_logger.entries[1]["tool_name"] == "tool_b"


class TestEnforcementEngineAgentDispatch:
    """Agent dispatch verification through driving port."""

    @pytest.mark.parametrize(
        "wave,agent_name",
        [
            (0, "corpus-librarian"),
            (0, "solution-shaper"),
            (3, "writer"),
            (4, "writer"),
            (4, "reviewer"),
            (6, "compliance-sheriff"),
            (7, "reviewer"),
            (9, "debrief-analyst"),
        ],
    )
    def test_authorized_agent_allowed_for_wave(
        self, audit_logger: FakeAuditLogger, wave: int, agent_name: str
    ) -> None:
        state = {
            "proposal_id": "test-uuid-agent",
            "current_wave": wave,
        }
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        result = engine.check_agent_dispatch(state, agent_name)
        assert result.decision == Decision.ALLOW

    def test_authorized_dispatch_logs_allow_audit_entry(
        self, audit_logger: FakeAuditLogger
    ) -> None:
        state = {"proposal_id": "test-uuid-agent", "current_wave": 4}
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        engine.check_agent_dispatch(state, "writer")
        assert len(audit_logger.entries) == 1
        entry = audit_logger.entries[0]
        assert entry["event"] == "agent_dispatch"
        assert entry["decision"] == "allow"
        assert entry["agent_name"] == "writer"
        assert "timestamp" in entry

    @pytest.mark.parametrize(
        "wave,agent_name",
        [
            (4, "researcher"),
            (2, "writer"),
            (0, "writer"),
            (8, "reviewer"),
        ],
    )
    def test_unauthorized_agent_blocked_with_reason(
        self, audit_logger: FakeAuditLogger, wave: int, agent_name: str
    ) -> None:
        state = {
            "proposal_id": "test-uuid-agent",
            "current_wave": wave,
        }
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        result = engine.check_agent_dispatch(state, agent_name)
        assert result.decision == Decision.BLOCK
        msg = result.messages[0]
        assert agent_name in msg
        assert str(wave) in msg

    def test_unauthorized_dispatch_logs_block_audit_entry(
        self, audit_logger: FakeAuditLogger
    ) -> None:
        state = {"proposal_id": "test-uuid-agent", "current_wave": 4}
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        engine.check_agent_dispatch(state, "researcher")
        assert len(audit_logger.entries) == 1
        entry = audit_logger.entries[0]
        assert entry["event"] == "agent_dispatch"
        assert entry["decision"] == "block"
        assert entry["agent_name"] == "researcher"

    def test_unknown_agent_blocked_as_unrecognized(
        self, audit_logger: FakeAuditLogger
    ) -> None:
        state = {"proposal_id": "test-uuid-agent", "current_wave": 4}
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        result = engine.check_agent_dispatch(state, "rogue-agent")
        assert result.decision == Decision.BLOCK
        assert "rogue-agent" in result.messages[0]
        assert "not a recognized agent" in result.messages[0]

    def test_no_active_proposal_blocks_dispatch(
        self, audit_logger: FakeAuditLogger
    ) -> None:
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        result = engine.check_agent_dispatch(None, "writer")
        assert result.decision == Decision.BLOCK
        assert "no active proposal" in result.messages[0].lower()

    def test_dispatch_resilient_to_audit_failure(self) -> None:
        state = {"proposal_id": "test-uuid-agent", "current_wave": 4}
        engine = EnforcementEngine(FakeRuleLoader(), FailingAuditLogger())
        result = engine.check_agent_dispatch(state, "writer")
        assert result.decision == Decision.ALLOW


class TestEnforcementEngineAgentStop:
    """Agent stop (deactivation) recording through driving port.

    Test Budget: 2 behaviors x 2 = 4 max unit tests
    """

    def test_record_agent_stop_logs_audit_with_agent_name_and_wave(
        self, audit_logger: FakeAuditLogger
    ) -> None:
        state = {"proposal_id": "test-uuid-agent", "current_wave": 4}
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        result = engine.record_agent_stop(state, "writer")
        assert result.decision == Decision.ALLOW
        assert len(audit_logger.entries) == 1
        entry = audit_logger.entries[0]
        assert entry["event"] == "agent_stop"
        assert entry["decision"] == "allow"
        assert entry["agent_name"] == "writer"
        assert entry["wave"] == 4
        assert entry["proposal_id"] == "test-uuid-agent"
        assert "timestamp" in entry

    def test_record_agent_stop_resilient_to_audit_failure(self) -> None:
        state = {"proposal_id": "test-uuid-agent", "current_wave": 4}
        engine = EnforcementEngine(FakeRuleLoader(), FailingAuditLogger())
        result = engine.record_agent_stop(state, "writer")
        assert result.decision == Decision.ALLOW


class TestEnforcementEngineMultiReasonBlock:
    """Audit entry for multi-rule blocks includes all block reasons."""

    def test_audit_entry_captures_all_block_reasons(
        self, audit_logger: FakeAuditLogger
    ) -> None:
        wave_rule = _wave_ordering_rule()
        submission_rule = EnforcementRule(
            rule_id="submission-immutability",
            description="Block writes to submitted proposal",
            rule_type="submission_immutability",
            condition={"requires_immutable": True},
            message="Proposal is submitted. Artifacts are read-only.",
        )
        state = {
            "schema_version": "1.0.0",
            "proposal_id": "test-uuid-003",
            "go_no_go": "pending",
            "current_wave": 1,
            "waves": {"0": {"status": "active", "completed_at": None}},
            "topic": {"deadline": "2026-04-15"},
            "submission": {"status": "submitted", "immutable": True},
        }
        engine = EnforcementEngine(
            FakeRuleLoader([wave_rule, submission_rule]), audit_logger
        )
        result = engine.evaluate(state, tool_name="wave_1_strategy")
        assert result.decision == Decision.BLOCK
        assert len(result.messages) >= 2
        # Audit entry should have all reasons
        assert len(audit_logger.entries) == 1
        assert len(audit_logger.entries[0]["messages"]) >= 2


class TestEnforcementEngineToolContext:
    """evaluate() accepts and forwards tool_context to evaluators.

    Test Budget: 2 behaviors x 2 = 4 max unit tests
    """

    def test_evaluate_accepts_tool_context_parameter(
        self, audit_logger: FakeAuditLogger, clean_state: dict[str, Any]
    ) -> None:
        """evaluate() accepts optional tool_context dict without error."""
        engine = EnforcementEngine(FakeRuleLoader([]), audit_logger)
        result = engine.evaluate(
            clean_state,
            tool_name="Write",
            tool_context={"file_path": "artifacts/wave-5-visuals/fig.svg"},
        )
        assert result.decision == Decision.ALLOW

    def test_evaluate_defaults_tool_context_to_empty_dict(
        self, audit_logger: FakeAuditLogger, clean_state: dict[str, Any]
    ) -> None:
        """Existing callers without tool_context continue to work -- backward compat."""
        rules = [_wave_ordering_rule()]
        engine = EnforcementEngine(FakeRuleLoader(rules), audit_logger)
        result = engine.evaluate(clean_state, tool_name="wave_1_strategy")
        assert result.decision == Decision.ALLOW

    def test_all_eight_evaluators_accept_tool_context_kwarg(
        self, audit_logger: FakeAuditLogger, pending_state: dict[str, Any]
    ) -> None:
        """All 8 evaluators work when tool_context is passed."""
        rules = [
            _wave_ordering_rule(),
            EnforcementRule(
                rule_id="pdc-gate",
                description="PDC gate",
                rule_type="pdc_gate",
                condition={"requires_pdc_green": True, "target_wave": 5},
                message="PDC not green",
            ),
            EnforcementRule(
                rule_id="deadline-blocking",
                description="Deadline",
                rule_type="deadline_blocking",
                condition={"critical_days": 3, "non_essential_waves": [2, 3]},
                message="Deadline",
            ),
            EnforcementRule(
                rule_id="submission-immutability",
                description="Submission",
                rule_type="submission_immutability",
                condition={"requires_immutable": True},
                message="Immutable",
            ),
            EnforcementRule(
                rule_id="corpus-integrity",
                description="Corpus",
                rule_type="corpus_integrity",
                condition={"append_only_tags": True},
                message="Corpus",
            ),
            EnforcementRule(
                rule_id="figure-pipeline-requires-specs",
                description="Figure pipeline gate",
                rule_type="figure_pipeline_gate",
                condition={
                    "target_directory": "wave-5-visuals",
                    "required_artifact": "figure-specs.md",
                },
                message="Specs required",
            ),
            EnforcementRule(
                rule_id="figure-generation-requires-style",
                description="Style profile gate",
                rule_type="style_profile_gate",
                condition={
                    "target_directory": "wave-5-visuals",
                    "required_artifact": "style-profile.yaml",
                    "skip_state_key": "style_analysis_skipped",
                },
                message="Style required",
            ),
            EnforcementRule(
                rule_id="drafting-requires-style-selection",
                description="Writing style gate",
                rule_type="writing_style_gate",
                condition={
                    "target_directory": "wave-4-drafting",
                    "required_global_artifact": "quality-preferences.json",
                    "skip_state_field": "writing_style_selection_skipped",
                },
                message="Style selection required",
            ),
        ]
        engine = EnforcementEngine(FakeRuleLoader(rules), audit_logger)
        # Should not raise TypeError -- all evaluators accept tool_context
        result = engine.evaluate(
            pending_state,
            tool_name="Write",
            tool_context={"file_path": "artifacts/wave-5-visuals/fig.svg"},
        )
        # We only care that no TypeError is raised; decision depends on rule logic
        assert result.decision in (Decision.ALLOW, Decision.BLOCK)


class TestEnforcementEngineFigurePipelineRegistration:
    """Evaluator registration for figure pipeline and style profile gates.

    Test Budget: 4 behaviors x 2 = 8 max unit tests
    Behaviors: figure_pipeline_gate dispatches, style_profile_gate dispatches,
               figure_pipeline_gate blocks when specs missing,
               style_profile_gate blocks when style missing.
    """

    def test_figure_pipeline_gate_evaluator_blocks_when_specs_missing(
        self, audit_logger: FakeAuditLogger
    ) -> None:
        """Engine dispatches figure_pipeline_gate rule to registered evaluator."""
        rule = EnforcementRule(
            rule_id="figure-pipeline-requires-specs",
            description="Figure writes require figure-specs.md",
            rule_type="figure_pipeline_gate",
            condition={
                "target_directory": "wave-5-visuals",
                "required_artifact": "figure-specs.md",
            },
            message="Cannot write figure files before creating figure specifications",
        )
        state = {
            "proposal_id": "test-uuid-fig",
            "current_wave": 5,
        }
        engine = EnforcementEngine(FakeRuleLoader([rule]), audit_logger)
        result = engine.evaluate(
            state,
            tool_name="Write",
            tool_context={
                "file_path": "artifacts/wave-5-visuals/figure-1.svg",
                "artifacts_present": [],
            },
        )
        assert result.decision == Decision.BLOCK
        assert "figure" in result.messages[0].lower()

    def test_style_profile_gate_evaluator_blocks_when_style_missing(
        self, audit_logger: FakeAuditLogger
    ) -> None:
        """Engine dispatches style_profile_gate rule to registered evaluator."""
        rule = EnforcementRule(
            rule_id="figure-generation-requires-style",
            description="Figure writes require style profile",
            rule_type="style_profile_gate",
            condition={
                "target_directory": "wave-5-visuals",
                "required_artifact": "style-profile.yaml",
                "skip_state_key": "style_analysis_skipped",
            },
            message="Cannot generate figures before style analysis",
        )
        state = {
            "proposal_id": "test-uuid-style",
            "current_wave": 5,
        }
        engine = EnforcementEngine(FakeRuleLoader([rule]), audit_logger)
        result = engine.evaluate(
            state,
            tool_name="Write",
            tool_context={
                "file_path": "artifacts/wave-5-visuals/figure-1.svg",
                "artifacts_present": ["figure-specs.md"],
            },
        )
        assert result.decision == Decision.BLOCK
        assert "style" in result.messages[0].lower()

    def test_figure_pipeline_gate_allows_when_specs_present(
        self, audit_logger: FakeAuditLogger
    ) -> None:
        """Figure pipeline gate allows when figure-specs.md is present."""
        rule = EnforcementRule(
            rule_id="figure-pipeline-requires-specs",
            description="Figure writes require figure-specs.md",
            rule_type="figure_pipeline_gate",
            condition={
                "target_directory": "wave-5-visuals",
                "required_artifact": "figure-specs.md",
            },
            message="Cannot write figure files before creating figure specifications",
        )
        state = {
            "proposal_id": "test-uuid-fig",
            "current_wave": 5,
        }
        engine = EnforcementEngine(FakeRuleLoader([rule]), audit_logger)
        result = engine.evaluate(
            state,
            tool_name="Write",
            tool_context={
                "file_path": "artifacts/wave-5-visuals/figure-1.svg",
                "artifacts_present": ["figure-specs.md"],
            },
        )
        assert result.decision == Decision.ALLOW

    def test_style_profile_gate_allows_when_style_present(
        self, audit_logger: FakeAuditLogger
    ) -> None:
        """Style profile gate allows when style-profile.yaml is present."""
        rule = EnforcementRule(
            rule_id="figure-generation-requires-style",
            description="Figure writes require style profile",
            rule_type="style_profile_gate",
            condition={
                "target_directory": "wave-5-visuals",
                "required_artifact": "style-profile.yaml",
                "skip_state_key": "style_analysis_skipped",
            },
            message="Cannot generate figures before style analysis",
        )
        state = {
            "proposal_id": "test-uuid-style",
            "current_wave": 5,
        }
        engine = EnforcementEngine(FakeRuleLoader([rule]), audit_logger)
        result = engine.evaluate(
            state,
            tool_name="Write",
            tool_context={
                "file_path": "artifacts/wave-5-visuals/figure-1.svg",
                "artifacts_present": ["figure-specs.md", "style-profile.yaml"],
            },
        )
        assert result.decision == Decision.ALLOW


class TestEnforcementEngineWritingStyleGateRegistration:
    """Evaluator registration for writing style gate.

    Test Budget: 2 behaviors x 2 = 4 max unit tests
    Behaviors: writing_style_gate dispatches and blocks when prefs missing,
               writing_style_gate allows when prefs present.
    """

    def test_engine_has_eight_evaluators(
        self, audit_logger: FakeAuditLogger
    ) -> None:
        """Engine registers 8 evaluators including writing_style_gate."""
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        assert len(engine._evaluators) == 8
        assert "writing_style_gate" in engine._evaluators

    def test_writing_style_gate_blocks_when_prefs_missing(
        self, audit_logger: FakeAuditLogger
    ) -> None:
        """Engine dispatches writing_style_gate rule and blocks without quality-preferences.json."""
        rule = EnforcementRule(
            rule_id="drafting-requires-style-selection",
            description="Wave 4 drafting requires writing style selection",
            rule_type="writing_style_gate",
            condition={
                "target_directory": "wave-4-drafting",
                "required_global_artifact": "quality-preferences.json",
                "skip_state_field": "writing_style_selection_skipped",
            },
            message="Cannot write draft sections before writing style selection",
        )
        state = {
            "proposal_id": "test-uuid-wsg",
            "current_wave": 4,
        }
        engine = EnforcementEngine(FakeRuleLoader([rule]), audit_logger)
        result = engine.evaluate(
            state,
            tool_name="Write",
            tool_context={
                "file_path": "artifacts/wave-4-drafting/sections/technical-approach.md",
                "global_artifacts_present": [],
            },
        )
        assert result.decision == Decision.BLOCK
        assert "style" in result.messages[0].lower()

    def test_writing_style_gate_allows_when_prefs_present(
        self, audit_logger: FakeAuditLogger
    ) -> None:
        """Engine dispatches writing_style_gate rule and allows with quality-preferences.json."""
        rule = EnforcementRule(
            rule_id="drafting-requires-style-selection",
            description="Wave 4 drafting requires writing style selection",
            rule_type="writing_style_gate",
            condition={
                "target_directory": "wave-4-drafting",
                "required_global_artifact": "quality-preferences.json",
                "skip_state_field": "writing_style_selection_skipped",
            },
            message="Cannot write draft sections before writing style selection",
        )
        state = {
            "proposal_id": "test-uuid-wsg",
            "current_wave": 4,
        }
        engine = EnforcementEngine(FakeRuleLoader([rule]), audit_logger)
        result = engine.evaluate(
            state,
            tool_name="Write",
            tool_context={
                "file_path": "artifacts/wave-4-drafting/sections/technical-approach.md",
                "global_artifacts_present": ["quality-preferences.json"],
            },
        )
        assert result.decision == Decision.ALLOW
