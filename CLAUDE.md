# ForkFund — Claude Code Context

## What this project is

ForkFund is a student FinTech MVP (B2B credit-intelligence platform for restaurant financing).
It is **not** a lender, crowdfunding platform, investment platform, or real underwriting system.

The MVP flow:
restaurant onboarding → simulated data connection → data standardization → explainable scoring
→ Restaurant Credit Passport → lender filtering and decision support

## Tech stack

- Python 3.11+
- Streamlit (multi-page app, `pages/` directory)
- pandas, numpy, plotly
- Local CSV files only — no databases, no external APIs
- pytest for tests

## Repository layout

```
app.py                  Streamlit entry point
pages/                  One file per step in the user flow (auto-discovered by Streamlit)
src/                    All business logic — zero Streamlit imports inside src/
  connectors/           Simulated PSD2, POS, accounting, KvK data loaders
  standardization/      Maps raw connector output to the unified schema
  scoring/              Weighted credit scoring engine + explainability
  passport/             Assembles the Restaurant Credit Passport dict
  lender/               Filters lenders against a restaurant's score/profile
  utils/                Shared helpers and the synthetic data generator
data/synthetic/         Generated CSV files (committed — entirely synthetic)
data/schemas/           Field glossary and unified schema spec
docs/                   Human-readable architecture and methodology docs
tests/                  pytest unit tests (src/ only, no Streamlit)
```

## Hard constraints

- No API keys, no secrets, no .env committed (only .env.example with placeholders)
- No real banking, POS, or government API calls
- No Docker, no cloud infra, no authentication layer
- All restaurant and transaction data is synthetically generated

## Coding conventions

- Business logic lives in `src/`; Streamlit UI lives in `pages/`
- Each connector returns a pandas DataFrame with a documented schema
- `src/standardization/normalizer.py` is the single place that converts raw → unified
- Score is always in range 0–100; sub-scores are always 0–100
- No comments explaining *what* code does — only *why* when non-obvious
- No multi-paragraph docstrings; one-line module/function descriptions max

## Running the app

```bash
streamlit run app.py
```

## Running tests

```bash
pytest tests/
```

## Generating synthetic data

```bash
python -m src.utils.data_generator
```
