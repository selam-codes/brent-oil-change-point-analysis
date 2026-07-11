# Brent Oil Change Point Analysis

Bayesian change point analysis of Brent crude oil prices (1987–2022), linking detected
structural breaks to major geopolitical events, OPEC decisions, and economic shocks —
10 Academy KAIM 9, Week 10 Challenge, for Birhan Energies.

## Project Structure

```
├── .vscode/settings.json
├── .github/workflows/unittests.yml
├── requirements.txt
├── src/                 # reusable analysis code (data loading, change point model, metrics)
├── notebooks/           # EDA and Bayesian change point modeling notebooks
├── tests/               # unit tests
├── scripts/             # CLI utilities for reproducing analysis steps
├── data/
│   ├── raw/             # BrentOilPrices.csv (not committed if large) + key_events.csv
│   └── processed/       # cleaned/derived series (log returns, etc.)
├── reports/             # interim/final written reports and figures
└── dashboard/           # Flask API (backend) + React app (frontend) — Task 3
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data

Place the raw daily Brent price series at `data/raw/BrentOilPrices.csv` with columns
`Date` (`day-month-year`, e.g. `20-May-87`) and `Price` (USD/barrel). The curated list of
major oil-market events used for change-point association lives at
`data/raw/key_events.csv`.

## Status

- **Task 1 (interim):** complete — see `reports/interim_report.md` for the planned
  workflow, the key events dataset, documented assumptions/limitations, and initial EDA
  findings (`notebooks/1.0-eda.ipynb`, figures in `reports/figures/`).
- **Task 2:** Bayesian PyMC change point model — planned next.
- **Task 3:** Flask + React dashboard — planned (`dashboard/`).

## Running Tests

```bash
pytest tests/ -v
```
