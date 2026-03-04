"""
app.py — Tidhar Decision Intelligence Portal
Main Streamlit entrypoint: sidebar navigation, KPI header, module routing.

Run:  streamlit run app.py
"""

import streamlit as st

# ── Page config (MUST be first Streamlit call) ──
st.set_page_config(
    page_title="Deeply × Tidhar | Strategic Portal",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ──────────────────────────────────────
from style import inject_css, kpi_card
from data import TOTAL_PORTFOLIO_VALUE, ENERGY_SAVINGS_OPP, TENANTS_AT_RISK, get_tenants_at_risk, get_energy_savings_opp
from modules import asset_monitoring, ebitda_simulator, doc_intelligence, ai_agent, analytics_dashboard

# ── Inject global styles ────────────────────────
inject_css()

# ── AI Agent Dialog ─────────────────────────────
@st.dialog("🤖 AI Agent — Portfolio Insights", width="large")
def show_ai_agent():
    ai_agent.render_insights()

# ── Sidebar ─────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏗️ Deeply - Hospitality Demo")
    st.markdown("### 2026 Strategic Portal")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "📊 Smart Asset Monitoring",
            "💰 EBITDA Simulator",
            "📄 AI Document Intelligence",
            "📈 Analytics Dashboard",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.75rem; color:#AAAAAA; text-align:center;'>"
        "Live Strategic Prototype<br>"
        "Built by <b>Deeply</b> for <b>Tidhar Group</b><br>"
        "March 2026"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── AI Agent sidebar button ──────────────────
    st.markdown("---")
    _alert_count = ai_agent.get_alert_count()
    _badge_html = (
        f" <span style='background:#FF4B4B; color:#fff; border-radius:50%; "
        f"padding:1px 7px; font-size:0.72rem; font-weight:700; margin-left:4px;'>"
        f"{_alert_count}</span>"
        if _alert_count > 0 else ""
    )
    st.markdown(
        f"<div style='text-align:center; font-size:0.8rem; color:#AAAAAA; margin-bottom:6px;'>"
        f"AI Alerts{_badge_html}</div>",
        unsafe_allow_html=True,
    )
    if st.button("🤖  AI Insights", key="ai_sidebar_btn", use_container_width=True):
        show_ai_agent()

# ── Top KPI Row ────────────────────────────────
k1, k2, k3 = st.columns(3)
with k1:
    kpi_card("Total Portfolio Value", TOTAL_PORTFOLIO_VALUE, "5 active projects")
with k2:
    kpi_card("Energy Savings Opportunity", ENERGY_SAVINGS_OPP, "Based on inefficiency detection")
with k3:
    kpi_card("Tenants at High Risk", str(TENANTS_AT_RISK), "Churn probability > 60%")

st.markdown("<br>", unsafe_allow_html=True)

# ── Nav-to handler (from AI Agent action buttons) ──────────────
if "nav_to" in st.session_state:
    page = st.session_state.pop("nav_to")

# ── Page Router ─────────────────────────────────
if "Asset Monitoring" in page:
    asset_monitoring.render()
elif "EBITDA" in page:
    ebitda_simulator.render()
elif "Document" in page:
    doc_intelligence.render()
elif "Analytics" in page:
    analytics_dashboard.render()

# ── Floating AI Agent FAB ────────────────────────
import re as _re
import streamlit.components.v1 as _components

_fab_insights = ai_agent.generate_insights()
_fab_count = len([i for i in _fab_insights if i["severity"] in ("critical", "warning")])

# Alert preview bubble — positioned fixed via CSS
if _fab_insights:
    _first = _fab_insights[0]
    _sev_colors = {"critical": "#FF4B4B", "warning": "#FFD93D", "info": "#00CC99"}
    _fc = _sev_colors.get(_first["severity"], "#AAAAAA")
    _body_plain = _re.sub(r"<[^>]+>", "", _first["body"])
    _snippet = (_body_plain[:72] + "…") if len(_body_plain) > 72 else _body_plain
    st.markdown(
        f"<div class='ai-fab-preview'>"
        f"<span style='color:{_fc}; font-weight:700;'>{_first['icon']} {_first['title']}</span>"
        f"<div class='ai-fab-preview-body'>{_snippet}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

# Native Streamlit button — clicking this directly calls show_ai_agent() in Python
_fab_label = "🤖\u00a0 AI Insights" + (f"  ·  {_fab_count}" if _fab_count > 0 else "")
if st.button(_fab_label, key="ai_fab_btn"):
    show_ai_agent()

# JS (via same-origin iframe) repositions the native button to fixed bottom-right.
# MutationObserver reapplies styles after every Streamlit rerender.
_components.html("""
<script>
(function() {
    function styleFab() {
        try {
            var doc = window.parent.document;
            var buttons = doc.querySelectorAll('[data-testid="stButton"] button');
            for (var i = 0; i < buttons.length; i++) {
                var btn = buttons[i];
                if (btn.textContent.includes('AI Insights') && !btn.closest('[data-testid="stSidebar"]')) {
                    var wrapper = btn.closest('[data-testid="stButton"]');
                    if (!wrapper) continue;
                    wrapper.style.cssText = 'position:fixed;bottom:2.2rem;right:2.2rem;z-index:999999;width:auto;';
                    btn.style.cssText = [
                        'background:linear-gradient(135deg,#00CC99 0%,#0077FF 100%)',
                        'color:#FFFFFF',
                        'border:none',
                        'border-radius:50px',
                        'padding:13px 24px',
                        'font-size:0.97rem',
                        'font-weight:700',
                        'cursor:pointer',
                        'box-shadow:0 4px 20px #00CC9966',
                        'white-space:nowrap',
                        'letter-spacing:0.3px',
                        'transition:transform 0.18s ease,box-shadow 0.18s ease'
                    ].join(';') + ';';
                    break;
                }
            }
        } catch(e) {}
    }
    styleFab();
    setTimeout(styleFab, 150);
    setTimeout(styleFab, 600);
    try {
        var obs = new MutationObserver(styleFab);
        obs.observe(window.parent.document.body, {childList:true, subtree:true});
    } catch(e) {}
})();
</script>
""", height=0)
