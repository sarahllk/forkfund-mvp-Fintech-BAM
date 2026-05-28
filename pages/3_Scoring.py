"""Step 3 — Credit score computation and explainability."""

import streamlit as st

st.set_page_config(page_title="Scoring — ForkFund", layout="wide")

st.title("Credit Scoring")
st.caption("Step 3 of 6 — Explainable credit score")

st.info(
    "Scores are computed from synthetic data and are for demonstration only. "
    "This is not a real credit assessment.",
    icon="ℹ️",
)

st.markdown("---")

# TODO: Replace with real calls to src.scoring.engine and src.scoring.explainer
# once those modules are implemented.

st.subheader("Score Overview")
st.markdown("_Score computation will appear here once scoring engine is wired up._")

st.subheader("Sub-score Breakdown")
st.markdown(
    """
    | Dimension | Weight | Score |
    |-----------|--------|-------|
    | Revenue stability | 25 % | — |
    | Cash flow health | 25 % | — |
    | Debt-to-revenue ratio | 20 % | — |
    | Business longevity | 15 % | — |
    | KvK compliance | 15 % | — |
    """
)

st.subheader("Score Explanation")
st.markdown("_Narrative explanation of the score will appear here._")
