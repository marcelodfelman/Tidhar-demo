"""
modules/analytics_dashboard.py — Tidhar Analytics Dashboard
PowerBI-style KPI dashboard covering income, manpower, room availability,
staff, costs, and revenue-per-unit metrics across the portfolio.

Layout
------
  Time filter → select_slider over MONTHS
  Tier 1 KPIs (7 cards) — Revenue & Efficiency
  Tier 2 KPIs (7 cards) — Operations & Asset
  Row 1: Income & NOI Trend  |  RevPAR / ADR / GOPPAR Trend
  Row 2: Room Availability by Type  |  Manpower Over Time
  Row 3: Cost Breakdown  |  Staff Utilization by Dept
  Asset Ratio Table (Cap Rate, GRM, NOI per project)
  ALOS footnote metric
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from style import kpi_card, section_header, CARD_BG, ACCENT, RED, YELLOW
from data import (
    MONTHS,
    TOTAL_ROOMS,
    BASELINE_EBITDA,
    SATISFACTION_SCORES,
    ALOS_BY_MONTH,
    EPOR_BENCHMARK,
    df_monthly_income,
    df_costs,
    df_revenue_per_unit,
    df_manpower,
    df_staff_by_dept,
    df_rooms_by_type,
    df_occupancy_trend,
    df_cap_table,
    df_tenants,
    df_cpor_monthly,
    df_epor_project,
)

# ─── Shared chart layout ──────────────────────────────────────────────────────
_CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=CARD_BG,
    plot_bgcolor=CARD_BG,
    font=dict(color="#E8E8E8", size=11),
    margin=dict(l=44, r=20, t=38, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10, font_color="#E8E8E8", orientation="h", y=1.12),
)


# ─── Helper ───────────────────────────────────────────────────────────────────
def _slice(df: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
    """Return rows [start … end] inclusive, reset index."""
    return df.iloc[start : end + 1].reset_index(drop=True)


def _force_two_decimal_hover(fig):
    """Force 2-decimal precision in numeric hover tooltips."""
    fig.update_xaxes(hoverformat=".2f")
    fig.update_yaxes(hoverformat=".2f")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN RENDER
# ─────────────────────────────────────────────────────────────────────────────
def render() -> None:
    section_header("📈 Analytics Dashboard")

    # ── Time Filter ───────────────────────────────────────────────────────────
    f_col, _ = st.columns([3, 1])
    with f_col:
        month_range = st.select_slider(
            "Period",
            options=MONTHS,
            value=(MONTHS[0], MONTHS[-1]),
        )

    start_idx = MONTHS.index(month_range[0])
    end_idx   = MONTHS.index(month_range[1])
    if start_idx > end_idx:
        start_idx, end_idx = end_idx, start_idx

    # Sliced DataFrames
    s_income  = _slice(df_monthly_income,  start_idx, end_idx)
    s_costs   = _slice(df_costs,           start_idx, end_idx)
    s_rev_pu  = _slice(df_revenue_per_unit, start_idx, end_idx)
    s_man     = _slice(df_manpower,        start_idx, end_idx)
    s_rooms   = _slice(df_rooms_by_type,   start_idx, end_idx)
    s_occ     = _slice(df_occupancy_trend, start_idx, end_idx)
    months_x  = s_income["Month"].tolist()

    # ── Derived Aggregates ────────────────────────────────────────────────────
    n_months    = end_idx - start_idx + 1
    total_rev   = int(s_income["Total"].sum())
    total_cost  = int(s_costs["Total (₪)"].sum())
    noi         = total_rev - total_cost
    op_margin   = (noi / total_rev * 100) if total_rev else 0.0
    ebitda_ann  = BASELINE_EBITDA * (n_months / 12)
    ebitda_marg = (ebitda_ann / total_rev * 100) if total_rev else 0.0

    avg_revpar  = int(s_rev_pu["RevPAR (₪)"].mean())
    avg_adr     = int(s_rev_pu["ADR (₪)"].mean())
    avg_goppar  = int(s_rev_pu["GOPPAR (₪)"].mean())

    _occ_cols   = [c for c in s_occ.columns if c != "Month"]
    avg_occ     = float(s_occ[_occ_cols].mean().mean())
    vacancy     = 100.0 - avg_occ

    # CPOR: use last-month occupancy to compute occupied rooms
    _last_occ_row = df_occupancy_trend.iloc[-1]
    occ_frac_now  = float(_last_occ_row[_occ_cols].mean()) / 100.0
    occupied_now  = max(occ_frac_now * TOTAL_ROOMS, 1)
    cpor          = total_cost / occupied_now / n_months

    tenant_ret    = (1.0 - float(df_tenants["Churn Risk"].mean())) * 100
    staff_avail   = int(s_man["Available"].iloc[-1])
    staff_total   = int(s_man["Total Headcount"].iloc[-1])
    staff_room    = round(staff_total / TOTAL_ROOMS, 3)
    avg_sat       = round(sum(SATISFACTION_SCORES.values()) / len(SATISFACTION_SCORES), 1)
    avg_alos      = round(sum(ALOS_BY_MONTH) / len(ALOS_BY_MONTH), 1)
    # ── Trend Indicators (vs. prior month in sliced period) ───────────────────
    def _pct_change_trend(series, invert=False):
        """Return (arrow_str, color) for MoM % change."""
        if len(series) < 2:
            return ("", "")
        cur, prev = float(series.iloc[-1]), float(series.iloc[-2])
        if prev == 0:
            return ("", "")
        pct = (cur - prev) / abs(prev) * 100
        positive = pct > 0 if not invert else pct < 0
        if abs(pct) < 0.05:
            return ("─", YELLOW)
        arrow = "▲" if pct > 0 else "▼"
        color = ACCENT if positive else RED
        return (f"{arrow} {abs(pct):.1f}%", color)

    tr_rev, tc_rev       = _pct_change_trend(s_income["Total"])
    tr_revpar, tc_revpar = _pct_change_trend(s_rev_pu["RevPAR (₪)"])
    tr_adr, tc_adr       = _pct_change_trend(s_rev_pu["ADR (₪)"])
    tr_goppar, tc_goppar = _pct_change_trend(s_rev_pu["GOPPAR (₪)"])
    _noi_s               = s_income["Total"] - s_costs["Total (₪)"]
    tr_noi, tc_noi       = _pct_change_trend(_noi_s)
    _op_m_s              = _noi_s / s_income["Total"] * 100
    tr_opm, tc_opm       = _pct_change_trend(_op_m_s)
    _occ_mean_s          = s_occ[_occ_cols].mean(axis=1)
    tr_occ, tc_occ       = _pct_change_trend(_occ_mean_s)
    tr_vac, tc_vac       = _pct_change_trend(100 - _occ_mean_s, invert=True)
    s_cpor               = _slice(df_cpor_monthly, start_idx, end_idx)
    tr_cpor, tc_cpor     = _pct_change_trend(s_cpor["CPOR (₪)"], invert=True)
    avg_epor             = float(df_epor_project["EPOR (kWh)"].mean())
    _high_risk           = df_tenants[df_tenants["Churn Risk"] >= 0.60]
    rev_at_risk_monthly  = int(_high_risk["Monthly Rent (₪)"].sum())
    rev_at_risk_annual   = rev_at_risk_monthly * 12
    # ─────────────────────────────────────────────────────────────────────────
    # TIER 1 — Revenue & Efficiency
    # ─────────────────────────────────────────────────────────────────────────
    section_header("Tier 1 — Revenue & Efficiency")
    t1 = st.columns(7)
    with t1[0]:
        kpi_card("Total Revenue",   f"₪{total_rev / 1e6:.1f}M",  f"{n_months}-month period", tr_rev, tc_rev)
    with t1[1]:
        kpi_card("RevPAR",          f"₪{avg_revpar:,}",           "Rev / available room", tr_revpar, tc_revpar)
    with t1[2]:
        kpi_card("ADR",             f"₪{avg_adr:,}",              "Avg daily rate", tr_adr, tc_adr)
    with t1[3]:
        kpi_card("GOPPAR",          f"₪{avg_goppar:,}",           "Gross op. profit / room", tr_goppar, tc_goppar)
    with t1[4]:
        kpi_card("NOI",             f"₪{noi / 1e6:.1f}M",         "Net operating income", tr_noi, tc_noi)
    with t1[5]:
        kpi_card("Operating Margin",f"{op_margin:.1f}%",           "NOI / Revenue", tr_opm, tc_opm)
    with t1[6]:
        kpi_card("EBITDA Margin",   f"{ebitda_marg:.1f}%",         "EBITDA / Revenue")

    st.markdown("<br>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # TIER 2 — Operations & Asset
    # ─────────────────────────────────────────────────────────────────────────
    section_header("Tier 2 — Operations & Asset")
    t2 = st.columns(7)
    with t2[0]:
        kpi_card("Avg Occupancy",     f"{avg_occ:.1f}%",              "Portfolio avg", tr_occ, tc_occ)
    with t2[1]:
        kpi_card("Vacancy Rate",      f"{vacancy:.1f}%",              "Unoccupied capacity", tr_vac, tc_vac)
    with t2[2]:
        kpi_card("CPOR",              f"₪{cpor:,.0f}",                "Cost / occ. room / mo", tr_cpor, tc_cpor)
    with t2[3]:
        _epor_above = avg_epor > EPOR_BENCHMARK
        kpi_card("EPOR",              f"{avg_epor:.1f} kWh",
                 f"Benchmark: {EPOR_BENCHMARK:.0f} kWh",
                 "▲ Above" if _epor_above else "▼ Below",
                 RED if _epor_above else ACCENT)
    with t2[4]:
        kpi_card("₪ Rev. at Risk",    f"₪{rev_at_risk_annual / 1e6:.1f}M/yr",
                 f"{len(_high_risk)} high-risk tenants")
    with t2[5]:
        kpi_card("Staff / Room",      f"{staff_room:.2f}",            f"{staff_total} ÷ {TOTAL_ROOMS}")
    with t2[6]:
        kpi_card("Avg Satisfaction",  f"{avg_sat}/10",                "Tenant survey score")

    st.markdown("<br>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 1 — Income & NOI  |  RevPAR / ADR / GOPPAR
    # ─────────────────────────────────────────────────────────────────────────
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        section_header("Income & NOI Trend")
        _noi_vals = (s_income["Total"] - s_costs["Total (₪)"]).tolist()
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        fig1.add_trace(
            go.Bar(
                x=months_x,
                y=s_income["Total"].tolist(),
                name="Monthly Revenue (₪)",
                marker_color=ACCENT,
                opacity=0.85,
            ),
            secondary_y=False,
        )
        fig1.add_trace(
            go.Scatter(
                x=months_x,
                y=_noi_vals,
                name="NOI (₪)",
                mode="lines+markers",
                line=dict(color=YELLOW, width=2),
                marker=dict(size=5),
            ),
            secondary_y=True,
        )
        fig1.update_layout(_CHART_LAYOUT)
        fig1.update_layout(height=320)
        fig1.update_yaxes(
            title_text="Revenue (₪)", secondary_y=False,
            gridcolor="#2A2F3B", tickformat=",",
        )
        fig1.update_yaxes(
            title_text="NOI (₪)", secondary_y=True,
            gridcolor="#2A2F3B", tickformat=",",
        )
        _force_two_decimal_hover(fig1)
        st.plotly_chart(fig1, use_container_width=True)

    with r1c2:
        section_header("RevPAR Decomposition — Rate vs. Volume")
        _occ_pct_series = s_occ[_occ_cols].mean(axis=1).values
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(
            go.Bar(
                x=months_x, y=_occ_pct_series.tolist(),
                name="Occupancy %", marker_color=ACCENT, opacity=0.45,
            ),
            secondary_y=True,
        )
        fig2.add_trace(
            go.Scatter(
                x=months_x, y=s_rev_pu["ADR (₪)"].tolist(),
                name="ADR (₪)", mode="lines+markers",
                line=dict(color="#0077FF", width=2.5), marker=dict(size=5),
            ),
            secondary_y=False,
        )
        fig2.add_trace(
            go.Scatter(
                x=months_x, y=s_rev_pu["RevPAR (₪)"].tolist(),
                name="RevPAR (₪)", mode="lines+markers",
                line=dict(color=YELLOW, width=2, dash="dash"), marker=dict(size=4),
            ),
            secondary_y=False,
        )
        fig2.update_layout(_CHART_LAYOUT)
        fig2.update_layout(height=320)
        fig2.update_yaxes(title_text="₪ / Room", secondary_y=False,
                          gridcolor="#2A2F3B", tickformat=",")
        fig2.update_yaxes(title_text="Occupancy %", secondary_y=True,
                          gridcolor="#2A2F3B", range=[0, 100])
        _force_two_decimal_hover(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────    # ROW 1b — GOPPAR vs CPOR Spread  |  EPOR by Project
    # ─────────────────────────────────────────────────────────────────────
    r1b_c1, r1b_c2 = st.columns(2)

    with r1b_c1:
        section_header("GOPPAR vs. CPOR — Efficiency Spread")
        _cpor_vals = s_cpor["CPOR (₪)"].tolist()
        fig_sp = go.Figure()
        fig_sp.add_trace(go.Scatter(
            x=months_x, y=s_rev_pu["GOPPAR (₪)"].tolist(),
            name="GOPPAR (₪)", mode="lines+markers",
            line=dict(color=ACCENT, width=2.5), marker=dict(size=5),
        ))
        fig_sp.add_trace(go.Scatter(
            x=months_x, y=_cpor_vals,
            name="CPOR (₪)", mode="lines+markers",
            line=dict(color=RED, width=2.5), marker=dict(size=5),
        ))
        fig_sp.update_layout(_CHART_LAYOUT)
        fig_sp.update_layout(
            height=320,
            yaxis=dict(gridcolor="#2A2F3B", tickformat=",", title="₪ / Room"),
        )
        _force_two_decimal_hover(fig_sp)
        st.plotly_chart(fig_sp, use_container_width=True)

    with r1b_c2:
        section_header("Energy per Occupied Room (EPOR)")
        _epor_sorted = df_epor_project.sort_values("EPOR (kWh)", ascending=True)
        _epor_colors = [RED if v > EPOR_BENCHMARK else ACCENT
                        for v in _epor_sorted["EPOR (kWh)"]]
        fig_ep = go.Figure(go.Bar(
            x=_epor_sorted["EPOR (kWh)"].tolist(),
            y=_epor_sorted["Project"].tolist(),
            orientation="h", marker_color=_epor_colors,
            text=[f"{v:.1f} kWh" for v in _epor_sorted["EPOR (kWh)"]],
            textposition="outside", opacity=0.9,
        ))
        fig_ep.add_vline(
            x=EPOR_BENCHMARK, line_dash="dash", line_color=YELLOW,
            annotation_text=f"Benchmark: {EPOR_BENCHMARK:.0f} kWh",
            annotation_position="top right",
            annotation_font_color=YELLOW,
        )
        fig_ep.update_layout(_CHART_LAYOUT)
        fig_ep.update_layout(
            height=320,
            xaxis=dict(gridcolor="#2A2F3B", title="kWh / Occupied Room"),
            yaxis=dict(gridcolor="#2A2F3B"),
        )
        _force_two_decimal_hover(fig_ep)
        st.plotly_chart(fig_ep, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────
    # RETENTION INTELLIGENCE — Tenant Churn Risk
    # ─────────────────────────────────────────────────────────────────────
    section_header("🔒 Retention Intelligence — Tenant Churn Risk")
    ri_c1, ri_c2 = st.columns(2)

    with ri_c1:
        _churn_sorted = df_tenants.sort_values("Churn Risk", ascending=True)
        _risk_colors = [RED if r >= 0.60 else YELLOW if r >= 0.30 else ACCENT
                        for r in _churn_sorted["Churn Risk"]]
        fig_ch = go.Figure(go.Bar(
            x=_churn_sorted["Churn Risk"].tolist(),
            y=_churn_sorted["Tenant"].tolist(),
            orientation="h", marker_color=_risk_colors,
            text=[f"{r:.0%}" for r in _churn_sorted["Churn Risk"]],
            textposition="outside", opacity=0.9,
        ))
        fig_ch.update_layout(_CHART_LAYOUT)
        fig_ch.update_layout(
            height=440,
            xaxis=dict(range=[0, 1.15], gridcolor="#2A2F3B",
                       title="Churn Risk Score", tickformat=".0%"),
            yaxis=dict(gridcolor="#2A2F3B"),
        )
        _force_two_decimal_hover(fig_ch)
        st.plotly_chart(fig_ch, use_container_width=True)

    with ri_c2:
        _tl = df_tenants.copy()
        _tl["Expiry"] = pd.to_datetime(_tl["Lease Expiry"])
        _sev_map = {"🔴 High Risk": RED, "🟡 Medium": YELLOW, "🟢 Low": ACCENT}
        _tl_colors = [_sev_map.get(r, ACCENT) for r in _tl["Risk Level"]]
        fig_tl = go.Figure(go.Scatter(
            x=_tl["Expiry"], y=_tl["Monthly Rent (₪)"],
            mode="markers+text",
            marker=dict(size=14, color=_tl_colors, opacity=0.85,
                        line=dict(width=1, color="#FFFFFF")),
            text=_tl["Tenant"], textposition="top center",
            textfont=dict(size=8, color="#E8E8E8"),
        ))
        fig_tl.update_layout(_CHART_LAYOUT)
        fig_tl.update_layout(
            height=440,
            xaxis=dict(gridcolor="#2A2F3B", title="Lease Expiry Date"),
            yaxis=dict(gridcolor="#2A2F3B", tickformat=",", title="Monthly Rent (₪)"),
        )
        _force_two_decimal_hover(fig_tl)
        st.plotly_chart(fig_tl, use_container_width=True)

    _at_risk_display = (
        df_tenants[df_tenants["Churn Risk"] >= 0.30]
        .sort_values("Churn Risk", ascending=False)
        [["Tenant", "Project", "Risk Level", "Churn Risk", "Monthly Rent (₪)", "Lease Expiry"]]
    )
    if not _at_risk_display.empty:
        st.dataframe(
            _at_risk_display.style.format({
                "Churn Risk": "{:.1%}", "Monthly Rent (₪)": "₪{:,.0f}",
            }),
            use_container_width=True, hide_index=True,
        )

    # ─────────────────────────────────────────────────────────────────────    # ROW 2 — Room Availability  |  Manpower
    # ─────────────────────────────────────────────────────────────────────────
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        section_header("Room Availability by Type")
        fig3 = go.Figure()
        _room_series = [
            ("Office (%)",  ACCENT),
            ("Meeting (%)", "#0077FF"),
            ("Common (%)",  "#9B59B6"),
        ]
        for col, color in _room_series:
            fig3.add_trace(go.Bar(
                x=months_x,
                y=s_rooms[col].tolist(),
                name=col,
                marker_color=color,
                opacity=0.85,
            ))
        fig3.update_layout(_CHART_LAYOUT)
        fig3.update_layout(
            height=320,
            barmode="group",
            yaxis=dict(range=[50, 100], gridcolor="#2A2F3B", title="Availability (%)"),
        )
        _force_two_decimal_hover(fig3)
        st.plotly_chart(fig3, use_container_width=True)

    with r2c2:
        section_header("Manpower Over Time")
        fig4 = go.Figure()
        _man_series = [
            ("Available",   ACCENT),
            ("On Leave",    YELLOW),
            ("Contractors", "#0077FF"),
        ]
        for col, color in _man_series:
            fig4.add_trace(go.Bar(
                x=months_x,
                y=s_man[col].tolist(),
                name=col,
                marker_color=color,
                opacity=0.85,
            ))
        fig4.update_layout(_CHART_LAYOUT)
        fig4.update_layout(
            height=320,
            barmode="stack",
            yaxis=dict(gridcolor="#2A2F3B", title="Headcount"),
        )
        _force_two_decimal_hover(fig4)
        st.plotly_chart(fig4, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 3 — Cost Breakdown  |  Staff Utilization
    # ─────────────────────────────────────────────────────────────────────────
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        section_header("Cost Breakdown")
        fig5 = go.Figure()
        _cost_series = [
            ("Energy (₪)",      "#FF6B35"),
            ("Labor (₪)",       "#E74C3C"),
            ("Maintenance (₪)", YELLOW),
            ("Other (₪)",       "#95A5A6"),
        ]
        for col, color in _cost_series:
            fig5.add_trace(go.Bar(
                x=months_x,
                y=s_costs[col].tolist(),
                name=col,
                marker_color=color,
                opacity=0.85,
            ))
        fig5.update_layout(_CHART_LAYOUT)
        fig5.update_layout(
            height=320,
            barmode="stack",
            yaxis=dict(gridcolor="#2A2F3B", tickformat=",", title="Cost (₪)"),
        )
        _force_two_decimal_hover(fig5)
        st.plotly_chart(fig5, use_container_width=True)

    with r3c2:
        section_header("Staff Utilization by Department")
        _util   = df_staff_by_dept["Utilization (%)"].tolist()
        _depts  = df_staff_by_dept["Department"].tolist()
        _colors = [ACCENT if u >= 90 else YELLOW if u >= 80 else RED for u in _util]
        fig6 = go.Figure(go.Bar(
            x=_util,
            y=_depts,
            orientation="h",
            marker_color=_colors,
            text=[f"{u}%" for u in _util],
            textposition="outside",
            opacity=0.9,
        ))
        fig6.update_layout(_CHART_LAYOUT)
        fig6.update_layout(
            height=320,
            xaxis=dict(range=[0, 112], gridcolor="#2A2F3B", title="Utilization (%)"),
            yaxis=dict(gridcolor="#2A2F3B"),
        )
        _force_two_decimal_hover(fig6)
        st.plotly_chart(fig6, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────
    # ASSET RATIO TABLE — Cap Rate & GRM
    # ─────────────────────────────────────────────────────────────────────────
    section_header("Asset Ratios — Cap Rate & GRM")
    st.dataframe(
        df_cap_table.style.format({
            "Asset Value (₪B)": "{:.2f}",
            "Annual NOI (₪M)":  "{:.1f}",
            "Cap Rate (%)":     "{:.2f}%",
            "GRM":              "{:.2f}x",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # ─────────────────────────────────────────────────────────────────────────
    # ALOS FOOTNOTE
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    _alos_col, _, _ = st.columns([2, 1, 1])
    with _alos_col:
        st.metric(
            label="📅 Avg Length of Stay / Lease (portfolio)",
            value=f"{avg_alos} months",
            delta=f"{ALOS_BY_MONTH[-1] - ALOS_BY_MONTH[0]:+.1f} mo over 12m",
        )
