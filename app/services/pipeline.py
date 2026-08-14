"""Phase 5 — Pipeline orchestration."""

from datetime import datetime, timezone
from typing import Any

from app.models import Lead, LeadStatus
from app.services.google_places_scraper import collect_leads
from app.services.lead_classifier import classify_leads_batch
from app.services.outreach_generator import generate_drafts_for_leads
from app.services.pain_point_extractor import extract_pain_points


def run_pipeline(category: str, city: str, min_fit_score: int = 3, max_pages: int = 3) -> list[dict[str, Any]]:
    raw_leads = collect_leads(category, city, max_pages=max_pages)
    classified = classify_leads_batch(raw_leads)
    classified_by_place_id = {c["place_id"]: c for c in classified}

    merged_leads: list[dict[str, Any]] = []
    for lead in raw_leads:
        classification = classified_by_place_id.get(lead["place_id"], {})
        # Wire Google Places reviews into extract_pain_points when DETAIL_FIELDS includes "reviews".
        pain_point_result = extract_pain_points(lead["name"], reviews=[])
        merged = {**lead, **classification, **pain_point_result}
        merged_leads.append(merged)

    drafts = generate_drafts_for_leads(merged_leads, min_fit_score=min_fit_score)
    draft_by_place_id = {d["place_id"]: d["draft_message"] for d in drafts}

    for lead in merged_leads:
        lead["draft_message"] = draft_by_place_id.get(lead["place_id"])

    return merged_leads


def _status_for_lead(lead: dict[str, Any], min_fit_score: int) -> str:
    if lead.get("draft_message"):
        return LeadStatus.DRAFTED.value
    if lead.get("fit_score", 0) > 0:
        return LeadStatus.CLASSIFIED.value
    return LeadStatus.NEW.value


def _normalize_automation(value: Any) -> str | None:
    if isinstance(value, bool):
        return str(value).lower()
    return value


async def persist_leads(leads: list[dict[str, Any]], min_fit_score: int = 3) -> list[Lead]:
    saved: list[Lead] = []
    now = datetime.now(timezone.utc)

    for data in leads:
        place_id = data.get("place_id")
        if not place_id:
            continue

        fields = {
            "name": data.get("name") or "Unknown",
            "address": data.get("address"),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "website": data.get("website"),
            "rating": data.get("rating"),
            "review_count": data.get("review_count"),
            "category_searched": data.get("category_searched") or "",
            "city_searched": data.get("city_searched") or "",
            "google_types": data.get("google_types"),
            "business_status": data.get("business_status"),
            "normalized_category": data.get("normalized_category"),
            "messaging_volume": data.get("messaging_volume") or "unknown",
            "already_using_chat_automation": _normalize_automation(data.get("already_using_chat_automation")),
            "fit_score": int(data.get("fit_score") or 0),
            "classification_reasoning": data.get("classification_reasoning"),
            "pain_points": data.get("pain_points") or [],
            "has_signal": data.get("has_signal"),
            "draft_message": data.get("draft_message") or "",
            "status": data.get("status") or _status_for_lead(data, min_fit_score),
            "updated_at": now,
        }

        existing = await Lead.find_one(Lead.place_id == place_id)
        if existing:
            await existing.set(fields)
            saved.append(existing)
        else:
            lead = Lead(place_id=place_id, created_at=now, **fields)
            await lead.insert()
            saved.append(lead)

    return saved


async def search_and_persist_raw(
    raw_leads: list[dict[str, Any]],
    category: str,
    city: str,
) -> list[Lead]:
    """Persist scraped Google Places results as new leads (UI Find businesses)."""
    now = datetime.now(timezone.utc)
    saved: list[Lead] = []

    for data in raw_leads:
        place_id = data.get("place_id")
        if not place_id:
            continue

        scrape_fields = {
            "name": data.get("name") or "Unknown",
            "address": data.get("address"),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "website": data.get("website"),
            "rating": data.get("rating"),
            "review_count": data.get("review_count"),
            "category_searched": data.get("category_searched") or category,
            "city_searched": data.get("city_searched") or city,
            "google_types": data.get("google_types"),
            "business_status": data.get("business_status"),
            "updated_at": now,
        }

        existing = await Lead.find_one(Lead.place_id == place_id)
        if existing:
            await existing.set(scrape_fields)
            saved.append(existing)
        else:
            lead = Lead(
                place_id=place_id,
                created_at=now,
                messaging_volume="unknown",
                already_using_chat_automation="unknown",
                fit_score=0,
                pain_points=[],
                draft_message="",
                status=LeadStatus.NEW.value,
                **scrape_fields,
            )
            await lead.insert()
            saved.append(lead)

    return saved
