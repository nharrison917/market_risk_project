import sqlite3
import pandas as pd


def init_db(db_path="data_store.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            date TEXT,
            ticker TEXT,
            close REAL,
            adj_close REAL,
            volume REAL,
            PRIMARY KEY (date, ticker)
        )
    """)

    conn.commit()
    conn.close()


def write_prices(df, db_path="data_store.db"):
    conn = sqlite3.connect(db_path)
    df.to_sql("prices", conn, if_exists="replace", index=False)
    conn.close()

def load_prices_from_db():
    conn = sqlite3.connect("data_store.db")

    df = pd.read_sql("SELECT * FROM prices", conn)

    conn.close()

    # Convert date column safely
    df["date"] = pd.to_datetime(df["date"], utc=True).dt.tz_localize(None)

    return df