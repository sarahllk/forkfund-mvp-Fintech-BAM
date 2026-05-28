"""
Lightweight Plotly chart helpers for ForkFund.

All charts share a consistent institutional aesthetic: no animations,
muted gridlines, FF colour palette. Call inject_chart_styles() once per
page before rendering charts.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.scoring.engine import ScoreResult

# ── Shared chart config ───────────────────────────────────────────────────────

_CHART_FONT = dict(family="Inter, system-ui, sans-serif", size=11, color="#4B5563")

_LAYOUT_DEFAULTS = dict(
    font=_CHART_FONT,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False,
)

_AXIS_DEFAULTS = dict(
    showgrid=False,
    zeroline=False,
    showline=False,
    tickfont=_CHART_FONT,
)

_CONFIG = dict(
    displayModeBar=False,
    staticPlot=True,       # no hover, no toolbar — pure display
)

_BAR_COLORS = {
    "high":   "#16A34A",
    "mid":    "#D97706",
    "low":    "#DC2626",
}

_DIMENSION_LABELS = {
    "revenue_stability":  "Revenue Stability",
    "cash_flow_strength": "Cash-Flow Strength",
    "debt_burden":        "Debt Burden",
    "repayment_capacity": "Repayment Capacity",
    "cost_structure":     "Cost Structure",
    "business_maturity":  "Business Maturity",
}


def _bar_color(score: float) -> str:
    if score >= 70:
        return _BAR_COLORS["high"]
    if score >= 50:
        return _BAR_COLORS["mid"]
    return _BAR_COLORS["low"]


def _axis(**overrides) -> dict:
    """Merge _AXIS_DEFAULTS with caller overrides using dict-literal syntax.

    dict(**_AXIS_DEFAULTS, key=val) raises TypeError when key already exists in
    _AXIS_DEFAULTS.  {**_AXIS_DEFAULTS, **overrides} handles duplicates correctly
    (last value wins) and is safe in all Python 3 versions.
    """
    return {**_AXIS_DEFAULTS, **overrides}


# ── Sub-score bar chart ───────────────────────────────────────────────────────

def render_subscore_chart(score_result: ScoreResult, height: int = 230) -> None:
    """Horizontal bar chart of the 6 scored dimensions (excludes data_completeness)."""
    dims = {k: v for k, v in score_result.sub_scores.items() if k != "data_completeness"}
    labels = [_DIMENSION_LABELS.get(k, k) for k in reversed(dims)]
    scores = list(reversed(list(dims.values())))
    colors = [_bar_color(s) for s in scores]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=scores,
        y=labels,
        orientation="h",
        marker=dict(color=colors, cornerradius=3),
        text=[f"{s:.0f}" for s in scores],
        textposition="outside",
        textfont=dict(size=11, color="#374151"),
        cliponaxis=False,
    ))

    # Faint benchmark line at 70
    fig.add_vline(x=70, line_dash="dot", line_color="#D1D5DB", line_width=1)

    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        height=height,
        xaxis=_axis(range=[0, 115], tickvals=[0, 25, 50, 70, 100],
                   ticktext=["0", "25", "50", "70", "100"]),
        yaxis=_axis(tickfont=dict(size=11, color="#374151")),
        bargap=0.28,
    )

    st.plotly_chart(fig, use_container_width=True, config=_CONFIG)


# ── Monthly revenue trend chart ───────────────────────────────────────────────

def render_revenue_trend(pos: pd.DataFrame, height: int = 170) -> None:
    """Monthly net revenue line chart over the available POS history."""
    if pos.empty:
        st.caption("No POS data available for revenue trend.")
        return

    monthly = (
        pos.assign(month=pos["date"].dt.to_period("M"))
        .groupby("month")["net_revenue_eur"]
        .sum()
        .reset_index()
    )
    monthly["month_str"] = monthly["month"].astype(str)

    # Last 12 months only to keep the chart readable
    monthly = monthly.tail(12)

    # Compute a simple 3-month rolling mean for the trend line
    monthly["rolling"] = monthly["net_revenue_eur"].rolling(3, min_periods=1).mean()

    fig = go.Figure()

    # Filled area under revenue bars
    fig.add_trace(go.Bar(
        x=monthly["month_str"],
        y=monthly["net_revenue_eur"],
        marker_color="#BFDBFE",
        marker_line_width=0,
        name="Monthly Revenue",
    ))

    # Trend line
    fig.add_trace(go.Scatter(
        x=monthly["month_str"],
        y=monthly["rolling"],
        mode="lines",
        line=dict(color="#2563EB", width=2),
        name="3-month trend",
    ))

    mean_rev = monthly["net_revenue_eur"].mean()
    fig.add_hline(y=mean_rev, line_dash="dot", line_color="#9CA3AF", line_width=1)

    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        height=height,
        xaxis=_axis(tickangle=-30, tickfont=dict(size=10, color="#9CA3AF")),
        yaxis=_axis(tickformat="€,.0f", tickfont=dict(size=10, color="#9CA3AF")),
        bargap=0.15,
    )

    st.plotly_chart(fig, use_container_width=True, config=_CONFIG)
