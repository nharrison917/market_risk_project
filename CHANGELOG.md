# Changelog

All notable changes to this project are documented here.

---

## Phase Two — Streamlit Dashboard (2026-04-02)

### Added

- **`app.py`** — Streamlit dashboard deployed to
  [Streamlit Community Cloud](https://marketriskproject-7tn7cdfwyuyhbuquj2y6kh.streamlit.app/).
  Two-tab layout: Executive Summary and Deep Dive.

- **Regime-sliced performance analysis** — portfolio metrics split by sustained correlation
  breakdown episodes (60-day SPY-TLT correlation > 0.2 for >= 21 consecutive trading days).
  The 21-day threshold filters noise while capturing structurally meaningful episodes;
  6 episodes identified since 2006, totalling 310 trading days.

- **Drawdown chart shading** — sustained breakdown episodes highlighted with amber vrects,
  visible on both light and dark themes.

- **Sharpe ratio** — added to `risk/performance.py` using a fixed 2% risk-free rate
  (long-run average). Rate is displayed explicitly in the UI.

- **8 pre-computed CSV outputs** committed to `outputs/` for dashboard use:
  `current_regime.csv`, `drawdown_timeseries.csv`, `correlation_modern.csv`,
  `correlation_historical.csv`, `portfolio_returns.csv`, `performance_summary.csv`,
  `tail_risk_summary.csv`, `historical_regime_summary.csv`.

- **`FUTURE_DIRECTIONS.md`** — documents the regime detection timing problem and potential
  approaches (HMM, Kalman filter, cost-of-being-wrong analysis).

### Changed

- **`data/fred_ingestion.py`** — replaced `pandas-datareader` CSV scraping with `fredapi`
  and a key-based approach (`FRED_API_KEY` environment variable via `python-dotenv`).
  The old endpoint (`fredgraph.csv`) was unreliable and timed out repeatedly.

- **`analysis_notes.py`** — `decade_structure_analysis` and `real_yield_shock_analysis`
  now return DataFrames for dashboard consumption while preserving CLI print behavior
  via `if __name__ == "__main__"`.

- **`main.py`** — added 8 CSV output steps; reordered so ETF-era outputs are written before
  the FRED/Shiller historical fetch (which is the slower, failure-prone step).

- **`requirements.txt`** — added `streamlit>=1.35.0`, `fredapi>=0.5.0`,
  `python-dotenv>=1.0.0`.

- **`.gitignore`** — changed `outputs/` blanket exclusion to `outputs/*` +
  `!outputs/*.csv`; figures and SQLite DB remain excluded.

### Architectural decisions

- **Committed CSV snapshot (not live fetch):** The dashboard reads from pre-computed CSVs
  rather than calling yfinance/FRED at runtime. This gives instant cold starts on Streamlit
  Community Cloud and removes external API calls as a runtime dependency. A live refresh
  button is a natural future addition but was out of scope here.

- **Figures built inline from CSVs:** The existing `visuals/plots.py` functions write HTML
  files but return nothing. Rather than refactor them, `app.py` builds all Plotly figures
  directly from the CSV data. This avoids sizing and theme issues with loading static HTML
  into Streamlit.

- **Streamlit Community Cloud deployment:** Free tier, public repo, `FRED_API_KEY` injected
  via Streamlit Secrets UI. `load_dotenv()` is a no-op when the variable is already in the
  environment, so the same code path works locally and in production.

### Known limitations

- Shiller monthly data (used for the 1962-present historical correlation chart and decade
  breakdown table) is updated with a lag at Yale's source. Current coverage ends
  September 2023. The ETF-era data (yfinance) is current to the most recent pipeline run.

- Regime detection is retrospective. The dashboard identifies breakdown episodes in hindsight;
  real-time detection involves meaningful lag and false-positive tradeoffs.
  See `FUTURE_DIRECTIONS.md`.

---

## Phase One — Analysis Pipeline (initial release)

### Added

- Pipeline for regime-dependent stock-bond diversification analysis combining modern ETF
  data (2006-present via yfinance) with 60+ years of macro history (1962-present via
  Shiller + FRED).
- Tri-axis regime classification: volatility (LOW/NORMAL/HIGH), correlation
  (DIVERSIFYING/NEUTRAL/BREAKDOWN), drawdown (NORMAL/CORRECTION/STRESS).
- Portfolio comparison: SPY, 60/40 (SPY+TLT), 60/30/10 (SPY+TLT+DBC).
- Tail risk analysis: historical VaR and CVaR at 5th percentile, split across
  Full Sample / Pre-2022 / Post-2022.
- Interactive Plotly charts saved to `outputs/figures/`.
- SQLite price cache (`data_store.db`) for offline reruns.
- `analysis_notes.py`: exploratory decade-level correlation structure and real yield shock
  comparison (1970s vs 2020s).
