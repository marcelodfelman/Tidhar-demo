# Analytics Dashboard — Implementation Plan
**Feature:** `📈 Analytics Dashboard` — PowerBI-style business intelligence section  
**Date:** March 2, 2026  
**Author:** GitHub Copilot / Deeply  
**Status:** ✅ Implemented (Phase 1 Quick Wins applied March 2026)

---

## 1. Overview

A new **Analytics Dashboard** module added to the Tidhar Decision Intelligence Portal. It delivers a PowerBI-style layout with:

- **Time-range filter** — `st.select_slider()` over the portfolio's 12-month window
- **Tier 1 KPIs** — 7 revenue & efficiency cards with ▲/▼ MoM trend indicators
- **Tier 2 KPIs** — 7 operations & asset cards (EPOR + ₪ Revenue at Risk replaced Staff Available + Tenant Retention)
- **8 chart panels** — arranged in a 2-column grid (original 6 + RevPAR Decomposition + GOPPAR/CPOR Spread + EPOR)
- **Retention Intelligence** — churn risk waterfall + lease expiry scatter + at-risk data table
- **Asset Ratio Table** — per-project Cap Rate, GRM, NOI (point-in-time)
- **ALOS footnote** — Average Length of Stay / Lease as a single `st.metric`

All data lives exclusively in `data.py`. All rendering logic lives in `modules/analytics_dashboard.py`. The module follows the exact same pattern as the three existing modules.

---

## 2. Files Changed

| File | Change Type | Purpose |
|---|---|---|
| `data.py` | Extended | New constants + 7 new DataFrames |
| `modules/analytics_dashboard.py` | Created | Full dashboard render module |
| `app.py` | Two edits | Import + nav radio + router branch |
| `modules/ai_agent.py` | Extended | Two new detection rules |

---

## 3. Data Layer — `data.py` Changes

### 3.1 New Constants (Section 5b)

```python
ROOMS_PER_PROJECT = { ... }   # dict[project → room count]; sum = TOTAL_ROOMS = 1,220
TOTAL_ROOMS = 1_220

SQM_PER_PROJECT = { ... }     # dict[project → m²] for CPOR/sqm calculations

ASSET_VALUE_PER_PROJECT = {   # dict[project → ₪]; sum ≈ ₪12.4B
    "Tidhar Tower Givatayim":    3_800_000_000,
    "Park HaMada Rehovot":       2_500_000_000,
    "Bnei Brak Business Center": 1_600_000_000,
    "Herzliya Marina Medical":   2_800_000_000,
    "Cu High-Tech Park":         1_700_000_000,
}

SATISFACTION_SCORES = { ... } # dict[project → float 6.8–9.1] (1-10 scale)
ALOS_BY_MONTH = [...]         # list[float] — avg lease duration in months, 12 entries
```

### 3.2 New DataFrames

| DataFrame | Shape | Key Columns | Notes |
|---|---|---|---|
| `df_monthly_income` | 12 × 7 | `Month`, 5 project columns, `Total` | Extends monthly revenue snapshot into a time series |
| `df_costs` | 12 × 6 | `Month`, `Energy (₪)`, `Labor (₪)`, `Maintenance (₪)`, `Other (₪)`, `Total (₪)` | Energy cost derived from `df_energy_trend × ENERGY_COST_PER_KWH` |
| `df_revenue_per_unit` | 12 × 5 | `Month`, `RevPAR (₪)`, `ADR (₪)`, `Rev per Person (₪)`, `GOPPAR (₪)` | All computed from income ÷ room/headcount constants |
| `df_manpower` | 12 × 6 | `Month`, `Total Headcount`, `Available`, `On Leave`, `Contractors`, `Availability (%)` | Portfolio-wide headcount series |
| `df_staff_by_dept` | 7 × 4 | `Department`, `Total`, `Available`, `Utilization (%)` | Snapshot across 7 departments |
| `df_rooms_by_type` | 12 × 4 | `Month`, `Office (%)`, `Meeting (%)`, `Common (%)` | Availability rates by room category |
| `df_cap_table` | 5 × 5 | `Project`, `Asset Value (₪B)`, `Annual NOI (₪M)`, `Cap Rate (%)`, `GRM` | Point-in-time per-project asset ratios |

---

## 4. Module — `analytics_dashboard.py`

### 4.1 Structure

```
render()
 ├── section_header("📈 Analytics Dashboard")
 ├── Time filter  [st.select_slider → (start_idx, end_idx)]
 ├── _slice() helper — slices all DataFrames to selected period
 ├── Derived aggregates (total_rev, noi, op_margin, avg_occ, cpor, …)
 ├── Trend indicators (▲/▼ MoM % change for each applicable KPI)
 │
 ├── section_header("Tier 1 — Revenue & Efficiency")
 │    └── st.columns(7) → 7 × kpi_card() with trend arrows
 │         Total Revenue | RevPAR | ADR | GOPPAR | NOI | Op. Margin | EBITDA Margin
 │
 ├── section_header("Tier 2 — Operations & Asset")
 │    └── st.columns(7) → 7 × kpi_card() with trend arrows
 │         Avg Occupancy | Vacancy Rate | CPOR | EPOR |
 │         ₪ Rev. at Risk | Staff/Room Ratio | Avg Satisfaction
 │
 ├── Row 1 — st.columns(2)
 │    ├── Income & NOI Trend  [go.Bar + go.Scatter, dual-axis]
 │    └── RevPAR Decomposition — Rate vs. Volume  [dual-axis: Occ% bars + ADR/RevPAR lines]
 │
 ├── Row 1b — st.columns(2)
 │    ├── GOPPAR vs. CPOR — Efficiency Spread  [dual-line: green GOPPAR vs red CPOR]
 │    └── Energy per Occupied Room (EPOR)  [horizontal go.Bar + benchmark vline]
 │
 ├── Retention Intelligence — Tenant Churn Risk
 │    ├── st.columns(2)
 │    │    ├── Churn Risk Waterfall  [horizontal go.Bar, color by risk tier]
 │    │    └── Lease Expiry Scatter  [go.Scatter: x=expiry, y=rent, color=risk]
 │    └── At-Risk Tenant Table  [st.dataframe, sorted by churn risk desc]
 │
 ├── Row 2 — st.columns(2)
 │    ├── Room Availability by Type  [grouped go.Bar]
 │    └── Manpower Over Time  [stacked go.Bar]
 │
 ├── Row 3 — st.columns(2)
 │    ├── Cost Breakdown  [stacked go.Bar]
 │    └── Staff Utilization by Dept  [horizontal go.Bar, color-encoded]
 │
 ├── Asset Ratio Table  [st.dataframe(df_cap_table)]
 └── ALOS footnote  [st.metric]
```

### 4.2 Styling Rules

All charts use a shared `_CHART_LAYOUT` dict:
```python
_CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=CARD_BG,
    plot_bgcolor=CARD_BG,
    font=dict(color="#E8E8E8", size=11),
    margin=dict(l=44, r=20, t=38, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10, font_color="#E8E8E8", orientation="h", y=1.12),
)
```

**⚠️ CRITICAL:** The `legend` dict must include `font_color="#E8E8E8"`. Plotly's `plotly_dark` template uses a default legend font color that does NOT contrast against custom `paper_bgcolor` values like `CARD_BG` (`#1A1F2B`). Without an explicit `font_color`, legend labels are invisible (dark on dark). See DEVELOPER_NOTES.md Bug 3.

KPI cards use `style.kpi_card(label, value, delta, trend, trend_color)`. Section dividers use `style.section_header()`.

### 4.3 Time Filter Slicing

```python
start_idx = MONTHS.index(month_range[0])
end_idx   = MONTHS.index(month_range[1])
# All DataFrames sliced via: df.iloc[start_idx : end_idx + 1].reset_index(drop=True)
```

---

## 5. KPI Reference

### Tier 1 — Revenue & Efficiency

| # | KPI | Formula | Tier |
|---|---|---|---|
| 1 | **Total Revenue** | `df_monthly_income["Total"].sum()` (period) | 1 |
| 2 | **RevPAR** | `Monthly Revenue ÷ Total Available Rooms` | 1 |
| 3 | **ADR** | `Monthly Revenue ÷ Occupied Rooms` | 1 |
| 4 | **GOPPAR** | `(Revenue − Costs) ÷ Available Rooms` | 1 |
| 5 | **NOI** | `Total Revenue − Total Costs` | 1 |
| 6 | **Operating Margin** | `NOI ÷ Total Revenue × 100%` | 1 |
| 7 | **EBITDA Margin** | `BASELINE_EBITDA (annualised) ÷ Total Revenue × 100%` | 1 |

### Tier 2 — Operations & Asset

| # | KPI | Formula | Tier |
|---|---|---|---|
| 1 | **Avg Occupancy** | Mean of `df_occupancy_trend` project cols (period) | 2 |
| 2 | **Vacancy Rate** | `100% − Avg Occupancy` | 2 |
| 3 | **CPOR** | `Total Costs ÷ Occupied Rooms ÷ Months` | 2 |
| 4 | **EPOR** | `Energy (kWh) ÷ Occupied Rooms` per project; benchmark = 150 kWh | 2 |
| 5 | **₪ Rev. at Risk** | `Sum(Monthly Rent)` for tenants with Churn Risk ≥ 0.60 × 12 | 2 |
| 6 | **Staff / Room Ratio** | `Total Headcount ÷ TOTAL_ROOMS` | 2 |
| 7 | **Avg Satisfaction** | `mean(SATISFACTION_SCORES.values())` | 2 |

### Industry KPIs — Asset Ratio Table (point-in-time, not time-sliced)

| KPI | Formula | Data |
|---|---|---|
| **Cap Rate** | `Annual NOI ÷ Asset Value × 100%` | `df_cap_table` |
| **GRM** | `Asset Value ÷ Annual Gross Rent` | `df_cap_table` |
| **Annual NOI** | Derived per project from income margin | `df_cap_table` |

### ALOS
| KPI | Source |
|---|---|
| **Avg Length of Stay / Lease** | `mean(ALOS_BY_MONTH)` — portfolio-wide average lease duration in months |

---

## 6. App Registration

### `app.py` — Import

```python
from modules import asset_monitoring, ebitda_simulator, doc_intelligence, ai_agent, analytics_dashboard
```

### `app.py` — Navigation Radio

```python
page = st.radio(
    "Navigation",
    [
        "📊 Smart Asset Monitoring",
        "💰 EBITDA Simulator",
        "📄 AI Document Intelligence",
        "📈 Analytics Dashboard",
    ],
    ...
)
```

### `app.py` — Router

```python
elif "Analytics" in page:
    analytics_dashboard.render()
```

---

## 7. AI Agent Hooks

Two new rules added to `generate_insights()` in `modules/ai_agent.py`:

### Rule 5 — Cost Spike Warning

```
Trigger : df_costs["Total (₪)"].iloc[-1] > 110% of 12-month mean
Severity: warning
Icon    : 💸
Module  : "📈 Analytics Dashboard"
```

### Rule 6 — RevPAR MoM Decline Critical

```
Trigger : RevPAR MoM decline ≥ 8%
Severity: critical
Icon    : 📉
Module  : "📈 Analytics Dashboard"
```

---

## 8. Verification Checklist

- [ ] `streamlit run app.py` — no import errors
- [ ] Sidebar shows 4 navigation items
- [ ] "📈 Analytics Dashboard" renders without errors
- [ ] Tier 1 row: 7 KPI cards visible with ₪-formatted values
- [ ] Tier 2 row: 7 KPI cards visible
- [ ] Period slider moves → all 6 charts and both KPI rows update
- [ ] Chart 1: Income & NOI — dual-axis bar + line visible
- [ ] Chart 2: RevPAR / ADR / GOPPAR — 3 coloured trend lines
- [ ] Chart 3: Room Availability — grouped bar (Office / Meeting / Common)
- [ ] Chart 4: Manpower — stacked bar (Available / On Leave / Contractors)
- [ ] Chart 5: Cost Breakdown — stacked bar (4 cost categories)
- [ ] Chart 6: Staff Utilization — horizontal bar, colour-coded by threshold
- [ ] Asset Ratio Table — 5 projects × Cap Rate, GRM, NOI columns
- [ ] ALOS metric renders below table
- [ ] AI Agent dialog: Cost Spike rule evaluates (may be dormant with mock data)
- [ ] All existing pages (Asset Monitoring, EBITDA, Doc Intelligence) unaffected

---

## 9. Design Decisions

| Decision | Rationale |
|---|---|
| KPIs split into Tier 1 / Tier 2 sections | Mirrors user's request; separates revenue/margin KPIs (strategic) from ops/asset KPIs (operational) |
| Cap Rate / GRM as `st.dataframe` table | These are point-in-time per-asset ratios — not a time series; a table is the natural display |
| ALOS as `st.metric` footnote | Lower visual priority for commercial RE vs. hospitality; doesn't need a full chart panel |
| Satisfaction scores as scalar dict in `data.py` | Avoids over-engineering mock data; no time-series UX value for this metric |
| All computations in `render()`, no logic in `data.py` | Follows existing convention in `DEVELOPER_NOTES.md` — data layer provides raw & computed DataFrames, module renders them |
| `_CHART_LAYOUT` dict at module top | DRY — single place to update all chart styling |
| Time filter returns string values from `MONTHS` list | `select_slider` with the same `MONTHS` list used everywhere ensures index alignment |

---

## 10. Module Conventions (matching existing codebase)

- No top-level `st.*` calls outside `render()` — Streamlit calls only inside `render()`
- All imports at top of file
- `from style import kpi_card, section_header, CARD_BG, ACCENT, RED, YELLOW`
- `from data import ...` — explicit named imports only
- `plotly.graph_objects as go` + `plotly.subplots.make_subplots` for dual-axis charts
- `st.plotly_chart(fig, use_container_width=True)` — always full-width
- `height=320` on all chart figures for visual consistency
