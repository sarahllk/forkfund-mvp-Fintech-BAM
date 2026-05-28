"""Tests for src/connectors/ — verifies output shape and dtypes."""

import pandas as pd
import pytest


def test_psd2_returns_dataframe():
    from src.connectors.psd2 import load_transactions
    df = load_transactions("R0001")
    assert isinstance(df, pd.DataFrame)
    assert {"date", "amount_eur", "direction", "category"}.issubset(df.columns)
    assert len(df) > 0


def test_psd2_direction_values():
    from src.connectors.psd2 import load_transactions
    df = load_transactions("R0001")
    assert set(df["direction"].unique()).issubset({"credit", "debit"})


def test_pos_returns_dataframe():
    from src.connectors.pos import load_pos_records
    df = load_pos_records("R0001")
    assert isinstance(df, pd.DataFrame)
    assert {"date", "covers", "gross_revenue_eur", "net_revenue_eur"}.issubset(df.columns)
    assert len(df) > 0


def test_accounting_returns_dataframe():
    from src.connectors.accounting import load_accounting
    df = load_accounting("R0001")
    assert isinstance(df, pd.DataFrame)
    assert "total_revenue_eur" in df.columns
    assert list(df["year"]) == sorted(df["year"])


def test_kvk_returns_series():
    from src.connectors.kvk import load_kvk
    record = load_kvk("R0001")
    assert isinstance(record, pd.Series)
    assert "kvk_number" in record.index
    assert record["is_active"] in (True, False)


def test_kvk_raises_for_unknown_id():
    from src.connectors.kvk import load_kvk
    with pytest.raises(KeyError):
        load_kvk("DOES_NOT_EXIST")
