# ForkFund — Scoring Model

## Composite score

The composite credit score is a weighted average of seven sub-scores, each in [0, 100].

| Dimension | Weight | Primary data source |
|-----------|--------|-------------------|
| Revenue stability | 20 % | POS |
| Cash-flow strength | 20 % | PSD2 |
| Debt burden | 15 % | Accounting |
| Repayment capacity | 15 % | Accounting |
| Cost structure | 10 % | Accounting |
| Business maturity | 10 % | KvK |
| Data completeness | 10 % | All sources |

## Sub-score definitions

### Revenue stability (20 %)
Measures consistency of monthly net revenue across the review period.
- Input: daily POS records aggregated to monthly net revenue
- Method: 100 × (1 − coefficient_of_variation), clamped to [0, 100]
- Requires: ≥ 3 months of POS data; returns 50 if fewer months are present

### Cash-flow strength (20 %)
Measures the net operating margin implied by PSD2 transaction inflows and outflows.
- Input: total credits and total debits from PSD2 transactions
- Method: 100 × (net_inflow / total_credits) / 0.30, clamped to [0, 100]
- Benchmark: a 30 % net inflow margin maps to a score of 100

### Debt burden (15 %)
Measures total debt relative to annual revenue from the most recent accounting year.
- Input: total_debt_eur and total_revenue_eur (most recent year)
- Method: 100 × (1 − min(debt / revenue, 1)), clamped to [0, 100]
- Default: 50 when no accounting data is present

### Repayment capacity (15 %)
Measures EBITDA margin from the most recent accounting year.
- Input: ebitda_eur and total_revenue_eur (most recent year)
- Method: 100 × (EBITDA / revenue) / 0.30, clamped to [0, 100]
- Benchmark: a 30 % EBITDA margin maps to a score of 100
- Default: 50 when no accounting data is present

### Cost structure (10 %)
Measures operating cost ratio from the most recent accounting year.
- Input: total_costs_eur and total_revenue_eur (most recent year)
- Method: 100 × (0.85 − cost_ratio) / 0.40, clamped to [0, 100]
- Benchmarks: 45 % cost ratio → 100 (efficient); 85 % cost ratio → 0 (unsustainable)
- Default: 50 when no accounting data is present

### Business maturity (10 %)
Measures years since KvK registration, normalised to a 10-year ceiling.
- Input: registration_date and is_active from KvK
- Method: 100 × min(years_since_registration / 10, 1)
- Penalty: score multiplied by 0.5 if KvK registration is inactive
- Returns: 0 when no KvK data is present

### Data completeness (10 %)
Measures the fraction of the four expected data sources that are populated.
- Input: presence of transactions, POS records, accounting, and KvK data
- Method: 100 × (populated_sources / 4)

## Grades and risk bands

Grades and risk bands are computed independently from the same composite score.

| Score | Grade |
|-------|-------|
| ≥ 80 | A |
| 65 – 79 | B |
| 50 – 64 | C |
| 35 – 49 | D |
| < 35 | F |

| Score | Risk band |
|-------|-----------|
| ≥ 70 | Low |
| 50 – 69 | Medium |
| 30 – 49 | High |
| < 30 | Very High |

## Important caveats

- Weights are illustrative starting values, not derived from historical default data.
- The model has not been backtested or validated.
- All input data is synthetic — scores have no real predictive validity.
