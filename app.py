"""
ForkFund — Restaurant Credit Passport Platform
Entry point for the Streamlit multi-page application.
"""

import streamlit as st

st.set_page_config(
    page_title="ForkFund",
    page_icon="🍴",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("ForkFund")
st.subheader("Restaurant Credit Intelligence Platform")

st.markdown(
    """
    Welcome to **ForkFund** — a B2B credit-intelligence platform that helps restaurants
    build a verified **Credit Passport** and connect with suitable lenders.

    ---

    ### How it works

    | Step | Page | What happens |
    |------|------|-------------|
    | 1 | Onboarding | Register your restaurant |
    | 2 | Data Connection | Connect simulated PSD2, POS, and accounting data |
    | 3 | Scoring | Generate your explainable credit score |
    | 4 | Credit Passport | View your full Restaurant Credit Passport |
    | 5 | Lender Dashboard | Match with lenders based on your profile |
    | 6 | Methodology | Understand how scoring and data work |

    ---

    > **Disclaimer:** ForkFund is a prototype MVP using entirely synthetic data.
    > It does not perform real underwriting, provide financial advice, or connect
    > to any live banking, POS, or government systems.

    Use the sidebar to navigate between steps.
    """
)
