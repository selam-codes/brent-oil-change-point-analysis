import numpy as np
import pandas as pd

from src.data_loader import add_log_returns, load_events


def test_add_log_returns_computes_expected_values():
    df = pd.DataFrame({"Price": [100.0, 110.0, 99.0]})
    result = add_log_returns(df)
    assert np.isnan(result["log_return"].iloc[0])
    assert np.isclose(result["log_return"].iloc[1], np.log(110.0 / 100.0))
    assert np.isclose(result["log_return"].iloc[2], np.log(99.0 / 110.0))


def test_load_events_parses_dates_and_sorts_chronologically():
    events = load_events()
    assert events["date"].is_monotonic_increasing
    assert pd.api.types.is_datetime64_any_dtype(events["date"])
    assert len(events) >= 10
