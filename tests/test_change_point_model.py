import numpy as np
import pandas as pd

from src.change_point_model import (
    build_mean_shift_model,
    detect_changepoints_pelt,
    match_nearest_event,
    sample_model,
    summarize_regimes,
    tau_index_to_date,
)


def test_tau_index_to_date_maps_to_correct_row():
    dates = pd.Series(pd.date_range("2020-01-01", periods=10))
    assert tau_index_to_date(3, dates) == pd.Timestamp("2020-01-04")


def test_match_nearest_event_filters_by_window_and_sorts_by_distance():
    events = pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-01", "2020-01-10", "2020-03-01"]),
            "event_name": ["near", "far_but_in_window", "outside_window"],
        }
    )
    matches = match_nearest_event(pd.Timestamp("2020-01-03"), events, window_days=14)
    assert list(matches["event_name"]) == ["near", "far_but_in_window"]


def test_match_nearest_event_returns_empty_when_nothing_in_window():
    events = pd.DataFrame(
        {"date": pd.to_datetime(["2020-06-01"]), "event_name": ["too_far"]}
    )
    matches = match_nearest_event(pd.Timestamp("2020-01-01"), events, window_days=14)
    assert matches.empty


def test_detect_changepoints_pelt_finds_synthetic_break():
    rng = np.random.default_rng(0)
    signal = np.concatenate([rng.normal(0, 1, 200), rng.normal(10, 1, 200)])
    breakpoints = detect_changepoints_pelt(signal, penalty=50, min_size=30, jump=1)
    assert len(breakpoints) == 1
    assert 180 <= breakpoints[0] <= 220


def test_summarize_regimes_computes_before_after_means():
    dates = pd.Series(pd.date_range("2020-01-01", periods=6))
    values = pd.Series([1.0, 1.0, 1.0, 3.0, 3.0, 3.0])
    summary = summarize_regimes(dates, values, breakpoints=[3])
    assert summary.loc[0, "mean_before"] == 1.0
    assert summary.loc[0, "mean_after"] == 3.0
    assert np.isclose(summary.loc[0, "pct_change"], 200.0)


def test_mean_shift_model_samples_without_error_on_small_synthetic_data():
    rng = np.random.default_rng(1)
    data = np.concatenate([rng.normal(0, 0.01, 40), rng.normal(0.05, 0.01, 40)])
    model = build_mean_shift_model(data)
    idata = sample_model(model, draws=100, tune=100, chains=2, random_seed=1)
    assert "tau" in idata.posterior
    assert "mu_1" in idata.posterior
    assert "mu_2" in idata.posterior
