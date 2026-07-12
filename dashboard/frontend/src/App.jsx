import { useEffect, useState } from "react";
import "./theme.css";
import "./App.css";
import { getChangepoints, getEvents, getPrices, getSummary } from "./api";
import SummaryTiles from "./components/SummaryTiles";
import PriceChart from "./components/PriceChart";
import ChangePointPanel from "./components/ChangePointPanel";
import EventsPanel from "./components/EventsPanel";

const FULL_START = "1987-05-20";
const FULL_END = "2022-11-14";

function shiftDate(dateStr, days) {
  const d = new Date(dateStr);
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

export default function App() {
  const [summary, setSummary] = useState(null);
  const [events, setEvents] = useState([]);
  const [changepoints, setChangepoints] = useState(null);
  const [prices, setPrices] = useState([]);
  const [range, setRange] = useState({ start: FULL_START, end: FULL_END });
  const [loadingPrices, setLoadingPrices] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getSummary().then(setSummary).catch((e) => setError(e.message));
    getEvents().then((d) => setEvents(d.events)).catch((e) => setError(e.message));
    getChangepoints().then(setChangepoints).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    setLoadingPrices(true);
    getPrices(range.start, range.end)
      .then((d) => setPrices(d.prices))
      .catch((e) => setError(e.message))
      .finally(() => setLoadingPrices(false));
  }, [range]);

  const handleRangeChange = (start, end) => {
    setRange((prev) => ({ start: start ?? prev.start, end: end ?? prev.end }));
  };

  const handleSelectEvent = (event) => {
    setRange({ start: shiftDate(event.date, -180), end: shiftDate(event.date, 180) });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>Birhan Energies — Brent Oil Change Point Dashboard</h1>
          <p className="muted">
            Bayesian &amp; PELT change point analysis of Brent crude prices (1987–2022), linked to major
            geopolitical, OPEC, and macroeconomic events. 10 Academy KAIM 9 — Week 10 Challenge.
          </p>
        </div>
      </header>

      {error && <div className="error-banner">Failed to load dashboard data: {error}</div>}

      <SummaryTiles summary={summary} />

      <PriceChart
        prices={prices}
        events={events}
        trendBreakpoints={changepoints?.trend_breakpoints ?? []}
        onRangeChange={handleRangeChange}
        loading={loadingPrices}
      />

      <div className="two-col">
        <ChangePointPanel changepoints={changepoints} />
        <EventsPanel events={events} onSelectEvent={handleSelectEvent} />
      </div>

      <footer className="app-footer muted">
        Data: BrentOilPrices.csv (1987-05-20 to 2022-11-14) · Change points computed in{" "}
        <code>notebooks/2.0-change-point-model.ipynb</code> · Served by the Flask API in{" "}
        <code>dashboard/backend</code>.
      </footer>
    </div>
  );
}
