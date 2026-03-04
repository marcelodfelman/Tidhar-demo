---
name: dev-execution
description: This skill should be used when a developer needs to run, launch, build, or iteratively develop the Tidhar Decision Intelligence Streamlit application. It covers environment setup, dependency management, app startup, hot-reloading, module editing, and structured code changes across the project.
---

# Skill: Developer Execution

## 1. Purpose

Provide a complete, opinionated workflow for executing and iterating on the Tidhar Decision Intelligence Portal — a Streamlit application composed of `app.py`, `data.py`, `style.py`, and feature modules under `modules/`. Use this skill for any task that involves running, modifying, or deploying the application.

## 2. Project Structure Reference

```
app.py              — Streamlit entrypoint; page config, sidebar nav, module routing
data.py             — All data constants, DataFrames, and computation helpers
style.py            — Global CSS injection, KPI card renderer, color tokens
requirements.txt    — Python package dependencies
modules/
  __init__.py
  asset_monitoring.py   — Page: Smart Asset Monitoring (energy & churn)
  ebitda_simulator.py   — Page: EBITDA Simulator
  doc_intelligence.py   — Page: AI Document Intelligence
```

Each module exposes a `render()` function called by `app.py` based on the active sidebar selection.

## 3. Environment Setup

### 3.1 Install dependencies

```bash
pip install -r requirements.txt
```

Verify installed versions match the minimums in `requirements.txt` (`streamlit>=1.30`, `pandas>=2.0`, `plotly>=5.18`, `numpy>=1.24`). If version conflicts arise, use a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

### 3.2 Verify environment

```bash
streamlit --version
python -c "import pandas, plotly, numpy; print('OK')"
```

Expected: no import errors; Streamlit version ≥ 1.30.

## 4. Running the Application

### 4.1 Standard launch

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` by default. Hot-reload is active — saved file changes reflect immediately without restarting.

### 4.2 Custom port

```bash
streamlit run app.py --server.port 8502
```

### 4.3 Headless mode (CI / remote)

```bash
streamlit run app.py --server.headless true
```

## 5. Development Workflow

### 5.1 Adding or editing a module

1. Edit the target file in `modules/` (e.g., `modules/asset_monitoring.py`).
2. All business logic goes inside the `render()` function; do not add top-level Streamlit calls.
3. If new data constants or DataFrames are required, add them to `data.py` first.
4. If new CSS tokens or card components are required, add them to `style.py`.
5. Import new helpers in `app.py` only if a new routing branch is needed.

### 5.2 Adding a new module page

1. Create `modules/<module_name>.py` with a `render()` function.
2. Add `from modules import <module_name>` to `app.py`.
3. Add the page label to the `st.radio()` options list in `app.py`.
4. Add the routing branch to the `if/elif` block at the bottom of `app.py`.
5. Register any new data symbols in `data.py` and re-export them in `modules/__init__.py` if needed.

### 5.3 Editing global styles

All color tokens (`NAVY`, `ACCENT`, `RED`, `YELLOW`, `GREY`, `CARD_BG`, `TEXT`) are defined in `style.py`. Import them from there — never hardcode hex values in module files.

### 5.4 Editing data constants

All KPI constants (`TOTAL_PORTFOLIO_VALUE`, `ENERGY_SAVINGS_OPP`, `TENANTS_AT_RISK`) and DataFrame factories are in `data.py`. When a module needs fresh data, modify the source in `data.py` and re-import; do not replicate data logic inside module files.

## 6. Common Execution Tasks & Commands

| Task | Command |
|---|---|
| Launch app | `streamlit run app.py` |
| Install/update deps | `pip install -r requirements.txt` |
| Check for import errors | `python -c "import app"` |
| Freeze current deps | `pip freeze > requirements.txt` |
| Clear Streamlit cache | Delete `.streamlit/` folder or use `st.cache_data.clear()` at runtime |
| Lint code | `python -m py_compile app.py data.py style.py modules/*.py` |

## 7. Execution Guardrails

* Always keep `st.set_page_config()` as the very first Streamlit call in `app.py`. Moving it will raise a Streamlit runtime error.
* Do not call `st.*` functions at module import time (outside `render()`). This breaks Streamlit's execution model.
* When modifying `data.py`, verify that all importing modules (`app.py`, `modules/*.py`) destructure only symbols that still exist after the edit.
* If adding a `pip` dependency, add it to `requirements.txt` with a minimum version pin (`>=`) before committing.

## 8. Stopping the Application

Press `Ctrl+C` in the terminal where `streamlit run` is active. No cleanup steps are required.
