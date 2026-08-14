import React, { useEffect, useMemo, useState } from "react";
import {
  Search, Phone, Globe, ChevronDown, Star, Mail, Loader2,
  MessageSquare, MapPin, Filter, X, ArrowUpDown, MessageCircle,
} from "lucide-react";
import { API_BASE, listLeads, searchLeads, sendWhatsApp, updateLead as patchLead } from "./api";

const STAGES = ["new", "classified", "drafted", "contacted", "responded", "converted"];

const STAGE_LABELS = {
  new: "New",
  classified: "Classified",
  drafted: "Draft Ready",
  contacted: "Contacted",
  responded: "Responded",
  converted: "Converted",
  rejected: "Rejected",
};

const STAGE_COLORS = {
  new: "#94A3B8",
  classified: "#225AD6",
  drafted: "#7C3AED",
  contacted: "#F59E0B",
  responded: "#0EA5A4",
  converted: "#11B780",
  rejected: "#94A3B8",
};

function titleCase(s) {
  return s.replace(/\b\w/g, (c) => c.toUpperCase());
}

function StageBar({ leads, activeFilter, onSelect }) {
  const counts = STAGES.map((s) => leads.filter((l) => l.status === s).length);
  const total = leads.length || 1;

  return (
    <div className="w-full">
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-slate-100">
        {STAGES.map((s, i) => (
          <div
            key={s}
            style={{ width: `${(counts[i] / total) * 100}%`, backgroundColor: STAGE_COLORS[s] }}
            className="h-full transition-all"
          />
        ))}
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        {STAGES.map((s, i) => (
          <button
            key={s}
            onClick={() => onSelect(activeFilter === s ? null : s)}
            className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium transition-colors ${
              activeFilter === s
                ? "border-transparent text-white"
                : "border-slate-200 text-slate-600 hover:border-slate-300"
            }`}
            style={activeFilter === s ? { backgroundColor: STAGE_COLORS[s] } : {}}
          >
            <span
              className="h-1.5 w-1.5 rounded-full"
              style={{ backgroundColor: activeFilter === s ? "white" : STAGE_COLORS[s] }}
            />
            {STAGE_LABELS[s]}
            <span className="tabular-nums opacity-80">{counts[i]}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function FitScoreBadge({ score }) {
  const colors = {
    5: "bg-emerald-100 text-emerald-700",
    4: "bg-emerald-50 text-emerald-600",
    3: "bg-amber-50 text-amber-700",
    2: "bg-slate-100 text-slate-500",
    1: "bg-slate-100 text-slate-400",
    0: "bg-slate-100 text-slate-400",
  };
  return (
    <div className={`flex items-center gap-1 rounded-md px-2 py-1 text-xs font-semibold ${colors[score] ?? colors[0]}`}>
      <Star size={12} className="fill-current" />
      {score > 0 ? `${score}/5` : "—"}
    </div>
  );
}

function VolumeTag({ volume }) {
  const map = {
    high: "bg-[#11B780]/10 text-[#0d8f63]",
    medium: "bg-[#225AD6]/10 text-[#225AD6]",
    low: "bg-slate-100 text-slate-500",
    unknown: "bg-slate-100 text-slate-400",
  };
  return (
    <span className={`rounded px-2 py-0.5 text-[11px] font-medium capitalize ${map[volume] ?? map.unknown}`}>
      {volume === "unknown" ? "not classified" : `${volume} volume`}
    </span>
  );
}

function WhatsAppPreview({ businessName }) {
  const name = (businessName || "").trim() || "Customer";
  const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  return (
    <div className="overflow-hidden rounded-xl border border-[#c5ddd4] shadow-sm">
      <div className="flex items-center gap-2.5 bg-[#075E54] px-3 py-2.5 text-white">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white/15">
          <MessageCircle size={15} />
        </div>
        <div className="min-w-0">
          <div className="truncate text-[13px] font-semibold">{name}</div>
          <div className="text-[11px] text-white/70">WhatsApp · template preview</div>
        </div>
      </div>
      <div
        className="px-3 py-4"
        style={{
          backgroundColor: "#EFEAE2",
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d4cdc3' fill-opacity='0.35'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
        }}
      >
        <div className="ml-auto max-w-[92%] rounded-lg rounded-tr-none bg-[#D9FDD3] px-2.5 py-2 text-[13px] leading-[1.45] text-[#111b21] shadow-sm">
          <p>Hi {name} 👋</p>
          <p className="mt-2">
            We came across your business and believe <strong>Wapnexus Business</strong> can help you
            connect with more customers and grow your brand.
          </p>
          <p className="mt-2">With Wapnexus, you can:</p>
          <p className="mt-1">✅ Send offers and updates through WhatsApp</p>
          <p>✅ Automate customer communication</p>
          <p>✅ Manage enquiries in one place</p>
          <p>✅ Build stronger customer relationships</p>
          <p>✅ Increase repeat bookings and sales</p>
          <p className="mt-2">Would you like to learn how Wapnexus can support your business?</p>
          <p className="mt-2">
            Reply <strong>YES</strong> for a quick demo.
          </p>
          <p className="mt-2">— Team Wapnexus</p>
          <p>
            🌐{" "}
            <a
              href="http://www.wapnexus.com"
              target="_blank"
              rel="noreferrer"
              className="text-[#027eb5] underline"
            >
              www.wapnexus.com
            </a>
          </p>
          <p className="mt-2 text-slate-600">Reply STOP to opt out.</p>
          <div className="mt-1 text-right text-[10px] text-slate-500">{now}</div>
        </div>
      </div>
    </div>
  );
}

function LeadRow({ lead, isOpen, onToggle, onUpdateLead }) {
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const setStatus = (status) => onUpdateLead(lead.id, { status });
  const painPoints = lead.pain_points || [];

  const handleWhatsApp = async () => {
    if (!lead.phone || sending) return;
    setSending(true);
    setError("");
    setSent(false);
    try {
      const result = await sendWhatsApp(lead.id);
      await onUpdateLead(lead.id, result.lead, { skipPatch: true });
      setSent(true);
    } catch (err) {
      setError(err.message || "WhatsApp send failed");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="border-b border-slate-100 last:border-b-0">
      <button
        onClick={onToggle}
        className="flex w-full items-center gap-4 px-4 py-3 text-left hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#225AD6]/40"
      >
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="truncate font-medium text-slate-800">{lead.name}</span>
            <span
              className="hidden shrink-0 rounded-full px-2 py-0.5 text-[11px] font-medium text-white sm:inline"
              style={{ backgroundColor: STAGE_COLORS[lead.status] || STAGE_COLORS.new }}
            >
              {STAGE_LABELS[lead.status] || lead.status}
            </span>
          </div>
          <div className="mt-0.5 flex items-center gap-1.5 text-xs text-slate-500">
            <MapPin size={11} />
            {lead.city_searched}
            <span className="text-slate-300">·</span>
            {lead.normalized_category}
          </div>
        </div>

        <VolumeTag volume={lead.messaging_volume} />
        <FitScoreBadge score={lead.fit_score} />
        <ChevronDown
          size={16}
          className={`shrink-0 text-slate-400 transition-transform ${isOpen ? "rotate-180" : ""}`}
        />
      </button>

      {isOpen && (
        <div className="border-t border-slate-100 bg-slate-50/60 px-4 py-4">
          <div className="grid gap-4 sm:grid-cols-[1fr_1.4fr]">
            <div className="space-y-3">
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">Contact</div>
                <div className="mt-1 space-y-1 text-sm text-slate-600">
                  {lead.phone && (
                    <div className="flex items-center gap-1.5"><Phone size={13} /> {lead.phone}</div>
                  )}
                  {lead.email && (
                    <div className="flex items-center gap-1.5 truncate"><Mail size={13} /> {lead.email}</div>
                  )}
                  {lead.website ? (
                    <div className="flex items-center gap-1.5 truncate"><Globe size={13} /> {lead.website}</div>
                  ) : (
                    <div className="text-slate-400">No website listed</div>
                  )}
                  <div className="text-slate-400">
                    {lead.rating ?? "—"} rating · {lead.review_count ?? 0} reviews
                  </div>
                </div>
              </div>

              <div>
                <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">Pain-point signals</div>
                {painPoints.length > 0 ? (
                  <ul className="mt-1 space-y-1 text-sm text-slate-600">
                    {painPoints.map((p, i) => (
                      <li key={i} className="flex gap-1.5">
                        <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-[#225AD6]" />
                        {p}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="mt-1 text-sm text-slate-400">No signal found yet</div>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                WhatsApp message
              </div>
              <WhatsAppPreview businessName={lead.name} />

              <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                <button
                  onClick={handleWhatsApp}
                  disabled={!lead.phone || sending}
                  title={!lead.phone ? "No phone number on file" : "Send this template to the business WhatsApp number"}
                  className="flex items-center gap-1.5 rounded-md bg-[#11B780] px-2.5 py-1.5 text-xs font-medium text-white hover:bg-[#0d8f63] disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
                >
                  {sending ? <Loader2 size={12} className="animate-spin" /> : <MessageCircle size={12} />}
                  {sending ? "Sending..." : "Send WhatsApp message"}
                </button>
                <button
                  onClick={() => setStatus("rejected")}
                  className="flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-slate-400 hover:bg-slate-100"
                >
                  <X size={12} /> Not a fit
                </button>
              </div>
              {sent && (
                <p className="text-xs text-[#0d8f63]">Template sent to {lead.phone}.</p>
              )}
              {error && <p className="text-xs text-red-600">{error}</p>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function PlaceSearchBar({ onResults }) {
  const [category, setCategory] = useState("");
  const [city, setCity] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastSearch, setLastSearch] = useState(null);
  const [error, setError] = useState("");

  const runSearch = async () => {
    if (!category.trim() || !city.trim() || loading) return;
    setLoading(true);
    setError("");
    try {
      const res = await searchLeads({
        category: category.trim(),
        city: city.trim(),
        max_pages: 1,
        run_ai: false,
      });
      onResults(res.leads || []);
      setLastSearch({
        category: titleCase(category.trim()),
        city: titleCase(city.trim()),
        count: res.count ?? (res.leads || []).length,
      });
    } catch (err) {
      setError(err.message || "Search failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-5 rounded-xl border border-slate-100 bg-slate-50/60 p-4">
      <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">Find new businesses</div>
      <div className="mt-2 flex flex-wrap items-center gap-2">
        <input
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && runSearch()}
          placeholder="Category — e.g. salons, real estate agents"
          className="min-w-[200px] flex-1 rounded-md border border-slate-200 bg-white py-1.5 px-3 text-sm focus:border-[#225AD6] focus:outline-none focus:ring-1 focus:ring-[#225AD6]/30"
        />
        <div className="relative min-w-[160px] flex-1">
          <MapPin size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={city}
            onChange={(e) => setCity(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && runSearch()}
            placeholder="City — e.g. Surat"
            className="w-full rounded-md border border-slate-200 bg-white py-1.5 pl-8 pr-3 text-sm focus:border-[#225AD6] focus:outline-none focus:ring-1 focus:ring-[#225AD6]/30"
          />
        </div>
        <button
          onClick={runSearch}
          disabled={!category.trim() || !city.trim() || loading}
          className="flex items-center gap-1.5 rounded-md bg-[#225AD6] px-3 py-1.5 text-sm font-medium text-white hover:bg-[#1b48b0] disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
        >
          {loading ? <Loader2 size={14} className="animate-spin" /> : <Search size={14} />}
          {loading ? "Searching..." : "Find businesses"}
        </button>
      </div>
      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
      <p className="mt-2 text-[11px] text-slate-400">
        {lastSearch
          ? `Added ${lastSearch.count} leads for "${lastSearch.category}" in ${lastSearch.city}.`
          : `Calls POST ${API_BASE}/leads/search`}
      </p>
    </div>
  );
}

export default function LeadDashboard() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [query, setQuery] = useState("");
  const [city, setCity] = useState("all");
  const [category, setCategory] = useState("all");
  const [minFit, setMinFit] = useState(0);
  const [stageFilter, setStageFilter] = useState(null);
  const [openId, setOpenId] = useState(null);
  const [sortDesc, setSortDesc] = useState(true);

  const refreshLeads = async () => {
    const res = await listLeads();
    setLeads(res.leads || []);
  };

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setLoadError("");
      try {
        const res = await listLeads();
        if (!cancelled) setLeads(res.leads || []);
      } catch (err) {
        if (!cancelled) setLoadError(err.message || "Failed to load leads");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const cities = useMemo(() => ["all", ...new Set(leads.map((l) => l.city_searched).filter(Boolean))], [leads]);
  const categories = useMemo(
    () => ["all", ...new Set(leads.map((l) => l.normalized_category).filter(Boolean))],
    [leads],
  );

  const updateLead = async (id, patch, options = {}) => {
    setLeads((prev) => prev.map((l) => (l.id === id ? { ...l, ...patch } : l)));
    if (options.skipPatch) return;
    try {
      const updated = await patchLead(id, patch);
      setLeads((prev) => prev.map((l) => (l.id === id ? updated : l)));
    } catch (err) {
      await refreshLeads();
      throw err;
    }
  };

  const addSearchResults = (results) => {
    setLeads((prev) => {
      const existing = new Set(prev.map((l) => l.id));
      const fresh = results.filter((r) => !existing.has(r.id));
      return [...fresh, ...prev];
    });
    setStageFilter("new");
  };

  const filtered = useMemo(() => {
    let result = leads.filter((l) => {
      if (city !== "all" && l.city_searched !== city) return false;
      if (category !== "all" && l.normalized_category !== category) return false;
      if ((l.fit_score || 0) < minFit) return false;
      if (stageFilter && l.status !== stageFilter) return false;
      if (query && !(l.name || "").toLowerCase().includes(query.toLowerCase())) return false;
      return true;
    });
    result.sort((a, b) => (sortDesc ? (b.fit_score || 0) - (a.fit_score || 0) : (a.fit_score || 0) - (b.fit_score || 0)));
    return result;
  }, [leads, city, category, minFit, stageFilter, query, sortDesc]);

  const avgFit = leads.length
    ? (leads.reduce((sum, l) => sum + (l.fit_score || 0), 0) / leads.length).toFixed(1)
    : "0.0";

  return (
    <div className="min-h-full w-full bg-white font-sans text-slate-800" style={{ fontFamily: "'Segoe UI', 'Helvetica Neue', Arial, sans-serif" }}>
      <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6">
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#11B780]">
                <MessageSquare size={15} className="text-white" />
              </div>
              <h1 className="text-lg font-bold text-slate-900">WapNexus Lead Pipeline</h1>
            </div>
            <p className="mt-1 text-sm text-slate-500">
              Businesses scraped, scored, and drafted for WhatsApp API outreach.
            </p>
          </div>
          <div className="flex shrink-0 gap-4 text-right">
            <div>
              <div className="text-xl font-bold text-slate-900">{leads.length}</div>
              <div className="text-[11px] text-slate-400">total leads</div>
            </div>
            <div>
              <div className="text-xl font-bold text-[#11B780]">{avgFit}</div>
              <div className="text-[11px] text-slate-400">avg fit score</div>
            </div>
          </div>
        </div>

        <PlaceSearchBar onResults={addSearchResults} />

        <div className="mb-5 rounded-xl border border-slate-100 p-4">
          <StageBar leads={leads} activeFilter={stageFilter} onSelect={setStageFilter} />
        </div>

        <div className="mb-4 flex flex-wrap items-center gap-2">
          <div className="relative flex-1 min-w-[160px]">
            <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by name..."
              className="w-full rounded-md border border-slate-200 py-1.5 pl-8 pr-3 text-sm focus:border-[#225AD6] focus:outline-none focus:ring-1 focus:ring-[#225AD6]/30"
            />
          </div>

          <select
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="rounded-md border border-slate-200 py-1.5 px-2 text-sm text-slate-600 focus:border-[#225AD6] focus:outline-none"
          >
            {cities.map((c) => (
              <option key={c} value={c}>{c === "all" ? "All cities" : c}</option>
            ))}
          </select>

          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="rounded-md border border-slate-200 py-1.5 px-2 text-sm text-slate-600 focus:border-[#225AD6] focus:outline-none"
          >
            {categories.map((c) => (
              <option key={c} value={c}>{c === "all" ? "All categories" : c}</option>
            ))}
          </select>

          <select
            value={minFit}
            onChange={(e) => setMinFit(Number(e.target.value))}
            className="flex items-center rounded-md border border-slate-200 py-1.5 px-2 text-sm text-slate-600 focus:border-[#225AD6] focus:outline-none"
          >
            <option value={0}>Any fit score</option>
            <option value={3}>Fit score 3+</option>
            <option value={4}>Fit score 4+</option>
            <option value={5}>Fit score 5</option>
          </select>

          <button
            onClick={() => setSortDesc((s) => !s)}
            className="flex items-center gap-1 rounded-md border border-slate-200 px-2.5 py-1.5 text-sm text-slate-600 hover:bg-slate-50"
            title="Toggle sort order"
          >
            <ArrowUpDown size={13} />
          </button>

          {(city !== "all" || category !== "all" || minFit > 0 || stageFilter || query) && (
            <button
              onClick={() => { setCity("all"); setCategory("all"); setMinFit(0); setStageFilter(null); setQuery(""); }}
              className="flex items-center gap-1 rounded-md px-2 py-1.5 text-sm text-slate-400 hover:text-slate-600"
            >
              <X size={13} /> Clear
            </button>
          )}
        </div>

        <div className="mb-2 flex items-center gap-1.5 text-xs text-slate-400">
          <Filter size={12} /> Showing {filtered.length} of {leads.length} leads
        </div>

        <div className="overflow-hidden rounded-xl border border-slate-100">
          {loading ? (
            <div className="flex items-center justify-center gap-2 px-4 py-10 text-sm text-slate-400">
              <Loader2 size={16} className="animate-spin" /> Loading leads…
            </div>
          ) : loadError ? (
            <div className="px-4 py-10 text-center text-sm text-red-600">{loadError}</div>
          ) : filtered.length > 0 ? (
            filtered.map((lead) => (
              <LeadRow
                key={lead.id}
                lead={lead}
                isOpen={openId === lead.id}
                onToggle={() => setOpenId(openId === lead.id ? null : lead.id)}
                onUpdateLead={updateLead}
              />
            ))
          ) : (
            <div className="px-4 py-10 text-center text-sm text-slate-400">
              No leads match these filters. Try widening your search.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
