import yfinance as yf
import pandas as pd


def fetch_history(ticker_symbol, start="1993-01-01"):
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(start=start, auto_adjust=True)

    df = df.reset_index()
    df = df[["Date", "Close", "Volume"]]
    df.columns = ["date", "adj_close", "volume"]

    df["ticker"] = ticker_symbol

    return df