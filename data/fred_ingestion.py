import pandas as pd
from pandas_datareader import data as pdr


def fetch_fred_series(series_id, start="1962-01-01"):
    """
    Fetches a FRED series from St. Louis Fed.
    """
    df = pdr.DataReader(series_id, "fred", start)
    df = df.dropna()
    df.index.name = "date"
    return df