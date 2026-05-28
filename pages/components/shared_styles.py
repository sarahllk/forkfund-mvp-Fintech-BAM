"""
Shared CSS for all ForkFund pages.

Call inject_shared_styles() once at the top of each page.
The passport card (passport_card.py) has its own styles for its specialized elements.
"""

import streamlit as st

_CSS = """
<style>

/* ── Base cards ────────────────────────────────────────────────────── */
.ff-card {
  background:#FFFFFF; border:1px solid #E5E7EB; border-radius:8px;
  padding:18px 20px; margin-bottom:10px;
}
.ff-card-alt {
  background:#F9FAFB; border:1px solid #E5E7EB; border-radius:8px;
  padding:18px 20px; margin-bottom:10px;
}
.ff-card-inset {
  background:#F9FAFB; border:1px solid #F3F4F6; border-radius:6px;
  padding:12px 16px; margin-top:8px;
}

/* ── Section labels ────────────────────────────────────────────────── */
.ff-section-label {
  font-size:10px; font-weight:700; letter-spacing:.09em;
  text-transform:uppercase; color:#9CA3AF;
  display:block; margin-bottom:10px;
}

/* ── Grade and risk tags ───────────────────────────────────────────── */
.ff-grade-tag {
  display:inline-block; padding:2px 9px; border-radius:4px;
  font-size:11px; font-weight:700; margin-right:5px;
}
.ff-risk-tag {
  display:inline-block; padding:2px 9px; border-radius:4px;
  font-size:11px; font-weight:600;
}

/* ── Context strip ─────────────────────────────────────────────────── */
.ff-context-strip {
  background:#F9FAFB; border:1px solid #E5E7EB; border-radius:6px;
  padding:10px 16px; margin-bottom:16px;
  display:flex; gap:10px; align-items:center; flex-wrap:wrap;
}
.ff-context-name  { font-size:13px; font-weight:700; color:#111827; }
.ff-context-meta  { font-size:12px; color:#6B7280; }

/* ── Empty state ───────────────────────────────────────────────────── */
.ff-empty-state {
  text-align:center; padding:56px 24px;
  border:1px solid #E5E7EB; border-radius:8px; background:#FAFAFA;
}
.ff-empty-icon  { font-size:28px; color:#D1D5DB; margin-bottom:14px; }
.ff-empty-title { font-size:15px; font-weight:600; color:#374151; margin-bottom:6px; }
.ff-empty-body  { font-size:13px; color:#6B7280; line-height:1.6; }

/* ── Row utilities ─────────────────────────────────────────────────── */
.ff-row {
  display:flex; justify-content:space-between; align-items:baseline;
  padding:5px 0; border-bottom:1px solid #F3F4F6;
}
.ff-row:last-child { border-bottom:none; }
.ff-row-lbl { font-size:11.5px; color:#6B7280; }
.ff-row-val { font-size:12.5px; font-weight:600; color:#111827; }

/* ── Info / note boxes ─────────────────────────────────────────────── */
.ff-note {
  background:#F9FAFB; border:1px solid #E5E7EB; border-radius:6px;
  padding:11px 15px; font-size:12px; color:#6B7280; line-height:1.6;
}
.ff-alert-amber {
  background:#FFFBEB; border:1px solid #FDE68A; border-radius:6px;
  padding:11px 15px; font-size:12px; color:#92400E; line-height:1.6;
}
.ff-alert-red {
  background:#FFF1F2; border:1px solid #FECDD3; border-radius:6px;
  padding:11px 15px; font-size:12px; color:#9F1239; line-height:1.6;
}
.ff-alert-green {
  background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px;
  padding:11px 15px; font-size:12px; color:#166534; line-height:1.6;
}

/* ── Disclaimer footer ─────────────────────────────────────────────── */
.ff-footer {
  font-size:10px; color:#D1D5DB; line-height:1.6;
  padding-top:10px; border-top:1px solid #F3F4F6; margin-top:14px;
}

/* ── Step label ────────────────────────────────────────────────────── */
.ff-page-step {
  font-size:11px; color:#9CA3AF; margin-bottom:14px; display:block;
}

</style>
"""

# Grade/risk colour maps used across pages
GRADE_COLOR = {"A": "#15803D", "B": "#4D7C0F", "C": "#B45309", "D": "#C2410C", "F": "#B91C1C"}
GRADE_BG    = {"A": "#DCFCE7", "B": "#ECFCCB", "C": "#FEF3C7", "D": "#FFEDD5", "F": "#FEE2E2"}
RISK_COLOR  = {"Low": "#15803D", "Medium": "#B45309", "High": "#C2410C", "Very High": "#B91C1C"}
RISK_BG     = {"Low": "#F0FDF4", "Medium": "#FFFBEB", "High": "#FFF7ED", "Very High": "#FEF2F2"}


def inject_shared_styles() -> None:
    """Inject the shared CSS into the current page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_empty_state(
    title: str,
    body: str,
    link_page: str | None = None,
    link_label: str = "Continue →",
) -> None:
    """Render a centered empty state with an optional navigation link."""
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown(f"""
<div class="ff-empty-state">
  <div class="ff-empty-icon">○</div>
  <p class="ff-empty-title">{title}</p>
  <p class="ff-empty-body">{body}</p>
</div>""", unsafe_allow_html=True)
        if link_page:
            st.markdown("<div style='text-align:center;margin-top:12px;'>", unsafe_allow_html=True)
            st.page_link(link_page, label=link_label)
            st.markdown("</div>", unsafe_allow_html=True)


def render_session_banner() -> None:
    """Render a subtle one-line session-state notice near the top of the page.

    Shown on pages 2–5 to prevent demo confusion when a page refresh resets state.
    Uses a muted, low-noise style — informative but not alarming.
    """
    st.markdown("""
<div style="font-size:11px;color:#9CA3AF;padding:4px 0 12px;
     border-bottom:1px solid #F3F4F6;margin-bottom:6px;">
  This prototype stores workflow state within the active browser session.
  Refreshing the page will reset the current demo flow.
</div>""", unsafe_allow_html=True)


def context_strip_html(
    display_name: str,
    meta: str,
    grade: str = "",
    risk_band: str = "",
    score: float = 0.0,
    request: str = "",
) -> str:
    """Return HTML for the restaurant context strip shown at the top of pages 2-5."""
    grade_html = ""
    if grade:
        gc = GRADE_COLOR.get(grade, "#6B7280")
        gb = GRADE_BG.get(grade, "#F3F4F6")
        grade_html = (
            f'<span class="ff-grade-tag" style="background:{gb};color:{gc};">'
            f"Grade {grade}</span>"
        )
    risk_html = ""
    if risk_band:
        rc = RISK_COLOR.get(risk_band, "#6B7280")
        rb = RISK_BG.get(risk_band, "#F9FAFB")
        risk_html = (
            f'<span class="ff-risk-tag" style="background:{rb};color:{rc};">'
            f"{risk_band} risk</span>"
        )
    score_html = (
        f'<span class="ff-context-meta">{score:.0f} / 100</span>'
        if score else ""
    )
    request_html = (
        f'<span class="ff-context-meta" style="margin-left:auto;">{request}</span>'
        if request else ""
    )
    return f"""
<div class="ff-context-strip">
  <span class="ff-context-name">{display_name}</span>
  <span class="ff-context-meta">{meta}</span>
  {grade_html} {risk_html} {score_html}
  {request_html}
</div>"""
