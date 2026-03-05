# Hospitality Analytics Audit & Improvement Roadmap
**Portal:** Tidhar Decision Intelligence Portal  
**Date:** March 4, 2026  
**Author:** GitHub Copilot — Senior Hospitality Analytics Consultant  
**Status:** 📋 Plan Complete — Ready for Implementation

---

## Headline Finding

> Your RevPAR chart is a single-line trend with no context — it tells you *what* happened but cannot tell you *why* or *whether it's good*. That is the single most expensive visualization gap in the portal, and it is fixable in one day.

Across the full portal, you are tracking **14 KPIs** and **6 charts**. The analysis catalog contains **30+ analyses** applicable to your segment. You are covering roughly **20%** of the high-value decision surface. The remaining 80% is detailed below, ranked by financial impact.

---

## 1. Audit — Inventory of What Exists Today

**Segment classification:** Mixed-use B2B property operator (Israel). Portfolio characteristics map to **Co-working / Flex (C)** and **Hotel extended-stay (H)** in the analysis catalog. F&B analyses are out of scope.

### 1.1 Existing KPI Cards (14 total)

| # | KPI | Tag | Time Grain | Limitation |
|---|-----|-----|------------|------------|
| 1 | Total Revenue | Revenue-facing | Monthly | No variance vs. budget; no project breakdown |
| 2 | RevPAR | Revenue-facing | Monthly avg | No decomposition; no context layer |
| 3 | ADR | Revenue-facing | Monthly avg | No segment or room-type split |
| 4 | GOPPAR | Revenue-facing | Monthly avg | Not compared to CPOR for spread analysis |
| 5 | NOI | Revenue-facing | Monthly | No project-level attribution |
| 6 | Operating Margin | Revenue-facing | Monthly | No benchmark line |
| 7 | EBITDA Margin | Revenue-facing | Monthly | Derived from annualized constant — no per-project split |
| 8 | Avg Occupancy | Operational | Monthly avg | Portfolio average hides 45%–91% range |
| 9 | Vacancy Rate | Operational | Monthly avg | Inverse of occupancy — no additional decision value |
| 10 | CPOR | Cost-facing | Monthly avg | No benchmarking line; no by-department split |
| 11 | Tenant Retention | Revenue-facing | Computed avg | No cohort view; no expiry calendar |
| 12 | Staff Available | Operational | Snapshot | Raw count with no productivity context |
| 13 | Staff / Room | Operational | Snapshot | Ratio without revenue-per-headcount overlay |
| 14 | Avg Satisfaction | Operational | Survey avg | Not linked to revenue — pure decoration today |

### 1.2 Existing Charts (6 total)

| # | Chart | Type | Tag | Missing Dimensions |
|---|-------|------|-----|--------------------|
| 1 | Income & NOI Trend | Bar + Line (dual-axis) | Revenue-facing | No project breakdown; no budget line |
| 2 | RevPAR / ADR / GOPPAR Trend | 3-line scatter | Revenue-facing | No rate-vs-volume decomposition; no benchmark |
| 3 | Room Availability by Type | Grouped bar | Operational | Availability %, not revenue yield |
| 4 | Manpower Over Time | Stacked bar | Operational | No productivity overlay |
| 5 | Cost Breakdown | Stacked bar | Cost-facing | No per-occupied-unit normalization |
| 6 | Staff Utilization by Dept | Horizontal bar | Operational | No revenue-per-headcount context |

### 1.3 Other Elements

| Element | Tag | Notes |
|---------|-----|-------|
| Asset Ratio Table (Cap Rate, GRM, NOI) | Asset-facing | Snapshot only — no trend; no target yield per project |
| ALOS footnote metric | Operational | No LOS-based pricing analysis attached |

---

## 2. Gap Analysis — Catalog Comparison

Reference: `analysis-catalog.md` — 30 analyses across Revenue (R01–R13), Cost (C01–C10), and Dual-Impact (D01–D10).

### 2.1 Analyses Currently Covered (Partial or Full)

| Catalog # | Analysis | Coverage |
|-----------|----------|----------|
| C03 | CPOR Benchmarking | Partial — CPOR computed but no benchmark reference |
| D04 | Churn Prediction | Partial — Tenant Retention KPI exists but hides risk distribution |
| — | Occupancy tracking | Full — time-series by project available |
| — | Cost monitoring | Partial — stacked bar shows totals but no unit normalization |

### 2.2 Analyses NOT Covered (Applicable to Segments H + C)

| Catalog # | Analysis | Segment | Impact Type |
|-----------|----------|---------|-------------|
| R01 | Dynamic Pricing / Rate Optimization | H | Rev+ |
| R02 | Channel Mix Optimization | H | Rev+ / Cost− |
| R03 | Demand Forecasting & Pace Analysis | H | Rev+ |
| R05 | Ancillary Revenue per Guest | H | Rev+ |
| R06 | Guest / Tenant LTV Segmentation | H, C | Rev+ |
| R10 | Upsell & Cross-sell Tracking | H, C | Rev+ |
| R11 | RevPAD (Revenue per Available Desk) | C | Rev+ |
| R12 | Meeting Room Yield Management | H, C | Rev+ |
| R13 | Length-of-Stay Pricing | H | Rev+ |
| C01 | Labor Productivity & Scheduling | A | Cost− |
| C02 | Energy per Occupied Room (EPOR) | H, C | Cost− |
| C05 | Procurement & Supplier Consolidation | A | Cost− |
| C06 | Preventive vs. Reactive Maintenance | H, C | Cost− |
| C07 | Overtime & Provisional Labor Leakage | A | Cost− |
| C08 | Utility Peak/Off-Peak Profiling | H, C | Cost− |
| D01 | Break-Even Occupancy & GOP Flow-Through | H, C | Both |
| D02 | Competitive Set Benchmarking (STR) | H | Both |
| D03 | Satisfaction → Revenue Correlation | H | Both |
| D05 | Space Utilization Heatmapping | C, H | Both |
| D06 | RevPAR Decomposition (Rate vs. Volume) | H | Both |
| D07 | Segment Profitability Analysis | H | Both |
| D09 | Cancellation & No-Show Patterns | H, C | Both |
| D10 | Total Revenue Management (TRevPAR) | H | Both |

**Total gaps: 23 out of 30 applicable analyses are not implemented.**

---

## 3. Prioritized Recommendations

### 3.1 Priority Tiers

| Priority | Criteria |
|----------|----------|
| **P1 — Quick Win** | High $ impact + low implementation effort (< 1 week) + no new data needed |
| **P2 — Strategic** | High $ impact + moderate effort (1–4 weeks) |
| **P3 — Foundation** | Enables future P1/P2 analyses (data infrastructure) |
| **P4 — Nice-to-have** | Low $ impact or highly uncertain ROI |

---

### P1 — Quick Wins

---

#### Rec #1 — RevPAR Decomposition (Rate vs. Volume)

| Field | Content |
|-------|---------|
| **Catalog Ref** | D06 |
| **Impact Rating** | P1 |
| **Impact Estimate** | Diagnostic — prevents wrong corrective actions worth 3–8% RevPAR |
| **Why It Matters** | If RevPAR rose 5%, is that because ADR rose 8% but occupancy fell 3% (pricing out demand) or occupancy rose 7% but ADR fell 2% (discounting to fill)? These are opposite problems requiring opposite responses. Today you cannot tell which is happening. |
| **Key Metrics** | RevPAR, ADR, Occupancy % — all already in `df_revenue_per_unit` and `df_occupancy_trend` |
| **Recommended Visualization** | Dual-axis chart — grouped bars for Occupancy % (right axis) + line for ADR (left axis) + RevPAR as derived annotation. Add rate-contribution vs. volume-contribution waterfall. |
| **Data Needed** | No new data — recombine existing DataFrames |
| **Segment Applicability** | H (primary), C (analogous with desk metrics) |
| **Implementation Location** | Replace or augment current RevPAR / ADR / GOPPAR Trend chart in `modules/analytics_dashboard.py` |

---

#### Rec #2 — Break-Even Occupancy & GOP Flow-Through

| Field | Content |
|-------|---------|
| **Catalog Ref** | D01 |
| **Impact Rating** | P1 |
| **Impact Estimate** | Decision framework — every 1% occupancy above break-even flows 60–80% to GOP |
| **Why It Matters** | Bnei Brak is at 45% occupancy and declining. Without knowing break-even occupancy for that project, management cannot answer: "Should we cut price to fill, cut costs to survive, or exit?" This analysis converts known fixed/variable cost data into a go/no-go decision threshold. |
| **Key Metrics** | Fixed vs. variable cost split (derive from `df_costs`), occupancy %, GOP % |
| **Recommended Visualization** | Horizontal reference line on occupancy trend chart at break-even %; flow-through table per project |
| **Data Needed** | Requires cost categorization into fixed vs. variable — small addition to `data.py` |
| **Segment Applicability** | H, C |
| **Implementation Location** | New "Break-Even & Flow-Through" panel below the asset ratio table |

---

#### Rec #3 — Tenant Churn Risk Waterfall by Project & Expiry

| Field | Content |
|-------|---------|
| **Catalog Ref** | D04 (upgrade from partial coverage) |
| **Impact Rating** | P1 |
| **Impact Estimate** | 5 percentage point churn reduction = 15–25% retained annual revenue |
| **Why It Matters** | You have `Churn Risk` as a single average in the Tenant Retention KPI card. The underlying `df_tenants` reveals 6 leases expiring April–September 2026 (WeWork Flex, Psagot, Wix, Monday.com, IEC, Harel) — concentrated exposure that the current dashboard completely hides. At least ₪1.235M/month in rent is at risk within 6 months. |
| **Key Metrics** | Churn Risk per tenant, Lease Expiry date, Monthly Rent (₪), Activity Score — all in `df_tenants` |
| **Recommended Visualization** | Horizontal sorted bar chart colored by risk tier (red/yellow/green) + expiry timeline scatter showing ₪ at risk per month. Add "Revenue at Risk (12-month)" as a new P1 KPI card. |
| **Data Needed** | No new data — all fields exist in `df_tenants` |
| **Segment Applicability** | C (primary — lease-based tenants) |
| **Implementation Location** | New "Retention Intelligence" sub-section or separate tab |

---

#### Rec #4 — Energy per Occupied Room (EPOR)

| Field | Content |
|-------|---------|
| **Catalog Ref** | C02 |
| **Impact Rating** | P1 |
| **Impact Estimate** | 10–25% energy cost reduction opportunity |
| **Why It Matters** | Energy is shown as absolute monthly cost in a stacked bar. But Bnei Brak consumes 35,800 kWh/month at 45% occupancy — meaning ~55% of energy is heating/cooling empty space. EPOR turns an unactionable cost line into a targeting metric for immediate efficiency action. |
| **Key Metrics** | kWh ÷ occupied rooms = EPOR by project; benchmark: 25–40 kWh/room-month |
| **Recommended Visualization** | Bullet chart or horizontal bar per project with a benchmark reference line at 35 kWh |
| **Data Needed** | No new data — compute from existing `df_energy_trend` / `df_occupancy_trend` / `ROOMS_PER_PROJECT` |
| **Segment Applicability** | H, C |
| **Implementation Location** | New chart in Row 3 area; also add EPOR as Tier 2 KPI card (replace raw "Staff Available" count) |

---

### P2 — Strategic Analyses

---

#### Rec #5 — Guest Satisfaction → Revenue Correlation

| Field | Content |
|-------|---------|
| **Catalog Ref** | D03 |
| **Impact Rating** | P2 |
| **Impact Estimate** | 1-point improvement in review/satisfaction score correlates with 1–5% ADR premium (Cornell research) |
| **Why It Matters** | Avg Satisfaction (7.4/10) is a KPI card with no connection to revenue. Scatter satisfaction vs. RevPAR by project and you will likely see Herzliya (9.1/10) commanding the highest ADR and Bnei Brak (6.8/10) the lowest — validating where quality investment produces the most yield. |
| **Key Metrics** | `SATISFACTION_SCORES` by project + RevPAR or ADR by project |
| **Recommended Visualization** | Scatter plot (X = satisfaction score, Y = RevPAR or ADR) with regression line + labeled dots per project. Annotate "ADR uplift per 1-point increase." |
| **Data Needed** | Needs per-project ADR — currently only portfolio average in `df_revenue_per_unit`. Requires project-level revenue split addition to `data.py`. |
| **Segment Applicability** | H, C |

---

#### Rec #6 — Meeting Room Yield Management

| Field | Content |
|-------|---------|
| **Catalog Ref** | R12 |
| **Impact Rating** | P2 |
| **Impact Estimate** | 10–30% meeting-space revenue uplift with time-based pricing |
| **Why It Matters** | "Room Availability by Type" shows availability %. This tells you capacity, not revenue per meeting room hour (RevPASM). Morning peak (9–12 AM) is likely >90% utilized while afternoon sits at ~30%. Flat pricing leaves revenue on the table. |
| **Key Metrics** | Utilization % by room type by time-of-day, Revenue per room per hour, Cancellation/no-show rate |
| **Recommended Visualization** | Heatmap (room type × hour-of-day, color = utilization %) + dual-axis chart (utilization bar + revenue/hour line) |
| **Data Needed** | Booking-level data by room type and time-of-day — likely requires PMS/booking system integration. Flag as **aspirational** if booking-level data is unavailable; use `df_rooms_by_type` as placeholder. |
| **Segment Applicability** | H, C |

---

#### Rec #7 — Space Utilization Heatmap by Project

| Field | Content |
|-------|---------|
| **Catalog Ref** | D05 |
| **Impact Rating** | P2 |
| **Impact Estimate** | 10–20% revenue uplift from repricing underused zones + 5–10% cost reduction from closing them |
| **Why It Matters** | Portfolio occupancy averages 75%, but the range is 45%–91%. A spatial heatmap immediately surfaces which projects have cold zones (Bnei Brak declining to 45%). This enables zone-consolidation, sub-lease, or repurposing decisions currently invisible. |
| **Key Metrics** | Occupancy % by project by floor/zone, Revenue per sqm, Foot traffic |
| **Recommended Visualization** | Heatmap grid (projects × months, color = occupancy intensity). Floor/zone breakdown would be ideal; project-level heatmap is implementable today from `df_occupancy_trend`. |
| **Data Needed** | Floor/zone breakdown aspirational; project-level available now |
| **Segment Applicability** | C (primary), H (conference/event) |

---

#### Rec #8 — Segment Profitability Analysis

| Field | Content |
|-------|---------|
| **Catalog Ref** | D07 |
| **Impact Rating** | P2 |
| **Impact Estimate** | 2–6% margin improvement by reallocating capacity from low-margin to high-margin tenant segments |
| **Why It Matters** | Tenants are grouped by sector in `df_tenants` but profitability per sector is never computed. A Technology tenant at ₪620K/month may have very different service costs than a Flex/Co-working tenant at ₪185K/month. Without per-segment margin analysis, pricing negotiations are blind. |
| **Key Metrics** | Revenue by tenant sector, Operating cost allocated by sector, Net margin per sector |
| **Recommended Visualization** | Horizontal bar chart sorted by margin % + stacked bar (revenue vs. cost) per sector |
| **Data Needed** | Cost allocation per tenant or sector — requires addition to `data.py` |
| **Segment Applicability** | H, C |

---

### P3 — Foundation Analyses

---

#### Rec #9 — Tenant Acquisition Channel Mix

| Field | Content |
|-------|---------|
| **Catalog Ref** | R02 (adapted for leasing) |
| **Impact Rating** | P3 |
| **Impact Estimate** | 2–6% net revenue gain by tracking direct vs. broker vs. platform acquisition cost |
| **Why It Matters** | No channel attribution exists. Cannot determine if direct-leasing or broker-sourced tenants have better LTV, lower churn, or higher rent. This is a data collection problem, not an analytics problem. |
| **Key Metrics** | Acquisition channel per tenant, Acquisition cost, LTV by channel |
| **Recommended Visualization** | Donut chart (channel mix) + horizontal bar (LTV by channel) |
| **Data Needed** | Add `Acquisition Channel` and `Acquisition Cost` fields to `df_tenants` — **requires operational data capture** |
| **Segment Applicability** | H, C |

---

#### Rec #10 — Labor Productivity (Revenue per Headcount)

| Field | Content |
|-------|---------|
| **Catalog Ref** | C01 |
| **Impact Rating** | P3 |
| **Impact Estimate** | 3–8% labor cost reduction (labor = 25–45% of total operating costs) |
| **Why It Matters** | Manpower Over Time shows headcount. Revenue per available staff member is not tracked. Overlay total revenue ÷ total headcount as a trend line to monitor productivity vs. cost. |
| **Key Metrics** | Revenue per headcount, Rooms managed per staff member, Revenue per department head |
| **Recommended Visualization** | Dual-axis on existing Manpower chart — headcount bars (left) + revenue-per-headcount line (right) |
| **Data Needed** | No new data for portfolio-level; dept-level productivity requires revenue attribution by dept |
| **Segment Applicability** | A (all segments) |

---

#### Rec #11 — Preventive vs. Reactive Maintenance Ratio

| Field | Content |
|-------|---------|
| **Catalog Ref** | C06 |
| **Impact Rating** | P3 |
| **Impact Estimate** | 15–30% maintenance cost reduction; reactive repairs cost 3–5× preventive |
| **Why It Matters** | Maintenance appears as a single cost bucket. Splitting into Preventive vs. Reactive — even estimated — reveals whether the operation is firefighting (expensive) or preventing (efficient). Target ratio: 70% preventive / 30% reactive. |
| **Key Metrics** | Work orders by type, Mean time between failures, Maintenance cost per room |
| **Recommended Visualization** | Donut or split bar showing ratio + trend line of preventive % over time |
| **Data Needed** | Split `Maintenance (₪)` in `df_costs` into `Preventive` and `Reactive` subcategories |
| **Segment Applicability** | H, C |

---

## 4. Existing Visualization Improvements

### 4.1 RevPAR Chart Redesign (Highest Priority)

| Field | Content |
|-------|---------|
| **Current Element** | RevPAR / ADR / GOPPAR Trend — 3-line `go.Scatter` chart, 320px, single time axis |
| **Limitation** | Three competing lines create visual noise without insight. No benchmark, no decomposition, no context. GOPPAR on the same axis as RevPAR/ADR misleads on scale. Violates visualization playbook §1.1 ("A single line without context tells you *what* happened but not *whether it's good*"). |
| **Upgrade** | **Split into 2 charts:** |
| | **Chart A — RevPAR Decomposition:** Dual-axis — grouped bars for Occupancy % (right axis, 0–100%) + line for ADR (left axis, ₪) + RevPAR as shaded area or dashed line. Add a dashed horizontal target line for RevPAR budget. Add `vs. Prior Year` toggle with delta shading. |
| | **Chart B — GOPPAR vs. CPOR Efficiency Spread:** Dual-line — GOPPAR (green) and CPOR (red) over time. The spread is the profitability story: converging = margin compression; widening = efficiency gains. |
| **Decision It Enables** | Chart A: Immediately answers "is RevPAR movement rate-driven or volume-driven?" Chart B: Answers "is operating efficiency improving or deteriorating?" |
| **Playbook Reference** | §1.1 — "Two related KPIs (ADR × Occupancy → RevPAR): Dual-axis: bar (volume) + line (rate)" |

### 4.2 Income & NOI Trend — Add Project Dimension

| Field | Content |
|-------|---------|
| **Current Element** | Monthly Revenue (bar) + NOI (line) — portfolio total only |
| **Limitation** | An aggregate bar hides individual project performance. Herzliya at ₪2.85M/month is masking Bnei Brak at ₪0.98M/month and declining. |
| **Upgrade** | Change from single bar to **stacked bar by project** (5 color-coded segments). Keep NOI as overlay line. Add a toggle to switch between absolute (₪) and indexed (100 = first month) views. |
| **Decision It Enables** | Which project is driving or dragging revenue, and whether the NOI trend is broad-based or carried by one project. |
| **Playbook Reference** | §2 Dimension Enrichment — "Total Revenue (time) + by Channel → Which channels to invest in vs. reduce" |

### 4.3 Cost Breakdown — Add CPOR Normalization

| Field | Content |
|-------|---------|
| **Current Element** | Stacked bar (Energy / Labor / Maintenance / Other) — absolute ₪ |
| **Limitation** | Absolute cost rises with occupancy — this is expected. A rising cost is alarming in isolation but may reflect healthy growth. Without normalization, the chart triggers false urgency. |
| **Upgrade** | Add a toggle to switch between absolute (₪) and **cost-per-occupied-room** (CPOR by category). Add a horizontal benchmark reference line at industry CPOR (~₪2,800–3,400/room/month). |
| **Decision It Enables** | "Are costs rising because we're growing, or because we're becoming less efficient?" |

### 4.4 KPI Card Upgrades (All 14 Cards)

Per visualization playbook §3, every current KPI card is missing:

| Missing Element | Fix |
|-----------------|-----|
| Trend indicator (▲/▼) | Add % change vs. prior month |
| Sparkline | Add 7–12 period mini line chart |
| Context (vs. target) | Add target/benchmark reference |
| Color coding | Green (above target) / Red (below) / Yellow (within 5%) |

**Priority card upgrades:**

| Card | Specific Upgrade |
|------|-----------------|
| RevPAR | Add ▲/▼ vs. prior month + target line — highest visibility card |
| Tenant Retention | Replace with "₪ Revenue at Risk (12-month)" — financial framing instead of % |
| Avg Satisfaction | Add per-project breakdown tooltip; link to ADR correlation |
| CPOR | Add benchmark reference (Israeli mixed-use: ₪2,800–3,400/room/month) |
| Avg Occupancy | Split into "Best" / "Worst" project sub-label (currently hides 45%–91% range) |
| Staff Available | Replace with EPOR (Energy per Occupied Room) — more actionable |

### 4.5 Room Availability — Convert to Revenue Yield View

| Field | Content |
|-------|---------|
| **Current Element** | Grouped bar — Office / Meeting / Common availability % over time |
| **Limitation** | Availability tells you capacity, not whether that capacity is generating revenue. 95% available = 5% utilized = a problem, not a success. |
| **Upgrade** | Invert to **utilization %** (100 − availability). Overlay revenue-per-room-type if data exists. Add threshold coloring: <50% utilization in red (underperforming), >80% in green (healthy). |
| **Decision It Enables** | Which room types to reprice, repurpose, or promote. |

---

## 5. Implementation Roadmap

### Phase 1 — Quick Wins (Week 1)

| Task | Effort | Dependencies | Files Affected |
|------|--------|--------------|----------------|
| RevPAR Decomposition chart (Chart A) | 0.5 day | None | `modules/analytics_dashboard.py` |
| GOPPAR vs. CPOR Spread chart (Chart B) | 0.5 day | None | `modules/analytics_dashboard.py` |
| Tenant Churn Risk waterfall | 1 day | None | New section in `modules/analytics_dashboard.py` or new module |
| EPOR computation + chart + KPI card | 0.5 day | None | `data.py` (computation), `modules/analytics_dashboard.py` |
| KPI card ▲/▼ trend indicators (all 14) | 1 day | None | `style.py` (update `kpi_card`), `modules/analytics_dashboard.py` |

### Phase 2 — Strategic (Weeks 2–4)

| Task | Effort | Dependencies | Files Affected |
|------|--------|--------------|----------------|
| Break-Even Occupancy panel | 1 week | Fixed vs. variable cost split in `data.py` | `data.py`, `modules/analytics_dashboard.py` |
| Satisfaction → Revenue scatter | 3 days | Per-project ADR in `data.py` | `data.py`, `modules/analytics_dashboard.py` |
| Space Utilization heatmap | 3 days | None (project-level) | `modules/analytics_dashboard.py` |
| Income chart — stacked by project | 1 day | None | `modules/analytics_dashboard.py` |
| Cost chart — CPOR normalization toggle | 1 day | None | `modules/analytics_dashboard.py` |
| Segment Profitability analysis | 1 week | Cost allocation by sector in `data.py` | `data.py`, new module or section |

### Phase 3 — Foundation (Month 2+)

| Task | Effort | Dependencies | Files Affected |
|------|--------|--------------|----------------|
| Acquisition channel tracking | Data capture setup | Operational process change | `data.py` |
| Labor productivity overlay | 2 days | Dept-level revenue attribution | `data.py`, `modules/analytics_dashboard.py` |
| Preventive/Reactive maintenance split | 3 days | Maintenance categorization | `data.py`, `modules/analytics_dashboard.py` |
| Meeting Room Yield (RevPASM) | 1 week | PMS/booking system integration | New data source, new module |

---

## 6. Validation Criteria

| What to Validate | How |
|------------------|-----|
| P1 analyses produce numbers consistent with `data.py` ground truth | Unit tests: compute EPOR manually and compare to chart values |
| RevPAR decomposition passes ADR × (Occ/100) ≈ RevPAR | Tolerance: ±2% |
| Churn waterfall sums match `df_tenants` totals | Sum of ₪ at risk = sum of `Monthly Rent` for high-risk tenants |
| All imports remain clean after changes | Run `python -c "from modules.analytics_dashboard import render"` |
| No UI regressions | Dev-testing skill: import integrity + UI regression smoke tests |

---

## 7. Key Decisions & Assumptions

| Decision | Rationale |
|----------|-----------|
| **Segment**: Treated as Co-working/Flex (C) + Hotel extended-stay (H) | Portfolio characteristics: multi-tenant, lease-based, office/meeting room types |
| **F&B analyses excluded** | No restaurant/food-service operations in the portfolio |
| **RevPAR redesign: split into 2 charts** | Avoids overcrowding; decomposition and efficiency spread serve different audiences |
| **EPOR replaces "Staff Available" in Tier 2 KPI** | Raw headcount count is operational decoration without revenue context |
| **P1 ordering: D06 → D01 → D04 → C02** | Ordered by implementation effort (lowest first) within "no new data required" constraint |
| **Industry benchmarks used (not client-specific)** | All impact ranges sourced from `analysis-catalog.md` and labeled as benchmarks |

---

## 8. Next Steps

**Immediate action (today):**
1. Redesign the RevPAR chart into Chart A (Decomposition) + Chart B (GOPPAR/CPOR Spread)
2. Add the Tenant Churn Risk waterfall visualization

Both require **zero new data** and are implementable entirely from existing `df_revenue_per_unit`, `df_occupancy_trend`, and `df_tenants` DataFrames.
