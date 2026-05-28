"""Simulated POS (point-of-sale) connector."""

from pathlib import Path
import pandas as pd

_CSV = Path("data/synthetic/pos_records.csv")
_dtypes = {
    "restaurant_id": str,
    "covers": int,
    "gross_revenue_eur": float,
    "net_revenue_eur": float,
    "avg_spend_eur": float,
}


def load_pos_records(restaurant_id: str) -> pd.DataFrame:
    """Return synthetic POS daily revenue records for the given restaurant.

    Columns: date, covers, gross_revenue_eur, net_revenue_eur, avg_spend_eur
    """
    df = pd.read_csv(_CSV, dtype=_dtypes, parse_dates=["date"])
    return df[df["restaurant_id"] == restaurant_id].reset_index(drop=True)
