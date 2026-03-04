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
_avg_occ_series = df_occupancy_trend[_occ_proj_cols].mean(axis=1).values / 100.0
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
