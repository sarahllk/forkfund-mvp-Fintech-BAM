# ForkFund — Architecture

## Overview

ForkFund is a single-process Streamlit application. There is no backend server,
no database, and no external network calls. All state is held in Streamlit session state
for the duration of a browser session.

```
Browser
  └── Streamlit (app.py + pages/)
        └── src/
              ├── connectors/        reads from data/synthetic/ CSVs
              ├── standardization/   normalises connector output
              ├── scoring/           computes credit score
              ├── passport/          assembles Credit Passport
              └── lender/            filters lenders from CSV
```

## Module responsibilities

### `src/connectors/`
Each connector simulates reading from a specific external data source. Functions
accept a `restaurant_id` and return a `pd.DataFrame` (or `pd.Series` for KvK).
Connectors must not contain scoring or normalisation logic.

### `src/standardization/normalizer.py`
Single module that converts raw connector output to the unified schema defined in
`data/schemas/unified_schema.md`. This is the only place where column renaming,
type casting, and missing-value handling occurs.

### `src/scoring/engine.py`
Computes a composite 0–100 credit score from a standardised data dict. Returns a
`ScoreResult` dataclass. Contains score weights and grade/risk-band thresholds.

### `src/scoring/explainer.py`
Takes a `ScoreResult` and generates human-readable narrative per sub-score and an
overall summary. Has no scoring logic of its own.

### `src/passport/generator.py`
Assembles the final `CreditPassport` dataclass from a restaurant dict, a
`ScoreResult`, explanations, and lender eligibility flags. Can serialise to JSON.

### `src/lender/filters.py`
Loads `data/synthetic/lenders.csv` and filters/ranks rows against the restaurant's
score, loan amount, and purpose.

### `src/utils/data_generator.py`
Standalone script that generates all synthetic CSV files. Run once before starting
the app or whenever fresh data is needed.

### `src/utils/helpers.py`
Pure utility functions (clamp, formatting, colour mapping). No side effects.

## Data flow

```
data_generator.py
      │ writes
      ▼
data/synthetic/*.csv
      │ read by
      ▼
connectors/*.py  →  normalizer.py  →  engine.py  →  explainer.py
                                            │
                                            ▼
                                     generator.py  →  CreditPassport
                                                           │
                                                     filters.py (lenders)
```

## State management

Streamlit session state keys used across pages:

| Key | Type | Set in | Used in |
|-----|------|--------|---------|
| `restaurant` | dict | Page 1 | Pages 2–5 |
| `connected_sources` | dict | Page 2 | Pages 3–5 |
| `score_result` | ScoreResult | Page 3 | Pages 4–5 |
| `passport` | CreditPassport | Page 4 | Page 5 |
