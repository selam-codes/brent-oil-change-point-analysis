"""Flask API serving Brent oil price, event, and change point results (Task 3).

Data is precomputed by the Task 1/2 notebooks (data/processed/, data/raw/) and
loaded once at startup — this API only serves results, it does not re-run any
EDA or MCMC sampling on request.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DATA_RAW = BASE_DIR / "data" / "raw"

app = Flask(__name__)
CORS(app)

_prices_df = pd.read_csv(DATA_PROCESSED / "brent_prices_clean.csv", parse_dates=["Date"])
_events_df = pd.read_csv(DATA_RAW / "key_events.csv", parse_dates=["date"])
_changepoints = json.loads((DATA_PROCESSED / "changepoint_results.json").read_text())


def _parse_date_arg(name: str) -> pd.Timestamp | None:
    value = request.args.get(name)
    return pd.to_datetime(value) if value else None


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/prices")
def get_prices():
    """Historical daily price series, optionally filtered by ?start=&end= (YYYY-MM-DD)."""
    start = _parse_date_arg("start")
    end = _parse_date_arg("end")

    df = _prices_df
    if start is not None:
        df = df[df["Date"] >= start]
    if end is not None:
        df = df[df["Date"] <= end]

    df = df.assign(Date=df["Date"].dt.strftime("%Y-%m-%d"))
    df = df.astype(object).where(pd.notnull(df), None)
    records = df.to_dict(orient="records")
    return jsonify({"count": len(records), "prices": records})


@app.get("/api/events")
def get_events():
    """The curated key-events dataset, optionally filtered by ?category=."""
    df = _events_df
    category = request.args.get("category")
    if category:
        df = df[df["category"].str.contains(category, case=False, na=False)]

    records = df.assign(date=df["date"].dt.strftime("%Y-%m-%d")).to_dict(orient="records")
    return jsonify({"count": len(records), "events": records})


@app.get("/api/changepoints")
def get_changepoints():
    """Precomputed Bayesian + PELT change point results (Task 2 notebook output)."""
    return jsonify(_changepoints)


@app.get("/api/summary")
def get_summary():
    """Top-line stats for dashboard overview tiles."""
    price_col = _prices_df["Price"]
    return jsonify(
        {
            "date_range": {
                "start": _prices_df["Date"].min().strftime("%Y-%m-%d"),
                "end": _prices_df["Date"].max().strftime("%Y-%m-%d"),
            },
            "n_observations": int(len(_prices_df)),
            "price_stats": {
                "mean": round(float(price_col.mean()), 2),
                "min": round(float(price_col.min()), 2),
                "max": round(float(price_col.max()), 2),
                "std": round(float(price_col.std()), 2),
            },
            "n_events": int(len(_events_df)),
            "n_volatility_breakpoints": len(_changepoints["volatility_breakpoints"]),
            "n_trend_breakpoints": len(_changepoints["trend_breakpoints"]),
            "covid_case_study_change_date": _changepoints["covid_case_study"]["change_date"],
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
