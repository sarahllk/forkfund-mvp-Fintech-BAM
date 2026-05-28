"""Simulated PSD2 / open-banking connector."""

from pathlib import Path
import pandas as pd

_CSV = Path("data/synthetic/transactions.csv")
_dtypes = {
    "restaurant_id": str,
    "amount_eur": float,
    "direction": str,
    "category": str,
    "description": str,
}


def load_transactions(restaurant_id: str) -> pd.DataFrame:
    """Return synthetic bank transactions for the given restaurant.

    Columns: date, amount_eur, direction (credit/debit), category, description
    """
    df = pd.read_csv(_CSV, dtype=_dtypes, parse_dates=["date"])
    return df[df["restaurant_id"] == restaurant_id].reset_index(drop=True)
