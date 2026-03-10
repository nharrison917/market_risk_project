import pandas as pd
import numpy as np


def compute_risk_metrics(df):
    df = df.sort_values(["ticker", "date"]).copy()

    # Daily returns per ticker
    df["daily_return"] = df.groupby("ticker")["adj_close"].pct_change()

    # Rolling volatility per ticker
    df["rolling_vol_30"] = (
        df.groupby("ticker")["daily_return"]
        .rolling(30)
        .std()
        .reset_index(level=0, drop=True)
        * np.sqrt(252)
    )

    # Cumulative return per ticker
    df["cumulative_return"] = (
        df.groupby("ticker")["daily_return"]
        .apply(lambda x: (1 + x).cumprod())
        .reset_index(level=0, drop=True)
    )

    # Rolling max per ticker
    df["rolling_max"] = df.groupby("ticker")["cumulative_return"].cummax()

    # Drawdown per ticker
    df["drawdown"] = df["cumulative_return"] / df["rolling_max"] - 1

    # Pivot returns for correlation
    returns = df.pivot(index="date", columns="ticker", values="daily_return")

    rolling_corr = returns["SPY"].rolling(60).corr(returns["TLT"])

    return df, rolling_corr


def classify_regimes(df, rolling_corr):
    df = df.copy()

    # Filter SPY only
    spy_df = df[df["ticker"] == "SPY"].copy()
    spy_df = spy_df.set_index("date")

    # Align correlation
    spy_df["corr"] = rolling_corr

    vol_high = spy_df["rolling_vol_30"].quantile(0.8)
    vol_low = spy_df["rolling_vol_30"].quantile(0.4)

    def label_row(row):
        vol = row["rolling_vol_30"]
        corr = row["corr"]
        drawdown = row["drawdown"]

        if pd.isna(vol) or pd.isna(corr):
            return None

        # Vol regime
        if vol >= vol_high:
            vol_regime = "HIGH_VOL"
        elif vol <= vol_low:
            vol_regime = "LOW_VOL"
        else:
            vol_regime = "NORMAL_VOL"

        # Correlation regime
        if corr > 0.2:
            corr_regime = "BREAKDOWN"
        elif corr < -0.2:
            corr_regime = "DIVERSIFYING"
        else:
            corr_regime = "NEUTRAL"

        # Drawdown regime
        if drawdown <= -0.10:
            dd_regime = "STRESS"
        elif drawdown <= -0.05:
            dd_regime = "CORRECTION"
        else:
            dd_regime = "NORMAL"

        return f"{vol_regime} | {corr_regime} | {dd_regime}"

    spy_df["regime"] = spy_df.apply(label_row, axis=1)

    return spy_df


def compute_portfolio(df):
    df = df.sort_values(["date", "ticker"]).copy()

    # Pivot returns
    returns = df.pivot(index="date", columns="ticker", values="daily_return")

    # Drop rows with NaN
    returns = returns.dropna()

    # 60/40 portfolio
    returns["portfolio_60_40"] = 0.6 * returns["SPY"] + 0.4 * returns["TLT"]

    # Portfolio cumulative return
    returns["portfolio_cum"] = (1 + returns["portfolio_60_40"]).cumprod()

    # Portfolio rolling vol
    returns["portfolio_vol_30"] = (
        returns["portfolio_60_40"]
        .rolling(30)
        .std()
        * (252 ** 0.5)
    )

    # Portfolio drawdown
    rolling_max = returns["portfolio_cum"].cummax()
    returns["portfolio_drawdown"] = returns["portfolio_cum"] / rolling_max - 1

    return returns

def compute_portfolio_3asset(df):
    df = df.sort_values(["date", "ticker"]).copy()

    returns = df.pivot(index="date", columns="ticker", values="daily_return")
    returns = returns.dropna()

    returns["portfolio_60_30_10"] = (
        0.6 * returns["SPY"] +
        0.3 * returns["TLT"] +
        0.1 * returns["DBC"]
    )

    returns["cum"] = (1 + returns["portfolio_60_30_10"]).cumprod()

    returns["vol_30"] = (
        returns["portfolio_60_30_10"]
        .rolling(30)
        .std()
        * (252 ** 0.5)
    )

    rolling_max = returns["cum"].cummax()
    returns["drawdown"] = returns["cum"] / rolling_max - 1



    return returns