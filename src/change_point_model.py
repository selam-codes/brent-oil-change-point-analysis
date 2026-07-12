"""Bayesian change point modeling of Brent oil log returns (Task 2).

Implements a single change-point mean-shift model (as specified in the challenge
brief) and a mean+variance switch extension, both built with PyMC. Also provides
helpers to translate posterior results into dates, quantified impact statements,
and matches against the researched key-events dataset.
"""

from __future__ import annotations

from dataclasses import dataclass

import arviz as az
import numpy as np
import pandas as pd
import pymc as pm


def build_mean_shift_model(returns: np.ndarray) -> pm.Model:
    """Single change-point model: two regime means, shared variance.

    `tau` is a discrete-uniform prior over all valid indices in `returns`.
    `pm.math.switch` selects mu_1 before tau and mu_2 from tau onward.
    """
    n = len(returns)
    with pm.Model() as model:
        tau = pm.DiscreteUniform("tau", lower=0, upper=n - 1)
        mu_1 = pm.Normal("mu_1", mu=0.0, sigma=0.1)
        mu_2 = pm.Normal("mu_2", mu=0.0, sigma=0.1)
        sigma = pm.HalfNormal("sigma", sigma=0.1)

        idx = np.arange(n)
        mu = pm.math.switch(tau >= idx, mu_1, mu_2)

        pm.Normal("obs", mu=mu, sigma=sigma, observed=returns)
    return model


def build_mean_variance_shift_model(returns: np.ndarray) -> pm.Model:
    """Change-point model letting both mean and variance switch at tau."""
    n = len(returns)
    with pm.Model() as model:
        tau = pm.DiscreteUniform("tau", lower=0, upper=n - 1)
        mu_1 = pm.Normal("mu_1", mu=0.0, sigma=0.1)
        mu_2 = pm.Normal("mu_2", mu=0.0, sigma=0.1)
        sigma_1 = pm.HalfNormal("sigma_1", sigma=0.1)
        sigma_2 = pm.HalfNormal("sigma_2", sigma=0.1)

        idx = np.arange(n)
        before = tau >= idx
        mu = pm.math.switch(before, mu_1, mu_2)
        sigma = pm.math.switch(before, sigma_1, sigma_2)

        pm.Normal("obs", mu=mu, sigma=sigma, observed=returns)
    return model


def sample_model(
    model: pm.Model,
    draws: int = 2000,
    tune: int = 1500,
    chains: int = 4,
    random_seed: int = 42,
) -> az.InferenceData:
    """Run NUTS (for continuous params) + built-in discrete sampling for tau."""
    with model:
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            random_seed=random_seed,
            progressbar=False,
        )
    return idata


def check_convergence(idata: az.InferenceData, var_names: list[str] | None = None) -> pd.DataFrame:
    """Return an arviz summary (r_hat, ess_bulk, ess_tail, etc.)."""
    return az.summary(idata, var_names=var_names)


def tau_index_to_date(tau_index: int, dates: pd.Series) -> pd.Timestamp:
    """Map a discrete tau index (0-based row position) to its calendar date."""
    return pd.Timestamp(dates.iloc[int(tau_index)])


@dataclass
class ChangePointResult:
    tau_index_mean: float
    tau_index_mode: int
    change_date: pd.Timestamp
    hdi_low_date: pd.Timestamp
    hdi_high_date: pd.Timestamp
    mu_1_mean: float
    mu_2_mean: float
    prob_increase: float
    pct_change_price: float
    sigma_1_mean: float | None = None
    sigma_2_mean: float | None = None


def quantify_impact(
    idata: az.InferenceData,
    dates: pd.Series,
    has_variance_switch: bool = False,
) -> ChangePointResult:
    """Summarize the posterior into a change date, effect sizes, and probabilities."""
    tau_samples = idata.posterior["tau"].values.flatten()
    tau_mode = int(pd.Series(tau_samples).mode().iloc[0])
    tau_mean = float(tau_samples.mean())

    hdi = az.hdi(idata, var_names=["tau"], prob=0.94)["tau"].values
    hdi_low, hdi_high = int(hdi[0]), int(hdi[1])

    mu_1_samples = idata.posterior["mu_1"].values.flatten()
    mu_2_samples = idata.posterior["mu_2"].values.flatten()
    mu_1_mean = float(mu_1_samples.mean())
    mu_2_mean = float(mu_2_samples.mean())

    # log-return means map to a multiplicative daily-average price effect;
    # exp(mu) - 1 is the implied average daily percentage price change.
    pct_change_price = float((np.exp(mu_2_mean) - np.exp(mu_1_mean)) / np.exp(mu_1_mean) * 100)
    prob_increase = float((mu_2_samples > mu_1_samples).mean())

    result = ChangePointResult(
        tau_index_mean=tau_mean,
        tau_index_mode=tau_mode,
        change_date=tau_index_to_date(tau_mode, dates),
        hdi_low_date=tau_index_to_date(hdi_low, dates),
        hdi_high_date=tau_index_to_date(hdi_high, dates),
        mu_1_mean=mu_1_mean,
        mu_2_mean=mu_2_mean,
        prob_increase=prob_increase,
        pct_change_price=pct_change_price,
    )

    if has_variance_switch:
        result.sigma_1_mean = float(idata.posterior["sigma_1"].values.mean())
        result.sigma_2_mean = float(idata.posterior["sigma_2"].values.mean())

    return result


def match_nearest_event(
    change_date: pd.Timestamp,
    events: pd.DataFrame,
    window_days: int = 14,
) -> pd.DataFrame:
    """Return events within `window_days` of `change_date`, nearest first."""
    diffs = (events["date"] - change_date).abs()
    within_window = events[diffs <= pd.Timedelta(days=window_days)].copy()
    within_window["days_from_changepoint"] = (within_window["date"] - change_date).dt.days
    return within_window.sort_values("days_from_changepoint", key=lambda s: s.abs())


def detect_changepoints_pelt(
    signal: np.ndarray,
    penalty: float,
    min_size: int = 90,
    jump: int = 5,
) -> list[int]:
    """Multiple change-point detection via PELT (non-Bayesian robustness baseline).

    `signal` should be standardized (or otherwise on a consistent scale) so that
    `penalty` is meaningful: use raw log returns for a volatility-driven view of
    breaks, or a z-scored price level for a trend-driven view. Returns 0-based
    breakpoint indices (excludes the trailing end-of-series index ruptures adds).
    """
    import ruptures as rpt

    algo = rpt.Pelt(model="l2", min_size=min_size, jump=jump).fit(signal)
    breakpoints = algo.predict(pen=penalty)
    return [b for b in breakpoints if b < len(signal)]


def summarize_regimes(
    dates: pd.Series,
    values: pd.Series,
    breakpoints: list[int],
) -> pd.DataFrame:
    """Build a before/after summary table for each detected breakpoint.

    For each breakpoint, compares the mean of `values` in the segment before it
    to the mean in the segment after it (up to the next breakpoint), producing
    the "$X to $Y, a Z% change" style quantified impact statement per break.
    """
    bounds = [0] + list(breakpoints) + [len(values)]
    rows = []
    for i, bkpt in enumerate(breakpoints):
        seg_before = values.iloc[bounds[i]:bkpt]
        seg_after = values.iloc[bkpt:bounds[i + 2]]
        mean_before = seg_before.mean()
        mean_after = seg_after.mean()
        rows.append(
            {
                "breakpoint_index": bkpt,
                "date": dates.iloc[bkpt],
                "mean_before": mean_before,
                "mean_after": mean_after,
                "pct_change": (mean_after - mean_before) / mean_before * 100,
            }
        )
    return pd.DataFrame(rows)
