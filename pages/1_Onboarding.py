"""Step 1 — Restaurant onboarding and registration."""

import streamlit as st

st.set_page_config(page_title="Onboarding — ForkFund", layout="wide")

st.title("Restaurant Onboarding")
st.caption("Step 1 of 6 — Register your restaurant")

st.markdown("---")

with st.form("onboarding_form"):
    st.subheader("Basic Information")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Restaurant name *")
        cuisine = st.selectbox(
            "Cuisine type *",
            ["Italian", "Asian", "Burger & Grill", "Pizza", "Sushi",
             "Mexican", "Middle Eastern", "French", "Bakery & Café", "Other"],
        )
        founding_year = st.number_input(
            "Year founded *", min_value=1950, max_value=2025, value=2018
        )
    with col2:
        city = st.text_input("City *")
        seats = st.number_input("Number of seats *", min_value=1, max_value=1000, value=40)
        kvk_number = st.text_input("KvK number (simulated) *")

    st.subheader("Financing Request")
    col3, col4 = st.columns(2)
    with col3:
        loan_amount = st.number_input(
            "Requested loan amount (€) *", min_value=5_000, max_value=500_000,
            step=5_000, value=50_000
        )
    with col4:
        loan_purpose = st.selectbox(
            "Purpose *",
            ["Equipment purchase", "Renovation", "Working capital",
             "Expansion", "Inventory", "Other"],
        )

    submitted = st.form_submit_button("Continue to Data Connection →")

if submitted:
    if not name or not city or not kvk_number:
        st.error("Please fill in all required fields.")
    else:
        st.session_state["restaurant"] = {
            "name": name,
            "cuisine": cuisine,
            "founding_year": founding_year,
            "city": city,
            "seats": seats,
            "kvk_number": kvk_number,
            "loan_amount": loan_amount,
            "loan_purpose": loan_purpose,
        }
        st.success(f"Registered **{name}**. Continue to Step 2 in the sidebar.")
