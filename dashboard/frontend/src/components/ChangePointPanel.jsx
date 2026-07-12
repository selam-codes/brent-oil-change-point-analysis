export default function ChangePointPanel({ changepoints }) {
  if (!changepoints) return null;

  const { covid_case_study: covid, volatility_breakpoints: volBreaks, trend_breakpoints: trendBreaks } = changepoints;

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Bayesian Change Point Analysis</h2>
      </div>

      <div className="case-study-card">
        <h3>Case study: 2020 COVID-19 demand collapse</h3>
        <p className="muted">
          Window {covid.window_start} to {covid.window_end}. PyMC single change-point model, r_hat ≈ 1.00.
        </p>
        <div className="stat-grid">
          <div>
            <div className="stat-label">Most probable change date</div>
            <div className="stat-value">{covid.change_date}</div>
          </div>
          <div>
            <div className="stat-label">94% credible interval</div>
            <div className="stat-value">
              {covid.hdi_low} – {covid.hdi_high}
            </div>
          </div>
          <div>
            <div className="stat-label">Avg. price before → after</div>
            <div className="stat-value">
              ${covid.mean_price_before.toFixed(2)} → ${covid.mean_price_after.toFixed(2)} ({covid.pct_price_change.toFixed(1)}%)
            </div>
          </div>
          <div>
            <div className="stat-label">P(mean increased after change point)</div>
            <div className="stat-value">{(covid.prob_increase * 100).toFixed(1)}%</div>
          </div>
        </div>
        {covid.matched_events?.length > 0 && (
          <p className="matched-events">
            Matched event(s): <strong>{covid.matched_events.join(", ")}</strong>
          </p>
        )}
      </div>

      <div className="breakpoint-tables">
        <div>
          <h3>Volatility-driven breaks (log returns, PELT)</h3>
          <BreakpointTable rows={volBreaks} beforeKey="avg_daily_log_return_before" afterKey="avg_daily_log_return_after" isReturn />
        </div>
        <div>
          <h3>Trend-driven breaks (price level, PELT)</h3>
          <BreakpointTable rows={trendBreaks} beforeKey="mean_before" afterKey="mean_after" />
        </div>
      </div>
    </div>
  );
}

function BreakpointTable({ rows, beforeKey, afterKey, isReturn }) {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>{isReturn ? "Avg daily return before" : "Avg price before"}</th>
            <th>{isReturn ? "Avg daily return after" : "Avg price after"}</th>
            <th>Matched event</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.date}>
              <td>{r.date}</td>
              <td>{isReturn ? r[beforeKey].toFixed(4) : `$${r[beforeKey].toFixed(2)}`}</td>
              <td>{isReturn ? r[afterKey].toFixed(4) : `$${r[afterKey].toFixed(2)}`}</td>
              <td className={r.matched_events === "no match in window" ? "muted" : ""}>{r.matched_events}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
