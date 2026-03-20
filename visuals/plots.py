# -*- coding: utf-8 -*-
import os
import plotly.graph_objects as go


def ensure_output_dir():
    os.makedirs("outputs/figures", exist_ok=True)


def plot_rolling_correlation_modern(df):
    ensure_output_dir()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["corr"],
        mode="lines",
        name="60-Day Correlation",
        line=dict(width=1.5)
    ))

    fig.add_hline(y=0, line=dict(dash="dash", width=1, color="grey"))
    fig.add_hline(y=0.2, line=dict(dash="dash", width=1, color="red"),
                  annotation_text="Breakdown threshold (0.2)",
                  annotation_position="top left")

    fig.update_layout(
        title="Rolling 60-Day SPY-TLT Correlation (2006-Present)",
        xaxis_title="Date",
        yaxis_title="Correlation",
        hovermode="x unified",
        template="plotly_white"
    )

    fig.write_html("outputs/figures/rolling_correlation_modern.html")


def plot_drawdowns(df):
    ensure_output_dir()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index, y=df["drawdown"],
        mode="lines", name="SPY", line=dict(width=1.5)
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["portfolio_drawdown"],
        mode="lines", name="60/40", line=dict(width=1.5)
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["portfolio_60_30_10_drawdown"],
        mode="lines", name="60/30/10", line=dict(width=1.5)
    ))

    fig.update_layout(
        title="Drawdown Comparison (2006-Present)",
        xaxis_title="Date",
        yaxis_title="Drawdown",
        hovermode="x unified",
        template="plotly_white"
    )

    fig.write_html("outputs/figures/drawdown_comparison_3asset.html")


def plot_historical_correlation(df):
    ensure_output_dir()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["rolling_corr_36m"],
        mode="lines",
        name="36-Month Correlation",
        line=dict(width=1.5)
    ))

    fig.add_hline(y=0, line=dict(dash="dash", width=1, color="grey"))

    fig.update_layout(
        title="36-Month Rolling Stock-Bond Correlation (1962-Present)",
        xaxis_title="Date",
        yaxis_title="Correlation",
        hovermode="x unified",
        template="plotly_white"
    )

    fig.write_html("outputs/figures/historical_correlation_36m.html")
