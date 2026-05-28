"""Simulated KvK (Dutch Chamber of Commerce) connector."""

from pathlib import Path
import pandas as pd

_CSV = Path("data/synthetic/restaurants.csv")
_dtypes = {
    "restaurant_id": str,
    "legal_name": str,
    "cuisine_type": str,
    "city": str,
    "legal_form": str,
    "kvk_number": str,
    "sbi_code": str,
    "is_active": str,   # parsed manually below — CSV stores "True"/"False" strings
    "seats": int,
    "loan_amount_requested_eur": float,
    "loan_purpose": str,
}


def load_kvk(restaurant_id: str) -> pd.Series:
    """Return the synthetic KvK registration record for the given restaurant.

    Fields: kvk_number, legal_name, legal_form, registration_date,
            is_active, sbi_code, address_city
    """
    df = pd.read_csv(_CSV, dtype=_dtypes, parse_dates=["registration_date"])
    df["is_active"] = df["is_active"].map({"True": True, "False": False}).astype(bool)
    matches = df[df["restaurant_id"] == restaurant_id]
    if matches.empty:
        raise KeyError(f"No restaurant found with id '{restaurant_id}'")
    return matches.iloc[0]
