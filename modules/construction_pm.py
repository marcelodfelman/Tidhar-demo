"""
construction_pm.py - Construction Project Manager
Schedule-aware dashboard focused on where each project should be today,
where it actually is, and the immediate financial exposure.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

from style import section_header, kpi_card, alert_card, CARD_BG, ACCENT, RED, YELLOW
import data as _data


_HAS_CONSTRUCTION_DATA = all(
    hasattr(_data, name)
    for name in [
        "CONSTRUCTION_PROJECTS",
        "get_construction_snapshot",
        "get_construction_status_table",
        "get_construction_progress_curve",
        "get_construction_gantt",
        "df_construction_risks",
        "df_construction_milestones",
    ]
)

CONSTRUCTION_PROJECTS = getattr(_data, "CONSTRUCTION_PROJECTS", ["Demo Construction Project"])
REF_DATE = getattr(_data, "REF_DATE", date(2026, 3, 1))


def _fallback_snapshot(_project: str) -> dict:
    return {
        "planned_progress": 64.0,
        "actual_progress": 58.0,
        "schedule_var": -6.0,
        "spi": 0.91,
        "cpi": 0.96,
        "delay_days": 18,
        "planned_cost": 120_000_000.0,
        "actual_cost": 126_000_000.0,
        "budget_var_pct": 5.0,
        "eac_var_pct": 4.2,
        "delay_cost_low": 70_000.0,
        "delay_cost_high": 250_000.0,
        "critical_risks": 2,
        "high_risks": 3,
        "overdue_milestones": 2,
        "lti_ytd": 3,
        "trir": 1.8,
        "open_rfis": 11,
    }


def _fallback_status_table(project: str = "All Projects", as_of_date=None) -> pd.DataFrame:
    _ = as_of_date
    rows = [
        {
            "Project": p,
            "Status": "Amber",
            "Planned % Today": 64.0,
            "Actual % Today": 58.0,
            "Gap (pts)": -6.0,
            "SPI": 0.91,
            "CPI": 0.96,
            "Delay Days": 18,
            "EAC Var (%)": 4.2,
            "Overdue Critical": 2,
            "Open RFIs": 11,
        }
        for p in (CONSTRUCTION_PROJECTS if project == "All Projects" else [project])
    ]
    return pd.DataFrame(rows)


def _fallback_progress_curve(project: str = "All Projects") -> pd.DataFrame:
    _ = project
    return pd.DataFrame(
        {
            "Month": ["Oct 2025", "Nov 2025", "Dec 2025", "Jan 2026", "Feb 2026", "Mar 2026"],
            "Planned (%)": [36, 44, 51, 57, 61, 64],
            "Actual (%)": [31, 38, 45, 50, 54, 58],
        }
    )


def _fallback_gantt(project: str = "All Projects", as_of_date=None) -> pd.DataFrame:
    _ = as_of_date
    proj = CONSTRUCTION_PROJECTS[0] if project == "All Projects" else project
    rows = [
        {"Project": proj, "Task": "Foundations", "Track": "Baseline", "Start": pd.Timestamp("2025-10-01"), "Finish": pd.Timestamp("2025-12-15"), "State": "Baseline", "Is Critical": True},
        {"Project": proj, "Task": "Foundations", "Track": "Forecast/Actual", "Start": pd.Timestamp("2025-10-05"), "Finish": pd.Timestamp("2025-12-28"), "State": "Done", "Is Critical": True},
        {"Project": proj, "Task": "Structure", "Track": "Baseline", "Start": pd.Timestamp("2025-12-16"), "Finish": pd.Timestamp("2026-02-20"), "State": "Baseline", "Is Critical": True},
        {"Project": proj, "Task": "Structure", "Track": "Forecast/Actual", "Start": pd.Timestamp("2025-12-29"), "Finish": pd.Timestamp("2026-03-12"), "State": "Delayed", "Is Critical": True},
        {"Project": proj, "Task": "MEP Rough-In", "Track": "Baseline", "Start": pd.Timestamp("2026-02-21"), "Finish": pd.Timestamp("2026-04-10"), "State": "Baseline", "Is Critical": True},
        {"Project": proj, "Task": "MEP Rough-In", "Track": "Forecast/Actual", "Start": pd.Timestamp("2026-03-13"), "Finish": pd.Timestamp("2026-04-28"), "State": "In Progress", "Is Critical": True},
    ]
    return pd.DataFrame(rows)


get_construction_snapshot = getattr(_data, "get_construction_snapshot", _fallback_snapshot)
get_construction_status_table = getattr(_data, "get_construction_status_table", _fallback_status_table)
get_construction_progress_curve = getattr(_data, "get_construction_progress_curve", _fallback_progress_curve)
get_construction_gantt = getattr(_data, "get_construction_gantt", _fallback_gantt)
df_construction_risks = getattr(
    _data,
    "df_construction_risks",
    pd.DataFrame(
        {
            "Risk ID": ["R-001"],
            "Project": [CONSTRUCTION_PROJECTS[0]],
            "Category": ["Schedule"],
            "Description": ["Fallback data: update data.py construction block."],
            "Severity": ["High"],
            "Probability (%)": [50],
            "Impact (₪)": [3_000_000],
            "Owner": ["PMO"],
        }
    ),
)
df_construction_milestones = getattr(
    _data,
    "df_construction_milestones",
    pd.DataFrame(
        {
            "Project": [CONSTRUCTION_PROJECTS[0]],
            "Milestone": ["Fallback milestone"],
            "Planned Date": ["2026-03-01"],
            "Forecast Date": ["2026-03-20"],
            "Status": ["Open"],
        }
    ),
)


_CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=CARD_BG,
    plot_bgcolor=CARD_BG,
    font=dict(color="#E8E8E8", size=11),
    margin=dict(l=42, r=20, t=36, b=36),
    legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10, font_color="#E8E8E8", orientation="h", y=1.1),
)


def _trend_text(value: float, invert: bool = False):
    if abs(value) < 0.1:
        return ("- Stable", YELLOW)
    positive = value > 0 if not invert else value < 0
    arrow = "▲" if value > 0 else "▼"
    color = ACCENT if positive else RED
    return (f"{arrow} {abs(value):.1f}", color)


def render() -> None:
    section_header("Construction Project Manager")
    if not _HAS_CONSTRUCTION_DATA:
        st.warning(
            "Construction dataset not found in data.py on this environment. "
            "Running with fallback demo data. Sync latest data.py to enable full analytics.",
            icon="⚠️",
        )
    st.caption(
        "Planned = expected completion by today (baseline). "
        "Actual = certified execution by today. Gap = Actual - Planned."
    )

    p1, _ = st.columns([3, 2])
    with p1:
        project = st.selectbox("Project Scope", ["All Projects"] + CONSTRUCTION_PROJECTS, index=0)

    snap = get_construction_snapshot(project)
    status_df = get_construction_status_table(project=project, as_of_date=REF_DATE)
    progress_df = get_construction_progress_curve(project=project)
    gantt_df = get_construction_gantt(project=project, as_of_date=REF_DATE)

    # Executive KPI row
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    tr_sched, tc_sched = _trend_text(snap["schedule_var"])
    tr_eac, tc_eac = _trend_text(snap["eac_var_pct"], invert=True)

    with k1:
        kpi_card("Planned Today", f"{snap['planned_progress']:.1f}%", "Where we should be now")
    with k2:
        kpi_card("Actual Today", f"{snap['actual_progress']:.1f}%", "Where we really are now")
    with k3:
        kpi_card("Gap", f"{snap['schedule_var']:+.1f} pts", "Actual - Planned", tr_sched, tc_sched)
    with k4:
        kpi_card("SPI", f"{snap['spi']:.2f}", "Schedule performance")
    with k5:
        kpi_card("CPI", f"{snap['cpi']:.2f}", "Cost performance")
    with k6:
        kpi_card("Delay Days", str(snap["delay_days"]), "Forecast finish - baseline")

    st.markdown("<br>", unsafe_allow_html=True)

    k7, k8, k9, k10 = st.columns(4)
    with k7:
        kpi_card("EAC Variance", f"{snap['eac_var_pct']:+.1f}%", "Estimate at completion", tr_eac, tc_eac)
    with k8:
        kpi_card("Critical Risks", str(snap["critical_risks"]), f"High risks: {snap['high_risks']}")
    with k9:
        kpi_card("Overdue Milestones", str(snap["overdue_milestones"]), "Planned date passed")
    with k10:
        kpi_card("Open RFIs", str(snap["open_rfis"]), "Pending engineering answers")

    st.markdown("<br>", unsafe_allow_html=True)

    if snap["spi"] < 0.93:
        alert_card(
            "Schedule Recovery Needed",
            f"SPI is <b>{snap['spi']:.2f}</b>. Trigger a 24h recovery plan on critical-path activities.",
        )
    if snap["cpi"] < 0.95 or snap["eac_var_pct"] > 3.0:
        alert_card(
            "Budget Escalation",
            f"CPI is <b>{snap['cpi']:.2f}</b> and EAC variance is <b>{snap['eac_var_pct']:+.1f}%</b>. "
            "Freeze non-critical commitments and re-baseline forecast-to-complete.",
        )
    if snap["delay_days"] > 0:
        alert_card(
            "Delay Cost Exposure",
            f"Current delay is <b>{snap['delay_days']} days</b>. Estimated exposure range: "
            f"<b>₪{snap['delay_cost_low']*snap['delay_days']:,.0f}</b> to "
            f"<b>₪{snap['delay_cost_high']*snap['delay_days']:,.0f}</b>.",
        )

    c1, c2 = st.columns(2)

    with c1:
        section_header("Where Should We Be Today? Planned vs Actual")
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(
                x=progress_df["Month"],
                y=progress_df["Planned (%)"],
                mode="lines+markers",
                name="Planned",
                line=dict(color="#0077FF", width=2.4),
            )
        )
        fig1.add_trace(
            go.Scatter(
                x=progress_df["Month"],
                y=progress_df["Actual (%)"],
                mode="lines+markers",
                name="Actual",
                line=dict(color=ACCENT, width=2.4),
            )
        )
        fig1.update_layout(_CHART_LAYOUT)
        fig1.update_layout(height=320)
        fig1.update_yaxes(title_text="Completion (%)", range=[0, 100], gridcolor="#2A2F3B")
        fig1.update_xaxes(gridcolor="#2A2F3B")
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        section_header("As-of Cost Signal")
        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(
                x=["Planned Cost", "Actual Cost"],
                y=[snap["planned_cost"] / 1e6, snap["actual_cost"] / 1e6],
                marker_color=["#4E79A7", RED],
                opacity=0.88,
                name="As-of Today",
            )
        )
        fig2.update_layout(_CHART_LAYOUT)
        fig2.update_layout(height=320)
        fig2.update_yaxes(title_text="Cost (M₪)", gridcolor="#2A2F3B")
        fig2.update_xaxes(gridcolor="#2A2F3B")
        st.plotly_chart(fig2, use_container_width=True)

    section_header("Project Status Board (Action-Oriented)")
    if not status_df.empty:
        _table = status_df.copy()
        _table["Status"] = _table["Status"].map({"Red": "Delayed", "Amber": "At Risk", "Green": "On Track"})
        st.dataframe(
            _table[[
                "Project", "Status", "Planned % Today", "Actual % Today", "Gap (pts)",
                "SPI", "CPI", "Delay Days", "EAC Var (%)", "Overdue Critical", "Open RFIs",
            ]].style.format({
                "Planned % Today": "{:.1f}%",
                "Actual % Today": "{:.1f}%",
                "Gap (pts)": "{:+.1f}",
                "SPI": "{:.2f}",
                "CPI": "{:.2f}",
                "EAC Var (%)": "{:+.1f}%",
            }),
            use_container_width=True,
            height=260,
        )

    section_header("Dynamic Gantt - Baseline vs Forecast/Actual")
    if not gantt_df.empty:
        fig_gantt = px.timeline(
            gantt_df,
            x_start="Start",
            x_end="Finish",
            y="Task",
            color="Track",
            color_discrete_map={"Baseline": "#5B6274", "Forecast/Actual": "#00CC99"},
            hover_data={
                "Project": True,
                "Track": True,
                "State": True,
                "Is Critical": True,
                "Start": True,
                "Finish": True,
                "Task": False,
            },
        )
        fig_gantt.update_layout(_CHART_LAYOUT)
        fig_gantt.update_layout(height=max(340, min(760, len(gantt_df["Task"].unique()) * 24)))
        _today_ts = pd.Timestamp(REF_DATE)
        # add_vline can fail with Timestamp on some Plotly/Pandas combinations,
        # so we draw an explicit shape + annotation instead.
        fig_gantt.add_shape(
            type="line",
            x0=_today_ts,
            x1=_today_ts,
            y0=0,
            y1=1,
            xref="x",
            yref="paper",
            line=dict(color=YELLOW, width=2, dash="dash"),
        )
        fig_gantt.add_annotation(
            x=_today_ts,
            y=1.03,
            xref="x",
            yref="paper",
            text="Today",
            showarrow=False,
            font=dict(color=YELLOW),
        )
        fig_gantt.update_yaxes(autorange="reversed", gridcolor="#2A2F3B")
        fig_gantt.update_xaxes(gridcolor="#2A2F3B")
        st.plotly_chart(fig_gantt, use_container_width=True)
    else:
        st.info("No Gantt data available for selected scope.")

    section_header("Operational Detail: Risk Register")
    risks = df_construction_risks.copy()
    if project != "All Projects":
        risks = risks[risks["Project"] == project].copy()

    if not risks.empty:
        risks["Expected Exposure (₪)"] = risks["Probability (%)"] / 100.0 * risks["Impact (₪)"]
        risks = risks.sort_values("Expected Exposure (₪)", ascending=False)
        st.dataframe(
            risks[[
                "Risk ID", "Project", "Category", "Description", "Severity",
                "Probability (%)", "Impact (₪)", "Expected Exposure (₪)", "Owner",
            ]].style.format({
                "Probability (%)": "{:.0f}%",
                "Impact (₪)": "₪{:,.0f}",
                "Expected Exposure (₪)": "₪{:,.0f}",
            }),
            use_container_width=True,
            height=320,
        )
    else:
        st.info("No risks found for the selected project scope.")

    section_header("Milestone Watchlist")
    ms = df_construction_milestones.copy()
    if project != "All Projects":
        ms = ms[ms["Project"] == project].copy()

    if not ms.empty:
        ms["Planned Date"] = pd.to_datetime(ms["Planned Date"])
        ms["Forecast Date"] = pd.to_datetime(ms["Forecast Date"])
        ms["Slippage (days)"] = (ms["Forecast Date"] - ms["Planned Date"]).dt.days
        ms["Planned Date"] = ms["Planned Date"].dt.date
        ms["Forecast Date"] = ms["Forecast Date"].dt.date
        st.dataframe(ms, use_container_width=True, height=230)

    s1, s2 = st.columns(2)
    with s1:
        kpi_card("LTI (YTD)", str(snap["lti_ytd"]), "Lost-time incidents")
    with s2:
        kpi_card("TRIR (YTD)", f"{snap['trir']:.2f}", "Incidents per 200k work hours")
