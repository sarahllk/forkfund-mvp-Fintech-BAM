# ForkFund

**B2B Credit Intelligence Platform for Restaurant Financing**

> Student FinTech MVP — synthetic data only — not a real financial product.

---

## What is ForkFund?

ForkFund helps restaurants build a **Restaurant Credit Passport**: a standardised, explainable
credit profile derived from simulated open-banking (PSD2), POS, accounting, and company-registration
(KvK) data. Lenders can use this passport to make faster, more transparent financing decisions.

### ForkFund is NOT:
- a lender
- a crowdfunding or investment platform
- a real underwriting system
- connected to any live financial or government data

### ForkFund IS:
Restaurant onboarding → simulated data connection → data standardisation →
explainable scoring → Credit Passport → lender filtering and decision support

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit (multi-page) |
| Logic | Python 3.11+ |
| Data | pandas, numpy |
| Charts | plotly |
| Storage | Local CSV files |
| Tests | pytest |

---

## Quick start

```bash
# 1. Clone the repo
git clone <repo-url>
cd forkfund-mvp-Fintech-BAM

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate synthetic data
python -m src.utils.data_generator

# 5. Run the app
streamlit run app.py
```

---

## User flow

1. **Onboarding** — register a restaurant (name, type, location, founding date)
2. **Data Connection** — simulate connecting PSD2, POS, accounting, and KvK data
3. **Scoring** — view the explainable credit score (0–100) with sub-score breakdown
4. **Credit Passport** — view and download the full Restaurant Credit Passport
5. **Lender Dashboard** — filter and compare matched lenders
6. **Methodology** — understand scoring logic, data sources, and legal boundaries

---

## Project structure

```
app.py                  Entry point
pages/                  Streamlit pages (one per flow step)
src/                    Business logic
  connectors/           Simulated data source adapters
  standardization/      Unified schema normaliser
  scoring/              Credit scoring engine + explainability
  passport/             Credit Passport assembler
  lender/               Lender filtering
  utils/                Helpers and synthetic data generator
data/synthetic/         Generated CSV datasets
data/schemas/           Field definitions
docs/                   Architecture and methodology documentation
tests/                  pytest unit tests
```

---

## Disclaimer

ForkFund is a student prototype built for educational and demonstration purposes.
It uses entirely synthetic, computer-generated data. It does not constitute financial
advice, real credit assessment, or any regulated financial service.
