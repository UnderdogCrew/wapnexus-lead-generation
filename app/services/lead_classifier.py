"""Phase 2 — AI lead classification."""

import json
from typing import Any

from openai import OpenAI

from app.config import get_settings

CLASSIFICATION_PROMPT = """You are helping a WhatsApp Business API company (WapNexus) qualify sales leads.

Given the business info below, return ONLY a JSON object with these exact keys:
- "normalized_category": a short, standard category name (e.g. "salon", "real estate agency", "restaurant")
- "messaging_volume": one of "high", "medium", "low" — how much customer messaging (order updates, appointment reminders, inquiries) this type of business typically handles
- "already_using_chat_automation": true, false, or "unknown" — based on website/name text, whether they already seem to use a chatbot or WhatsApp API
- "fit_score": integer 1-5 — how good a fit this business is for a WhatsApp Business API product (5 = excellent fit, 1 = poor fit)
- "reasoning": one short sentence explaining the fit_score

Business info:
Name: {name}
Category (from Google): {google_types}
Website: {website}
Rating: {rating} ({review_count} reviews)
Business status: {business_status}

Return ONLY the JSON object, no other text.
"""


def _client() -> OpenAI:
    settings = get_settings()
    return OpenAI(api_key=settings.openai_api_key)


def classify_lead(lead: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    prompt = CLASSIFICATION_PROMPT.format(
        name=lead.get("name", "Unknown"),
        google_types=lead.get("google_types", []),
        website=lead.get("website") or "none listed",
        rating=lead.get("rating", "N/A"),
        review_count=lead.get("review_count", 0),
        business_status=lead.get("business_status", "unknown"),
    )

    response = _client().chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    raw_text = response.choices[0].message.content.strip()
    raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        result = {
            "normalized_category": "unknown",
            "messaging_volume": "unknown",
            "already_using_chat_automation": "unknown",
            "fit_score": 0,
            "reasoning": "Failed to parse LLM response",
        }

    result["place_id"] = lead.get("place_id")
    # Normalize key name for DB field
    if "reasoning" in result and "classification_reasoning" not in result:
        result["classification_reasoning"] = result.pop("reasoning")
    return result


def classify_leads_batch(leads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    classified: list[dict[str, Any]] = []
    for lead in leads:
        try:
            classified.append(classify_lead(lead))
        except Exception as e:
            print(f"Failed to classify lead {lead.get('name')}: {e}")
    return classified
