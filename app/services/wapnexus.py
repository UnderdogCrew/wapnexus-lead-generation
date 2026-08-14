"""Send WhatsApp template messages via the WapNexus API."""

import re
from typing import Any

import requests

from app.config import get_settings

INDIAN_MOBILE_RE = re.compile(r"^[6-9]\d{9}$")


def normalize_phone(phone: str | None) -> str:
    """Turn a Places-formatted number into E.164, defaulting to +91 for local Indian numbers."""
    raw = (phone or "").strip()
    if not raw:
        return ""

    has_plus = raw.startswith("+")
    digits = re.sub(r"\D", "", raw)
    if not digits:
        return ""

    if has_plus:
        return f"+{digits}"
    if digits.startswith("91") and len(digits) >= 12:
        return f"+{digits}"
    if digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    if INDIAN_MOBILE_RE.fullmatch(digits):
        return f"+91{digits}"
    return f"+{digits}"


def send_template_message(phone: str, business_name: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.wapnexus_api_token:
        raise RuntimeError("WAPNEXUS_API_TOKEN is not set.")

    number = normalize_phone(phone)
    if not number:
        raise ValueError("A valid phone number is required")

    name = (business_name or "").strip() or "Customer"
    payload = {
        "text": "",
        "template_name": settings.wapnexus_template_name,
        "message_type": 2,
        "is_select_all": False,
        "numbers": [number],
        "metadata": {"1": name},
        "paramsFallbackValue": {"1": "Customer"},
    }
    resp = requests.post(
        settings.wapnexus_send_url,
        headers={
            "authorization": f"Bearer {settings.wapnexus_api_token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    try:
        body = resp.json()
    except ValueError:
        body = {"raw": resp.text}

    if not resp.ok:
        detail = body.get("message") or body.get("detail") or body.get("error") or resp.text
        raise RuntimeError(f"WapNexus send failed ({resp.status_code}): {detail}")

    if isinstance(body, dict) and body.get("success") is False:
        raise RuntimeError(body.get("message") or body.get("error") or "WapNexus send failed")

    return {"number": number, "response": body}
