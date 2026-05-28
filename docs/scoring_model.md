# ForkFund — Scoring Model

## Composite score

The composite credit score is a weighted average of five sub-scores, each in [0, 100].

| Dimension | Weight | Primary data source |
|-----------|--------|-------------------|
| Revenue stability | 25 % | PSD2 + POS |
| Cash flow health | 25 % | PSD2 |
| Debt-to-revenue ratio | 20 % | Accounting |
| Business longevity | 15 % | KvK |
| KvK compliance | 15 % | KvK |

## Sub-score definitions

### Revenue stability (25 %)
Measures consistency of monthly revenue over the last 24 months.
- Input: monthly net revenue from PSD2 credits and POS net_revenue_eur
- Method: 100 × (1 − coefficient_of_variation), clamped to [0, 100]

### Cash flow health (25 %)
Measures the ratio of credit to debit transactions.
- Input: total credits and total debits from PSD2 transactions
- Method: 100 × (total_credits / (total_credits + total_debits)), clamped to [0, 100]

### Debt-to-revenue ratio (20 %)
Measures debt load relative to annual revenue.
- Input: total_debt_eur and total_revenue_eur from most recent accounting year
- Method: 100 × (1 − min(debt/revenue, 1))

### Business longevity (15 %)
Rewards established businesses.
- Input: registration_date from KvK
- Method: 100 × min(years_in_business / 10, 1)

### KvK compliance (15 %)
Binary check that the KvK registration is active.
- Input: is_active from KvK
- Method: 100 if active, 0 if inactive

## Grades and risk bands

| Score | Grade | Risk band |
|-------|-------|-----------|
| 80–100 | A | Low |
| 65–79 | B | Low |
| 50–64 | C | Medium |
| 35–49 | D | High |
| 0–34 | F | Very High |

## Important caveats

- Weights are illustrative starting values, not derived from historical default data.
- The model has not been backtested or validated.
- All input data is synthetic — scores have no real predictive validity.
