from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PipelineRunRequest(BaseModel):
    category: str = Field(..., examples=["salons"])
    city: str = Field(..., examples=["Surat"])
    min_fit_score: int = Field(3, ge=1, le=5)
    max_pages: int = Field(3, ge=1, le=10)
    persist: bool = Field(True, description="Upsert results into the leads collection")


class PipelineRunResponse(BaseModel):
    category: str
    city: str
    total_leads: int
    qualified_leads: int
    leads: list[dict[str, Any]]


class LeadSearchRequest(BaseModel):
    category: str = Field(..., min_length=1, examples=["salons"])
    city: str = Field(..., min_length=1, examples=["Surat"])
    max_pages: int = Field(1, ge=1, le=10)
    run_ai: bool = Field(
        False,
        description="If true, also classify + extract pain points + generate drafts (full pipeline).",
    )
    min_fit_score: int = Field(3, ge=1, le=5)


class LeadUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    draft_message: str | None = None
    outreach_channel: str | None = None
    email: str | None = None
    contacted_at: datetime | None = None
    follow_up_at: datetime | None = None


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    place_id: str
    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    rating: float | None = None
    review_count: int | None = None
    category_searched: str
    city_searched: str
    google_types: list | None = None
    business_status: str | None = None
    normalized_category: str | None = None
    messaging_volume: str = "unknown"
    already_using_chat_automation: str | None = None
    fit_score: int = 0
    classification_reasoning: str | None = None
    pain_points: list[str] = Field(default_factory=list)
    has_signal: bool | None = None
    draft_message: str = ""
    outreach_channel: str | None = None
    status: str = "new"
    contacted_at: datetime | None = None
    follow_up_at: datetime | None = None
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class LeadListResponse(BaseModel):
    total: int
    leads: list[LeadOut]


class LeadSearchResponse(BaseModel):
    category: str
    city: str
    count: int
    leads: list[LeadOut]


class WhatsAppSendResponse(BaseModel):
    ok: bool = True
    message: str = "WhatsApp message sent"
    number: str
    lead: LeadOut
