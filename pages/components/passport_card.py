"""
ForkFund Credit Passport — reusable presentation component.

All functions are pure display: they accept data objects and render Streamlit UI.
No business logic, no data fetching. Import and call render_passport().
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.passport.generator import CreditPassport
from src.scoring.engine import ScoreResult

# ── Design tokens ─────────────────────────────────────────────────────────────

_GRADE_COLOR: dict[str, str] = {
    "A": "#15803D",
    "B": "#4D7C0F",
    "C": "#B45309",
    "D": "#C2410C",
    "F": "#B91C1C",
}

_GRADE_BG: dict[str, str] = {
    "A": "#DCFCE7",
    "B": "#ECFCCB",
    "C": "#FEF3C7",
    "D": "#FFEDD5",
    "F": "#FEE2E2",
}

_RISK_COLOR: dict[str, str] = {
    "Low":       "#15803D",
    "Medium":    "#B45309",
    "High":      "#C2410C",
    "Very High": "#B91C1C",
}

_RISK_BG: dict[str, str] = {
    "Low":       "#F0FDF4",
    "Medium":    "#FFFBEB",
    "High":      "#FFF7ED",
    "Very High": "#FEF2F2",
}

_DIMENSION_LABEL: dict[str, str] = {
    "revenue_stability":  "Revenue Stability",
    "cash_flow_strength": "Cash-Flow Strength",
    "debt_burden":        "Debt Burden",
    "repayment_capacity": "Repayment Capacity",
    "cost_structure":     "Cost Structure",
    "business_maturity":  "Business Maturity",
    "data_completeness":  "Data Completeness",
}

_ALL_SOURCES = [
    "PSD2 / Open Banking",
    "POS System",
    "Accounting / P&L",
    "KvK Registration",
]


# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS = """
<style>

/* ── Layout cards ──────────────────────────────────────────────────── */
.ff-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 20px 22px 18px;
    margin-bottom: 10px;
    height: 100%;
    box-sizing: border-box;
}
.ff-card-alt {
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 18px 20px 16px;
    margin-bottom: 10px;
    height: 100%;
    box-sizing: border-box;
}

/* ── Section micro-labels ──────────────────────────────────────────── */
.ff-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: #9CA3AF;
    margin: 0 0 10px 0;
    display: block;
}

/* ── Identity header ───────────────────────────────────────────────── */
.ff-id-wrap {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
}
.ff-id-left { flex: 1; min-width: 0; }

.ff-name {
    font-size: 21px;
    font-weight: 700;
    color: #111827;
    margin: 0 0 3px 0;
    line-height: 1.25;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.ff-meta {
    font-size: 12px;
    color: #6B7280;
    margin: 0 0 10px 0;
}
.ff-tags { margin-bottom: 10px; }
.ff-tag {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 5px;
    letter-spacing: 0.01em;
}

/* ── Score badge ───────────────────────────────────────────────────── */
.ff-badge-wrap {
    text-align: center;
    flex-shrink: 0;
}
.ff-badge {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 84px;
    height: 84px;
    border-radius: 50%;
    border: 3px solid rgba(255,255,255,0.30);
}
.ff-badge-score {
    font-size: 30px;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1;
}
.ff-badge-denom {
    font-size: 10px;
    color: rgba(255,255,255,0.75);
    margin-top: 1px;
}
.ff-badge-label {
    font-size: 10px;
    color: #6B7280;
    margin-top: 5px;
    text-align: center;
    line-height: 1.3;
}

/* ── Data source chips ─────────────────────────────────────────────── */
.ff-sources { margin-top: 14px; padding-top: 12px; border-top: 1px solid #F3F4F6; }
.ff-chip {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 12px;
    font-size: 10.5px;
    font-weight: 500;
    margin-right: 5px;
    margin-bottom: 4px;
}
.ff-chip-ok  { background:#DCFCE7; color:#166534; border:1px solid #BBF7D0; }
.ff-chip-off { background:#F3F4F6; color:#9CA3AF; border:1px solid #E5E7EB; }

/* ── Sub-score bars ────────────────────────────────────────────────── */
.ff-bar-row {
    display: flex;
    align-items: center;
    gap: 7px;
    margin-bottom: 6px;
}
.ff-bar-lbl {
    width: 152px;
    font-size: 11.5px;
    color: #4B5563;
    flex-shrink: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.ff-bar-track {
    flex: 1;
    height: 5px;
    background: #E5E7EB;
    border-radius: 3px;
    overflow: hidden;
}
.ff-bar-fill { height: 100%; border-radius: 3px; }
.ff-bar-val {
    width: 26px;
    font-size: 11.5px;
    font-weight: 600;
    color: #374151;
    text-align: right;
    flex-shrink: 0;
}

/* ── Financial indicator rows ──────────────────────────────────────── */
.ff-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 5px 0;
    border-bottom: 1px solid #F3F4F6;
}
.ff-row:last-child { border-bottom: none; }
.ff-row-lbl { font-size: 11.5px; color: #6B7280; }
.ff-row-val { font-size: 12.5px; font-weight: 600; color: #111827; }

/* ── Readiness box ─────────────────────────────────────────────────── */
.ff-readiness {
    border-radius: 6px;
    padding: 9px 13px;
    font-size: 11.5px;
    line-height: 1.5;
    margin-top: 10px;
    display: flex;
    gap: 8px;
    align-items: flex-start;
}

/* ── Assessment ────────────────────────────────────────────────────── */
.ff-summary {
    font-size: 12.5px;
    color: #374151;
    line-height: 1.65;
    padding: 11px 15px;
    background: #F9FAFB;
    border-left: 3px solid #CBD5E1;
    border-radius: 0 5px 5px 0;
    margin-bottom: 14px;
}
.ff-driver {
    display: flex;
    gap: 7px;
    align-items: flex-start;
    font-size: 11.5px;
    color: #374151;
    padding: 3px 0;
    line-height: 1.45;
}
.ff-driver-icon { flex-shrink: 0; font-size: 11px; margin-top: 1px; }
.ff-flag {
    display: flex;
    gap: 8px;
    align-items: flex-start;
    background: #FFF1F2;
    border: 1px solid #FECDD3;
    border-radius: 5px;
    padding: 8px 11px;
    margin-bottom: 5px;
    font-size: 11.5px;
    color: #9F1239;
    line-height: 1.45;
}

/* ── Disclaimer ────────────────────────────────────────────────────── */
.ff-disclaimer {
    font-size: 10px;
    color: #D1D5DB;
    margin-top: 14px;
    padding-top: 10px;
    border-top: 1px solid #F3F4F6;
    line-height: 1.6;
}

</style>
"""


def inject_styles() -> None:
    """Inject passport CSS into the page. Call once per render."""
    st.markdown(_CSS, unsafe_allow_html=True)


# ── HTML helpers ──────────────────────────────────────────────────────────────

def _bar_color(score: float) -> str:
    if score >= 70:
        return "#16A34A"
    if score >= 50:
        return "#D97706"
    return "#DC2626"


def _score_badge_html(composite: float, grade: str) -> str:
    bg = _GRADE_COLOR.get(grade, "#6B7280")
    return f"""
<div class="ff-badge-wrap">
  <div class="ff-badge" style="background:{bg};">
    <span class="ff-badge-score">{composite:.0f}</span>
    <span class="ff-badge-denom">/ 100</span>
  </div>
  <div class="ff-badge-label">Pre-underwriting<br>Score</div>
</div>"""


def _tag_html(text: str, color: str, bg: str) -> str:
    return f'<span class="ff-tag" style="color:{color};background:{bg};">{text}</span>'


def _chip_html(label: str, verified: bool) -> str:
    cls = "ff-chip ff-chip-ok" if verified else "ff-chip ff-chip-off"
    icon = "✓" if verified else "○"
    return f'<span class="{cls}">{icon} {label}</span>'


def _bar_row_html(label: str, score: float) -> str:
    color = _bar_color(score)
    pct = min(100.0, max(0.0, score))
    return f"""
<div class="ff-bar-row">
  <span class="ff-bar-lbl">{label}</span>
  <div class="ff-bar-track"><div class="ff-bar-fill" style="width:{pct:.0f}%;background:{color};"></div></div>
  <span class="ff-bar-val">{score:.0f}</span>
</div>"""


def _ind_row_html(label: str, value: str) -> str:
    return f"""
<div class="ff-row">
  <span class="ff-row-lbl">{label}</span>
  <span class="ff-row-val">{value}</span>
</div>"""


def _driver_html(text: str, positive: bool) -> str:
    icon  = "✓" if positive else "⚠"
    color = "#16A34A" if positive else "#CA8A04"
    return f"""
<div class="ff-driver">
  <span class="ff-driver-icon" style="color:{color};">{icon}</span>
  <span>{text}</span>
</div>"""


def _flag_html(text: str) -> str:
    return f"""
<div class="ff-flag">
  <span style="flex-shrink:0;">●</span>
  <span>{text}</span>
</div>"""


# ── Section renderers ─────────────────────────────────────────────────────────

def render_identity_header(
    passport: CreditPassport,
    display_name: str | None = None,
) -> None:
    """Restaurant name, meta, score badge, grade/risk tags, source chips.

    Args:
        display_name: When provided (e.g. a curated scenario label), shown as the
                      primary heading. The legal name is shown as a smaller reference
                      line. When absent, the legal name is used as the primary heading.
    """
    p = passport.profile
    sr = passport.score_result

    years_str = ""
    try:
        reg = pd.to_datetime(p.get("registration_date", "")).date()
        yrs = (date.today() - reg).days // 365
        years_str = f"Est. {reg.year} &nbsp;·&nbsp; {yrs} {'yr' if yrs == 1 else 'yrs'} operating"
    except Exception:
        pass

    legal_name = p.get("legal_name", "")
    cuisine    = p.get("cuisine_type", "")
    city       = p.get("city", "")
    kvk        = p.get("kvk_number", "")
    seats      = p.get("seats", "")
    grade      = sr.grade
    risk       = sr.risk_band

    # When a curated display name is active, show it prominently and render the
    # legal name as a secondary reference (useful for verification / audit trail).
    if display_name:
        primary_name = display_name
        secondary_line = (
            f'<p class="ff-meta" style="margin:0 0 8px;">'
            f'Registered as: {legal_name} &nbsp;·&nbsp; {cuisine} &nbsp;·&nbsp; {city}'
            f'</p>'
        )
    else:
        primary_name = legal_name or "—"
        secondary_line = (
            f'<p class="ff-meta" style="margin:0 0 8px;">'
            f'{cuisine} &nbsp;·&nbsp; {city}'
            f'</p>'
        )

    badge = _score_badge_html(sr.composite, grade)
    g_tag = _tag_html(f"Grade {grade}", _GRADE_COLOR.get(grade, "#666"), _GRADE_BG.get(grade, "#F3F4F6"))
    r_tag = _tag_html(f"{risk} Risk",    _RISK_COLOR.get(risk, "#666"),  _RISK_BG.get(risk, "#F9FAFB"))
    chips = "".join(_chip_html(s, s in passport.data_sources) for s in _ALL_SOURCES)

    st.markdown(f"""
<div class="ff-card">
  <div class="ff-id-wrap">
    <div class="ff-id-left">
      <p class="ff-name">{primary_name}</p>
      {secondary_line}
      <p class="ff-meta" style="margin:0 0 8px;">
        KvK {kvk} &nbsp;·&nbsp; {seats} seats
      </p>
      <div class="ff-tags">{g_tag} {r_tag}</div>
      <p class="ff-meta" style="margin:0;">{years_str}</p>
    </div>
    {badge}
  </div>
  <div class="ff-sources">
    <span class="ff-label" style="display:inline;margin-right:8px;">Data Sources</span>
    {chips}
  </div>
</div>""", unsafe_allow_html=True)


def render_sub_scores(score_result: ScoreResult) -> None:
    """Sub-score bars panel."""
    bars = "".join(
        _bar_row_html(_DIMENSION_LABEL.get(dim, dim), score)
        for dim, score in score_result.sub_scores.items()
    )
    st.markdown(f"""
<div class="ff-card-alt" style="height:auto;">
  <span class="ff-label">Score Breakdown</span>
  {bars}
</div>""", unsafe_allow_html=True)


def render_key_indicators(passport: CreditPassport) -> None:
    """Key financial indicators panel."""
    ind = passport.financial_indicators

    def _eur(k: str) -> str:
        v = ind.get(k)
        return f"€{v:,.0f}" if v is not None else "—"

    def _pct(k: str) -> str:
        v = ind.get(k)
        return f"{v:.1f}%" if v is not None else "—"

    def _ratio(k: str) -> str:
        v = ind.get(k)
        return f"{v:.2f}×" if v is not None else "—"

    rows = "".join([
        _ind_row_html("Annual Revenue",       _eur("annual_revenue_eur")),
        _ind_row_html("EBITDA",               _eur("ebitda_eur")),
        _ind_row_html("EBITDA Margin",        _pct("ebitda_margin_pct")),
        _ind_row_html("Cost Ratio",           _pct("cost_ratio_pct")),
        _ind_row_html("Debt-to-Revenue",      _ratio("debt_to_revenue")),
        _ind_row_html("Avg Monthly Revenue",  _eur("avg_monthly_revenue_eur")),
        _ind_row_html("Trailing 12m Revenue", _eur("trailing_12m_revenue_eur")),
    ])

    yr = ind.get("latest_year", "")
    yr_note = f"<span class='ff-label' style='display:inline;'>Based on {yr} accounts</span>" if yr else ""

    st.markdown(f"""
<div class="ff-card-alt" style="height:auto;">
  <span class="ff-label">Key Financial Indicators</span>
  {rows}
  <div style="margin-top:8px;">{yr_note}</div>
</div>""", unsafe_allow_html=True)


def render_financing_request(passport: CreditPassport) -> None:
    """Financing request and readiness panel."""
    p = passport.profile
    readiness = passport.financing_readiness

    if "Financing-ready" in readiness:
        r_color, r_bg, r_border, r_icon = "#166534", "#F0FDF4", "#BBF7D0", "✓"
    elif "Conditionally" in readiness:
        r_color, r_bg, r_border, r_icon = "#92400E", "#FFFBEB", "#FDE68A", "◎"
    elif "Limited" in readiness:
        r_color, r_bg, r_border, r_icon = "#9A3412", "#FFF7ED", "#FDBA74", "⚠"
    else:
        r_color, r_bg, r_border, r_icon = "#991B1B", "#FEF2F2", "#FECACA", "✗"

    amt = p.get("loan_amount_requested_eur", 0)
    purpose = p.get("loan_purpose", "—")

    rows = "".join([
        _ind_row_html("Requested Amount", f"€{amt:,.0f}"),
        _ind_row_html("Purpose",          purpose),
        _ind_row_html("Legal Form",       p.get("legal_form", "—")),
    ])

    st.markdown(f"""
<div class="ff-card-alt" style="height:auto;">
  <span class="ff-label">Financing Request</span>
  {rows}
  <div class="ff-readiness" style="background:{r_bg};border:1px solid {r_border};color:{r_color};">
    <span style="flex-shrink:0;font-weight:700;">{r_icon}</span>
    <span>{readiness}</span>
  </div>
</div>""", unsafe_allow_html=True)


def render_assessment(explanations: dict, score_result: ScoreResult) -> None:
    """Summary, positive drivers, areas of concern, risk flags."""
    summary   = explanations.get("summary", "")
    positives = explanations.get("positive_drivers", [])
    negatives = explanations.get("negative_drivers", [])
    flags     = explanations.get("risk_flags", [])

    pos_html = ("".join(_driver_html(d, True)  for d in positives)
                or "<span style='font-size:11px;color:#9CA3AF;'>No positive indicators at threshold.</span>")
    neg_html = ("".join(_driver_html(d, False) for d in negatives)
                or "<span style='font-size:11px;color:#9CA3AF;'>No areas of concern identified.</span>")

    flag_section = ""
    if flags:
        flags_html = "".join(_flag_html(f) for f in flags)
        flag_section = f"""
<div style="margin-top:16px;">
  <span class="ff-label" style="color:#9F1239;">Risk Flags ({len(flags)})</span>
  {flags_html}
</div>"""

    completeness = score_result.sub_scores.get("data_completeness", 0)
    completeness_note = (
        f"<span style='font-size:11px;color:#6B7280;'>Data completeness: "
        f"<strong>{completeness:.0f}%</strong></span>"
    )

    st.markdown(f"""
<div class="ff-card">
  <span class="ff-label">Lender Assessment</span>
  <div class="ff-summary">{summary}</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;">
    <div>
      <span class="ff-label" style="color:#166534;">Positive Indicators</span>
      {pos_html}
    </div>
    <div>
      <span class="ff-label" style="color:#B45309;">Areas of Concern</span>
      {neg_html}
    </div>
  </div>
  {flag_section}
  <div style="margin-top:14px;">{completeness_note}</div>
</div>""", unsafe_allow_html=True)


def render_disclaimer(generated_at: str = "") -> None:
    """Regulatory and MVP disclaimer footer."""
    ts = f" &nbsp;·&nbsp; Generated {generated_at}" if generated_at else ""
    st.markdown(f"""
<div class="ff-disclaimer">
  Pre-underwriting reference only. Not a credit decision, credit approval,
  or financial advice. Derived from entirely synthetic, computer-generated data.
  ForkFund is a demonstration prototype — not a regulated financial service.{ts}
</div>""", unsafe_allow_html=True)


# ── Master entry point ────────────────────────────────────────────────────────

def render_passport(
    passport: CreditPassport,
    explanations: dict,
    display_name: str | None = None,
) -> None:
    """Render the complete Credit Passport.

    Args:
        passport:     assembled CreditPassport (from src.passport.generator.generate)
        explanations: output of src.scoring.explainer.explain
        display_name: optional curated label shown as primary heading in the
                      identity header (e.g. a scenario label). Does not affect
                      the underlying passport data or JSON export.
    """
    inject_styles()

    render_identity_header(passport, display_name=display_name)

    col_l, col_m, col_r = st.columns([2.3, 2.1, 1.6])
    with col_l:
        render_sub_scores(passport.score_result)
    with col_m:
        render_key_indicators(passport)
    with col_r:
        render_financing_request(passport)

    render_assessment(explanations, passport.score_result)
    render_disclaimer(passport.generated_at)
