"""Tests for src/passport/generator.py."""

import json
from datetime import date, timedelta

import pandas as pd

from src.scoring.engine import ScoreResult, WEIGHTS, _grade, _risk_band
from src.passport.generator import CreditPassport, generate, to_json


def _score(composite: float = 70.0) -> ScoreResult:
    sub = {k: composite for k in WEIGHTS}
    return ScoreResult(
        composite=composite,
        sub_scores=sub,
        weights=dict(WEIGHTS),
        grade=_grade(composite),
        risk_band=_risk_band(composite),
        data_completeness=sub.get("data_completeness", composite),
    )


def _restaurant() -> dict:
    return {
        "restaurant_id": "R_TEST",
        "legal_name": "Test Restaurant BV",
        "cuisine_type": "Italian",
        "city": "Amsterdam",
        "legal_form": "BV",
        "kvk_number": "12345678",
        "registration_date": date(2015, 6, 1),
        "is_active": True,
        "seats": 50,
        "loan_amount_requested_eur": 75_000.0,
        "loan_purpose": "Renovation",
    }


def _accounting() -> pd.DataFrame:
    return pd.DataFrame([{
        "restaurant_id": "R_TEST",
        "year": date.today().year - 1,
        "total_revenue_eur": 200_000.0,
        "total_costs_eur": 130_000.0,
        "ebitda_eur": 50_000.0,
        "net_profit_eur": 35_000.0,
        "total_debt_eur": 40_000.0,
        "total_assets_eur": 160_000.0,
    }])


def _pos() -> pd.DataFrame:
    today = date.today()
    rows = [
        {
            "restaurant_id": "R_TEST",
            "date": pd.Timestamp(today - timedelta(days=i)),
            "covers": 30,
            "gross_revenue_eur": 600.0,
            "net_revenue_eur": 510.0,
            "avg_spend_eur": 20.0,
        }
        for i in range(365)
    ]
    return pd.DataFrame(rows)


def _explanations(flags: list | None = None) -> dict:
    return {
        "positive_drivers": ["Revenue is consistent."],
        "negative_drivers": [],
        "risk_flags": flags or [],
        "dimension_notes": {},
        "summary": "Overall score: 70/100.",
    }


# ── Type and structure ────────────────────────────────────────────────────────

def test_generate_returns_credit_passport():
    passport = generate(_restaurant(), _score(), _explanations(), _accounting(), _pos())
    assert isinstance(passport, CreditPassport)


def test_passport_restaurant_id():
    passport = generate(_restaurant(), _score(), _explanations(), _accounting(), _pos())
    assert passport.restaurant_id == "R_TEST"


def test_passport_legal_name():
    passport = generate(_restaurant(), _score(), _explanations(), _accounting(), _pos())
    assert passport.legal_name == "Test Restaurant BV"


def test_passport_generated_at_is_string():
    passport = generate(_restaurant(), _score(), _explanations(), _accounting(), _pos())
    assert isinstance(passport.generated_at, str)
    assert "T" in passport.generated_at   # ISO-8601 contains T


def test_passport_profile_keys():
    passport = generate(_restaurant(), _score(), _explanations(), _accounting(), _pos())
    expected = {"restaurant_id", "legal_name", "city", "kvk_number", "is_active", "seats"}
    assert expected.issubset(passport.profile.keys())


# ── Financial indicators ──────────────────────────────────────────────────────

def test_indicators_include_annual_revenue():
    passport = generate(_restaurant(), _score(), _explanations(), _accounting(), _pos())
    assert "annual_revenue_eur" in passport.financial_indicators
    assert passport.financial_indicators["annual_revenue_eur"] == 200_000.0


def test_indicators_include_ebitda_margin():
    passport = generate(_restaurant(), _score(), _explanations(), _accounting(), _pos())
    assert "ebitda_margin_pct" in passport.financial_indicators


def test_indicators_include_trailing_revenue():
    passport = generate(_restaurant(), _score(), _explanations(), _accounting(), _pos())
    assert "trailing_12m_revenue_eur" in passport.financial_indicators
    assert passport.financial_indicators["trailing_12m_revenue_eur"] > 0


def test_empty_accounting_no_revenue_key():
    passport = generate(
        _restaurant(), _score(), _explanations(), pd.DataFrame(), _pos()
    )
    assert "annual_revenue_eur" not in passport.financial_indicators


# ── Financing readiness ───────────────────────────────────────────────────────

def test_high_score_financing_ready():
    passport = generate(_restaurant(), _score(75.0), _explanations(), _accounting(), _pos())
    assert "Financing-ready" in passport.financing_readiness


def test_mid_score_conditionally_ready():
    passport = generate(_restaurant(), _score(58.0), _explanations(), _accounting(), _pos())
    assert "Conditionally" in passport.financing_readiness


def test_low_score_not_ready():
    passport = generate(_restaurant(), _score(28.0), _explanations(), _accounting(), _pos())
    assert "Not currently" in passport.financing_readiness


# ── Risk flags ────────────────────────────────────────────────────────────────

def test_risk_flags_propagated():
    flags = ["Revenue volatility is severe.", "EBITDA is near zero."]
    passport = generate(_restaurant(), _score(), _explanations(flags), _accounting(), _pos())
    assert passport.risk_flags == flags


def test_no_risk_flags_by_default():
    passport = generate(_restaurant(), _score(), _explanations(), _accounting(), _pos())
    assert passport.risk_flags == []


# ── JSON serialisation ────────────────────────────────────────────────────────

def test_to_json_is_valid_json():
    passport = generate(_restaurant(), _score(), _explanations(), _accounting(), _pos())
    json_str = to_json(passport)
    parsed = json.loads(json_str)
    assert isinstance(parsed, dict)


def test_to_json_contains_restaurant_id():
    passport = generate(_restaurant(), _score(), _explanations(), _accounting(), _pos())
    parsed = json.loads(to_json(passport))
    assert parsed["restaurant_id"] == "R_TEST"


def test_to_json_contains_composite_score():
    passport = generate(_restaurant(), _score(72.0), _explanations(), _accounting(), _pos())
    parsed = json.loads(to_json(passport))
    assert parsed["score_result"]["composite"] == 72.0
