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
