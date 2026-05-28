"""Step 2 — Simulate connecting data sources."""

import streamlit as st

from src.demo.scenarios import SCENARIOS
from pages.components.progress_bar import render_progress
from pages.components.shared_styles import (
    inject_shared_styles, render_empty_state, render_session_banner, context_strip_html,
)

st.set_page_config(page_title="Data Connection — ForkFund", layout="wide")
inject_shared_styles()

st.markdown("""
<style>
.ff-source-card {
  border:1px solid #E5E7EB; border-radius:8px; padding:16px 20px;
  background:#FFFFFF; margin-bottom:10px; display:flex; gap:16px;
  align-items:flex-start;
}
.ff-source-connected { border-left:3px solid #16A34A; }
.ff-source-icon  { font-size:20px; flex-shrink:0; margin-top:2px; }
.ff-source-body  { flex:1; min-width:0; }
.ff-source-name  { font-size:13px; font-weight:700; color:#111827; margin:0 0 2px; }
.ff-source-desc  { font-size:12px; color:#4B5563; margin:0; line-height:1.5; }
.ff-source-note  {
  margin-top:8px; background:#F9FAFB; border:1px solid #F3F4F6;
  border-radius:5px; padding:9px 13px; font-size:11.5px; color:#6B7280; line-height:1.55;
}
.ff-source-status {
  flex-shrink:0; font-size:11px; font-weight:700; letter-spacing:.04em;
  text-transform:uppercase; white-space:nowrap; margin-top:4px;
}
</style>
""", unsafe_allow_html=True)

st.title("Data Connection")
render_progress(2)
render_session_banner()

# ── Gate: require completed onboarding ───────────────────────────────────────
restaurant_id = st.session_state.get("restaurant_id")
scenario      = st.session_state.get("scenario")

if not restaurant_id:
    render_empty_state(
        title="No restaurant selected",
        body="Select a restaurant profile in Step 1 before connecting data sources.",
        link_page="pages/1_Onboarding.py",
        link_label="Go to Onboarding →",
    )
    st.stop()

# ── Context strip ─────────────────────────────────────────────────────────────
display_name = scenario["label"] if scenario else st.session_state.get(
    "custom_restaurant", {}).get("name", restaurant_id)
meta = scenario.get("tagline", "") if scenario else ""

st.markdown(context_strip_html(display_name, meta), unsafe_allow_html=True)

# ── Sources definition ────────────────────────────────────────────────────────
SOURCES = [
    {
        "key":   "psd2",
        "icon":  "🏦",
        "label": "Open Banking (PSD2)",
        "desc":  "12-month bank transaction history covering all credits and debits. "
                 "Powers the cash-flow strength and revenue calculation.",
        "note":  "In production this requires a PSD2-licenced TPP and explicit account-holder "
                 "consent. Here a synthetic transaction file is loaded directly.",
    },
    {
        "key":   "pos",
        "icon":  "🖨️",
        "label": "Point of Sale",
        "desc":  "Daily covers and net revenue from the point-of-sale system. "
                 "Used to assess revenue stability and detect seasonal patterns.",
        "note":  "A real connection would use a POS provider API (Lightspeed, Square) "
                 "under an OAuth flow authorised by the operator.",
    },
    {
        "key":   "accounting",
        "icon":  "📊",
        "label": "Accounting Records",
        "desc":  "Three years of annual profit and loss and balance sheet. "
                 "Provides EBITDA margin, cost ratio, and debt figures.",
        "note":  "Production access would connect to accounting software (Exact, Moneybird) "
                 "via their published APIs.",
    },
    {
        "key":   "kvk",
        "icon":  "🏛️",
        "label": "KvK Registration",
        "desc":  "Dutch Chamber of Commerce registration data: legal name, form, "
                 "registration date, and active status.",
        "note":  "A production version would verify identity against the KvK OpenData API, "
                 "matched to the authenticated account holder.",
    },
]

connected = st.session_state.get("connected_sources") or {}

for src in SOURCES:
    k           = src["key"]
    is_connected = connected.get(k, False)
    card_cls    = "ff-source-card ff-source-connected" if is_connected else "ff-source-card"
    status_html = (
        '<span class="ff-source-status" style="color:#16A34A;">Connected</span>'
        if is_connected
        else '<span class="ff-source-status" style="color:#D1D5DB;">Not connected</span>'
    )

    col_card, col_btn = st.columns([5.5, 1])
    with col_card:
        st.markdown(f"""
<div class="{card_cls}">
  <div class="ff-source-icon">{src['icon']}</div>
  <div class="ff-source-body">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
      <p class="ff-source-name">{src['label']}</p>
      {status_html}
    </div>
    <p class="ff-source-desc">{src['desc']}</p>
    <div class="ff-source-note"><strong>Production equivalent:</strong> {src['note']}</div>
  </div>
</div>""", unsafe_allow_html=True)

    with col_btn:
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        if is_connected:
            if st.button("Disconnect", key=f"disc_{k}", use_container_width=True):
                connected[k] = False
                st.session_state["connected_sources"] = connected
                st.session_state["passport"] = None
                st.rerun()
        else:
            if st.button("Connect", key=f"conn_{k}", use_container_width=True, type="primary"):
                connected[k] = True
                st.session_state["connected_sources"] = connected
                st.rerun()

# ── Status footer ─────────────────────────────────────────────────────────────
n = sum(1 for v in connected.values() if v)
st.markdown("---")

if n == 4:
    st.session_state["data_connected"] = True
    st.markdown("""
<div class="ff-alert-green">
  All four sources connected. Proceed to <strong>Scoring</strong>.
</div>""", unsafe_allow_html=True)
elif n == 0:
    st.markdown("""
<div class="ff-note">
  Connect all four sources to proceed. Each source contributes to a different
  dimension of the credit assessment.
</div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""
<div class="ff-alert-amber">
  {n} of 4 sources connected. All four are required for a complete assessment.
</div>""", unsafe_allow_html=True)
