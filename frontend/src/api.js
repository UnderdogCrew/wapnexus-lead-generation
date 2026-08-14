const API_BASE = (
  import.meta.env.VITE_API_BASE_URL || "https://lead-api.wapnexus.com"
).replace(/\/$/, "");

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 204) return null;

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data.detail || data.message || res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

export function listLeads(params = {}) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "" && value !== "all") {
      qs.set(key, value);
    }
  });
  const query = qs.toString();
  return request(`/leads${query ? `?${query}` : ""}`);
}

export function searchLeads({ category, city, max_pages = 1, run_ai = false }) {
  return request("/leads/search", {
    method: "POST",
    body: JSON.stringify({ category, city, max_pages, run_ai }),
  });
}

export function updateLead(id, patch) {
  return request(`/leads/${id}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export function sendWhatsApp(id) {
  return request(`/leads/${id}/whatsapp`, { method: "POST" });
}

export function deleteLead(id) {
  return request(`/leads/${id}`, { method: "DELETE" });
}

export { API_BASE };
