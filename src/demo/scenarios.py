"""
Curated demo restaurant scenarios for ForkFund presentations.

Each scenario is tied to a specific synthetic restaurant and illustrates
a distinct financing case lenders routinely encounter.
No business logic — pure reference data used by the UI layer.

IDs are stable. The legal names in the CSV are synthetic and irrelevant to users;
the `label` field is always shown instead.
"""

from __future__ import annotations

SCENARIOS: dict[str, dict] = {

    "R0084": {
        "restaurant_id": "R0084",
        "label": "Established Neighbourhood Restaurant",
        "tagline": "19-year business with stable year-round revenue and healthy margins.",
        "scenario_type": "financing_ready",
        "grade_hint": "A",
        "risk_hint": "Low",
        "context": (
            "A mature, well-run restaurant with nearly two decades of trading history. "
            "Revenue is consistent month-on-month, EBITDA margin is healthy at 35%, "
            "and existing debt is modest relative to revenue. "
            "The working capital request is small in relation to annual turnover."
        ),
        "lender_notice": (
            "Strong margins and a long track record make this a straightforward "
            "assessment. The primary due-diligence question is whether the facility "
            "is genuinely needed for working capital or represents an opportunity "
            "to build a banking relationship."
        ),
        "financing_challenge": (
            "Working capital facility (€25k) against annual revenue of approximately "
            "€341k. Serviceability is not in question. Lenders may apply standard "
            "hospitality sector policies around minimum annual turnover and operating tenure."
        ),
        "lender_focus": [
            "Revenue consistency and month-on-month stability",
            "EBITDA margin relative to sector benchmarks",
            "Existing debt service coverage",
        ],
    },

    "R0029": {
        "restaurant_id": "R0029",
        "label": "Seasonal Restaurant with Revenue Variability",
        "tagline": "9-year business with pronounced seasonal swings and moderate margins.",
        "scenario_type": "seasonal_risk",
        "grade_hint": "C",
        "risk_hint": "Medium",
        "context": (
            "A 9-year restaurant with good peak-season revenue but a revenue "
            "stability score of 30 out of 100 — among the lowest in the dataset. "
            "EBITDA margin is 26% at the most recent year-end, but the seasonal "
            "trough creates recurring working capital pressure. "
            "Existing debt is significant at 0.62 times revenue."
        ),
        "lender_notice": (
            "Revenue variability is the dominant concern. A lender should examine "
            "whether off-peak cash flow is sufficient to service new debt obligations "
            "before the next peak period arrives. Operating cost control is also "
            "below typical sector benchmarks."
        ),
        "financing_challenge": (
            "Working capital facility (€25k) to bridge seasonal cash-flow gaps. "
            "Serviceability at peak is adequate; the question is whether winter "
            "cash reserves can carry repayments through the trough months."
        ),
        "lender_focus": [
            "Month-by-month cash flow distribution",
            "Off-peak reserve adequacy",
            "Debt service coverage at minimum seasonal revenue",
        ],
    },

    "R0002": {
        "restaurant_id": "R0002",
        "label": "Fast-Growing Restaurant with High Leverage",
        "tagline": "4-year business with exceptional margins but an already-leveraged balance sheet.",
        "scenario_type": "growth_stage",
        "grade_hint": "B",
        "risk_hint": "Low",
        "context": (
            "A relatively young restaurant (3.9 years) that has reached €310k annual "
            "revenue. EBITDA margin is exceptional at 49.5%. However, existing debt "
            "stands at 0.71 times revenue, and business maturity is low due to "
            "the limited trading history."
        ),
        "lender_notice": (
            "The financial performance is strong, but the combination of limited "
            "trading history and an already-leveraged balance sheet warrants scrutiny. "
            "A lender should assess whether additional revolving capacity will be "
            "used to fund growth or to bridge cash-flow gaps."
        ),
        "financing_challenge": (
            "Revolving credit facility (€75k). The business is profitable enough "
            "to service the commitment, but post-drawdown leverage needs to be "
            "assessed against projected revenue growth and debt service obligations."
        ),
        "lender_focus": [
            "Revenue growth trajectory and consistency",
            "Purpose and utilisation of the revolving facility",
            "Post-drawdown debt service coverage",
        ],
    },

    "R0028": {
        "restaurant_id": "R0028",
        "label": "Recently Opened Restaurant",
        "tagline": "2.8-year business with solid margins but a trading record below standard thresholds.",
        "scenario_type": "limited_history",
        "grade_hint": "B",
        "risk_hint": "Medium",
        "context": (
            "A restaurant that opened 2.8 years ago with €400k annual revenue and "
            "a 34% EBITDA margin — indicating sound operations. The lower composite "
            "score is driven almost entirely by business maturity (below standard "
            "3-year thresholds). The loan request is modest at €10k."
        ),
        "lender_notice": (
            "The financials are healthy for a business this age. The main risk is "
            "the absence of a long trading record to confirm that current performance "
            "is sustainable. Many standard lender policies require a minimum of "
            "3 years of filed accounts."
        ),
        "financing_challenge": (
            "Small term loan (€10k). Serviceability is strong, but the sub-3-year "
            "operating history may exclude this business from standard underwriting "
            "criteria. Specialist SME or micro-finance lenders are the appropriate channel."
        ),
        "lender_focus": [
            "Management background and relevant sector experience",
            "Revenue trajectory since opening",
            "Whether trading history meets minimum lender policy requirements",
        ],
    },

    "R0022": {
        "restaurant_id": "R0022",
        "label": "Mature Restaurant with Stretched Margins",
        "tagline": "25-year business with high revenue but compressed margins and significant existing debt.",
        "scenario_type": "high_leverage",
        "grade_hint": "C",
        "risk_hint": "Medium",
        "context": (
            "A well-established restaurant group with €651k annual revenue. "
            "The business has a long trading history and relatively stable revenue. "
            "However, existing debt stands at 0.71 times revenue, the EBITDA margin "
            "has compressed to 18%, and the cost structure score is very low — "
            "indicating thin operating margins relative to revenue."
        ),
        "lender_notice": (
            "The leverage ratio is the central concern. At 0.71 times debt-to-revenue "
            "with an 18% EBITDA margin, debt service coverage is already under "
            "pressure. Additional revolving credit will further increase the "
            "fixed obligations that must be covered from operating cash flow."
        ),
        "financing_challenge": (
            "Revolving credit facility (€50k) — likely intended to manage "
            "working capital as margins have compressed. While modest relative to "
            "revenue, the incremental debt service burden is material given the "
            "existing leverage position."
        ),
        "lender_focus": [
            "Debt service coverage ratio before and after the new facility",
            "Root cause of margin compression over recent years",
            "Management plan to address cost structure",
        ],
    },

    "R0086": {
        "restaurant_id": "R0086",
        "label": "Operationally Distressed Restaurant",
        "tagline": "21-year business with very thin margins and multiple risk flags.",
        "scenario_type": "distressed",
        "grade_hint": "C",
        "risk_hint": "Medium",
        "context": (
            "Despite 21 years of operation and low debt (0.15 times revenue), "
            "this restaurant is under significant operational stress. The cost ratio "
            "is 94.2%, the EBITDA margin is 5.8%, and the repayment capacity score "
            "is 19 out of 100. Cash-flow strength from transaction data is 30 — "
            "indicating weak operating cash flow relative to revenues of €159k."
        ),
        "lender_notice": (
            "Three risk flags are active. The near-zero EBITDA margin means any "
            "additional fixed obligation threatens viability. This is an operational "
            "problem, not a financial structure problem — the business has limited "
            "debt but cannot generate sufficient free cash flow to service it."
        ),
        "financing_challenge": (
            "Equipment finance (€10k). A lender would need to understand how the "
            "new equipment specifically addresses the margin problem before advancing "
            "any facility. Financing operational distress without a remediation "
            "plan typically results in a larger problem deferred."
        ),
        "lender_focus": [
            "Identifying the root cause of the 94% cost ratio",
            "Management's plan to restore margins before expansion",
            "Whether new equipment addresses cost structure or increases it",
        ],
    },
}

# Ordered for display — from strongest to most distressed
SCENARIO_ORDER = ["R0084", "R0002", "R0022", "R0028", "R0029", "R0086"]

SCENARIO_TYPE_COLOR: dict[str, tuple[str, str]] = {
    "financing_ready": ("#15803D", "#F0FDF4"),
    "growth_stage":    ("#2563EB", "#EFF6FF"),
    "high_leverage":   ("#B45309", "#FFFBEB"),
    "limited_history": ("#6D28D9", "#F5F3FF"),
    "seasonal_risk":   ("#0E7490", "#ECFEFF"),
    "distressed":      ("#B91C1C", "#FEF2F2"),
}

SCENARIO_TYPE_LABEL: dict[str, str] = {
    "financing_ready": "Financing Ready",
    "growth_stage":    "Growth Stage",
    "high_leverage":   "High Leverage",
    "limited_history": "Limited History",
    "seasonal_risk":   "Seasonal Risk",
    "distressed":      "Operational Distress",
}


def get_scenario(restaurant_id: str) -> dict | None:
    return SCENARIOS.get(restaurant_id)


def scenario_ids() -> list[str]:
    return SCENARIO_ORDER
