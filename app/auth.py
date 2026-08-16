import base64
import hashlib
import hmac
import json
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings

_bearer = HTTPBearer(auto_error=False)

TOKEN_TTL_SECONDS = 7 * 24 * 60 * 60


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _secret() -> str:
    settings = get_settings()
    if settings.auth_secret:
        return settings.auth_secret
    material = f"{settings.admin_username}:{settings.admin_password}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _digest(value: str) -> bytes:
    return hashlib.sha256(value.encode("utf-8")).digest()


def credentials_match(username: str, password: str) -> bool:
    settings = get_settings()
    if not settings.admin_username or not settings.admin_password:
        return False
    user_ok = hmac.compare_digest(_digest(username), _digest(settings.admin_username))
    pass_ok = hmac.compare_digest(_digest(password), _digest(settings.admin_password))
    return user_ok and pass_ok


def create_token(username: str) -> str:
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _b64url_encode(
        json.dumps(
            {"sub": username, "exp": int(time.time()) + TOKEN_TTL_SECONDS},
            separators=(",", ":"),
        ).encode()
    )
    signing_input = f"{header}.{payload}"
    signature = hmac.new(_secret().encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def verify_token(token: str) -> dict:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e

    signing_input = f"{header_b64}.{payload_b64}"
    expected = _b64url_encode(
        hmac.new(_secret().encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    )
    if not hmac.compare_digest(expected, signature_b64):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e

    if int(payload.get("exp") or 0) < int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    return payload


async def require_admin(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    if creds is None or creds.scheme.lower() != "bearer" or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return verify_token(creds.credentials)
