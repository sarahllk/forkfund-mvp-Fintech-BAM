"""Tests for src/scoring/engine.py."""

from datetime import date, timedelta

import pandas as pd
import pytest

from src.scoring.engine import (
    ScoreResult,
    WEIGHTS,
    _grade,
    _risk_band,
    _data_completeness,
    compute_score,
)
from src.utils.helpers import clamp


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_pos(n_months: int = 24, mean: float = 10_000, cv: float = 0.05) -> pd.DataFrame:
    """Synthetic POS records with controllable variability."""
    import numpy as np
    rng = np.random.default_rng(0)
    today = date.today()
    rows = []
    for i in range(n_months * 30):
        d = today - timedelta(days=n_months * 30 - i)
        rev = max(0, float(rng.normal(mean, mean * cv)))
        rows.append({
            "restaurant_id": "R_TEST",
            "date": pd.Timestamp(d),
            "covers": 30,
            "gross_revenue_eur": rev * 1.1,
            "net_revenue_eur": rev,
            "avg_spend_eur": 25.0,
        })
    return pd.DataFrame(rows)


def _make_accounting(revenue: float = 200_000, cost_ratio: float = 0.65,
                     debt_ratio: float = 0.3) -> pd.DataFrame:
    ebitda = revenue * (1 - cost_ratio) * 0.8
    return pd.DataFrame([{
        "restaurant_id": "R_TEST",
        "year": date.today().year - 1,
        "total_revenue_eur": revenue,
        "total_costs_eur": revenue * cost_ratio,
        "ebitda_eur": ebitda,
        "net_profit_eur": ebitda * 0.7,
        "total_debt_eur": revenue * debt_ratio,
        "total_assets_eur": revenue * 0.8,
    }])


def _make_transactions(credit_total: float = 200_000,
                       debit_total: float = 120_000) -> pd.DataFrame:
    today = date.today()
    rows = [
        {"restaurant_id": "R_TEST", "date": pd.Timestamp(today - timedelta(days=1)),
         "amount_eur": credit_total, "direction": "credit",
         "category": "Revenue", "description": ""},
        {"restaurant_id": "R_TEST", "date": pd.Timestamp(today - timedelta(days=1)),
         "amount_eur": debit_total, "direction": "debit",
         "category": "Costs", "description": ""},
    ]
    return pd.DataFrame(rows)


def _make_kvk(years_old: float = 5.0, is_active: bool = True) -> dict:
    reg_date = date.today() - timedelta(days=int(years_old * 365.25))
    return {
        "restaurant_id": "R_TEST",
        "legal_name": "Test Restaurant BV",
        "kvk_number": "12345678",
        "registration_date": reg_date,
        "is_active": is_active,
        "seats": 50,
        "loan_amount_requested_eur": 75_000.0,
        "loan_purpose": "Renovation",
    }


def _full_data(**overrides) -> dict:
    data = {
        "pos": _make_pos(),
        "transactions": _make_transactions(),
        "accounting": _make_accounting(),
        "kvk": _make_kvk(),
    }
    data.update(overrides)
    return data


# ── Weights ───────────────────────────────────────────────────────────────────

def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_weights_all_positive():
    assert all(v > 0 for v in WEIGHTS.values())


# ── Grade boundaries ──────────────────────────────────────────────────────────

def test_grade_boundaries():
    assert _grade(100) == "A"
    assert _grade(80) == "A"
    assert _grade(79) == "B"
    assert _grade(65) == "B"
    assert _grade(64) == "C"
    assert _grade(50) == "C"
    assert _grade(49) == "D"
    assert _grade(35) == "D"
    assert _grade(34) == "F"
    assert _grade(0) == "F"


def test_risk_band_boundaries():
    assert _risk_band(70) == "Low"
    assert _risk_band(69) == "Medium"
    assert _risk_band(50) == "Medium"
    assert _risk_band(49) == "High"  # corrected: <50 is High not Medium
    assert _risk_band(30) == "High"
    assert _risk_band(29) == "Very High"


# ── clamp ─────────────────────────────────────────────────────────────────────

def test_clamp_above():
    assert clamp(110) == 100.0


def test_clamp_below():
    assert clamp(-5) == 0.0


def test_clamp_within():
    assert clamp(55) == 55.0


# ── compute_score ─────────────────────────────────────────────────────────────

def test_compute_score_returns_score_result():
    result = compute_score(_full_data())
    assert isinstance(result, ScoreResult)


def test_composite_in_range():
    result = compute_score(_full_data())
    assert 0 <= result.composite <= 100


def test_all_sub_scores_in_range():
    result = compute_score(_full_data())
    for dim, score in result.sub_scores.items():
        assert 0 <= score <= 100, f"{dim} sub-score {score} out of range"


def test_grade_matches_composite():
    result = compute_score(_full_data())
    assert result.grade == _grade(result.composite)


def test_risk_band_matches_composite():
    result = compute_score(_full_data())
    assert result.risk_band == _risk_band(result.composite)


def test_compute_score_is_deterministic():
    data = _full_data()
    r1 = compute_score(data)
    r2 = compute_score(data)
    assert r1.composite == r2.composite
    assert r1.sub_scores == r2.sub_scores


def test_full_data_scores_above_empty():
    full = compute_score(_full_data())
    empty = compute_score({})
    assert full.composite > empty.composite


# ── Missing data handling ─────────────────────────────────────────────────────

def test_empty_data_returns_score_result():
    result = compute_score({})
    assert isinstance(result, ScoreResult)
    assert 0 <= result.composite <= 100


def test_empty_data_completeness_is_zero():
    result = compute_score({})
    assert result.sub_scores["data_completeness"] == 0.0


def test_full_data_completeness_is_100():
    result = compute_score(_full_data())
    assert result.sub_scores["data_completeness"] == 100.0


def test_missing_pos_reduces_completeness():
    result = compute_score(_full_data(pos=pd.DataFrame()))
    assert result.sub_scores["data_completeness"] == 75.0


def test_missing_accounting_neutral_sub_scores():
    """Debt burden, repayment capacity, and cost structure default to 50 when absent."""
    result = compute_score(_full_data(accounting=pd.DataFrame()))
    assert result.sub_scores["debt_burden"] == 50.0
    assert result.sub_scores["repayment_capacity"] == 50.0
    assert result.sub_scores["cost_structure"] == 50.0


# ── Sub-score sensitivity ─────────────────────────────────────────────────────

def test_high_debt_lowers_score():
    low_debt = compute_score(_full_data(accounting=_make_accounting(debt_ratio=0.1)))
    high_debt = compute_score(_full_data(accounting=_make_accounting(debt_ratio=0.9)))
    assert low_debt.sub_scores["debt_burden"] > high_debt.sub_scores["debt_burden"]


def test_high_cost_ratio_lowers_score():
    low_cost = compute_score(_full_data(accounting=_make_accounting(cost_ratio=0.50)))
    high_cost = compute_score(_full_data(accounting=_make_accounting(cost_ratio=0.82)))
    assert low_cost.sub_scores["cost_structure"] > high_cost.sub_scores["cost_structure"]


def test_older_business_higher_maturity():
    young = compute_score(_full_data(kvk=_make_kvk(years_old=0.5)))
    old = compute_score(_full_data(kvk=_make_kvk(years_old=12.0)))
    assert old.sub_scores["business_maturity"] > young.sub_scores["business_maturity"]


def test_inactive_kvk_penalises_maturity():
    active = compute_score(_full_data(kvk=_make_kvk(years_old=5, is_active=True)))
    inactive = compute_score(_full_data(kvk=_make_kvk(years_old=5, is_active=False)))
    assert active.sub_scores["business_maturity"] > inactive.sub_scores["business_maturity"]
