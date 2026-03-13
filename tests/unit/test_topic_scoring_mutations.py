"""Targeted mutation-killing tests for TopicScoringService.

Comprehensive tests covering all scoring dimensions, thresholds,
disqualifiers, and edge cases.
"""

from __future__ import annotations

from typing import Any

import pytest

from pes.domain.topic_scoring import (
    CLEARANCE_LEVELS,
    THRESHOLD_EVALUATE,
    THRESHOLD_GO,
    WEIGHT_CERT,
    WEIGHT_ELIG,
    WEIGHT_PP,
    WEIGHT_SME,
    WEIGHT_STTR,
    ScoredTopic,
    TopicScoringService,
)


def _topic(**kw: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "topic_id": "AF263-042",
        "topic_code": "AF263-042",
        "title": "Compact Directed Energy for C-UAS",
        "program": "SBIR",
        "phase": "I",
        "agency": "Air Force",
        "requires_clearance": "secret",
    }
    defaults.update(kw)
    return defaults


def _full_profile(**kw: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "company_name": "Radiant Defense Systems",
        "capabilities": ["directed energy", "RF power systems", "thermal management"],
        "certifications": {
            "sam_gov": {"active": True, "cage_code": "7X2K9"},
            "security_clearance": "secret",
            "itar_registered": True,
        },
        "employee_count": 15,
        "key_personnel": [
            {"name": "Dr. Elena Vasquez", "expertise": ["directed energy"]},
            {"name": "Marcus Chen", "expertise": ["RF power systems"]},
        ],
        "past_performance": [
            {"agency": "Air Force", "topic_area": "Compact Directed Energy", "outcome": "awarded"},
        ],
        "research_institution_partners": ["Georgia Tech Research Institute"],
    }
    defaults.update(kw)
    return defaults


class TestWeightConstants:
    """Kill mutants on weight constant values."""

    def test_weights_sum_to_one(self) -> None:
        total = WEIGHT_SME + WEIGHT_PP + WEIGHT_CERT + WEIGHT_ELIG + WEIGHT_STTR
        assert abs(total - 1.0) < 0.001

    def test_individual_weights(self) -> None:
        assert WEIGHT_SME == 0.35
        assert WEIGHT_PP == 0.25
        assert WEIGHT_CERT == 0.15
        assert WEIGHT_ELIG == 0.15
        assert WEIGHT_STTR == 0.10

    def test_thresholds(self) -> None:
        assert THRESHOLD_GO == 0.60
        assert THRESHOLD_EVALUATE == 0.30

    def test_clearance_levels(self) -> None:
        assert CLEARANCE_LEVELS["none"] == 0
        assert CLEARANCE_LEVELS["confidential"] == 1
        assert CLEARANCE_LEVELS["secret"] == 2
        assert CLEARANCE_LEVELS["top_secret"] == 3


class TestScoredTopicDefaults:
    """Kill mutants on ScoredTopic dataclass defaults."""

    def test_defaults(self) -> None:
        st = ScoredTopic(topic_id="X", composite_score=0.5,
                         dimensions={}, recommendation="GO")
        assert st.disqualifiers == []
        assert st.warnings == []
        assert st.key_personnel_match == []


class TestApplyRecommendation:
    """Kill mutants on threshold logic."""

    def test_go_at_exact_threshold(self) -> None:
        svc = TopicScoringService()
        assert svc.apply_recommendation(0.60) == "GO"

    def test_go_above_threshold(self) -> None:
        svc = TopicScoringService()
        assert svc.apply_recommendation(0.85) == "GO"

    def test_evaluate_at_exact_threshold(self) -> None:
        svc = TopicScoringService()
        assert svc.apply_recommendation(0.30) == "EVALUATE"

    def test_evaluate_between_thresholds(self) -> None:
        svc = TopicScoringService()
        assert svc.apply_recommendation(0.45) == "EVALUATE"

    def test_nogo_below_evaluate(self) -> None:
        svc = TopicScoringService()
        assert svc.apply_recommendation(0.29) == "NO-GO"

    def test_nogo_at_zero(self) -> None:
        svc = TopicScoringService()
        assert svc.apply_recommendation(0.0) == "NO-GO"

    def test_just_below_go(self) -> None:
        svc = TopicScoringService()
        assert svc.apply_recommendation(0.59) == "EVALUATE"

    def test_just_below_evaluate(self) -> None:
        svc = TopicScoringService()
        assert svc.apply_recommendation(0.299) == "NO-GO"


class TestDisqualifiers:
    """Kill mutants on disqualifier detection."""

    def test_ts_clearance_disqualifies_secret_holder(self) -> None:
        svc = TopicScoringService()
        topic = _topic(requires_clearance="top_secret")
        profile = _full_profile()  # secret clearance
        result = svc.score_topic(topic, profile)
        assert len(result.disqualifiers) == 1
        assert "TS" in result.disqualifiers[0]
        assert "Secret" in result.disqualifiers[0]
        assert result.recommendation == "NO-GO"

    def test_secret_clearance_ok_for_secret_topic(self) -> None:
        svc = TopicScoringService()
        topic = _topic(requires_clearance="secret")
        profile = _full_profile()
        result = svc.score_topic(topic, profile)
        assert len(result.disqualifiers) == 0

    def test_no_clearance_required(self) -> None:
        svc = TopicScoringService()
        topic = _topic(requires_clearance="none")
        profile = _full_profile()
        result = svc.score_topic(topic, profile)
        clearance_disq = [d for d in result.disqualifiers if "clearance" in d.lower()]
        assert clearance_disq == []

    def test_sttr_without_partner_disqualifies(self) -> None:
        svc = TopicScoringService()
        topic = _topic(program="STTR")
        profile = _full_profile(research_institution_partners=[])
        result = svc.score_topic(topic, profile)
        assert "No research institution partner" in result.disqualifiers
        assert result.recommendation == "NO-GO"

    def test_sttr_with_partner_no_disqualifier(self) -> None:
        svc = TopicScoringService()
        topic = _topic(program="STTR")
        profile = _full_profile()
        result = svc.score_topic(topic, profile)
        sttr_disq = [d for d in result.disqualifiers if "partner" in d.lower()]
        assert sttr_disq == []

    def test_sbir_program_no_partner_check(self) -> None:
        svc = TopicScoringService()
        topic = _topic(program="SBIR")
        profile = _full_profile(research_institution_partners=[])
        result = svc.score_topic(topic, profile)
        partner_disq = [d for d in result.disqualifiers if "partner" in d.lower()]
        assert partner_disq == []

    def test_clearance_disqualifier_message_format(self) -> None:
        svc = TopicScoringService()
        topic = _topic(requires_clearance="top_secret")
        profile = _full_profile(certifications={"security_clearance": "none"})
        result = svc.score_topic(topic, profile)
        assert result.disqualifiers[0] == "Requires TS clearance (profile: None)"

    def test_confidential_vs_none(self) -> None:
        svc = TopicScoringService()
        topic = _topic(requires_clearance="confidential")
        profile = _full_profile(certifications={"security_clearance": "none"})
        result = svc.score_topic(topic, profile)
        assert len(result.disqualifiers) >= 1
        assert any("clearance" in d.lower() for d in result.disqualifiers)


class TestSMEScoring:
    """Kill mutants on subject matter expertise scoring."""

    def test_full_phrase_match_scores_high(self) -> None:
        svc = TopicScoringService()
        topic = _topic(title="Directed Energy for Defense")
        profile = _full_profile(capabilities=["directed energy"])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["subject_matter"] >= 0.70

    def test_no_match_scores_zero(self) -> None:
        svc = TopicScoringService()
        topic = _topic(title="Marine Biology Research")
        profile = _full_profile(capabilities=["directed energy"])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["subject_matter"] == 0.0

    def test_empty_capabilities_scores_zero(self) -> None:
        svc = TopicScoringService()
        topic = _topic()
        profile = _full_profile(capabilities=[])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["subject_matter"] == 0.0

    def test_partial_word_overlap_scores_lower(self) -> None:
        svc = TopicScoringService()
        # "power" overlaps but "RF power systems" doesn't as full phrase
        topic = _topic(title="High Power Amplifier Design")
        profile = _full_profile(capabilities=["RF power systems"])
        result = svc.score_topic(topic, profile)
        sme = result.dimensions["subject_matter"]
        assert 0.0 < sme < 0.70  # Partial, not full match

    def test_multiple_capabilities_matched(self) -> None:
        svc = TopicScoringService()
        topic = _topic(title="Directed Energy Thermal Management System")
        profile = _full_profile(capabilities=["directed energy", "thermal management"])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["subject_matter"] >= 0.70


class TestPastPerformanceScoring:
    """Kill mutants on past performance scoring."""

    def test_same_agency_strong_domain_awarded(self) -> None:
        svc = TopicScoringService()
        topic = _topic(title="Compact Directed Energy for C-UAS", agency="Air Force")
        profile = _full_profile(past_performance=[
            {"agency": "Air Force", "topic_area": "Compact Directed Energy", "outcome": "awarded"},
        ])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["past_performance"] == 0.80

    def test_no_past_performance_scores_zero_with_warning(self) -> None:
        svc = TopicScoringService()
        topic = _topic()
        profile = _full_profile(past_performance=[])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["past_performance"] == 0.0
        assert any("past_performance" in w for w in result.warnings)

    def test_same_agency_no_domain_overlap(self) -> None:
        svc = TopicScoringService()
        topic = _topic(title="Compact Directed Energy", agency="Air Force")
        profile = _full_profile(past_performance=[
            {"agency": "Air Force", "topic_area": "Marine Biology", "outcome": "completed"},
        ])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["past_performance"] == 0.30

    def test_different_agency_strong_domain(self) -> None:
        svc = TopicScoringService()
        topic = _topic(title="Compact Directed Energy", agency="Navy")
        profile = _full_profile(past_performance=[
            {"agency": "Air Force", "topic_area": "Compact Directed Energy", "outcome": "awarded"},
        ])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["past_performance"] == 0.40

    def test_non_awarded_outcome_degrades(self) -> None:
        svc = TopicScoringService()
        topic = _topic(title="Compact Directed Energy", agency="Air Force")
        profile = _full_profile(past_performance=[
            {"agency": "Air Force", "topic_area": "Compact Directed Energy", "outcome": "pending"},
        ])
        result = svc.score_topic(topic, profile)
        # 0.80 * 0.7 = 0.56
        assert result.dimensions["past_performance"] == 0.56


class TestCertificationsScoring:
    """Kill mutants on certifications scoring."""

    def test_active_sam_scores_one(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(_topic(), _full_profile())
        assert result.dimensions["certifications"] == 1.0

    def test_no_certs_scores_zero(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(_topic(), _full_profile(certifications={}))
        assert result.dimensions["certifications"] == 0.0

    def test_inactive_sam_scores_zero(self) -> None:
        svc = TopicScoringService()
        profile = _full_profile(certifications={"sam_gov": {"active": False}})
        result = svc.score_topic(_topic(), profile)
        assert result.dimensions["certifications"] == 0.0

    def test_missing_sam_active_scores_zero(self) -> None:
        svc = TopicScoringService()
        profile = _full_profile(certifications={"sam_gov": {}})
        result = svc.score_topic(_topic(), profile)
        assert result.dimensions["certifications"] == 0.0


class TestEligibilityScoring:
    """Kill mutants on eligibility scoring."""

    def test_under_500_employees_phase_i_scores_one(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(
            _topic(phase="I"), _full_profile(employee_count=15),
        )
        assert result.dimensions["eligibility"] == 1.0

    def test_500_plus_employees_scores_zero(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(
            _topic(phase="I"), _full_profile(employee_count=500),
        )
        assert result.dimensions["eligibility"] == 0.0

    def test_499_employees_still_eligible(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(
            _topic(phase="I"), _full_profile(employee_count=499),
        )
        assert result.dimensions["eligibility"] == 1.0

    def test_phase_ii_scores_half(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(
            _topic(phase="II"), _full_profile(employee_count=15),
        )
        assert result.dimensions["eligibility"] == 0.5

    def test_zero_employees_still_eligible(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(
            _topic(phase="I"), _full_profile(employee_count=0),
        )
        assert result.dimensions["eligibility"] == 1.0


class TestSTTRScoring:
    """Kill mutants on STTR scoring."""

    def test_sbir_program_scores_one(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(_topic(program="SBIR"), _full_profile())
        assert result.dimensions["sttr"] == 1.0

    def test_sttr_with_partner_scores_one(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(
            _topic(program="STTR"),
            _full_profile(research_institution_partners=["MIT"]),
        )
        assert result.dimensions["sttr"] == 1.0

    def test_sttr_without_partner_scores_zero(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(
            _topic(program="STTR"),
            _full_profile(research_institution_partners=[]),
        )
        assert result.dimensions["sttr"] == 0.0


class TestCompositeScore:
    """Kill mutants on composite calculation and clamping."""

    def test_composite_is_weighted_sum(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(_topic(), _full_profile())
        # Manual calculation based on known dimensions
        dims = result.dimensions
        expected = (
            dims["subject_matter"] * 0.35
            + dims["past_performance"] * 0.25
            + dims["certifications"] * 0.15
            + dims["eligibility"] * 0.15
            + dims["sttr"] * 0.10
        )
        assert abs(result.composite_score - round(expected, 2)) <= 0.01

    def test_composite_clamped_at_zero(self) -> None:
        """Composite never goes negative."""
        svc = TopicScoringService()
        # All zeros: no caps, no past perf, no SAM
        profile = {"company_name": "X", "capabilities": []}
        result = svc.score_topic(_topic(), profile)
        assert result.composite_score >= 0.0

    def test_composite_clamped_at_one(self) -> None:
        """Composite never exceeds 1.0."""
        svc = TopicScoringService()
        result = svc.score_topic(_topic(), _full_profile())
        assert result.composite_score <= 1.0

    def test_composite_rounded_to_two_decimal(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(_topic(), _full_profile())
        # Check it's a proper 2-decimal round
        assert result.composite_score == round(result.composite_score, 2)

    def test_dimensions_rounded_to_two_decimal(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(_topic(), _full_profile())
        for k, v in result.dimensions.items():
            assert v == round(v, 2), f"{k} not rounded"


class TestKeyPersonnelMatch:
    """Kill mutants on key personnel matching."""

    def test_matches_personnel_by_expertise(self) -> None:
        svc = TopicScoringService()
        topic = _topic(title="Directed Energy Laser System")
        profile = _full_profile()
        result = svc.score_topic(topic, profile)
        assert "Dr. Elena Vasquez" in result.key_personnel_match

    def test_no_match_returns_empty(self) -> None:
        svc = TopicScoringService()
        topic = _topic(title="Marine Biology Research")
        profile = _full_profile()
        result = svc.score_topic(topic, profile)
        assert result.key_personnel_match == []

    def test_no_personnel_in_profile(self) -> None:
        svc = TopicScoringService()
        profile = _full_profile(key_personnel=[])
        result = svc.score_topic(_topic(), profile)
        assert result.key_personnel_match == []


class TestRecommendationLogic:
    """Kill mutants on recommendation decision tree."""

    def test_disqualifier_always_nogo(self) -> None:
        svc = TopicScoringService()
        topic = _topic(requires_clearance="top_secret")
        profile = _full_profile()
        result = svc.score_topic(topic, profile)
        assert result.recommendation == "NO-GO"

    def test_zero_eligibility_always_nogo(self) -> None:
        svc = TopicScoringService()
        profile = _full_profile(employee_count=500)
        result = svc.score_topic(_topic(), profile)
        assert result.recommendation == "NO-GO"

    def test_zero_certifications_always_nogo(self) -> None:
        svc = TopicScoringService()
        profile = _full_profile(certifications={})
        result = svc.score_topic(_topic(), profile)
        assert result.recommendation == "NO-GO"

    def test_no_past_performance_caps_at_evaluate(self) -> None:
        svc = TopicScoringService()
        profile = _full_profile(past_performance=[])
        # Even with high other dimensions, capped at EVALUATE
        result = svc.score_topic(_topic(), profile)
        assert result.recommendation in ("EVALUATE", "NO-GO")
        assert result.recommendation != "GO"

    def test_high_score_with_all_data_is_go(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(_topic(), _full_profile())
        # With strong matching profile, should be GO
        assert result.composite_score >= 0.60
        assert result.recommendation == "GO"


class TestScoreBatch:
    """Kill mutants on batch scoring and sorting."""

    def test_batch_returns_sorted_descending(self) -> None:
        svc = TopicScoringService()
        topics = [
            _topic(topic_id="A", title="Marine Biology"),
            _topic(topic_id="B", title="Directed Energy System"),
        ]
        results = svc.score_batch(topics, _full_profile())
        assert len(results) == 2
        assert results[0].composite_score >= results[1].composite_score

    def test_batch_empty_returns_empty(self) -> None:
        svc = TopicScoringService()
        results = svc.score_batch([], _full_profile())
        assert results == []

    def test_batch_single_returns_single(self) -> None:
        svc = TopicScoringService()
        results = svc.score_batch([_topic()], _full_profile())
        assert len(results) == 1


class TestTopicIdExtraction:
    """Kill mutants on topic_id extraction from topic dict."""

    def test_topic_id_from_dict(self) -> None:
        svc = TopicScoringService()
        result = svc.score_topic(_topic(topic_id="AF263-042"), _full_profile())
        assert result.topic_id == "AF263-042"

    def test_missing_topic_id_defaults_empty(self) -> None:
        svc = TopicScoringService()
        topic = {"title": "Test", "program": "SBIR", "phase": "I"}
        result = svc.score_topic(topic, _full_profile())
        assert result.topic_id == ""


class TestSMEScoringExactValues:
    """Kill mutants on exact numeric constants in _score_sme."""

    def test_single_full_match_one_capability(self) -> None:
        """1 full match / 1 capability = ratio 1.0 -> min(0.70+1.0, 1.0) = 1.0"""
        svc = TopicScoringService()
        topic = _topic(title="directed energy systems")
        profile = _full_profile(capabilities=["directed energy"])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["subject_matter"] == 1.0

    def test_single_full_match_two_capabilities(self) -> None:
        """1 full match / 2 capabilities = ratio 0.5 -> min(0.70+0.5, 1.0) = 1.0"""
        svc = TopicScoringService()
        topic = _topic(title="directed energy systems")
        profile = _full_profile(capabilities=["directed energy", "quantum computing"])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["subject_matter"] == 1.0

    def test_single_full_match_four_capabilities(self) -> None:
        """1/4 = ratio 0.25 -> 0.30 + 0.25*2.0 = 0.80"""
        svc = TopicScoringService()
        topic = _topic(title="directed energy systems")
        profile = _full_profile(capabilities=["directed energy", "quantum", "bio", "nano"])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["subject_matter"] == 0.80

    def test_partial_word_overlap_exact_score(self) -> None:
        """1 word overlap / 3 cap words = 0.3 * 1/3 ≈ 0.0999 -> ratio < 0.1
        -> ratio * 3.0 ≈ 0.30 (floating point: 0.3*1/3 < 0.1)"""
        svc = TopicScoringService()
        # "power" is in title, cap has 3 words, overlap = 1 word
        topic = _topic(title="high power system")
        profile = _full_profile(capabilities=["rf power systems"])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["subject_matter"] == 0.30

    def test_very_small_ratio_uses_3x_multiplier(self) -> None:
        """Small ratio < 0.1: uses ratio * 3.0"""
        svc = TopicScoringService()
        # 1 word overlap / 3 cap words = 0.1 per cap; ratio = 0.1/10 = 0.01
        topic = _topic(title="high power system")
        caps = ["rf power systems"] + [f"unrelated{i}" for i in range(9)]
        profile = _full_profile(capabilities=caps)
        result = svc.score_topic(topic, profile)
        sme = result.dimensions["subject_matter"]
        assert 0.0 < sme < 0.30  # Below medium range

    def test_full_phrase_adds_1_0_not_0_3(self) -> None:
        """Full phrase match adds 1.0, not 0.3 (partial word coefficient)."""
        svc = TopicScoringService()
        topic = _topic(title="directed energy")
        # With 1 cap, full match ratio = 1.0 -> min(0.70+1.0, 1.0) = 1.0
        profile_full = _full_profile(capabilities=["directed energy"])
        result = svc.score_topic(topic, profile_full)
        assert result.dimensions["subject_matter"] == 1.0


class TestPastPerformanceBoundaries:
    """Kill mutants on exact boundary conditions in _score_past_performance."""

    def test_domain_overlap_exactly_50_pct_is_strong(self) -> None:
        """50% overlap should trigger strong match (>= 0.5)."""
        svc = TopicScoringService()
        # title: "compact energy" -> words: {"compact", "energy"}
        # area: "compact directed energy systems" -> 4 words; overlap: {"compact", "energy"} -> 2/4 = 0.5
        topic = _topic(title="compact energy", agency="Air Force")
        profile = _full_profile(past_performance=[
            {"agency": "Air Force", "topic_area": "compact directed energy systems", "outcome": "awarded"},
        ])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["past_performance"] == 0.80

    def test_same_agency_weak_domain_overlap_scores_0_50(self) -> None:
        """Same agency with domain_overlap > 0 but < 0.5 => 0.50."""
        svc = TopicScoringService()
        # title words: {"compact", "laser"}, area words: {"compact", "directed", "energy", "systems"}
        # overlap = {"compact"} -> 1/4 = 0.25 (< 0.5 but > 0)
        topic = _topic(title="compact laser", agency="Air Force")
        profile = _full_profile(past_performance=[
            {"agency": "Air Force", "topic_area": "compact directed energy systems", "outcome": "awarded"},
        ])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["past_performance"] == 0.50

    def test_outcome_won_is_positive(self) -> None:
        """'won' counts as positive outcome (factor 1.0)."""
        svc = TopicScoringService()
        topic = _topic(title="compact directed energy", agency="Air Force")
        profile = _full_profile(past_performance=[
            {"agency": "Air Force", "topic_area": "compact directed energy", "outcome": "won"},
        ])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["past_performance"] == 0.80

    def test_outcome_completed_is_positive(self) -> None:
        """'completed' counts as positive outcome (factor 1.0)."""
        svc = TopicScoringService()
        topic = _topic(title="compact directed energy", agency="Air Force")
        profile = _full_profile(past_performance=[
            {"agency": "Air Force", "topic_area": "compact directed energy", "outcome": "completed"},
        ])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["past_performance"] == 0.80

    def test_warning_message_exact(self) -> None:
        """Kill mutants on exact warning string."""
        svc = TopicScoringService()
        result = svc.score_topic(_topic(), _full_profile(past_performance=[]))
        assert "Profile incomplete: past_performance empty" in result.warnings

    def test_best_score_selects_highest(self) -> None:
        """Multiple past performances: selects highest score."""
        svc = TopicScoringService()
        topic = _topic(title="compact directed energy", agency="Air Force")
        profile = _full_profile(past_performance=[
            {"agency": "Navy", "topic_area": "Marine Biology", "outcome": "completed"},
            {"agency": "Air Force", "topic_area": "compact directed energy", "outcome": "awarded"},
        ])
        result = svc.score_topic(topic, profile)
        assert result.dimensions["past_performance"] == 0.80


class TestClearanceLabelFormatting:
    """Kill mutants on clearance label string formatting."""

    def test_secret_vs_confidential_label(self) -> None:
        svc = TopicScoringService()
        topic = _topic(requires_clearance="secret")
        profile = _full_profile(certifications={"security_clearance": "confidential"})
        result = svc.score_topic(topic, profile)
        assert result.disqualifiers[0] == "Requires Secret clearance (profile: Confidential)"

    def test_ts_label_abbreviation(self) -> None:
        """'top_secret' becomes 'TS' in the message."""
        svc = TopicScoringService()
        topic = _topic(requires_clearance="top_secret")
        profile = _full_profile(certifications={"security_clearance": "secret"})
        result = svc.score_topic(topic, profile)
        assert "Requires TS clearance" in result.disqualifiers[0]
        assert "(profile: Secret)" in result.disqualifiers[0]

    def test_zero_req_level_no_disqualifier(self) -> None:
        """req_level = 0 should never produce clearance disqualifier."""
        svc = TopicScoringService()
        topic = _topic(requires_clearance="none")
        profile = _full_profile(certifications={"security_clearance": "none"})
        result = svc.score_topic(topic, profile)
        clearance_disq = [d for d in result.disqualifiers if "clearance" in d.lower()]
        assert clearance_disq == []


class TestBatchSortVerification:
    """Kill mutants on reverse=True in score_batch sort."""

    def test_highest_score_is_first(self) -> None:
        svc = TopicScoringService()
        topics = [
            _topic(topic_id="LOW", title="Marine Biology Research"),
            _topic(topic_id="HIGH", title="Directed Energy Thermal Management"),
        ]
        results = svc.score_batch(topics, _full_profile())
        assert results[0].topic_id == "HIGH"
        assert results[1].topic_id == "LOW"
        assert results[0].composite_score > results[1].composite_score


class TestRecommendWithDataGaps:
    """Kill mutants on _recommend with profile gaps."""

    def test_no_pp_with_nonzero_composite_evaluates(self) -> None:
        """No past_performance + composite above EVALUATE threshold -> EVALUATE."""
        svc = TopicScoringService()
        topic = _topic(title="Marine Biology Research")
        profile = _full_profile(past_performance=[])
        result = svc.score_topic(topic, profile)
        # cert 1.0*0.15 + elig 1.0*0.15 + sttr 1.0*0.10 = 0.40 >= 0.30
        assert result.recommendation == "EVALUATE"
        assert result.composite_score >= THRESHOLD_EVALUATE

    def test_no_pp_above_evaluate_capped(self) -> None:
        """No past_performance + high composite -> EVALUATE (capped, not GO)."""
        svc = TopicScoringService()
        topic = _topic(title="Directed Energy Thermal Management")
        profile = _full_profile(past_performance=[])
        result = svc.score_topic(topic, profile)
        # Even with high SME, no past_performance caps at EVALUATE
        assert result.recommendation == "EVALUATE"

    def test_eligibility_zero_overrides_high_composite(self) -> None:
        """Eligibility = 0.0 always NO-GO regardless of composite."""
        svc = TopicScoringService()
        profile = _full_profile(employee_count=500)
        result = svc.score_topic(_topic(), profile)
        assert result.dimensions["eligibility"] == 0.0
        assert result.recommendation == "NO-GO"

    def test_certs_zero_overrides_high_composite(self) -> None:
        """Certifications = 0.0 always NO-GO regardless of composite."""
        svc = TopicScoringService()
        profile = _full_profile(certifications={})
        result = svc.score_topic(_topic(), profile)
        assert result.dimensions["certifications"] == 0.0
        assert result.recommendation == "NO-GO"


class TestStopWordsExcluded:
    """Kill mutants on stopword set in _score_past_performance."""

    def test_stopwords_excluded_from_title_matching(self) -> None:
        """Words like 'for', 'the' should not count as domain overlap."""
        svc = TopicScoringService()
        # Title: "for the a of" -> all stopwords, no meaningful words
        topic = _topic(title="for the a of in and or", agency="Air Force")
        profile = _full_profile(past_performance=[
            {"agency": "Air Force", "topic_area": "for the a of in and or", "outcome": "awarded"},
        ])
        result = svc.score_topic(topic, profile)
        # All words are stopwords -> area_words empty -> domain_overlap = 0/max(0,1) = 0
        # agency_match = True but domain_overlap = 0 -> falls to "same agency, no domain" = 0.30
        assert result.dimensions["past_performance"] == 0.30
