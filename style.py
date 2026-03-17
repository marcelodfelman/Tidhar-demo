"""
style.py — Tidhar dark-theme CSS and reusable UI helpers.
"""

import streamlit as st

# ─── Theme Tokens ─────────────────────────────
THEMES = {
    "dark": {
        "NAVY": "#003366",
        "GREY": "#B0BEC5",
        "ACCENT": "#00CC99",
        "BG": "#0E1117",
        "CARD_BG": "#1A1F2B",
        "TEXT": "#E8E8E8",
        "TEXT_MUTED": "#CFD8DC",
        "TEXT_SUBTLE": "#AAAAAA",
        "RED": "#FF4B4B",
        "YELLOW": "#FFD93D",
        "GRID": "#2A2F3B",
        "SIDEBAR_TEXT": "#FFFFFF",
        "SIDEBAR_BUTTON_BG": "rgba(255,255,255,0.12)",
        "SIDEBAR_BUTTON_BORDER": "rgba(255,255,255,0.25)",
        "SIDEBAR_BUTTON_HOVER_BG": "rgba(255,255,255,0.22)",
        "SIDEBAR_BUTTON_HOVER_BORDER": "rgba(255,255,255,0.5)",
        "SELECT_TEXT": "#FFFFFF",
        "PLOTLY_TEMPLATE": "plotly_dark",
    },
    "light": {
        "NAVY": "#E9F0F6",
        "GREY": "#5F6C72",
        "ACCENT": "#009E76",
        "BG": "#F5F7FA",
        "CARD_BG": "#FFFFFF",
        "TEXT": "#1F2933",
        "TEXT_MUTED": "#52606D",
        "TEXT_SUBTLE": "#7B8794",
        "RED": "#C62828",
        "YELLOW": "#B26A00",
        "GRID": "#D9E2EC",
        "SIDEBAR_TEXT": "#102A43",
        "SIDEBAR_BUTTON_BG": "rgba(16,42,67,0.06)",
        "SIDEBAR_BUTTON_BORDER": "rgba(16,42,67,0.22)",
        "SIDEBAR_BUTTON_HOVER_BG": "rgba(16,42,67,0.14)",
        "SIDEBAR_BUTTON_HOVER_BORDER": "rgba(16,42,67,0.36)",
        "SELECT_TEXT": "#102A43",
        "PLOTLY_TEMPLATE": "plotly",
    },
}

# Backward-compatible constants (dark theme defaults for existing module imports).
NAVY = THEMES["dark"]["NAVY"]
GREY = THEMES["dark"]["GREY"]
ACCENT = THEMES["dark"]["ACCENT"]
BG_DARK = THEMES["dark"]["BG"]
CARD_BG = THEMES["dark"]["CARD_BG"]
TEXT = THEMES["dark"]["TEXT"]
RED = THEMES["dark"]["RED"]
YELLOW = THEMES["dark"]["YELLOW"]


def get_theme_name(theme: str | None = None) -> str:
    """Return normalized theme key: 'light' or 'dark'."""
    raw = (theme if theme is not None else st.session_state.get("theme", "Light"))
    name = str(raw).strip().lower()
    return "dark" if name == "dark" else "light"


def get_theme_tokens(theme: str | None = None) -> dict:
    """Get theme token dict for current or explicit theme."""
    return THEMES[get_theme_name(theme)]


def get_chart_layout(theme: str | None = None, **overrides) -> dict:
    """Return a Plotly layout baseline for the active theme."""
    t = get_theme_tokens(theme)
    layout = dict(
        template=t["PLOTLY_TEMPLATE"],
        paper_bgcolor=t["CARD_BG"],
        plot_bgcolor=t["CARD_BG"],
        font=dict(color=t["TEXT"], size=11),
        margin=dict(l=42, r=20, t=36, b=36),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10, color=t["TEXT"]),
            title=dict(font=dict(color=t["TEXT"])),
            orientation="h",
            y=1.1,
        ),
    )
    layout.update(overrides)
    return layout


def inject_css(theme: str | None = None):
    """Inject the global dark-themed CSS once per session."""
    t = get_theme_tokens(theme)
    st.markdown(f"""
    <style>
        /* ── Global ── */
        .stApp {{
            background-color: {t['BG']};
            color: {t['TEXT']};
        }}

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {{
            background-color: {t['NAVY']};
        }}
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3 {{
            color: {t['SIDEBAR_TEXT']};
        }}
        section[data-testid="stSidebar"] .stRadio label span {{
            color: {t['SIDEBAR_TEXT']} !important;
        }}
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
            color: {t['SIDEBAR_TEXT']} !important;
        }}
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {{
            color: {t['SIDEBAR_TEXT']} !important;
        }}
        section[data-testid="stSidebar"] .stButton > button {{
            color: {t['SIDEBAR_TEXT']} !important;
            background-color: {t['SIDEBAR_BUTTON_BG']} !important;
            border: 1px solid {t['SIDEBAR_BUTTON_BORDER']} !important;
        }}
        section[data-testid="stSidebar"] .stButton > button:hover {{
            background-color: {t['SIDEBAR_BUTTON_HOVER_BG']} !important;
            border-color: {t['SIDEBAR_BUTTON_HOVER_BORDER']} !important;
        }}

        /* ── Global widget labels ── */
        .stSelectbox label, .stSlider label, .stTextArea label,
        .stRadio label, .stCheckbox label, .stNumberInput label {{
            color: {t['TEXT']} !important;
        }}
        div[data-testid="stCheckbox"] label,
        div[data-testid="stCheckbox"] label p,
        div[data-testid="stCheckbox"] span,
        div[data-testid="stWidgetLabel"] p {{
            color: {t['TEXT']} !important;
        }}
        .stSelectbox div[data-baseweb="select"] span {{
            color: {t['SELECT_TEXT']} !important;
        }}

        /* ── KPI Cards ── */
        .kpi-card {{
            background: {t['CARD_BG']};
            border-left: 4px solid {t['ACCENT']};
            border-radius: 8px;
            padding: 20px 24px;
            margin: 4px 0;
        }}
        .kpi-card .label {{
            font-size: 0.82rem;
            color: {t['TEXT_MUTED']};
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }}
        .kpi-card .value {{
            font-size: 1.9rem;
            font-weight: 700;
            color: {t['TEXT']};
        }}
        .kpi-card .delta {{
            font-size: 0.85rem;
            color: {t['ACCENT']};
            margin-top: 2px;
        }}

        /* ── Alert Card ── */
        .alert-card {{
            background: rgba(255, 75, 75, 0.12);
            border-left: 4px solid {t['RED']};
            border-radius: 8px;
            padding: 16px 20px;
            margin: 8px 0;
            color: {t['TEXT']};
        }}
        .alert-card .alert-title {{
            font-weight: 700;
            color: {t['RED']};
            margin-bottom: 4px;
        }}

        /* ── Section Headers ── */
        .section-header {{
            font-size: 1.3rem;
            font-weight: 700;
            color: {t['TEXT']};
            border-bottom: 2px solid {t['ACCENT']};
            padding-bottom: 6px;
            margin: 24px 0 16px 0;
        }}

        /* ── JSON output card ── */
        .json-card {{
            background: {t['CARD_BG']};
            border: 1px solid {t['ACCENT']};
            border-radius: 8px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 0.88rem;
            color: {t['ACCENT']};
            white-space: pre-wrap;
        }}

        /* ── Streamlit overrides ── */
        .stMetric label {{
            color: {t['TEXT_MUTED']} !important;
        }}
        .stMetric [data-testid="stMetricValue"] {{
            color: {t['TEXT']} !important;
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
            background: {t['CARD_BG']};
            border: 1px solid {t['GRID']};
            border-radius: 10px;
            padding: 9px 14px;
            max-width: 280px;
            font-size: 0.82rem;
            line-height: 1.4;
            box-shadow: 0 4px 16px rgba(0,0,0,0.5);
            pointer-events: none;
        }}
        .ai-fab-preview-body {{
            color: {t['TEXT_SUBTLE']};
            font-size: 0.75rem;
            margin-top: 3px;
            font-weight: 400;
        }}
    </style>
    """, unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str = "", trend: str = "", trend_color: str = ""):
    """Render a styled KPI metric card with optional trend indicator."""
    t = get_theme_tokens()
    delta_html = f'<div class="delta">{delta}</div>' if delta else ""
    trend_html = ""
    if trend:
        tc = trend_color or t["ACCENT"]
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
    t = get_theme_tokens()
    st.markdown(f"""
    <div class="alert-card">
        <div class="alert-title" style="color:{t['RED']};">⚠ {title}</div>
        <div>{body}</div>
    </div>
    """, unsafe_allow_html=True)
