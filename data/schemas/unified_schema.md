# ForkFund — Unified Schema

All connector output is normalised to these canonical fields before scoring.

---

## Restaurant (from KvK connector)

| Field | Type | Description |
|-------|------|-------------|
| `restaurant_id` | string | Internal identifier (e.g. R0001) |
| `legal_name` | string | Registered business name |
| `cuisine_type` | string | Cuisine category |
| `city` | string | City of operation |
| `legal_form` | string | BV / VOF / Eenmanszaak / CV |
| `kvk_number` | string | 8-digit KvK registration number |
| `sbi_code` | string | SBI activity code |
| `registration_date` | date | Date of KvK registration |
| `is_active` | bool | Whether the company is currently active |
| `seats` | int | Number of restaurant seats |
| `loan_amount_requested_eur` | float | Requested financing amount |
| `loan_purpose` | string | Purpose of the loan |

---

## Transactions (from PSD2 connector)

| Field | Type | Description |
|-------|------|-------------|
| `restaurant_id` | string | FK to restaurant |
| `date` | date | Transaction date |
| `amount_eur` | float | Absolute amount in euros |
| `direction` | string | `credit` or `debit` |
| `category` | string | Transaction category label |
| `description` | string | Free-text description |

---

## POS Records (from POS connector)

| Field | Type | Description |
|-------|------|-------------|
| `restaurant_id` | string | FK to restaurant |
| `date` | date | Record date |
| `covers` | int | Number of guests served |
| `gross_revenue_eur` | float | Revenue before discounts/VAT |
| `net_revenue_eur` | float | Revenue after discounts/VAT |
| `avg_spend_eur` | float | Average spend per cover |

---

## Accounting (from accounting connector)

| Field | Type | Description |
|-------|------|-------------|
| `restaurant_id` | string | FK to restaurant |
| `year` | int | Financial year |
| `total_revenue_eur` | float | Annual gross revenue |
| `total_costs_eur` | float | Total operating costs |
| `ebitda_eur` | float | EBITDA |
| `net_profit_eur` | float | Net profit after tax |
| `total_debt_eur` | float | Total outstanding debt |
| `total_assets_eur` | float | Total asset value |

---

## Lenders

| Field | Type | Description |
|-------|------|-------------|
| `lender_id` | string | Internal identifier (e.g. L01) |
| `name` | string | Fictional lender name |
| `min_score` | int | Minimum credit score required |
| `max_loan_eur` | float | Maximum loan amount offered |
| `min_loan_eur` | float | Minimum loan amount offered |
| `interest_rate_pct` | float | Indicative interest rate |
| `max_term_months` | int | Maximum loan term |
| `supported_purposes` | string | Pipe-separated list of supported purposes |
| `focus` | string | Lender market focus description |
