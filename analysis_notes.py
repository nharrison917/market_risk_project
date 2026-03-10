 
"""
Exploratory Macro Regime Analysis

Supplementary structural analysis supporting diversification study.
"""

import pandas as pd
from research.historical_regime_analysis import build_historical_dataset


def correlation_velocity_analysis(df):

    print("\n" + "="*60)
    print("Correlation Velocity Comparison (1970s vs 2020s)")
    print("="*60)

    corr_70s = df.loc["1970":"1982", "rolling_corr_36m"]
    corr_2020s = df.loc["2020":"2023", "rolling_corr_36m"]

    df["corr_12m_change"] = df["rolling_corr_36m"].diff(12)

    print(f"70s max level: {corr_70s.max():.4f}")
    print(f"2020s max level: {corr_2020s.max():.4f}")

    print(f"70s max 12m change: {corr_70s.diff(12).max():.4f}")
    print(f"2020s max 12m change: {corr_2020s.diff(12).max():.4f}")


def real_yield_shock_analysis(df):

    print("\n" + "="*60)
    print("Real Yield Shock Comparison")
    print("="*60)

    df["real_yield_proxy"] = (
        df["yield_10y"] - df["inflation_yoy"]
    )

    df["real_yield_12m_change"] = (
        df["real_yield_proxy"].diff(12)
    )

    ry_70s = df.loc["1970":"1982", "real_yield_12m_change"]
    ry_2020s = df.loc["2020":"2023", "real_yield_12m_change"]

    print(f"70s max real yield 12m change: {ry_70s.max():.4f}")
    print(f"2020s max real yield 12m change: {ry_2020s.max():.4f}")


def decade_structure_analysis(df):

    print("\n" + "="*60)
    print("Decade-Level Correlation Structure")
    print("="*60)

    df["decade"] = (df.index.year // 10) * 10

    decade_corr = (
        df.groupby("decade")["rolling_corr_36m"].mean()
    )

    positive_share = (
        df.groupby("decade")["rolling_corr_36m"]
        .apply(lambda x: (x > 0).mean())
    )

    print("\nAverage 36m correlation by decade:")
    print(decade_corr)

    print("\nShare of positive months by decade:")
    print(positive_share)


if __name__ == "__main__":

    print("\nBuilding historical dataset once...")
    historical_df = build_historical_dataset()

    correlation_velocity_analysis(historical_df.copy())
    real_yield_shock_analysis(historical_df.copy())
    decade_structure_analysis(historical_df.copy())

    print("\nAnalysis complete.")