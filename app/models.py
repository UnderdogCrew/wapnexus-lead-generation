from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any

from beanie import Document, Indexed
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel


class LeadStatus(str, Enum):
    NEW = "new"
    CLASSIFIED = "classified"
    DRAFTED = "drafted"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    CONVERTED = "converted"
    REJECTED = "rejected"


class MessagingVolume(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class Lead(Document):
    # Raw scraped data (Phase 1)
    place_id: Annotated[str, Indexed(unique=True)]
    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    rating: float | None = None
    review_count: int | None = None
    category_searched: str
    city_searched: str
    google_types: list[Any] | None = None
    business_status: str | None = None

    # AI classification (Phase 2)
    normalized_category: str | None = None
    messaging_volume: str = MessagingVolume.UNKNOWN.value
    already_using_chat_automation: str | None = None
    fit_score: int = 0
    classification_reasoning: str | None = None

    # Pain-point extraction (Phase 3)
    pain_points: list[str] | None = None
    has_signal: bool | None = None

    # Outreach (Phase 4)
    draft_message: str | None = None
    outreach_channel: str | None = None

    # Tracking (Phase 6)
    status: str = LeadStatus.NEW.value
    contacted_at: datetime | None = None
    follow_up_at: datetime | None = None
    notes: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "leads"
        indexes = [
            IndexModel([("city_searched", ASCENDING), ("category_searched", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("fit_score", DESCENDING)]),
        ]
