import { useMemo, useState } from "react";
import {
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  Tooltip,
  XAxis,
  YAxis,
  Brush,
} from "recharts";

const PRESETS = [
  { label: "Full history", start: "1987-05-20", end: "2022-11-14" },
  { label: "2008 financial crisis", start: "2007-06-01", end: "2009-12-31" },
  { label: "2014–2016 OPEC collapse", start: "2014-01-01", end: "2016-12-31" },
  { label: "2020 COVID-19 shock", start: "2020-01-01", end: "2020-12-31" },
  { label: "2022 Russia–Ukraine", start: "2021-06-01", end: "2022-11-14" },
];

const DATE_FMT = new Intl.DateTimeFormat("en-US", { year: "numeric", month: "short", day: "2-digit" });
const TICK_FMT = new Intl.DateTimeFormat("en-US", { year: "numeric", month: "short" });

function toTime(dateStr) {
  return new Date(dateStr).getTime();
}

function nearestRow(rows, targetTime) {
  let best = null;
  let bestDiff = Infinity;
  for (const row of rows) {
    const diff = Math.abs(row.t - targetTime);
    if (diff < bestDiff) {
      bestDiff = diff;
      best = row;
    }
  }
  return best;
}

function EventDot(props) {
  const { cx, cy, payload } = props;
  if (cx == null || cy == null) return null;
  const isIncrease = payload.expected_price_impact === "Increase";
  const color = isIncrease ? "var(--status-good)" : "var(--status-critical)";
  const path = isIncrease
    ? `M ${cx} ${cy - 6} L ${cx + 6} ${cy + 5} L ${cx - 6} ${cy + 5} Z`
    : `M ${cx} ${cy + 6} L ${cx + 6} ${cy - 5} L ${cx - 6} ${cy - 5} Z`;
  return <path d={path} fill={color} stroke="var(--surface-1)" strokeWidth={1} />;
}

function ChartTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;
  const pricePoint = payload.find((p) => p.dataKey === "Price" && !p.payload.event_name);
  const eventPoint = payload.find((p) => p.payload.event_name);
  const anyPoint = pricePoint ?? payload[0];
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-date">{DATE_FMT.format(new Date(anyPoint.payload.t))}</div>
      {pricePoint && <div>Price: ${Number(pricePoint.value).toFixed(2)}</div>}
      {eventPoint?.payload?.event_name && (
        <div className="chart-tooltip-event">
          <strong>{eventPoint.payload.event_name}</strong>
          <div>{eventPoint.payload.category}</div>
        </div>
      )}
    </div>
  );
}

export default function PriceChart({ prices, events, trendBreakpoints, onRangeChange, loading }) {
  const [showEvents, setShowEvents] = useState(true);
  const [showBreakpoints, setShowBreakpoints] = useState(true);
  const [activePreset, setActivePreset] = useState("Full history");

  const chartData = useMemo(
    () => (prices ?? []).map((p) => ({ ...p, t: toTime(p.Date) })),
    [prices]
  );

  const eventMarkers = useMemo(() => {
    if (!showEvents || !chartData.length || !events?.length) return [];
    const start = chartData[0].t;
    const end = chartData[chartData.length - 1].t;
    return events
      .filter((e) => {
        const t = toTime(e.date);
        return t >= start && t <= end;
      })
      .map((e) => {
        const row = nearestRow(chartData, toTime(e.date));
        return { ...row, event_name: e.event_name, category: e.category, expected_price_impact: e.expected_price_impact };
      });
  }, [chartData, events, showEvents]);

  const visibleBreakpoints = useMemo(() => {
    if (!showBreakpoints || !chartData.length || !trendBreakpoints?.length) return [];
    const start = chartData[0].t;
    const end = chartData[chartData.length - 1].t;
    return trendBreakpoints
      .map((b) => ({ ...b, t: toTime(b.date) }))
      .filter((b) => b.t >= start && b.t <= end);
  }, [chartData, trendBreakpoints, showBreakpoints]);

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Brent Crude Price</h2>
        <div className="chart-legend">
          <span className="legend-item">
            <span className="legend-swatch" style={{ background: "var(--series-1)" }} />
            Price (USD/barrel)
          </span>
          <span className="legend-item">
            <span className="legend-icon" style={{ color: "var(--status-good)" }}>▲</span>
            Event: expected increase
          </span>
          <span className="legend-item">
            <span className="legend-icon" style={{ color: "var(--status-critical)" }}>▼</span>
            Event: expected decrease
          </span>
        </div>
      </div>

      <div className="filter-row">
        {PRESETS.map((p) => (
          <button
            key={p.label}
            className={`preset-btn ${activePreset === p.label ? "active" : ""}`}
            onClick={() => {
              setActivePreset(p.label);
              onRangeChange(p.start, p.end);
            }}
          >
            {p.label}
          </button>
        ))}
        <label className="toggle">
          <input type="checkbox" checked={showEvents} onChange={(e) => setShowEvents(e.target.checked)} />
          Highlight events
        </label>
        <label className="toggle">
          <input type="checkbox" checked={showBreakpoints} onChange={(e) => setShowBreakpoints(e.target.checked)} />
          Show trend breakpoints
        </label>
      </div>

      {loading ? (
        <div className="chart-loading">Loading price series…</div>
      ) : (
        <ResponsiveContainer width="100%" height={420}>
          <ComposedChart data={chartData} margin={{ top: 8, right: 24, bottom: 8, left: 0 }}>
            <CartesianGrid stroke="var(--gridline)" vertical={false} />
            <XAxis
              dataKey="t"
              type="number"
              scale="time"
              domain={["dataMin", "dataMax"]}
              tickFormatter={(t) => TICK_FMT.format(new Date(t))}
              tick={{ fill: "var(--text-muted)", fontSize: 12 }}
              stroke="var(--axis)"
              minTickGap={50}
            />
            <YAxis
              tick={{ fill: "var(--text-muted)", fontSize: 12 }}
              stroke="var(--axis)"
              width={56}
              label={{ value: "USD/barrel", angle: -90, position: "insideLeft", fill: "var(--text-muted)", fontSize: 12 }}
            />
            <Tooltip content={<ChartTooltip />} />
            {visibleBreakpoints.map((b) => (
              <ReferenceLine key={b.date} x={b.t} stroke="var(--breakpoint-line)" strokeDasharray="4 4" />
            ))}
            <Line type="monotone" dataKey="Price" stroke="var(--series-1)" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Scatter data={eventMarkers} dataKey="Price" shape={<EventDot />} isAnimationActive={false} />
            <Brush
              dataKey="t"
              height={24}
              stroke="var(--axis)"
              travellerWidth={8}
              tickFormatter={(t) => TICK_FMT.format(new Date(t))}
            />
          </ComposedChart>
        </ResponsiveContainer>
      )}

      <div className="date-range-form">
        <label>
          Start
          <input
            type="date"
            defaultValue={PRESETS[0].start}
            onChange={(e) => onRangeChange(e.target.value, undefined)}
          />
        </label>
        <label>
          End
          <input
            type="date"
            defaultValue={PRESETS[0].end}
            onChange={(e) => onRangeChange(undefined, e.target.value)}
          />
        </label>
      </div>
    </div>
  );
}
