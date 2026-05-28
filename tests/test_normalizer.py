"""Tests for src/standardization/normalizer.py."""

import pandas as pd
import pytest


def _sample_transactions():
    return pd.DataFrame({
        "restaurant_id": ["R0001", "R0001"],
        "date": ["2024-01-01", "2024-01-02"],
        "amount_eur": [100.0, 50.0],
        "direction": ["Credit", "debit"],
        "category": ["Revenue", "Costs"],
        "description": ["Sale", "Expense"],
    })


def _sample_pos():
    return pd.DataFrame({
        "restaurant_id": ["R0001"],
        "date": ["2024-01-01"],
        "covers": [30],
        "gross_revenue_eur": [600.0],
        "net_revenue_eur": [510.0],
        "avg_spend_eur": [20.0],
    })


def _sample_accounting():
    return pd.DataFrame({
        "restaurant_id": ["R0001"],
        "year": [2023],
        "total_revenue_eur": [200000.0],
        "total_costs_eur": [150000.0],
        "ebitda_eur": [50000.0],
        "net_profit_eur": [30000.0],
        "total_debt_eur": [40000.0],
        "total_assets_eur": [120000.0],
    })


def _sample_kvk():
    return pd.Series({
        "restaurant_id": "R0001",
        "legal_name": "Test Restaurant BV",
        "cuisine_type": "Italian",
        "city": "Amsterdam",
        "legal_form": "BV",
        "kvk_number": "12345678",
        "sbi_code": "56101",
        "registration_date": "2015-06-01",
        "is_active": True,
        "seats": 50,
        "loan_amount_requested_eur": 75000.0,
        "loan_purpose": "Renovation",
    })


def test_normalize_transactions_columns():
    from src.standardization.normalizer import normalize_transactions
    result = normalize_transactions(_sample_transactions())
    expected = {"restaurant_id", "date", "amount_eur", "direction", "category", "description"}
    assert expected.issubset(result.columns)


def test_normalize_transactions_direction_lowercased():
    from src.standardization.normalizer import normalize_transactions
    result = normalize_transactions(_sample_transactions())
    assert all(d == d.lower() for d in result["direction"])


def test_normalize_pos_columns():
    from src.standardization.normalizer import normalize_pos
    result = normalize_pos(_sample_pos())
    expected = {"restaurant_id", "date", "covers", "gross_revenue_eur",
                "net_revenue_eur", "avg_spend_eur"}
    assert expected.issubset(result.columns)


def test_normalize_accounting_columns():
    from src.standardization.normalizer import normalize_accounting
    result = normalize_accounting(_sample_accounting())
    expected = {"restaurant_id", "year", "total_revenue_eur", "ebitda_eur"}
    assert expected.issubset(result.columns)


def test_normalize_kvk_returns_dict():
    from src.standardization.normalizer import normalize_kvk
    result = normalize_kvk(_sample_kvk())
    assert isinstance(result, dict)
    assert result["kvk_number"] == "12345678"
    assert result["is_active"] is True
    assert isinstance(result["seats"], int)
