import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd



def ensure_output_dir():
    os.makedirs("outputs/figures", exist_ok=True)



def plot_rolling_correlation_modern(df):
    ensure_output_dir()

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df.index, df["corr"], linewidth=1.5)

    ax.axhline(0, linestyle="--", linewidth=1)
    ax.axhline(0.2, linestyle="--", linewidth=1)

    ax.set_title("Rolling 60-Day SPY–TLT Correlation (2006–Present)", fontsize=14)
    ax.set_ylabel("Correlation")

    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("outputs/figures/rolling_correlation_modern.png")
    plt.close()


def plot_drawdowns(df):
    ensure_output_dir()

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df.index, df["drawdown"], label="SPY", linewidth=1.5)
    ax.plot(df.index, df["portfolio_drawdown"], label="60/40", linewidth=1.5)
    ax.plot(df.index, df["portfolio_60_30_10_drawdown"], label="60/30/10", linewidth=1.5)

    ax.set_title("Drawdown Comparison (2006–Present)", fontsize=14)
    ax.set_ylabel("Drawdown")

    ax.legend()

    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("outputs/figures/drawdown_comparison_3asset.png")
    plt.close()


def plot_historical_correlation(df):
    ensure_output_dir()

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df.index, df["rolling_corr_36m"], linewidth=1.5)

    ax.axhline(0, linestyle="--", linewidth=1)

    ax.set_title("36-Month Rolling Stock–Bond Correlation (1962–Present)", fontsize=14)
    ax.set_ylabel("Correlation")

    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("outputs/figures/historical_correlation_36m.png")
    plt.close()