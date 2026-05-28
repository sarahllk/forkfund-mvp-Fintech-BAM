"""ForkFund — Restaurant Credit Passport Platform."""

import streamlit as st

from src.demo.scenarios import SCENARIOS, SCENARIO_TYPE_COLOR, SCENARIO_TYPE_LABEL, scenario_ids
from pages.components.shared_styles import inject_shared_styles

st.set_page_config(
    page_title="ForkFund",
    page_icon="🍴",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_shared_styles()

st.markdown("""
<style>
.ff-hero { margin-bottom:24px; }
.ff-hero-title { font-size:30px; font-weight:800; color:#111827; margin:0 0 4px; }
.ff-hero-sub { font-size:14px; color:#9CA3AF; margin:0; font-weight:400; }
.ff-workflow-row { display:flex; gap:0; margin:0 0 20px; }
.ff-workflow-step {
  flex:1; padding:14px 16px; background:#F9FAFB; border:1px solid #E5E7EB;
  border-right:none; font-size:12px;
}
.ff-workflow-step:first-child { border-radius:8px 0 0 8px; }
.ff-workflow-step:last-child  { border-radius:0 8px 8px 0; border-right:1px solid #E5E7EB; }
.ff-workflow-num  { font-size:10px; font-weight:700; color:#9CA3AF;
  letter-spacing:.07em; text-transform:uppercase; margin-bottom:3px; }
.ff-workflow-name { font-size:12.5px; font-weight:700; color:#111827; }
.ff-workflow-desc { font-size:11.5px; color:#6B7280; margin-top:2px; }
.ff-scenario-mini {
  border:1px solid #E5E7EB; border-radius:6px; padding:9px 13px;
  background:#FFFFFF; margin-bottom:5px;
}
.ff-scenario-type-tag {
  display:inline-block; padding:1px 7px; border-radius:3px;
  font-size:9.5px; font-weight:700; letter-spacing:.06em;
  text-transform:uppercase; margin-bottom:3px;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ff-hero">
  <p class="ff-hero-title">ForkFund</p>
  <p class="ff-hero-sub">Restaurant Credit Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

col_main, col_side = st.columns([2.5, 1])

with col_main:
    # ── Workflow ──────────────────────────────────────────────────────────────
    st.markdown("""
<div class="ff-workflow-row">
  <div class="ff-workflow-step">
    <div class="ff-workflow-num">Step 1</div>
    <div class="ff-workflow-name">Onboarding</div>
    <div class="ff-workflow-desc">Select a scenario or register a restaurant</div>
  </div>
  <div class="ff-workflow-step">
    <div class="ff-workflow-num">Step 2</div>
    <div class="ff-workflow-name">Data Connection</div>
    <div class="ff-workflow-desc">Simulate connecting PSD2, POS, accounting, KvK</div>
  </div>
  <div class="ff-workflow-step">
    <div class="ff-workflow-num">Step 3</div>
    <div class="ff-workflow-name">Scoring</div>
    <div class="ff-workflow-desc">Compute an explainable 7-dimension credit score</div>
  </div>
  <div class="ff-workflow-step">
    <div class="ff-workflow-num">Step 4</div>
    <div class="ff-workflow-name">Credit Passport</div>
    <div class="ff-workflow-desc">Review the lender-facing Restaurant Credit Passport</div>
  </div>
  <div class="ff-workflow-step">
    <div class="ff-workflow-num">Step 5</div>
    <div class="ff-workflow-name">Lender Review</div>
    <div class="ff-workflow-desc">Filter and compare lenders by eligibility</div>
  </div>
</div>

<p style="font-size:13px;color:#374151;">
  Begin by choosing a restaurant profile in <strong>Step 1 — Onboarding</strong>
  using the sidebar on the left.
</p>
""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Product positioning ───────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**About this prototype**")
        st.markdown("""
ForkFund is a B2B credit-intelligence tool that aggregates restaurant financial data
into a structured pre-underwriting document. The core output — the Restaurant Credit
Passport — is designed to give lending officers a single, explainable view of a
restaurant's financial health before a formal application is made.

The scoring model is rules-based, transparent, and deterministic. Sub-scores are
displayed individually so that lenders can understand exactly which dimensions
are driving the overall assessment.
        """)
    with c2:
        st.markdown("**Scope and constraints**")
        st.markdown("""
This is a student prototype built for demonstration and evaluation purposes.
All data is computer-generated. The scoring model uses illustrative weights
that have not been validated against real credit outcomes.

ForkFund does not provide credit decisions, financial advice, or any regulated
financial service. It does not connect to live banking, POS, or government systems.
See the Methodology page for a full discussion of limitations.
        """)

    st.markdown("""
<div class="ff-note" style="margin-top:4px;">
  All restaurant, transaction, and lender data shown throughout this application
  is synthetic. No real business records or personal financial data are used.
</div>""", unsafe_allow_html=True)

with col_side:
    # ── Scenario quick list ───────────────────────────────────────────────────
    st.markdown("**Six demo scenarios**")
    st.caption("Available in Step 1 — Onboarding.")

    for rid in scenario_ids():
        s = SCENARIOS[rid]
        color, bg = SCENARIO_TYPE_COLOR.get(s["scenario_type"], ("#6B7280", "#F3F4F6"))
        type_label = SCENARIO_TYPE_LABEL.get(s["scenario_type"], "")
        gh = s.get("grade_hint", "")
        st.markdown(f"""
<div class="ff-scenario-mini">
  <span class="ff-scenario-type-tag" style="background:{bg};color:{color};">{type_label}</span>
  <div style="font-size:12.5px;font-weight:700;color:#111827;">{s['label']}</div>
  <div style="font-size:11px;color:#9CA3AF;margin-top:1px;">Grade {gh} · {s.get('risk_hint','')} risk</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    st.page_link("pages/6_Methodology.py", label="Methodology and limitations")
