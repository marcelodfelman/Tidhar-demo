"""
modules/ai_agent.py — Tidhar AI Agent Insight Engine
Generates ranked portfolio insights from live data and renders them
inside a Streamlit dialog modal.
"""

import streamlit as st
from datetime import date

# ── Data imports ─────────────────────────────────────────────────────────────
from data import df_tenants, df_projects, df_occupancy_trend, REF_DATE, df_costs, df_revenue_per_unit


# ─────────────────────────────────────────────────────────────────────────────
# INSIGHT GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_insights() -> list[dict]:
    """
    Analyse live data and return a sorted list of insight dicts.

    Each dict contains:
        severity  : 'critical' | 'warning' | 'info'
        icon      : emoji string
        title     : short headline
        body      : HTML string with detail text
        action    : button label
        module    : target navigation string (matches st.radio options in app.py)
    """
    insights: list[dict] = []

    # ── Rule 1: High churn tenants (Churn Risk ≥ 0.60) → critical ────────────
    high_churn = df_tenants[df_tenants["Churn Risk"] >= 0.60]
    for _, row in high_churn.iterrows():
        insights.append({
            "severity": "critical",
            "icon": "🔴",
            "title": f"Critical Churn Risk — {row['Tenant']}",
            "body": (
                f"<b>{row['Tenant']}</b> ({row['Project']}) has a churn risk of "
                f"<b>{row['Churn Risk']:.0%}</b>. "
                f"Sector: {row['Sector']} · Lease expires: {row['Lease Expiry']} · "
                f"Activity score: {row['Activity Score']:.2f}. "
                f"Immediate retention action recommended."
            ),
            "action": "View Asset Monitoring",
            "module": "📊 Smart Asset Monitoring",
        })

    # ── Rule 2: Energy inefficiency — Occupancy < 50% → warning ─────────────
    low_occ_projects = df_projects[df_projects["Occupancy (%)"] < 50]
    for _, row in low_occ_projects.iterrows():
        insights.append({
            "severity": "warning",
            "icon": "⚡",
            "title": f"Energy Inefficiency — {row['Project']}",
            "body": (
                f"<b>{row['Project']}</b> has only <b>{row['Occupancy (%)']}%</b> occupancy "
                f"but consumes <b>{row['Energy (kWh)']:,} kWh</b>/month. "
                f"Estimated waste: ~{int(row['Energy (kWh)'] * 0.40):,} kWh. "
                f"Consider consolidation or smart HVAC scheduling."
            ),
            "action": "View EBITDA Simulator",
            "module": "💰 EBITDA Simulator",
        })

    # ── Rule 3: Leases expiring within 180 days (not already critical) ────────
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
            insights.append({
                "severity": "warning",
                "icon": "📅",
                "title": f"Lease Expiring Soon — {row['Tenant']}",
                "body": (
                    f"<b>{row['Tenant']}</b> ({row['Project']}) lease ends "
                    f"<b>{row['Lease Expiry']}</b> — <b>{days_left} days</b> remaining. "
                    f"Monthly rent: ₪{row['Monthly Rent (₪)']:,}. "
                    f"Renewal negotiation should begin immediately."
                ),
                "action": "View Asset Monitoring",
                "module": "📊 Smart Asset Monitoring",
            })

    # ── Rule 4: 12-month occupancy decline ≥ 8 pp → info ────────────────────
    numeric_cols = [c for c in df_occupancy_trend.columns if c != "Month"]
    if len(df_occupancy_trend) >= 12:
        first_row = df_occupancy_trend.iloc[0]
        last_row  = df_occupancy_trend.iloc[-1]
        for project in numeric_cols:
            try:
                decline = float(first_row[project]) - float(last_row[project])
            except (TypeError, ValueError):
                continue
            if decline >= 8:
                current_occ = float(last_row[project])
                insights.append({
                    "severity": "info",
                    "icon": "📉",
                    "title": f"Occupancy Decline — {project}",
                    "body": (
                        f"<b>{project}</b> occupancy has dropped <b>{decline:.0f} pp</b> "
                        f"over the past 12 months "
                        f"(from {float(first_row[project]):.0f}% → {current_occ:.0f}%). "
                        f"Review leasing strategy and tenant pipeline."
                    ),
                    "action": "View Asset Monitoring",
                    "module": "📊 Smart Asset Monitoring",
                })

    # ── Rule 5: Operating cost spike — last month > 110% of 12-month avg ─────
    cost_avg  = df_costs["Total (₪)"].mean()
    cost_last = df_costs["Total (₪)"].iloc[-1]
    if cost_last > cost_avg * 1.10:
        pct_above = (cost_last / cost_avg - 1) * 100
        insights.append({
            "severity": "warning",
            "icon": "💸",
            "title": "Operating Cost Spike Detected",
            "body": (
                f"Last month's total operating costs reached "
                f"<b>₪{cost_last:,.0f}</b>, which is "
                f"<b>{pct_above:.1f}% above</b> the 12-month average "
                f"(₪{cost_avg:,.0f}). "
                f"Review energy, labour, and maintenance spend in the Analytics Dashboard."
            ),
            "action": "View Analytics Dashboard",
            "module": "📈 Analytics Dashboard",
        })

    # ── Rule 6: RevPAR month-on-month decline ≥ 8% → critical ───────────────
    if len(df_revenue_per_unit) >= 2:
        revpar_last = float(df_revenue_per_unit["RevPAR (₪)"].iloc[-1])
        revpar_prev = float(df_revenue_per_unit["RevPAR (₪)"].iloc[-2])
        if revpar_prev > 0:
            revpar_drop = (revpar_prev - revpar_last) / revpar_prev * 100
            if revpar_drop >= 8:
                insights.append({
                    "severity": "critical",
                    "icon": "📉",
                    "title": f"RevPAR Decline — {revpar_drop:.1f}% MoM Drop",
                    "body": (
                        f"Portfolio RevPAR dropped from <b>₪{revpar_prev:,.0f}</b> to "
                        f"<b>₪{revpar_last:,.0f}</b> month-on-month — a "
                        f"<b>{revpar_drop:.1f}% decline</b>. "
                        f"Investigate occupancy and pricing strategy immediately."
                    ),
                    "action": "View Analytics Dashboard",
                    "module": "📈 Analytics Dashboard",
                })

    # Sort: critical → warning → info
    order = {"critical": 0, "warning": 1, "info": 2}
    insights.sort(key=lambda x: order.get(x["severity"], 99))
    return insights


# ─────────────────────────────────────────────────────────────────────────────
# BADGE COUNT
# ─────────────────────────────────────────────────────────────────────────────

def get_alert_count() -> int:
    """Return total count of critical + warning insights."""
    insights = generate_insights()
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


def render_insights():
    """
    Render all insights inside the AI Agent dialog.
    Shows a summary badge row, then one styled card + action button per insight.
    On action-button click, stores nav_to in session_state and shows a toast.
    """
    insights = generate_insights()

    if not insights:
        st.success("✅ No active alerts — portfolio looks healthy!")
        return

    # ── Summary badge row ────────────────────────────────────────────────────
    n_critical = sum(1 for i in insights if i["severity"] == "critical")
    n_warning  = sum(1 for i in insights if i["severity"] == "warning")
    n_info     = sum(1 for i in insights if i["severity"] == "info")

    st.markdown(
        f"""
        <div style="display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap;">
            <span style="background:#FF4B4B22; color:#FF4B4B; border:1px solid #FF4B4B;
                          border-radius:20px; padding:4px 14px; font-size:0.82rem; font-weight:700;">
                🔴 {n_critical} Critical
            </span>
            <span style="background:#FFD93D22; color:#FFD93D; border:1px solid #FFD93D;
                          border-radius:20px; padding:4px 14px; font-size:0.82rem; font-weight:700;">
                ⚠️ {n_warning} Warning
            </span>
            <span style="background:#00CC9922; color:#00CC99; border:1px solid #00CC99;
                          border-radius:20px; padding:4px 14px; font-size:0.82rem; font-weight:700;">
                ℹ️ {n_info} Info
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Per-insight cards ────────────────────────────────────────────────────
    for idx, insight in enumerate(insights):
        color = _SEVERITY_COLOR.get(insight["severity"], "#AAAAAA")
        label = _SEVERITY_LABEL.get(insight["severity"], "")

        st.markdown(
            f"""
            <div style="background:#1A1F2B; border-left:4px solid {color};
                         border-radius:8px; padding:16px 20px; margin:8px 0;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                    <span style="font-size:1.2rem;">{insight['icon']}</span>
                    <span style="font-weight:700; color:#FFFFFF; font-size:0.97rem;">
                        {insight['title']}
                    </span>
                    <span style="margin-left:auto; background:{color}33; color:{color};
                                  border:1px solid {color}; border-radius:12px;
                                  padding:2px 10px; font-size:0.72rem; font-weight:700;">
                        {label}
                    </span>
                </div>
                <div style="color:#CFD8DC; font-size:0.85rem; line-height:1.5;">
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
