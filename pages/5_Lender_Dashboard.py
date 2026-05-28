"""Step 5 — Lender Review: eligible lenders and exclusion analysis."""

import streamlit as st

from src.connectors.accounting import load_accounting
from src.connectors.kvk import load_kvk
from src.connectors.pos import load_pos_records
from src.connectors.psd2 import load_transactions
from src.lender.filters import explain_exclusions, filter_lenders, load_lenders, rank_lenders
from src.passport.generator import generate
from src.scoring.engine import compute_score
from src.scoring.explainer import explain
from src.standardization.normalizer import (
    normalize_accounting, normalize_kvk, normalize_pos, normalize_transactions,
)
from src.demo.scenarios import SCENARIOS, scenario_ids
from pages.components.progress_bar import render_progress
from pages.components.shared_styles import (
    inject_shared_styles, render_empty_state, render_session_banner, context_strip_html,
    GRADE_COLOR, GRADE_BG, RISK_COLOR,
)

st.set_page_config(page_title="Lender Review — ForkFund", layout="wide")
inject_shared_styles()

st.markdown("""
<style>
.ff-lender-card {
  border:1px solid #D1FAE5; border-left:3px solid #16A34A; border-radius:8px;
  padding:16px 18px; background:#FFFFFF; height:100%; box-sizing:border-box;
}
.ff-lender-name   { font-size:13px; font-weight:700; color:#111827; margin:0 0 2px; }
.ff-lender-focus  { font-size:11.5px; color:#6B7280; margin:0 0 10px; }
.ff-headroom {
  display:inline-block; padding:2px 9px; border-radius:4px;
  font-size:11px; font-weight:700; margin-top:8px;
}
.ff-excl-table { width:100%; border-collapse:collapse; }
.ff-excl-table td {
  padding:7px 12px; font-size:12px; vertical-align:top;
  border-bottom:1px solid #F3F4F6;
}
.ff-excl-table tr:last-child td { border-bottom:none; }
.ff-excl-name { font-weight:600; color:#374151; width:180px; }
.ff-excl-reason { color:#6B7280; line-height:1.5; }
.ff-summary-strip {
  display:flex; gap:24px; align-items:center;
  background:#F9FAFB; border:1px solid #E5E7EB; border-radius:8px;
  padding:14px 20px; margin-bottom:18px; flex-wrap:wrap;
}
.ff-summary-stat { text-align:center; flex-shrink:0; }
.ff-summary-num  { font-size:26px; font-weight:800; line-height:1; }
.ff-summary-lbl  {
  font-size:10px; font-weight:700; letter-spacing:.07em;
  text-transform:uppercase; color:#9CA3AF;
}
.ff-divider { width:1px; height:36px; background:#E5E7EB; }
.ff-summary-note {
  flex:1; font-size:11.5px; color:#6B7280; line-height:1.6;
}
.ff-purpose-tag {
  display:inline-block; padding:1px 7px; border-radius:3px;
  font-size:10.5px; background:#F3F4F6; color:#374151;
  margin:1px 2px 1px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("Lender Review")
render_progress(5)
render_session_banner()


@st.cache_data(show_spinner=False)
def _get_passport(rid: str):
    txn = normalize_transactions(load_transactions(rid))
    pos = normalize_pos(load_pos_records(rid))
    acc = normalize_accounting(load_accounting(rid))
    kvk = normalize_kvk(load_kvk(rid))
    sr  = compute_score({"transactions": txn, "pos": pos, "accounting": acc, "kvk": kvk})
    expl = explain(sr)
    return generate(restaurant=kvk, score_result=sr, explanations=expl, accounting=acc, pos=pos), expl


# ── Resolve source ────────────────────────────────────────────────────────────
session_id = st.session_state.get("restaurant_id")
scenario   = st.session_state.get("scenario")
demo_mode  = not bool(session_id)

if demo_mode:
    st.markdown("""
<div class="ff-note" style="margin-bottom:14px;">
  No active session. Select a scenario below to explore lender eligibility.
</div>""", unsafe_allow_html=True)

    ids  = scenario_ids()
    sel  = st.selectbox(
        "Select a scenario",
        ids,
        format_func=lambda k: SCENARIOS[k]["label"],
        label_visibility="collapsed",
    )
    restaurant_id = sel
    scenario      = SCENARIOS.get(sel)
else:
    restaurant_id = session_id

with st.spinner("Loading assessment…"):
    try:
        cached_passport = st.session_state.get("passport")
        cached_expl     = st.session_state.get("explanations")
        if cached_passport and cached_expl:
            passport, explanations = cached_passport, cached_expl
        else:
            passport, explanations = _get_passport(restaurant_id)
            st.session_state["passport"]     = passport
            st.session_state["explanations"] = explanations
    except Exception as e:
        st.error(f"Assessment could not be loaded: {e}")
        st.stop()

# ── Key values ────────────────────────────────────────────────────────────────
score      = passport.score_result.composite
loan_amt   = passport.profile.get("loan_amount_requested_eur", 0)
loan_purp  = passport.profile.get("loan_purpose", "")
grade      = passport.score_result.grade
risk_band  = passport.score_result.risk_band

display_name = scenario["label"] if scenario else passport.profile.get("legal_name", "")
meta         = f"Score {score:.0f} · Grade {grade} · {risk_band} risk"
request_str  = f"Request: €{loan_amt:,.0f} for {loan_purp}"

st.markdown("---")
st.markdown(context_strip_html(display_name, meta, request=request_str), unsafe_allow_html=True)

# ── Filter lenders ────────────────────────────────────────────────────────────
all_lenders     = load_lenders()
eligible        = rank_lenders(
    filter_lenders(all_lenders, score=score, loan_amount=loan_amt, loan_purpose=loan_purp),
    score=score,
)
excluded_notes  = explain_exclusions(all_lenders, score=score, loan_amount=loan_amt, loan_purpose=loan_purp)
n_eligible      = len(eligible)
n_total         = len(all_lenders)
n_excluded      = n_total - n_eligible

# ── Summary strip ─────────────────────────────────────────────────────────────
elig_color = "#16A34A" if n_eligible > 0 else "#B91C1C"
criteria_text = (
    "Criteria applied to all lenders: credit score threshold, "
    "loan amount range, and supported loan purpose. "
    "Results are sorted by interest rate."
)

st.markdown(f"""
<div class="ff-summary-strip">
  <div class="ff-summary-stat">
    <div class="ff-summary-num" style="color:{elig_color};">{n_eligible}</div>
    <div class="ff-summary-lbl">Eligible</div>
  </div>
  <div class="ff-divider"></div>
  <div class="ff-summary-stat">
    <div class="ff-summary-num" style="color:#9CA3AF;">{n_excluded}</div>
    <div class="ff-summary-lbl">Not eligible</div>
  </div>
  <div class="ff-divider"></div>
  <div class="ff-summary-stat">
    <div class="ff-summary-num" style="color:#374151;">{n_total}</div>
    <div class="ff-summary-lbl">Assessed</div>
  </div>
  <div class="ff-summary-note">{criteria_text}</div>
</div>
""", unsafe_allow_html=True)

# ── Eligible lenders ──────────────────────────────────────────────────────────
st.markdown('<span class="ff-section-label">Eligible Lenders</span>', unsafe_allow_html=True)

if eligible.empty:
    st.markdown("""
<div class="ff-alert-amber">
  <strong>No lenders currently meet all criteria</strong> for this profile.
  Common reasons include: credit score below lender thresholds,
  loan amount outside available ranges, or unsupported loan purpose.
  See the section below for per-lender details.
</div>""", unsafe_allow_html=True)
else:
    for i in range(0, len(eligible), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(eligible):
                break
            row = eligible.iloc[idx]

            headroom = score - row["min_score"]
            h_color = "#16A34A" if headroom >= 20 else "#D97706" if headroom >= 5 else "#6B7280"
            h_bg    = "#DCFCE7" if headroom >= 20 else "#FEF3C7" if headroom >= 5 else "#F3F4F6"

            # Purpose tags
            purposes = [p.strip() for p in str(row["supported_purposes"]).split("|") if p.strip()]
            purpose_tags = " ".join(f'<span class="ff-purpose-tag">{p}</span>' for p in purposes)

            with col:
                st.markdown(f"""
<div class="ff-lender-card">
  <p class="ff-lender-name">{row['name']}</p>
  <p class="ff-lender-focus">{row['focus']}</p>
  <div class="ff-row">
    <span class="ff-row-lbl">Interest rate</span>
    <span class="ff-row-val">{row['interest_rate_pct']:.1f}%</span>
  </div>
  <div class="ff-row">
    <span class="ff-row-lbl">Maximum term</span>
    <span class="ff-row-val">{row['max_term_months']} months</span>
  </div>
  <div class="ff-row">
    <span class="ff-row-lbl">Loan range</span>
    <span class="ff-row-val">€{row['min_loan_eur']:,.0f} – €{row['max_loan_eur']:,.0f}</span>
  </div>
  <div class="ff-row">
    <span class="ff-row-lbl">Min. score</span>
    <span class="ff-row-val">{row['min_score']}</span>
  </div>
  <div class="ff-row" style="border-bottom:none;">
    <span class="ff-row-lbl">Products</span>
    <span>{purpose_tags}</span>
  </div>
  <div>
    <span class="ff-headroom" style="background:{h_bg};color:{h_color};">
      +{headroom:.0f} pts above minimum
    </span>
  </div>
</div>""", unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

# ── Excluded lenders ──────────────────────────────────────────────────────────
with st.expander(f"Lenders not meeting criteria ({n_excluded})", expanded=False):
    if not excluded_notes:
        st.caption("All lenders passed the eligibility criteria.")
    else:
        st.markdown("""
<div class="ff-note" style="margin-bottom:10px;">
  Each lender is assessed against three criteria: minimum score threshold,
  loan amount range, and supported loan purpose. Any failed criterion is listed below.
</div>""", unsafe_allow_html=True)
        rows_html = "".join(
            f"""<tr>
  <td class="ff-excl-name">{item['lender']}</td>
  <td class="ff-excl-reason">{"<br>".join(item['reasons'])}</td>
</tr>"""
            for item in excluded_notes
        )
        st.markdown(
            f'<table class="ff-excl-table">{rows_html}</table>',
            unsafe_allow_html=True,
        )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ff-footer">
  All lender profiles are fictional and exist solely for demonstration purposes.
  Rates, criteria, and products shown do not represent any real financial institution.
  This output does not constitute a financing offer or regulated financial advice.
</div>""", unsafe_allow_html=True)
