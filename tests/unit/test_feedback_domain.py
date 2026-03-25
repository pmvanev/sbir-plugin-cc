"""Unit tests for the feedback domain model.

Test budget: 5 distinct behaviors x 2 = 10 max unit tests.
Behaviors:
  1. FeedbackType enum values
  2. QualityRatings accepts None and valid int 1-5 per field
  3. FeedbackSnapshot has all 14 required fields
  4. FeedbackEntry.to_dict() is json.dumps()-safe
  5. to_dict() round-trip preserves all fields
"""

import json

import pytest

from pes.domain.feedback import FeedbackEntry, FeedbackSnapshot, FeedbackType, QualityRatings


# ---------- Behavior 1: FeedbackType enum values ----------

def test_feedback_type_has_exactly_three_values():
    values = {m.value for m in FeedbackType}
    assert values == {"bug", "suggestion", "quality"}


# ---------- Behavior 2: QualityRatings field acceptance ----------

@pytest.mark.parametrize("pp,iq,wq,ts", [
    (None, None, None, None),
    (1, 1, 1, 1),
    (5, 5, 5, 5),
    (3, 2, 4, 1),
    (None, 3, None, 5),
])
def test_quality_ratings_accepts_none_and_1_to_5(pp, iq, wq, ts):
    ratings = QualityRatings(
        past_performance=pp,
        image_quality=iq,
        writing_quality=wq,
        topic_scoring=ts,
    )
    assert ratings.past_performance == pp
    assert ratings.image_quality == iq
    assert ratings.writing_quality == wq
    assert ratings.topic_scoring == ts


# ---------- Behavior 3: FeedbackSnapshot has all 14 fields ----------

def _make_snapshot(**overrides) -> FeedbackSnapshot:
    defaults = dict(
        plugin_version="abc1234",
        proposal_id="prop-001",
        topic_id="N00-001",
        topic_title="Advanced Radar",
        topic_agency="Navy",
        topic_deadline="2026-06-01",
        topic_phase="I",
        current_wave=3,
        completed_waves=[0, 1, 2],
        skipped_waves=[],
        rigor_profile="standard",
        company_name="Acme Defense",
        company_profile_age_days=7,
        finder_results_age_days=2,
        top_scored_topics=[{"topic_id": "N00-001", "composite_score": 85, "recommendation": "apply"}],
        generated_artifacts=["draft.md", "exec-summary.md"],
    )
    defaults.update(overrides)
    return FeedbackSnapshot(**defaults)


def test_feedback_snapshot_has_all_14_required_fields():
    snapshot = _make_snapshot()
    field_names = {
        "plugin_version", "proposal_id", "topic_id", "topic_title",
        "topic_agency", "topic_deadline", "topic_phase", "current_wave",
        "completed_waves", "skipped_waves", "rigor_profile", "company_name",
        "company_profile_age_days", "finder_results_age_days",
        "top_scored_topics", "generated_artifacts",
    }
    for name in field_names:
        assert hasattr(snapshot, name), f"Missing field: {name}"


def test_feedback_snapshot_list_fields_never_none():
    snapshot = _make_snapshot(completed_waves=[], skipped_waves=[], top_scored_topics=[], generated_artifacts=[])
    assert snapshot.completed_waves == []
    assert snapshot.skipped_waves == []
    assert snapshot.top_scored_topics == []
    assert snapshot.generated_artifacts == []


# ---------- Behavior 4: FeedbackEntry.to_dict() is json.dumps()-safe ----------

def _make_entry(
    feedback_id: str = "550e8400-e29b-41d4-a716-446655440000",
    timestamp: str = "2026-03-25T12:00:00Z",
    feedback_type: FeedbackType = FeedbackType.QUALITY,
) -> FeedbackEntry:
    ratings = QualityRatings(past_performance=4, image_quality=None, writing_quality=3, topic_scoring=5)
    snapshot = _make_snapshot()
    return FeedbackEntry(
        feedback_id=feedback_id,
        timestamp=timestamp,
        type=feedback_type,
        ratings=ratings,
        free_text="Great topic alignment.",
        context_snapshot=snapshot,
    )


def test_to_dict_is_json_serializable():
    entry = _make_entry()
    result = entry.to_dict()
    # Must not raise TypeError
    serialized = json.dumps(result)
    assert isinstance(serialized, str)


# ---------- Behavior 5: to_dict() round-trip preserves all fields ----------

def test_to_dict_round_trip_preserves_all_fields():
    entry = _make_entry()
    d = entry.to_dict()

    assert d["feedback_id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert d["timestamp"] == "2026-03-25T12:00:00Z"
    assert d["type"] == "quality"
    assert d["ratings"]["past_performance"] == 4
    assert d["ratings"]["image_quality"] is None
    assert d["ratings"]["writing_quality"] == 3
    assert d["ratings"]["topic_scoring"] == 5
    assert d["free_text"] == "Great topic alignment."

    snapshot_d = d["context_snapshot"]
    assert snapshot_d["plugin_version"] == "abc1234"
    assert snapshot_d["proposal_id"] == "prop-001"
    assert snapshot_d["completed_waves"] == [0, 1, 2]
    assert snapshot_d["skipped_waves"] == []
    assert snapshot_d["company_name"] == "Acme Defense"
    assert snapshot_d["generated_artifacts"] == ["draft.md", "exec-summary.md"]
