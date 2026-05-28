"""Step 5 — Lender filtering and decision-support dashboard."""

import streamlit as st

st.set_page_config(page_title="Lender Dashboard — ForkFund", layout="wide")

st.title("Lender Dashboard")
st.caption("Step 5 of 6 — Match with suitable lenders")

st.info(
    "All lenders shown are fictional and exist only for demonstration purposes.",
    icon="ℹ️",
)

st.markdown("---")

# TODO: Replace with real call to src.lender.filters once implemented.

st.subheader("Filter Lenders")

col1, col2, col3 = st.columns(3)
with col1:
    min_score = st.slider("Minimum credit score accepted", 0, 100, 50)
with col2:
    max_loan = st.number_input("Maximum loan amount needed (€)", value=100_000, step=10_000)
with col3:
    product_type = st.multiselect(
        "Loan product type",
        ["Term loan", "Revolving credit", "Equipment finance", "Working capital"],
        default=["Term loan"],
    )

st.subheader("Matched Lenders")
st.markdown("_Lender cards will appear here once the filter engine is wired up._")

st.subheader("Comparison Table")
st.markdown("_Side-by-side lender comparison will appear here._")
