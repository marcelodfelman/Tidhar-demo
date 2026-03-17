"""
modules/ai_agent.py — Tidhar AI Agent Insight Engine
Generates ranked portfolio insights from live data and renders them
inside a Streamlit dialog modal.
"""

import streamlit as st
from datetime import date
import pandas as pd
from typing import Any, cast
from style import get_theme_tokens

# ── Data imports (robust to partial datasets across environments) ───────────
import data as _data

df_tenants = _data.df_tenants
df_projects = _data.df_projects
df_occupancy_trend = _data.df_occupancy_trend
REF_DATE = _data.REF_DATE
df_costs = _data.df_costs
df_revenue_per_unit = _data.df_revenue_per_unit
df_monthly_income = getattr(_data, "df_monthly_income", pd.DataFrame())
MOCK_AI_EXTRACTION = getattr(_data, "MOCK_AI_EXTRACTION", {})

get_construction_status_table = getattr(_data, "get_construction_status_table", None)
get_construction_gantt = getattr(_data, "get_construction_gantt", None)
df_construction_risks = getattr(_data, "df_construction_risks", pd.DataFrame())
df_construction_safety = getattr(_data, "df_construction_safety", pd.DataFrame())


_PAGE_KEYS = {
    "asset": "Asset Monitoring",
    "ebitda": "EBITDA",
    "document": "Document",
    "analytics": "Analytics",
    "construction": "Construction",
}


def _normalize_context_page(current_page: str | None) -> str | None:
    """Map full navigation labels to a stable page key."""
    if not current_page:
        return None

    for key, needle in _PAGE_KEYS.items():
        if needle in current_page:
            return key
    return None


def _add_insight(
    insights: list[dict],
    *,
    severity: str,
    icon: str,
    title: str,
    body: str,
    action: str,
    module: str,
    contexts: tuple[str, ...],
) -> None:
    insights.append(
        {
            "severity": severity,
            "icon": icon,
            "title": title,
            "body": body,
            "action": action,
            "module": module,
            "contexts": contexts,
        }
    )


# ─────────────────────────────────────────────────────────────────────────────
# INSIGHT GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_insights(current_page: str | None = None) -> list[dict]:
    """
    Analyse live data and return a sorted list of insight dicts.
    If current_page is provided, only returns insights relevant to that section.

    Each dict contains:
        severity  : 'critical' | 'warning' | 'info'
        icon      : emoji string
        title     : short headline
        body      : HTML string with detail text
        action    : button label
        module    : target navigation string (matches st.radio options in app.py)
    """
    page_key = _normalize_context_page(current_page)
    insights: list[dict] = []

    # Asset Monitoring rules
    high_churn = df_tenants[df_tenants["Churn Risk"] >= 0.60]
    for _, row in high_churn.iterrows():
        _add_insight(
            insights,
            severity="critical",
            icon="🔴",
            title=f"Critical Churn Risk — {row['Tenant']}",
            body=(
                f"<b>{row['Tenant']}</b> ({row['Project']}) has a churn risk of "
                f"<b>{row['Churn Risk']:.0%}</b>. "
                f"Sector: {row['Sector']} · Lease expires: {row['Lease Expiry']} · "
                f"Activity score: {row['Activity Score']:.2f}. "
                f"Immediate retention action recommended."
            ),
            action="View Asset Monitoring",
            module="📊 Smart Asset Monitoring",
            contexts=("asset",),
        )

    # Cross-module energy and profitability signals
    low_occ_projects = df_projects[df_projects["Occupancy (%)"] < 50]
    for _, row in low_occ_projects.iterrows():
        _add_insight(
            insights,
            severity="warning",
            icon="⚡",
            title=f"Energy Inefficiency — {row['Project']}",
            body=(
                f"<b>{row['Project']}</b> has only <b>{row['Occupancy (%)']}%</b> occupancy "
                f"but consumes <b>{row['Energy (kWh)']:,} kWh</b>/month. "
                f"Estimated waste: ~{int(row['Energy (kWh)'] * 0.40):,} kWh. "
                f"Consider consolidation or smart HVAC scheduling."
            ),
            action="View EBITDA Simulator",
            module="💰 EBITDA Simulator",
            contexts=("ebitda", "analytics"),
        )

    critical_tenants = set(high_churn["Tenant"])
    today = REF_DATE
    for _, row in df_tenants.iterrows():
        if row["Tenant"] in critical_tenants:
            continue
        days_left = row.get("Days to Expiry")
        if days_left is None:
            try:
                days_left = (
                    date.fromisoformat(str(row["Lease Expiry"]) + "-01") - today
                ).days
            except Exception:
                continue
        if 0 <= days_left <= 180:
            _add_insight(
                insights,
                severity="warning",
                icon="📅",
                title=f"Lease Expiring Soon — {row['Tenant']}",
                body=(
                    f"<b>{row['Tenant']}</b> ({row['Project']}) lease ends "
                    f"<b>{row['Lease Expiry']}</b> — <b>{days_left} days</b> remaining. "
                    f"Monthly rent: ₪{row['Monthly Rent (₪)']:,}. "
                    f"Renewal negotiation should begin immediately."
                ),
                action="View Asset Monitoring",
                module="📊 Smart Asset Monitoring",
                contexts=("asset", "document"),
            )

    numeric_cols = [c for c in df_occupancy_trend.columns if c != "Month"]
    if len(df_occupancy_trend) >= 12:
        first_row = df_occupancy_trend.iloc[0]
        last_row = df_occupancy_trend.iloc[-1]
        for project in numeric_cols:
            try:
                decline = float(first_row[project]) - float(last_row[project])
            except (TypeError, ValueError):
                continue
            if decline >= 8:
                current_occ = float(last_row[project])
                _add_insight(
                    insights,
                    severity="info",
                    icon="📉",
                    title=f"Occupancy Decline — {project}",
                    body=(
                        f"<b>{project}</b> occupancy has dropped <b>{decline:.0f} pp</b> "
                        f"over the past 12 months "
                        f"(from {float(first_row[project]):.0f}% → {current_occ:.0f}%). "
                        f"Review leasing strategy and tenant pipeline."
                    ),
                    action="View Asset Monitoring",
                    module="📊 Smart Asset Monitoring",
                    contexts=("asset", "analytics"),
                )

    cost_avg = df_costs["Total (₪)"].mean()
    cost_last = df_costs["Total (₪)"].iloc[-1]
    if cost_last > cost_avg * 1.10:
        pct_above = (cost_last / cost_avg - 1) * 100
        _add_insight(
            insights,
            severity="warning",
            icon="💸",
            title="Operating Cost Spike Detected",
            body=(
                f"Last month's total operating costs reached "
                f"<b>₪{cost_last:,.0f}</b>, which is "
                f"<b>{pct_above:.1f}% above</b> the 12-month average "
                f"(₪{cost_avg:,.0f}). "
                f"Review energy, labour, and maintenance spend in the Analytics Dashboard."
            ),
            action="View Analytics Dashboard",
            module="📈 Analytics Dashboard",
            contexts=("analytics", "ebitda"),
        )

    if len(df_revenue_per_unit) >= 2:
        revpar_last = float(df_revenue_per_unit["RevPAR (₪)"].iloc[-1])
        revpar_prev = float(df_revenue_per_unit["RevPAR (₪)"].iloc[-2])
        if revpar_prev > 0:
            revpar_drop = (revpar_prev - revpar_last) / revpar_prev * 100
            if revpar_drop >= 8:
                _add_insight(
                    insights,
                    severity="critical",
                    icon="📉",
                    title=f"RevPAR Decline — {revpar_drop:.1f}% MoM Drop",
                    body=(
                        f"Portfolio RevPAR dropped from <b>₪{revpar_prev:,.0f}</b> to "
                        f"<b>₪{revpar_last:,.0f}</b> month-on-month — a "
                        f"<b>{revpar_drop:.1f}% decline</b>. "
                        f"Investigate occupancy and pricing strategy immediately."
                    ),
                    action="View Analytics Dashboard",
                    module="📈 Analytics Dashboard",
                    contexts=("analytics", "ebitda"),
                )

    # EBITDA-specific margin signal
    if not df_monthly_income.empty and not df_costs.empty:
        income_last = float(df_monthly_income["Total"].iloc[-1])
        cost_last = float(df_costs["Total (₪)"].iloc[-1])
        margin = ((income_last - cost_last) / income_last) if income_last > 0 else 0.0
        if margin < 0.35:
            _add_insight(
                insights,
                severity="warning",
                icon="📊",
                title=f"EBITDA Pressure — Margin {margin:.1%}",
                body=(
                    f"Latest operating margin is <b>{margin:.1%}</b> "
                    f"(income ₪{income_last:,.0f} vs cost ₪{cost_last:,.0f}). "
                    "Prioritize energy reduction and labor productivity actions."
                ),
                action="View EBITDA Simulator",
                module="💰 EBITDA Simulator",
                contexts=("ebitda",),
            )

    # Document Intelligence signals
    if MOCK_AI_EXTRACTION:
        extracted = MOCK_AI_EXTRACTION.get("extracted_fields", {})
        exp_date = extracted.get("expiration_date", "N/A")
        flags = MOCK_AI_EXTRACTION.get("risk_flags", [])
        confidence = float(MOCK_AI_EXTRACTION.get("confidence", 0.0))
        if flags:
            _add_insight(
                insights,
                severity="warning",
                icon="📄",
                title="Lease Clause Risk Flags Detected",
                body=(
                    f"AI extraction found <b>{len(flags)} risk flag(s)</b> "
                    f"with confidence <b>{confidence:.0%}</b>. "
                    f"Latest extracted expiration date: <b>{exp_date}</b>. "
                    "Review pricing flexibility and renewal terms before negotiation."
                ),
                action="View Document Intelligence",
                module="📄 AI Document Intelligence",
                contexts=("document",),
            )

    # Construction PM signals
    if callable(get_construction_status_table):
        try:
            c_status_raw = get_construction_status_table(project="All Projects", as_of_date=REF_DATE)
        except Exception:
            c_status_raw = pd.DataFrame()

        c_status = c_status_raw if isinstance(c_status_raw, pd.DataFrame) else pd.DataFrame()

        if not c_status.empty:
            spi_series = c_status["SPI"].astype(float)
            cpi_series = c_status["CPI"].astype(float)
            delay_series = c_status["Delay Days"].astype(float)
            rfi_series = c_status["Open RFIs"].astype(float)

            worst_spi_idx = spi_series.idxmin()
            worst_cpi_idx = cpi_series.idxmin()
            max_delay_idx = delay_series.idxmax()
            max_rfi_idx = rfi_series.idxmax()

            worst_spi = float(cast(Any, c_status.at[worst_spi_idx, "SPI"]))
            worst_spi_project = str(c_status.at[worst_spi_idx, "Project"])
            worst_gap = float(cast(Any, c_status.at[worst_spi_idx, "Gap (pts)"]))

            worst_cpi = float(cast(Any, c_status.at[worst_cpi_idx, "CPI"]))
            worst_cpi_project = str(c_status.at[worst_cpi_idx, "Project"])

            max_delay = int(cast(Any, c_status.at[max_delay_idx, "Delay Days"]))
            max_delay_project = str(c_status.at[max_delay_idx, "Project"])

            max_rfi = int(cast(Any, c_status.at[max_rfi_idx, "Open RFIs"]))
            max_rfi_project = str(c_status.at[max_rfi_idx, "Project"])

            eac_var = float(c_status["EAC Var (%)"].astype(float).max())

            if worst_spi < 0.93:
                _add_insight(
                    insights,
                    severity="critical",
                    icon="🏗️",
                    title=f"Schedule Slippage — SPI {worst_spi:.2f}",
                    body=(
                        f"<b>{worst_spi_project}</b> is below schedule threshold "
                        f"with SPI <b>{worst_spi:.2f}</b> and gap <b>{worst_gap:+.1f} pts</b>. "
                        "Run 24h critical-path recovery planning."
                    ),
                    action="View Construction PM",
                    module="🏗️ Construction Project Manager",
                    contexts=("construction",),
                )

            if worst_cpi < 0.95 or eac_var > 3.0:
                sev = "critical" if worst_cpi < 0.93 or eac_var > 6.0 else "warning"
                _add_insight(
                    insights,
                    severity=sev,
                    icon="💰",
                    title=f"Cost Overrun Risk — CPI {worst_cpi:.2f}",
                    body=(
                        f"Worst project <b>{worst_cpi_project}</b> has CPI <b>{worst_cpi:.2f}</b>. "
                        f"Portfolio max EAC variance is <b>{eac_var:+.1f}%</b>. "
                        "Freeze non-critical commitments and rebalance forecast-to-complete."
                    ),
                    action="View Construction PM",
                    module="🏗️ Construction Project Manager",
                    contexts=("construction",),
                )

            if max_delay > 0:
                sev = "critical" if max_delay >= 21 else "warning"
                _add_insight(
                    insights,
                    severity=sev,
                    icon="⏱️",
                    title=f"Delay Exposure — {max_delay} Days",
                    body=(
                        f"<b>{max_delay_project}</b> has the largest delay at <b>{max_delay} days</b>. "
                        f"Highest RFI queue is <b>{max_rfi}</b> in "
                        f"<b>{max_rfi_project}</b>, increasing dependency risk."
                    ),
                    action="View Construction PM",
                    module="🏗️ Construction Project Manager",
                    contexts=("construction",),
                )

    if not df_construction_risks.empty:
        risks = df_construction_risks.copy()
        risks["Expected Exposure (₪)"] = (
            risks["Probability (%)"].astype(float) / 100.0
        ) * risks["Impact (₪)"].astype(float)

        critical_count = int((risks["Severity"] == "Critical").sum())
        top_risk = risks.sort_values("Expected Exposure (₪)", ascending=False).iloc[0]
        if critical_count > 0:
            sev = "critical" if critical_count >= 2 else "warning"
            _add_insight(
                insights,
                severity=sev,
                icon="⚠️",
                title=f"Construction Risk Pressure — {critical_count} Critical",
                body=(
                    f"Top exposure is <b>{top_risk['Project']}</b> / {top_risk['Category']} at "
                    f"~<b>₪{float(top_risk['Expected Exposure (₪)']):,.0f}</b> expected impact. "
                    "Escalate mitigation owner and due date this week."
                ),
                action="View Construction PM",
                module="🏗️ Construction Project Manager",
                contexts=("construction",),
            )

    if not df_construction_safety.empty and len(df_construction_safety) >= 2:
        safety = df_construction_safety.copy()
        near_last = int(safety["Near Misses"].iloc[-1])
        near_prev = int(safety["Near Misses"].iloc[-2])
        lti_ytd = int(safety["Lost Time Incidents"].sum())
        if near_last > near_prev or lti_ytd > 0:
            sev = "critical" if near_last - near_prev >= 2 or lti_ytd >= 3 else "warning"
            _add_insight(
                insights,
                severity=sev,
                icon="🦺",
                title="Safety Trend Alert",
                body=(
                    f"Near misses moved from <b>{near_prev}</b> to <b>{near_last}</b> month-on-month. "
                    f"YTD lost-time incidents: <b>{lti_ytd}</b>. "
                    "Trigger focused HSE intervention on active high-risk zones."
                ),
                action="View Construction PM",
                module="🏗️ Construction Project Manager",
                contexts=("construction",),
            )

    if callable(get_construction_gantt):
        try:
            gantt_raw = get_construction_gantt(project="All Projects", as_of_date=REF_DATE)
        except Exception:
            gantt_raw = pd.DataFrame()

        gantt = gantt_raw if isinstance(gantt_raw, pd.DataFrame) else pd.DataFrame()

        if not gantt.empty:
            dep_blocked = gantt[
                (gantt["Track"] == "Forecast/Actual")
                & (gantt["Is Critical"] == True)
                & (gantt["Predecessor Task"].notna())
                & (gantt["State"].isin(["Delayed", "Critical"]))
            ]
            if not dep_blocked.empty:
                b = dep_blocked.iloc[0]
                _add_insight(
                    insights,
                    severity="warning",
                    icon="🔗",
                    title="Critical Dependency Blocked",
                    body=(
                        f"Task <b>{b['Task']}</b> in <b>{b['Project']}</b> is "
                        f"<b>{b['State']}</b> and depends on <b>{b['Predecessor Task']}</b>. "
                        "Review handover constraints and unblock predecessor chain."
                    ),
                    action="View Construction PM",
                    module="🏗️ Construction Project Manager",
                    contexts=("construction",),
                )

    # Context filter. Unknown contexts fall back to global (all).
    if page_key is not None:
        insights = [i for i in insights if page_key in i.get("contexts", ())]

    # Hide internal context metadata from renderer callers.
    for insight in insights:
        insight.pop("contexts", None)

    # Sort: critical → warning → info
    order = {"critical": 0, "warning": 1, "info": 2}
    insights.sort(key=lambda x: order.get(x["severity"], 99))
    return insights


# ─────────────────────────────────────────────────────────────────────────────
# BADGE COUNT
# ─────────────────────────────────────────────────────────────────────────────

def get_alert_count(current_page: str | None = None) -> int:
    """Return total count of critical + warning insights."""
    insights = generate_insights(current_page=current_page)
    return sum(1 for i in insights if i["severity"] in ("critical", "warning"))


# ─────────────────────────────────────────────────────────────────────────────
# RENDERER
# ─────────────────────────────────────────────────────────────────────────────

# Map severity → card border colour
_SEVERITY_COLOR = {
    "critical": "#FF4B4B",
    "warning":  "#FFD93D",
    "info":     "#00CC99",
}

_SEVERITY_LABEL = {
    "critical": "CRITICAL",
    "warning":  "WARNING",
    "info":     "INFO",
}


def render_insights(current_page: str | None = None):
    """
    Render all insights inside the AI Agent dialog.
    Shows a summary badge row, then one styled card + action button per insight.
    On action-button click, stores nav_to in session_state and shows a toast.
    """
    insights = generate_insights(current_page=current_page)
    t = get_theme_tokens()

    if not insights:
        st.success("✅ No active alerts for this section.")
        return

    # ── Summary badge row ────────────────────────────────────────────────────
    n_critical = sum(1 for i in insights if i["severity"] == "critical")
    n_warning  = sum(1 for i in insights if i["severity"] == "warning")
    n_info     = sum(1 for i in insights if i["severity"] == "info")

    st.markdown(
        f"""
        <div style="display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap;">
            <span style="background:{_SEVERITY_COLOR['critical']}22; color:{_SEVERITY_COLOR['critical']}; border:1px solid {_SEVERITY_COLOR['critical']};
                          border-radius:20px; padding:4px 14px; font-size:0.82rem; font-weight:700;">
                🔴 {n_critical} Critical
            </span>
            <span style="background:{_SEVERITY_COLOR['warning']}22; color:{_SEVERITY_COLOR['warning']}; border:1px solid {_SEVERITY_COLOR['warning']};
                          border-radius:20px; padding:4px 14px; font-size:0.82rem; font-weight:700;">
                ⚠️ {n_warning} Warning
            </span>
            <span style="background:{_SEVERITY_COLOR['info']}22; color:{_SEVERITY_COLOR['info']}; border:1px solid {_SEVERITY_COLOR['info']};
                          border-radius:20px; padding:4px 14px; font-size:0.82rem; font-weight:700;">
                ℹ️ {n_info} Info
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Per-insight cards ────────────────────────────────────────────────────
    for idx, insight in enumerate(insights):
        color = _SEVERITY_COLOR.get(insight["severity"], t["TEXT_SUBTLE"])
        label = _SEVERITY_LABEL.get(insight["severity"], "")

        st.markdown(
            f"""
            <div style="background:{t['CARD_BG']}; border-left:4px solid {color};
                         border-radius:8px; padding:16px 20px; margin:8px 0;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                    <span style="font-size:1.2rem;">{insight['icon']}</span>
                    <span style="font-weight:700; color:{t['TEXT']}; font-size:0.97rem;">
                        {insight['title']}
                    </span>
                    <span style="margin-left:auto; background:{color}33; color:{color};
                                  border:1px solid {color}; border-radius:12px;
                                  padding:2px 10px; font-size:0.72rem; font-weight:700;">
                        {label}
                    </span>
                </div>
                <div style="color:{t['TEXT_MUTED']}; font-size:0.85rem; line-height:1.5;">
                    {insight['body']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            f"→ {insight['action']}",
            key=f"ai_insight_action_{idx}",
            use_container_width=False,
        ):
            st.session_state["nav_to"] = insight["module"]
            st.toast(f"Navigating to {insight['module']}…", icon="🚀")
            st.rerun()
