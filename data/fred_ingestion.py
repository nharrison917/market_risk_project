import os
import pandas as pd
from fredapi import Fred
from dotenv import load_dotenv

load_dotenv()


def fetch_fred_series(series_id, start="1962-01-01"):
    """
    Fetches a FRED series via the official FRED API.
    Requires FRED_API_KEY environment variable (set in .env).
    """
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "FRED_API_KEY not set. Add it to your .env file. "
            "Get a free key at fredaccount.stlouisfed.org."
        )

    fred = Fred(api_key=api_key)
    series = fred.get_series(series_id, observation_start=start)
    series = series.dropna()

    df = series.to_frame(name=series_id)
    df.index.name = "date"
    return df