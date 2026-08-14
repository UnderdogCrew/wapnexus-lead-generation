"""Phase 4 — Outreach draft generation."""

from typing import Any

from openai import OpenAI

from app.config import get_settings

OUTREACH_PROMPT = """Write a short, casual outreach message from a WhatsApp Business API
company called WapNexus to a local business owner.

Business name: {name}
Business category: {category}
Pain point signal (may be empty): {pain_point}

Rules:
- Under 60 words.
- Sound like a real person, not a marketing template.
- If a pain point is given, reference it naturally and specifically.
- If no pain point is given, keep it general but still specific to their business type.
- End with a soft, low-pressure call to action (e.g. offering a quick demo), not a hard sell.
- Do not use emojis, exclamation-heavy language, or generic phrases like "Hope this finds you well."

Return ONLY the message text, no quotes, no other commentary.
"""


def _client() -> OpenAI:
    settings = get_settings()
    return OpenAI(api_key=settings.openai_api_key)


def generate_outreach_message(name: str, category: str, pain_point: str = "") -> str:
    settings = get_settings()
    prompt = OUTREACH_PROMPT.format(name=name, category=category, pain_point=pain_point)

    response = _client().chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
    )

    return response.choices[0].message.content.strip()


def generate_drafts_for_leads(leads: list[dict[str, Any]], min_fit_score: int = 3) -> list[dict[str, Any]]:
    drafts: list[dict[str, Any]] = []
    for lead in leads:
        if lead.get("fit_score", 0) < min_fit_score:
            continue

        pain_point = ""
        if lead.get("pain_points"):
            pain_point = lead["pain_points"][0]

        message = generate_outreach_message(
            name=lead.get("name", "there"),
            category=lead.get("normalized_category", "business"),
            pain_point=pain_point,
        )

        drafts.append(
            {
                "place_id": lead.get("place_id"),
                "name": lead.get("name"),
                "draft_message": message,
                "status": "pending_review",
            }
        )

    return drafts
