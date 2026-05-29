# ForkFund — Data Model

All field definitions are canonical in `data/schemas/unified_schema.md`.
This document describes relationships, generation rules, and data quality assumptions.

## Entity relationships

```
Restaurant (1) ──< Transactions (many)   [restaurant_id]
Restaurant (1) ──< POS Records (many)    [restaurant_id]
Restaurant (1) ──< Accounting (many)     [restaurant_id, year]
Lenders (independent reference table)
```

## Generation parameters (data_generator.py)

| Parameter | Value |
|-----------|-------|
| Number of restaurants | 120 |
| Transaction history | 12 months |
| POS history | 12 months |
| Accounting years | 3 years |
| Number of lenders | 10 |
| Random seed | 42 |

## Data quality assumptions

- All amounts are in euros (no currency conversion needed).
- Dates are ISO-8601 strings in CSV files.
- `restaurant_id` is the join key across all tables.
- No missing values in generated data (NaN handling is a normaliser concern for real data).
- Synthetic data follows realistic statistical distributions but is not calibrated to actual Dutch restaurant industry benchmarks.
