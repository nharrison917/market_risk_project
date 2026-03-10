import numpy as np
import pandas as pd


def compute_var_cvar(series, alpha=0.05):
    """
    Historical VaR and CVaR
    """
    series = series.dropna()

    var = np.percentile(series, alpha * 100)
    cvar = series[series <= var].mean()

    return var, cvar


def compute_tail_comparison(master_df):

    results = {}

    pre_2022 = master_df[master_df.index < "2022-01-01"]
    post_2022 = master_df[master_df.index >= "2022-01-01"]

    periods = {
        "Full Sample": master_df,
        "Pre-2022": pre_2022,
        "Post-2022": post_2022
    }

    for label, df in periods.items():

        spy_var, spy_cvar = compute_var_cvar(df["daily_return"])
        port_var, port_cvar = compute_var_cvar(df["portfolio_60_40"])
        port3_var, port3_cvar = compute_var_cvar(df["portfolio_60_30_10"])

        results[label] = {
            "SPY_VaR_5%": spy_var,
            "SPY_CVaR_5%": spy_cvar,
            "60_40_VaR_5%": port_var,
            "60_40_CVaR_5%": port_cvar,
            "60_30_10_VaR_5%": port3_var,
            "60_30_10_CVaR_5%": port3_cvar
        }

    return pd.DataFrame(results).T

