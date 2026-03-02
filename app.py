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
from modules import asset_monitoring, ebitda_simulator, doc_intelligence

# ── Inject global styles ────────────────────────
inject_css()

# ── Sidebar ─────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏗️ Deeply × Tidhar")
    st.markdown("### 2026 Strategic Portal")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "📊 Smart Asset Monitoring",
            "💰 EBITDA Simulator",
            "📄 AI Document Intelligence",
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

# ── Top KPI Row ────────────────────────────────
k1, k2, k3 = st.columns(3)
with k1:
    kpi_card("Total Portfolio Value", TOTAL_PORTFOLIO_VALUE, "5 active projects")
with k2:
    kpi_card("Energy Savings Opportunity", ENERGY_SAVINGS_OPP, "Based on inefficiency detection")
with k3:
    kpi_card("Tenants at High Risk", str(TENANTS_AT_RISK), "Churn probability > 60%")

st.markdown("<br>", unsafe_allow_html=True)

# ── Page Router ─────────────────────────────────
if "Asset Monitoring" in page:
    asset_monitoring.render()
elif "EBITDA" in page:
    ebitda_simulator.render()
elif "Document" in page:
    doc_intelligence.render()
