import logging
import pandas as pd
from data.ingestion import fetch_history
from data.store import init_db, write_prices
from risk.metrics import compute_risk_metrics, classify_regimes, compute_portfolio, compute_portfolio_3asset
from pathlib import Path
from datetime import datetime
from visuals.plots import plot_rolling_correlation_modern, plot_drawdowns, plot_historical_correlation
from risk.tail_risk import compute_tail_comparison
from risk.performance import compute_performance_summary
from research.historical_regime_analysis import (
    build_historical_dataset,
    compute_historical_regime_summary
)

def setup_logging(log_level=logging.INFO):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"risk_{timestamp}.log"

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear existing handlers (important when rerunning in VS Code)
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler (detailed logging)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Console handler (quiet)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def main():

    REFRESH_DATA = False
    Path("outputs").mkdir(exist_ok=True)
    setup_logging(log_level=logging.INFO)
    print("setup_logging executed")

    logging.info("Starting multi-asset risk pipeline")

    tickers = ["SPY", "TLT", "DBC"]

    if REFRESH_DATA:
        frames = []
        for t in tickers:
            df_t = fetch_history(t)
            frames.append(df_t)

        df = pd.concat(frames)
        init_db()
        write_prices(df)
    else:
        from data.store import load_prices_from_db
        df = load_prices_from_db()

    logging.info(f"Data range: {df['date'].min()} -> {df['date'].max()}")

    # Risk metrics
    df, rolling_corr = compute_risk_metrics(df)
    spy_regimes = classify_regimes(df, rolling_corr)

    # Portfolios
    portfolio_df = compute_portfolio(df)
    portfolio_3 = compute_portfolio_3asset(df)

    # Build master dataframe
    master_df = spy_regimes.join(
        portfolio_df[["SPY", "TLT", "portfolio_60_40", "portfolio_drawdown"]],
        how="inner"
    )

    master_df = master_df.join(
        portfolio_3[["DBC", "portfolio_60_30_10", "drawdown"]]
        .rename(columns={"drawdown": "portfolio_60_30_10_drawdown"}),
        how="inner"
    )

    master_df = master_df.rename(columns={
        "SPY": "spy_return",
        "TLT": "tlt_return"
    })

    # Generate charts
    plot_rolling_correlation_modern(master_df)
    plot_drawdowns(master_df)

    # Tail summary saved silently
    tail_results = compute_tail_comparison(master_df)
    tail_results.to_csv("outputs/tail_risk_summary.csv")

    performance_summary = compute_performance_summary(master_df)
    performance_summary.to_csv("outputs/performance_summary.csv")

    # --- Timeseries CSVs for dashboard (written before historical fetch) ---

    # Current regime snapshot (last valid row)
    last_row = spy_regimes.dropna(subset=["regime"]).iloc[[-1]].copy()
    regime_parts = last_row["regime"].iloc[0].split(" | ")
    last_row["vol_regime"] = regime_parts[0]
    last_row["corr_regime"] = regime_parts[1]
    last_row["dd_regime"] = regime_parts[2]
    last_row.index.name = "date"
    last_row[["vol_regime", "corr_regime", "dd_regime",
              "rolling_vol_30", "corr", "drawdown", "regime"]].to_csv("outputs/current_regime.csv")

    # Drawdown timeseries
    master_df[["drawdown", "portfolio_drawdown", "portfolio_60_30_10_drawdown"]].to_csv(
        "outputs/drawdown_timeseries.csv"
    )

    # Modern rolling correlation timeseries
    master_df[["corr"]].rename(columns={"corr": "rolling_corr_60d"}).to_csv(
        "outputs/correlation_modern.csv"
    )

    # Daily portfolio returns (for regime-sliced performance analysis)
    master_df[["daily_return", "portfolio_60_40", "portfolio_60_30_10"]].rename(columns={
        "daily_return": "spy",
        "portfolio_60_40": "port_60_40",
        "portfolio_60_30_10": "port_60_30_10",
    }).to_csv("outputs/portfolio_returns.csv")

    historical_df = build_historical_dataset()
    plot_historical_correlation(historical_df)

    historical_summary = compute_historical_regime_summary(historical_df)
    historical_summary.to_csv("outputs/historical_regime_summary.csv")

    # Historical rolling correlation timeseries
    historical_df[["rolling_corr_36m"]].to_csv("outputs/correlation_historical.csv")

    logging.info("Charts and summaries generated successfully.")

if __name__ == "__main__":
    main()