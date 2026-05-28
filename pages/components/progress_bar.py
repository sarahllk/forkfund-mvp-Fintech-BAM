"""
Workflow progress indicator — lightweight 5-step stepper shown on every page.
"""

from __future__ import annotations

import streamlit as st

_STEPS = [
    (1, "Onboarding"),
    (2, "Data"),
    (3, "Scoring"),
    (4, "Passport"),
    (5, "Lender Review"),
]

_CSS = """
<style>
.ff-stepper {
  display:flex; align-items:flex-start;
  padding:10px 0 18px; gap:0;
}
.ff-step-col {
  display:flex; flex-direction:column; align-items:center;
  flex-shrink:0; width:78px;
}
.ff-step-dot {
  width:24px; height:24px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:10.5px; font-weight:700; margin-bottom:5px;
}
.ff-step-dot-done    { background:#F0FDF4; color:#16A34A; border:1.5px solid #BBF7D0; }
.ff-step-dot-current { background:#1B2B4B; color:#FFFFFF; }
.ff-step-dot-pending { background:#FFFFFF; color:#E5E7EB; border:1.5px solid #E5E7EB; }
.ff-step-lbl {
  font-size:9px; font-weight:600; text-align:center;
  letter-spacing:.05em; text-transform:uppercase; line-height:1.3;
}
.ff-step-lbl-done    { color:#9CA3AF; }
.ff-step-lbl-current { color:#111827; }
.ff-step-lbl-pending { color:#D1D5DB; }
.ff-step-line {
  flex:1; height:1.5px; margin:10px 2px 0; min-width:16px;
}
.ff-step-line-done    { background:#BBF7D0; }
.ff-step-line-pending { background:#E5E7EB; }
</style>
"""


def render_progress(current_step: int) -> None:
    """Render the 5-step workflow indicator. current_step is 1-indexed."""
    st.markdown(_CSS, unsafe_allow_html=True)

    parts: list[str] = ['<div class="ff-stepper">']

    for i, (n, label) in enumerate(_STEPS):
        if n < current_step:
            dot_cls = "ff-step-dot-done"
            lbl_cls = "ff-step-lbl-done"
            dot_content = "✓"
        elif n == current_step:
            dot_cls = "ff-step-dot-current"
            lbl_cls = "ff-step-lbl-current"
            dot_content = str(n)
        else:
            dot_cls = "ff-step-dot-pending"
            lbl_cls = "ff-step-lbl-pending"
            dot_content = str(n)

        parts.append(f"""
  <div class="ff-step-col">
    <div class="ff-step-dot {dot_cls}">{dot_content}</div>
    <span class="ff-step-lbl {lbl_cls}">{label}</span>
  </div>""")

        if i < len(_STEPS) - 1:
            line_cls = "ff-step-line-done" if n < current_step else "ff-step-line-pending"
            parts.append(f'  <div class="ff-step-line {line_cls}"></div>')

    parts.append("</div>")
    st.markdown("\n".join(parts), unsafe_allow_html=True)
