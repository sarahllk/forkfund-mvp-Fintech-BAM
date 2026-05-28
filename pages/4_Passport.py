"""Step 4 — Restaurant Credit Passport."""

import streamlit as st

from src.connectors.accounting import load_accounting
from src.connectors.kvk import load_kvk
from src.connectors.pos import load_pos_records
from src.connectors.psd2 import load_transactions
from src.passport.generator import generate, to_json
from src.scoring.engine import compute_score
from src.scoring.explainer import explain
from src.standardization.normalizer import (
    normalize_accounting, normalize_kvk, normalize_pos, normalize_transactions,
)
from src.demo.scenarios import SCENARIOS, scenario_ids
from pages.components.passport_card import render_passport
from pages.components.scenario_panel import render_scenario_panel
from pages.components.progress_bar import render_progress
from pages.components.shared_styles import inject_shared_styles, render_empty_state, render_session_banner

st.set_page_config(page_title="Credit Passport — ForkFund", layout="wide")
inject_shared_styles()

st.title("Credit Passport")
render_progress(4)
render_session_banner()


@st.cache_data(show_spinner=False)
def _build(rid: str):
    txn = normalize_transactions(load_transactions(rid))
    pos = normalize_pos(load_pos_records(rid))
    acc = normalize_accounting(load_accounting(rid))
    kvk = normalize_kvk(load_kvk(rid))
    sr  = compute_score({"transactions": txn, "pos": pos, "accounting": acc, "kvk": kvk})
    expl = explain(sr)
    return generate(restaurant=kvk, score_result=sr, explanations=expl, accounting=acc, pos=pos), expl


# ── Resolve source: session state or demo fallback ────────────────────────────
session_id = st.session_state.get("restaurant_id")
scenario   = st.session_state.get("scenario")
demo_mode  = not bool(session_id)

if demo_mode:
    st.markdown("""
<div class="ff-note" style="margin-bottom:14px;">
  No active session. Choose a scenario below, or start from
  <strong>Step 1 — Onboarding</strong> for the full guided workflow.
</div>""", unsafe_allow_html=True)

    ids    = scenario_ids()
    sel_id = st.selectbox(
        "Select a scenario",
        ids,
        format_func=lambda k: SCENARIOS[k]["label"],
        label_visibility="collapsed",
    )
    restaurant_id = sel_id
    scenario      = SCENARIOS.get(sel_id)
else:
    restaurant_id = session_id

    # Use pre-computed passport from session if available
    cached_passport     = st.session_state.get("passport")
    cached_explanations = st.session_state.get("explanations")
    if cached_passport and cached_explanations:
        _passport_data = (cached_passport, cached_explanations)
    else:
        _passport_data = None

st.markdown("---")

# ── Build passport ────────────────────────────────────────────────────────────
with st.spinner("Preparing passport…"):
    try:
        if demo_mode or not st.session_state.get("passport"):
            passport, explanations = _build(restaurant_id)
        else:
            passport, explanations = (
                st.session_state["passport"],
                st.session_state["explanations"],
            )
    except Exception as e:
        st.error(f"Passport could not be generated: {e}")
        st.stop()

# ── Scenario panel (curated profiles only) ────────────────────────────────────
if scenario:
    render_scenario_panel(scenario)

# ── Passport card ─────────────────────────────────────────────────────────────
# Pass the scenario label as the primary display name when a curated scenario
# is active, so the header matches the scenario panel above it.
render_passport(
    passport,
    explanations,
    display_name=scenario["label"] if scenario else None,
)

# ── Download ──────────────────────────────────────────────────────────────────
safe_name = passport.profile.get("legal_name", "restaurant").lower().replace(" ", "_")[:28]
st.download_button(
    label="Download Passport (JSON)",
    data=to_json(passport),
    file_name=f"credit_passport_{safe_name}.json",
    mime="application/json",
)
