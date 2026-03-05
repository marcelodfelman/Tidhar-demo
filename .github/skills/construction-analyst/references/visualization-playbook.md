# Construction Visualization Playbook — Israel

Reference for recommending chart types, upgrade patterns, and avoiding common anti-patterns
in construction dashboards. Load this file when proposing new visualizations (Operating Loop
Step 4.4) or improving existing ones (Step 4.5).

---

## 1. Chart Selection by Analysis Type

### 1.1 Time-Series Project KPIs (Cost, Revenue, Cash Flow, Margin)

| Scenario | Recommended Chart | Why |
|---|---|---|
| Single KPI over time (monthly) | Line chart | Clean trend; max 36 months on one axis |
| Planned vs. Actual cost (S-curve) | Dual-line (Planned + Actual + EAC dashed) | Classic EVM visual; gap = variance |
| Cash flow forecast | Stacked area (inflows) + negative area (outflows) + net line | Shows both sides of liquidity |
| Budget vs. Actual by category | Grouped bar (budget bar + actual bar side by side) | Direct comparison per category |
| Project margin trend | Line + shaded zone (margin target band) | Instant: margin healthy or eroding? |
| Multi-project comparison | Small multiples (one mini-chart per project) | Avoids clutter of overlapping lines |

**Upgrade pattern**: A standalone "Total Cost" line chart should always gain a Planned Value
curve and an EAC projection. Without these, the chart shows *what happened* but not *whether
it's on track* or *where it's heading*.

### 1.2 EVM (Earned Value) Specific Charts

| Scenario | Recommended Chart | Why |
|---|---|---|
| PV / EV / AC over time | Triple-line (PV=dashed blue, EV=solid green, AC=solid red) | Standard EVM format; gap between lines tells the story |
| CPI and SPI trend | Dual-line with reference line at 1.0 | Values below 1.0 = problem; the reference line is critical |
| Variance at Completion | Bullet chart (EAC as bar, budget as target line) | Shows exactly how much over/under budget |
| Multiple projects CPI comparison | Horizontal bar sorted by CPI (worst first) | Ranking identifies which projects need attention |

### 1.3 Composition & Cost Breakdown

| Scenario | Recommended Chart | Why |
|---|---|---|
| Cost by CSI division (single period) | Treemap or horizontal bar (sorted by value) | Treemap for proportions; bar for ranking |
| Cost breakdown over time | Stacked bar (absolute) | Shows growth and mix shift |
| Budget allocation vs. spend | 100% stacked bar (budget alongside actual) | Reveals which categories are over/under absorbing |
| Subcontractor spend distribution | Horizontal bar sorted descending | Top subcontractors visible immediately |
| Material cost by category | Donut (for current period) or stacked bar (over time) | Donut only for single-period snapshot |

**Upgrade pattern**: Replace any pie chart with a donut or horizontal bar. Replace a single-period
view with a time-series view to reveal trends.

### 1.4 Schedule & Progress Visualization

| Scenario | Recommended Chart | Why |
|---|---|---|
| Overall project timeline | Gantt chart (critical path highlighted in red) | Industry standard; the critical path must be visually distinct |
| Milestone tracking | Timeline chart with planned (hollow) vs. actual (filled) markers | Gap between markers = delay |
| Progress by trade/floor | Heatmap (rows=floors, columns=trades, color=% complete) | Instant spatial progress view |
| Look-ahead (3-week rolling) | Simplified Gantt with status colors (on-track / at-risk / delayed) | Action-oriented short-term view |
| Weather impact on schedule | Calendar heatmap (rows=weeks, columns=days, color=productivity) | Shows seasonal patterns clearly |

### 1.5 Safety Dashboard Charts

| Scenario | Recommended Chart | Why |
|---|---|---|
| Incident trend (monthly) | Line chart with severity coloring (minor/major/fatal) | Trend is the story; severity adds urgency |
| Leading vs. lagging indicators | Dual-panel: leading (observations/near-miss) left, lagging (incidents) right | Side-by-side makes the prediction visible |
| Safety score by project | Horizontal bar with threshold zones (green/yellow/red) | Ranking + severity in one view |
| Top violation types | Horizontal bar sorted by frequency | Pareto — focus on the top 3 |
| Toolbox talk / training compliance | Progress bar or radial gauge (% complete) | Simple target-tracking |

### 1.6 Comparison & Benchmarking (Subcontractors, Projects, Market)

| Scenario | Recommended Chart | Why |
|---|---|---|
| ₪/sqm by project | Horizontal bar with market benchmark line | Shows which projects are above/below market |
| Subcontractor performance matrix | Scatter (x=cost, y=quality rating, size=scope ₪) | Multi-dimensional comparison |
| Project ranking (Health Score) | Horizontal bar sorted by composite score + color bands | Portfolio triage at a glance |
| Metric vs. benchmark (single) | Bullet chart or KPI card with reference indicator | Compact; dashboard-friendly |
| Madad trend vs. contract exposure | Dual-axis: area (exposure ₪) + line (madad index) | Shows when exposure is unhedged |

### 1.7 Risk & Legal

| Scenario | Recommended Chart | Why |
|---|---|---|
| Risk register heatmap | Heatmap (x=likelihood, y=impact) with risk items plotted | Classic risk matrix; quadrants drive action |
| Claims exposure over time | Stacked area by claim type | Shows accumulation and composition |
| Permit pipeline | Kanban/funnel chart (applied → in-review → approved) | Progress tracking with bottleneck visibility |
| Cash-flow scenarios | Fan chart (base + optimistic + pessimistic bands) | Decision support for financing |

---

## 2. Dimension Enrichment Guide

Most construction charts are built with only one dimension (time or project). Adding a second
dimension transforms a chart from "reporting" to "decision support."

| Base Analysis | Add This Dimension | Decision It Enables |
|---|---|---|
| Total Cost (time) | + by CSI division | Which cost categories are over-running |
| Budget Variance (project) | + by phase (foundations/structure/finishes/MEP) | Where in the build is margin leaking |
| Subcontractor Cost (project) | + by trade | Which trades to renegotiate or replace |
| Schedule Delay (time) | + by cause (weather/permits/labor/materials) | Root cause prioritization |
| Safety Incidents (time) | + by trade or project | Where to deploy safety resources |
| Labor Hours (time) | + by workforce category (Israeli/Palestinian/foreign) | Workforce planning and permit coordination |
| Material Cost (time) | + by supplier | Supplier consolidation opportunities |
| Cash Flow (time) | + by project | Which project is the cash drain |
| Defects at Handover (project) | + by trade/system | Systemic quality failures vs. random |
| Pre-sales (time) | + by unit type/floor | Pricing optimization signal |

**Rule of thumb**: If a chart has only a time axis and a single measure, it is always improvable
by adding a segmentation dimension. The question is *which* dimension creates the most actionable
contrast.

---

## 3. KPI Card Best Practices

### Required Elements for Construction KPI Cards

| Element | Purpose | Example |
|---|---|---|
| **Value** | Current metric | CPI: 0.94 |
| **Label** | What it measures | Cost Performance Index |
| **Trend indicator** | Direction vs. prior period | ▼ 0.03 vs. last month |
| **Sparkline** | Recent trend (3–6 months) | Mini line chart |
| **Threshold context** | Target or benchmark | Target: ≥ 1.00 |
| **Color coding** | Status at a glance | Red (CPI < 0.95), Yellow (0.95–1.00), Green (> 1.00) |

### Common KPI Card Mistakes in Construction Dashboards

| Mistake | Problem | Fix |
|---|---|---|
| % Complete without EV context | 80% complete doesn't mean 80% of budget was well-spent | Pair with CPI or cost variance |
| Budget variance in ₪ only | ₪500K over-budget means different things on a ₪10M vs. ₪200M project | Show variance as % of budget |
| Schedule shown in days, not money | "15 days late" has no urgency | Add cost-per-day-of-delay (finance + GC) |
| Safety in incidents only | 0 incidents this month ≠ safe site | Add leading indicators (near-miss, observations) |
| All projects in one average | Average CPI of 1.02 hides one project at 0.85 | Show per-project or worst-performer |
| Too many decimals | CPI: 0.93847 | Round: CPI: 0.94 |

### Recommended Tier Structure

| Tier | KPIs (6–8 per tier) | Audience |
|---|---|---|
| **Tier 1 — Financial** | Total Revenue, Total Cost, Project Margin %, NOI, Madad Exposure, Cash Buffer (weeks), EBITDA | CEO, CFO |
| **Tier 2 — Operational** | CPI, SPI, ₪/sqm, Subcontractor Payment Status, Safety Score, Permit Pipeline, Labor Productivity | Project Managers, COO |

---

## 4. Dashboard Layout Patterns

### 4.1 Project Dashboard (Single Project View)

```
┌──────────────────────────────────────────────────────────────┐
│  Project Header: Name, Status Badge, % Complete, Days to Go  │
├──────────────────────────┬───────────────────────────────────┤
│  KPI Row: Budget Var │ Schedule Var │ CPI │ SPI │ Safety    │
├──────────────────────────┬───────────────────────────────────┤
│  S-Curve                 │  Margin Waterfall                 │
│  (PV/EV/AC + EAC)       │  (Tender → Current → Forecast)    │
├──────────────────────────┬───────────────────────────────────┤
│  Cost Breakdown          │  Schedule - Critical Path Status  │
│  (by CSI or by phase)    │  (milestone timeline)             │
├──────────────────────────┬───────────────────────────────────┤
│  Safety Leading Indicators│  Subcontractor Status Table      │
│  (near-miss, observations)│  (payment, quality, schedule)    │
├──────────────────────────┴───────────────────────────────────┤
│  Cash Flow Forecast (12-month stacked area)                   │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 Portfolio Dashboard (Multi-Project View)

```
┌──────────────────────────────────────────────────────────────┐
│  Portfolio KPIs: Total Backlog │ Active Projects │ Avg CPI   │
│                  Avg SPI │ Total Cash Buffer │ Safety Score  │
├──────────────────────────┬───────────────────────────────────┤
│  Project Health Ranking  │  Cash Flow Aggregate              │
│  (horizontal bar, sorted │  (stacked by project)             │
│   by composite score)    │                                   │
├──────────────────────────┬───────────────────────────────────┤
│  CPI/SPI Scatter         │  Resource Demand Heatmap          │
│  (each dot = a project)  │  (trades × months)                │
├──────────────────────────┴───────────────────────────────────┤
│  Project Table (sortable: name, status, CPI, SPI, margin %) │
└──────────────────────────────────────────────────────────────┘
```

### 4.3 Filter & Navigation

- **Time range**: Select by project phase or calendar period; default = project-to-date.
- **Project selector**: Sidebar dropdown for multi-project portfolios.
- **Comparison period**: vs. prior month, vs. tender baseline, vs. re-baseline.
- **Segment filter**: Residential / Commercial / Urban Renewal / Infrastructure.

---

## 5. Anti-Patterns to Flag

| Anti-Pattern | Why It's Harmful | Recommended Fix |
|---|---|---|
| **% Complete without EV** | Meaningless — work done ≠ value earned | Add Earned Value and CPI |
| **Gantt chart never updated** | False confidence in schedule | Require weekly update; flag stale Gantts |
| **Cost report without forecast** | Looks at the past; doesn't predict the future | Add EAC and VAC columns |
| **Safety only shows lagging indicators** | Reactive; incidents already happened | Add leading indicators dashboard |
| **Single-color project status** | "Green" with no criteria | Define quantitative thresholds (CPI > 0.97 = green) |
| **Portfolio as spreadsheet only** | No visual hierarchy; 30 columns of numbers | Convert to ranked bar charts + health scores |
| **3D charts or decorative charts** | Distort values; waste dashboard space | Always 2D; every chart must answer a question |
| **Madad shown as single number** | Index without context of exposure | Show index trend alongside ₪ exposure |
| **Subcontractor data not consolidated** | Each project has its own opinion | Centralize scoring and benchmarking |
| **Cash flow without scenarios** | One plan = one surprise away from crisis | Add optimistic/base/pessimistic bands |

---

## 6. Color Palette Recommendations

### Semantic Colors

| Purpose | Color | Usage |
|---|---|---|
| On-track / Within budget | Green / Teal (`#00B894`) | CPI > 1.0, on schedule, safety compliant |
| Warning / Attention | Amber (`#FDCB6E`) | CPI 0.95–1.0, minor delay, approaching threshold |
| Over-budget / Delayed / At-risk | Red (`#E17055`) | CPI < 0.95, critical delay, safety incident |
| Neutral / Baseline | Slate grey or blue (`#636E72`) | Budget line, planned value, reference |
| Forecast / Projected | Dashed line (same color, lighter opacity) | EAC, projected cash flow |

### Construction-Specific Color Codes

| Dimension | Color Approach |
|---|---|
| **Project phases** (Foundation → Structure → Finishes → MEP → Handover) | Sequential palette: dark blue → mid blue → teal → light green → green |
| **Risk levels** | Red / Orange / Yellow / Green (high → low) |
| **Workforce category** | Distinct hue per category (max 4 colors) |
| **Trades** | Use 6–8 colors max; group minor trades as "Other" |

### Dark Theme Considerations

- Background: dark charcoal (`#1E1E2F` to `#2D2D44`) — not pure black.
- Card background: slightly lighter (`#1A1F2B` to `#2B2B3D`).
- Text: off-white (`#E0E0E0` to `#E8E8E8`) — not pure white.
- Grid lines: very low opacity (`rgba(255,255,255,0.08)`).
- **Legend `font_color`**: Must be explicitly set to match text color when using a custom
  `paper_bgcolor`. Plotly's `plotly_dark` template does NOT inherit legend font color from
  the parent `font.color` — always set `legend.font_color` explicitly.

---

## 7. Upgrade Recipes

### Recipe A: Budget Number → Cost Intelligence Tile
**Before**: `Total Cost: ₪45.2M`
**After**: KPI card with value (₪45.2M), CPI (0.96), ▼2.1% vs. last month, sparkline (6-month),
budget line (₪44.0M), color (amber — over budget).

### Recipe B: % Complete Bar → Earned Value Dashboard
**Before**: Progress bar showing "72% complete."
**After**: S-curve with PV/EV/AC lines, CPI and SPI callout boxes, EAC projection (dashed),
and variance-at-completion in ₪.

### Recipe C: Cost Table → Margin Waterfall
**Before**: Spreadsheet of cost vs. budget by line item.
**After**: Waterfall chart: Tender Margin (starting bar) → Material Variance → Labor Variance →
Subcontractor Variance → Madad Adjustment → Change Orders → Current Estimated Margin.

### Recipe D: Incident Count → Safety Intelligence
**Before**: "3 incidents this year."
**After**: Dual-panel: left = leading indicators (weekly near-misses, observations, toolbox talks);
right = lagging indicators (incidents by severity + lost-time days). Sparklines on both.

### Recipe E: Project List → Portfolio Health Ranking
**Before**: Table of projects with green/yellow/red manual status.
**After**: Horizontal bar chart sorted by composite Health Score (weighted CPI + SPI + Safety +
Quality). Color-coded by segment. Click-through to individual project dashboard.

### Recipe F: Cash Flow Line → Scenario Planning View
**Before**: Line chart of monthly cash in/out.
**After**: Stacked area (inflows by source: buyer payments, bank drawdowns, other) + negative
area (outflows by type: subcontractors, materials, GC, finance). Fan overlay with
pessimistic/base/optimistic scenarios determined by key risk variables.

### Recipe G: Static Subcontractor List → Performance Dashboard
**Before**: Table of subcontractors with contract value and payment status.
**After**: Scatter plot (x = ₪/sqm variance from benchmark, y = quality score, size = contract
value). Color by on-time delivery rate. Table below sorted by composite performance score with
trend sparkline.
