"""Tests for src/scoring/explainer.py."""

from src.scoring.engine import ScoreResult, WEIGHTS
from src.scoring.explainer import explain, DIMENSION_LABELS


def _make_result(composite: float, sub_scores: dict | None = None) -> ScoreResult:
    if sub_scores is None:
        sub_scores = {k: composite for k in WEIGHTS}
    from src.scoring.engine import _grade, _risk_band
    return ScoreResult(
        composite=composite,
        sub_scores=sub_scores,
        weights=dict(WEIGHTS),
        grade=_grade(composite),
        risk_band=_risk_band(composite),
        data_completeness=sub_scores.get("data_completeness", composite),
    )


# ── Structure ─────────────────────────────────────────────────────────────────

def test_explain_returns_expected_keys():
    result = explain(_make_result(65.0))
    assert "positive_drivers" in result
    assert "negative_drivers" in result
    assert "risk_flags" in result
    assert "dimension_notes" in result
    assert "summary" in result


def test_dimension_notes_covers_all_dimensions():
    result = explain(_make_result(65.0))
    for dim in WEIGHTS:
        assert dim in result["dimension_notes"], f"Missing note for {dim}"


def test_all_lists_are_lists():
    result = explain(_make_result(50.0))
    assert isinstance(result["positive_drivers"], list)
    assert isinstance(result["negative_drivers"], list)
    assert isinstance(result["risk_flags"], list)


# ── Driver classification ─────────────────────────────────────────────────────

def test_high_scores_produce_positive_drivers():
    sub_scores = {k: 85.0 for k in WEIGHTS}
    result = explain(_make_result(85.0, sub_scores))
    assert len(result["positive_drivers"]) > 0


def test_low_scores_produce_negative_drivers():
    sub_scores = {k: 40.0 for k in WEIGHTS}
    result = explain(_make_result(40.0, sub_scores))
    assert len(result["negative_drivers"]) > 0


def test_very_low_scores_produce_risk_flags():
    sub_scores = {k: 20.0 for k in WEIGHTS}
    result = explain(_make_result(20.0, sub_scores))
    assert len(result["risk_flags"]) > 0


def test_high_scores_produce_no_risk_flags():
    sub_scores = {k: 80.0 for k in WEIGHTS}
    result = explain(_make_result(80.0, sub_scores))
    assert result["risk_flags"] == []


def test_no_positive_driver_for_low_score():
    sub_scores = {k: 30.0 for k in WEIGHTS}
    result = explain(_make_result(30.0, sub_scores))
    assert result["positive_drivers"] == []


def test_no_negative_driver_for_high_score():
    sub_scores = {k: 90.0 for k in WEIGHTS}
    result = explain(_make_result(90.0, sub_scores))
    assert result["negative_drivers"] == []


# ── Mixed sub-scores ──────────────────────────────────────────────────────────

def test_mixed_scores_split_drivers():
    sub_scores = {k: 80.0 for k in WEIGHTS}
    sub_scores["cash_flow_strength"] = 20.0   # one bad dimension
    result = explain(_make_result(68.0, sub_scores))
    assert len(result["positive_drivers"]) > 0
    assert len(result["negative_drivers"]) > 0
    assert len(result["risk_flags"]) == 1


# ── Summary ───────────────────────────────────────────────────────────────────

def test_summary_is_non_empty_string():
    result = explain(_make_result(60.0))
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 20


def test_summary_contains_grade():
    sr = _make_result(72.0)
    result = explain(sr)
    assert sr.grade in result["summary"]


def test_summary_contains_score():
    sr = _make_result(55.0)
    result = explain(sr)
    assert "55" in result["summary"]


# ── Dimension labels ──────────────────────────────────────────────────────────

def test_all_dimensions_have_labels():
    for dim in WEIGHTS:
        assert dim in DIMENSION_LABELS
