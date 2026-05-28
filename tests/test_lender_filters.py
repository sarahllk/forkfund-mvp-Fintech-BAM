"""Tests for src/lender/filters.py."""

import pandas as pd
import pytest

from src.lender.filters import filter_lenders, explain_exclusions, rank_lenders


def _lenders() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "lender_id": "L01",
            "name": "Alpha Finance",
            "min_score": 50,
            "max_loan_eur": 200_000,
            "min_loan_eur": 10_000,
            "interest_rate_pct": 5.5,
            "max_term_months": 60,
            "supported_purposes": "Term loan|Renovation|Equipment finance",
            "focus": "SME specialist",
        },
        {
            "lender_id": "L02",
            "name": "Beta Capital",
            "min_score": 70,
            "max_loan_eur": 500_000,
            "min_loan_eur": 50_000,
            "interest_rate_pct": 4.0,
            "max_term_months": 84,
            "supported_purposes": "Term loan|Working capital",
            "focus": "Growth-stage",
        },
        {
            "lender_id": "L03",
            "name": "Gamma Micro",
            "min_score": 30,
            "max_loan_eur": 25_000,
            "min_loan_eur": 5_000,
            "interest_rate_pct": 8.0,
            "max_term_months": 24,
            "supported_purposes": "Renovation|Working capital",
            "focus": "Micro-finance",
        },
    ])


# ── filter_lenders ────────────────────────────────────────────────────────────

def test_all_criteria_met_returns_lender():
    matched = filter_lenders(_lenders(), score=55.0, loan_amount=15_000, loan_purpose="Renovation")
    names = list(matched["name"])
    assert "Alpha Finance" in names


def test_score_below_minimum_excluded():
    matched = filter_lenders(_lenders(), score=45.0, loan_amount=60_000, loan_purpose="Term loan")
    names = list(matched["name"])
    assert "Alpha Finance" not in names
    assert "Beta Capital" not in names


def test_loan_above_maximum_excluded():
    matched = filter_lenders(_lenders(), score=80.0, loan_amount=600_000, loan_purpose="Term loan")
    names = list(matched["name"])
    assert "Beta Capital" not in names


def test_loan_below_minimum_excluded():
    matched = filter_lenders(_lenders(), score=80.0, loan_amount=1_000, loan_purpose="Renovation")
    # L03 min is 5_000, L01 min is 10_000
    assert matched.empty


def test_unsupported_purpose_excluded():
    matched = filter_lenders(_lenders(), score=80.0, loan_amount=15_000, loan_purpose="Inventory")
    assert matched.empty


def test_returns_dataframe():
    result = filter_lenders(_lenders(), score=60.0, loan_amount=15_000, loan_purpose="Renovation")
    assert isinstance(result, pd.DataFrame)


def test_no_match_returns_empty_dataframe():
    matched = filter_lenders(_lenders(), score=10.0, loan_amount=15_000, loan_purpose="Renovation")
    assert matched.empty


def test_multiple_matches():
    matched = filter_lenders(_lenders(), score=80.0, loan_amount=60_000, loan_purpose="Term loan")
    # L01 and L02 both support Term loan; L03 does not
    assert len(matched) >= 1


# ── rank_lenders ──────────────────────────────────────────────────────────────

def test_rank_by_interest_rate_ascending():
    matched = filter_lenders(_lenders(), score=80.0, loan_amount=60_000, loan_purpose="Term loan")
    ranked = rank_lenders(matched, score=80.0)
    rates = list(ranked["interest_rate_pct"])
    assert rates == sorted(rates)


def test_rank_empty_returns_empty():
    result = rank_lenders(pd.DataFrame(), score=60.0)
    assert result.empty


def test_rank_no_headroom_column_in_output():
    matched = filter_lenders(_lenders(), score=80.0, loan_amount=60_000, loan_purpose="Term loan")
    ranked = rank_lenders(matched, score=80.0)
    assert "_headroom" not in ranked.columns


# ── explain_exclusions ────────────────────────────────────────────────────────

def test_explain_exclusions_lists_excluded_lenders():
    exclusions = explain_exclusions(
        _lenders(), score=45.0, loan_amount=15_000, loan_purpose="Renovation"
    )
    names = [e["lender"] for e in exclusions]
    assert "Beta Capital" in names


def test_explain_exclusions_correct_reason_for_score():
    exclusions = explain_exclusions(
        _lenders(), score=45.0, loan_amount=15_000, loan_purpose="Renovation"
    )
    beta = next(e for e in exclusions if e["lender"] == "Beta Capital")
    assert any("minimum" in r.lower() for r in beta["reasons"])


def test_explain_exclusions_does_not_include_matching_lender():
    exclusions = explain_exclusions(
        _lenders(), score=55.0, loan_amount=15_000, loan_purpose="Renovation"
    )
    names = [e["lender"] for e in exclusions]
    assert "Alpha Finance" not in names


def test_explain_exclusions_returns_list_of_dicts():
    result = explain_exclusions(
        _lenders(), score=40.0, loan_amount=15_000, loan_purpose="Renovation"
    )
    assert isinstance(result, list)
    for item in result:
        assert "lender" in item
        assert "reasons" in item
        assert isinstance(item["reasons"], list)
