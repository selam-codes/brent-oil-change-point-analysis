export default function SummaryTiles({ summary }) {
  if (!summary) return null;

  const tiles = [
    { label: "Date range", value: `${summary.date_range.start} → ${summary.date_range.end}` },
    { label: "Observations", value: summary.n_observations.toLocaleString() },
    { label: "Mean price", value: `$${summary.price_stats.mean.toFixed(2)}` },
    { label: "Price range", value: `$${summary.price_stats.min.toFixed(2)} – $${summary.price_stats.max.toFixed(2)}` },
    { label: "Key events tracked", value: summary.n_events },
    {
      label: "Detected change points",
      value: `${summary.n_volatility_breakpoints} volatility / ${summary.n_trend_breakpoints} trend`,
    },
  ];

  return (
    <div className="tile-row">
      {tiles.map((t) => (
        <div className="tile" key={t.label}>
          <div className="tile-label">{t.label}</div>
          <div className="tile-value">{t.value}</div>
        </div>
      ))}
    </div>
  );
}
