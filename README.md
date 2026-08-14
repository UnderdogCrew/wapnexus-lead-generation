# WapNexus Lead Generation Pipeline

Scrape local businesses by category + city, classify them with an LLM, extract
communication pain points, and generate personalized outreach drafts — FastAPI
backend + React dashboard.

See `PLAN.md` for the full phased plan and rationale.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill in GOOGLE_PLACES_API_KEY and (optional) OPENAI_API_KEY

cd frontend && npm install && cd ..
```

You need:
- A Google Cloud project with the **Places API** enabled, and an API key.
- MongoDB running (or a remote URI in `.env`).
- An OpenAI API key only if you enable AI classification / outreach drafts.

## Run

Terminal 1 — API:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Terminal 2 — UI:

```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The dashboard calls
[https://lead-api.wapnexus.com](https://lead-api.wapnexus.com/) (set `VITE_API_BASE_URL` in `frontend/.env` to override).

API docs: [https://lead-api.wapnexus.com/docs](https://lead-api.wapnexus.com/docs).

## Business search

`POST /leads/search` and the dashboard **Find businesses** button use the
**Google Places** Text Search + Details APIs.

Set `GOOGLE_PLACES_API_KEY` in `.env`.

## Dashboard wiring

| UI action | API |
|-----------|-----|
| Load list | `GET /leads` |
| **Find businesses** | `POST /leads/search` `{ category, city, max_pages, run_ai }` |
| Save status / send | `PATCH /leads/{id}` / `POST /leads/{id}/whatsapp` |

- Default search scrapes Google Places and saves leads as `status: new`.
- **Send WhatsApp message** sends the `grow_business_with_wapnexus` template to the lead's phone, with the business name in template variable `{{1}}`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/leads/search` | Scrape Google Places (+ optional AI) and upsert leads |
| `POST` | `/pipeline/run` | Full scrape → classify → pain points → outreach |
| `GET` | `/leads` | List/filter (`city`, `category`, `status`, `q`, `min_fit_score`) |
| `GET` | `/leads/{id}` | Lead detail |
| `PATCH` | `/leads/{id}` | Update status, draft, outreach_channel, email, notes |
| `DELETE` | `/leads/{id}` | Delete a lead |
| `GET` | `/health` | Health check |

### Find businesses

```bash
curl -X POST https://lead-api.wapnexus.com/leads/search \
  -H "Content-Type: application/json" \
  -d '{"category": "salons", "city": "Surat", "max_pages": 1, "run_ai": false}'
```

Valid statuses: `new`, `classified`, `drafted`, `contacted`, `responded`, `converted`, `rejected`.

## Database

```
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=wapnexus_leads
```

## Project layout

```
app/
  services/google_places_scraper.py   # Google Places search
frontend/
  src/LeadDashboard.jsx
  src/api.js
```

## Guardrails

- Respect Google Places API ToS on storing/reusing data — outreach research, not resale.
- Keep outreach volume low and personalized; review drafts before sending.
