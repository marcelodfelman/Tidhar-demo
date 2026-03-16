"""
data.py — Single source of truth for all Tidhar demo data.
Raw observables are hardcoded; all scores and KPIs are COMPUTED
so any parameter change cascades through the entire app in real time.
"""

import pandas as pd
import numpy as np
from datetime import date

# ─────────────────────────────────────────────
# REFERENCE DATE (controls all expiry countdowns)
# ─────────────────────────────────────────────
REF_DATE = date(2026, 3, 1)

# ─────────────────────────────────────────────
# 1. PROJECT-LEVEL SNAPSHOT
# ─────────────────────────────────────────────
PROJECTS = [
    "Tidhar Tower Givatayim",
    "Park HaMada Rehovot",
    "Bnei Brak Business Center",
    "Herzliya Marina Medical",
    "Cu High-Tech Park",
]

df_projects = pd.DataFrame({
    "Project":             PROJECTS,
    "Occupancy (%)":       [88, 72, 45, 91, 63],
    "Energy (kWh)":        [24_500, 31_200, 35_800, 18_900, 28_700],
    "Monthly Revenue (₪)": [3_200_000, 2_100_000, 980_000, 2_850_000, 1_750_000],
    # Churn Risk derived below from tenant-level scoring
})

# ─────────────────────────────────────────────
# ENERGY COST MODEL PARAMETERS (adjustable in UI)
# ─────────────────────────────────────────────
ENERGY_COST_PER_KWH = 0.55   # ₪/kWh Israeli industrial tariff Q1 2026
ENERGY_WASTE_FACTOR = 0.40   # % energy wasted in low-occupancy buildings
OCC_ALERT_THRESHOLD = 50     # occupancy % below which an inefficiency alert fires
NRG_ALERT_THRESHOLD = 0.80   # fraction of peak energy that triggers alert

# ─────────────────────────────────────────────
# 2. 12-MONTH HISTORICAL TRENDS
# ─────────────────────────────────────────────
MONTHS = pd.date_range("2025-03", periods=12, freq="MS").strftime("%b %Y").tolist()

# Occupancy trends (%) — each row is a month, columns are projects
_occ_data = {
    "Month": MONTHS,
    "Tidhar Tower Givatayim":       [82, 83, 84, 85, 86, 86, 87, 87, 88, 88, 88, 88],
    "Park HaMada Rehovot":          [78, 77, 76, 75, 74, 74, 73, 73, 72, 72, 72, 72],
    "Bnei Brak Business Center":    [60, 58, 56, 54, 52, 51, 50, 49, 48, 47, 46, 45],
    "Herzliya Marina Medical":      [85, 86, 87, 88, 89, 89, 90, 90, 91, 91, 91, 91],
    "Cu High-Tech Park":            [70, 69, 68, 67, 66, 66, 65, 65, 64, 64, 63, 63],
}
df_occupancy_trend = pd.DataFrame(_occ_data)

# Energy consumption trends (kWh)
_energy_data = {
    "Month": MONTHS,
    "Tidhar Tower Givatayim":       [23_000, 23_200, 23_500, 23_800, 24_000, 24_200, 24_300, 24_400, 24_400, 24_500, 24_500, 24_500],
    "Park HaMada Rehovot":          [28_000, 28_500, 29_000, 29_500, 29_800, 30_000, 30_500, 30_800, 31_000, 31_000, 31_100, 31_200],
    "Bnei Brak Business Center":    [33_000, 33_500, 34_000, 34_200, 34_500, 34_800, 35_000, 35_200, 35_400, 35_500, 35_700, 35_800],
    "Herzliya Marina Medical":      [20_000, 19_800, 19_600, 19_500, 19_300, 19_200, 19_100, 19_000, 18_900, 18_900, 18_900, 18_900],
    "Cu High-Tech Park":            [26_000, 26_500, 27_000, 27_200, 27_500, 27_800, 28_000, 28_200, 28_400, 28_500, 28_600, 28_700],
}
df_energy_trend = pd.DataFrame(_energy_data)

# ─────────────────────────────────────────────
# 3. TENANT-LEVEL RAW OBSERVABLES
#    Only factual inputs hardcoded — churn scores computed below.
# ─────────────────────────────────────────────

# Sector baseline churn tendency — adjustable via UI
SECTOR_BASE_RISK = {
    "Professional Services": 0.25,
    "Flex / Co-working":     0.55,
    "Healthcare":            0.10,
    "Technology":            0.30,
    "Food & Consumer":       0.20,
    "Defence":               0.08,
    "Finance":               0.15,
    "Telecom":               0.18,
    "Energy / Utilities":    0.12,
    "Insurance":             0.13,
}

# Default model weights (normalised internally — don't need to sum to 1)
DEFAULT_W_EXPIRY   = 0.40   # approaching lease end
DEFAULT_W_ACTIVITY = 0.35   # low badge / access activity
DEFAULT_W_SECTOR   = 0.15   # sector baseline
DEFAULT_W_RENT     = 0.10   # below-median rent → fewer switching costs

# Leases expiring within this window are scored on a sliding scale
EXPIRY_HORIZON_DAYS = 730   # 2 years

df_tenants = pd.DataFrame({
    "Tenant": [
        "Deloitte Israel", "WeWork Flex", "Maccabi Health", "Intel Labs",
        "Strauss HQ", "Elbit Systems", "Psagot Investments", "Wix.com",
        "Partner Comms", "Discount Bank Branch", "Amdocs R&D", "Check Point SW",
        "IEC Regional Office", "Harel Insurance", "Monday.com",
    ],
    "Project": [
        "Tidhar Tower Givatayim", "Tidhar Tower Givatayim", "Tidhar Tower Givatayim",
        "Park HaMada Rehovot", "Park HaMada Rehovot", "Park HaMada Rehovot",
        "Bnei Brak Business Center", "Bnei Brak Business Center", "Bnei Brak Business Center",
        "Herzliya Marina Medical", "Herzliya Marina Medical", "Herzliya Marina Medical",
        "Cu High-Tech Park", "Cu High-Tech Park", "Cu High-Tech Park",
    ],
    "Sector": [
        "Professional Services", "Flex / Co-working", "Healthcare",
        "Technology",            "Food & Consumer",   "Defence",
        "Finance",               "Technology",        "Telecom",
        "Healthcare",            "Technology",        "Technology",
        "Energy / Utilities",    "Insurance",         "Technology",
    ],
    "Lease Expiry": [
        "2027-06", "2026-09", "2028-01",
        "2026-12", "2027-03", "2028-06",
        "2026-05", "2026-04", "2026-07",
        "2028-12", "2027-09", "2029-01",
        "2026-08", "2027-11", "2026-06",
    ],
    "Monthly Rent (₪)": [
        420_000, 185_000, 310_000,
        380_000, 290_000, 510_000,
        120_000,  95_000, 145_000,
        550_000, 480_000, 620_000,
        280_000, 350_000, 410_000,
    ],
    # Badge scans, meeting bookings, visitor entries — normalised 0→1
    "Activity Score": [
        0.92, 0.65, 0.88,
        0.71, 0.55, 0.90,
        0.30, 0.22, 0.40,
        0.95, 0.82, 0.93,
        0.48, 0.70, 0.38,
    ],
})


# ─────────────────────────────────────────────
# CHURN SCORING ENGINE
# ─────────────────────────────────────────────

def compute_churn_scores(
    df,
    w_expiry=DEFAULT_W_EXPIRY,
    w_activity=DEFAULT_W_ACTIVITY,
    w_sector=DEFAULT_W_SECTOR,
    w_rent=DEFAULT_W_RENT,
    horizon=EXPIRY_HORIZON_DAYS,
    ref_date=REF_DATE,
):
    """
    Compute Churn Risk [0-1] from four first-principles signals.
    All weights adjustable by the UI. Returns a new DataFrame.

    Factors:
      expiry_score : 1.0 when expiry == today → 0.0 when >= horizon days away
      inactivity   : 1 - Activity Score
      sector_score : sector base risk from SECTOR_BASE_RISK
      rent_stress  : how far BELOW portfolio median (lower rent = easier to lose)
    """
    df = df.copy()
    expiry_dates = pd.to_datetime(df["Lease Expiry"]).dt.date
    days_left = [(e - ref_date).days for e in expiry_dates]
    df["Days to Expiry"] = days_left
    expiry_score = np.clip(1.0 - np.array(days_left, dtype=float) / horizon, 0.0, 1.0)
    inactivity   = 1.0 - df["Activity Score"].values
    sector_score = df["Sector"].map(SECTOR_BASE_RISK).fillna(0.25).values
    median_rent  = df["Monthly Rent (₪)"].median()
    rent_stress  = np.clip(
        (median_rent - df["Monthly Rent (₪)"].values) / median_rent, 0.0, 1.0
    )
    total_w = w_expiry + w_activity + w_sector + w_rent or 1.0
    churn = (
        w_expiry * expiry_score + w_activity * inactivity
        + w_sector * sector_score + w_rent * rent_stress
    ) / total_w
    df["Churn Risk"] = np.clip(churn, 0.0, 1.0).round(3)
    return df


def apply_risk_labels(df, high=0.60, medium=0.30):
    """Attach Risk Level label using caller-defined thresholds."""
    df = df.copy()
    df["Risk Level"] = df["Churn Risk"].apply(
        lambda x: "🔴 High Risk" if x >= high else ("🟡 Medium" if x >= medium else "🟢 Low")
    )
    return df


# Compute at import time with default weights
df_tenants  = compute_churn_scores(df_tenants)
df_tenants  = apply_risk_labels(df_tenants)

# Back-fill project-level Churn Risk as mean of tenant scores
_proj_churn = df_tenants.groupby("Project")["Churn Risk"].mean().reset_index()
df_projects = df_projects.merge(_proj_churn, on="Project", how="left")

# ─────────────────────────────────────────────
# 4. AGGREGATE KPI FUNCTIONS (computed, not static)
# ─────────────────────────────────────────────
TOTAL_PORTFOLIO_VALUE = "₪12.4B"


def get_tenants_at_risk(df=None, threshold=0.60):
    """Count tenants at or above the churn risk threshold."""
    if df is None:
        df = df_tenants
    return int((df["Churn Risk"] >= threshold).sum())


def get_energy_savings_opp(
    cost_per_kwh=ENERGY_COST_PER_KWH,
    waste_factor=ENERGY_WASTE_FACTOR,
    occ_thresh=OCC_ALERT_THRESHOLD,
):
    """Estimate annual energy savings from under-occupied buildings."""
    wasteful = df_projects.loc[df_projects["Occupancy (%)"] < occ_thresh, "Energy (kWh)"]
    annual   = wasteful.sum() * waste_factor * cost_per_kwh * 12
    return f"₪{annual:,.0f} / yr" if annual > 0 else "₪0 / yr"


# Convenience defaults for the header KPI bar
TENANTS_AT_RISK    = get_tenants_at_risk()
ENERGY_SAVINGS_OPP = get_energy_savings_opp()

# ─────────────────────────────────────────────
# 5. EBITDA SIMULATOR PARAMETERS
# Named constants — the simulator surfaces them as adjustable controls.
# ─────────────────────────────────────────────
BASELINE_EBITDA          = 50_000_000   # ₪50M
STEEL_EBITDA_SENSITIVITY = 0.40         # 1% steel ↑ → −0.40% EBITDA
RATE_COST_PER_100BPS     = 2_000_000    # ₪ cost per 100 bps rate rise
LABOR_EBITDA_SENSITIVITY = 0.25         # 1% efficiency gain → +0.25% EBITDA
EBITDA_TARGET_FLOOR      = 45_000_000   # ₪45M board minimum threshold

# ─────────────────────────────────────────────
# 5b. ANALYTICS DASHBOARD DATA
#     All new constants and DataFrames used exclusively by
#     modules/analytics_dashboard.py — no side-effects on existing modules.
# ─────────────────────────────────────────────

# Room inventory per project
ROOMS_PER_PROJECT = {
    "Tidhar Tower Givatayim":    320,
    "Park HaMada Rehovot":       240,
    "Bnei Brak Business Center": 180,
    "Herzliya Marina Medical":   280,
    "Cu High-Tech Park":         200,
}
TOTAL_ROOMS = sum(ROOMS_PER_PROJECT.values())   # 1 220

# Gross floor area per project (m²)
SQM_PER_PROJECT = {
    "Tidhar Tower Givatayim":    32_000,
    "Park HaMada Rehovot":       24_000,
    "Bnei Brak Business Center": 18_000,
    "Herzliya Marina Medical":   28_000,
    "Cu High-Tech Park":         20_000,
}

# Asset valuations (₪) — sum = ₪12.4B, consistent with TOTAL_PORTFOLIO_VALUE
ASSET_VALUE_PER_PROJECT = {
    "Tidhar Tower Givatayim":    3_800_000_000,
    "Park HaMada Rehovot":       2_500_000_000,
    "Bnei Brak Business Center": 1_600_000_000,
    "Herzliya Marina Medical":   2_800_000_000,
    "Cu High-Tech Park":         1_700_000_000,
}

# Tenant satisfaction scores (1–10 scale, quarterly survey)
SATISFACTION_SCORES = {
    "Tidhar Tower Givatayim":    8.9,
    "Park HaMada Rehovot":       7.8,
    "Bnei Brak Business Center": 6.8,
    "Herzliya Marina Medical":   9.1,
    "Cu High-Tech Park":         7.2,
}

# Average commercial lease duration (months) — 12-month trend
ALOS_BY_MONTH = [42.5, 43.0, 42.8, 43.5, 44.0, 43.8, 44.5, 45.0, 44.8, 45.5, 46.0, 46.2]

# ── 12-month Income Series ────────────────────────────────────────────────────
# Monthly revenue (₪) per project — slight upward/downward trend from snapshot
_income_data = {
    "Month": MONTHS,
    "Tidhar Tower Givatayim":    [3_020_000, 3_040_000, 3_060_000, 3_080_000, 3_100_000, 3_120_000,
                                  3_140_000, 3_160_000, 3_180_000, 3_200_000, 3_200_000, 3_200_000],
    "Park HaMada Rehovot":       [2_200_000, 2_190_000, 2_180_000, 2_165_000, 2_150_000, 2_140_000,
                                  2_130_000, 2_120_000, 2_110_000, 2_100_000, 2_100_000, 2_100_000],
    "Bnei Brak Business Center": [1_100_000, 1_080_000, 1_060_000, 1_040_000, 1_020_000, 1_005_000,
                                    990_000,   985_000,   982_000,   980_000,   980_000,   980_000],
    "Herzliya Marina Medical":   [2_700_000, 2_720_000, 2_740_000, 2_760_000, 2_790_000, 2_810_000,
                                  2_820_000, 2_830_000, 2_840_000, 2_850_000, 2_850_000, 2_850_000],
    "Cu High-Tech Park":         [1_800_000, 1_790_000, 1_780_000, 1_775_000, 1_768_000, 1_762_000,
                                  1_758_000, 1_754_000, 1_752_000, 1_750_000, 1_750_000, 1_750_000],
}
df_monthly_income = pd.DataFrame(_income_data)
_income_proj_cols = [c for c in df_monthly_income.columns if c != "Month"]
df_monthly_income["Total"] = df_monthly_income[_income_proj_cols].sum(axis=1)

# ── 12-month Cost Series ──────────────────────────────────────────────────────
# Energy cost derived from energy trend aggregate × ENERGY_COST_PER_KWH
_energy_total_kwh = (
    df_energy_trend["Tidhar Tower Givatayim"]
    + df_energy_trend["Park HaMada Rehovot"]
    + df_energy_trend["Bnei Brak Business Center"]
    + df_energy_trend["Herzliya Marina Medical"]
    + df_energy_trend["Cu High-Tech Park"]
)
_energy_cost_monthly = (_energy_total_kwh * ENERGY_COST_PER_KWH).round(0).astype(int).tolist()

df_costs = pd.DataFrame({
    "Month":           MONTHS,
    "Energy (₪)":      _energy_cost_monthly,
    "Labor (₪)":       [4_200_000, 4_200_000, 4_250_000, 4_250_000, 4_300_000, 4_300_000,
                        4_350_000, 4_350_000, 4_400_000, 4_400_000, 4_450_000, 4_450_000],
    "Maintenance (₪)": [  850_000,   860_000,   870_000,   865_000,   875_000,   880_000,
                          885_000,   890_000,   895_000,   900_000,   910_000,   920_000],
    "Other (₪)":       [  320_000,   330_000,   325_000,   340_000,   335_000,   340_000,
                          345_000,   350_000,   355_000,   360_000,   358_000,   365_000],
})
df_costs["Total (₪)"] = (
    df_costs["Energy (₪)"] + df_costs["Labor (₪)"]
    + df_costs["Maintenance (₪)"] + df_costs["Other (₪)"]
)

# ── Revenue-per-Unit Series ───────────────────────────────────────────────────
# All columns derived from df_monthly_income and room/headcount constants
_occ_proj_cols  = [c for c in df_occupancy_trend.columns if c != "Month"]
_avg_occ_series = pd.to_numeric(
    df_occupancy_trend[_occ_proj_cols].mean(axis=1), errors="coerce"
).fillna(0.0).to_numpy(dtype=float) / 100.0
_occupied_rooms = (_avg_occ_series * TOTAL_ROOMS).round(0)
_headcount_base = np.array([158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 170], dtype=float)

df_revenue_per_unit = pd.DataFrame({
    "Month":              MONTHS,
    "RevPAR (₪)":         (df_monthly_income["Total"] / TOTAL_ROOMS).round(0).astype(int),
    "ADR (₪)":            (df_monthly_income["Total"] / _occupied_rooms).round(0).astype(int),
    "Rev per Person (₪)": (df_monthly_income["Total"] / _headcount_base).round(0).astype(int),
    "GOPPAR (₪)":         ((df_monthly_income["Total"] - df_costs["Total (₪)"]) / TOTAL_ROOMS).round(0).astype(int),
})

# ── 12-month Manpower Series ──────────────────────────────────────────────────
df_manpower = pd.DataFrame({
    "Month":           MONTHS,
    "Total Headcount": [158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 170],
    "Available":       [142, 144, 145, 147, 148, 149, 150, 151, 152, 153, 153, 155],
    "On Leave":        [ 10,  10,   9,   9,   9,   9,   9,   9,   9,   9,  10,  10],
    "Contractors":     [  6,   5,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5],
})
df_manpower["Availability (%)"] = (
    df_manpower["Available"] / df_manpower["Total Headcount"] * 100
).round(1)

# ── Department Snapshot ───────────────────────────────────────────────────────
df_staff_by_dept = pd.DataFrame({
    "Department":      ["Facilities Mgmt", "Security", "Administration", "IT & Systems",
                        "Finance", "Leasing", "Maintenance"],
    "Total":           [28, 35, 18, 14, 12, 16, 47],
    "Available":       [26, 33, 17, 13, 11, 15, 40],
    "Utilization (%)": [92, 94, 94, 93, 92, 94, 85],
})

# ── Room Availability by Type (12-month %) ────────────────────────────────────
df_rooms_by_type = pd.DataFrame({
    "Month":       MONTHS,
    "Office (%)":  [88, 87, 86, 85, 84, 84, 83, 83, 82, 82, 82, 82],
    "Meeting (%)": [72, 71, 70, 69, 68, 68, 67, 67, 66, 66, 66, 66],
    "Common (%)":  [95, 95, 94, 94, 93, 93, 93, 92, 92, 92, 91, 91],
})

# ── Per-Project Asset Ratio Table (point-in-time) ─────────────────────────────
# Cap rates and GRM are realistic benchmarks for Israeli prime commercial RE.
# Full consistency with exact revenue figures would require a full DCF model;
# these are industry-calibrated values suitable for the demo dashboard.
df_cap_table = pd.DataFrame({
    "Project":            PROJECTS,
    "Asset Value (₪B)":   [3.80, 2.50, 1.60, 2.80, 1.70],
    "Annual NOI (₪M)":    [209.0, 130.0, 76.8, 158.2, 92.3],
    "Cap Rate (%)":       [5.50, 5.20, 4.80, 5.65, 5.43],
    "GRM":                [18.2, 19.2, 20.8, 17.7, 18.4],
})

# ── CPOR Monthly Series (Cost per Occupied Room) ─────────────────────────────
_occ_avg_frac_series = (
    df_occupancy_trend[[c for c in df_occupancy_trend.columns if c != "Month"]]
    .mean(axis=1) / 100.0
)
_occupied_rooms_monthly = (_occ_avg_frac_series * TOTAL_ROOMS).round(0).clip(lower=1)
df_cpor_monthly = pd.DataFrame({
    "Month": MONTHS,
    "CPOR (₪)": (df_costs["Total (₪)"] / _occupied_rooms_monthly).round(0).astype(int),
})

# ── EPOR per Project (Energy per Occupied Room, latest snapshot) ──────────────
EPOR_BENCHMARK = 150.0   # kWh per occupied room/month — portfolio benchmark
_epor_rows = []
for _p in PROJECTS:
    _occ = df_projects.loc[df_projects["Project"] == _p, "Occupancy (%)"].values[0]
    _kwh = df_projects.loc[df_projects["Project"] == _p, "Energy (kWh)"].values[0]
    _rms = ROOMS_PER_PROJECT[_p]
    _occ_rms = max(_occ / 100.0 * _rms, 1)
    _epor_rows.append({"Project": _p, "EPOR (kWh)": round(_kwh / _occ_rms, 1),
                        "Occupied Rooms": int(_occ_rms), "Energy (kWh)": _kwh})
df_epor_project = pd.DataFrame(_epor_rows)

# ─────────────────────────────────────────────
# 5c. CONSTRUCTION PROJECT MANAGER DATA (MVP)
#     Synthetic but coherent construction data used by
#     modules/construction_pm.py.
# ─────────────────────────────────────────────

CONSTRUCTION_PROJECTS = [
    "Ramat Gan North Towers",
    "Holon Mixed-Use Campus",
    "Jerusalem Central Offices",
    "Haifa Waterfront Residences",
    "Beer Sheva Innovation Hub",
]

df_construction_projects = pd.DataFrame({
    "Project": CONSTRUCTION_PROJECTS,
    "Budget at Completion (₪)": [410_000_000, 360_000_000, 335_000_000, 390_000_000, 300_000_000],
    "Budget To Date (₪)": [235_000_000, 188_000_000, 165_000_000, 210_000_000, 152_000_000],
    "Actual Cost To Date (₪)": [241_000_000, 196_000_000, 181_000_000, 214_000_000, 159_000_000],
    "Open RFIs": [14, 23, 31, 17, 21],
    "Active Subcontractors": [12, 15, 13, 11, 14],
    "Safety Incidents MTD": [1, 2, 3, 1, 2],
    "Delay Cost Range Low (₪/day)": [95_000, 85_000, 78_000, 90_000, 70_000],
    "Delay Cost Range High (₪/day)": [390_000, 345_000, 320_000, 375_000, 290_000],
})

df_construction_schedule = pd.DataFrame({
    "Project": [
        "Ramat Gan North Towers", "Ramat Gan North Towers", "Ramat Gan North Towers", "Ramat Gan North Towers", "Ramat Gan North Towers", "Ramat Gan North Towers",
        "Holon Mixed-Use Campus", "Holon Mixed-Use Campus", "Holon Mixed-Use Campus", "Holon Mixed-Use Campus", "Holon Mixed-Use Campus", "Holon Mixed-Use Campus",
        "Jerusalem Central Offices", "Jerusalem Central Offices", "Jerusalem Central Offices", "Jerusalem Central Offices", "Jerusalem Central Offices", "Jerusalem Central Offices",
        "Haifa Waterfront Residences", "Haifa Waterfront Residences", "Haifa Waterfront Residences", "Haifa Waterfront Residences", "Haifa Waterfront Residences", "Haifa Waterfront Residences",
        "Beer Sheva Innovation Hub", "Beer Sheva Innovation Hub", "Beer Sheva Innovation Hub", "Beer Sheva Innovation Hub", "Beer Sheva Innovation Hub", "Beer Sheva Innovation Hub",
    ],
    "Work Package": [
        "Foundations", "Structure", "Facade", "MEP Rough-In", "Interior Finishes", "Commissioning",
        "Foundations", "Structure", "Facade", "MEP Rough-In", "Interior Finishes", "Commissioning",
        "Foundations", "Structure", "Facade", "MEP Rough-In", "Interior Finishes", "Commissioning",
        "Foundations", "Structure", "Facade", "MEP Rough-In", "Interior Finishes", "Commissioning",
        "Foundations", "Structure", "Facade", "MEP Rough-In", "Interior Finishes", "Commissioning",
    ],
    "Weight (%)": [12, 22, 16, 19, 21, 10] * 5,
    "Is Critical": [True, True, True, True, True, True] * 5,
    "Predecessor": [None, "Foundations", "Structure", "Facade", "MEP Rough-In", "Interior Finishes"] * 5,
    "Baseline Start": [
        "2025-02-01", "2025-05-15", "2025-09-01", "2025-10-15", "2026-01-10", "2026-05-20",
        "2025-03-01", "2025-06-20", "2025-10-01", "2025-11-15", "2026-02-01", "2026-06-10",
        "2025-02-15", "2025-06-01", "2025-09-20", "2025-11-10", "2026-01-20", "2026-05-15",
        "2025-03-10", "2025-06-15", "2025-09-15", "2025-11-01", "2026-01-15", "2026-05-25",
        "2025-04-01", "2025-07-01", "2025-10-20", "2025-12-01", "2026-02-10", "2026-06-20",
    ],
    "Baseline Finish": [
        "2025-05-15", "2025-09-01", "2025-12-15", "2026-02-28", "2026-05-20", "2026-07-20",
        "2025-06-20", "2025-10-01", "2026-01-20", "2026-03-20", "2026-06-10", "2026-08-15",
        "2025-06-01", "2025-09-20", "2026-01-10", "2026-03-30", "2026-05-15", "2026-07-25",
        "2025-06-15", "2025-09-15", "2025-12-30", "2026-03-10", "2026-05-25", "2026-08-05",
        "2025-07-01", "2025-10-20", "2026-01-30", "2026-04-10", "2026-06-20", "2026-09-05",
    ],
    "Forecast Start": [
        "2025-02-08", "2025-05-24", "2025-09-10", "2025-10-28", "2026-01-20", "2026-06-08",
        "2025-03-08", "2025-07-05", "2025-10-20", "2025-12-03", "2026-02-20", "2026-07-03",
        "2025-03-01", "2025-06-22", "2025-10-18", "2025-12-06", "2026-02-22", "2026-06-25",
        "2025-03-15", "2025-06-28", "2025-09-25", "2025-11-20", "2026-01-25", "2026-06-12",
        "2025-04-08", "2025-07-18", "2025-11-08", "2025-12-20", "2026-02-24", "2026-07-10",
    ],
    "Forecast Finish": [
        "2025-05-24", "2025-09-10", "2025-12-30", "2026-03-14", "2026-06-08", "2026-08-04",
        "2025-07-05", "2025-10-20", "2026-02-10", "2026-04-12", "2026-07-03", "2026-09-06",
        "2025-06-22", "2025-10-18", "2026-02-14", "2026-04-26", "2026-06-25", "2026-09-02",
        "2025-06-28", "2025-09-25", "2026-01-15", "2026-03-28", "2026-06-12", "2026-08-20",
        "2025-07-18", "2025-11-08", "2026-02-24", "2026-05-05", "2026-07-10", "2026-09-30",
    ],
    "Actual Start": [
        "2025-02-08", "2025-05-24", "2025-09-10", "2025-10-28", "2026-01-20", None,
        "2025-03-08", "2025-07-05", "2025-10-20", "2025-12-03", "2026-02-20", None,
        "2025-03-01", "2025-06-22", "2025-10-18", "2025-12-06", None, None,
        "2025-03-15", "2025-06-28", "2025-09-25", "2025-11-20", "2026-01-25", None,
        "2025-04-08", "2025-07-18", "2025-11-08", "2025-12-20", "2026-02-24", None,
    ],
    "Actual Finish": [
        "2025-05-24", "2025-09-12", "2026-01-04", None, None, None,
        "2025-07-10", "2025-10-30", None, None, None, None,
        "2025-06-30", "2025-11-01", None, None, None, None,
        "2025-06-30", "2025-10-02", "2026-01-28", None, None, None,
        "2025-07-22", "2025-11-20", None, None, None, None,
    ],
})

for _date_col in [
    "Baseline Start", "Baseline Finish", "Forecast Start", "Forecast Finish", "Actual Start", "Actual Finish"
]:
    df_construction_schedule[_date_col] = pd.to_datetime(df_construction_schedule[_date_col], errors="coerce")


def _bounded_progress(start, finish, as_of_ts: pd.Timestamp) -> float:
    """Return bounded [0,1] progress for an activity between start and finish."""
    if pd.isna(start) or pd.isna(finish):
        return 0.0
    if as_of_ts <= start:
        return 0.0
    if as_of_ts >= finish:
        return 1.0
    dur = max((finish - start).days, 1)
    return float((as_of_ts - start).days / dur)


def get_project_schedule_status(project: str, as_of_date=REF_DATE) -> dict:
    """Compute schedule/cost status for one project at an as-of date."""
    as_of_ts = pd.Timestamp(as_of_date)
    sched = df_construction_schedule[df_construction_schedule["Project"] == project].copy()
    meta = df_construction_projects[df_construction_projects["Project"] == project].iloc[0]

    weights = sched["Weight (%)"].astype(float)
    planned_w = 0.0
    actual_w = 0.0

    for _, row in sched.iterrows():
        w = float(row["Weight (%)"])
        planned_w += w * _bounded_progress(row["Baseline Start"], row["Baseline Finish"], as_of_ts)

        if pd.notna(row["Actual Start"]):
            actual_finish_ref = row["Actual Finish"] if pd.notna(row["Actual Finish"]) else row["Forecast Finish"]
            actual_w += w * _bounded_progress(row["Actual Start"], actual_finish_ref, as_of_ts)
        elif pd.notna(row["Actual Finish"]) and as_of_ts >= row["Actual Finish"]:
            actual_w += w

    planned_pct = planned_w / weights.sum() * 100.0 if weights.sum() else 0.0
    actual_pct = actual_w / weights.sum() * 100.0 if weights.sum() else 0.0
    gap_pts = actual_pct - planned_pct
    spi = (actual_pct / planned_pct) if planned_pct > 0 else 1.0

    bac = float(meta["Budget at Completion (₪)"])
    ac = float(meta["Actual Cost To Date (₪)"])
    ev = bac * (actual_pct / 100.0)
    pv = bac * (planned_pct / 100.0)
    cpi = (ev / ac) if ac > 0 else 1.0
    eac = (ac / max(actual_pct / 100.0, 0.05)) if actual_pct > 0 else bac
    eac_var_pct = ((eac - bac) / bac * 100.0) if bac else 0.0

    baseline_finish = pd.to_datetime(sched["Baseline Finish"].max())
    forecast_finish = pd.to_datetime(sched["Forecast Finish"].max())
    delay_days = int((forecast_finish - baseline_finish).days)

    overdue_critical = int(((sched["Is Critical"]) & (sched["Baseline Finish"] < as_of_ts) & (sched["Actual Finish"].isna())).sum())

    if spi < 0.93 or cpi < 0.93 or overdue_critical > 0:
        status = "Red"
    elif spi < 0.98 or cpi < 0.98 or delay_days > 0:
        status = "Amber"
    else:
        status = "Green"

    return {
        "Project": project,
        "Planned % Today": round(planned_pct, 1),
        "Actual % Today": round(actual_pct, 1),
        "Gap (pts)": round(gap_pts, 1),
        "SPI": round(spi, 2),
        "CPI": round(cpi, 2),
        "Delay Days": delay_days,
        "Overdue Critical": overdue_critical,
        "PV (₪)": pv,
        "EV (₪)": ev,
        "AC (₪)": ac,
        "EAC (₪)": eac,
        "EAC Var (%)": round(eac_var_pct, 1),
        "BAC (₪)": bac,
        "Status": status,
        "Open RFIs": int(meta["Open RFIs"]),
        "Low Delay Cost (₪/day)": float(meta["Delay Cost Range Low (₪/day)"]),
        "High Delay Cost (₪/day)": float(meta["Delay Cost Range High (₪/day)"]),
    }


def get_construction_status_table(project: str = "All Projects", as_of_date=REF_DATE) -> pd.DataFrame:
    """Return per-project status table at as-of date."""
    selected = CONSTRUCTION_PROJECTS if project == "All Projects" else [project]
    rows = [get_project_schedule_status(p, as_of_date=as_of_date) for p in selected]
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    _status_rank = {"Red": 0, "Amber": 1, "Green": 2}
    df["_rank"] = df["Status"].map(_status_rank).fillna(3)
    df = df.sort_values(["_rank", "Delay Days", "EAC Var (%)"], ascending=[True, False, False]).drop(columns=["_rank"])
    return df.reset_index(drop=True)


def get_construction_progress_curve(project: str = "All Projects") -> pd.DataFrame:
    """Compute planned/actual progress curve over the last 12 monthly cutoffs."""
    cutoffs = pd.date_range("2025-04-01", periods=12, freq="MS")
    rows = []
    selected = CONSTRUCTION_PROJECTS if project == "All Projects" else [project]

    for d in cutoffs:
        statuses = [get_project_schedule_status(p, as_of_date=d.date()) for p in selected]
        if not statuses:
            continue
        planned = float(np.mean([s["Planned % Today"] for s in statuses]))
        actual = float(np.mean([s["Actual % Today"] for s in statuses]))
        rows.append({"Month": d.strftime("%b %Y"), "Planned (%)": round(planned, 1), "Actual (%)": round(actual, 1)})

    return pd.DataFrame(rows)


def get_construction_gantt(project: str = "All Projects", as_of_date=REF_DATE) -> pd.DataFrame:
    """Return baseline and forecast/actual timeline rows for Gantt rendering."""
    as_of_ts = pd.Timestamp(as_of_date)
    sched = df_construction_schedule.copy()
    if project != "All Projects":
        sched = sched[sched["Project"] == project].copy()

    rows = []
    for _, row in sched.iterrows():
        task = row["Work Package"] if project != "All Projects" else f"{row['Project']} | {row['Work Package']}"
        predecessor = row["Predecessor"]
        predecessor_task = (
            predecessor if project != "All Projects" or predecessor is None
            else f"{row['Project']} | {predecessor}"
        )

        rows.append({
            "Project": row["Project"],
            "Task": task,
            "Track": "Baseline",
            "Start": row["Baseline Start"],
            "Finish": row["Baseline Finish"],
            "Is Critical": bool(row["Is Critical"]),
            "State": "Baseline",
            "Predecessor Task": predecessor_task,
        })

        run_start = row["Actual Start"] if pd.notna(row["Actual Start"]) else row["Forecast Start"]
        run_finish = row["Actual Finish"] if pd.notna(row["Actual Finish"]) else row["Forecast Finish"]
        if pd.notna(row["Actual Finish"]) and row["Actual Finish"] <= as_of_ts:
            state = "Done"
        elif row["Baseline Finish"] < as_of_ts and pd.isna(row["Actual Finish"]):
            state = "Delayed"
        elif bool(row["Is Critical"]):
            state = "Critical"
        else:
            state = "In Progress"

        rows.append({
            "Project": row["Project"],
            "Task": task,
            "Track": "Forecast/Actual",
            "Start": run_start,
            "Finish": run_finish,
            "Is Critical": bool(row["Is Critical"]),
            "State": state,
            "Predecessor Task": predecessor_task,
        })

    return pd.DataFrame(rows)

df_construction_progress = pd.DataFrame({
    "Month": MONTHS,
    "Planned (%)": [6, 12, 18, 26, 34, 43, 52, 61, 70, 79, 88, 96],
    "Actual (%)": [5, 10, 16, 22, 30, 39, 47, 55, 63, 71, 79, 87],
})

df_construction_budget = pd.DataFrame({
    "Month": MONTHS,
    "Planned Spend (₪)": [
        82_000_000, 85_000_000, 88_000_000, 90_000_000, 92_000_000, 94_000_000,
        95_000_000, 97_000_000, 98_000_000, 100_000_000, 101_000_000, 103_000_000,
    ],
    "Actual Spend (₪)": [
        84_000_000, 88_000_000, 90_000_000, 93_000_000, 95_000_000, 97_000_000,
        99_000_000, 100_000_000, 102_000_000, 103_000_000, 105_000_000, 108_000_000,
    ],
})

df_construction_safety = pd.DataFrame({
    "Month": MONTHS,
    "Lost Time Incidents": [0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    "Near Misses": [2, 3, 2, 4, 3, 2, 5, 3, 4, 5, 3, 4],
    "Worker Hours": [175_000, 178_000, 181_000, 183_000, 186_000, 188_000, 191_000, 194_000, 196_000, 198_000, 201_000, 204_000],
})

df_construction_risks = pd.DataFrame({
    "Risk ID": ["R-001", "R-002", "R-003", "R-004", "R-005", "R-006", "R-007"],
    "Project": [
        "Ramat Gan North Towers",
        "Holon Mixed-Use Campus",
        "Jerusalem Central Offices",
        "Haifa Waterfront Residences",
        "Beer Sheva Innovation Hub",
        "Jerusalem Central Offices",
        "Holon Mixed-Use Campus",
    ],
    "Category": ["Permits", "Supply Chain", "Concrete", "Design", "Labor", "MEP", "Safety"],
    "Description": [
        "Municipality permit extension delayed",
        "Facade material lead-time increased",
        "Concrete strength test rework",
        "Late architectural IFC package",
        "Skilled labor shortage in finishing phase",
        "MEP coordination clashes",
        "Repeated near-miss events in tower crane zone",
    ],
    "Probability (%)": [35, 40, 55, 30, 45, 50, 60],
    "Impact (₪)": [7_500_000, 5_800_000, 9_200_000, 4_600_000, 6_700_000, 8_100_000, 3_900_000],
    "Severity": ["High", "High", "Critical", "Medium", "High", "Critical", "Critical"],
    "Owner": ["PMO", "Procurement", "QA/QC", "Design", "HR", "Engineering", "HSE"],
})

df_construction_milestones = pd.DataFrame({
    "Project": [
        "Ramat Gan North Towers",
        "Holon Mixed-Use Campus",
        "Jerusalem Central Offices",
        "Haifa Waterfront Residences",
        "Beer Sheva Innovation Hub",
        "Jerusalem Central Offices",
    ],
    "Milestone": [
        "Basement waterproofing complete",
        "Tower A structure top-out",
        "Facade package approved",
        "MEP rough-in complete",
        "Public utility connection",
        "Final fire safety audit",
    ],
    "Planned Date": [
        "2026-02-15",
        "2026-03-10",
        "2026-01-20",
        "2026-04-05",
        "2026-03-01",
        "2026-02-28",
    ],
    "Forecast Date": [
        "2026-02-22",
        "2026-03-24",
        "2026-04-15",
        "2026-04-12",
        "2026-03-18",
        "2026-03-25",
    ],
    "Status": ["Done", "Open", "Open", "Open", "Open", "Open"],
})


def get_construction_snapshot(project: str = "All Projects") -> dict:
    """Return aggregated KPIs for the construction PM dashboard."""
    status_df = get_construction_status_table(project=project, as_of_date=REF_DATE)

    if project == "All Projects":
        risks = df_construction_risks.copy()
        milestones = df_construction_milestones.copy()
    else:
        risks = df_construction_risks[df_construction_risks["Project"] == project].copy()
        milestones = df_construction_milestones[df_construction_milestones["Project"] == project].copy()

    if status_df.empty:
        planned_progress = 0.0
        actual_progress = 0.0
        schedule_var = 0.0
        spi = 1.0
        cpi = 1.0
        delay_days = 0
        eac_var_pct = 0.0
        planned_cost = 0.0
        actual_cost = 0.0
        delay_cost_low = 0.0
        delay_cost_high = 0.0
    else:
        planned_progress = float(status_df["Planned % Today"].mean())
        actual_progress = float(status_df["Actual % Today"].mean())
        schedule_var = actual_progress - planned_progress
        spi = float(status_df["EV (₪)"].sum() / max(status_df["PV (₪)"].sum(), 1.0))
        cpi = float(status_df["EV (₪)"].sum() / max(status_df["AC (₪)"].sum(), 1.0))
        delay_days = int(status_df["Delay Days"].max())
        eac_var_pct = float((status_df["EAC (₪)"].sum() - status_df["BAC (₪)"].sum()) / max(status_df["BAC (₪)"].sum(), 1.0) * 100.0)
        planned_cost = float(status_df["PV (₪)"].sum())
        actual_cost = float(status_df["AC (₪)"].sum())
        delay_cost_low = float(status_df["Low Delay Cost (₪/day)"].sum())
        delay_cost_high = float(status_df["High Delay Cost (₪/day)"].sum())

    budget_var_pct = ((actual_cost - planned_cost) / planned_cost * 100.0) if planned_cost else 0.0

    critical_risks = int((risks["Severity"] == "Critical").sum()) if not risks.empty else 0
    high_risks = int((risks["Severity"] == "High").sum()) if not risks.empty else 0

    milestones = milestones.copy()
    if not milestones.empty:
        milestones["Planned Date"] = pd.to_datetime(milestones["Planned Date"]).dt.date
        overdue_mask = (milestones["Planned Date"] < REF_DATE) & (milestones["Status"] != "Done")
        overdue_milestones = int(overdue_mask.sum())
    else:
        overdue_milestones = 0

    lti_ytd = int(df_construction_safety["Lost Time Incidents"].sum())
    worker_hours_ytd = float(df_construction_safety["Worker Hours"].sum())
    trir = (lti_ytd * 200_000.0 / worker_hours_ytd) if worker_hours_ytd else 0.0

    return {
        "planned_progress": planned_progress,
        "actual_progress": actual_progress,
        "schedule_var": schedule_var,
        "spi": round(spi, 2),
        "cpi": round(cpi, 2),
        "delay_days": delay_days,
        "planned_cost": planned_cost,
        "actual_cost": actual_cost,
        "budget_var_pct": budget_var_pct,
        "eac_var_pct": round(eac_var_pct, 1),
        "delay_cost_low": delay_cost_low,
        "delay_cost_high": delay_cost_high,
        "critical_risks": critical_risks,
        "high_risks": high_risks,
        "overdue_milestones": overdue_milestones,
        "lti_ytd": lti_ytd,
        "trir": trir,
        "open_rfis": int(status_df["Open RFIs"].sum()) if not status_df.empty else 0,
        "status_df": status_df,
    }

# ─────────────────────────────────────────────
# 6. MOCK AI DOCUMENT EXTRACTION
# ─────────────────────────────────────────────
MOCK_LEASE_CLAUSE = (
    "The Tenant ('Wix.com Ltd.') shall occupy floors 8-12 of Tidhar Tower Givatayim "
    "for a period commencing January 1, 2024 and terminating December 31, 2028. "
    "Rent shall be linked to the Israeli Consumer Price Index (CPI) and adjusted "
    "annually on January 1st. The Tenant shall have the right to renew this lease "
    "for two additional periods of 36 months each, subject to 180 days' prior "
    "written notice."
)

MOCK_AI_EXTRACTION = {
    "document_type": "Commercial Lease Agreement",
    "confidence": 0.97,
    "extracted_fields": {
        "tenant": "Wix.com Ltd.",
        "property": "Tidhar Tower Givatayim, Floors 8-12",
        "expiration_date": "2028-12-31",
        "index_linkage": "Israeli CPI — Annual adjustment on Jan 1st",
        "renewal_option": "2 × 36-month extensions (180-day notice required)",
        "lease_duration_months": 60,
    },
    "risk_flags": [
        "Long renewal window may limit rent re-pricing flexibility",
        "CPI linkage exposes landlord to low-inflation scenarios",
    ],
}
