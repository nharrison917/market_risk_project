import numpy as np
import pandas as pd
from data.fred_ingestion import fetch_fred_series
from data.shiller_ingestion import fetch_shiller_data


def build_historical_dataset():

    sp500 = fetch_shiller_data()
    dgs10 = fetch_fred_series("DGS10").rename(columns={"DGS10": "yield_10y"})
    cpi = fetch_fred_series("CPIAUCSL").rename(columns={"CPIAUCSL": "cpi"})


    # Convert all to monthly (month-end frequency)
    dgs10 = dgs10.resample("ME").last()
    cpi = cpi.resample("ME").last()

    # Join after frequency alignment
    df = sp500.join(dgs10, how="inner")
    df = df.join(cpi, how="inner")

    # Compute returns
    df["equity_return"] = df["sp500"].pct_change(fill_method=None)

    df["yield_change"] = df["yield_10y"].diff() / 100
    duration = 8
    df["bond_return"] = -duration * df["yield_change"]

    df["inflation_yoy"] = df["cpi"].pct_change(12, fill_method=None)

    df["rolling_corr_36m"] = (
        df["equity_return"]
        .rolling(36)
        .corr(df["bond_return"])
    )

    df = df.dropna(subset=["equity_return", "bond_return"])
    return df


def compute_historical_regime_summary(historical_df):

    pre_2000_avg = historical_df.loc[: "1999", "rolling_corr_36m"].mean()
    post_2000_avg = historical_df.loc["2000":, "rolling_corr_36m"].mean()

    summary = {
        "Pre_2000_Avg_36m_Corr": pre_2000_avg,
        "Post_2000_Avg_36m_Corr": post_2000_avg
    }

    return pd.DataFrame([summary])