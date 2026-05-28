"""
Generates all synthetic CSV datasets for ForkFund.

Run with:  python -m src.utils.data_generator
Outputs:
  data/synthetic/restaurants.csv
  data/synthetic/transactions.csv
  data/synthetic/pos_records.csv
  data/synthetic/accounting.csv
  data/synthetic/lenders.csv

Scale targets (approximate):
  restaurants  ~120 rows
  transactions ~88k rows   (120 restaurants × 365 days × 2 tx/day)
  pos_records  ~44k rows   (120 restaurants × 365 days × 1 row/day)
  accounting   ~360 rows   (120 restaurants × 3 annual years)
  lenders      10 rows
"""

import math
import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_RESTAURANTS = 120
HISTORY_DAYS = 365          # 12 months for both transactions and POS
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

REVENUE_CATEGORIES = ["Card Terminal Revenue", "Online Order Revenue", "Walk-in Revenue"]

COST_CATEGORIES = [
    "Food & Beverage Supply", "Staff Costs", "Rent", "Utilities",
    "Marketing", "Insurance", "Maintenance", "Tax", "Loan Repayment", "Miscellaneous",
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
        # Registration from 1998 to 2023 — wider range produces more maturity spread
        reg_date = _random_date(1998, 2023)
        city = random.choice(CITIES)
        cuisine = random.choice(CUISINE_TYPES)
        seats = int(rng.integers(12, 160))
        rows.append({
            "restaurant_id": f"R{i+1:04d}",
            "legal_name": f"{cuisine} {city} {i+1}",
            "cuisine_type": cuisine,
            "city": city,
            "legal_form": random.choice(LEGAL_FORMS),
            "kvk_number": _kvk_number(),
            "sbi_code": random.choice(SBI_CODES),
            "registration_date": reg_date.isoformat(),
            "is_active": random.random() > 0.07,
            "seats": seats,
            "loan_amount_requested_eur": int(rng.choice(
                [10_000, 25_000, 50_000, 75_000, 100_000, 150_000, 200_000, 250_000]
            )),
            "loan_purpose": random.choice([
                "Equipment purchase", "Renovation", "Working capital",
                "Expansion", "Inventory",
            ]),
        })
    return pd.DataFrame(rows)


# ── Bank transactions (PSD2) ──────────────────────────────────────────────────

def generate_transactions(restaurants: pd.DataFrame) -> pd.DataFrame:
    """Generate exactly 2 transaction rows per restaurant per day (1 credit + 1 debit).

    Total rows: N_RESTAURANTS × HISTORY_DAYS × 2 ≈ 87,600.

    Debit amounts span a wider range (up to 85% of daily revenue) so that
    net cash-flow margin varies meaningfully across restaurants and produces
    spread in the cash_flow_strength sub-score.
    """
    rows = []
    today = date.today()
    start = today - timedelta(days=HISTORY_DAYS)

    for _, rest in restaurants.iterrows():
        r_id = rest["restaurant_id"]
        seats = rest["seats"]
        daily_revenue = seats * float(rng.uniform(7, 18))   # €/seat/day

        # Cost pressure 0.28–0.92: wide range ensures cash_flow_strength spans
        # from ~27 (high-cost operator) to 100 (low-cost operator).
        cost_pressure = float(rng.uniform(0.28, 0.92))

        current = start
        while current <= today:
            credit = max(0.0, round(float(rng.normal(daily_revenue, daily_revenue * 0.12)), 2))
            debit = max(0.0, round(float(rng.normal(
                daily_revenue * cost_pressure,
                daily_revenue * cost_pressure * 0.15,
            )), 2))
            rows.append({
                "restaurant_id": r_id,
                "date": current.isoformat(),
                "amount_eur": credit,
                "direction": "credit",
                "category": random.choice(REVENUE_CATEGORIES),
                "description": "Daily revenue",
            })
            rows.append({
                "restaurant_id": r_id,
                "date": current.isoformat(),
                "amount_eur": debit,
                "direction": "debit",
                "category": random.choice(COST_CATEGORIES),
                "description": "Operating expense",
            })
            current += timedelta(days=1)

    return pd.DataFrame(rows)


# ── POS records ───────────────────────────────────────────────────────────────

def generate_pos_records(restaurants: pd.DataFrame) -> pd.DataFrame:
    """Generate one daily POS summary row per restaurant per day.

    Total rows: N_RESTAURANTS × HISTORY_DAYS ≈ 43,800.

    Cover variance is set at ±35% (up from ±20%) so that monthly revenue
    aggregates have more spread, producing a wider range of revenue_stability scores.
    """
    rows = []
    today = date.today()
    start = today - timedelta(days=HISTORY_DAYS)

    for _, rest in restaurants.iterrows():
        r_id = rest["restaurant_id"]
        seats = rest["seats"]
        base_covers = int(seats * float(rng.uniform(0.35, 1.25)))
        avg_spend = float(rng.uniform(12, 55))

        # Seasonal amplitude 0.0–0.85 per restaurant.
        # 0 = year-round stable (high revenue_stability score).
        # 0.85 = peak season is 85% above trough (low revenue_stability score).
        # Peak month varies: summer terraces peak in July, bakeries in December, etc.
        seasonal_amp = float(rng.uniform(0.0, 0.85))
        peak_month = int(rng.integers(1, 13))

        current = start
        while current <= today:
            seasonal_factor = 1.0 + seasonal_amp * math.sin(
                2 * math.pi * (current.month - peak_month) / 12
            )
            covers = max(0, int(rng.normal(base_covers * seasonal_factor, base_covers * 0.30)))
            gross = round(covers * avg_spend * float(rng.uniform(0.94, 1.06)), 2)
            net = round(gross * float(rng.uniform(0.80, 0.93)), 2)
            rows.append({
                "restaurant_id": r_id,
                "date": current.isoformat(),
                "covers": covers,
                "gross_revenue_eur": gross,
                "net_revenue_eur": net,
                "avg_spend_eur": round(avg_spend, 2),
            })
            current += timedelta(days=1)

    return pd.DataFrame(rows)


# ── Accounting / P&L ─────────────────────────────────────────────────────────

def generate_accounting(restaurants: pd.DataFrame) -> pd.DataFrame:
    """Generate 3 years of annual P&L and balance-sheet rows per restaurant.

    Distributions are widened to produce genuine low / medium / high risk spread:
      cost_ratio  0.48–0.92  → cost_structure scores span 0–92,
                                repayment_capacity scores span ~13–100
      debt_ratio  0.00–0.75  → debt_burden scores span 25–100
    """
    rows = []
    current_year = date.today().year

    for _, rest in restaurants.iterrows():
        r_id = rest["restaurant_id"]
        seats = rest["seats"]
        # Annual revenue base: €2,500–€6,000 per seat per year
        base_revenue = seats * float(rng.uniform(2_500, 6_000))

        for yr in range(current_year - 3, current_year):
            revenue = round(float(base_revenue * rng.uniform(0.82, 1.18)), 2)
            # 40% of restaurants are high-cost operators (cost_ratio 0.76–0.95).
            # 60% are healthy-to-moderate (cost_ratio 0.48–0.78).
            # This bimodal split reflects the real hospitality market.
            if rng.random() < 0.40:
                cost_ratio = float(rng.uniform(0.76, 0.95))
            else:
                cost_ratio = float(rng.uniform(0.48, 0.78))
            costs = round(revenue * cost_ratio, 2)
            ebitda = round(revenue - costs, 2)
            net_profit = round(ebitda * float(rng.uniform(0.45, 0.90)), 2)
            total_debt = round(float(rng.uniform(0, revenue * 0.75)), 2)
            total_assets = round(float(rng.uniform(revenue * 0.25, revenue * 1.20)), 2)
            rows.append({
                "restaurant_id": r_id,
                "year": yr,
                "total_revenue_eur": revenue,
                "total_costs_eur": costs,
                "ebitda_eur": ebitda,
                "net_profit_eur": net_profit,
                "total_debt_eur": total_debt,
                "total_assets_eur": total_assets,
            })

    return pd.DataFrame(rows)


# ── Lenders ───────────────────────────────────────────────────────────────────

def generate_lenders() -> pd.DataFrame:
    """Generate a fictional lender reference table."""
    rows = []
    for i, name in enumerate(LENDER_NAMES):
        min_score = int(rng.integers(30, 65))
        rows.append({
            "lender_id": f"L{i+1:02d}",
            "name": name,
            "min_score": min_score,
            "max_loan_eur": int(rng.choice([50_000, 100_000, 250_000, 500_000, 1_000_000])),
            "min_loan_eur": int(rng.choice([5_000, 10_000, 25_000])),
            "interest_rate_pct": round(float(rng.uniform(3.5, 12.0)), 2),
            "max_term_months": int(rng.choice([12, 24, 36, 60, 84])),
            "supported_purposes": "|".join(
                random.sample(LOAN_PRODUCTS, k=random.randint(2, 4))
            ),
            "focus": random.choice([
                "All restaurants", "Sustainable only",
                "SME specialist", "Micro-finance", "Growth-stage",
            ]),
        })
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
