"""Phase 1 — Google Places data collection."""

import time
from typing import Any

import requests

from app.config import get_settings

TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
DETAIL_FIELDS = (
    "name,formatted_address,formatted_phone_number,website,rating,"
    "user_ratings_total,business_status,types"
)


def search_places(category: str, city: str, max_pages: int = 3) -> list[dict[str, Any]]:
    settings = get_settings()
    if not settings.google_places_api_key:
        raise RuntimeError("GOOGLE_PLACES_API_KEY is not set. Copy .env.example to .env and fill it in.")

    query = f"{category} in {city}"
    params: dict[str, str] = {"query": query, "key": settings.google_places_api_key}
    results: list[dict[str, Any]] = []

    for _ in range(max_pages):
        resp = requests.get(TEXT_SEARCH_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            raise RuntimeError(f"Google Places error: {data.get('status')} — {data.get('error_message', '')}")

        results.extend(data.get("results", []))

        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break

        time.sleep(2)
        params = {"pagetoken": next_page_token, "key": settings.google_places_api_key}

    return results


def get_place_details(place_id: str) -> dict[str, Any]:
    settings = get_settings()
    params = {
        "place_id": place_id,
        "fields": DETAIL_FIELDS,
        "key": settings.google_places_api_key,
    }
    resp = requests.get(DETAILS_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data.get("result", {})


def collect_leads(
    category: str,
    city: str,
    max_pages: int = 3,
    sleep_between_details: float = 0.2,
) -> list[dict[str, Any]]:
    raw_results = search_places(category, city, max_pages=max_pages)
    leads: list[dict[str, Any]] = []

    for place in raw_results:
        place_id = place.get("place_id")
        details = get_place_details(place_id) if place_id else {}
        time.sleep(sleep_between_details)

        leads.append(
            {
                "place_id": place_id,
                "name": details.get("name") or place.get("name"),
                "address": details.get("formatted_address") or place.get("formatted_address"),
                "phone": details.get("formatted_phone_number"),
                "website": details.get("website"),
                "rating": details.get("rating") or place.get("rating"),
                "review_count": details.get("user_ratings_total") or place.get("user_ratings_total"),
                "business_status": details.get("business_status") or place.get("business_status"),
                "google_types": details.get("types") or place.get("types"),
                "category_searched": category,
                "city_searched": city,
                "source": "google_places",
            }
        )

    return leads
