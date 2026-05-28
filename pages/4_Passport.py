"""Step 4 — Restaurant Credit Passport display."""

import streamlit as st

st.set_page_config(page_title="Credit Passport — ForkFund", layout="wide")

st.title("Restaurant Credit Passport")
st.caption("Step 4 of 6 — Your verified credit profile")

st.info(
    "This passport is generated from synthetic data for demonstration purposes only.",
    icon="ℹ️",
)

st.markdown("---")

# TODO: Replace with real call to src.passport.generator once implemented.

st.subheader("Restaurant Profile")
st.markdown("_Restaurant details will appear here after onboarding._")

st.subheader("Credit Summary")
st.markdown("_Overall score, grade, and risk band will appear here._")

st.subheader("Data Sources Used")
st.markdown("_Connected data sources and their contribution will appear here._")

st.subheader("Score Breakdown")
st.markdown("_Sub-score chart will appear here._")

st.subheader("Lender Eligibility Summary")
st.markdown("_High-level eligibility summary will appear here._")

st.download_button(
    label="Download Passport (JSON)",
    data="{}",
    file_name="credit_passport.json",
    mime="application/json",
    disabled=True,
)
