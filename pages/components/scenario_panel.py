"""
Scenario context panel — shows a brief lender-oriented briefing
for a curated demo restaurant above the main passport card.
"""

from __future__ import annotations

import streamlit as st

from src.demo.scenarios import SCENARIO_TYPE_COLOR, SCENARIO_TYPE_LABEL

_CSS = """
<style>
.ff-scenario-wrap {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 14px;
    background: #FAFAFA;
}
.ff-scenario-type-tag {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.ff-scenario-title {
    font-size: 14px;
    font-weight: 700;
    color: #111827;
    margin: 0 0 3px 0;
}
.ff-scenario-tagline {
    font-size: 12px;
    color: #6B7280;
    margin: 0 0 12px 0;
}
.ff-scenario-body {
    font-size: 12px;
    color: #374151;
    line-height: 1.6;
    margin-bottom: 10px;
}
.ff-scenario-col-head {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #9CA3AF;
    margin-bottom: 5px;
}
.ff-scenario-col-body {
    font-size: 11.5px;
    color: #4B5563;
    line-height: 1.55;
}
.ff-focus-item {
    display: flex;
    gap: 6px;
    align-items: flex-start;
    padding: 2px 0;
    font-size: 11.5px;
    color: #4B5563;
    line-height: 1.45;
}
.ff-focus-dot {
    flex-shrink: 0;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #9CA3AF;
    margin-top: 5px;
}
</style>
"""


def render_scenario_panel(scenario: dict) -> None:
    """Render the scenario context panel for a curated demo restaurant."""
    st.markdown(_CSS, unsafe_allow_html=True)

    s_type  = scenario.get("scenario_type", "")
    color, bg = SCENARIO_TYPE_COLOR.get(s_type, ("#6B7280", "#F9FAFB"))
    type_label = SCENARIO_TYPE_LABEL.get(s_type, s_type.replace("_", " ").title())

    focus_items = "".join(
        f'<div class="ff-focus-item"><div class="ff-focus-dot"></div><span>{f}</span></div>'
        for f in scenario.get("lender_focus", [])
    )

    st.markdown(f"""
<div class="ff-scenario-wrap">
  <span class="ff-scenario-type-tag" style="background:{bg};color:{color};">{type_label}</span>
  <p class="ff-scenario-title">{scenario.get("label", "")}</p>
  <p class="ff-scenario-tagline">{scenario.get("tagline", "")}</p>

  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;margin-top:4px;">
    <div>
      <div class="ff-scenario-col-head">Context</div>
      <div class="ff-scenario-col-body">{scenario.get("context", "")}</div>
    </div>
    <div>
      <div class="ff-scenario-col-head">What lenders notice</div>
      <div class="ff-scenario-col-body">{scenario.get("lender_notice", "")}</div>
    </div>
    <div>
      <div class="ff-scenario-col-head">Key lender focus areas</div>
      {focus_items}
      <div style="margin-top:8px;" class="ff-scenario-col-head">Financing challenge</div>
      <div class="ff-scenario-col-body">{scenario.get("financing_challenge", "")}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)
