# Phase Two: Business Recommendation Dashboard

## Goal

Build a two-section Streamlit dashboard that tells a coherent investment story:
"60/40 diversification is regime-dependent — the 2000–2020 negative correlation was the anomaly.
A modest commodity allocation improves resilience under inflation stress at low long-run cost."

Target audience: both technical (quant/risk) and generalist (PM/strategy) hiring managers.
Deployment target: Streamlit Community Cloud (public repo, free tier).

---

## Architecture Decisions

### Data layer: committed snapshot (Option B)

The dashboard reads from pre-computed CSVs already in `outputs/`. No live API calls on load.
This gives instant cold starts and removes yfinance/FRED as runtime dependencies.

The `analysis_notes.py` exploratory results (decade breakdown, real yield shocks) are currently
print-only. They need to be refactored to return DataFrames so the dashboard can consume them.

An optional "Refresh Data" button is out of scope for the initial build but is a natural
future addition (would call `main.py` pipeline and regenerate CSVs).

### Sharpe ratio

Sharpe = (annualized return - risk-free rate) / annualized vol.
Use a fixed risk-free rate assumption of 2.0% (roughly the long-run average Fed funds rate
over the analysis period — display the assumption explicitly in the UI so it's transparent).
The inputs (annualized return, annualized vol) already exist in `performance_summary.csv`.
Add computation to `risk/performance.py` and regenerate the CSV before building the dashboard.

### No new data fetching

Do not add any new API dependencies to the dashboard entry point. All data comes from CSVs.

---

## Files to Create or Modify

### New files

| File | Purpose |
|---|---|
| `app.py` | Streamlit entry point — all dashboard layout and rendering logic lives here |

### Files to modify

| File | Change |
|---|---|
| `risk/performance.py` | Add Sharpe ratio (with configurable risk-free rate) to the performance summary output |
| `analysis_notes.py` | Refactor decade breakdown and real yield shock sections to return DataFrames instead of printing. Keep a `if __name__ == "__main__"` block that prints them for CLI use. |
| `requirements.txt` | Add `streamlit` |
| `main.py` | Re-run after performance.py changes to regenerate `outputs/performance_summary.csv` |

### Do not modify

`risk/metrics.py`, `risk/tail_risk.py`, `visuals/plots.py`, all data ingestion modules.
These are working and tested — the dashboard reads their outputs, not their internals.

---

## Dashboard Layout Spec

Entry point: `app.py`
Layout: `st.tabs(["Executive Summary", "Deep Dive"])`

---

### Tab 1: Executive Summary

**Header**
- Title: "Portfolio Regime Analysis: Is 60/40 Still Enough?"
- One-sentence subtitle framing the thesis

**Current Regime Snapshot** (`st.columns(3)`)
- Three `st.metric` cards reading the most recent row of the regime-labeled data:
  - Volatility Regime (LOW_VOL / NORMAL_VOL / HIGH_VOL)
  - Correlation Regime (DIVERSIFYING / NEUTRAL / BREAKDOWN)
  - Drawdown Regime (NORMAL / CORRECTION / STRESS)
- Color-coded via `st.metric` delta styling (green = benign, red = stress)
- Source: read the last row of the computed regime timeseries
  (requires exposing this from `risk/metrics.py` as a CSV — see implementation note below)

**Key Metrics Table** (`st.dataframe` or `st.table`)
- Rows: SPY | 60/40 | 60/30/10
- Columns: Annualized Return | Annualized Vol | Max Drawdown | Sharpe Ratio
- Source: `outputs/performance_summary.csv` (after Sharpe is added)

**Recommendation Callout** (`st.info` or `st.success`)
- Plain-English 2–3 sentence box:
  "The 60/30/10 portfolio modestly underperforms 60/40 over the full sample but provides
  meaningfully better drawdown protection during inflation-driven stress regimes.
  Post-2022, 60/40 tail risk worsened. The cost of the commodity hedge is low; the benefit
  is asymmetric to the downside."

**Drawdown Comparison Chart**
- `st.plotly_chart(fig, use_container_width=True)`
- Load from `outputs/figures/drawdown_comparison_3asset.html` or regenerate inline
- Preferred: regenerate inline by calling the figure-building function from `visuals/plots.py`
  so it renders cleanly in Streamlit's theme rather than loading a static HTML file

---

### Tab 2: Deep Dive

This tab is for viewers who want to understand the mechanics behind the recommendation.
Mix of charts and tables is intentional.

**Section: The Long View — 60+ Years of Stock-Bond Correlation**
- `st.plotly_chart`: historical 36-month rolling correlation chart (1962–present)
- Source: figure from `visuals/plots.py` / `outputs/figures/historical_correlation_36m.html`
- Brief `st.caption` explaining what the chart shows and where the pre/post-2000 break is

**Section: Decade Breakdown** (`st.dataframe`)
- Table: decade | avg 36m correlation | share of positive-correlation months
- Source: refactored output from `analysis_notes.py`
- This contextualizes the long-run chart with a scannable summary

**Section: How Bad Did It Get? — Tail Risk by Era**
- `st.dataframe`: 5% VaR and CVaR for SPY / 60/40 / 60/30/10, split across Full / Pre-2022 / Post-2022
- Source: `outputs/tail_risk_summary.csv`
- Add a `st.caption` noting that post-2022 represents the inflation shock regime

**Section: Regime Transitions — Real Yield Shocks**
- `st.dataframe` or small bar chart: real yield shock analysis from `analysis_notes.py`
  (12-month change in real yield, compared across eras)
- Keep this concise — a table is fine here
- Brief explanatory text: why real yield shocks matter for stock-bond correlation

**Section: Modern Correlation (2006–Present)**
- `st.plotly_chart`: rolling 60-day SPY-TLT correlation
- Source: `outputs/figures/rolling_correlation_modern.html` or regenerated inline
- This ties the long-run historical view back to the ETF-era data

---

## Implementation Note: Regime Snapshot CSV

The current regime labels are computed in `risk/metrics.py` but only held in memory during
pipeline runs — they are not written to `outputs/`. To support the Tab 1 regime snapshot cards,
add one output file to `main.py`:

```
outputs/current_regime.csv
```

Single-row CSV containing: date, vol_regime, correlation_regime, drawdown_regime, spy_drawdown,
rolling_vol, rolling_corr. Written as the last step of `main.py` after regime labeling.
Commit this file alongside the other CSVs.

---

## Deployment Checklist (Streamlit Community Cloud)

1. Confirm repo is public on GitHub
2. `requirements.txt` includes `streamlit`, `plotly`, `pandas`, `yfinance`, `pandas-datareader`
3. All output CSVs committed to repo (verify `.gitignore` does not exclude `outputs/*.csv`)
4. `app.py` at repo root (Community Cloud expects entry point at root by default)
5. Create free account at streamlit.io, link GitHub
6. "New app" → select repo → select branch `main` → entry point `app.py`
7. No secrets required for this build (all data from committed files)

---

## Build Order

1. Modify `risk/performance.py` — add Sharpe ratio
2. Re-run `main.py` — regenerate `outputs/performance_summary.csv`
3. Modify `main.py` — add `current_regime.csv` output step
4. Refactor `analysis_notes.py` — return DataFrames from decade breakdown and real yield shock sections
5. Add `streamlit` to `requirements.txt`
6. Build `app.py` — Tab 1 first (Executive Summary), then Tab 2 (Deep Dive)
7. Test locally with `streamlit run app.py`
8. Commit outputs and push; deploy to Community Cloud

---

## Out of Scope (Future)

- Live data refresh button (would require yfinance/FRED at runtime)
- Streamlit secrets / API key management
- Custom CSS theming beyond Streamlit defaults
- Multi-page app structure (tabs are sufficient at current scope)
- Backtesting interface or portfolio optimizer
