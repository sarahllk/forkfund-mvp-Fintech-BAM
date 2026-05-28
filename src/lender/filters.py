"""Filters and ranks lenders against a restaurant's credit profile.

All filtering is deterministic and rule-based. No ranking algorithm or
matching score is applied — only hard criteria stated by the lender.
"""

from pathlib import Path

import pandas as pd

_CSV = Path("data/synthetic/lenders.csv")


def load_lenders() -> pd.DataFrame:
    """Return the full lenders reference table."""
    return pd.read_csv(_CSV)


def filter_lenders(
    lenders: pd.DataFrame,
    score: float,
    loan_amount: float,
    loan_purpose: str,
) -> pd.DataFrame:
    """Return lenders whose stated criteria the restaurant meets.

    Criteria applied (all must pass):
        min_score       <= score
        min_loan_eur    <= loan_amount
        max_loan_eur    >= loan_amount
        loan_purpose  in supported_purposes
    """
    df = lenders.copy()
    df = df[df["min_score"] <= score]
    df = df[(df["min_loan_eur"] <= loan_amount) & (df["max_loan_eur"] >= loan_amount)]
    df = df[df["supported_purposes"].str.contains(loan_purpose, na=False, regex=False)]
    return df.reset_index(drop=True)


def explain_exclusions(
    lenders: pd.DataFrame,
    score: float,
    loan_amount: float,
    loan_purpose: str,
) -> list[dict]:
    """Return an exclusion reason for each lender that did not pass all criteria.

    Each dict has keys: "lender" (str) and "reasons" (list[str]).
    Lenders that pass all criteria are not included.
    """
    results = []
    for _, row in lenders.iterrows():
        reasons = []
        if row["min_score"] > score:
            reasons.append(
                f"Score {score:.0f} is below this lender's minimum of {row['min_score']}"
            )
        if loan_amount < row["min_loan_eur"]:
            reasons.append(
                f"Requested amount €{loan_amount:,.0f} is below "
                f"the minimum of €{row['min_loan_eur']:,.0f}"
            )
        if loan_amount > row["max_loan_eur"]:
            reasons.append(
                f"Requested amount €{loan_amount:,.0f} exceeds "
                f"the maximum of €{row['max_loan_eur']:,.0f}"
            )
        if loan_purpose not in str(row["supported_purposes"]):
            reasons.append(
                f"Loan purpose '{loan_purpose}' is not in this lender's supported products"
            )
        if reasons:
            results.append({"lender": row["name"], "reasons": reasons})
    return results


def rank_lenders(matched: pd.DataFrame, score: float) -> pd.DataFrame:
    """Sort matched lenders: interest rate ascending, score headroom descending.

    Score headroom = how far the restaurant's score exceeds the lender's minimum.
    Higher headroom indicates more comfortable eligibility.
    """
    if matched.empty:
        return matched
    df = matched.copy()
    df["_headroom"] = score - df["min_score"]
    return (
        df.sort_values(["interest_rate_pct", "_headroom"], ascending=[True, False])
        .drop(columns=["_headroom"])
        .reset_index(drop=True)
    )
