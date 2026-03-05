# Tidhar Decision Intelligence Portal — Developer Notes

> **Audience:** developers maintaining or extending this project.  
> **Stack:** Python · Streamlit ≥ 1.30 · Plotly ≥ 5.18 · Pandas ≥ 2.0  
> **Run:** `streamlit run app.py`

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Architecture Overview](#2-architecture-overview)
3. [Data Layer — `data.py`](#3-data-layer--datapy)
4. [Style System — `style.py`](#4-style-system--stylepy)
5. [Modules](#5-modules)
6. [AI Agent — Alerts & Dialog](#6-ai-agent--alerts--dialog)
7. [Floating FAB Button](#7-floating-fab-button)
8. [Streamlit Gotchas — Critical Rules](#8-streamlit-gotchas--critical-rules)
9. [CSS Gotchas — Critical Rules](#9-css-gotchas--critical-rules)
10. [Bugs Fixed & Why They Failed](#10-bugs-fixed--why-they-failed)
11. [Adding New Features — Checklist](#11-adding-new-features--checklist)

---

## 1. Project Structure

```
app.py                        # Entrypoint: config, sidebar, KPIs, router, FAB
data.py                       # Single source of truth for all data + KPIs
style.py                      # Global CSS injection + reusable UI helper functions
requirements.txt              # streamlit, pandas, plotly, numpy
modules/
  __init__.py
  ai_agent.py                 # Insight engine + dialog renderer
  asset_monitoring.py         # Smart Asset Monitoring page
  ebitda_simulator.py         # EBITDA Simulator page
  doc_intelligence.py         # AI Document Intelligence page
```

---

## 2. Architecture Overview

```
app.py
 ├── st.set_page_config()          ← MUST be the very first Streamlit call
 ├── inject_css()                  ← injects all global CSS via st.markdown
 ├── @st.dialog show_ai_agent()    ← dialog definition (must be defined BEFORE any call to it)
 ├── with st.sidebar               ← navigation radio + AI Insights sidebar button
 ├── KPI row                       ← kpi_card() calls
 ├── nav_to handler                ← pops session_state["nav_to"] → overrides page
 ├── Page Router                   ← if/elif on page value → module.render()
 └── Floating FAB                  ← native st.button + components.v1.html for positioning
```

### Key Streamlit lifecycle rules

- `st.set_page_config()` must be the **very first** Streamlit call in the file — nothing can come before it.
- `@st.dialog` decorated functions must be **defined before** they are called anywhere. Define at top of `app.py`.
- Every user interaction triggers a **full top-to-bottom script re-run**. Do not rely on in-memory state between runs — use `st.session_state`.
- `st.session_state` persists across reruns within the same browser session. Use it for cross-run state (e.g., navigation targets, dialog flags).

---

## 3. Data Layer — `data.py`

All data is hardcoded in `data.py`. This is the **single source of truth** — never put raw numbers in modules.

### Key exports

| Name | Type | Description |
|---|---|---|
| `REF_DATE` | `date` | Reference date for all expiry calculations (currently `2026-03-01`) |
| `df_projects` | DataFrame | Project-level: occupancy, energy, revenue |
| `df_tenants` | DataFrame | Tenant-level: churn risk, lease expiry, sector, rent |
| `df_occupancy_trend` | DataFrame | 12-month occupancy history per project |
| `df_energy_trend` | DataFrame | 12-month energy consumption history |
| `TOTAL_PORTFOLIO_VALUE` | str | Formatted string KPI |
| `ENERGY_SAVINGS_OPP` | str | Formatted string KPI |
| `TENANTS_AT_RISK` | int | Count of tenants with churn risk ≥ 0.60 |
| `compute_churn_scores()` | function | Recalculates churn scores with given weights |
| `apply_risk_labels()` | function | Applies Low/Medium/High labels to a scored DataFrame |
| `df_cpor_monthly` | DataFrame | 12-month CPOR series: `Month`, `CPOR (₪)` |
| `df_epor_project` | DataFrame | EPOR per project: `Project`, `EPOR (kWh)`, `Occupied Rooms`, `Energy (kWh)` |
| `EPOR_BENCHMARK` | float | 150.0 kWh — target benchmark for energy per occupied room |

### Churn score model

Churn risk is a weighted sum of four factors:

```
churn = w_expiry * expiry_score + w_activity * (1 - activity_score)
      + w_sector * sector_base_risk + w_rent * rent_pressure_score
```

Weights are user-adjustable in the Asset Monitoring module via an expander UI. Default weights are exported as `DEFAULT_W_EXPIRY`, `DEFAULT_W_ACTIVITY`, `DEFAULT_W_SECTOR`, `DEFAULT_W_RENT`.

### Alert thresholds (adjustable constants)

```python
ENERGY_COST_PER_KWH = 0.55    # ₪/kWh
ENERGY_WASTE_FACTOR = 0.40    # fraction wasted in low-occupancy buildings
OCC_ALERT_THRESHOLD = 50      # % occupancy — below this fires energy inefficiency alert
NRG_ALERT_THRESHOLD = 0.80    # fraction of peak energy — alert threshold
```

---

## 4. Style System — `style.py`

### Color palette

```python
NAVY    = "#003366"   # sidebar background
GREY    = "#B0BEC5"
ACCENT  = "#00CC99"   # teal — primary brand color, borders, highlights
BG_DARK = "#0E1117"   # main page background
CARD_BG = "#1A1F2B"   # card/panel backgrounds
TEXT    = "#E8E8E8"   # default body text
RED     = "#FF4B4B"   # critical alerts
YELLOW  = "#FFD93D"   # warnings
```

### Helper functions

| Function | Usage |
|---|---|
| `inject_css()` | Call once at top of `app.py`. Injects all global styles. |
| `kpi_card(label, value, delta, trend, trend_color)` | Renders a dark themed KPI metric card. `trend` = arrow text (e.g. `"▲ 2.1%"`), `trend_color` = hex color for the arrow (defaults to `ACCENT`). |
| `section_header(title)` | Renders a section heading with teal underline. |
| `alert_card(title, body)` | Renders a red-bordered alert card. |

### ⚠️ CSS rules — NEVER use a wildcard sidebar selector

```css
/* ❌ WRONG — forces white text on ALL elements including buttons */
section[data-testid="stSidebar"] * { color: #FFFFFF; }

/* ✅ CORRECT — target only what needs white text */
section[data-testid="stSidebar"] .stMarkdown p { color: #FFFFFF; }
section[data-testid="stSidebar"] .stButton > button {
    color: #FFFFFF !important;
    background-color: rgba(255,255,255,0.12) !important;
}
```

The wildcard `* { color: #FFFFFF }` makes button text white on Streamlit's default white/light button background — completely invisible. Always use specific selectors for sidebar elements.

---

## 5. Modules

Each module exports a single `render()` function called by the page router in `app.py`.

### `asset_monitoring.py`
- Shows project-level occupancy, energy, and churn dashboards
- User-adjustable churn model weights via `st.expander`
- Calls `compute_churn_scores()` and `apply_risk_labels()` from `data.py` with live weight values

### `ebitda_simulator.py`
- Interactive EBITDA scenario modeler
- Sliders for occupancy, rent, energy cost assumptions
- Renders Plotly waterfall / bar charts

### `analytics_dashboard.py`
- PowerBI-style KPI dashboard with 14 cards (7 Tier 1 + 7 Tier 2) and 8 chart panels
- **Phase 1 additions:** RevPAR Decomposition (dual-axis), GOPPAR vs CPOR Spread, EPOR by Project, Retention Intelligence (churn risk waterfall + expiry scatter + at-risk table)
- **KPI trend indicators:** ▲/▼ with MoM % change color-coded (green = positive, red = negative)
- **Replaced KPIs:** "Staff Available" → EPOR, "Tenant Retention" → ₪ Revenue at Risk
- Uses shared `_CHART_LAYOUT` dict for consistent Plotly styling across all charts

### `doc_intelligence.py`
- AI document analysis simulation
- Renders document cards with extracted insights

### `ai_agent.py`
- `generate_insights()` — runs 4 detection rules against live data, returns sorted list of insight dicts
- `get_alert_count()` — returns count of critical + warning insights (used for badges)
- `render_insights()` — renders full insight cards inside the dialog

#### Insight dict schema
```python
{
    "severity": "critical" | "warning" | "info",
    "icon":     str,          # emoji
    "title":    str,          # short headline
    "body":     str,          # HTML string — rendered with unsafe_allow_html
    "action":   str,          # button label
    "module":   str,          # must match exactly one of the st.radio options in app.py
}
```

#### Detection rules
| Rule | Condition | Severity |
|---|---|---|
| 1 | Churn Risk ≥ 0.60 | critical |
| 2 | Occupancy < 50% (energy waste) | warning |
| 3 | Lease expiry within 180 days (non-critical tenants) | warning |
| 4 | Occupancy decline ≥ 8 pp over 12 months | info |

#### Navigation from dialog
When an action button is clicked inside the dialog:
```python
st.session_state["nav_to"] = insight["module"]
st.rerun()
```
Back in `app.py`, before the page router:
```python
if "nav_to" in st.session_state:
    page = st.session_state.pop("nav_to")
```
The `module` string in the insight dict must **exactly match** one of the `st.radio` option strings.

---

## 6. AI Agent — Alerts & Dialog

The AI Agent dialog is defined with `@st.dialog` at the top of `app.py`:

```python
@st.dialog("🤖 AI Agent — Portfolio Insights", width="large")
def show_ai_agent():
    ai_agent.render_insights()
```

It can be opened from two places:
1. **Sidebar button** — `st.button("🤖  AI Insights", key="ai_sidebar_btn")`; calls `show_ai_agent()` directly on click.
2. **Floating FAB button** — native `st.button` repositioned to `position:fixed` via `streamlit.components.v1.html` JavaScript (see section 7).

**Important:** `show_ai_agent()` must be called during the **current script run** for the dialog to appear. It cannot be scheduled for a future run via session state alone without additional `st.rerun()` calls.

---

## 7. Floating FAB Button

The FAB is a **native `st.button`** (not an HTML `<button>`) repositioned to the bottom-right corner by JavaScript injected via `streamlit.components.v1.html`. This is the only reliable way to make a clickable floating element open a Streamlit dialog.

### How it works

```python
# 1. Render the preview bubble (fixed via CSS class ai-fab-preview in style.py)
st.markdown("<div class='ai-fab-preview'>...</div>", unsafe_allow_html=True)

# 2. Render the native Streamlit button
if st.button("🤖\u00a0 AI Insights", key="ai_fab_btn"):
    show_ai_agent()

# 3. Inject JS via components.v1.html (same-origin iframe — scripts execute here)
import streamlit.components.v1 as _components
_components.html("""<script>
(function() {
    function styleFab() {
        var doc = window.parent.document;
        var buttons = doc.querySelectorAll('[data-testid="stButton"] button');
        for (var i = 0; i < buttons.length; i++) {
            var btn = buttons[i];
            if (btn.textContent.includes('AI Insights') &&
                !btn.closest('[data-testid="stSidebar"]')) {
                var wrapper = btn.closest('[data-testid="stButton"]');
                wrapper.style.cssText = 'position:fixed;bottom:2.2rem;right:2.2rem;z-index:999999;width:auto;';
                btn.style.cssText = '...full gradient button styles...';
                break;
            }
        }
    }
    styleFab();
    setTimeout(styleFab, 150);
    setTimeout(styleFab, 600);
    var obs = new MutationObserver(styleFab);
    obs.observe(window.parent.document.body, {childList:true, subtree:true});
})();
</script>""", height=0)
```

The `MutationObserver` reapplies styles after every Streamlit rerender (which replaces DOM nodes).

### Why the button selector excludes the sidebar

Both `ai_sidebar_btn` and `ai_fab_btn` have "AI Insights" in their text. The JS filter `!btn.closest('[data-testid="stSidebar"]')` ensures only the main-area FAB button gets repositioned.

---

## 8. Streamlit Gotchas — Critical Rules

### `st.query_params.clear()` is a silent rerun

```python
# ❌ WRONG — .clear() halts the script immediately; the next line never runs
if st.query_params.get("open_ai") == "1":
    st.query_params.clear()
    show_ai_agent()          # ← NEVER REACHED

# ❌ ALSO WRONG — session state is set, but the dialog call on the same run is gone
if st.query_params.get("open_ai") == "1":
    st.query_params.clear()
    st.session_state["_open_ai_dialog"] = True   # ← NEVER REACHED
```

`st.query_params.clear()` (and `st.query_params[key] = value`) trigger an immediate script stop + rerun, similar to `st.rerun()`. Any code after these calls in the same `if` block does not execute.

**Rule:** Never call `st.query_params.clear()` before code you need to run in the same pass.

### `@st.dialog` must be defined before first call

The `@st.dialog` decorated function must be defined at the top of `app.py`, before the sidebar block or any other code that might call it. Streamlit registers the dialog context during definition.

### `element.click()` does not work on Streamlit buttons

Streamlit's frontend runs on React 18, which uses **event delegation**: all event listeners are registered on `document` root, not on individual DOM elements. Calling `element.click()` from JavaScript fires a native `MouseEvent` that bypasses React's synthetic event dispatcher — the Python callback never fires.

```javascript
// ❌ WRONG — React ignores programmatic .click()
document.querySelector('button').click();
```

**Rule:** Never use `element.click()` to trigger Streamlit button callbacks. Use native `st.button` with JavaScript that only repositions/styles it — the user's actual mouse click goes to React correctly.

### `<script>` tags in `st.markdown` are stripped

Streamlit passes HTML through **DOMPurify** before rendering. DOMPurify removes all `<script>` tags by design. Scripts injected via `st.markdown(..., unsafe_allow_html=True)` never execute in the browser.

```python
# ❌ WRONG — script tag is stripped before the browser sees it
st.markdown("<script>window.history.replaceState(...);</script>",
            unsafe_allow_html=True)
```

**Rule:** Use `streamlit.components.v1.html(...)` for JavaScript that must execute. This renders in a sandboxed same-origin iframe where scripts run normally. Access the parent page via `window.parent.document`.

### Python unicode escapes in JavaScript strings

Do not use JavaScript template literal unicode escapes (`\u{1F916}`) inside Python string literals — Python tries to decode them as Python unicode escapes (`\uXXXX` — 4 hex digits, no braces) and raises a `SyntaxError`.

```python
# ❌ SyntaxError — Python sees \u{1F916} and fails
_components.html("""<script>if (btn.textContent.startsWith('\u{1F916}')) {</script>""")

# ✅ Use the literal emoji character or \uD83E\uDD16 (surrogate pair) instead
_components.html("""<script>if (btn.textContent.includes('AI Insights')) {</script>""")
```

---

## 9. CSS Gotchas — Critical Rules

### Streamlit data-testid selectors (as of Streamlit ≥ 1.30)

| Element | Selector |
|---|---|
| Sidebar | `section[data-testid="stSidebar"]` |
| Any `st.button` wrapper | `[data-testid="stButton"]` |
| Button element | `[data-testid="stButton"] > button` or `.stButton > button` |
| Metric value | `[data-testid="stMetricValue"]` |
| DataFrame | `.stDataFrame` |

**Warning:** Streamlit may change `data-testid` values between versions. If styles stop working after a Streamlit upgrade, inspect the live DOM to find the new selectors.

### CSS `{{}}` double-braces in Python f-strings

All CSS injected via `inject_css()` uses Python f-strings for color interpolation. CSS uses `{}` for property values. Inside an f-string, literal `{` and `}` must be escaped as `{{` and `}}`.

```python
# ✅ Correct
st.markdown(f"""
<style>
    .kpi-card {{
        background: {CARD_BG};
        border-left: 4px solid {ACCENT};
    }}
</style>""", unsafe_allow_html=True)
```

---

## 10. Bugs Fixed & Why They Failed

### Bug 1 — Sidebar "AI Insights" button: white text on white background

**Symptom:** Button label invisible in sidebar.

**Root cause:** `style.py` had a catch-all rule:
```css
section[data-testid="stSidebar"] * { color: #FFFFFF; }
```
This forced white text on every sidebar element, including `<button>` whose Streamlit default background is white/light grey.

**Fix:** Remove the wildcard rule. Add a specific override for sidebar buttons:
```css
section[data-testid="stSidebar"] .stButton > button {
    color: #FFFFFF !important;
    background-color: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
}
```

---

### Bug 2 — Floating FAB button: clicking does nothing (3 failed attempts)

#### Attempt 1 — `querySelector + element.click()`
```javascript
// ❌ Programmatic .click() bypasses React's synthetic event system
sidebar.querySelectorAll('button')[i].click();
```
**Why it failed:** React 18 event delegation — native DOM `.click()` events are not dispatched through React's synthetic event handler. The Python button callback never fires.

#### Attempt 2 — `st.query_params.clear()` + `show_ai_agent()`
```python
# ❌ .clear() is a silent st.rerun(); show_ai_agent() never executes
if st.query_params.get("open_ai") == "1":
    st.query_params.clear()
    show_ai_agent()
```
**Why it failed:** `st.query_params.clear()` stops the current script run immediately and starts a new one. Everything after it in the same `if` block is unreachable.

#### Attempt 3 — `st.query_params.clear()` + session state flag
```python
# ❌ Same problem — session state assignment is also unreachable
if st.query_params.get("open_ai") == "1":
    st.query_params.clear()
    st.session_state["_open_ai_dialog"] = True   # never set
```
**Why it failed:** Same root cause as Attempt 2.

#### Attempt 4 — `st.markdown("<script>history.replaceState...</script>")`
```python
# ❌ Scripts stripped by DOMPurify before browser renders them
st.markdown("<script>window.history.replaceState(...);</script>",
            unsafe_allow_html=True)
```
**Why it failed:** Streamlit sanitizes all HTML through DOMPurify, which removes `<script>` tags.

#### ✅ Final Fix — native `st.button` + `components.v1.html` repositioning
- Use a real `st.button` (native Python callback, no React workaround needed).
- Use `streamlit.components.v1.html(script)` to inject JavaScript that repositions the button's DOM wrapper to `position:fixed`. This iframe is same-origin and JS executes.
- `MutationObserver` on `window.parent.document.body` reapplies the fixed positioning after every Streamlit rerender.

---

## 11. Adding New Features — Checklist

### Adding a new page/module
1. Create `modules/new_module.py` exporting `render()`
2. Add the page label to the `st.radio` options in `app.py`
3. Add an `elif "NewPage" in page:` branch in the page router
4. If the AI Agent should navigate to it, use the exact radio label string in the insight dict's `"module"` field

### Adding a new AI alert rule
1. Open `modules/ai_agent.py`, add a new block in `generate_insights()`
2. Return a dict with keys: `severity`, `icon`, `title`, `body`, `action`, `module`
3. `body` may contain HTML (`<b>`, `<span>`, etc.) — rendered with `unsafe_allow_html=True`
4. `module` must exactly match a `st.radio` option string in `app.py`
5. `severity` must be `"critical"`, `"warning"`, or `"info"` — controls sort order and badge count

### Adding new CSS styles
1. Add rules inside `inject_css()` in `style.py`
2. Remember double-braces `{{` / `}}` for literal CSS curly braces inside f-strings
3. Use `data-testid` selectors for Streamlit-generated elements
4. Never use sidebar wildcard `section[data-testid="stSidebar"] *` — it breaks button text visibility
5. Test both light and dark themes if applicable

### Running a JavaScript action from Python
- **`st.markdown` scripts are always stripped.** Never use this for JS.
- Use `streamlit.components.v1.html("<script>...</script>", height=0)` instead.
- Access the main Streamlit document from the component iframe via `window.parent.document`.
- For security, the component must be same-origin (localhost during dev, same domain in production).

---

### Bug 3 — Plotly chart legends: invisible text (dark on dark)

**Symptom:** Legend labels in Analytics Dashboard charts were the same color as the dark background — completely invisible.

**Root cause:** Plotly's `plotly_dark` template sets a default legend font color that blends into the custom `paper_bgcolor=CARD_BG` (`#1A1F2B`). The shared `_CHART_LAYOUT` dict defined `font=dict(color="#E8E8E8")` for **axis/title** text, but the `legend` sub-dict did **not** inherit this color — it used Plotly's template default, which was near-black.

```python
# ❌ WRONG — legend font color not explicitly set, inherits dark template default
_CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=CARD_BG,
    font=dict(color="#E8E8E8", size=11),
    legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10, orientation="h", y=1.12),
)
```

**Fix:** Always set `font_color` explicitly in the legend dict:

```python
# ✅ CORRECT — legend text is explicitly light-colored
_CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=CARD_BG,
    font=dict(color="#E8E8E8", size=11),
    legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10, font_color="#E8E8E8", orientation="h", y=1.12),
)
```

**Rule:** When using a custom `paper_bgcolor` with Plotly dark templates, **always set explicit `font_color` on legends, axis titles, and tick labels**. Plotly's template defaults assume the standard template background and may not contrast with custom backgrounds.

---

*Last updated: March 2026 — Deeply × Tidhar Strategic Portal v1*
