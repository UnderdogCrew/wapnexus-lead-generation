# WapNexus Lead Generation Pipeline — Plan

## Goal
Find local businesses that would benefit from the WhatsApp Business API and generate
personalized outreach for each one, using scraping + AI, on a repeatable schedule.

## Phases

### Phase 1 — Data Collection (Week 1)
- Build Google Places scraper: pull businesses by category + city (e.g. "salons in Surat").
- Fields captured: name, address, phone, website, category, rating, review count.
- Store results in MongoDB (`leads` collection), keyed by Google `place_id`.
- Add a Justdial/IndiaMart scraper later if Google Places coverage is thin for a category.

### Phase 2 — AI Classification (Week 1–2)
- For each raw lead, run an LLM classification chain that returns structured JSON:
  - normalized category
  - estimated messaging volume (high/medium/low)
  - already using WhatsApp/chat automation? (true/false/unknown)
  - lead fit score (1–5)
- Store results in a `ClassifiedLead` table linked to the raw lead.

### Phase 3 — Pain-Point Extraction (Week 2)
- Scrape last 10–20 Google reviews per lead.
- Run an LLM extraction chain over reviews + website copy to pull out concrete pain
  points (slow replies, no booking system, manual order confirmation, etc).
- Store as a list of short strings per lead — these become outreach hooks.

### Phase 4 — Outreach Draft Generation (Week 2–3)
- For leads with fit score ≥ 3, generate a short personalized WhatsApp/email pitch
  referencing their specific pain point.
- Drafts go into a review queue — you approve/edit before sending (important early on,
  both for quality and to avoid WhatsApp spam flags).

### Phase 5 — Pipeline Orchestration (Week 3)
- Wire it together behind `POST /pipeline/run` in FastAPI.
- Add Celery (or a background task queue) later for scheduling once the manual flow is validated.

### Phase 6 — Tracking Dashboard (Week 3–4)
- Beanie `Lead` document in MongoDB + REST endpoints: lead status (new → classified →
  drafted → contacted → responded → converted).
- Filter by city, category, fit score via `GET /leads`.

## Artifacts in this package
- `PLAN.md` — this file
- `requirements.txt` — Python dependencies
- `.env.example` — required API keys/config
- `app/main.py` — FastAPI entrypoint
- `app/services/google_places_scraper.py` — Phase 1
- `app/services/lead_classifier.py` — Phase 2
- `app/services/pain_point_extractor.py` — Phase 3
- `app/services/outreach_generator.py` — Phase 4
- `app/services/pipeline.py` — Phase 5 orchestration
- `app/models.py` — Phase 6 data model (Beanie / MongoDB)
- `app/api/routes/` — pipeline + leads HTTP API
- `README.md` — setup and run instructions

## Notes / Guardrails
- Google Places API has usage costs and ToS limits on storing/reusing certain fields —
  use for outreach research, not resale.
- Keep early outreach volume low and personalized; WhatsApp restricts accounts that
  send templated bulk messages flagged as spam.
- Human review step before any message is actually sent, at least for the first few
  batches.
