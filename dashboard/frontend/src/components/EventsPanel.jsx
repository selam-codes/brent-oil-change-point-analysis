import { useMemo, useState } from "react";

export default function EventsPanel({ events, onSelectEvent }) {
  const [query, setQuery] = useState("");

  const categories = useMemo(() => {
    const set = new Set(events.map((e) => e.category));
    return ["All", ...Array.from(set)];
  }, [events]);
  const [category, setCategory] = useState("All");

  const filtered = useMemo(() => {
    return events.filter((e) => {
      const matchesCategory = category === "All" || e.category === category;
      const matchesQuery = query.trim() === "" || e.event_name.toLowerCase().includes(query.toLowerCase());
      return matchesCategory && matchesQuery;
    });
  }, [events, category, query]);

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Key Oil-Market Events</h2>
      </div>
      <div className="filter-row">
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <input
          type="search"
          placeholder="Search events…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      <div className="events-list">
        {filtered.map((e) => (
          <button className="event-row" key={e.event_id} onClick={() => onSelectEvent(e)}>
            <span className={`impact-dot ${e.expected_price_impact === "Increase" ? "good" : "critical"}`} />
            <span className="event-date">{e.date}</span>
            <span className="event-name">{e.event_name}</span>
            <span className="event-category muted">{e.category}</span>
          </button>
        ))}
        {filtered.length === 0 && <p className="muted">No events match this filter.</p>}
      </div>
    </div>
  );
}
