"""Rules-based credit scoring engine — produces a 0–100 composite score.

Scores represent pre-underwriting decision support only. They do not constitute
a credit decision, probability of default, or automated underwriting determination.
"""

from dataclasses import dataclass, field
from datetime import date

import pandas as pd

from src.utils.helpers import clamp

WEIGHTS: dict[str, float] = {
    "revenue_stability":   0.20,
    "cash_flow_strength":  0.20,
    "debt_burden":         0.15,
    "repayment_capacity":  0.15,
    "cost_structure":      0.10,
    "business_maturity":   0.10,
    "data_completeness":   0.10,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"


@dataclass
class ScoreResult:
    composite: float                          # 0–100
    sub_scores: dict = field(default_factory=dict)   # {dimension: 0–100}
    weights: dict = field(default_factory=dict)
    grade: str = ""                           # A / B / C / D / F
    risk_band: str = ""                       # Low / Medium / High / Very High
    data_completeness: float = 0.0


def compute_score(data: dict) -> ScoreResult:
    """Compute a composite pre-underwriting score from standardised restaurant data.

    Args:
        data: dict with optional keys:
            "transactions"  pd.DataFrame  normalised PSD2 data
            "pos"           pd.DataFrame  normalised POS records
            "accounting"    pd.DataFrame  normalised P&L / balance sheet
            "kvk"           dict          normalised KvK record
    """
    txn = data.get("transactions", pd.DataFrame())
    pos = data.get("pos", pd.DataFrame())
    acc = data.get("accounting", pd.DataFrame())
    kvk = data.get("kvk", {})

    sub_scores = {
        "revenue_stability":  _revenue_stability(pos),
        "cash_flow_strength": _cash_flow_strength(txn),
        "debt_burden":        _debt_burden(acc),
        "repayment_capacity": _repayment_capacity(acc),
        "cost_structure":     _cost_structure(acc),
        "business_maturity":  _business_maturity(kvk),
        "data_completeness":  _data_completeness(data),
    }

    composite = clamp(sum(sub_scores[k] * WEIGHTS[k] for k in WEIGHTS))

    return ScoreResult(
        composite=round(composite, 2),
        sub_scores={k: round(v, 2) for k, v in sub_scores.items()},
        weights=dict(WEIGHTS),
        grade=_grade(composite),
        risk_band=_risk_band(composite),
        data_completeness=round(sub_scores["data_completeness"], 2),
    )


# ── Sub-score calculators ─────────────────────────────────────────────────────

def _revenue_stability(pos: pd.DataFrame) -> float:
    """Low coefficient of variation in monthly net revenue → high stability score.

    Benchmark: CV of 0 → 100, CV of 1 → 0. Requires ≥3 months of data.
    """
    if pos.empty:
        return 0.0
    monthly = (
        pos.assign(month=pos["date"].dt.to_period("M"))
        .groupby("month")["net_revenue_eur"]
        .sum()
    )
    if len(monthly) < 3:
        return 50.0
    mean = monthly.mean()
    if mean <= 0:
        return 0.0
    cv = monthly.std() / mean
    return clamp(100.0 * (1.0 - cv))


def _cash_flow_strength(txn: pd.DataFrame) -> float:
    """Net operating margin derived from transaction inflows and outflows.

    Benchmark: 30% net margin → 100. Negative net → 0.
    """
    if txn.empty:
        return 0.0
    credits = txn.loc[txn["direction"] == "credit", "amount_eur"].sum()
    debits = txn.loc[txn["direction"] == "debit", "amount_eur"].sum()
    if credits <= 0:
        return 0.0
    net_ratio = (credits - debits) / credits
    return clamp(100.0 * net_ratio / 0.30)


def _debt_burden(acc: pd.DataFrame) -> float:
    """Debt-to-revenue ratio on the most recent accounting year.

    Benchmark: 0 debt → 100; debt ≥ revenue → 0.
    Returns 50 when no accounting data is present (neutral / unknown).
    """
    if acc.empty:
        return 50.0
    latest = acc.sort_values("year").iloc[-1]
    revenue = latest["total_revenue_eur"]
    if revenue <= 0:
        return 0.0
    dtr = latest["total_debt_eur"] / revenue
    return clamp(100.0 * (1.0 - min(dtr, 1.0)))


def _repayment_capacity(acc: pd.DataFrame) -> float:
    """EBITDA margin on the most recent accounting year.

    Benchmark: 30% EBITDA margin → 100; ≤0% → 0.
    Returns 50 when no accounting data is present.
    """
    if acc.empty:
        return 50.0
    latest = acc.sort_values("year").iloc[-1]
    revenue = latest["total_revenue_eur"]
    if revenue <= 0:
        return 0.0
    margin = latest["ebitda_eur"] / revenue
    return clamp(100.0 * margin / 0.30)


def _cost_structure(acc: pd.DataFrame) -> float:
    """Operating cost ratio on the most recent accounting year.

    Benchmarks: 45% cost ratio → 100 (efficient); 85% → 0 (unsustainable).
    Returns 50 when no accounting data is present.
    """
    if acc.empty:
        return 50.0
    latest = acc.sort_values("year").iloc[-1]
    revenue = latest["total_revenue_eur"]
    if revenue <= 0:
        return 0.0
    cost_ratio = latest["total_costs_eur"] / revenue
    return clamp(100.0 * (0.85 - cost_ratio) / 0.40)


def _business_maturity(kvk: dict) -> float:
    """Years since KvK registration, normalised to 10 years.

    Inactive registration applies a 50% penalty to the raw score.
    Returns 0 when no KvK data is present.
    """
    if not kvk:
        return 0.0
    reg_date = kvk.get("registration_date")
    if reg_date is None:
        return 0.0
    ref = reg_date.date() if hasattr(reg_date, "date") else reg_date
    years = (date.today() - ref).days / 365.25
    score = clamp(100.0 * years / 10.0)
    if not kvk.get("is_active", True):
        score *= 0.5
    return score


def _data_completeness(data: dict) -> float:
    """Fraction of the four expected data sources that are populated."""
    checks = {
        "transactions": not data.get("transactions", pd.DataFrame()).empty,
        "pos":          not data.get("pos", pd.DataFrame()).empty,
        "accounting":   not data.get("accounting", pd.DataFrame()).empty,
        "kvk":          bool(data.get("kvk")),
    }
    return clamp(100.0 * sum(checks.values()) / len(checks))


# ── Grade / risk band ─────────────────────────────────────────────────────────

def _grade(score: float) -> str:
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    if score >= 35:
        return "D"
    return "F"


def _risk_band(score: float) -> str:
    if score >= 70:
        return "Low"
    if score >= 50:
        return "Medium"
    if score >= 30:
        return "High"
    return "Very High"
