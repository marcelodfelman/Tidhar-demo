"""
style.py — Tidhar dark-theme CSS and reusable UI helpers.
"""

import streamlit as st

# ─── Color Palette ─────────────────────────────
NAVY    = "#003366"
GREY    = "#B0BEC5"
ACCENT  = "#00CC99"
BG_DARK = "#0E1117"
CARD_BG = "#1A1F2B"
TEXT    = "#E8E8E8"
RED     = "#FF4B4B"
YELLOW  = "#FFD93D"

def inject_css():
    """Inject the global dark-themed CSS once per session."""
    st.markdown(f"""
    <style>
        /* ── Global ── */
        .stApp {{
            background-color: {BG_DARK};
            color: {TEXT};
        }}

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {{
            background-color: {NAVY};
        }}
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3 {{
            color: #FFFFFF;
        }}
        section[data-testid="stSidebar"] .stRadio label span {{
            color: #FFFFFF !important;
        }}
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
            color: #FFFFFF !important;
        }}
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {{
            color: #FFFFFF !important;
        }}
        section[data-testid="stSidebar"] .stButton > button {{
            color: #FFFFFF !important;
            background-color: rgba(255,255,255,0.12) !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
        }}
        section[data-testid="stSidebar"] .stButton > button:hover {{
            background-color: rgba(255,255,255,0.22) !important;
            border-color: rgba(255,255,255,0.5) !important;
        }}

        /* ── Global widget labels ── */
        .stSelectbox label, .stSlider label, .stTextArea label,
        .stRadio label, .stCheckbox label, .stNumberInput label {{
            color: #E0E0E0 !important;
        }}
        .stSelectbox div[data-baseweb="select"] span {{
            color: #FFFFFF !important;
        }}

        /* ── KPI Cards ── */
        .kpi-card {{
            background: {CARD_BG};
            border-left: 4px solid {ACCENT};
            border-radius: 8px;
            padding: 20px 24px;
            margin: 4px 0;
        }}
        .kpi-card .label {{
            font-size: 0.82rem;
            color: #CFD8DC;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }}
        .kpi-card .value {{
            font-size: 1.9rem;
            font-weight: 700;
            color: #FFFFFF;
        }}
        .kpi-card .delta {{
            font-size: 0.85rem;
            color: {ACCENT};
            margin-top: 2px;
        }}

        /* ── Alert Card ── */
        .alert-card {{
            background: rgba(255, 75, 75, 0.12);
            border-left: 4px solid {RED};
            border-radius: 8px;
            padding: 16px 20px;
            margin: 8px 0;
            color: {TEXT};
        }}
        .alert-card .alert-title {{
            font-weight: 700;
            color: {RED};
            margin-bottom: 4px;
        }}

        /* ── Section Headers ── */
        .section-header {{
            font-size: 1.3rem;
            font-weight: 700;
            color: #FFFFFF;
            border-bottom: 2px solid {ACCENT};
            padding-bottom: 6px;
            margin: 24px 0 16px 0;
        }}

        /* ── JSON output card ── */
        .json-card {{
            background: {CARD_BG};
            border: 1px solid {ACCENT};
            border-radius: 8px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 0.88rem;
            color: {ACCENT};
            white-space: pre-wrap;
        }}

        /* ── Streamlit overrides ── */
        .stMetric label {{
            color: #CFD8DC !important;
        }}
        .stMetric [data-testid="stMetricValue"] {{
            color: #FFFFFF !important;
        }}

        /* Dataframe styling */
        .stDataFrame {{
            border-radius: 8px;
            overflow: hidden;
        }}

        /* ── AI Agent FAB preview bubble (fixed position) ── */
        .ai-fab-preview {{
            position: fixed;
            bottom: 5.8rem;
            right: 2.2rem;
            z-index: 999998;
            background: rgba(20, 26, 38, 0.96);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 10px;
            padding: 9px 14px;
            max-width: 280px;
            font-size: 0.82rem;
            line-height: 1.4;
            box-shadow: 0 4px 16px rgba(0,0,0,0.5);
            pointer-events: none;
        }}
        .ai-fab-preview-body {{
            color: #BBBBBB;
            font-size: 0.75rem;
            margin-top: 3px;
            font-weight: 400;
        }}
    </style>
    """, unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str = "", trend: str = "", trend_color: str = ""):
    """Render a styled KPI metric card with optional trend indicator."""
    delta_html = f'<div class="delta">{delta}</div>' if delta else ""
    trend_html = ""
    if trend:
        tc = trend_color or ACCENT
        trend_html = f'<span style="font-size:0.82rem; color:{tc}; font-weight:600; margin-left:6px;">{trend}</span>'
    st.markdown(f"""
    <div class="kpi-card">
        <div class="label">{label}</div>
        <div class="value">{value}{trend_html}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str):
    """Render a styled section heading."""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def alert_card(title: str, body: str):
    """Render a red alert card."""
    st.markdown(f"""
    <div class="alert-card">
        <div class="alert-title">⚠ {title}</div>
        <div>{body}</div>
    </div>
    """, unsafe_allow_html=True)
