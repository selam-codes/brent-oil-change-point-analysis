import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dashboard" / "backend"))

from app import app  # noqa: E402


def client():
    app.testing = True
    return app.test_client()


def test_health_ok():
    resp = client().get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_prices_returns_records_and_respects_date_filter():
    c = client()
    resp = c.get("/api/prices?start=2020-01-01&end=2020-01-10")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] > 0
    assert all("2020-01-01" <= row["Date"] <= "2020-01-10" for row in data["prices"])


def test_prices_unfiltered_is_strictly_valid_json():
    # The unfiltered series includes the first row, whose log_return/rolling
    # volatility are NaN. Flask's own test client tolerates a literal `NaN`
    # token, but browsers' JSON.parse does not - so this must use the
    # stdlib's strict decoder (parse_constant=None disables NaN/Infinity).
    resp = client().get("/api/prices")
    assert resp.status_code == 200
    json.loads(resp.data, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"non-JSON constant: {x}")))


def test_events_category_filter():
    c = client()
    resp = c.get("/api/events?category=OPEC")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] > 0
    assert all("opec" in row["category"].lower() for row in data["events"])


def test_changepoints_has_expected_keys():
    resp = client().get("/api/changepoints")
    assert resp.status_code == 200
    data = resp.get_json()
    assert {"full_series_model", "covid_case_study", "volatility_breakpoints", "trend_breakpoints"} <= data.keys()


def test_summary_has_expected_shape():
    resp = client().get("/api/summary")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "price_stats" in data
    assert data["n_observations"] > 9000
