# ForkFund — User Flow

## Actors

- **Restaurant owner** — the primary user navigating the MVP.
- **Lender** — passive; represented only as reference data, not a live actor.

## Step-by-step flow

```
1. Onboarding (pages/1_Onboarding.py)
   └── Restaurant owner fills in name, cuisine, city, seats, KvK number, loan request.
   └── Data stored in st.session_state["restaurant"].

2. Data Connection (pages/2_Data_Connection.py)
   └── Owner clicks "Connect" for each data source (PSD2, POS, Accounting, KvK).
   └── Each click simulates an OAuth/consent flow (no real network call).
   └── Connected sources stored in st.session_state["connected_sources"].

3. Scoring (pages/3_Scoring.py)
   └── src/connectors/ loads CSV data for a matched synthetic restaurant.
   └── src/standardization/normalizer.py converts to unified schema.
   └── src/scoring/engine.py computes composite score and sub-scores.
   └── src/scoring/explainer.py generates narratives.
   └── ScoreResult stored in st.session_state["score_result"].

4. Credit Passport (pages/4_Passport.py)
   └── src/passport/generator.py assembles CreditPassport.
   └── Passport displayed with score gauge, sub-score chart, data source summary.
   └── JSON download available.
   └── Passport stored in st.session_state["passport"].

5. Lender Dashboard (pages/5_Lender_Dashboard.py)
   └── src/lender/filters.py loads lenders.csv and filters by score, amount, purpose.
   └── Matched lenders displayed as cards and comparison table.

6. Methodology (pages/6_Methodology.py)
   └── Static informational page. No session state required.
```

## Session state lifecycle

Session state is lost on page refresh. There is no persistence layer.
The flow assumes the user navigates pages in order within a single session.
