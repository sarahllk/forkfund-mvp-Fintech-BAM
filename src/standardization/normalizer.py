"""Maps raw connector DataFrames to the unified ForkFund schema."""

import pandas as pd


def normalize_transactions(raw: pd.DataFrame) -> pd.DataFrame:
    """Standardise PSD2 transaction data to the unified schema.

    Ensures correct dtypes and presence of all expected columns.
    """
    df = raw.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["amount_eur"] = df["amount_eur"].astype(float).abs()
    df["direction"] = df["direction"].str.lower().str.strip()
    return df[["restaurant_id", "date", "amount_eur", "direction", "category", "description"]]


def normalize_pos(raw: pd.DataFrame) -> pd.DataFrame:
    """Standardise POS records to the unified schema."""
    df = raw.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["covers"] = df["covers"].astype(int)
    for col in ("gross_revenue_eur", "net_revenue_eur", "avg_spend_eur"):
        df[col] = df[col].astype(float)
    return df[["restaurant_id", "date", "covers", "gross_revenue_eur",
               "net_revenue_eur", "avg_spend_eur"]]


def normalize_accounting(raw: pd.DataFrame) -> pd.DataFrame:
    """Standardise accounting data to the unified schema."""
    df = raw.copy()
    df["year"] = df["year"].astype(int)
    for col in ("total_revenue_eur", "total_costs_eur", "ebitda_eur",
                "net_profit_eur", "total_debt_eur", "total_assets_eur"):
        df[col] = df[col].astype(float)
    return df[["restaurant_id", "year", "total_revenue_eur", "total_costs_eur",
               "ebitda_eur", "net_profit_eur", "total_debt_eur", "total_assets_eur"]]


def normalize_kvk(raw: pd.Series) -> dict:
    """Standardise KvK record to the unified schema."""
    return {
        "restaurant_id": str(raw["restaurant_id"]),
        "legal_name": str(raw["legal_name"]),
        "cuisine_type": str(raw["cuisine_type"]),
        "city": str(raw["city"]),
        "legal_form": str(raw["legal_form"]),
        "kvk_number": str(raw["kvk_number"]),
        "sbi_code": str(raw["sbi_code"]),
        "registration_date": pd.to_datetime(raw["registration_date"]),
        "is_active": bool(raw["is_active"]),
        "seats": int(raw["seats"]),
        "loan_amount_requested_eur": float(raw["loan_amount_requested_eur"]),
        "loan_purpose": str(raw["loan_purpose"]),
    }
