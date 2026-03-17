"""
asset_monitoring.py — Smart Asset Monitoring (Energy & Churn)
Model weights, thresholds, and energy params are user-adjustable via expander.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from data import (
    PROJECTS, df_projects, df_occupancy_trend, df_energy_trend, df_tenants,
    compute_churn_scores, apply_risk_labels,
    DEFAULT_W_EXPIRY, DEFAULT_W_ACTIVITY, DEFAULT_W_SECTOR, DEFAULT_W_RENT,
    EXPIRY_HORIZON_DAYS, SECTOR_BASE_RISK,
    ENERGY_COST_PER_KWH, ENERGY_WASTE_FACTOR,
    OCC_ALERT_THRESHOLD, NRG_ALERT_THRESHOLD,
)
from style import section_header, alert_card, ACCENT, RED, YELLOW, get_chart_layout, get_theme_tokens


def render(selected_project=None):
    """Main render function for the Asset Monitoring page."""
    t = get_theme_tokens()
    chart_layout = get_chart_layout()

    # ── Project filter ──────────────────────────────────────────────────────
    project = st.selectbox(
        "Select Project",
        ["All Projects"] + PROJECTS,
        index=0 if selected_project is None else PROJECTS.index(selected_project) + 1,
    )
    projects_to_show = PROJECTS if project == "All Projects" else [project]

    # ── MODEL PARAMETERS PANEL ─────────────────────────────────────────────
    with st.expander("⚙️  Churn Model Parameters — adjust weights & thresholds", expanded=False):
        st.markdown(
            "These weights control how each signal contributes to the **Churn Risk** score. "
            "Changes instantly re-score all tenants and update every downstream KPI."
        )
        pc1, pc2 = st.columns(2)
        with pc1:
            w_expiry = st.slider(
                "Weight: Lease Expiry Proximity",
                0.0, 1.0, float(DEFAULT_W_EXPIRY), 0.05,
                help="Higher = expiring leases dominate the risk score",
            )
            w_activity = st.slider(
                "Weight: Tenant Inactivity",
                0.0, 1.0, float(DEFAULT_W_ACTIVITY), 0.05,
                help="Higher = low badge/access activity raises risk more",
            )
        with pc2:
            w_sector = st.slider(
                "Weight: Sector Baseline Risk",
                0.0, 1.0, float(DEFAULT_W_SECTOR), 0.05,
                help="Higher = industry churn tendency matters more",
            )
            w_rent = st.slider(
                "Weight: Rent Stress (below median)",
                0.0, 1.0, float(DEFAULT_W_RENT), 0.05,
                help="Higher = tenants paying less than median score riskier",
            )

        st.markdown("---")
        th1, th2, th3 = st.columns(3)
        with th1:
            high_thresh = st.slider("🔴 High Risk threshold", 0.30, 0.90, 0.60, 0.05)
        with th2:
            medium_thresh = st.slider("🟡 Medium Risk threshold", 0.10, 0.59, 0.30, 0.05)
        with th3:
            horizon = st.slider(
                "Expiry horizon (days)", 180, 1460, EXPIRY_HORIZON_DAYS, 30,
                help="Leases expiring within this window are scored on a sliding scale",
            )

        st.markdown("---")
        st.markdown("**Energy Model Parameters**")
        e1, e2, e3 = st.columns(3)
        with e1:
            cost_kwh = st.number_input(
                "Energy cost (₪/kWh)", 0.20, 2.00,
                float(ENERGY_COST_PER_KWH), 0.05, format="%.2f",
            )
        with e2:
            waste_factor = st.slider(
                "Waste factor (%)", 10, 80,
                int(ENERGY_WASTE_FACTOR * 100), 5,
            ) / 100.0
        with e3:
            occ_thresh = st.slider(
                "Occupancy alert threshold (%)", 20, 80,
                OCC_ALERT_THRESHOLD, 5,
            )

    # ── Recompute churn with live weights ──────────────────────────────────
    df_live = compute_churn_scores(
        df_tenants,
        w_expiry=w_expiry, w_activity=w_activity,
        w_sector=w_sector, w_rent=w_rent,
        horizon=horizon,
    )
    df_live = apply_risk_labels(df_live, high=high_thresh, medium=medium_thresh)

    # ── 1. Dual-Axis Chart ──────────────────────
    section_header("Occupancy vs Energy Consumption — 12-Month Trend")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    colors_occ = ["#4FC3F7", "#81C784", "#FFB74D", "#E57373", "#BA68C8"]
    colors_nrg = ["#0288D1", "#388E3C", "#F57C00", "#D32F2F", "#7B1FA2"]

    for i, proj in enumerate(projects_to_show):
        months = df_occupancy_trend["Month"]

        # Occupancy bars
        fig.add_trace(
            go.Bar(
                x=months,
                y=df_occupancy_trend[proj],
                name=f"{proj} — Occupancy",
                marker_color=colors_occ[PROJECTS.index(proj) % len(colors_occ)],
                opacity=0.7,
            ),
            secondary_y=False,
        )

        # Energy line
        fig.add_trace(
            go.Scatter(
                x=months,
                y=df_energy_trend[proj],
                name=f"{proj} — Energy",
                mode="lines+markers",
                line=dict(width=2.5, color=colors_nrg[PROJECTS.index(proj) % len(colors_nrg)]),
            ),
            secondary_y=True,
        )

    _layout = dict(chart_layout)
    _layout.update(
        barmode="group",
        height=440,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.35,
            xanchor="center", x=0.5, font=dict(size=11, color=t["TEXT"]),
        ),
    )
    fig.update_layout(_layout)
    fig.update_yaxes(title_text="Occupancy (%)", secondary_y=False, range=[0, 100],
                      title_font=dict(color=t["TEXT"]), tickfont=dict(color=t["TEXT"]))
    fig.update_yaxes(title_text="Energy (kWh)", secondary_y=True,
                      title_font=dict(color=t["TEXT"]), tickfont=dict(color=t["TEXT"]))
    fig.update_xaxes(tickfont=dict(color=t["TEXT"]))

    st.plotly_chart(fig, use_container_width=True)

    # ── 2. Inefficiency Alerts (reactive to energy params) ─────────────────
    section_header("Inefficiency Detection")

    peak_energy = df_projects["Energy (kWh)"].max()
    alerts_found = False

    for _, row in df_projects.iterrows():
        if row["Project"] not in projects_to_show:
            continue
        occ = row["Occupancy (%)"]
        nrg = row["Energy (kWh)"]
        if occ < occ_thresh and nrg > NRG_ALERT_THRESHOLD * peak_energy:
            saving = int(nrg * waste_factor * cost_kwh * 12)
            alert_card(
                f"Inefficiency Alert — {row['Project']}",
                f"Occupancy is only <b>{occ}%</b> (threshold: {occ_thresh}%) but energy is "
                f"<b>{nrg:,} kWh</b> ({nrg / peak_energy * 100:.0f}% of portfolio peak). "
                f"At ₪{cost_kwh:.2f}/kWh with {waste_factor*100:.0f}% waste factor → "
                f"potential annual saving: <b>₪{saving:,}</b>.",
            )
            alerts_found = True

    if not alerts_found:
        st.success(f"✅ No inefficiency alerts at {occ_thresh}% occupancy threshold.")

    # ── 3. Tenant Health (live-scored from model params) ──────────────────
    section_header("Tenant Health — Churn Intelligence")

    tenants_filtered = df_live[df_live["Project"].isin(projects_to_show)].copy()
    tenants_display = tenants_filtered[
        ["Tenant", "Project", "Sector", "Lease Expiry", "Days to Expiry",
         "Monthly Rent (₪)", "Activity Score", "Churn Risk", "Risk Level"]
    ].sort_values("Churn Risk", ascending=False).reset_index(drop=True)

    def _color_risk(val):
        if "High" in str(val):
            return f"background-color: rgba(255,75,75,0.18); color: {RED}; font-weight: 700"
        if "Medium" in str(val):
            return f"background-color: rgba(255,217,61,0.15); color: {YELLOW}; font-weight: 600"
        return f"color: {ACCENT}"

    def _color_activity(val):
        try:
            v = float(val)
        except (ValueError, TypeError):
            return ""
        if v < 0.35:
            return f"color: {RED}; font-weight: 700"
        if v < 0.55:
            return f"color: {YELLOW}"
        return f"color: {ACCENT}"

    def _color_days(val):
        try:
            v = int(val)
        except (ValueError, TypeError):
            return ""
        if v < 120:
            return f"color: {RED}; font-weight: 700"
        if v < 365:
            return f"color: {YELLOW}"
        return ""

    styled = (
        tenants_display.style
        .map(_color_risk, subset=["Risk Level"])
        .map(_color_activity, subset=["Activity Score"])
        .map(_color_days, subset=["Days to Expiry"])
        .format({
            "Monthly Rent (₪)": "₪{:,.0f}",
            "Churn Risk": "{:.2f}",
            "Activity Score": "{:.2f}",
        })
    )

    st.dataframe(styled, use_container_width=True, height=420)

    # Summary metrics
    high_risk_count = (tenants_filtered["Churn Risk"] >= high_thresh).sum()
    total_rent_at_risk = tenants_filtered.loc[
        tenants_filtered["Churn Risk"] >= high_thresh, "Monthly Rent (₪)"
    ].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Tenants at High Risk", str(high_risk_count))
    c2.metric("Monthly Revenue at Risk", f"₪{total_rent_at_risk:,.0f}")
    c3.metric("Annual Revenue at Risk", f"₪{total_rent_at_risk * 12:,.0f}")
