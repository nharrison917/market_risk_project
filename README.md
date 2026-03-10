# Market Risk Project

## Regime Dependence of Stock--Bond Diversification

------------------------------------------------------------------------

## Executive Summary

Stock–bond correlation is regime-dependent. The deeply negative 2000–2020
correlation regime was historically atypical relative to pre-2000 norms.
A modest allocation to inflation-sensitive assets reduces inflation-shock
drawdowns with limited long-run return tradeoff.

------------------------------------------------------------------------

## Overview

This project analyzes the regime dependence of stock–bond diversification 
and evaluates structural portfolio robustness under inflation-driven stress
environments.

The traditional 60/40 portfolio assumes that bonds hedge equity risk during
drawdowns. However, stock–bond correlation is not structurally stable across
macro regimes. This project investigates whether the negative correlation 
regime observed from 2000–2020 was historically typical, and whether modest
inflation-sensitive exposure improves portfolio robustness. 

The project combines modern ETF data (2002--present) with 60 years of
macroeconomic history (1962--present).

------------------------------------------------------------------------

## Research Questions

1.  How persistent is negative stock--bond correlation?
2.  Was the 2000--2020 regime historically anomalous?
3.  How did diversification behave during inflation-driven drawdowns?
4.  Can modest commodity exposure improve portfolio robustness without
    overfitting?

------------------------------------------------------------------------

## Data & Methodology

### Modern ETF Layer (2006--Present)

**Assets:**
 - SPY (equities)
 - TLT (long-duration Treasuries)
 - DBC (broad commodities)

**Metrics:** - Daily returns - Rolling 30-day volatility - Rolling
60-day SPY--TLT correlation - Drawdowns - Tail risk (VaR, CVaR) -
Conditional equity tail performance

**Structural Test:** - 60/40 portfolio - 60/30/10 portfolio (adding 10%
commodities)

Additional exploratory regime analysis is available in analysis_notes.py
and is not required for core outputs.

------------------------------------------------------------------------

### Historical Macro Layer (1962--Present)

**Data sources:** - Shiller S&P data (monthly) - FRED 10-year Treasury
yields (DGS10) - CPI (CPIAUCSL)

**Constructed:** - Monthly equity returns - Bond returns are approximated
using a constant-duration duration × yield change framework.
 - 36-month rolling stock--bond correlation

This provides a 60-year macro view of correlation regimes.

------------------------------------------------------------------------

## Key Findings

All statistics are computed using rolling correlations and non-parametric
historical tail metrics (VaR, CVaR).

### 1. Stock--Bond Correlation Is Regime-Dependent

Correlation has historically been:

-   Mostly positive prior to 2000
-   Deeply negative during 2000--2020
-   Rising again during the 2022 inflation shock

------------------------------------------------------------------------

### 2. The 2000--2020 Negative Regime Was Historically Unusual

-   Pre-2000 average 36m correlation: **+0.12**
-   Post-2000 average 36m correlation: **−0.32**
-   1970s--1990s saw predominantly positive correlation

The negative stock–bond correlation regime commonly assumed in
portfolio construction is not the long-run historical norm.

------------------------------------------------------------------------

### 3. 2022 Represented a Rapid Partial Reversion

-   Correlation levels resembled historical inflation regimes.
-   The speed of transition was historically extreme.
-   Suggests that modern market structure may amplify regime transitions.

------------------------------------------------------------------------

### 4. Adding Commodities Improved Inflation Shock Robustness

In 2022:

-   60/40: −24.4%
-   60/30/10: −18.8%

However:

-   2008 and 2020 favored 60/40
-   Long-run return tradeoff was modest (\~16 bps annualized)

Adding commodities reduced regime asymmetry but sacrificed some
growth-shock performance.

------------------------------------------------------------------------

## Portfolio Implications

-   Diversification is structurally regime-dependent.
-   The 60/40 portfolio performs strongly during growth-dominant
    regimes.
-   Inflation regimes require broader structural diversification.
-   Regime timing remains difficult; structural robustness may be
    preferable to tactical timing.

------------------------------------------------------------------------

## Charts Included

-   36-Month Rolling Stock--Bond Correlation (1962--Present)
-   Rolling 60-Day SPY--TLT Correlation (Modern)
-   Drawdown Comparison: SPY vs 60/40 vs 60/30/10

------------------------------------------------------------------------

## Outputs

- performance_summary.csv
- tail_risk_summary.csv
- historical_regime_summary.csv

------------------------------------------------------------------------

## Environment Setup


To recreate the environment:

``` bash
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Developed and tested using Python 3.11 and pandas 2.1.4 (pandas < 2.2
required for pandas-datareader compatibility).