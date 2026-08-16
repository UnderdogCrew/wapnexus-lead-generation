from datetime import datetime, timezone
import asyncio
import re

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import require_admin

from app.models import Lead, LeadStatus
from app.schemas import (
    LeadListResponse,
    LeadOut,
    LeadSearchRequest,
    LeadSearchResponse,
    LeadUpdate,
    WhatsAppSendResponse,
)
from app.services.google_places_scraper import collect_leads
from app.services.pipeline import persist_leads, run_pipeline, search_and_persist_raw
from app.services.wapnexus import send_template_message

router = APIRouter(prefix="/leads", tags=["leads"], dependencies=[Depends(require_admin)])


def _lead_out(lead: Lead) -> LeadOut:
    data = lead.model_dump()
    data["id"] = str(lead.id)
    data["pain_points"] = data.get("pain_points") or []
    data["draft_message"] = data.get("draft_message") or ""
    data["messaging_volume"] = data.get("messaging_volume") or "unknown"
    data["fit_score"] = data.get("fit_score") or 0
    if not data.get("normalized_category"):
        data["normalized_category"] = data.get("category_searched") or "Business"
    return LeadOut(**data)


@router.get("", response_model=LeadListResponse)
async def list_leads(
    city: str | None = None,
    category: str | None = None,
    status: str | None = None,
    q: str | None = Query(None, description="Case-insensitive name search"),
    min_fit_score: int | None = Query(None, ge=0, le=5),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    mongo_filter: dict = {}
    if city:
        mongo_filter["city_searched"] = {"$regex": f"^{re.escape(city)}$", "$options": "i"}
    if category:
        mongo_filter["$or"] = [
            {"category_searched": {"$regex": f"^{re.escape(category)}$", "$options": "i"}},
            {"normalized_category": {"$regex": f"^{re.escape(category)}$", "$options": "i"}},
        ]
    if status:
        mongo_filter["status"] = status
    if min_fit_score is not None:
        mongo_filter["fit_score"] = {"$gte": min_fit_score}
    if q:
        mongo_filter["name"] = {"$regex": re.escape(q), "$options": "i"}

    query = Lead.find(mongo_filter) if mongo_filter else Lead.find_all()
    total = await query.count()
    leads = await query.sort([("fit_score", -1), ("created_at", -1)]).skip(skip).limit(limit).to_list()
    return LeadListResponse(total=total, leads=[_lead_out(lead) for lead in leads])


@router.post("/search", response_model=LeadSearchResponse)
async def search_leads(body: LeadSearchRequest):
    """UI 'Find businesses' button — scrape Google Places and upsert leads."""
    category = body.category.strip()
    city = body.city.strip()
    if not category or not city:
        raise HTTPException(status_code=400, detail="category and city are required")

    try:
        if body.run_ai:
            results = await asyncio.to_thread(
                run_pipeline,
                category,
                city,
                body.min_fit_score,
                body.max_pages,
            )
            saved = await persist_leads(results, min_fit_score=body.min_fit_score)
        else:
            raw = await asyncio.to_thread(collect_leads, category, city, body.max_pages)
            saved = await search_and_persist_raw(raw, category=category, city=city)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Search failed: {e}") from e

    return LeadSearchResponse(
        category=category,
        city=city,
        count=len(saved),
        leads=[_lead_out(lead) for lead in saved],
    )


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: str):
    lead = await _get_lead_or_404(lead_id)
    return _lead_out(lead)


@router.post("/{lead_id}/whatsapp", response_model=WhatsAppSendResponse)
async def send_lead_whatsapp(lead_id: str):
    """Send the WapNexus grow_business template to this lead's phone number."""
    lead = await _get_lead_or_404(lead_id)
    if not lead.phone:
        raise HTTPException(status_code=400, detail="No phone number on file")

    try:
        result = await asyncio.to_thread(send_template_message, lead.phone, lead.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"WhatsApp send failed: {e}") from e

    now = datetime.now(timezone.utc)
    await lead.set(
        {
            "status": LeadStatus.CONTACTED.value,
            "outreach_channel": "whatsapp",
            "contacted_at": now,
            "updated_at": now,
        }
    )
    return WhatsAppSendResponse(number=result["number"], lead=_lead_out(lead))


@router.patch("/{lead_id}", response_model=LeadOut)
async def update_lead(lead_id: str, body: LeadUpdate):
    lead = await _get_lead_or_404(lead_id)

    updates = body.model_dump(exclude_unset=True)
    if "status" in updates and updates["status"] is not None:
        valid = {s.value for s in LeadStatus}
        if updates["status"] not in valid:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {sorted(valid)}")

    updates["updated_at"] = datetime.now(timezone.utc)
    await lead.set(updates)
    return _lead_out(lead)


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(lead_id: str):
    lead = await _get_lead_or_404(lead_id)
    await lead.delete()
    return None


async def _get_lead_or_404(lead_id: str) -> Lead:
    try:
        object_id = PydanticObjectId(lead_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid lead id") from e

    lead = await Lead.get(object_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
