"""Loading and basic preparation of the Brent oil price series and event dataset."""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_RAW = Path(__file__).resolve().parents[1] / "data" / "raw"


def _parse_mixed_date(value: str) -> pd.Timestamp:
    """Parse a date given as either 'DD-Mon-YY' or 'Mon DD, YYYY'.

    The published BrentOilPrices.csv switches date format partway through
    (rows through 2020-04-21 use e.g. '20-May-87'; later rows use e.g.
    'Apr 22, 2020'), so a single fixed strptime format cannot parse the file.
    """
    value = value.strip()
    fmt = "%d-%b-%y" if "-" in value else "%b %d, %Y"
    return pd.to_datetime(value, format=fmt)


def load_prices(path: Path = DATA_RAW / "BrentOilPrices.csv") -> pd.DataFrame:
    """Load raw Brent prices, parse dates, and sort chronologically."""
    df = pd.read_csv(path)
    df["Date"] = df["Date"].apply(_parse_mixed_date)
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def add_log_returns(df: pd.DataFrame, price_col: str = "Price") -> pd.DataFrame:
    """Add a log-return column: log(P_t) - log(P_{t-1})."""
    df = df.copy()
    df["log_price"] = np.log(df[price_col])
    df["log_return"] = df["log_price"].diff()
    return df


def load_events(path: Path = DATA_RAW / "key_events.csv") -> pd.DataFrame:
    """Load the curated key events dataset."""
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)
