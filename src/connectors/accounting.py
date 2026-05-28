"""Simulated accounting / P&L connector."""

from pathlib import Path
import pandas as pd

_CSV = Path("data/synthetic/accounting.csv")
_dtypes = {
    "restaurant_id": str,
    "year": int,
    "total_revenue_eur": float,
    "total_costs_eur": float,
    "ebitda_eur": float,
    "net_profit_eur": float,
    "total_debt_eur": float,
    "total_assets_eur": float,
}


def load_accounting(restaurant_id: str) -> pd.DataFrame:
    """Return synthetic annual P&L and balance-sheet rows for the given restaurant.

    Columns: year, total_revenue_eur, total_costs_eur, ebitda_eur,
             net_profit_eur, total_debt_eur, total_assets_eur
    """
    df = pd.read_csv(_CSV, dtype=_dtypes)
    return (
        df[df["restaurant_id"] == restaurant_id]
        .sort_values("year")
        .reset_index(drop=True)
    )
