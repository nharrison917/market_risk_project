# -*- coding: utf-8 -*-
"""
Market Risk Regime Dashboard
Streamlit entry point for portfolio regime analysis.
All data read from pre-computed CSVs in outputs/.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Portfolio Regime Analysis",
    page_icon=None,
    layout="wide",
)

OUTPUTS = Path("outputs")
RISK_FREE_RATE = 0.02  # Used in Sharpe computation; displayed explicitly

# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

@st.cache_data
def load_performance():
    df = pd.read_csv(OUTPUTS / "performance_summary.csv", index_col=0)
    return df


@st.cache_data
def load_tail_risk():
    df = pd.read_csv(OUTPUTS / "tail_risk_summary.csv", index_col=0)
    return df


@st.cache_data
def load_current_regime():
    df = pd.read_csv(OUTPUTS / "current_regime.csv", index_col=0)
    return df.iloc[0]


@st.cache_data
def load_drawdown_ts():
    df = pd.read_csv(OUTPUTS / "drawdown_timeseries.csv", index_col=0, parse_dates=True)
    return df


@st.cache_data
def load_corr_modern():
    df = pd.read_csv(OUTPUTS / "correlation_modern.csv", index_col=0, parse_dates=True)
    return df


@st.cache_data
def load_corr_historical():
    df = pd.read_csv(OUTPUTS / "correlation_historical.csv", index_col=0, parse_dates=True)
    return df


@st.cache_data
def load_historical_summary():
    df = pd.read_csv(OUTPUTS / "historical_regime_summary.csv", index_col=0)
    return df


@st.cache_data
def load_portfolio_returns():
    df = pd.read_csv(OUTPUTS / "portfolio_returns.csv", index_col=0, parse_dates=True)
    return df


@st.cache_data
def load_decade_structure():
    df = pd.read_csv(OUTPUTS / "decade_structure.csv", index_col=0)
    return df


@st.cache_data
def load_real_yield_shocks():
    df = pd.read_csv(OUTPUTS / "real_yield_shocks.csv")
    return df


# ---------------------------------------------------------------------------
# Data coverage -- every date label in the app derives from these, so labels
# stay correct if the pipeline (main.py) is re-run on newer data.
# ---------------------------------------------------------------------------

def fmt_month(ts):
    return ts.strftime("%B %Y")


@st.cache_data
def get_coverage():
    modern = load_corr_modern()
    hist = load_corr_historical()
    return {
        "modern_start": modern.index.min(),
        "modern_end": modern.index.max(),
        "hist_start": hist.index.min(),
        "hist_end": hist.index.max(),
        # First month with a full 36-month correlation window
        "hist_corr_start": hist["rolling_corr_36m"].first_valid_index(),
    }


# ---------------------------------------------------------------------------
# Sustained breakdown logic
# ---------------------------------------------------------------------------

BREAKDOWN_MIN_DAYS = 21  # 1 trading month minimum for a "meaningful" regime episode


@st.cache_data
def get_sustained_breakdown_periods(min_days=BREAKDOWN_MIN_DAYS):
    """
    Returns a list of (start, end) tuples for sustained breakdown episodes.
    Breakdown = 60-day SPY-TLT correlation > 0.2 for at least min_days consecutive trading days.
    """
    corr = load_corr_modern().copy()
    corr.columns = ["corr"]
    corr["breakdown"] = corr["corr"] > 0.2
    corr["run_id"] = (corr["breakdown"] != corr["breakdown"].shift()).cumsum()

    periods = []
    for _, group in corr[corr["breakdown"]].groupby("run_id"):
        if len(group) >= min_days:
            periods.append((group.index.min(), group.index.max()))
    return periods


@st.cache_data
def compute_regime_metrics():
    """
    Splits portfolio daily returns into sustained-breakdown vs non-breakdown days
    and computes annualized return, annualized vol, and CVaR (5%) for each.
    """
    import numpy as np
    returns = load_portfolio_returns().dropna()
    corr = load_corr_modern().copy()
    corr.columns = ["corr"]

    # Build boolean mask: True = inside a sustained breakdown episode
    breakdown_mask = pd.Series(False, index=returns.index)
    for start, end in get_sustained_breakdown_periods():
        breakdown_mask.loc[start:end] = True

    results = []
    for label, mask in [("Sustained Breakdown", breakdown_mask),
                        ("Non-Breakdown", ~breakdown_mask)]:
        subset = returns[mask]
        n = len(subset)
        if n < 2:
            continue
        for col, name in [("spy", "SPY"), ("port_60_40", "60/40"), ("port_60_30_10", "60/30/10")]:
            s = subset[col]
            ann_ret = (1 + s).prod() ** (252 / n) - 1
            ann_vol = s.std() * np.sqrt(252)
            var_5 = s.quantile(0.05)
            cvar_5 = s[s <= var_5].mean()
            results.append({
                "Period": label,
                "Portfolio": name,
                "Ann. Return": ann_ret,
                "Ann. Volatility": ann_vol,
                "CVaR (5%)": cvar_5,
            })

    df = pd.DataFrame(results)
    return df


# ---------------------------------------------------------------------------
# Figure builders
# ---------------------------------------------------------------------------

def build_drawdown_fig(df, breakdown_periods=None):
    fig = go.Figure()

    # Shade sustained breakdown episodes first (renders behind lines)
    if breakdown_periods:
        first = True
        for start, end in breakdown_periods:
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor="rgba(255,180,0,0.22)",
                line_color="rgba(255,180,0,0.55)",
                line_width=1,
                name="Sustained Breakdown" if first else None,
                showlegend=first,
            )
            first = False

    fig.add_trace(go.Scatter(
        x=df.index, y=df["drawdown"] * 100,
        mode="lines", name="SPY (100% Equity)",
        line=dict(width=1.5, color="#EF553B")
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["portfolio_drawdown"] * 100,
        mode="lines", name="60/40 (SPY + TLT)",
        line=dict(width=1.5, color="#636EFA")
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["portfolio_60_30_10_drawdown"] * 100,
        mode="lines", name="60/30/10 (+ Commodities)",
        line=dict(width=1.5, color="#00CC96")
    ))
    fig.update_layout(
        title="Portfolio Drawdown Comparison — Shaded: Sustained Correlation Breakdown Episodes (>=21 days)",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(tickformat=".0f", ticksuffix="%"),
    )
    return fig


def build_corr_modern_fig(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df["rolling_corr_60d"],
        mode="lines", name="60-Day SPY-TLT Correlation",
        line=dict(width=1.5, color="#636EFA")
    ))
    fig.add_hline(y=0, line=dict(dash="dash", width=1, color="grey"))
    fig.add_hline(
        y=0.2, line=dict(dash="dash", width=1, color="#EF553B"),
        annotation_text="Breakdown threshold (0.2)",
        annotation_position="top left"
    )
    fig.update_layout(
        title=f"Rolling 60-Day SPY-TLT Correlation ({df.index.min().year}–{fmt_month(df.index.max())})",
        xaxis_title="Date",
        yaxis_title="Correlation",
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def build_corr_historical_fig(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df["rolling_corr_36m"],
        mode="lines", name="36-Month Stock-Bond Correlation",
        line=dict(width=1.5, color="#AB63FA")
    ))
    fig.add_hline(y=0, line=dict(dash="dash", width=1, color="grey"))
    fig.add_vrect(
        x0="2000-01-01", x1=str(df.index.max()),
        fillcolor="rgba(99,110,250,0.07)", line_width=0,
        annotation_text="Modern era (post-2000)",
        annotation_position="top left"
    )
    fig.update_layout(
        title=f"36-Month Rolling Stock-Bond Correlation ({df.index.min().year}\u2013{fmt_month(df.index.max())})",
        xaxis_title="Date",
        yaxis_title="Correlation",
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


# ---------------------------------------------------------------------------
# Regime color helpers
# ---------------------------------------------------------------------------

REGIME_COLORS = {
    # Vol
    "LOW_VOL":    "normal",
    "NORMAL_VOL": "normal",
    "HIGH_VOL":   "inverse",
    # Corr
    "DIVERSIFYING": "normal",
    "NEUTRAL":      "normal",
    "BREAKDOWN":    "inverse",
    # Drawdown
    "NORMAL":     "normal",
    "CORRECTION": "off",
    "STRESS":     "inverse",
}

REGIME_LABELS = {
    "LOW_VOL": "Low Volatility",
    "NORMAL_VOL": "Normal Volatility",
    "HIGH_VOL": "High Volatility",
    "DIVERSIFYING": "Diversifying",
    "NEUTRAL": "Neutral",
    "BREAKDOWN": "Breakdown",
    "NORMAL": "Normal",
    "CORRECTION": "Correction",
    "STRESS": "Stress",
}

# ---------------------------------------------------------------------------
# Format helpers
# ---------------------------------------------------------------------------

def fmt_pct(val, decimals=1):
    return f"{val * 100:.{decimals}f}%"


def fmt_float(val, decimals=2):
    return f"{val:.{decimals}f}"


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------

cov = get_coverage()
modern_range = f"{fmt_month(cov['modern_start'])} – {cov['modern_end'].strftime('%B %d, %Y')}"
hist_range = f"{fmt_month(cov['hist_start'])} – {fmt_month(cov['hist_end'])}"
hist_end = fmt_month(cov["hist_end"])
modern_end = fmt_month(cov["modern_end"])

st.caption(
    f"**Data coverage** — ETF era (SPY, TLT, DBC daily): {modern_range}. "
    f"Historical (Shiller S&P 500 + FRED, monthly): {hist_range}. "
    "Figures are a fixed snapshot of the analysis; \"current\" means the latest date above."
)

tab1, tab2 = st.tabs(["Executive Summary", "Deep Dive"])

# ===========================================================================
# TAB 1: EXECUTIVE SUMMARY
# ===========================================================================
with tab1:
    st.title("Portfolio Regime Analysis: Is 60/40 Still Enough?")
    st.markdown(
        "The negative stock-bond correlation that made the classic 60/40 portfolio so effective "
        "from 2000-2020 was historically unusual, not the long-run norm. "
        "This analysis examines whether adding a modest commodity allocation improves resilience "
        "when that relationship breaks down."
    )

    st.divider()

    # --- Current Regime Snapshot ---
    st.subheader("Current Market Regime")
    regime = load_current_regime()
    regime_date = pd.to_datetime(regime.name).strftime("%B %d, %Y") if regime.name else "Unknown"
    st.caption(f"As of {regime_date} | Based on SPY 30-day rolling vol, 60-day SPY-TLT correlation, and SPY drawdown from peak")

    col1, col2, col3, col4 = st.columns(4)

    vol_label = REGIME_LABELS.get(regime["vol_regime"], regime["vol_regime"])
    corr_label = REGIME_LABELS.get(regime["corr_regime"], regime["corr_regime"])
    dd_label = REGIME_LABELS.get(regime["dd_regime"], regime["dd_regime"])

    col1.metric(
        label="Volatility Regime",
        value=vol_label,
        delta=f"{regime['rolling_vol_30'] * 100:.1f}% annualized vol",
        delta_color=REGIME_COLORS.get(regime["vol_regime"], "normal"),
    )
    col2.metric(
        label="Correlation Regime",
        value=corr_label,
        delta=f"SPY-TLT corr: {regime['corr']:.2f}",
        delta_color=REGIME_COLORS.get(regime["corr_regime"], "normal"),
    )
    col3.metric(
        label="Drawdown Regime",
        value=dd_label,
        delta=f"SPY drawdown: {regime['drawdown'] * 100:.1f}%",
        delta_color=REGIME_COLORS.get(regime["dd_regime"], "normal"),
    )
    col4.metric(
        label="Full Regime Label",
        value="",
        delta=regime["regime"],
        delta_color="off",
    )

    st.divider()

    # --- Regime-sliced metrics ---
    st.subheader("Where the Hedge Earns Its Cost: Performance by Correlation Regime")
    st.markdown(
        "The full-sample numbers favor 60/40 — and they should. Most of 2006-2020 was a "
        "low-inflation, negative-correlation environment where bonds were excellent diversifiers. "
        "The table below slices by regime: **sustained breakdown episodes** (60-day SPY-TLT "
        f"correlation > 0.2 for at least {BREAKDOWN_MIN_DAYS} consecutive trading days) "
        "vs all other periods."
    )

    regime_metrics = compute_regime_metrics()

    for period_label in ["Sustained Breakdown", "Non-Breakdown"]:
        subset = regime_metrics[regime_metrics["Period"] == period_label].copy()
        subset = subset.drop(columns="Period").set_index("Portfolio")
        subset["Ann. Return"] = subset["Ann. Return"].apply(lambda x: fmt_pct(x))
        subset["Ann. Volatility"] = subset["Ann. Volatility"].apply(lambda x: fmt_pct(x))
        subset["CVaR (5%)"] = subset["CVaR (5%)"].apply(lambda x: fmt_pct(x))

        if period_label == "Sustained Breakdown":
            st.markdown("**During sustained correlation breakdown episodes**")
        else:
            st.markdown("**Outside breakdown episodes (bonds diversifying or neutral)**")
        st.dataframe(subset)

    st.caption(
        f"Daily returns, {modern_range}. "
        f"Sustained breakdown = 60-day SPY-TLT correlation > 0.2 for >= {BREAKDOWN_MIN_DAYS} "
        "consecutive trading days. CVaR (5%) = average daily loss on the worst 5% of days. "
        f"Sharpe ratio (full sample, 2% risk-free rate) — SPY: {fmt_float(load_performance().loc['SPY','Sharpe_Ratio'])}, "
        f"60/40: {fmt_float(load_performance().loc['60_40','Sharpe_Ratio'])}, "
        f"60/30/10: {fmt_float(load_performance().loc['60_30_10','Sharpe_Ratio'])}."
    )

    # --- Recommendation callout ---
    _rm = compute_regime_metrics()
    _bd = _rm[_rm["Period"] == "Sustained Breakdown"].set_index("Portfolio")
    _ret_diff = (_bd.loc["60/30/10", "Ann. Return"] - _bd.loc["60/40", "Ann. Return"]) * 100
    _cvar_diff = (_bd.loc["60/30/10", "CVaR (5%)"] - _bd.loc["60/40", "CVaR (5%)"]) * 100

    st.info(
        f"**Key finding:** During sustained correlation breakdown episodes, 60/30/10 shows "
        f"**{abs(_cvar_diff):.2f} percentage points better daily CVaR** than 60/40 "
        f"({'better' if _cvar_diff > 0 else 'worse'} tail protection), "
        f"with a return difference of {_ret_diff:+.2f}pp annualized. "
        "Outside these episodes — when bonds are doing their job — 60/40 leads on both return and vol. "
        "The commodity allocation is regime insurance: it costs little in benign environments "
        "and stabilizes tail risk precisely when the stock-bond hedge fails."
    )

    st.divider()

    # --- Drawdown chart ---
    st.subheader("Drawdown Through Time")
    st.caption(
        f"{modern_range}. Shaded regions mark sustained correlation breakdown episodes "
        f"(>={BREAKDOWN_MIN_DAYS} trading days above 0.2 threshold)."
    )
    drawdown_df = load_drawdown_ts()
    breakdown_periods = get_sustained_breakdown_periods()
    st.plotly_chart(build_drawdown_fig(drawdown_df, breakdown_periods))


# ===========================================================================
# TAB 2: DEEP DIVE
# ===========================================================================
with tab2:
    st.title("Deep Dive: The Mechanics Behind the Recommendation")
    st.markdown(
        "The executive summary recommendation rests on two structural claims: "
        "(1) stock-bond diversification is regime-dependent across history, not a stable property; "
        "(2) the current inflation-shock regime closely resembles prior breakdowns. "
        "The analysis below supports both."
    )

    st.divider()

    # --- Historical correlation chart ---
    hist_corr = load_corr_historical()

    st.subheader(f"{cov['hist_start'].year}–{hist_end}: Stock-Bond Correlation")
    st.markdown(
        "The 36-month rolling correlation between stocks and bonds has spent significant time "
        "in positive territory. The post-2000 negative correlation period was the exception. "
        "The shaded region marks the modern era (post-2000) that most investors treat as the baseline."
    )
    st.caption(
        f"Source: Robert Shiller (Yale) monthly S&P 500 data + FRED 10-year Treasury yield, "
        f"{hist_range} (the Shiller source used ends {hist_end}). The 36-month correlation "
        f"begins {fmt_month(cov['hist_corr_start'])}, once a full window is available. "
        f"For the period after {hist_end}, see the ETF-era correlation chart below."
    )

    st.plotly_chart(build_corr_historical_fig(hist_corr))

    # --- Decade breakdown table ---
    st.subheader("Decade-Level Correlation Structure")
    st.markdown(
        "Breaking the historical period into decades reveals the structural shift. "
        "The 1970s through 1990s were characterized by predominantly positive stock-bond correlation "
        "(80–94% of months); the late 1960s were mixed. "
        "The 2000s-2010s were anomalously negative. The 2020s have already begun reverting."
    )

    st.dataframe(load_decade_structure())
    st.caption(
        f"Based on 36-month rolling correlation, {fmt_month(cov['hist_corr_start'])} – {hist_end}. "
        f"Partial decades: the 1960s row covers {cov['hist_corr_start'].year}–1969 only, and the "
        f"2020s row covers January 2020 – {hist_end} only. The correlation reversal it shows has "
        f"continued and deepened through {modern_end}; see the ETF-era chart below for the full "
        "post-2022 picture."
    )

    st.divider()

    # --- Tail risk table ---
    st.subheader("Tail Risk: Before and After the 2022 Regime Shift")
    st.markdown(
        "The 2022 inflation shock was the clearest test of regime-dependence in the modern ETF era. "
        "Historical VaR and CVaR (both at the 5th percentile) show how tail risk changed "
        "once the stock-bond correlation flipped positive."
    )

    tail = load_tail_risk()
    st.dataframe(tail)
    st.caption(
        f"Source: daily ETF returns (SPY, TLT, DBC) via yfinance. Coverage: {modern_range}. "
        "VaR: daily loss exceeded 5% of the time. CVaR: average loss on those worst-5% days. "
        f"Pre-2022 = 2006–2021. Post-2022 = January 2022–{modern_end}."
    )

    st.divider()

    # --- Real yield shock ---
    st.subheader("Regime Transitions: Real Yield Shocks")
    st.markdown(
        "Real yield shocks (12-month change in nominal 10-year yield minus YoY CPI) drive "
        "correlation regime transitions. The 2020s shock magnitude is comparable to the 1970s, "
        "which is the last sustained period of positive stock-bond correlation."
    )

    st.dataframe(load_real_yield_shocks(), hide_index=True)
    st.caption(
        "Real yield proxy = 10-year nominal yield minus YoY CPI inflation (both in percent). "
        "Max 12-month change measured within each era: 1970s = January 1970 – December 1982; "
        f"2020s = January 2020 – {hist_end} (end of historical data)."
    )

    st.divider()

    # --- Modern correlation chart ---
    st.subheader(f"Modern Era: Rolling 60-Day SPY-TLT Correlation ({cov['modern_start'].year}–{modern_end})")
    st.markdown(
        "Zooming into the ETF era, the breakdown threshold (correlation > 0.2) was crossed "
        "in 2022 and has persisted. This is what the current regime snapshot on the summary tab is detecting."
    )

    corr_modern = load_corr_modern()
    st.plotly_chart(build_corr_modern_fig(corr_modern))
