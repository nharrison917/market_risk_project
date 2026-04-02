import pandas as pd
import numpy as np

RISK_FREE_RATE = 0.02  # Long-run average; displayed explicitly in dashboard


def compute_performance_summary(master_df):

    def summarize(series):
        total_return = (1 + series).prod() - 1
        ann_return = (1 + total_return) ** (252 / len(series)) - 1
        ann_vol = series.std() * (252 ** 0.5)
        max_dd = (series.add(1).cumprod() /
                  series.add(1).cumprod().cummax() - 1).min()

        sharpe = (ann_return - RISK_FREE_RATE) / ann_vol
        return ann_return, ann_vol, max_dd, sharpe

    results = {}

    portfolios = {
        "SPY": master_df["daily_return"],
        "60_40": master_df["portfolio_60_40"],
        "60_30_10": master_df["portfolio_60_30_10"]
    }

    for name, series in portfolios.items():
        ann_return, ann_vol, max_dd, sharpe = summarize(series)

        results[name] = {
            "Annual_Return": ann_return,
            "Annual_Volatility": ann_vol,
            "Max_Drawdown": max_dd,
            "Sharpe_Ratio": sharpe
        }

    return pd.DataFrame(results).T