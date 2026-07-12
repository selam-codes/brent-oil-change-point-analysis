const BASE = "/api";

async function fetchJSON(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    throw new Error(`API error ${res.status} on ${path}`);
  }
  return res.json();
}

export const getSummary = () => fetchJSON("/summary");

export const getPrices = (start, end) => {
  const params = new URLSearchParams();
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  const qs = params.toString();
  return fetchJSON(`/prices${qs ? `?${qs}` : ""}`);
};

export const getEvents = (category) =>
  fetchJSON(`/events${category ? `?category=${encodeURIComponent(category)}` : ""}`);

export const getChangepoints = () => fetchJSON("/changepoints");
