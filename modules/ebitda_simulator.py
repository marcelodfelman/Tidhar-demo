"""
ebitda_simulator.py — Strategic EBITDA Simulator
All cost coefficients are user-adjustable via an advanced panel.
Includes board-floor reference line and steel breakeven KPI.
"""

import streamlit as st
import plotly.graph_objects as go

from data import (
    BASELINE_EBITDA,
    STEEL_EBITDA_SENSITIVITY,
    RATE_COST_PER_100BPS,
    LABOR_EBITDA_SENSITIVITY,
    EBITDA_TARGET_FLOOR,
)
from style import section_header, kpi_card, ACCENT, RED, CARD_BG, TEXT, NAVY


def render():
    """Main render function for the EBITDA Simulator page."""

    section_header("Strategic EBITDA Simulator")

    st.markdown(
        f"Baseline EBITDA: **₪{BASELINE_EBITDA:,.0f}** · "
        f"Board floor: **₪{EBITDA_TARGET_FLOOR:,.0f}**  \n"
        "Adjust the macro levers. Expand **Advanced** to tune the cost-model coefficients."
    )

    # ── Primary levers ──────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        steel_pct = st.slider(
            "🔩 Steel Price Change (%)",
            min_value=-20, max_value=50, value=0, step=1,
            help="Positive = cost increase, Negative = cost decrease",
        )
    with col2:
        rate_bps = st.slider(
            "📈 Interest Rate Impact (bps)",
            min_value=0, max_value=200, value=0, step=5,
            help="Each 100 bps ≈ 1% additional financing cost",
        )
    with col3:
        labor_eff = st.slider(
            "👷 Labor Efficiency (%)",
            min_value=50, max_value=120, value=100, step=1,
            help="Below 100% = inefficiency, Above 100% = productivity gain",
        )

    # ── Advanced coefficient tuning ─────────────────────────────────────────
    with st.expander("⚙️  Advanced — Cost Model Coefficients", expanded=False):
        st.markdown(
            "These coefficients translate macro changes into EBITDA impact. "
            "Calibrate them to Tidhar's actual cost structure for board scenarios."
        )
        a1, a2, a3, a4 = st.columns(4)
        with a1:
            steel_sens = st.number_input(
                "Steel sensitivity (EBITDA % per 1% steel)",
                0.05, 1.00, float(STEEL_EBITDA_SENSITIVITY), 0.05,
                format="%.2f",
                help="Default 0.40 = 1% steel rise erodes 0.40% EBITDA",
            )
        with a2:
            rate_cost = st.number_input(
                "Rate cost (₪ per 100 bps)",
                100_000, 10_000_000, int(RATE_COST_PER_100BPS), 100_000,
                format="%d",
            )
        with a3:
            labor_sens = st.number_input(
                "Labor sensitivity (EBITDA % per 1% eff)",
                0.05, 1.00, float(LABOR_EBITDA_SENSITIVITY), 0.05,
                format="%.2f",
            )
        with a4:
            target_floor = st.number_input(
                "Board target floor (₪)",
                10_000_000, 80_000_000, int(EBITDA_TARGET_FLOOR), 1_000_000,
                format="%d",
            )

    # ── Live calculations ────────────────────────────────────────────────────
    steel_impact = -BASELINE_EBITDA * (steel_pct / 100) * steel_sens
    rate_impact  = -(rate_bps / 100) * rate_cost
    labor_impact =  BASELINE_EBITDA * ((labor_eff - 100) / 100) * labor_sens
    projected    = BASELINE_EBITDA + steel_impact + rate_impact + labor_impact
    delta        = projected - BASELINE_EBITDA
    delta_pct    = (delta / BASELINE_EBITDA) * 100
    above_floor  = projected - target_floor
    breached     = projected < target_floor

    # ── KPI Cards ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card("Projected EBITDA", f"₪{projected:,.0f}",
                 f"{'▲' if delta >= 0 else '▼'} {abs(delta_pct):.1f}% vs baseline")
    with k2:
        kpi_card("Net Impact", f"₪{delta:+,.0f}",
                 "Gain" if delta >= 0 else "Loss")
    with k3:
        kpi_card("vs Board Floor", f"₪{above_floor:+,.0f}",
                 "🔴 Floor BREACHED" if breached else "✅ Above floor")
    with k4:
        # Breakeven: at what steel % does projected hit the floor?
        denom = BASELINE_EBITDA * steel_sens
        if denom != 0:
            breakeven_steel = (
                (BASELINE_EBITDA + rate_impact + labor_impact - target_floor) / denom * 100
            )
            kpi_card("Steel Breakeven", f"+{breakeven_steel:.1f}%",
                     "Max steel rise before floor breach")
        else:
            kpi_card("Steel Breakeven", "N/A", "")

    # ── Waterfall Chart ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("EBITDA Waterfall — Impact Breakdown")

    labels = ["Baseline EBITDA", "Steel Price", "Interest Rate", "Labor Efficiency", "Projected EBITDA"]
    measures = ["absolute", "relative", "relative", "relative", "total"]
    values = [BASELINE_EBITDA, steel_impact, rate_impact, labor_impact, projected]

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=measures,
        x=labels,
        y=values,
        text=[f"₪{v:+,.0f}" if m == "relative" else f"₪{v:,.0f}" for v, m in zip(values, measures)],
        textposition="outside",
        textfont=dict(size=12, color=TEXT),
        connector=dict(line=dict(color=ACCENT, width=1, dash="dot")),
        increasing=dict(marker=dict(color=ACCENT)),
        decreasing=dict(marker=dict(color=RED)),
        totals=dict(marker=dict(color=NAVY)),
    ))

    # Board floor reference line
    fig.add_hline(
        y=target_floor,
        line_dash="dash", line_color=RED, line_width=1.5,
        annotation_text=f"Board Floor ₪{target_floor/1e6:.0f}M",
        annotation_position="top left",
        annotation_font=dict(color=RED, size=11),
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color="#FFFFFF"),
        height=480,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis=dict(title="₪ (ILS)", tickformat=",",
                   title_font=dict(color="#FFFFFF"), tickfont=dict(color="#E0E0E0")),
        xaxis=dict(tickfont=dict(color="#E0E0E0")),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Narrative insights ───────────────────────────────────────────────────
    insights = []
    if breached:
        insights.append(
            f"🔴 **Board floor BREACHED** — projected EBITDA is "
            f"₪{abs(above_floor):,.0f} below the ₪{target_floor/1e6:.0f}M target."
        )
    if steel_pct > 10:
        insights.append(f"⚠ Steel prices at +{steel_pct}% remove ₪{abs(steel_impact):,.0f} from EBITDA.")
    if rate_bps >= 100:
        insights.append(f"⚠ {rate_bps} bps rate rise adds ₪{abs(rate_impact):,.0f} in financing costs.")
    if labor_eff < 80:
        insights.append(f"⚠ Labor at {labor_eff}% efficiency costs ₪{abs(labor_impact):,.0f} in productivity drag.")
    if labor_eff > 105:
        insights.append(f"✅ Labor efficiency at {labor_eff}% contributes +₪{labor_impact:,.0f}.")
    if not breached and delta >= 0:
        insights.append(f"✅ Net effect is positive: +₪{delta:,.0f} above baseline.")

    if insights:
        st.markdown("---")
        section_header("AI Insights")
        for ins in insights:
            st.markdown(f"- {ins}")
