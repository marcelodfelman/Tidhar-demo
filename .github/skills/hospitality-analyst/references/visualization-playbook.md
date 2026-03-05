# Hospitality Visualization Playbook

Reference for recommending chart types, upgrade patterns, and avoiding common anti-patterns
in hospitality dashboards. Load this file when proposing new visualizations (Operating Loop
Step 4.4) or improving existing ones (Step 4.5).

---

## 1. Chart Selection by Analysis Type

### 1.1 Time-Series KPIs (RevPAR, ADR, Occupancy, GOPPAR, Revenue)

| Scenario | Recommended Chart | Why |
|---|---|---|
| Single KPI over time | Line chart | Clean trend visibility; avoid bar charts for 12+ periods |
| KPI vs. budget/forecast | Dual-line (actual + dashed target) | Instant gap recognition |
| KPI vs. prior year | Dual-line with shaded variance band | Year-over-year context without clutter |
| KPI vs. competitive set | Multi-line (property + comp set + index line at 100) | STR-style benchmarking |
| Two related KPIs (e.g., ADR × Occupancy → RevPAR) | Dual-axis: bar (volume) + line (rate) | Shows the multiplicative relationship |

**Upgrade pattern**: A standalone RevPAR line chart should always be upgraded to include at
least one context layer — budget, prior year, or competitive set. A single line without context
tells you *what* happened but not *whether it's good*.

### 1.2 Composition & Mix (Channel Mix, Segment Mix, Cost Breakdown)

| Scenario | Recommended Chart | Why |
|---|---|---|
| Parts of a whole, single period | Donut chart (not pie) | Cleaner; center can hold a total $ figure |
| Parts of a whole, over time | 100% stacked bar | Shows mix shift period to period |
| Absolute + proportional | Stacked bar (absolute) with a toggle to 100% | Lets user switch contexts |
| Top contributors | Horizontal bar (sorted descending) | Ranking is instant; vertical bars waste label space |

**Upgrade pattern**: Replace any pie chart with a donut. Replace any single-period donut with
a time-series stacked bar to reveal mix trends — a static snapshot hides the shift.

### 1.3 Comparison / Benchmarking (CPOR, EPOR, STR Indices, Department KPIs)

| Scenario | Recommended Chart | Why |
|---|---|---|
| Property vs. benchmark | Bullet chart or bar + reference line | Shows gap to target in one glance |
| Multiple properties side-by-side | Grouped bar chart | Direct comparison |
| KPI vs. threshold (red/yellow/green) | Horizontal bar with color-coded zones | Traffic-light urgency |
| Ranking of items (menu items, departments) | Horizontal bar sorted by value | Natural reading order for ranked data |

**Upgrade pattern**: Any metric displayed as a single number (big-number KPI card) without
context should gain a **sparkline** (7–30 day trend) and a **vs. target indicator** (▲/▼ with %).

### 1.4 Distribution & Correlation

| Scenario | Recommended Chart | Why |
|---|---|---|
| Menu Engineering (popularity × margin) | Scatter plot with quadrant lines | Classic Kasavana-Smith 4-quadrant view |
| Guest satisfaction vs. RevPAR | Scatter plot with regression line | Shows financial impact of satisfaction |
| Utilization heatmap (zones × hours) | Heatmap (color intensity) | Instant identification of cold/hot zones |
| Rate distribution across bookings | Histogram or box plot | Reveals rate dispersion hidden by averages |

### 1.5 Operational Dashboards (Labor, Maintenance, Energy)

| Scenario | Recommended Chart | Why |
|---|---|---|
| Staffing over time (by category) | Stacked area chart | Shows total + breakdown; area conveys volume |
| Department utilization | Horizontal bar with threshold coloring (≥90% green, ≥80% yellow, <80% red) | Action-oriented — red bars need attention |
| Maintenance: preventive vs. reactive ratio | Donut or split bar | Ratio is the story |
| Energy by time-of-day | Area chart with peak-tariff zone shaded | Highlights cost-trigger periods |

---

## 2. Dimension Enrichment Guide

Most hospitality charts are built with only one dimension (time). Adding a second dimension
transforms a chart from "reporting" to "decision support."

| Base Analysis | Add This Dimension | Decision It Enables |
|---|---|---|
| Total Revenue (time) | + by Channel | Which channels to invest in vs. reduce |
| Occupancy (time) | + by Segment (transient/group/contract) | Which segment is driving or dragging |
| ADR (time) | + by Room Type | Whether premium rooms are pulling their weight |
| RevPAR (time) | + vs. Competitive Set (RGI line) | Whether growth is real or just market tide |
| Labor Cost (time) | + by Department | Where overstaffing lives |
| Energy (time) | + by Zone or Building | Where waste concentrates |
| F&B Revenue (time) | + by Daypart | Which meal periods to activate or cut |
| Guest Satisfaction (time) | + by Category (room, service, F&B, amenities) | Where to prioritize investment |
| Desk Utilization (time) | + by Floor / Zone | Spatial rebalancing or repricing |
| Churn Rate (time) | + by Cohort (join month) | Are newer members stickier or weaker |

**Rule of thumb**: If a chart has only a time axis and a single measure, it is always improvable
by adding a segmentation dimension. The question is *which* dimension creates the most actionable
contrast.

---

## 3. KPI Card Best Practices

KPI cards (big-number tiles at the top of a dashboard) are the most viewed elements. They must
be designed for instant comprehension.

### Required Elements for an Effective KPI Card

| Element | Purpose | Example |
|---|---|---|
| **Value** | Current period metric | ₪12,450 |
| **Label** | What it measures | RevPAR |
| **Trend indicator** | Direction vs. prior period | ▲ 3.2% |
| **Sparkline** | 7–30 day visual trend | Mini line chart (50×15px) |
| **Context** | Budget, target, or benchmark | Target: ₪13,000 |
| **Color coding** | Status at a glance | Green (above target) / Red (below) |

### Common KPI Card Mistakes

| Mistake | Problem | Fix |
|---|---|---|
| Value without trend | No sense of direction | Add ▲/▼ % change |
| Trend without context | "Up 3%" — is that good? | Add vs. budget or vs. prior year |
| Too many decimals | Cognitive load | Round to meaningful precision (₪12.5K, not ₪12,487.33) |
| All green / no thresholds | No urgency signal | Set thresholds; if everything is green, thresholds are too loose |
| 10+ KPI cards in a row | Dashboard fatigue | Max 6–8 top-level; group into tiers (Tier 1: strategic, Tier 2: operational) |

---

## 4. Dashboard Layout Patterns

### 4.1 The Executive Summary Layout (Recommended Default)

```
┌─────────────────────────────────────────────────────────┐
│  KPI Cards (4–6 top-level metrics with sparklines)      │
├──────────────────────────┬──────────────────────────────┤
│  Primary Revenue Chart   │  Primary Cost/Margin Chart   │
│  (RevPAR or TRevPAR     │  (GOP % or CPOR trend        │
│   with benchmark line)   │   with break-even line)      │
├──────────────────────────┬──────────────────────────────┤
│  Mix/Composition Chart   │  Operational Chart            │
│  (Channel mix or         │  (Labor utilization or        │
│   segment mix over time) │   energy by zone)            │
├──────────────────────────┴──────────────────────────────┤
│  Detail Table / Drill-down (property list, item list)   │
└─────────────────────────────────────────────────────────┘
```

**Principle**: Top-to-bottom = strategic-to-tactical. The CFO reads the top row. The operations
manager scrolls to the bottom.

### 4.2 Time Filter Placement

- **Always** provide a time range filter at the very top (above KPI cards).
- Default range: current month vs. prior month (for operational dashboards) or trailing 12 months
  (for strategic dashboards).
- Include **comparison period** toggle: vs. prior year, vs. budget, vs. competitive set.

### 4.3 Segment/Property Filter

- If multi-property: property selector **in the sidebar** (not inline) — it affects all charts.
- If single-property: segment filter (transient/group/OTA, or F&B outlet, or floor/zone).

---

## 5. Anti-Patterns to Flag

When auditing an existing dashboard, flag these common anti-patterns:

| Anti-Pattern | Why It's Harmful | Recommended Fix |
|---|---|---|
| **Vanity metrics** (total revenue without context) | Looks good, drives no action | Add per-unit metrics (RevPAR, CPOR) and benchmarks |
| **Single-point-in-time snapshots** | No trend = no urgency | Add trailing-period trend lines |
| **Averages without distribution** | Hides bimodal or skewed data | Add box plots or histograms alongside averages |
| **Too many chart types** on one page | Cognitive overload | Standardize on 2–3 chart types per dashboard |
| **3D charts** | Distort perception of values | Always use 2D |
| **Dual Y-axes with mismatched scales** | Suggests false correlation | Normalize scales or use separate panels |
| **Traffic-light colors without thresholds** | "Green" means nothing if threshold is arbitrary | Define thresholds from benchmarks or business targets |
| **Tables with 20+ columns** | Unreadable; no visual hierarchy | Highlight top/bottom performers; hide columns behind drill-down |
| **Pie charts with 7+ slices** | Slices become indistinguishable | Group small slices into "Other"; or switch to horizontal bar |
| **Dashboard with no actionable insight** | "So what?" problem | Every dashboard needs at least one **call-to-action** element — an alert, a threshold breach, a recommendation |

---

## 6. Color Palette Recommendations

### Semantic Colors (Universal)

| Purpose | Color | Usage |
|---|---|---|
| Positive / On-track | Teal / Green (`#00B894` or similar) | Above target, improvement |
| Warning / Attention | Amber / Yellow (`#FDCB6E`) | Within 5% of threshold |
| Negative / Below target | Red (`#E17055`) | Below threshold, declining |
| Neutral / Informational | Slate blue or grey | Baselines, reference lines |
| Budget/Target line | Dashed grey or white | Distinguished from actuals |

### Segment Differentiation

- Use a maximum of **6 distinct colors** per chart.
- For time-series with many segments, use **2–3 primary colors** with **opacity variation** for
  sub-segments.
- Ensure colorblind accessibility: avoid red/green only — pair with shape or pattern.

### Dark Theme Considerations

- Background: dark charcoal (`#1E1E2F` to `#2D2D44`) — not pure black.
- Card background: slightly lighter (`#2B2B3D`).
- Text: off-white (`#E0E0E0`) — not pure white.
- Grid lines: very low opacity (`rgba(255,255,255,0.08)`).

---

## 7. Upgrade Recipes

Quick-reference recipes for the most common "before → after" upgrades:

### Recipe A: Single Revenue Number → Revenue Dashboard Tile
**Before**: `Total Revenue: ₪2.4M`
**After**: KPI card with value (₪2.4M), ▲4.2% vs. prior month, sparkline (12-month),
target line (₪2.5M), color (amber — below target).

### Recipe B: Simple Occupancy Line → Contextualized Occupancy
**Before**: Line chart of occupancy % over 12 months.
**After**: Dual-line (actual vs. prior year) + shaded break-even zone below 62% +
segment breakdown toggle (transient / group / contract).

### Recipe C: Cost Bar Chart → Actionable Cost Analysis
**Before**: Stacked bar of monthly costs by category.
**After**: Same stacked bar + a CPOR line overlay (second Y-axis) + USALI benchmark
reference line for CPOR. Adds a "cost per occupied unit" perspective to raw totals.

### Recipe D: Static F&B Revenue → Menu Engineering View
**Before**: Total F&B revenue by month.
**After**: Scatter plot (Kasavana-Smith matrix) with items plotted by popularity (X) and
contribution margin (Y), quadrant lines at median, items labeled, color-coded by category.
Plus a secondary panel showing RevPASH by daypart.

### Recipe E: Occupancy KPI → Space Utilization Heatmap
**Before**: Single occupancy % for the building.
**After**: Heatmap (rows = floors/zones, columns = hours of the day), color intensity =
utilization %. Instant visual of where and when capacity is wasted.

### Recipe F: Member Count → Churn Cohort Analysis
**Before**: Total active members (single number or line chart).
**After**: Cohort retention chart (rows = join-month cohorts, columns = months since joining,
cells = % retained). Reveals whether newer cohorts retain better or worse than older ones.
