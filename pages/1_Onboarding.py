"""Step 1 — Choose a demo scenario or register a restaurant."""

import streamlit as st

from src.demo.scenarios import SCENARIOS, SCENARIO_TYPE_COLOR, SCENARIO_TYPE_LABEL, scenario_ids
from pages.components.progress_bar import render_progress
from pages.components.shared_styles import inject_shared_styles, GRADE_COLOR, GRADE_BG

st.set_page_config(page_title="Onboarding — ForkFund", layout="wide")
inject_shared_styles()

st.markdown("""
<style>
.ff-scenario-card {
  border:1.5px solid #E5E7EB; border-radius:8px; padding:16px 18px;
  background:#FFFFFF; height:100%; box-sizing:border-box;
}
.ff-scenario-card-selected { border-color:#1B2B4B; background:#F8FAFF; }
.ff-scenario-type-tag {
  display:inline-block; padding:2px 8px; border-radius:4px;
  font-size:10px; font-weight:700; letter-spacing:.07em;
  text-transform:uppercase; margin-bottom:6px;
}
.ff-scenario-name  { font-size:13px; font-weight:700; color:#111827; margin:0 0 4px; }
.ff-scenario-hint  { font-size:11.5px; color:#6B7280; line-height:1.5; margin:0; }
.ff-scenario-footer { margin-top:10px; display:flex; align-items:center; gap:6px; }
.ff-coming-soon {
  text-align:center; padding:40px 24px;
  border:1px solid #E5E7EB; border-radius:8px; background:#FAFAFA;
}
</style>
""", unsafe_allow_html=True)

st.title("Onboarding")
render_progress(1)

tab_demo, tab_custom = st.tabs(["Choose a Scenario", "Custom Entry"])

# ── Demo scenarios ────────────────────────────────────────────────────────────
with tab_demo:
    st.markdown(
        "Select one of six restaurant profiles. Each illustrates a distinct "
        "financing situation — from a straightforward equipment loan to an "
        "operationally distressed business seeking expansion capital.",
    )
    st.markdown("---")

    selected_id = st.session_state.get("restaurant_id")
    ids = scenario_ids()
    cols = st.columns(3)

    for i, rid in enumerate(ids):
        s = SCENARIOS[rid]
        color, bg = SCENARIO_TYPE_COLOR.get(s["scenario_type"], ("#6B7280", "#F3F4F6"))
        type_label = SCENARIO_TYPE_LABEL.get(s["scenario_type"], "")
        gh = s.get("grade_hint", "")
        gc = GRADE_COLOR.get(gh, "#6B7280")
        gb = GRADE_BG.get(gh, "#F3F4F6")
        is_selected = (rid == selected_id)
        card_cls = "ff-scenario-card ff-scenario-card-selected" if is_selected else "ff-scenario-card"

        with cols[i % 3]:
            st.markdown(f"""
<div class="{card_cls}">
  <span class="ff-scenario-type-tag" style="background:{bg};color:{color};">{type_label}</span>
  <p class="ff-scenario-name">{s['label']}</p>
  <p class="ff-scenario-hint">{s['tagline']}</p>
  <div class="ff-scenario-footer">
    <span style="background:{gb};color:{gc};padding:2px 8px;border-radius:4px;
         font-size:10.5px;font-weight:700;">Grade {gh}</span>
    <span style="font-size:11px;color:#9CA3AF;">{s.get('risk_hint','')} risk</span>
  </div>
</div>""", unsafe_allow_html=True)

            btn_label = "Selected ✓" if is_selected else "Select →"
            btn_type  = "primary" if is_selected else "secondary"
            if st.button(btn_label, key=f"sel_{rid}", use_container_width=True, type=btn_type):
                st.session_state["restaurant_id"] = rid
                st.session_state["scenario"]      = SCENARIOS[rid]
                # Clear downstream state so pages recompute
                for k in ("data_connected", "passport", "explanations"):
                    st.session_state[k] = None
                st.rerun()

    if selected_id and selected_id in SCENARIOS:
        st.markdown("---")
        s = SCENARIOS[selected_id]
        st.markdown(f"""
<div class="ff-alert-green">
  <strong>{s['label']}</strong> selected.
  Continue to <strong>Data Connection</strong> using the sidebar.
</div>""", unsafe_allow_html=True)

# ── Custom Entry ──────────────────────────────────────────────────────────────
with tab_custom:
    st.markdown("""
<div class="ff-coming-soon">
  <p style="font-size:22px;color:#D1D5DB;margin-bottom:12px;">⊘</p>
  <p style="font-size:14px;font-weight:600;color:#374151;margin-bottom:6px;">
    Custom entry is not available in this prototype
  </p>
  <p style="font-size:13px;color:#6B7280;line-height:1.6;max-width:420px;margin:0 auto;">
    Scoring and passport generation require a matched synthetic data record.
    Custom entry — connecting user-supplied data to the scoring pipeline —
    is a planned feature not yet implemented in this MVP.
  </p>
  <p style="font-size:12px;color:#9CA3AF;margin-top:16px;">
    Use the <strong>Choose a Scenario</strong> tab to proceed.
  </p>
</div>""", unsafe_allow_html=True)
