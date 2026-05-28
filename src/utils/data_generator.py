"""
Generates all synthetic CSV datasets for ForkFund.

Run with:  python -m src.utils.data_generator
Outputs:
  data/synthetic/restaurants.csv
  data/synthetic/transactions.csv
  data/synthetic/pos_records.csv
  data/synthetic/accounting.csv
  data/synthetic/lenders.csv
"""

import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_RESTAURANTS = 175
OUTPUT_DIR = Path("data/synthetic")

rng = np.random.default_rng(SEED)
random.seed(SEED)

# ── Reference data ────────────────────────────────────────────────────────────

CUISINE_TYPES = [
    "Italian", "Asian", "Burger & Grill", "Pizza", "Sushi",
    "Mexican", "Middle Eastern", "French", "Bakery & Café", "Seafood",
    "Steakhouse", "Vegan", "Turkish", "Indian", "Fusion",
]

CITIES = [
    "Amsterdam", "Rotterdam", "Utrecht", "Den Haag", "Eindhoven",
    "Groningen", "Tilburg", "Almere", "Breda", "Nijmegen",
    "Haarlem", "Arnhem", "Zaandam", "Maastricht", "Leiden",
]

LEGAL_FORMS = ["BV", "VOF", "Eenmanszaak", "CV"]

SBI_CODES = ["56101", "56102", "56103", "56210", "56290"]

LENDER_NAMES = [
    "Rabobank Zakelijk",
    "ING Business Finance",
    "ABN AMRO Bedrijfskredieten",
    "Triodos Groenfonds",
    "New10",
    "Qredits Microfinanciering",
    "Funding Circle NL",
    "October NL",
    "NIBC Direct Zakelijk",
    "BNG Bank",
]

LOAN_PRODUCTS = [
    "Term loan",
    "Revolving credit",
    "Equipment finance",
    "Working capital",
]

TX_CATEGORIES = [
    "Food & Beverage Supply",
    "Staff Costs",
    "Rent",
    "Utilities",
    "Marketing",
    "Insurance",
    "Maintenance",
    "Tax",
    "Card Terminal Revenue",
    "Online Order Revenue",
    "Walk-in Revenue",
    "Loan Repayment",
    "Miscellaneous",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _random_date(start_year: int, end_year: int) -> date:
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))


def _kvk_number() -> str:
    return str(random.randint(10_000_000, 99_999_999))


# ── Restaurants ───────────────────────────────────────────────────────────────

def generate_restaurants() -> pd.DataFrame:
    """Generate the master restaurant table (one row per restaurant)."""
    rows = []
    for i in range(N_RESTAURANTS):
        reg_date = _random_date(2000, 2023)
        city = random.choice(CITIES)
        cuisine = random.choice(CUISINE_TYPES)
        seats = int(rng.integers(15, 180))
        rows.append(
            {
                "restaurant_id": f"R{i+1:04d}",
                "legal_name": f"{cuisine} {city} {i+1}",
                "cuisine_type": cuisine,
                "city": city,
                "legal_form": random.choice(LEGAL_FORMS),
                "kvk_number": _kvk_number(),
                "sbi_code": random.choice(SBI_CODES),
                "registration_date": reg_date.isoformat(),
                "is_active": random.random() > 0.05,
                "seats": seats,
                "loan_amount_requested_eur": int(
                    rng.choice(
                        [10_000, 25_000, 50_000, 75_000, 100_000,
                         150_000, 200_000, 250_000]
                    )
                ),
                "loan_purpose": random.choice(
                    ["Equipment purchase", "Renovation", "Working capital",
                     "Expansion", "Inventory"]
                ),
            }
        )
    return pd.DataFrame(rows)


# ── Bank transactions (PSD2) ──────────────────────────────────────────────────

def generate_transactions(restaurants: pd.DataFrame) -> pd.DataFrame:
    """Generate ~730 daily transaction records per restaurant (24 months)."""
    rows = []
    today = date.today()
    start = today - timedelta(days=730)

    for _, rest in restaurants.iterrows():
        r_id = rest["restaurant_id"]
        seats = rest["seats"]
        base_revenue = seats * rng.uniform(18, 55)   # daily revenue baseline

        current = start
        while current <= today:
            # Revenue transactions (2–4 per day)
            for _ in range(random.randint(2, 4)):
                rows.append(
                    {
                        "restaurant_id": r_id,
                        "date": current.isoformat(),
                        "amount_eur": round(
                            float(rng.normal(base_revenue / 3, base_revenue / 8)), 2
                        ),
                        "direction": "credit",
                        "category": random.choice(
                            ["Card Terminal Revenue",
                             "Online Order Revenue",
                             "Walk-in Revenue"]
                        ),
                        "description": "Daily revenue",
                    }
                )
            # Cost transactions (1–3 per day)
            for _ in range(random.randint(1, 3)):
                rows.append(
                    {
                        "restaurant_id": r_id,
                        "date": current.isoformat(),
                        "amount_eur": round(
                            float(rng.uniform(50, base_revenue * 0.6)), 2
                        ),
                        "direction": "debit",
                        "category": random.choice(
                            [c for c in TX_CATEGORIES
                             if c not in ("Card Terminal Revenue",
                                          "Online Order Revenue",
                                          "Walk-in Revenue")]
                        ),
                        "description": "Operating expense",
                    }
                )
            current += timedelta(days=1)

    return pd.DataFrame(rows)


# ── POS records ───────────────────────────────────────────────────────────────

def generate_pos_records(restaurants: pd.DataFrame) -> pd.DataFrame:
    """Generate daily POS summary records for 24 months."""
    rows = []
    today = date.today()
    start = today - timedelta(days=730)

    for _, rest in restaurants.iterrows():
        r_id = rest["restaurant_id"]
        seats = rest["seats"]
        base_covers = int(seats * rng.uniform(0.4, 1.2))
        avg_spend = float(rng.uniform(14, 55))

        current = start
        while current <= today:
            covers = max(0, int(rng.normal(base_covers, base_covers * 0.2)))
            gross = round(covers * avg_spend * rng.uniform(0.95, 1.05), 2)
            net = round(gross * rng.uniform(0.82, 0.92), 2)
            rows.append(
                {
                    "restaurant_id": r_id,
                    "date": current.isoformat(),
                    "covers": covers,
                    "gross_revenue_eur": gross,
                    "net_revenue_eur": net,
                    "avg_spend_eur": round(avg_spend, 2),
                }
            )
            current += timedelta(days=1)

    return pd.DataFrame(rows)


# ── Accounting / P&L ─────────────────────────────────────────────────────────

def generate_accounting(restaurants: pd.DataFrame) -> pd.DataFrame:
    """Generate 3 years of annual P&L and balance-sheet rows per restaurant."""
    rows = []
    current_year = date.today().year

    for _, rest in restaurants.iterrows():
        r_id = rest["restaurant_id"]
        seats = rest["seats"]
        base_revenue = seats * rng.uniform(200_000 / 80, 500_000 / 80)

        for yr in range(current_year - 3, current_year):
            revenue = round(float(base_revenue * rng.uniform(0.85, 1.15)), 2)
            cost_ratio = float(rng.uniform(0.55, 0.80))
            costs = round(revenue * cost_ratio, 2)
            ebitda = round(revenue - costs, 2)
            net_profit = round(ebitda * rng.uniform(0.5, 0.9), 2)
            total_debt = round(float(rng.uniform(0, revenue * 0.6)), 2)
            total_assets = round(float(rng.uniform(revenue * 0.3, revenue * 1.2)), 2)
            rows.append(
                {
                    "restaurant_id": r_id,
                    "year": yr,
                    "total_revenue_eur": revenue,
                    "total_costs_eur": costs,
                    "ebitda_eur": ebitda,
                    "net_profit_eur": net_profit,
                    "total_debt_eur": total_debt,
                    "total_assets_eur": total_assets,
                }
            )

    return pd.DataFrame(rows)


# ── Lenders ───────────────────────────────────────────────────────────────────

def generate_lenders() -> pd.DataFrame:
    """Generate a fictional lender reference table."""
    rows = []
    for i, name in enumerate(LENDER_NAMES):
        min_score = int(rng.integers(30, 65))
        rows.append(
            {
                "lender_id": f"L{i+1:02d}",
                "name": name,
                "min_score": min_score,
                "max_loan_eur": int(
                    rng.choice([50_000, 100_000, 250_000, 500_000, 1_000_000])
                ),
                "min_loan_eur": int(rng.choice([5_000, 10_000, 25_000])),
                "interest_rate_pct": round(float(rng.uniform(3.5, 12.0)), 2),
                "max_term_months": int(rng.choice([12, 24, 36, 60, 84])),
                "supported_purposes": "|".join(
                    random.sample(LOAN_PRODUCTS, k=random.randint(2, 4))
                ),
                "focus": random.choice(
                    ["All restaurants", "Sustainable only",
                     "SME specialist", "Micro-finance", "Growth-stage"]
                ),
            }
        )
    return pd.DataFrame(rows)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating restaurants…")
    restaurants = generate_restaurants()
    restaurants.to_csv(OUTPUT_DIR / "restaurants.csv", index=False)
    print(f"  {len(restaurants)} restaurants → restaurants.csv")

    print("Generating transactions…")
    transactions = generate_transactions(restaurants)
    transactions.to_csv(OUTPUT_DIR / "transactions.csv", index=False)
    print(f"  {len(transactions):,} rows → transactions.csv")

    print("Generating POS records…")
    pos = generate_pos_records(restaurants)
    pos.to_csv(OUTPUT_DIR / "pos_records.csv", index=False)
    print(f"  {len(pos):,} rows → pos_records.csv")

    print("Generating accounting data…")
    accounting = generate_accounting(restaurants)
    accounting.to_csv(OUTPUT_DIR / "accounting.csv", index=False)
    print(f"  {len(accounting):,} rows → accounting.csv")

    print("Generating lenders…")
    lenders = generate_lenders()
    lenders.to_csv(OUTPUT_DIR / "lenders.csv", index=False)
    print(f"  {len(lenders)} lenders → lenders.csv")

    print("Done.")


if __name__ == "__main__":
    main()
