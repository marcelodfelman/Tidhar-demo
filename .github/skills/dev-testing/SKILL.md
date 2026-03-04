---
name: dev-testing
description: This skill should be used when a developer needs to validate, test, or quality-assure the Tidhar Decision Intelligence Streamlit application. It covers import integrity checks, data-layer validation, module smoke tests, UI regression testing, and structured defect reporting for the Streamlit codebase.
---

# Skill: Development Testing

## 1. Purpose

Provide a systematic, reproducible testing workflow for the Tidhar Decision Intelligence Portal. Apply this skill to catch regressions after edits, validate new features before merge, and produce structured defect reports. Testing is organized in three layers: **Import & Syntax**, **Data Layer**, and **Module / UI**.

## 2. Testing Layers

```
Layer 1 — Import & Syntax     Fast, no-browser, whole-project
Layer 2 — Data Layer          Validate constants, DataFrames, and computation helpers
Layer 3 — Module / UI         Exercise each render() function via live Streamlit session
```

Run layers in order. Stop at the first failing layer and fix before proceeding.

## 3. Layer 1 — Import & Syntax Checks

### 3.1 Syntax validation (all files)

```bash
python -m py_compile app.py data.py style.py modules/asset_monitoring.py modules/ebitda_simulator.py modules/doc_intelligence.py
```

**Pass criterion:** Command exits with code 0 and produces no output.
**Fail action:** Note the file and line number from the error, fix the syntax error, re-run.

### 3.2 Import graph validation

```bash
python -c "import app"
```

**Pass criterion:** No `ImportError`, `ModuleNotFoundError`, or `AttributeError`.
**Fail action:** Identify the missing or renamed symbol; trace it back to `data.py`, `style.py`, or the relevant module.

### 3.3 Module import isolation

```bash
python -c "from modules import asset_monitoring, ebitda_simulator, doc_intelligence; print('modules OK')"
```

**Pass criterion:** Prints `modules OK`.

## 4. Layer 2 — Data Layer Validation

### 4.1 Scalar constants

Run this inline script to assert key constants are present and sensible:

```python
python - <<'EOF'
from data import (
    TOTAL_PORTFOLIO_VALUE, ENERGY_SAVINGS_OPP, TENANTS_AT_RISK,
    PROJECTS, df_projects, df_occupancy_trend, df_energy_trend, df_tenants,
    DEFAULT_W_EXPIRY, DEFAULT_W_ACTIVITY, DEFAULT_W_SECTOR, DEFAULT_W_RENT,
    ENERGY_COST_PER_KWH, ENERGY_WASTE_FACTOR,
    OCC_ALERT_THRESHOLD, NRG_ALERT_THRESHOLD,
)
assert isinstance(TOTAL_PORTFOLIO_VALUE, (int, float)) and TOTAL_PORTFOLIO_VALUE > 0, "TOTAL_PORTFOLIO_VALUE invalid"
assert isinstance(ENERGY_SAVINGS_OPP, (int, float)) and ENERGY_SAVINGS_OPP > 0, "ENERGY_SAVINGS_OPP invalid"
assert isinstance(TENANTS_AT_RISK, (int, float)), "TENANTS_AT_RISK invalid"
assert isinstance(PROJECTS, list) and len(PROJECTS) > 0, "PROJECTS must be a non-empty list"
print("Scalar constants: OK")
EOF
```

**Pass criterion:** Prints `Scalar constants: OK`.

### 4.2 DataFrame shape and column validation

```python
python - <<'EOF'
import pandas as pd
from data import df_projects, df_occupancy_trend, df_energy_trend, df_tenants

assert isinstance(df_projects, pd.DataFrame) and not df_projects.empty, "df_projects empty"
assert isinstance(df_occupancy_trend, pd.DataFrame) and not df_occupancy_trend.empty, "df_occupancy_trend empty"
assert isinstance(df_energy_trend, pd.DataFrame) and not df_energy_trend.empty, "df_energy_trend empty"
assert isinstance(df_tenants, pd.DataFrame) and not df_tenants.empty, "df_tenants empty"
print("DataFrames: OK")
print(f"  df_projects      {df_projects.shape}  cols={list(df_projects.columns)}")
print(f"  df_occupancy     {df_occupancy_trend.shape}  cols={list(df_occupancy_trend.columns)}")
print(f"  df_energy        {df_energy_trend.shape}  cols={list(df_energy_trend.columns)}")
print(f"  df_tenants       {df_tenants.shape}  cols={list(df_tenants.columns)}")
EOF
```

**Pass criterion:** Prints `DataFrames: OK` followed by shape/column info.

### 4.3 Computation helper validation

```python
python - <<'EOF'
from data import df_tenants, compute_churn_scores, apply_risk_labels
import pandas as pd
result = compute_churn_scores(df_tenants)
assert isinstance(result, pd.DataFrame), "compute_churn_scores must return DataFrame"
assert "churn_score" in result.columns, "Missing column: churn_score"
labeled = apply_risk_labels(result)
assert "risk_label" in labeled.columns, "Missing column: risk_label"
print("Computation helpers: OK")
EOF
```

**Pass criterion:** Prints `Computation helpers: OK`.

## 5. Layer 3 — Module / UI Smoke Tests

### 5.1 Prerequisites

The app must be running before executing UI tests:

```bash
streamlit run app.py --server.headless true &
```

Wait for `You can now view your Streamlit app in your browser` in the terminal output before proceeding.

### 5.2 Manual smoke test checklist

Perform the following checks in the browser at `http://localhost:8501`:

| # | Action | Pass Criterion |
|---|---|---|
| 1 | Open the app | Page loads with sidebar and KPI header; no red error banner |
| 2 | Read KPI header | Three KPI cards visible with non-zero numeric values |
| 3 | Select "Smart Asset Monitoring" | Page renders project selector, charts (occupancy & energy), and tenant risk table without error |
| 4 | Change the project selector dropdown | Charts and table update to reflect the new project selection |
| 5 | Expand the "Model weights / thresholds" expander | Sliders render; adjusting a slider updates the churn scores table |
| 6 | Select "EBITDA Simulator" | Page renders input controls and output charts without error |
| 7 | Adjust EBITDA simulator inputs | Output values react in real time |
| 8 | Select "AI Document Intelligence" | Page renders document upload/query interface without error |
| 9 | Return to "Smart Asset Monitoring" | State resets correctly; no stale data from previous session |

Record each result as `PASS` or `FAIL — <description of actual behavior>`.

### 5.3 Regression test after edits

After any code change, run the full sequence:

1. Layer 1 (syntax + imports) — terminal
2. Layer 2 (data validation) — terminal
3. Layer 3 items 1–9 — browser

All three layers must pass before considering the change complete.

## 6. Defect Reporting Format

When a test fails, capture and report the following:

```
DEFECT REPORT
─────────────────────────────────────────────
Layer        : <1 | 2 | 3>
Test ID      : <e.g., Layer2-4.2 or Layer3-Step5>
Severity     : <Critical | High | Medium | Low>
File         : <path/to/file.py>
Line (if known): <line number>
Observed     : <exact error message or screenshot description>
Expected     : <what should have happened>
Reproduction : <minimal steps to reproduce>
Proposed Fix : <hypothesis or suggested code change>
─────────────────────────────────────────────
```

## 7. Testing Guardrails

* Never modify production data or constants in `data.py` solely to make a test pass. Fix the broken code instead.
* Layer 3 tests are manual and subjective — document the tester's name and timestamp for traceability.
* If `st.set_page_config()` is called more than once the app will crash on load; this is a Critical Layer 1 defect.
* A module's `render()` function must be callable without arguments (or with only optional arguments) for Layer 3 smoke tests to work.
* Do not run multiple `streamlit run` instances on the same port; kill existing processes first with `Ctrl+C` or `taskkill /F /IM streamlit.exe` (Windows).
