"""Assembles the Restaurant Credit Passport from scored and explained data."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime

import pandas as pd

from src.scoring.engine import ScoreResult


@dataclass
class CreditPassport:
    restaurant_id: str
    legal_name: str
    generated_at: str                         # ISO-8601 timestamp
    score_result: ScoreResult                 # required — no safe default exists
    profile: dict = field(default_factory=dict)
    financial_indicators: dict = field(default_factory=dict)
    explanations: dict = field(default_factory=dict)
    risk_flags: list = field(default_factory=list)
    financing_readiness: str = ""
    data_sources: list = field(default_factory=list)


def generate(
    restaurant: dict,
    score_result: ScoreResult,
    explanations: dict,
    accounting: pd.DataFrame,
    pos: pd.DataFrame,
) -> CreditPassport:
    """Assemble a CreditPassport from scored and explained restaurant data.

    Args:
        restaurant:   normalised KvK dict (from normalizer.normalize_kvk)
        score_result: output of engine.compute_score
        explanations: output of explainer.explain
        accounting:   normalised accounting DataFrame
        pos:          normalised POS DataFrame
    """
    profile = {
        "restaurant_id":          str(restaurant.get("restaurant_id", "")),
        "legal_name":             str(restaurant.get("legal_name", "")),
        "cuisine_type":           str(restaurant.get("cuisine_type", "")),
        "city":                   str(restaurant.get("city", "")),
        "legal_form":             str(restaurant.get("legal_form", "")),
        "kvk_number":             str(restaurant.get("kvk_number", "")),
        "registration_date":      _fmt_date(restaurant.get("registration_date")),
        "is_active":              bool(restaurant.get("is_active", True)),
        "seats":                  int(restaurant.get("seats", 0)),
        "loan_amount_requested_eur": float(restaurant.get("loan_amount_requested_eur", 0)),
        "loan_purpose":           str(restaurant.get("loan_purpose", "")),
    }

    return CreditPassport(
        restaurant_id=profile["restaurant_id"],
        legal_name=profile["legal_name"],
        generated_at=datetime.now().isoformat(timespec="seconds"),
        profile=profile,
        financial_indicators=_compute_indicators(accounting, pos),
        score_result=score_result,
        explanations=explanations,
        risk_flags=explanations.get("risk_flags", []),
        financing_readiness=_financing_readiness(score_result.composite),
        data_sources=_active_sources(score_result),
    )


def to_json(passport: CreditPassport) -> str:
    """Serialise a CreditPassport to a JSON string."""
    return json.dumps(asdict(passport), indent=2, default=str)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _compute_indicators(accounting: pd.DataFrame, pos: pd.DataFrame) -> dict:
    """Derive key financial indicators from normalised source data."""
    indicators: dict = {}

    if not accounting.empty:
        latest = accounting.sort_values("year").iloc[-1]
        revenue = float(latest["total_revenue_eur"])
        indicators["latest_year"] = int(latest["year"])
        indicators["annual_revenue_eur"] = round(revenue, 2)
        indicators["annual_costs_eur"] = round(float(latest["total_costs_eur"]), 2)
        indicators["ebitda_eur"] = round(float(latest["ebitda_eur"]), 2)
        indicators["net_profit_eur"] = round(float(latest["net_profit_eur"]), 2)
        indicators["total_debt_eur"] = round(float(latest["total_debt_eur"]), 2)
        if revenue > 0:
            indicators["ebitda_margin_pct"] = round(100.0 * latest["ebitda_eur"] / revenue, 1)
            indicators["cost_ratio_pct"] = round(100.0 * latest["total_costs_eur"] / revenue, 1)
            indicators["debt_to_revenue"] = round(float(latest["total_debt_eur"]) / revenue, 2)

    if not pos.empty:
        monthly = (
            pos.assign(month=pos["date"].dt.to_period("M"))
            .groupby("month")["net_revenue_eur"]
            .sum()
        )
        indicators["avg_monthly_revenue_eur"] = round(float(monthly.mean()), 2)
        indicators["trailing_12m_revenue_eur"] = round(float(monthly.tail(12).sum()), 2)

    return indicators


def _financing_readiness(composite: float) -> str:
    if composite >= 70:
        return (
            "Financing-ready — key indicators are within acceptable bounds "
            "for standard lending review."
        )
    if composite >= 50:
        return (
            "Conditionally ready — review of specific risk areas is recommended "
            "before advancing to formal credit assessment."
        )
    if composite >= 35:
        return (
            "Limited readiness — material concerns are present that require "
            "detailed lender review and possible remediation."
        )
    return (
        "Not currently financing-ready — significant barriers to standard "
        "lending criteria are present."
    )


def _active_sources(result: ScoreResult) -> list[str]:
    """Return the data sources that contributed to this score."""
    all_sources = [
        "PSD2 / Open Banking",
        "POS System",
        "Accounting / P&L",
        "KvK Registration",
    ]
    # data_completeness: 100 = all 4, 75 = 3, 50 = 2, 25 = 1, 0 = none
    n = round(result.sub_scores.get("data_completeness", 0) / 25)
    return all_sources[:n]


def _fmt_date(value) -> str:
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)
