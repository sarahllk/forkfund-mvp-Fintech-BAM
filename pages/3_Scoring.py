"""Step 3 — Credit score computation, dimension analysis, and revenue trend."""

import streamlit as st

from src.connectors.accounting import load_accounting
from src.connectors.kvk import load_kvk
from src.connectors.pos import load_pos_records
from src.connectors.psd2 import load_transactions
from src.passport.generator import generate
from src.scoring.engine import compute_score
from src.scoring.explainer import explain, DIMENSION_LABELS
from src.standardization.normalizer import (
    normalize_accounting, normalize_kvk, normalize_pos, normalize_transactions,
)
from src.demo.scenarios import SCENARIOS
from pages.components.progress_bar import render_progress
from pages.components.shared_styles import (
    inject_shared_styles, render_empty_state, render_session_banner, context_strip_html,
    GRADE_COLOR, GRADE_BG, RISK_COLOR, RISK_BG,
)
from pages.components.charts import render_subscore_chart, render_revenue_trend

st.set_page_config(page_title="Scoring — ForkFund", layout="wide")
inject_shared_styles()

st.markdown("""
<style>
.ff-score-hero {
  text-align:center; padding:22px 0 16px;
}
.ff-score-num {
  font-size:60px; font-weight:800; line-height:1; letter-spacing:-2px;
}
.ff-score-sub  { font-size:17px; color:#9CA3AF; }
.ff-dim-card   {
  border:1px solid #E5E7EB; border-radius:6px; padding:12px 14px; margin-bottom:6px;
}
.ff-dim-name   { font-size:12px; font-weight:700; color:#111827; margin:0 0 3px; }
.ff-dim-note   { font-size:11.5px; color:#4B5563; line-height:1.5; margin:0; }
.ff-risk-flag  {
  display:flex; gap:8px; align-items:flex-start;
  background:#FFF1F2; border:1px solid #FECDD3; border-radius:5px;
  padding:9px 12px; margin-bottom:5px; font-size:12px; color:#9F1239; line-height:1.5;
}
</style>
""", unsafe_allow_html=True)

st.title("Credit Scoring")
render_progress(3)
render_session_banner()

# ── Gate ──────────────────────────────────────────────────────────────────────
restaurant_id = st.session_state.get("restaurant_id")
scenario      = st.session_state.get("scenario")

if not restaurant_id:
    render_empty_state(
        title="No restaurant selected",
        body="Select a restaurant profile in Step 1 to generate a credit assessment.",
        link_page="pages/1_Onboarding.py",
        link_label="Go to Onboarding →",
    )
    st.stop()


@st.cache_data(show_spinner=False)
def _score(rid: str):
    txn = normalize_transactions(load_transactions(rid))
    pos = normalize_pos(load_pos_records(rid))
    acc = normalize_accounting(load_accounting(rid))
    kvk = normalize_kvk(load_kvk(rid))
    sr  = compute_score({"transactions": txn, "pos": pos, "accounting": acc, "kvk": kvk})
    expl = explain(sr)
    passport = generate(restaurant=kvk, score_result=sr, explanations=expl, accounting=acc, pos=pos)
    return sr, expl, passport, pos


with st.spinner("Computing assessment…"):
    try:
        score_result, explanations, passport, pos_df = _score(restaurant_id)
    except Exception as e:
        st.error(f"Assessment could not be completed: {e}")
        st.stop()

st.session_state["passport"]     = passport
st.session_state["explanations"] = explanations

# ── Context strip ─────────────────────────────────────────────────────────────
display_name = scenario["label"] if scenario else passport.profile.get("legal_name", "")
meta         = f"{passport.profile.get('cuisine_type','')} · {passport.profile.get('city','')}"

st.markdown(context_strip_html(display_name, meta), unsafe_allow_html=True)

# ── Prototype notice ──────────────────────────────────────────────────────────
st.markdown("""
<div class="ff-note" style="margin-bottom:16px;">
  This assessment uses synthetic data and is for demonstration purposes only.
  It does not constitute a credit decision or financial advice.
</div>""", unsafe_allow_html=True)

# ── Score hero + chart ────────────────────────────────────────────────────────
g  = score_result.grade
r  = score_result.risk_band
gc = GRADE_COLOR.get(g, "#6B7280")
gb = GRADE_BG.get(g, "#F3F4F6")
rc = RISK_COLOR.get(r, "#6B7280")
rb = RISK_BG.get(r, "#F9FAFB")

col_score, col_chart = st.columns([1, 2.6])

with col_score:
    st.markdown(f"""
<div class="ff-card" style="text-align:center;padding:22px 16px;">
  <span class="ff-section-label">Pre-Underwriting Score</span>
  <div class="ff-score-hero">
    <span class="ff-score-num" style="color:{gc};">{score_result.composite:.0f}</span>
    <span class="ff-score-sub"> / 100</span>
    <div style="margin-top:10px;">
      <span style="background:{gb};color:{gc};padding:3px 12px;border-radius:4px;
           font-size:13px;font-weight:700;">Grade {g}</span>
    </div>
    <div style="margin-top:6px;">
      <span style="background:{rb};color:{rc};padding:2px 10px;border-radius:4px;
           font-size:12px;font-weight:600;">{r} Risk</span>
    </div>
  </div>
  <div style="font-size:11px;color:#9CA3AF;padding-top:10px;border-top:1px solid #F3F4F6;">
    Data completeness: {score_result.data_completeness:.0f}%
  </div>
</div>""", unsafe_allow_html=True)

with col_chart:
    st.markdown('<div class="ff-card-alt">', unsafe_allow_html=True)
    st.markdown('<span class="ff-section-label">Score Breakdown</span>', unsafe_allow_html=True)
    st.caption("Dotted line at 70 marks the benchmark. Green ≥ 70, amber 50–69, red below 50.")
    render_subscore_chart(score_result, height=215)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Revenue trend ─────────────────────────────────────────────────────────────
st.markdown("---")
col_rt, col_rt_info = st.columns([3, 1])
with col_rt:
    st.markdown('<span class="ff-section-label">Monthly Revenue Trend (12 Months)</span>',
                unsafe_allow_html=True)
    render_revenue_trend(pos_df, height=165)
with col_rt_info:
    st.markdown("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
    st.markdown("""
<div class="ff-card-inset">
  <span style="font-size:10.5px;color:#6B7280;line-height:1.6;display:block;">
    <strong>Blue bars:</strong> monthly net revenue<br>
    <strong>Blue line:</strong> 3-month rolling average<br>
    <strong>Grey dotted:</strong> 12-month mean
  </span>
</div>""", unsafe_allow_html=True)

# ── Dimension notes ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<span class="ff-section-label">Dimension Notes</span>', unsafe_allow_html=True)

dim_notes = explanations.get("dimension_notes", {})
items = [(k, v) for k, v in dim_notes.items() if k != "data_completeness"]
note_cols = st.columns(2)

for i, (dim, note) in enumerate(items):
    score = score_result.sub_scores.get(dim, 0)
    bar_color = "#16A34A" if score >= 70 else "#D97706" if score >= 50 else "#DC2626"
    label = DIMENSION_LABELS.get(dim, dim)
    with note_cols[i % 2]:
        st.markdown(f"""
<div class="ff-dim-card">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:3px;">
    <p class="ff-dim-name">{label}</p>
    <span style="font-size:14px;font-weight:700;color:{bar_color};">{score:.0f}</span>
  </div>
  <p class="ff-dim-note">{note}</p>
</div>""", unsafe_allow_html=True)

# ── Risk flags ────────────────────────────────────────────────────────────────
flags = explanations.get("risk_flags", [])
if flags:
    st.markdown("---")
    st.markdown(
        f'<span class="ff-section-label" style="color:#9F1239;">'
        f'Risk Flags ({len(flags)})</span>',
        unsafe_allow_html=True,
    )
    for f in flags:
        st.markdown(f'<div class="ff-risk-flag"><span style="flex-shrink:0;">●</span><span>{f}</span></div>',
                    unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div class="ff-note">
  Continue to <strong>Credit Passport</strong> to view the complete lender-facing document,
  or skip directly to <strong>Lender Review</strong>.
</div>""", unsafe_allow_html=True)
