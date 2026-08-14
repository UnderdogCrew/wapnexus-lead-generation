"""Phase 3 — Pain-point extraction from reviews / website copy."""

import json
from typing import Any

from openai import OpenAI

from app.config import get_settings

EXTRACTION_PROMPT = """You are analyzing customer reviews for a local business to find
communication-related pain points a WhatsApp automation product could solve.

Business name: {name}
Reviews:
{reviews_text}

Website copy snippet (may be empty):
{website_snippet}

Return ONLY a JSON object with:
- "pain_points": a list of up to 3 short strings (max ~15 words each) describing
  concrete communication pain points found (e.g. "customers mention slow reply times
  to booking inquiries"). If none are found, return an empty list.
- "has_signal": true if at least one real pain point was found, false otherwise

Return ONLY the JSON object, no other text.
"""


def _client() -> OpenAI:
    settings = get_settings()
    return OpenAI(api_key=settings.openai_api_key)


def extract_pain_points(name: str, reviews: list[str], website_snippet: str = "") -> dict[str, Any]:
    settings = get_settings()
    reviews_text = "\n".join(f"- {r}" for r in reviews) if reviews else "(no reviews available)"

    prompt = EXTRACTION_PROMPT.format(
        name=name,
        reviews_text=reviews_text,
        website_snippet=website_snippet or "(none)",
    )

    response = _client().chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    raw_text = response.choices[0].message.content.strip()
    raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {"pain_points": [], "has_signal": False}
