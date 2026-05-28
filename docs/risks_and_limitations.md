# ForkFund — Risks and Limitations

## Product scope

ForkFund is a student prototype. It demonstrates a concept, not a production system.
The following limitations are intentional and must be understood before extending the MVP.

---

## Data risks

| Risk | Detail |
|------|--------|
| No real data | All restaurant, transaction, and lender data is synthetic. Results have zero predictive validity. |
| No data persistence | Session state is lost on refresh. There is no database. |
| Synthetic distributions | Generated data approximates plausible statistics but is not calibrated to real Dutch restaurant industry benchmarks. |
| No outlier handling | The scoring model does not handle extreme or adversarial inputs gracefully. |

---

## Scoring model risks

| Risk | Detail |
|------|--------|
| Unvalidated weights | Score weights (25/25/20/15/15) are illustrative. They are not derived from historical default or repayment data. |
| No backtesting | The model has never been tested against real credit outcomes. |
| Oversimplification | Five dimensions cannot capture the full complexity of restaurant creditworthiness. |
| No dynamic adjustment | Weights are hard-coded. A production model would learn from outcomes. |
| Grade thresholds are arbitrary | A/B/C/D/F cutoffs were chosen for readability, not statistical significance. |

---

## Regulatory and legal risks

| Risk | Detail |
|------|--------|
| Not a regulated product | ForkFund is not licensed as a credit intermediary or financial advisor. |
| GDPR exposure (if real data used) | Any transition to real data would require a full GDPR compliance review. |
| EU AI Act | A production credit-scoring system would likely be classified as high-risk AI under Article 6. |
| Right to explanation | GDPR Article 22 requires meaningful explanation for automated credit decisions. ForkFund's explainer is a simplified approximation. |
| PSD2 access requirements | Real open-banking access requires TPP registration with a national regulator. |

---

## Technical risks

| Risk | Detail |
|------|--------|
| No authentication | Anyone with access to the URL can use the app. |
| No input validation | The onboarding form does minimal validation. Malformed inputs may cause errors. |
| Session-only state | Refreshing the page resets all progress. |
| Performance at scale | Transaction and POS CSV files grow large (~500k+ rows). Pandas operations may be slow without caching. |
| No error handling | Most `src/` functions raise `NotImplementedError` until implemented. |

---

## What would need to change for a production version

1. Replace synthetic data with real, consented, GDPR-compliant data pipelines.
2. Obtain TPP registration to access real PSD2/open-banking APIs.
3. Conduct actuarial validation of the scoring model against historical default data.
4. Implement authentication, audit logging, and role-based access.
5. Commission a legal review covering credit intermediation, GDPR, and the EU AI Act.
6. Add a proper persistence layer (database) and session management.
7. Submit to external security review before handling real financial data.
