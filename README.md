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
│   └── processed/       # cleaned/derived series, changepoint_results.json
├── reports/             # interim/final written reports (.md + .pdf) and figures
└── dashboard/
    ├── backend/         # Flask API (Task 3)
    └── frontend/        # React + Recharts dashboard (Task 3)
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

- **Task 1:** complete — see `reports/interim_report.md` / `.pdf` for the planned
  workflow, the key events dataset, documented assumptions/limitations, and initial EDA
  findings (`notebooks/1.0-eda.ipynb`, figures in `reports/figures/`).
- **Task 2:** complete — see `notebooks/2.0-change-point-model.ipynb` for the Bayesian
  PyMC change point model (full-series run + a windowed 2020 COVID-19 case study) and a
  PELT multi-change-point robustness check. Reusable model code in
  `src/change_point_model.py`. Results are exported to
  `data/processed/changepoint_results.json` for the dashboard.
- **Task 3:** complete — Flask API (`dashboard/backend/`) + React dashboard
  (`dashboard/frontend/`), see below.
- **Final report:** `reports/final_report.md` / `.pdf` — full methodology, quantified
  impacts, dashboard screenshots, limitations and future work.

## Running Tests

```bash
pytest tests/ -v
```

## Running the Dashboard (Task 3)

Two processes, run from the project root:

```bash
# 1. Backend API (Flask, port 5001) — serves precomputed results, no live MCMC sampling
source .venv/bin/activate
python dashboard/backend/app.py

# 2. Frontend (React + Vite, port 5173) — proxies /api/* to the backend above
cd dashboard/frontend
npm install   # first time only
npm run dev
```

Then open `http://localhost:5173`. API endpoints (see `dashboard/backend/app.py`):

| Endpoint | Purpose |
|---|---|
| `GET /api/prices?start=&end=` | Historical daily price series, optionally date-filtered |
| `GET /api/events?category=` | The 17 key events, optionally filtered by category |
| `GET /api/changepoints` | Bayesian + PELT change point results from Task 2 |
| `GET /api/summary` | Overview stats for the dashboard's summary tiles |
