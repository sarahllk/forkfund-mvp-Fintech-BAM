"""Step 2 — Simulated data source connections (PSD2, POS, accounting, KvK)."""

import streamlit as st

st.set_page_config(page_title="Data Connection — ForkFund", layout="wide")

st.title("Data Connection")
st.caption("Step 2 of 6 — Connect your data sources")

st.info(
    "ForkFund uses **simulated** data connections. No real banking, POS, "
    "or government data is accessed. All data shown is synthetic.",
    icon="ℹ️",
)

st.markdown("---")

SOURCES = {
    "psd2": {
        "label": "Open Banking (PSD2)",
        "description": "Simulated bank account transactions for the last 24 months.",
        "icon": "🏦",
    },
    "pos": {
        "label": "POS System",
        "description": "Simulated daily revenue records from your point-of-sale system.",
        "icon": "🖨️",
    },
    "accounting": {
        "label": "Accounting / P&L",
        "description": "Simulated profit & loss statement and balance sheet data.",
        "icon": "📊",
    },
    "kvk": {
        "label": "KvK Registration",
        "description": "Simulated Dutch Chamber of Commerce company registration data.",
        "icon": "🏛️",
    },
}

connected = st.session_state.get("connected_sources", {})

for key, source in SOURCES.items():
    col1, col2, col3 = st.columns([1, 5, 2])
    with col1:
        st.markdown(f"### {source['icon']}")
    with col2:
        st.markdown(f"**{source['label']}**")
        st.caption(source["description"])
    with col3:
        if connected.get(key):
            st.success("Connected", icon="✓")
        else:
            if st.button(f"Connect {source['label']}", key=f"btn_{key}"):
                connected[key] = True
                st.session_state["connected_sources"] = connected
                st.rerun()
    st.markdown("---")

if len(connected) == len(SOURCES):
    st.success("All data sources connected. Continue to Step 3 →")
