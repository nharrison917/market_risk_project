import pandas as pd

def fetch_shiller_data():
    url = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"

    df = pd.read_excel(url, sheet_name="Data", skiprows=7)

    df = df[["Date", "P"]].copy()
    df.columns = ["date_decimal", "sp500"]

    df = df.dropna(subset=["date_decimal"])

    df["year"] = df["date_decimal"].astype(int)
    df["month"] = ((df["date_decimal"] - df["year"]) * 100).round().astype(int)

    df["date"] = pd.to_datetime(
        dict(year=df["year"], month=df["month"], day=1)
    )

    df = df.set_index("date")[["sp500"]]

    # 🔥 Convert to month-end to match FRED
    df.index = df.index + pd.offsets.MonthEnd(0)

    # 🔥 Ensure one row per month
    df = df.groupby(df.index).last()

    return df