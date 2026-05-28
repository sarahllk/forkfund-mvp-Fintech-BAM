"""Generates structured, lender-facing explanations from a ScoreResult.

Language is factual and operational. No marketing or predictive claims.
"""

from src.scoring.engine import ScoreResult

# Thresholds for driver classification
_POSITIVE_THRESHOLD = 70.0
_NEGATIVE_THRESHOLD = 50.0
_FLAG_THRESHOLD = 35.0

DIMENSION_LABELS: dict[str, str] = {
    "revenue_stability":  "Revenue Stability",
    "cash_flow_strength": "Cash-Flow Strength",
    "debt_burden":        "Debt Burden",
    "repayment_capacity": "Repayment Capacity",
    "cost_structure":     "Cost Structure",
    "business_maturity":  "Business Maturity",
    "data_completeness":  "Data Completeness",
}

_POSITIVE: dict[str, str] = {
    "revenue_stability":  "Revenue is consistent month-on-month, indicating stable trading conditions.",
    "cash_flow_strength": "Operating cash flow is net positive with a healthy inflow-to-outflow margin.",
    "debt_burden":        "Existing debt load is low relative to annual revenue.",
    "repayment_capacity": "EBITDA margin supports adequate debt service capacity.",
    "cost_structure":     "Operating cost ratio is within an efficient range for the hospitality sector.",
    "business_maturity":  "The business has an established trading history.",
    "data_completeness":  "All four data sources are present and sufficiently populated.",
}

_NEUTRAL: dict[str, str] = {
    "revenue_stability":  "Revenue shows moderate variability; further review of seasonal patterns is advised.",
    "cash_flow_strength": "Cash flow position is marginal; inflow-to-outflow margin is below benchmark.",
    "debt_burden":        "Debt level is moderate relative to revenue; serviceability depends on EBITDA trajectory.",
    "repayment_capacity": "EBITDA margin is below the sector benchmark but not critically low.",
    "cost_structure":     "Cost ratio is above the efficient threshold but within a manageable range.",
    "business_maturity":  "The business has a limited but developing trading history.",
    "data_completeness":  "One or more data sources have limited coverage; assessment confidence is reduced.",
}

_NEGATIVE: dict[str, str] = {
    "revenue_stability":  "Revenue exhibits significant month-to-month variation.",
    "cash_flow_strength": "Cash outflows are high relative to inflows; net operating margin is weak.",
    "debt_burden":        "Existing debt is elevated relative to annual revenue.",
    "repayment_capacity": "EBITDA margin is insufficient to comfortably service additional debt obligations.",
    "cost_structure":     "Operating cost ratio is high, materially compressing margins.",
    "business_maturity":  "The business has fewer than two years of trading history.",
    "data_completeness":  "Multiple data sources are absent; assessment reliability is significantly reduced.",
}

_RISK_FLAG: dict[str, str] = {
    "revenue_stability":  "Severe revenue volatility over the review period — structural trading instability cannot be ruled out.",
    "cash_flow_strength": "Net cash flow was negative over the review period — cash burn requires investigation.",
    "debt_burden":        "Debt burden is very high relative to revenue — capacity for additional financing is materially constrained.",
    "repayment_capacity": "EBITDA is negative or near zero — the business cannot currently service additional debt from operations.",
    "cost_structure":     "Cost structure is unsustainable at current revenue levels — intervention or restructuring may be required.",
    "business_maturity":  "Business is less than twelve months old — no meaningful historical trading record is available.",
    "data_completeness":  "Critical data gaps are present — the assessment should not be used as the sole basis for a financing decision.",
}


def explain(result: ScoreResult) -> dict:
    """Return structured lender-facing explanations from a ScoreResult.

    Returns a dict with keys:
        positive_drivers  list[str]       dimensions at or above the benchmark
        negative_drivers  list[str]       dimensions below the benchmark
        risk_flags        list[str]       dimensions requiring immediate lender attention
        dimension_notes   dict[str, str]  one note per dimension
        summary           str             single lender-facing paragraph
    """
    positive_drivers: list[str] = []
    negative_drivers: list[str] = []
    risk_flags: list[str] = []
    dimension_notes: dict[str, str] = {}

    for dim, score in result.sub_scores.items():
        note = _pick_note(dim, score)
        dimension_notes[dim] = note

        if score >= _POSITIVE_THRESHOLD:
            positive_drivers.append(_POSITIVE[dim])
        elif score < _NEGATIVE_THRESHOLD:
            negative_drivers.append(_NEGATIVE[dim])

        if score < _FLAG_THRESHOLD:
            risk_flags.append(_RISK_FLAG[dim])

    summary = _build_summary(result, positive_drivers, negative_drivers, risk_flags)

    return {
        "positive_drivers": positive_drivers,
        "negative_drivers": negative_drivers,
        "risk_flags": risk_flags,
        "dimension_notes": dimension_notes,
        "summary": summary,
    }


def _pick_note(dim: str, score: float) -> str:
    if score >= _POSITIVE_THRESHOLD:
        return _POSITIVE[dim]
    if score >= _NEGATIVE_THRESHOLD:
        return _NEUTRAL[dim]
    return _NEGATIVE[dim]


def _build_summary(
    result: ScoreResult,
    positive: list[str],
    negative: list[str],
    flags: list[str],
) -> str:
    opening = (
        f"Overall pre-underwriting score: {result.composite:.0f}/100 "
        f"(Grade {result.grade}, {result.risk_band} risk). "
    )

    if flags:
        n = len(flags)
        mid = f"{n} risk flag{'s' if n > 1 else ''} identified requiring lender review. "
    elif negative:
        n = len(negative)
        mid = f"{n} dimension{'s' if n > 1 else ''} below benchmark. "
    else:
        mid = "All assessed dimensions are at or above benchmark. "

    if len(positive) >= 3:
        close = (
            "Key strengths include revenue consistency, cash flow position, "
            "and operational efficiency."
        )
    elif len(positive) >= 1:
        n = len(positive)
        close = f"{n} positive indicator{'s' if n > 1 else ''} noted."
    else:
        close = "No dimensions currently exceed the benchmark threshold."

    return opening + mid + close
